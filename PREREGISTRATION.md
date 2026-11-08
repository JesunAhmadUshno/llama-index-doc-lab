# PREREGISTRATION: LlamaIndex Indexing and Retrieval versus the rag-foundation Production Pipeline

Frozen before any measured run in this repository. This file is the
first content commit. Nothing in it changes after the freeze; any
harness bug found later is logged in DECISIONS.md and the whole study
is rerun from scratch under the stop rule below.

Date of freeze: 2026-11-08.
Machine of record: htch-runtime (Linux 7.0.0-43-generic, x86_64,
4 vCPU, 8 GiB RAM), Python 3.12.3. All runs happen on this machine.

## Problem

Every team adopting a retrieval framework bets its search quality on
defaults it has not measured: chunk size, embedding model, vector
store, retriever behaviour. The bet is usually taken on documentation
and reputation. This study makes the bet a number on one fixed corpus
and one frozen question set, against the retrieval pipeline Jesun
already built and measured in rag-foundation (P05).

## Research question

On one fixed document corpus and one frozen question set, does
LlamaIndex's indexing and retrieval stack beat, match, or trail the
retrieval approach already built and measured in the rag-foundation
project, on retrieval accuracy, behaviour under out-of-corpus
questions, and indexing cost?

## Fixed inputs

Corpus and production code, pinned and read-only:

- JesunAhmadUshno/rag-foundation at commit
  007e33238e6ce49100650b30f6820149410f022b. The files
  level-2-build/corpus.py and level-2-build/pipeline.py are vendored
  byte-identical under src/prodref/ (sha256 corpus.py
  509021670026878115987d61f0efd9e615f24660a895c03b407ad6ab38458521,
  pipeline.py
  3776947f1b0dacf7da55861dec3c94b07b849e6e6ddb3d3da693f1e731a00f62),
  the same copies mlops-evidence-lab evaluated. The subject
  repository is never modified.
- The corpus is the 20 synthetic documents of that file: 72 to 87
  words each, 1,588 words in total, across 7 topics that deliberately
  share vocabulary, including three Northlight library documents that
  differ only in their facts.

Question set, frozen, imported verbatim:

- data/questions.json in this repository is a byte-identical copy of
  data/questions.json from JesunAhmadUshno/mlops-evidence-lab
  (question set built in that repository's commit 25fe70a, file
  unchanged at its HEAD 6ee6ef19432bc65522454fb0b708af7d5eda8e50;
  sha256 of the file
  f1b52a8d79ca1315f7a632cc659118101fab11821fe97d6b20d2d39a9ae0079b).
- 40 records: 28 in the in_corpus slice, each with one expected_doc
  among the 20 corpus documents; 12 in the adversarial slice
  (absent_detail, false_premise, out_of_corpus), with no expected
  document. No question is rewritten, added, or dropped.

## Arms

