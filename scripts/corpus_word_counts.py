"""Measure the corpus word counts behind DECISIONS.md D7.

PREREGISTRATION.md describes the corpus as 72 to 87 words per
document, 1,588 words in total. This script counts the words in
the committed corpus (DOCUMENTS in src/prodref/corpus.py, the
vendored byte-identical copy of rag-foundation's corpus.py) so
the correction of record rests on a measurement, not on the
paper's say-so. A word is a whitespace-delimited token
(len(text.split())), the plain reading of the counts the
pre-registration states.

Output (new file only): results/corpus_word_counts.json.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.prodref.corpus import DOCUMENTS  # noqa: E402


def main():
    per_doc = [{"id": d["id"], "topic": d["topic"],
                "words": len(d["text"].split())} for d in DOCUMENTS]
    counts = [d["words"] for d in per_doc]
    out = {
        "source": "src/prodref/corpus.py, DOCUMENTS (vendored "
                  "byte-identical from JesunAhmadUshno/rag-foundation "
                  "commit 007e33238e6ce49100650b30f6820149410f022b)",
        "method": "word = whitespace-delimited token, "
                  "len(text.split())",
        "documents": len(per_doc),
        "min_words": min(counts),
        "max_words": max(counts),
        "total_words": sum(counts),
        "per_document": per_doc,
        "preregistration_claim": {"per_document": "72 to 87",
                                  "total": 1588},
    }
    (ROOT / "results" / "corpus_word_counts.json").write_text(
        json.dumps(out, indent=1))
    print(f"documents {len(per_doc)}; min {min(counts)}; "
          f"max {max(counts)}; total {sum(counts)}")


if __name__ == "__main__":
    main()
