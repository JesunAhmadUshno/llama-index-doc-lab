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
