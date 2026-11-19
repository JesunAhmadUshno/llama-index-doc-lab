# Audit (the study report)

This file is the report in the portfolio standard's sense. It keeps
the name AUDIT.md, the name it was published under with the results;
PREREGISTRATION.md does not name a report file, so nothing in the
lock depends on it. Written after the results were computed and
before the results commit; restructured on 2026-11-08 for the
portfolio standard v2 (grade removed, since grades are internal;
every limitation it listed is kept below under Threats to validity).

Status, 2026-11-08: one scored pass, as registered, on the machine of
record htch-runtime. Verdicts are computed by scripts/make_results.py
from results/raw_runs.json and published in RESULTS.md.

## Results against the pre-registration

| Hypothesis | Frozen line | Verdict | Measured |
| --- | --- | --- | --- |
| H1: top-5 hit rates differ | absolute difference at least 0.10 | REFUTED | production 27/28, LlamaIndex 28/28, difference 0.0357 |
| H2: spurious retrieval rates differ | absolute difference at least 0.25 | CONFIRMED | production 9/12, LlamaIndex 5/12, difference 0.3333 |
| H3: LlamaIndex build cost per document about the same | ratio LI/PROD within [0.5, 2.0] | REFUTED | ratio 537.8 (medians of three builds) |

Two of three hypotheses missed their lines and are published as
measured. The harness integrity gate (production top-1 must equal the
sibling record, 23 of 28) passed before any LlamaIndex figure was
scored.

## How the evidence is protected

1. Pre-registration before results. PREREGISTRATION.md is the first
   content commit (9534f68, 2026-11-08 20:45:48 UTC) and the only file
   in it. It froze the arms, the floor rule, the margins and the stop
   rule. No later commit touches it; tests/test_layout.py pins its
   SHA-256, so one changed byte fails CI. The harness commit (9234c43)
   and the results commit (4dc544a) follow it, and the raw run records
   carry the timestamp 2026-11-08 20:52:04 UTC.
2. Frozen inputs, checked in code. The question set and both vendored
   production files are byte-identical to their pinned sources,
   verified by sha256 in tests/test_units.py.
3. An independent harness check. The production arm reproduces the
   sibling record exactly (top-1, 23 of 28, measured in
   mlops-evidence-lab), so the harness is verified against a separate
   measurement before the framework arm is scored. The same gate runs
   as a test and in scripts/make_results.py, which refuses to write
   results when it fails.
4. Numbers come from scripts. Verdicts are computed by
   scripts/make_results.py from results/raw_runs.json; CI regenerates
   RESULTS.md and results/ and fails on any byte of difference. Every
   headline figure was also recomputed from the raw records by a
   separate recount before this audit was written; the recount matched
   on every figure.
5. Versions recorded with the result. results/raw_runs.json carries
   the machine, platform, Python and package versions, the embedding
   model revision and the input hashes.
6. Failed attempts disclosed. The two failed run attempts are recorded
   in DECISIONS.md (D4, D5) rather than buried.
7. Spend and credentials. The study itself made no network calls
   during the scored runs and no paid calls. The one paid call was the
   Jev claim_check below, run once through the TypeSafe connector
   helper; no credential is stored in this repository.

## Deviations and incidents on record

- D4: the first run attempt failed at embedding load (an interrupted
  model download left an incomplete snapshot) before any arm was
  built. No records were written.
- D5: the second attempt executed the full pass but its records were
  lost to a missing output directory, a harness bug. The fix (one
  line in scripts/run_study.py creating results/) landed in the
  results commit, and the study was rerun from scratch per the stop
  rule. Process cost only; no data from either attempt exists or was
  used.
- Display precision. The results commit also changed
  scripts/make_results.py to print build times with four decimals
  instead of three, after the raw records existed. It changes how
  two RESULTS.md rows are rounded, not any metric or verdict, and is
  recorded here so the change is declared.

## Threats to validity

- Tiny synthetic corpus. The corpus is 20 synthetic documents,
  1,588 words, inherited from the fixed inputs. The verdicts describe
  this corpus only; nothing here licenses a claim about retrieval at
  production corpus scale.
- One embedding model, CPU only, one machine, one scored pass. Build
  and latency figures are medians of three, but there is no
  cross-model or cross-machine variance estimate, and no headline
  number carries an interval (none was pre-registered).
- One node per document. Under the frozen defaults the LlamaIndex
  arm holds exactly one node per document, so the study measures
  framework-default document-level dense retrieval. It does not
  measure LlamaIndex chunking behaviour, which is part of the
  framework's claim at real scale.
- H2 is definition-sensitive. H2 turns on the frozen own-floor rule
  (each arm's own 10th percentile). The rule was pre-registered and
  is applied symmetrically, and every raw top-1 score is published so
  any other floor can be applied, but a different defensible floor
  moves the rates.
- Timer resolution. Production build times (2.6 to 3.1 ms) sit near
  timer resolution, so the H3 ratio point estimate (537.8x) carries
  wide relative error. The REFUTED direction is not in doubt (the
  band edge is 2.0x), but the exact ratio should not be quoted as
  precise.
- No ablation. Neither arm was run with one part removed (for
  example LlamaIndex on 40-word chunks, or production without the
  rerank), so the study cannot say which part of each pipeline
  produces its result. Out of the frozen scope.
- Process cost. Two failed run attempts preceded the scored pass
  (above). No data from either was used.
- Claim gate on REVIEW. The Jev claim_check gate landed on REVIEW
  rather than clear (below), so the headline figures stand on the
  hand verification recorded here rather than on the gate.
- Lock timing rests on git. Commit times are written by the author's
  machine. The order of the commits is proven by git history; the
  GitHub repository was created at 20:45:55 UTC, seven seconds after
  the pre-registration commit time, which is consistent with it, but
  no external clock timestamps the harness before the run.


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
