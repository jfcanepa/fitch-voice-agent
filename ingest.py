"""
ingest.py — Fetch a Fitch report by URL and index it into ChromaDB.

Uses r.jina.ai to render JS-heavy Fitch pages into clean markdown.
Embeddings are generated locally via ChromaDB's built-in model (no API cost).

Usage:
    python ingest.py                          # prompted for URL interactively
    python ingest.py <url>                    # pass URL as argument
"""

import hashlib
import os
import sys

import chromadb
import requests
import tiktoken
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = "fitch_reports"
CHUNK_TOKENS = 400
CHUNK_OVERLAP = 50
JINA_PREFIX = "https://r.jina.ai/"

enc = tiktoken.get_encoding("cl100k_base")
embed_fn = DefaultEmbeddingFunction()


def get_collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},
    )


def fetch_report(url: str) -> tuple[str, str]:
    """Fetch a Fitch report page via Jina reader. Returns (title, text)."""
    print(f"Fetching: {url}")
    r = requests.get(JINA_PREFIX + url, timeout=60, headers={"Accept": "text/markdown"})
    r.raise_for_status()
    text = r.text

    title = url
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("Title:"):
            title = line.removeprefix("Title:").strip()
            break
        if line and not line.startswith("URL"):
            title = line.lstrip("#").strip()
            break

    return title, text


def chunk_text(text: str) -> list[str]:
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + CHUNK_TOKENS, len(tokens))
        chunks.append(enc.decode(tokens[start:end]))
        start += CHUNK_TOKENS - CHUNK_OVERLAP
    return chunks


def ingest_url(url: str) -> int:
    """Fetch, chunk, embed and store a report. Returns number of chunks added."""
    url = url.strip()
    collection = get_collection()

    doc_id = hashlib.md5(url.encode()).hexdigest()
    if collection.get(ids=[f"{doc_id}_0"])["ids"]:
        print(f"Already indexed: {url}")
        return 0

    title, text = fetch_report(url)
    if not text.strip():
        print("No content extracted.")
        return 0

    chunks = chunk_text(text)
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    metas = [{"url": url, "title": title, "chunk": i} for i in range(len(chunks))]

    # Embeddings generated locally by ChromaDB — no API call needed
    collection.add(ids=ids, documents=chunks, metadatas=metas)
    print(f"Indexed '{title}' — {len(chunks)} chunks.")
    return len(chunks)


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Paste the Fitch report URL: ").strip()

    if not url:
        print("No URL provided.")
        sys.exit(1)

    ingest_url(url)


if __name__ == "__main__":
    main()
