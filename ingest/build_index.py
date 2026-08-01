"""
Turns extracted PDF pages into overlapping text chunks, embeds them with
all-MiniLM-L6-v2, and builds a FAISS index for similarity search.

Run directly:
    python -m ingest.build_index
to (re)build the index from everything in sample_docs/.
"""

import os
import pickle
import logging

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config import (
    SAMPLE_DOCS_DIR, INDEX_DIR, CHUNKS_PATH,
    EMBEDDING_MODEL_NAME, CHUNK_SIZE, CHUNK_OVERLAP,
)
from ingest.pdf_loader import load_pdf_directory

logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Simple sliding-window character chunker with overlap."""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def build_chunks_from_pages(pages: list[dict]) -> list[dict]:
    """Convert page-level text into chunk-level records, preserving source/page."""
    chunks = []
    for page in pages:
        for i, chunk in enumerate(chunk_text(page["text"])):
            chunks.append({
                "text": chunk,
                "source": page["source"],
                "page": page["page"],
                "chunk_id": f"{page['source']}_p{page['page']}_c{i}",
            })
    return chunks


def build_index(source_dir: str = SAMPLE_DOCS_DIR):
    logging.basicConfig(level=logging.INFO)

    logger.info(f"Loading PDFs from {source_dir} ...")
    pages = load_pdf_directory(source_dir)
    logger.info(f"Loaded {len(pages)} pages")

    chunks = build_chunks_from_pages(pages)
    logger.info(f"Built {len(chunks)} chunks")

    logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    embeddings = embeddings.astype("float32")

    # Normalize for cosine similarity via inner product
    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    os.makedirs(INDEX_DIR, exist_ok=True)
    faiss.write_index(index, os.path.join(INDEX_DIR, "index.faiss"))

    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    logger.info(f"Index built with {index.ntotal} vectors -> saved to {INDEX_DIR}")
    return index, chunks


if __name__ == "__main__":
    build_index()
