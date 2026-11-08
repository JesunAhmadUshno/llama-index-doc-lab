"""Unit tests: metric math, frozen-input integrity, both arms.

The production-arm tests run the real vendored corpus and pipeline
(standard library only). The LlamaIndex test uses a MockEmbedding,
so no model download happens in CI; it tests the wiring (document
ids through metadata, full-ranking retrieval), not the frozen
embedding model, which the study itself exercises.
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import li_arm, prod_arm  # noqa: E402
from src.metrics import (  # noqa: E402
    accuracy_metrics,
    hit_at_k,
    percentile,
    reciprocal_rank,
    spurious_rate,
)
from src.prodref.corpus import DOCUMENTS  # noqa: E402

QUESTIONS_SHA256 = (
    "f1b52a8d79ca1315f7a632cc659118101fab11821fe97d6b20d2d39a9ae0079b")
CORPUS_PY_SHA256 = (
    "509021670026878115987d61f0efd9e615f24660a895c03b407ad6ab38458521")
PIPELINE_PY_SHA256 = (
    "3776947f1b0dacf7da55861dec3c94b07b849e6e6ddb3d3da693f1e731a00f62")


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def test_percentile_linear_interpolation():
    vals = [0.0, 1.0, 2.0, 3.0, 4.0]
    assert percentile(vals, 0) == 0.0
    assert percentile(vals, 50) == 2.0
    assert percentile(vals, 100) == 4.0
    assert abs(percentile(vals, 10) - 0.4) < 1e-12
    assert abs(percentile([5.0], 90) - 5.0) < 1e-12
    assert abs(percentile([1.0, 3.0], 25) - 1.5) < 1e-12


def test_hit_and_reciprocal_rank():
    ranking = ["a", "b", "c", "d", "e", "f"]
    assert hit_at_k(ranking, "a", 1) == 1
    assert hit_at_k(ranking, "b", 1) == 0
    assert hit_at_k(ranking, "f", 5) == 0
    assert hit_at_k(ranking, "f", 6) == 1
    assert reciprocal_rank(ranking, "c") == 1.0 / 3
    assert reciprocal_rank(ranking, "absent") == 0.0


def test_accuracy_metrics_toy():
    records = [
        {"ranked_docs": ["x", "y"], "expected_doc": "x"},
        {"ranked_docs": ["y", "x"], "expected_doc": "x"},
        {"ranked_docs": ["y", "z"], "expected_doc": "x"},
    ]
    out = accuracy_metrics(records)
    assert out["n"] == 3
    assert out["top1_hits"] == 1 and abs(out["top1"] - 1 / 3) < 1e-12
    assert out["top5_hits"] == 2 and abs(out["top5"] - 2 / 3) < 1e-12
    assert abs(out["mrr"] - (1 + 0.5 + 0.0) / 3) < 1e-12


def test_spurious_rate_toy():
    records = [
        {"ranked_docs": ["a"], "top1_score": 0.9},
        {"ranked_docs": ["b"], "top1_score": 0.1},
        {"ranked_docs": [], "top1_score": None},
        {"ranked_docs": ["c"], "top1_score": 0.5},
    ]
    out = spurious_rate(records, floor=0.5)
    assert out["count"] == 2 and out["rate"] == 0.5


def test_frozen_inputs_integrity():
    assert sha256_of(ROOT / "data" / "questions.json") == QUESTIONS_SHA256
    assert sha256_of(ROOT / "src" / "prodref" / "corpus.py") == \
        CORPUS_PY_SHA256
    assert sha256_of(ROOT / "src" / "prodref" / "pipeline.py") == \
        PIPELINE_PY_SHA256
    questions = json.loads((ROOT / "data" / "questions.json").read_text())
    in_corpus = [q for q in questions if q["slice"] == "in_corpus"]
    adversarial = [q for q in questions if q["slice"] == "adversarial"]
    assert len(questions) == 40
    assert len(in_corpus) == 28 and len(adversarial) == 12
    corpus_ids = {d["id"] for d in DOCUMENTS}
    assert len(corpus_ids) == 20
    assert all(q["expected_doc"] in corpus_ids for q in in_corpus)
    assert all(q["expected_doc"] is None for q in adversarial)


def test_prod_arm_reproduces_sibling_top1():
    """The pre-registered harness integrity gate, as a test: the
    production arm must reproduce mlops-evidence-lab's measured
    in-corpus top-1 of 23 of 28 on the frozen question set."""
    pipeline = prod_arm.build()
    questions = json.loads((ROOT / "data" / "questions.json").read_text())
    in_corpus = [q for q in questions if q["slice"] == "in_corpus"]
    records = []
    for q in in_corpus:
        ranked, _score, _n = prod_arm.retrieve(pipeline, q["question"])
        records.append({"ranked_docs": ranked,
                        "expected_doc": q["expected_doc"]})
    out = accuracy_metrics(records)
    assert out["top1_hits"] == 23, out


def test_li_arm_wiring_with_mock_embedding():
    from llama_index.core.embeddings import MockEmbedding

    docs = [("alpha", "Cats sleep all day."),
            ("beta", "Dogs bark at night."),
            ("gamma", "Birds fly south.")]
    index, node_count = li_arm.build(docs, MockEmbedding(embed_dim=16))
    assert node_count == 3
    ranked, score, n = li_arm.retrieve(index, "anything at all", top_k=3)
    assert n == 3 and sorted(ranked) == ["alpha", "beta", "gamma"]
    assert score is not None
