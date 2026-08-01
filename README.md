# 📄 DocuMind AI

<p align="center">

Enterprise Document Intelligence Platform powered by
<b>Retrieval-Augmented Generation (RAG)</b>,
<b>FAISS Vector Search</b>,
<b>Natural Language SQL</b>, and
<b>OCR-enabled PDF Processing</b>.

</p>

---

## 🚀 Overview

DocuMind AI is an offline-first enterprise document intelligence platform that enables users to:

- 📄 Upload PDF documents
- 🔍 Perform semantic search using FAISS
- 🤖 Ask questions using Retrieval-Augmented Generation (RAG)
- 📚 Receive grounded answers with document citations
- 🗄 Query structured databases using Natural Language
- 🧾 Automatically extract text from scanned PDFs using OCR

The application combines document understanding and database querying into a single intelligent interface.

---

# ✨ Features

### 🤖 AI Document Assistant

- Semantic document search
- Retrieval-Augmented Generation
- Source citations
- Multi-document support
- Offline inference using FLAN-T5

---

### 📊 Natural Language SQL

Ask questions like:

> Which department has the most personnel?

> Show all pending requisitions

> Count active employees

DocuMind automatically generates SQL, executes it, and displays the results.

---

### 📂 Knowledge Base

- Upload multiple PDFs
- Automatic indexing
- FAISS vector database
- OCR support for scanned PDFs
- Rebuild index with one click

---

## 🏗 Architecture

```

User

↓

Streamlit UI

↓

Question

↓

Sentence Transformer Embeddings

↓

FAISS Vector Search

↓

Top Relevant Chunks

↓

FLAN-T5

↓

Grounded Answer

↓

Source Citations

```

---

# 🖥 Screenshots

## Home

![Home](screenshots/home.png)

---

## AI Assistant

![Assistant](screenshots/chat.png)

---

## SQL Assistant

![SQL](screenshots/sql.png)

---

## Knowledge Base

![Knowledge Base](screenshots/upload.png)

---

# 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| Frontend | Streamlit |
| LLM | Google FLAN-T5 |
| Embeddings | Sentence Transformers |
| Vector DB | FAISS |
| OCR | Tesseract OCR |
| Database | SQLite |
| NLP Framework | LangChain |
| ML Framework | PyTorch |

---

# 📂 Project Structure

```

DocuMind

├── app.py

├── config.py

├── data/

├── ingest/

├── rag/

├── nl2sql/

├── sample_docs/

├── requirements.txt

└── README.md

```

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/shellsri/documind.git
```

Move inside the project

```bash
cd documind
```

Create a virtual environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Generate sample documents

```bash
python sample_docs/generate_samples.py
```

Create SQL schema

```bash
python -m nl2sql.schema
```

Build vector index

```bash
python -m ingest.build_index
```

Launch

```bash
streamlit run app.py
```

---

# 📊 Example Queries

### Document Assistant

- What is the internship leave policy?
- Explain reimbursement rules.
- What documents are required for onboarding?

### Database Assistant

- Count all employees.
- Which department has the highest personnel?
- Show pending requisitions.
- Average salary by department.

---

# 🌟 Highlights

- Enterprise UI
- Offline AI Support
- OCR-enabled PDF Processing
- Semantic Search
- Grounded Responses
- Source Citations
- Natural Language SQL
- FAISS Vector Database

---

# 🚀 Future Improvements

- Authentication
- Hybrid Search (BM25 + FAISS)
- Cross Encoder Reranking
- Chat History
- Streaming Responses
- Multi-user Workspaces
- Cloud Deployment
- Docker Support

---

# 👩‍💻 Author

**Shelly Srivastava**

GitHub

https://github.com/shellsri

---

## ⭐ If you found this project useful, consider starring the repository.
