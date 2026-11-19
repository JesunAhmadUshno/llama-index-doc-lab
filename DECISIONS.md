# DECISIONS

D1, embedding route is local. The brief offered a local embedding
model or the connected Gemini route. The sibling studies recorded
the Gemini route rate-limiting under burst load (document
intelligence: 27 HTTP 429 responses in one pass; mlops: scoring
never completed). This study's scope is retrieval only, so the
local route removes a known failure mode at no cost to the
question: sentence-transformers/all-MiniLM-L6-v2, the canonical
tutorial embedding, at the frozen revision in PREREGISTRATION.md.

D2, environment install route. The first pip install failed on
disk space because pip unpacks wheels in /tmp, a 512 MB tmpfs on
this VM; the install was rerun with TMPDIR on the workspace disk.
The default PyPI torch wheel bundles CUDA libraries; the study
installs torch 2.15.0+cpu from the PyTorch CPU index instead, and
requirements.txt notes the route. Neither change touches a frozen
element: versions were recorded before the freeze, and the freeze
pins what is installed.

D3, production score is top-1 chunk coverage. The pre-registration
needs one retrieval score per arm for the floor rule. For the
production arm the score is the coverage of the top-1 reranked
chunk, because coverage is the pipeline's own rerank currency (its
first sort key). The alternative, the RRF hybrid score, is a rank
artifact with no per-question meaning. Recorded here because the
pre-registration states the choice and this file states the reason.

D4, first run attempt failed at embedding load, before any scored
record existed. The initial snapshot_download of the embedding
model had been interrupted (a stalled transfer, killed), leaving
an incomplete snapshot; the offline load in run_study.py therefore
raised before any arm was built. The model load was completed
during harness debugging (one online load), offline loading was
then verified, and the study proceeded. No raw records were
written by the failed attempt.

D5, second run attempt executed the full protocol but failed at
the final write: the results/ directory did not exist in the fresh
clone layout, so raw_runs.json was never persisted and every
measurement from that pass was lost. Harness bug, ours. The fix
(run_study.py creates the directory) is in the harness commit
history, and the study was rerun from scratch, both arms, exactly
as the stop rule in PREREGISTRATION.md requires. The pass reported
in RESULTS.md is that rerun, and it is the only pass whose records
exist.

D6, post-registration analysis registered: H2 floor sensitivity
(registered 2026-11-17, before the analysis was run). AUDIT.md
deducts 600 because H2 turns on the frozen own-floor rule (each
arm's own 10th percentile of its 28 in-corpus top-1 scores) and a
different defensible floor moves the rates. This entry registers a
sensitivity analysis over floors, computed only from the committed
records of the scored pass (results/raw_runs.json); the study is
not rerun and no frozen element changes. Method: the repository's
own src/metrics.py percentile (linear interpolation, the numpy
default) and spurious_rate, the same functions
scripts/make_results.py uses. Floors, each arm's floor computed
from that arm's 28 in-corpus top-1 scores unless stated: (a) own
5th percentile; (b) own 10th percentile, the frozen rule, kept as
the reference point and expected to reproduce the published
floors (production 0.2350, LlamaIndex 0.5481) and rates (9 of 12,
5 of 12) exactly, as an integrity check on the analysis itself;
(c) own 25th percentile; (d) one shared absolute floor of 0.50
applied identically to both arms, defensible because both arms'
top-1 scores live on the same [0, 1] scale (production: coverage,
the share of distinct query content terms in the top-1 chunk;
LlamaIndex: cosine similarity), so 0.50 is the common scale
midpoint. For each floor the analysis reports both arms'
spurious counts and rates, the absolute difference, and which
arm is higher. Outputs go to new files only
(scripts/h2_floor_sensitivity.py, results/h2_floor_sensitivity.json,
results/h2_floor_sensitivity.md). This is a post-registration,
exploratory analysis: the frozen H2 verdict (CONFIRMED,
difference 0.3333 under the frozen floor) is unchanged by
anything it finds; it measures how definition-sensitive the
comparison is, which is the question AUDIT.md raises.

D7, correction of record: corpus word counts in
PREREGISTRATION.md (2026-11-17). PREREGISTRATION.md states, in
Fixed inputs and again in Arms, that the corpus documents run
"72 to 87 words each, 1,588 words in total". Those figures are
wrong. Measured on the committed corpus (the 20 documents of
DOCUMENTS in src/prodref/corpus.py, the vendored byte-identical
copy of JesunAhmadUshno/rag-foundation's corpus.py at commit
007e33238e6ce49100650b30f6820149410f022b), counting a word as a
whitespace-delimited token (len(text.split()),
scripts/corpus_word_counts.py, output
results/corpus_word_counts.json): the documents run 54 words
(water-cycle) to 73 words (earthquakes) each, 1,208 words in
total. PREREGISTRATION.md is a frozen record and is not edited;
this entry is the correction of record. The paper
(llama-index-doc-lab preprint, 2026-11-17) already flags this
discrepancy and reports the measured counts (54 to 73 words per
document, 1,208 total). Nothing in the study turns on the wrong
figures: the arms, the question set, the node count of 20 and
every measured result are unaffected, because the harness reads
the corpus itself, not the pre-registration's description of it.
AUDIT.md's minus-1,800 deduction quotes the wrong total (1,588
words) in passing; the deduction and its reason (a tiny synthetic
corpus) stand, on the corrected total of 1,208.