Production arm (PROD): the vendored RagPipeline with its shipped
defaults (chunk 40 words, 10 words overlap; BM25 k1 = 1.5, b = 0.75;
TF-IDF cosine; reciprocal rank fusion K = 60; rerank of the top 8 by
coverage, then token F1, then hybrid score). The document ranking is
the pipeline's full reranked chunk ranking collapsed to documents by
its own doc_ranking function, the same derivation
mlops-evidence-lab used for its top1_doc record. The arm's retrieval
score for a question is the coverage of its top-1 reranked chunk
(the share of distinct query content terms that chunk contains, the
pipeline's rerank currency). The arm is lexical by design: it has no
dense embedding, and no file here claims otherwise.

LlamaIndex arm (LI): llama-index 0.14.25 (llama-index-core 0.14.25,
llama-index-embeddings-huggingface 0.8.0, sentence-transformers
6.2.0, torch 2.15.0+cpu, numpy 2.5.4). VectorStoreIndex built by
from_documents over llama_index Documents carrying doc_id equal to
the corpus id and the document text, in corpus order. All framework
defaults are kept: SentenceSplitter chunk_size 1024 tokens and
chunk_overlap 20; the default in-memory SimpleVectorStore; the
default embed batch size. The documents run 72 to 87 words, far
below 1024 tokens, so each document yields exactly one node; the
node count is verified at run time and reported (expected 20). The
chunking contrast with the production arm (40-word windows versus
whole-document nodes) is a consequence of the framework's defaults
on this corpus and is part of what is measured, not a setting tuned
for this study. Embedding: HuggingFaceEmbedding with the local model
sentence-transformers/all-MiniLM-L6-v2 at revision
1110a243fdf4706b3f48f1d95db1a4f5529b4d41, on CPU. The route is
local on purpose: the sibling studies recorded the connected Gemini
route rate-limiting under burst load, and this study's scope is
retrieval only, so no external route is needed. Retrieval:
index.as_retriever with similarity_top_k set to the number of nodes,
so the full node ranking is returned and scored; the document
ranking is the node order mapped through doc_id. The arm's
retrieval score for a question is the cosine similarity of its
top-1 node, as returned by the retriever.

Both arms index the identical 20 document texts and nothing else.

## Harness integrity gate (stop rule)

Before any LlamaIndex figure is scored, the production arm must
reproduce the sibling record: mlops-evidence-lab measured the
production pipeline's in-corpus top-1 document hit as 23 of 28
(results/rag_samples.json, field top1_doc). If this harness's
production top-1 differs, the study stops, the cause is fixed,
DECISIONS.md records it, and the whole study reruns from scratch.
A production number that cannot reproduce the sibling measurement
would mean the comparison measures the harness, not the framework.

## Measures

All measures are computed by scripts/make_results.py from the raw
records written by scripts/run_study.py. Verdicts come from that
script, never from hand arithmetic.

In-corpus accuracy (n = 28): top-1 hit rate (expected doc first in
the document ranking), top-5 hit rate (expected doc among the first
5), and mean reciprocal rank of the expected doc over the full
document ranking (0 when absent).

Adversarial behaviour (n = 12): the spurious retrieval rate under
this frozen floor rule. For each arm, the floor is the 10th
percentile (numpy percentile, linear interpolation) of that arm's
top-1 retrieval scores across the 28 in-corpus questions: each arm
is held to the standard of its own weakest genuine matches. An
adversarial question counts as spuriously retrieved when the arm
returns at least one item and its top-1 score is at or above its
floor. An arm that returns nothing for a question does not
spuriously retrieve it. Both floor values and every question's
top-1 score are published, so any other floor can be applied by
the reader.

Latency: one untimed warm-up pass over all 40 questions per arm,
then 3 timed passes in file order. A question's latency is the
median of its 3 timed passes. LI latency is the retriever.retrieve
call including query embedding; PROD latency is the pipeline
rankings call. Arm figures are the median and the 95th percentile
(numpy percentile, linear interpolation) of the per-question
medians over the 28 in-corpus questions; adversarial latencies are
in the raw table.

Index build time: median of 3 fresh builds, wall clock. PROD build
is RagPipeline construction (chunking plus both retriever indexes).
LI build is VectorStoreIndex.from_documents (splitting, embedding,
vector store insert); the embedding model load happens once before
timing and is excluded, and that exclusion is stated wherever the
figure appears. Per-document build time is the total divided by 20.

Index size on disk: LI is the total bytes of the directory written
by index.persist. PROD, which ships as an in-memory design, is the
byte size of a pickle of its index state (chunks, BM25 idf, term
frequencies, document tokens and average length, vector idf and
vectors) written by the harness. The embedding model's own files
are shared local infrastructure and are excluded from the LI
figure; that exclusion is stated wherever the figure appears.

## Hypotheses and verdict lines

- H1: the arms differ on in-corpus top-5 hit rate by a real margin.
  CONFIRMED when the absolute difference of the two top-5 hit
  rates is at least 0.10 (about 3 of 28 questions); REFUTED when
  it is below 0.10 (a tie inside the band); INCONCLUSIVE only
  when a run failure makes scoring impossible.
- H2: the arms differ on adversarial behaviour. CONFIRMED when
  the absolute difference of the two spurious retrieval rates is
  at least 0.25 (3 of 12 questions); REFUTED when it is below
  0.25; INCONCLUSIVE as above.
- H3: LlamaIndex indexing costs about the same per document as
  the production build. CONFIRMED when the ratio of LI to PROD
  per-document build time lies within [0.5, 2.0]; REFUTED when
  it lies outside; INCONCLUSIVE as above.

Verdict language is CONFIRMED, REFUTED, or INCONCLUSIVE, published
either way.

## Protocol

One scored pass, as registered. No scored query is rerun after
its results are seen. If a harness bug is found after the pass,
DECISIONS.md records it and the whole study reruns from scratch,
both arms, with the earlier raw file discarded and the reason on
record. Scope is indexing and retrieval only: no answer
generation, no LLM judge, no network calls during the scored runs.
