"""
Builds a small SQLite database representing an enterprise-style
"requisitions & personnel" dataset — modeled loosely on the kind of
records an internal army/enterprise ERP tool would hold (personnel,
equipment requisitions, departments). All data here is synthetic.

Run directly:
    python -m nl2sql.schema
to (re)create data/records.db from scratch.
"""

import os
import sqlite3
import random
from datetime import date, timedelta

from config import SQLITE_DB_PATH

DEPARTMENTS = ["Logistics", "Signals", "Engineering", "Medical", "Administration", "IT"]
RANKS = ["Lieutenant", "Captain", "Major", "Colonel", "Civilian Staff"]
STATUSES = ["Pending", "Approved", "Rejected", "Fulfilled"]
ITEMS = ["Laptop", "Radio Set", "Generator", "Medical Kit", "Vehicle Spare Parts",
         "Office Furniture", "Server Hardware", "Field Tent", "Fuel Canister"]


def _random_date(start_year=2025, end_year=2026):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def build_database(db_path: str = SQLITE_DB_PATH, seed: int = 42, n_personnel: int = 40, n_requisitions: int = 120):
    random.seed(seed)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE departments (
            department_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE personnel (
            personnel_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            rank TEXT NOT NULL,
            department_id INTEGER NOT NULL,
            joining_date TEXT NOT NULL,
            FOREIGN KEY (department_id) REFERENCES departments(department_id)
        )
    """)

    cur.execute("""
        CREATE TABLE requisitions (
            requisition_id INTEGER PRIMARY KEY,
            personnel_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL,
            request_date TEXT NOT NULL,
            fulfilled_date TEXT,
            FOREIGN KEY (personnel_id) REFERENCES personnel(personnel_id)
        )
    """)

    for i, dept in enumerate(DEPARTMENTS, start=1):
        cur.execute("INSERT INTO departments (department_id, name) VALUES (?, ?)", (i, dept))

    first_names = ["Aarav", "Priya", "Rohan", "Sneha", "Vikram", "Ananya", "Karan",
                   "Meera", "Arjun", "Isha", "Dev", "Kavya", "Rahul", "Neha"]
    last_names = ["Sharma", "Verma", "Reddy", "Nair", "Singh", "Gupta", "Iyer", "Chatterjee"]

    for pid in range(1, n_personnel + 1):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        rank = random.choice(RANKS)
        dept_id = random.randint(1, len(DEPARTMENTS))
        joining = _random_date(2020, 2025).isoformat()
        cur.execute(
            "INSERT INTO personnel (personnel_id, name, rank, department_id, joining_date) VALUES (?, ?, ?, ?, ?)",
            (pid, name, rank, dept_id, joining),
        )

    for rid in range(1, n_requisitions + 1):
        pid = random.randint(1, n_personnel)
        item = random.choice(ITEMS)
        qty = random.randint(1, 20)
        status = random.choice(STATUSES)
        req_date = _random_date(2025, 2026)
        fulfilled = (req_date + timedelta(days=random.randint(2, 30))).isoformat() if status == "Fulfilled" else None
        cur.execute(
            """INSERT INTO requisitions
               (requisition_id, personnel_id, item_name, quantity, status, request_date, fulfilled_date)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (rid, pid, item, qty, status, req_date.isoformat(), fulfilled),
        )

    conn.commit()
    conn.close()
    print(f"Database built at {db_path} "
          f"({len(DEPARTMENTS)} departments, {n_personnel} personnel, {n_requisitions} requisitions)")


if __name__ == "__main__":
    build_database()
