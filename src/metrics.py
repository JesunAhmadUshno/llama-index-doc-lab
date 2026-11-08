"""Metric helpers shared by the results generator and the tests.

The percentile is the linear-interpolation method, identical to
numpy.percentile's default: rank = p / 100 * (n - 1) over the sorted
values, interpolated between the bracketing points.
"""

import math


def percentile(values, p):
    """Linear-interpolation percentile of a non-empty sequence."""
    vals = sorted(values)
    if not vals:
        raise ValueError("percentile of an empty sequence")
    if len(vals) == 1:
        return float(vals[0])
    rank = (p / 100.0) * (len(vals) - 1)
    lo = math.floor(rank)
    hi = math.ceil(rank)
    if lo == hi:
        return float(vals[int(rank)])
    frac = rank - lo
    return float(vals[lo] * (1 - frac) + vals[hi] * frac)


def median(values):
    return percentile(values, 50)


def hit_at_k(ranked_docs, expected_doc, k):
    """1 when the expected doc is among the first k ranked docs."""
    if expected_doc is None:
        raise ValueError("hit rate needs an expected doc")
    return 1 if expected_doc in ranked_docs[:k] else 0


def reciprocal_rank(ranked_docs, expected_doc):
    """1 / rank of the expected doc in the full ranking, 0 absent."""
    if expected_doc in ranked_docs:
        return 1.0 / (ranked_docs.index(expected_doc) + 1)
    return 0.0


def accuracy_metrics(records):
    """Top-1, top-5 and MRR over in-corpus records.

    Each record is a dict with ranked_docs (full document ranking)
    and expected_doc.
    """
    n = len(records)
    if n == 0:
        return {"n": 0, "top1": 0.0, "top5": 0.0, "mrr": 0.0,
                "top1_hits": 0, "top5_hits": 0}
    top1 = sum(hit_at_k(r["ranked_docs"], r["expected_doc"], 1)
               for r in records)
    top5 = sum(hit_at_k(r["ranked_docs"], r["expected_doc"], 5)
               for r in records)
    mrr = sum(reciprocal_rank(r["ranked_docs"], r["expected_doc"])
              for r in records) / n
    return {"n": n, "top1": top1 / n, "top5": top5 / n, "mrr": mrr,
            "top1_hits": top1, "top5_hits": top5}


def spurious_rate(records, floor):
    """Share of adversarial records that return context at or above
    the floor. A record spuriously retrieves when it returned at
    least one item and its top-1 score is at or above the floor."""
    n = len(records)
    if n == 0:
        return {"n": 0, "rate": 0.0, "count": 0}
    count = 0
    for r in records:
        if r["ranked_docs"] and r["top1_score"] is not None \
                and r["top1_score"] >= floor:
            count += 1
    return {"n": n, "rate": count / n, "count": count}
