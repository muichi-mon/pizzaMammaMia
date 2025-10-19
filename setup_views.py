"""
Setup script to create database views from business_queries.sql
Run this once to load all views (PizzaMenu, ProductMenu, CustomerLoyalty, etc.)
"""

import sqlite3
import os
import re

def convert_mysql_to_sqlite(sql_content):
    """Convert MySQL-specific syntax to SQLite-compatible SQL"""
    
    # Convert DATE_FORMAT to strftime
    sql_content = re.sub(
        r"DATE_FORMAT\(([^,]+),\s*'%m-%d'\)",
        r"strftime('%m-%d', \1)",
        sql_content,
        flags=re.IGNORECASE
    )
    
    # Convert CURDATE() to date('now')
    sql_content = re.sub(r'\bCURDATE\(\)', "date('now')", sql_content, flags=re.IGNORECASE)
    
    # Convert DATE_SUB to date arithmetic
    sql_content = re.sub(
        r"DATE_SUB\(CURDATE\(\),\s*INTERVAL\s+(\d+)\s+DAY\)",
        r"date('now', '-\1 days')",
        sql_content,
        flags=re.IGNORECASE
    )
    
    # Convert TIMESTAMPDIFF to julianday difference
    sql_content = re.sub(
        r"TIMESTAMPDIFF\(YEAR,\s*([^,]+),\s*CURDATE\(\)\)",
        r"CAST((julianday('now') - julianday(\1)) / 365.25 AS INTEGER)",
        sql_content,
        flags=re.IGNORECASE
    )
    
    # Convert TRUE/FALSE to 1/0
    sql_content = re.sub(r'\bTRUE\b', '1', sql_content, flags=re.IGNORECASE)
    sql_content = re.sub(r'\bFALSE\b', '0', sql_content, flags=re.IGNORECASE)
    
    # Convert BOOL to INTEGER
    sql_content = re.sub(r'\bBOOL\b', 'INTEGER', sql_content, flags=re.IGNORECASE)
    
    return sql_content

def load_views(db_path, sql_path):
    """Load views from business_queries.sql into the database"""
    
    print(f"Database: {db_path}")
    print(f"SQL file: {sql_path}")
    
    if not os.path.exists(sql_path):
        print(f"❌ Error: {sql_path} not found")
        return False
    
    # Read the SQL file
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Convert MySQL syntax to SQLite
    sql_content = convert_mysql_to_sqlite(sql_content)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Drop existing views (if any) to avoid conflicts
        view_names = [
            'PizzaMenu', 'ProductMenu', 'CustomerLoyalty', 'BirthdayCustomers',
            'AvailableDeliveryPersonnel', 'UndeliveredOrders', 'TopPizzasLastMonth',
            'EarningsByPostcode', 'EarningsByAgeGroup', 'OrderDetails'
        ]
        
        print("\n🗑️  Dropping old views (if they exist)...")
        for view_name in view_names:
            try:
                cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
            except sqlite3.Error as e:
                print(f"  Warning: Could not drop {view_name}: {e}")
        
        conn.commit()
        
        # Split SQL into individual statements
        # Remove comments and split by semicolon
        lines = []
        for line in sql_content.split('\n'):
            # Skip comment-only lines
            if line.strip().startswith('--'):
                continue
            lines.append(line)
        
        sql_clean = '\n'.join(lines)
        statements = [s.strip() for s in sql_clean.split(';') if s.strip()]
        
        # Execute each CREATE VIEW statement
        print("\n📊 Creating views...")
        created_count = 0
        
        for statement in statements:
            # Only execute CREATE VIEW statements
            if 'CREATE' in statement.upper() and 'VIEW' in statement.upper():
                try:
                    cursor.execute(statement)
                    # Extract view name from statement
                    match = re.search(r'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+(\w+)', statement, re.IGNORECASE)
                    view_name = match.group(1) if match else 'unknown'
                    print(f"  ✅ Created view: {view_name}")
                    created_count += 1
                except sqlite3.Error as e:
                    print(f"  ❌ Error creating view: {e}")
                    print(f"     Statement: {statement[:100]}...")
        
        conn.commit()
        
        # Verify views were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
        views = cursor.fetchall()
        
        print(f"\n✅ Successfully created {created_count} views")
        print(f"\n📋 Views in database:")
        for view in views:
            print(f"  - {view[0]}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

def main():
    # Paths
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, 'instance', 'database.db')
    sql_path = os.path.join(project_root, 'database_layer', 'business_queries.sql')
    
    print("=" * 60)
    print("DATABASE VIEWS SETUP")
    print("=" * 60)
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"\n⚠️  Warning: Database not found at {db_path}")
        print("Run load_sample_data.py first to create the database and tables")
        return
    
    # Load views
    success = load_views(db_path, sql_path)
    
    if success:
        print("\n🎉 Views setup complete!")
        print(f"Database location: {db_path}")
        print("\nYou can now query views like:")
        print("  - PizzaMenu (pizza prices with dietary info)")
        print("  - ProductMenu (drinks and snacks)")
        print("  - CustomerLoyalty (customer purchase history)")
        print("  - BirthdayCustomers (upcoming birthdays)")
    else:
        print("\n❌ Views setup failed")

if __name__ == '__main__':
    main()
