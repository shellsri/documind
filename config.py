"""
Central configuration for DocuMind.
Keeping all paths/model names in one place makes it trivial to swap
models later (e.g. FLAN-T5-base -> FLAN-T5-large) without touching
the rest of the codebase.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Data locations ---
SAMPLE_DOCS_DIR = os.path.join(BASE_DIR, "sample_docs")
DATA_DIR = os.path.join(BASE_DIR, "data")
INDEX_DIR = os.path.join(DATA_DIR, "faiss_index")
CHUNKS_PATH = os.path.join(DATA_DIR, "chunks.pkl")
SQLITE_DB_PATH = os.path.join(DATA_DIR, "records.db")

# --- Embedding model (same one used in the original RAG pipeline) ---
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output size

# --- Generation model for RAG answers ---
GENERATION_MODEL_NAME = "google/flan-t5-base"

# --- Chunking ---
CHUNK_SIZE = 500          # characters per chunk
CHUNK_OVERLAP = 80        # overlap between consecutive chunks
TOP_K_RETRIEVAL = 4       # number of chunks retrieved per query

# --- OCR ---
# If a PDF page has less than this many extracted characters via PyPDF2,
# we treat it as a scanned page and fall back to OCR.
OCR_FALLBACK_CHAR_THRESHOLD = 30

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SAMPLE_DOCS_DIR, exist_ok=True)
