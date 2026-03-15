import sqlite3
import pandas as pd

DB_PATH = "sales.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def run_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql(sql, conn)
    except Exception as e:
        raise e
    finally:
        conn.close()

def get_schema() -> str:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cursor.fetchall()]
        info = ["DATABASE TABLES (use ONLY these table names in your SQL):"]
        for t in tables:
            cursor.execute(f"PRAGMA table_info({t})")
            cols = [(c[1], c[2]) for c in cursor.fetchall()]
            col_str = ", ".join([f"{c[0]} ({c[1]})" for c in cols])
            info.append(f"  - Table `{t}`: {col_str}")
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            count = cursor.fetchone()[0]
            info.append(f"    ({count} rows)")
        info.append("\nSAMPLE DATA from orders:")
        cursor.execute("""
            SELECT o.id, p.product_name, c.customer_name,
                   o.total_amount, o.order_date
            FROM orders o
            JOIN products p ON o.product_id = p.id
            JOIN customers c ON o.customer_id = c.id
            LIMIT 3
        """)
        rows = cursor.fetchall()
        for r in rows:
            info.append(f"  {r}")
        return "\n".join(info)
    finally:
        cursor.close()
        conn.close()