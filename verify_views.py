import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== VERIFYING DATABASE VIEWS ===\n")

# List all views
cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
views = cursor.fetchall()
print(f"Total views created: {len(views)}")
for v in views:
    print(f"  ✓ {v[0]}")

print("\n--- Testing PizzaMenu View ---")
cursor.execute("SELECT pizza_id, name, price, is_vegetarian, is_vegan FROM PizzaMenu LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    print(f"  {row[0]}. {row[1]} - ${row[2]:.2f} (Veg: {row[3]}, Vegan: {row[4]})")

print("\n--- Testing ProductMenu View ---")
cursor.execute("SELECT product_id, name, category, price FROM ProductMenu LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    print(f"  {row[0]}. {row[1]} ({row[2]}) - ${row[3]:.2f}")

print("\n--- Testing CustomerLoyalty View ---")
cursor.execute("SELECT customer_id, total_pizzas_bought, eligible_for_loyalty_discount FROM CustomerLoyalty LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    print(f"  Customer {row[0]}: {row[1]} pizzas bought, Loyalty: {row[2]}")

conn.close()
print("\n✅ Views are working correctly!")
