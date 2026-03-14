"""
agent.py — RAG query agent over the indexed Fitch reports.

Retrieves relevant chunks from ChromaDB, then calls Claude to synthesise
a concise, spoken-language answer grounded in those chunks.
"""

import os

import chromadb
import anthropic
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

COLLECTION_NAME = "fitch_reports"
CLAUDE_MODEL = "claude-sonnet-4-6"
TOP_K = 6

embed_fn = DefaultEmbeddingFunction()

SYSTEM_PROMPT = """You are a structured finance analyst assistant with deep expertise in \
Fitch Ratings methodology. You answer questions strictly based on the provided report \
excerpts. If the answer cannot be found in the excerpts, say so clearly. \
Keep answers concise (3-5 sentences) and suitable for text-to-speech — avoid bullet \
points, tables, markdown, or special characters."""


def get_collection() -> chromadb.Collection:
    chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    db = chromadb.PersistentClient(path=chroma_dir)
    return db.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
    )


def retrieve(query: str, collection: chromadb.Collection, url_filter: str | None = None) -> list[dict]:
    where = {"url": url_filter} if url_filter else None
    results = collection.query(
        query_texts=[query],
        n_results=TOP_K,
        include=["documents", "metadatas", "distances"],
        where=where,
    )
    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": doc,
            "source": meta.get("url", ""),
            "title": meta.get("title", ""),
            "score": 1 - dist,
        })
    return chunks


def build_context(chunks: list[dict]) -> str:
    parts = []
    for i, c in enumerate(chunks, 1):
        parts.append(f"[{i}] {c['title']}\n{c['text']}")
    return "\n\n---\n\n".join(parts)


def answer(query: str, verbose: bool = False, url_filter: str | None = None) -> str:
    collection = get_collection()

    if collection.count() == 0:
        return "No reports have been indexed yet. Add one using the sidebar."

    chunks = retrieve(query, collection, url_filter=url_filter)

    if verbose:
        print("\n[Retrieved chunks]")
        for c in chunks:
            print(f"  score={c['score']:.3f}  {c['title'][:60]}  {c['text'][:80]!r}")

    context = build_context(chunks)

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Report excerpts:\n\n{context}\n\nQuestion: {query}",
            }
        ],
    )
    return response.content[0].text.strip()
