"""Embedding functionality for RAG. Owned by Safa.

Uses the Gemini embedding model so we don't need a second API key/provider.
"""

import os

from google import genai

_client: genai.Client | None = None

EMBEDDING_MODEL = "text-embedding-004"


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in the environment (.env)")
        _client = genai.Client(api_key=api_key)
    return _client


def create_embeddings(text_chunks: list[str]) -> list[list[float]]:
    """Create embeddings for a batch of text chunks (used when indexing a contract)."""
    client = _get_client()
    embeddings: list[list[float]] = []
    for chunk in text_chunks:
        result = client.models.embed_content(model=EMBEDDING_MODEL, contents=chunk)
        embeddings.append(result.embeddings[0].values)
    return embeddings


def embed_query(query: str) -> list[float]:
    """Create a single embedding for a user question (used at retrieval time)."""
    client = _get_client()
    result = client.models.embed_content(model=EMBEDDING_MODEL, contents=query)
    return result.embeddings[0].values
