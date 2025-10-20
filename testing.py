# test_orders.py
import sqlite3
from main import app

DB_PATH = app.config['SQLALCHEMY_DATABASE_URI'].replace("sqlite:///", "")


def print_table_contents(conn, table_name):
    cursor = conn.cursor()
    # Quote table name to avoid conflicts with reserved keywords
    cursor.execute(f'SELECT * FROM "{table_name}"')
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


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)

    # List of tables to check
    tables_to_check = ["Order", "OrderPizza", "OrderProduct"]

    for table in tables_to_check:
        print_table_contents(conn, table)

    conn.close()

