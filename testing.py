# test_database_contents.py
import sqlite3
from main import app

DB_PATH = app.config['SQLALCHEMY_DATABASE_URI'].replace("sqlite:///", "")

BASE_PRICE = 5  # same as in your add_to_cart calculation


def get_all_table_names(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    return tables


def print_table_contents(conn, table_name):
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


def print_pizza_prices(conn):
    """Calculate and print dynamic prices for all pizzas."""
    cursor = conn.cursor()
    cursor.execute("SELECT pizza_id, name FROM Pizza WHERE active=1")
    pizzas = cursor.fetchall()

    print("\nDynamic Prices for Active Pizzas")
    print("=" * 50)
    for pizza_id, pizza_name in pizzas:
        # Get ingredients for this pizza
        cursor.execute("""
            SELECT pi.grams, i.cost
            FROM PizzaIngredient pi
            JOIN Ingredient i ON pi.ingredient_id = i.ingredient_id
            WHERE pi.pizza_id = ?
        """, (pizza_id,))
        ingredients = cursor.fetchall()

        # Calculate price
        total_cost = BASE_PRICE
        for grams, cost in ingredients:
            total_cost += (grams / 100.0) * cost

        total_cost = round(total_cost, 2)
        print(f"{pizza_name} (ID: {pizza_id}) → ${total_cost}")


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

    # Print dynamic pizza prices
    print_pizza_prices(conn)

    conn.close()
