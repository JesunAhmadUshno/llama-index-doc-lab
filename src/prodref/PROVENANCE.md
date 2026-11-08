# Provenance of the vendored rag-foundation code

corpus.py and pipeline.py in this directory are verbatim copies of
level-2-build/corpus.py and level-2-build/pipeline.py from
JesunAhmadUshno/rag-foundation at commit
007e33238e6ce49100650b30f6820149410f022b, the pinned production
subject of this study (see PREREGISTRATION.md). They are the same
copies mlops-evidence-lab vendored and evaluated as its Half 2
subject. sha256: corpus.py
509021670026878115987d61f0efd9e615f24660a895c03b407ad6ab38458521,
pipeline.py
3776947f1b0dacf7da55861dec3c94b07b849e6e6ddb3d3da693f1e731a00f62.
The subject repository is Apache-2.0 licensed; its LICENSE terms
apply to these files. The subject repository is never modified by
this lab; the copy exists so the evaluated system is byte-identical
to the pinned subject and the study reproduces from this repo alone.

data/questions.json is a byte-identical copy of the frozen question
set from JesunAhmadUshno/mlops-evidence-lab (built in that
repository's commit 25fe70a, unchanged at its HEAD
6ee6ef19432bc65522454fb0b708af7d5eda8e50; sha256
f1b52a8d79ca1315f7a632cc659118101fab11821fe97d6b20d2d39a9ae0079b).
