"""Run the frozen study once and write the raw records.

Protocol (PREREGISTRATION.md): build each arm 3 times and take the
median build time; one untimed warm-up pass over all 40 questions
per arm; 3 timed passes in file order; rankings and top-1 scores
are recorded from timed pass 1; a question's latency is the median
of its 3 timed passes. Output: results/raw_runs.json.
"""

import hashlib
import importlib.metadata
import json
import os
import platform
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import li_arm, prod_arm  # noqa: E402
from src.metrics import median  # noqa: E402
from src.prodref.corpus import DOCUMENTS  # noqa: E402

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
N_BUILDS = 3
N_PASSES = 3


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def env_record():
    versions = {}
    for pkg in ("llama-index", "llama-index-core",
                "llama-index-embeddings-huggingface",
                "sentence-transformers", "torch", "numpy"):
        try:
            versions[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            versions[pkg] = None
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "machine": platform.node(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "packages": versions,
        "embed_model": MODEL_NAME,
        "embed_model_revision": MODEL_REVISION,
        "questions_sha256": sha256_of(ROOT / "data" / "questions.json"),
        "corpus_py_sha256": sha256_of(ROOT / "src" / "prodref" / "corpus.py"),
        "pipeline_py_sha256": sha256_of(
            ROOT / "src" / "prodref" / "pipeline.py"),
    }


def time_builds(build_fn):
    """Time N_BUILDS fresh builds; return (last_instance, times)."""
    times = []
    instance = None
    for _ in range(N_BUILDS):
        start = time.perf_counter()
        instance = build_fn()
        times.append(time.perf_counter() - start)
    return instance, times


def main():
    questions = json.loads((ROOT / "data" / "questions.json").read_text())
    doc_pairs = [(d["id"], d["text"]) for d in DOCUMENTS]
    n_docs = len(doc_pairs)

    # Production arm.
    pipeline, prod_times = time_builds(prod_arm.build)
    prod_record = {
        "build_times_s": prod_times,
        "build_median_s": median(prod_times),
        "build_per_doc_s": median(prod_times) / n_docs,
        "chunk_count": len(pipeline.chunks),
        "index_bytes": prod_arm.index_state_bytes(pipeline),
    }

    # LlamaIndex arm. The embedding model loads once, before timing.
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    embed_model = HuggingFaceEmbedding(model_name=MODEL_NAME)

    li_state = {}

    def build_li():
        index, node_count = li_arm.build(doc_pairs, embed_model)
        li_state["node_count"] = node_count
        return index

    index, li_times = time_builds(build_li)
    with tempfile.TemporaryDirectory() as tmp:
        li_bytes = li_arm.index_size_bytes(index, os.path.join(tmp, "idx"))
    li_record = {
        "build_times_s": li_times,
        "build_median_s": median(li_times),
        "build_per_doc_s": median(li_times) / n_docs,
        "node_count": li_state["node_count"],
        "index_bytes": li_bytes,
    }
    top_k = li_state["node_count"]

    arms = {
        "prod": lambda q: prod_arm.retrieve(pipeline, q),
        "li": lambda q: li_arm.retrieve(index, q, top_k),
    }

    # Warm-up pass, untimed.
    for record in questions:
        for fn in arms.values():
            fn(record["question"])

    # Timed passes. Rankings and scores come from pass 1.
    captured = {arm: {} for arm in arms}
    latencies = {arm: {} for arm in arms}
    for arm, fn in arms.items():
        for _pass in range(N_PASSES):
            for record in questions:
                start = time.perf_counter()
                ranked_docs, top1_score, _n = fn(record["question"])
                elapsed = time.perf_counter() - start
                latencies[arm].setdefault(record["id"], []).append(elapsed)
                if _pass == 0:
                    captured[arm][record["id"]] = {
                        "ranked_docs": ranked_docs,
                        "top1_score": top1_score,
                    }

    out_questions = []
    for record in questions:
        entry = {
            "id": record["id"],
            "slice": record["slice"],
            "category": record.get("category"),
            "question": record["question"],
            "expected_doc": record.get("expected_doc"),
        }
        for arm in arms:
            entry[arm] = {
                **captured[arm][record["id"]],
                "latencies_s": latencies[arm][record["id"]],
                "latency_median_s": median(latencies[arm][record["id"]]),
            }
        out_questions.append(entry)

    raw = {
        "env": env_record(),
        "builds": {"prod": prod_record, "li": li_record},
        "questions": out_questions,
    }
    out_path = ROOT / "results" / "raw_runs.json"
    out_path.write_text(json.dumps(raw, indent=1))
    print(f"wrote {out_path}")
    print(f"prod build median {prod_record['build_median_s']:.3f}s, "
          f"chunks {prod_record['chunk_count']}, "
          f"index {prod_record['index_bytes']} bytes")
    print(f"li build median {li_record['build_median_s']:.3f}s, "
          f"nodes {li_record['node_count']}, "
          f"index {li_record['index_bytes']} bytes")


if __name__ == "__main__":
    main()
