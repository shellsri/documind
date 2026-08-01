"""
Natural-language-to-SQL query engine.

Two backends are supported so this works whether or not you have an
API key:

  - "openai"  : uses any OpenAI-compatible chat endpoint via LangChain
                (set OPENAI_API_KEY in a .env file). Best SQL quality.
  - "local"   : uses the same local FLAN-T5 model already used for RAG,
                prompted for text-to-SQL. Works fully offline, weaker
                on complex joins but fine for a demo + shows you can
                build NL2SQL without depending on a paid API.

Either way, generated SQL is validated (must be a SELECT, checked
against the real schema) before being executed, and results are
returned as a pandas DataFrame.
"""

import os
import re
import logging

import pandas as pd
from sqlalchemy import create_engine, inspect, text

from config import SQLITE_DB_PATH

logger = logging.getLogger(__name__)

SCHEMA_DESCRIPTION = """
Tables:
  departments(department_id, name)
  personnel(personnel_id, name, rank, department_id, joining_date)
  requisitions(requisition_id, personnel_id, item_name, quantity, status, request_date, fulfilled_date)

Notes:
  - requisitions.status is one of: Pending, Approved, Rejected, Fulfilled
  - personnel.department_id references departments.department_id
  - requisitions.personnel_id references personnel.personnel_id
  - dates are stored as ISO strings (YYYY-MM-DD)
"""

SQL_PROMPT_TEMPLATE = """You are a SQL expert. Given the schema below, write a single
valid SQLite SELECT query that answers the question. Only output the SQL, nothing else.

{schema}

Examples:
Question: How many personnel are in the Signals department?
SQL: SELECT COUNT(*) FROM personnel p JOIN departments d ON p.department_id = d.department_id WHERE d.name = 'Signals';

Question: List all pending requisitions with the requester's name.
SQL: SELECT r.requisition_id, p.name, r.item_name, r.quantity FROM requisitions r JOIN personnel p ON r.personnel_id = p.personnel_id WHERE r.status = 'Pending';

Question: What is the most requested item?
SQL: SELECT item_name, COUNT(*) as request_count FROM requisitions GROUP BY item_name ORDER BY request_count DESC LIMIT 1;

Now answer this one:

Question: {question}

SQL:"""



class SQLGuard:
    """Basic safety check: only allow read-only SELECT statements."""

    FORBIDDEN = re.compile(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|PRAGMA)\b", re.IGNORECASE)

    @classmethod
    def is_safe(cls, sql: str) -> bool:
        sql_clean = sql.strip().rstrip(";")
        if not sql_clean.lower().startswith("select"):
            return False
        if cls.FORBIDDEN.search(sql_clean):
            return False
        return True


class NL2SQLEngine:
    def __init__(self, backend: str = "local"):
        self.backend = backend
        self.engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}")

        if backend == "openai":
            from langchain_openai import ChatOpenAI  # optional dependency
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise EnvironmentError("OPENAI_API_KEY not set. Add it to a .env file or switch backend='local'.")
            self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        elif backend == "local":
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            from config import GENERATION_MODEL_NAME
            self.tokenizer = AutoTokenizer.from_pretrained(GENERATION_MODEL_NAME)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(GENERATION_MODEL_NAME)
        else:
            raise ValueError(f"Unknown backend: {backend}")

    def _generate_sql_openai(self, question: str) -> str:
        prompt = SQL_PROMPT_TEMPLATE.format(schema=SCHEMA_DESCRIPTION, question=question)
        response = self.llm.invoke(prompt)
        return response.content.strip()

    def _generate_sql_local(self, question: str) -> str:
        prompt = SQL_PROMPT_TEMPLATE.format(schema=SCHEMA_DESCRIPTION, question=question)
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.model.generate(**inputs, max_new_tokens=150)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    def generate_sql(self, question: str) -> str:
        if self.backend == "openai":
            return self._generate_sql_openai(question)
        return self._generate_sql_local(question)

    def query(self, question: str) -> dict:
        """
        Generate SQL for the question, validate it, execute it, and
        return both the SQL and the result set (or an error message).
        """
        sql = self.generate_sql(question)

        if not SQLGuard.is_safe(sql):
            return {
                "sql": sql,
                "error": "Generated query failed safety validation (must be a read-only SELECT).",
                "result": None,
            }

        try:
            with self.engine.connect() as conn:
                df = pd.read_sql_query(text(sql), conn)
            return {"sql": sql, "error": None, "result": df}
        except Exception as e:
            return {"sql": sql, "error": str(e), "result": None}


def list_tables() -> list[str]:
    engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}")
    return inspect(engine).get_table_names()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Tables:", list_tables())
    engine = NL2SQLEngine(backend="local")
    result = engine.query("How many personnel are in the Signals department?")
    print(result)
