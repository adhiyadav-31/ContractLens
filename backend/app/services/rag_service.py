"""RAG service: chunking, ChromaDB storage, retrieval. Owned by Safa."""

import chromadb

from app.services.embedding_service import create_embeddings, embed_query
from app.services.pdf_service import PageText

_chroma_client: chromadb.Client | None = None
_COLLECTION_NAME = "contractlens_chunks"

CHUNK_SIZE = 800  # characters
CHUNK_OVERLAP = 150


def _get_collection():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path="./chroma_data")
    return _chroma_client.get_or_create_collection(name=_COLLECTION_NAME)


def chunk_text(pages: list[PageText]) -> list[dict]:
    """Split page text into overlapping chunks, preserving page metadata.

    Returns list of {"text": str, "page": int}.
    """
    chunks: list[dict] = []
    for page in pages:
        text = page.text
        if not text.strip():
            continue
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk_text_value = text[start:end].strip()
            if chunk_text_value:
                chunks.append({"text": chunk_text_value, "page": page.page_number})
            start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def index_contract(contract_id: str, pages: list[PageText]) -> int:
    """Chunk, embed, and store a contract's text in ChromaDB. Returns chunk count."""
    chunks = chunk_text(pages)
    if not chunks:
        return 0

    texts = [c["text"] for c in chunks]
    embeddings = create_embeddings(texts)

    ids = [f"{contract_id}-chunk-{i}" for i in range(len(chunks))]
    metadatas = [
        {"contract_id": contract_id, "page": c["page"], "chunk_id": ids[i]}
        for i, c in enumerate(chunks)
    ]

    collection = _get_collection()
    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    return len(chunks)


def retrieve_relevant_chunks(contract_id: str, query: str, top_k: int = 5) -> list[dict]:
    """Retrieve the top_k most relevant chunks for a query, scoped to one contract.

    Returns list of {"text": str, "page": int, "chunk_id": str, "section": str|None}.
    """
    collection = _get_collection()
    query_embedding = embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"contract_id": contract_id},
    )

    chunks: list[dict] = []
    if not results.get("documents"):
        return chunks

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    for doc, meta in zip(documents, metadatas):
        chunks.append(
            {
                "text": doc,
                "page": meta.get("page"),
                "chunk_id": meta.get("chunk_id"),
                "section": meta.get("section"),
            }
        )
    return chunks
