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
