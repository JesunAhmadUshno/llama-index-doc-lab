# AUDIT

Self-audit of llama-index-doc-lab against the standing project
standard, written after the results were computed and before the
results commit.

## Grade: 5,000 of 10,000

What is solid: the pre-registration is the first content commit
(9534f68) and froze the arms, the floor rule, the margins and the
stop rule before any measured run. The question set and both
vendored production files are byte-identical to their pinned
sources, verified by sha256 in the test suite. The production arm
reproduces the sibling record exactly (top-1, 23 of 28), which
verifies the harness against an independent measurement. Verdicts
are computed by scripts/make_results.py from
results/raw_runs.json, and every headline figure was recomputed
from the raw records by a separate recount before this audit was
written; the recount matched on every figure. Two of the three
verdicts are refutations of the framework-friendly reading (H1
tie at top-5, H3 build cost far outside the band), published as
measured. The two failed run attempts are disclosed in
DECISIONS.md (D4, D5) rather than buried.

Itemized deductions:

- Minus 1,800: the corpus is tiny and synthetic (20 documents,
  1,588 words), inherited from the fixed inputs. The verdicts
  describe this corpus only; nothing here licenses a claim about
  retrieval at production corpus scale.
- Minus 900: one embedding model, CPU only, one machine, one
  scored pass. Build and latency figures are medians of three,
  but there is no cross-model or cross-machine variance estimate.
- Minus 800: under the frozen defaults the LlamaIndex arm holds
  exactly one node per document, so the study measures
  framework-default document-level dense retrieval. It does not
  measure LlamaIndex chunking behaviour, which is part of the
  framework's claim at real scale.
- Minus 600: H2 turns on the frozen own-floor rule (own 10th
  percentile). The rule was pre-registered and is applied
  symmetrically, and every raw top-1 score is published so any
  other floor can be applied, but the verdict is
  definition-sensitive and a different defensible floor moves the
  rates.
- Minus 400: production build times (2.6 to 3.1 ms) sit near
  timer resolution, so the H3 ratio point estimate (537.8x)
  carries wide relative error. The REFUTED direction is not in
  doubt (the band edge is 2.0x), but the exact ratio should not
  be quoted as precise.
- Minus 300: two failed run attempts preceded the scored pass
  (D4: interrupted model download left an incomplete snapshot and
  the offline load failed before any arm was built; D5: the full
  pass executed but its records were lost to a missing output
  directory, a harness bug, and the study was rerun from scratch
  per the stop rule). Process cost only; no data from either
  attempt exists or was used.
- Minus 200: the Jev claim_check gate landed on REVIEW rather
  than clear (below), so the headline figures stand on the hand
  verification recorded here rather than on the gate.

Deductions total 5,000. Grade 5,000 of 10,000.

## Jev claim_check record

- Gate: claim_check (standing house gate), run through
  scripts/jev_claim_check.py via the TypeSafe connector helper.
- Claim: built by the script from results/metrics.json and
  results/verdicts.json (the three verdicts with their measured
  values, plus top-1 and MRR for both arms); evidence: the full
  RESULTS.md. Spec saved at results/jev-claim-spec.json, raw
  response at results/jev-claim-check.json.
- Model: jev-1.13.0. Noul: 0.63. Route: REVIEW (house bands:
  clear at 0.85 and above, block at 0.10 and below, review
  between). Usage: 5,446 input tokens, 20 output tokens.
- On REVIEW, per the brief, the headline figures were
  hand-verified: an independent recount from
  results/raw_runs.json with separate code reproduced every
  figure in the claim exactly (top-1 23/28 and 28/28; top-5
  27/28 and 28/28; MRR 0.8929 and 1.0000; floors 0.2350 and
  0.5481; spurious 9/12 and 5/12; build medians 0.0028 s and
  1.5073 s; index bytes 51,463 and 207,734). The verdicts stand
  on that verification.

## Open tails

- A second embedding model, or the same study on a larger
  real-world corpus, would test whether the top-1 sweep and the
  spurious gap survive scale. Out of this study's frozen scope;
  named here, not done.
- The production arm's high spurious rate under its own floor is
  a finding about rag-foundation, reported here only; any fix
  belongs to that repo, which this study never modified.
