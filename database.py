import sqlite3
from datetime import datetime
from pathlib import Path

DB_FILE = Path(__file__).with_name("expenses.db")


def connect():
    return sqlite3.connect(DB_FILE)


def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                description TEXT NOT NULL
            )
        """)
        conn.commit()


def add_expense(expense_date, category, amount, description):
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO expenses
            (expense_date, category, amount, description)
            VALUES (?, ?, ?, ?)
            """,
            (expense_date, category, amount, description)
        )
        conn.commit()


def get_expenses(search=""):
    with connect() as conn:
        if search:
            pattern = f"%{search}%"

            cursor = conn.execute("""
                SELECT id,
                       expense_date,
                       category,
                       printf('%.2f', amount),
                       description
                FROM expenses
                WHERE category LIKE ?
                   OR description LIKE ?
                   OR expense_date LIKE ?
                ORDER BY expense_date DESC, id DESC
            """, (pattern, pattern, pattern))

        else:
            cursor = conn.execute("""
                SELECT id,
                       expense_date,
                       category,
                       printf('%.2f', amount),
                       description
                FROM expenses
                ORDER BY expense_date DESC, id DESC
            """)

        return cursor.fetchall()


def update_expense(expense_id, expense_date, category, amount, description):
    with connect() as conn:
        conn.execute("""
            UPDATE expenses
            SET expense_date = ?,
                category = ?,
                amount = ?,
                description = ?
            WHERE id = ?
        """, (expense_date, category, amount, description, expense_id))

        conn.commit()


def delete_expense(expense_id):
    with connect() as conn:
        conn.execute(
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,)
        )
        conn.commit()


def get_summary():
    current_month = datetime.now().strftime("%Y-%m")

    with connect() as conn:

        total = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses"
        ).fetchone()[0]

        month_total = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            WHERE expense_date LIKE ?
            """,
            (current_month + "%",)
        ).fetchone()[0]

        top = conn.execute("""
            SELECT category, SUM(amount) AS total
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
            LIMIT 1
        """).fetchone()

    return total, month_total, top[0] if top else None
def get_category_summary():
    with connect() as conn:
        return conn.execute("""
            SELECT category, SUM(amount)
            FROM expenses
            GROUP BY category
            ORDER BY SUM(amount) DESC
        """).fetchall()


def get_monthly_summary():
    with connect() as conn:
        return conn.execute("""
            SELECT substr(expense_date, 1, 7) AS month,
                   SUM(amount)
            FROM expenses
            GROUP BY month
            ORDER BY month
        """).fetchall()
