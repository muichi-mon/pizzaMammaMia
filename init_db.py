"""
Database initialization script
Drops all tables, recreates them from schema.sql, and loads sample data
"""
import os
import sqlite3
from main import app, db

def init_database():
    """Initialize the database with schema and sample data"""
    
    db_path = os.path.join(app.instance_path, 'database.db')
    
    print(f"Reinitializing database: {db_path}")
    
    # Drop all tables and recreate them
    with app.app_context():
        db.drop_all()
        print("Dropped all existing tables")
        db.create_all()
        print("Created tables using SQLAlchemy ORM")
    
    # Now load sample data using raw SQL
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Read and execute sample data
        with open('database_layer/sample_data.sql', 'r', encoding='utf-8') as f:
            sample_sql = f.read()
            
            # Execute the entire script
            cursor.executescript(sample_sql)
        
        conn.commit()
        print("Sample data loaded successfully!")
        
        # Verify the data
        cursor.execute("SELECT COUNT(*) FROM Pizza")
        pizza_count = cursor.fetchone()[0]
        print(f"Total pizzas in database: {pizza_count}")
        
        cursor.execute("SELECT name, price, is_vegetarian, is_vegan FROM Pizza LIMIT 3")
        sample_pizzas = cursor.fetchall()
        print("\nSample pizzas:")
        for pizza in sample_pizzas:
            print(f"  - {pizza[0]}: €{pizza[1]} (Vegetarian: {bool(pizza[2])}, Vegan: {bool(pizza[3])})")
        
    except Exception as e:
        print(f"Error loading sample data: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    print("\nDatabase initialization complete!")

if __name__ == '__main__':
    init_database()
