"""
Loads the FAISS index + chunk metadata built by ingest/build_index.py
and exposes a simple retrieve(query, k) function.
"""

import os
import pickle
import logging

import faiss
from sentence_transformers import SentenceTransformer

from config import INDEX_DIR, CHUNKS_PATH, EMBEDDING_MODEL_NAME, TOP_K_RETRIEVAL

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self):
        index_path = os.path.join(INDEX_DIR, "index.faiss")
        if not os.path.exists(index_path) or not os.path.exists(CHUNKS_PATH):
            raise FileNotFoundError(
                "No index found. Run `python -m ingest.build_index` first "
                "to build the FAISS index from your documents."
            )

        self.index = faiss.read_index(index_path)
        with open(CHUNKS_PATH, "rb") as f:
            self.chunks = pickle.load(f)

        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    def retrieve(self, query: str, k: int = TOP_K_RETRIEVAL) -> list[dict]:
        """Return the top-k most similar chunks to the query, with scores."""
        query_vec = self.model.encode([query], convert_to_numpy=True).astype("float32")
        faiss.normalize_L2(query_vec)

        scores, indices = self.index.search(query_vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            chunk = self.chunks[idx]
            results.append({
                "text": chunk["text"],
                "source": chunk["source"],
                "page": chunk["page"],
                "score": float(score),
            })
        return results
