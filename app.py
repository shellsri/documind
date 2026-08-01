"""
DocuMind — Streamlit front-end.

Three tabs:
  1. Document Q&A   — ask questions grounded in your indexed PDFs (RAG)
  2. NL2SQL Query    — ask questions in plain English against the records DB
  3. Upload & Index  — drop in new PDFs and rebuild the FAISS index

Run with:  streamlit run app.py
"""

import os
import streamlit as st

from config import SAMPLE_DOCS_DIR, SQLITE_DB_PATH

st.set_page_config(page_title="DocuMind", page_icon="📄", layout="wide")

st.title("📄 DocuMind — RAG + NL2SQL Assistant")
st.caption("Local, API-independent document Q&A and natural-language database queries.")

tab_qa, tab_sql, tab_upload = st.tabs(["💬 Document Q&A", "🗄️ NL2SQL Query", "📤 Upload & Index"])


# ---------------------------------------------------------------------------
# Tab 1: Document Q&A (RAG)
# ---------------------------------------------------------------------------
with tab_qa:
    st.subheader("Ask a question about your indexed documents")

    index_exists = os.path.exists(os.path.join("data", "faiss_index", "index.faiss"))
    if not index_exists:
        st.warning(
            "No index found yet. Go to **Upload & Index** to add PDFs and build the index, "
            "or run `python -m ingest.build_index` from the terminal."
        )
    else:
        question = st.text_input("Your question", placeholder="e.g. What is the leave policy for interns?")
        if st.button("Get Answer", type="primary") and question:
            with st.spinner("Retrieving relevant passages and generating an answer..."):
                from rag.qa_chain import RAGQuestionAnswerer

                if "rag_qa" not in st.session_state:
                    st.session_state.rag_qa = RAGQuestionAnswerer()

                result = st.session_state.rag_qa.answer(question)

            st.markdown("### Answer")
            st.write(result["answer"])

            if result["sources"]:
                st.markdown("### Sources")
                for src in result["sources"]:
                    st.markdown(f"- `{src['source']}` — page {src['page']} (relevance: {src['score']})")


# ---------------------------------------------------------------------------
# Tab 2: NL2SQL Query
# ---------------------------------------------------------------------------
with tab_sql:
    st.subheader("Query the records database in plain English")
    st.caption(
        "Backed by a synthetic personnel/requisitions database. "
        "Try: *'How many requisitions are still pending?'* or "
        "*'Which department has the most personnel?'*"
    )

    backend = st.radio("LLM backend", ["local (offline)", "openai (needs API key)"], horizontal=True)
    nl_question = st.text_input("Your question", key="sql_question",
                                  placeholder="e.g. Which department has the most personnel?")

    if st.button("Run Query", type="primary") and nl_question:
        with st.spinner("Generating SQL and executing..."):
            from nl2sql.query_engine import NL2SQLEngine

            backend_key = "openai" if backend.startswith("openai") else "local"
            cache_key = f"nl2sql_engine_{backend_key}"
            if cache_key not in st.session_state:
                st.session_state[cache_key] = NL2SQLEngine(backend=backend_key)

            result = st.session_state[cache_key].query(nl_question)

        st.markdown("### Generated SQL")
        st.code(result["sql"], language="sql")

        if result["error"]:
            st.error(f"Query failed: {result['error']}")
            st.info("Local FLAN-T5 isn't fine-tuned for SQL, so complex questions may need rephrasing "
                     "or the openai backend for best accuracy.")
        else:
            st.markdown("### Result")
            st.dataframe(result["result"], use_container_width=True)


# ---------------------------------------------------------------------------
# Tab 3: Upload & Index
# ---------------------------------------------------------------------------
with tab_upload:
    st.subheader("Add documents to the knowledge base")

    uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
    if uploaded_files:
        os.makedirs(SAMPLE_DOCS_DIR, exist_ok=True)
        for f in uploaded_files:
            save_path = os.path.join(SAMPLE_DOCS_DIR, f.name)
            with open(save_path, "wb") as out:
                out.write(f.getbuffer())
        st.success(f"Saved {len(uploaded_files)} file(s) to {SAMPLE_DOCS_DIR}")

    if st.button("🔄 Rebuild Index"):
        with st.spinner("Building FAISS index (this may take a minute)..."):
            from ingest.build_index import build_index
            index, chunks = build_index()
        st.success(f"Index rebuilt: {index.ntotal} chunks indexed.")
        st.session_state.pop("rag_qa", None)  # force reload with new index

    st.markdown("---")
    st.markdown("### Currently indexed source files")
    if os.path.exists(SAMPLE_DOCS_DIR):
        files = [f for f in os.listdir(SAMPLE_DOCS_DIR) if f.lower().endswith(".pdf")]
        if files:
            for f in files:
                st.markdown(f"- {f}")
        else:
            st.caption("No PDFs yet.")
