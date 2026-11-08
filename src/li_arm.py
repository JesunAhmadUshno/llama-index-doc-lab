"""LlamaIndex arm: framework defaults over the identical corpus.

The index is built by VectorStoreIndex.from_documents with no
transformations argument, so the default SentenceSplitter applies
(chunk_size 1024 tokens, chunk_overlap 20) and the default in-memory
SimpleVectorStore holds the vectors. The embedding model object is
injected by the caller (the study passes the frozen local
HuggingFaceEmbedding; the tests pass a MockEmbedding), so this
module imports llama_index.core only.

Each source Document carries its corpus id in metadata under
doc_id; built nodes inherit it, and the document ranking is the
node order mapped through that metadata.
"""

import os

from llama_index.core import Document, VectorStoreIndex


def build(documents, embed_model):
    """Build the index over (doc_id, text) pairs, in order.

    Returns (index, node_count).
    """
    docs = [
        Document(text=text, metadata={"doc_id": doc_id})
        for doc_id, text in documents
    ]
    index = VectorStoreIndex.from_documents(docs, embed_model=embed_model)
    node_count = len(index.docstore.docs)
    return index, node_count


def retrieve(index, question, top_k):
    """Return (ranked_docs, top1_score, n_nodes_returned).

    top1_score is the cosine similarity of the top-1 node as
    returned by the retriever, or None when nothing is returned.
    """
    retriever = index.as_retriever(similarity_top_k=top_k)
    hits = retriever.retrieve(question)
    ranked_docs = [hit.node.metadata["doc_id"] for hit in hits]
    top1_score = float(hits[0].score) if hits else None
    return ranked_docs, top1_score, len(hits)


def index_size_bytes(index, persist_dir):
    """Persist the index and return the total bytes on disk."""
    index.storage_context.persist(persist_dir=persist_dir)
    total = 0
    for root, _dirs, files in os.walk(persist_dir):
        for name in files:
            total += os.path.getsize(os.path.join(root, name))
    return total
