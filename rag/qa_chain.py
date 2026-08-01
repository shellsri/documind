"""
RAG question-answering: retrieve top-k chunks, build a grounded prompt,
generate an answer with FLAN-T5, and return the answer with its source
citations so the UI can show "answered from: filename.pdf, page 3".
"""

import logging

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from config import GENERATION_MODEL_NAME
from rag.retriever import Retriever

logger = logging.getLogger(__name__)


PROMPT_TEMPLATE = """Answer the question using ONLY the context below.
If the context does not contain the answer, say "I don't have enough
information in the provided documents to answer that."

Context:
{context}

Question: {question}

Answer:"""


class RAGQuestionAnswerer:
    def __init__(self):
        self.retriever = Retriever()
        logger.info(f"Loading generation model: {GENERATION_MODEL_NAME}")
        self.tokenizer = AutoTokenizer.from_pretrained(GENERATION_MODEL_NAME)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(GENERATION_MODEL_NAME)

    def answer(self, question: str, k: int = 4) -> dict:
        retrieved = self.retriever.retrieve(question, k=k)

        if not retrieved:
            return {
                "answer": "I don't have enough information in the provided documents to answer that.",
                "sources": [],
            }

        context = "\n\n".join(
            f"[{r['source']} p.{r['page']}] {r['text']}" for r in retrieved
        )
        prompt = PROMPT_TEMPLATE.format(context=context, question=question)

        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        outputs = self.model.generate(**inputs, max_new_tokens=200)
        answer_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        sources = [
            {"source": r["source"], "page": r["page"], "score": round(r["score"], 3)}
            for r in retrieved
        ]

        return {"answer": answer_text, "sources": sources}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    qa = RAGQuestionAnswerer()
    result = qa.answer("What is the leave policy for interns?")
    print(result["answer"])
    print(result["sources"])
