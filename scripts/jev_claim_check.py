"""Run the house Jev claim_check gate over the headline verdicts.

The claim string is built from results/metrics.json and
results/verdicts.json (never hand-typed), the evidence is the full
RESULTS.md, and the spec plus the raw response are saved under
results/. Uses the connected TypeSafe connector helper
(custom.typesafe); the credential stays in the Secure Vault flow
inside the helper and is never printed here.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HELPER = Path.home() / ("workspace/custom-connectors/custom.typesafe/"
                        "bin/typesafe_jev.py")


def main():
    metrics = json.loads((ROOT / "results" / "metrics.json").read_text())
    verdicts = json.loads((ROOT / "results" / "verdicts.json").read_text())
    p, l = metrics["arms"]["prod"], metrics["arms"]["li"]
    pb, lb = metrics["builds"]["prod"], metrics["builds"]["li"]
    claim = (
        f"In the llama-index-doc-lab study (frozen 40-question set, "
        f"28 in-corpus and 12 adversarial, rag-foundation corpus), "
        f"H1 is {verdicts['H1']}: top-5 hit rate is "
        f"{p['accuracy']['top5']:.4f} ({p['accuracy']['top5_hits']} of 28) "
        f"for the production arm and {l['accuracy']['top5']:.4f} "
        f"({l['accuracy']['top5_hits']} of 28) for LlamaIndex, a "
        f"difference of {verdicts['detail']['top5_diff']:.4f}, below the "
        f"pre-registered 0.10 margin. H2 is {verdicts['H2']}: spurious "
        f"retrieval rate on the adversarial questions is "
        f"{p['spurious']['rate']:.4f} ({p['spurious']['count']} of 12) "
        f"for the production arm and {l['spurious']['rate']:.4f} "
        f"({l['spurious']['count']} of 12) for LlamaIndex, a difference "
        f"of {verdicts['detail']['spurious_diff']:.4f}, at or above the "
        f"pre-registered 0.25 margin. H3 is {verdicts['H3']}: index "
        f"build time per document is {pb['build_per_doc_s']:.4f} seconds "
        f"for the production arm and {lb['build_per_doc_s']:.4f} seconds "
        f"for LlamaIndex, a ratio of "
        f"{verdicts['detail']['build_ratio_li_over_prod']:.1f}, outside "
        f"the pre-registered band 0.5 to 2.0. Top-1 hit rate is "
        f"{p['accuracy']['top1']:.4f} for the production arm and "
        f"{l['accuracy']['top1']:.4f} for LlamaIndex; MRR is "
        f"{p['accuracy']['mrr']:.4f} and {l['accuracy']['mrr']:.4f}."
    )
    evidence = (ROOT / "RESULTS.md").read_text()
    spec = {
        "model": "jev-1.13.0",
        "state": {"claim": claim, "evidence": evidence},
        "questions": {
            "supported": {
                "type": "noul",
                "instructions": "Does the `evidence` in state fully "
                                "support the `claim` in state, with no "
                                "part of the claim going beyond the "
                                "evidence?",
                "criteria": {
                    "true": "Every part of the claim is directly backed "
                            "by the evidence",
                    "false": "Any part of the claim is missing from, "
                             "contradicted by, or stronger than the "
                             "evidence",
                },
            }
        },
    }
    spec_path = ROOT / "results" / "jev-claim-spec.json"
    spec_path.write_text(json.dumps(spec, indent=1))
    proc = subprocess.run(
        [sys.executable, str(HELPER), "evaluate", str(spec_path)],
        capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit("jev helper failed")
    outer = json.loads(proc.stdout)
    (ROOT / "results" / "jev-claim-check.json").write_text(
        json.dumps(outer, indent=1))
    body = outer.get("response", outer)
    answers = body.get("answers", {})
    noul = answers.get("supported", {}).get("noul")
    route = ("clear" if noul is not None and noul >= 0.85 else
             "block" if noul is not None and noul <= 0.10 else "review")
    print(json.dumps({
        "model": body.get("model"), "noul": noul, "route": route,
        "usage": body.get("usage"),
    }, indent=1))


if __name__ == "__main__":
    main()
