# test_customers.py
from datetime import datetime
from main import app  # your main Flask app
from ORM.Customer import Customer
from ORM import db

# Use the app context to access the database
with app.app_context():
    # Fetch all customers
    customers = Customer.query.all()

    if not customers:
        print("No customers found in the database.")
    else:
        print(f"Found {len(customers)} customer(s):\n")
        for c in customers:
            print(f"ID: {c.customer_id}")
            print(f"Name: {c.first_name} {c.last_name}")
            print(f"Email: {c.email}")
            print(f"Birth Date: {c.birth_date}")
            print(f"Postcode: {c.postcode}")
            print("-" * 30)
