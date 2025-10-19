# test_database_contents.py
import sqlite3
from main import app

DB_PATH = app.config['SQLALCHEMY_DATABASE_URI'].replace("sqlite:///", "")


def get_all_table_names(conn):
    """Return a list of all tables in the SQLite database."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    return tables


def print_table_contents(conn, table_name):
    """Print all rows from a table."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    print(f"\nTable: {table_name} ({len(rows)} rows)")
    print("-" * 50)
    for row in rows:
        row_dict = dict(zip(columns, row))
        for col, val in row_dict.items():
            print(f"{col}: {val}")
        print("-" * 20)
    if not rows:
        print("No rows in this table.")


# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    tables = get_all_table_names(conn)

    if not tables:
        print("No tables found in the database.")
    else:
        print(f"Found {len(tables)} table(s): {tables}\n")
        for table in tables:
            print_table_contents(conn, table)

    conn.close()
