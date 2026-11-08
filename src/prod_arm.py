"""Production arm: the vendored rag-foundation Build pipeline.

Wraps src/prodref (byte-identical to rag-foundation at the pinned
commit) and exposes the two operations the study needs: build the
pipeline over the corpus, and retrieve a document ranking plus the
top-1 retrieval score (coverage of the top-1 reranked chunk) for a
question. The document ranking is the pipeline's full reranked
chunk ranking collapsed by its own doc_ranking function, the same
derivation mlops-evidence-lab used for its top1_doc record.
"""

import pickle

from src.prodref.corpus import DOCUMENTS
from src.prodref.pipeline import RagPipeline, doc_ranking


def build():
    """Construct the production pipeline over the corpus."""
    return RagPipeline(DOCUMENTS)


def retrieve(pipeline, question):
    """Return (ranked_docs, top1_score, n_chunks_returned).

    top1_score is the coverage of the top-1 reranked chunk, or None
    when the ranking is empty.
    """
    stages = pipeline.rankings(question)
    reranked = stages["reranked"]
    ranked_docs = doc_ranking([entry["chunk"] for entry in reranked])
    top1_score = reranked[0]["coverage"] if reranked else None
    return ranked_docs, top1_score, len(reranked)


def index_state_bytes(pipeline):
    """Byte size of a pickle of the arm's index state, the frozen
    on-disk size definition for this in-memory design."""
    state = {
        "chunks": pipeline.chunks,
        "bm25_idf": pipeline.bm25.idf,
        "bm25_tf": pipeline.bm25._tf,
        "bm25_doc_tokens": pipeline.bm25.doc_tokens,
        "bm25_avgdl": pipeline.bm25.avgdl,
        "vector_idf": pipeline.vector.idf,
        "vector_vectors": pipeline.vector.vectors,
    }
    return len(pickle.dumps(state))
