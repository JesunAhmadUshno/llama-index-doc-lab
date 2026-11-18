"""Post-registration sensitivity analysis for H2: floor choice.

Registered in DECISIONS.md as D6 (2026-11-17) before this script
was run. H2's frozen verdict rests on the own-floor rule (each
arm's own 10th percentile of its 28 in-corpus top-1 scores).
This script recomputes both arms' spurious-answer rates from the
committed raw records (results/raw_runs.json) under alternative
floors, using the repository's own src/metrics.py percentile and
spurious_rate, the same functions scripts/make_results.py uses:

- own 5th percentile
- own 10th percentile (the frozen rule; reference point, checked
  against results/metrics.json before anything else is computed)
- own 25th percentile
- a shared absolute floor of 0.50 for both arms (both top-1
  scores live on [0, 1]: production coverage share, LlamaIndex
  cosine similarity; 0.50 is the common scale midpoint)

Outputs (new files only): results/h2_floor_sensitivity.json and
results/h2_floor_sensitivity.md. The frozen H2 verdict is not
recomputed and does not change; this measures how the comparison
moves with the floor definition.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.metrics import percentile, spurious_rate  # noqa: E402

ARMS = ("prod", "li")
ARM_NAMES = {"prod": "Production", "li": "LlamaIndex"}
H2_MARGIN = 0.25  # frozen verdict line in PREREGISTRATION.md
SHARED_FLOOR = 0.50
OWN_PERCENTILES = (5, 10, 25)


def fmt(x, digits=4):
    return f"{x:.{digits}f}"


def main():
    raw = json.loads((ROOT / "results" / "raw_runs.json").read_text())
    published = json.loads((ROOT / "results" / "metrics.json").read_text())
    questions = raw["questions"]
    in_corpus = [q for q in questions if q["slice"] == "in_corpus"]
    adversarial = [q for q in questions if q["slice"] == "adversarial"]
    assert len(in_corpus) == 28 and len(adversarial) == 12

    scores = {arm: [q[arm]["top1_score"] for q in in_corpus]
              for arm in ARMS}
    adv_records = {
        arm: [{"ranked_docs": q[arm]["ranked_docs"],
               "top1_score": q[arm]["top1_score"]} for q in adversarial]
        for arm in ARMS}

    # Integrity check: the frozen rule (own 10th percentile) must
    # reproduce the published floors and spurious counts exactly.
    for arm in ARMS:
        floor = percentile(scores[arm], 10)
        spur = spurious_rate(adv_records[arm], floor)
        pub = published["arms"][arm]
        assert abs(floor - pub["floor"]) < 1e-12, (
            f"{arm}: recomputed floor {floor} != published {pub['floor']}")
        assert spur["count"] == pub["spurious"]["count"], (
            f"{arm}: recomputed spurious count {spur['count']} "
            f"!= published {pub['spurious']['count']}")
    print("integrity check passed: own-10th-percentile floors and "
          "spurious counts reproduce results/metrics.json exactly")

    floors = []
    for p in OWN_PERCENTILES:
        floors.append({
            "name": f"own {p}th percentile"
                    + (" (frozen rule)" if p == 10 else ""),
            "kind": "own_percentile",
            "percentile": p,
            "floor_by_arm": {arm: percentile(scores[arm], p)
                             for arm in ARMS},
        })
    floors.append({
        "name": f"shared absolute floor {SHARED_FLOOR:.2f}",
        "kind": "shared_absolute",
        "percentile": None,
        "floor_by_arm": {arm: SHARED_FLOOR for arm in ARMS},
    })

    rows = []
    for spec in floors:
        row = {"floor": spec["name"], "kind": spec["kind"],
               "percentile": spec["percentile"], "arms": {}}
        for arm in ARMS:
            floor = spec["floor_by_arm"][arm]
            spur = spurious_rate(adv_records[arm], floor)
            row["arms"][arm] = {"floor": floor,
                                "spurious_count": spur["count"],
                                "spurious_rate": spur["rate"],
                                "n": spur["n"]}
        p_rate = row["arms"]["prod"]["spurious_rate"]
        l_rate = row["arms"]["li"]["spurious_rate"]
        row["difference"] = abs(p_rate - l_rate)
        row["higher_arm"] = (
            "prod" if p_rate > l_rate else
            "li" if l_rate > p_rate else "tie")
        row["difference_at_or_above_h2_margin"] = (
            row["difference"] >= H2_MARGIN)
        rows.append(row)

    out = {
        "analysis": "H2 floor sensitivity (post-registration, "
                    "DECISIONS.md D6, 2026-11-17)",
        "source": "results/raw_runs.json (committed scored pass)",
        "method": "src/metrics.py percentile (linear interpolation) "
                  "and spurious_rate, as in scripts/make_results.py",
        "integrity_check": "own 10th percentile reproduces the "
                           "published floors and spurious counts in "
                           "results/metrics.json exactly",
        "h2_margin": H2_MARGIN,
        "shared_floor": SHARED_FLOOR,
        "rows": rows,
    }
    (ROOT / "results" / "h2_floor_sensitivity.json").write_text(
        json.dumps(out, indent=1))

    lines = []
    lines.append("# H2 floor sensitivity (post-registration analysis, "
                 "DECISIONS.md D6, 2026-11-17)")
    lines.append("")
    lines.append("Generated by scripts/h2_floor_sensitivity.py from "
                 "results/raw_runs.json, the committed records of the "
                 "scored pass. The frozen H2 verdict (CONFIRMED under "
                 "the frozen own-10th-percentile floor, difference "
                 "0.3333) is unchanged; this analysis measures how the "
                 "comparison moves under other defensible floors.")
    lines.append("")
    lines.append("Integrity check: the own-10th-percentile row "
                 "reproduces the published floors (production "
                 "0.2350, LlamaIndex 0.5481) and spurious counts "
                 "(9 of 12, 5 of 12) from results/metrics.json "
                 "exactly.")
    lines.append("")
    lines.append("| Floor | Production floor | Production spurious "
                 "| LlamaIndex floor | LlamaIndex spurious | "
                 "|Difference| | Higher arm | At/above the frozen "
                 "0.25 margin |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in rows:
        p, l = row["arms"]["prod"], row["arms"]["li"]
        lines.append(
            f"| {row['floor']} | {fmt(p['floor'])} | "
            f"{fmt(p['spurious_rate'])} ({p['spurious_count']}/12) | "
            f"{fmt(l['floor'])} | "
            f"{fmt(l['spurious_rate'])} ({l['spurious_count']}/12) | "
            f"{fmt(row['difference'])} | "
            f"{ARM_NAMES[row['higher_arm']] if row['higher_arm'] != 'tie' else 'tie'} | "
            f"{'yes' if row['difference_at_or_above_h2_margin'] else 'no'} |")
    lines.append("")
    own_rows = [r for r in rows if r["kind"] == "own_percentile"]
    shared_row = [r for r in rows if r["kind"] == "shared_absolute"][0]
    lines.append(
        "Reading: under each own-percentile floor the production "
        "arm's spurious rate is the higher one ("
        + "; ".join(
            f"{row['floor']}: production "
            f"{fmt(row['arms']['prod']['spurious_rate'])}, "
            f"LlamaIndex {fmt(row['arms']['li']['spurious_rate'])}"
            for row in own_rows)
        + "), so within the own-floor family the direction of the "
          "comparison never changes. The size of the gap moves a "
          "lot: "
        + "; ".join(
            f"{row['floor']}: difference {fmt(row['difference'])}"
            for row in own_rows)
        + ", and only the frozen 10th-percentile difference "
          "reaches the frozen 0.25 margin; at the 5th and 25th "
          "percentiles the gap is one question of twelve. Under "
          "the shared absolute floor the direction reverses "
          f"(production {fmt(shared_row['arms']['prod']['spurious_rate'])}, "
          f"LlamaIndex {fmt(shared_row['arms']['li']['spurious_rate'])}, "
          f"difference {fmt(shared_row['difference'])}): the shared "
          "0.50 sits below the LlamaIndex arm's own 10th-percentile "
          "floor (0.5481) and well above the production arm's "
          "(0.2350), so one absolute line holds the two arms to "
          "different effective stringencies because their score "
          "distributions sit differently on the [0, 1] scale. Net: "
          "the H2 comparison is definition-sensitive in magnitude "
          "under every alternative computed here, and in direction "
          "under a shared absolute floor; within the own-floor "
          "family the direction is stable but the margin is met "
          "only at the frozen percentile. The margin column "
          "applies the frozen H2 verdict line (0.25) to each "
          "alternative difference for scale only; no verdict is "
          "re-issued under any floor but the frozen one.")
    lines.append("")
    (ROOT / "results" / "h2_floor_sensitivity.md").write_text(
        "\n".join(lines))

    for row in rows:
        p, l = row["arms"]["prod"], row["arms"]["li"]
        print(f"{row['floor']}: prod floor {fmt(p['floor'])} rate "
              f"{fmt(p['spurious_rate'])} ({p['spurious_count']}/12); "
              f"li floor {fmt(l['floor'])} rate "
              f"{fmt(l['spurious_rate'])} ({l['spurious_count']}/12); "
              f"diff {fmt(row['difference'])}; higher "
              f"{row['higher_arm']}; >= margin "
              f"{row['difference_at_or_above_h2_margin']}")


if __name__ == "__main__":
    main()
