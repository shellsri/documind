# DocuMind — RAG + NL2SQL Assistant

A local, API-independent AI assistant that combines two capabilities in one app:

1. **Document Q&A (RAG)** — ask natural-language questions over your own PDFs
   (including scanned/image PDFs via OCR), with answers grounded in retrieved
   passages and cited by source + page.
2. **NL2SQL Query** — ask natural-language questions against a structured
   database and get back generated SQL + results, with a safety guard that
   only allows read-only `SELECT` queries.

Built to be runnable fully offline once models are downloaded — no dependency
on paid APIs unless you choose to plug one in.

---

## Architecture

```
documind/
├── ingest/
│   ├── pdf_loader.py      # PyPDF2 text extraction + Tesseract OCR fallback for scanned pages
│   └── build_index.py     # Chunking, MiniLM embeddings, FAISS index build
├── rag/
│   ├── retriever.py       # FAISS similarity search over indexed chunks
│   └── qa_chain.py        # Grounded prompt construction + FLAN-T5 generation
├── nl2sql/
│   ├── schema.py          # Synthetic SQLite DB (personnel/departments/requisitions)
│   └── query_engine.py    # NL -> SQL generation (local FLAN-T5 or OpenAI-compatible) + SQL safety guard
├── sample_docs/
│   └── generate_samples.py # Generates demo PDFs so the app works out of the box
├── app.py                 # Streamlit UI: Document Q&A / NL2SQL / Upload & Index tabs
├── config.py               # All paths + model names in one place
└── requirements.txt
```

**Tech stack:** Python, PyTorch, Hugging Face Transformers, Sentence-Transformers
(all-MiniLM-L6-v2), FAISS, FLAN-T5, LangChain, SQLAlchemy, PyPDF2, pytesseract,
Streamlit, pandas.

---

## Setup (run these on your own machine — this repo was built in a sandboxed
environment without access to huggingface.co, so model downloads happen on first run)

```bash
# 1. Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. (Optional, for OCR on scanned PDFs) install system dependencies
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr poppler-utils
# macOS:
brew install tesseract poppler

# 4. Generate sample documents (or drop your own PDFs into sample_docs/)
python sample_docs/generate_samples.py

# 5. Build the NL2SQL demo database
python -m nl2sql.schema

# 6. Build the FAISS index from sample_docs/
python -m ingest.build_index

# 7. Launch the app
streamlit run app.py
```

The first run of steps 6 and 7 will download `all-MiniLM-L6-v2` and
`flan-t5-base` from Hugging Face (a few hundred MB total) — this needs
internet access once, then everything runs locally.

---

## Using an OpenAI-compatible API for better NL2SQL (optional)

The local FLAN-T5 backend works fully offline but is weaker on complex SQL
joins. If you have an API key, create a `.env` file:

```
OPENAI_API_KEY=your_key_here
```

then select the "openai" backend in the NL2SQL tab for noticeably better
query generation.

---

## Why this project

Built specifically to demonstrate practical, hands-on experience with:
- Retrieval-Augmented Generation (embeddings, vector search, grounded generation)
- Document intelligence (PDF parsing, OCR for scanned documents)
- Natural Language to SQL pipelines with safety guards
- Prompt engineering (few-shot prompting for structured output)
- Vector databases (FAISS)
- Full local/offline AI system design (no dependency on external inference APIs)
- Streamlit dashboarding

This maps directly onto the AI/ML engineering skill sets requested in current
internship postings emphasizing RAG pipelines, LLM-based assistants, NL2SQL,
document intelligence, and vector database implementation.
