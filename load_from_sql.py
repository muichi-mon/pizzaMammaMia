"""
Load data from MySQL SQL files by translating to SQLite syntax
Created by LLM to translate mysql schema and data inserts to sqlite
"""
import os
import re
import sqlite3

def mysql_to_sqlite_schema(mysql_sql):
    """Convert MySQL schema to SQLite syntax"""
    sqlite_sql = mysql_sql
    
    # Replace INT AUTO_INCREMENT PRIMARY KEY with INTEGER PRIMARY KEY AUTOINCREMENT
    sqlite_sql = re.sub(
        r'(\w+)\s+INT\s+AUTO_INCREMENT\s+PRIMARY\s+KEY',
        r'\1 INTEGER PRIMARY KEY AUTOINCREMENT',
        sqlite_sql,
        flags=re.IGNORECASE
    )
    
    # Replace remaining INT with INTEGER (for other integer columns)
    sqlite_sql = re.sub(r'\bINT\b(?!\s+NOT\s+NULL)', 'INTEGER', sqlite_sql, flags=re.IGNORECASE)
    sqlite_sql = re.sub(r'\bINT\s+NOT\s+NULL', 'INTEGER NOT NULL', sqlite_sql, flags=re.IGNORECASE)
    
    # Replace BOOL/BOOLEAN with BOOLEAN (SQLite treats as INTEGER)
    sqlite_sql = re.sub(r'\bBOOL\b', 'BOOLEAN', sqlite_sql, flags=re.IGNORECASE)
    
    # Replace ENUM with VARCHAR and CHECK constraint
    # Example: ENUM('drink', 'snack') -> VARCHAR(10) CHECK (category IN ('drink', 'snack'))
    def replace_enum(match):
        full_match = match.group(0)
        # Extract column name and enum values
        col_match = re.match(r"(\w+)\s+ENUM\((.*?)\)", full_match, re.IGNORECASE)
        if col_match:
            column = col_match.group(1)
            values = col_match.group(2)
            # Extract the enum values
            enum_values = re.findall(r"'([^']+)'", values)
            max_len = max(len(v) for v in enum_values)
            check = f"CHECK ({column} IN ({values}))"
            return f"{column} VARCHAR({max_len}) NOT NULL {check}"
        return full_match
    
    sqlite_sql = re.sub(
        r"\w+\s+ENUM\(.*?\)\s+NOT NULL",
        replace_enum,
        sqlite_sql,
        flags=re.IGNORECASE
    )
    
    # Remove REGEXP constraints (SQLite doesn't support REGEXP without extension)
    # Remove entire CHECK constraint lines that contain REGEXP
    sqlite_sql = re.sub(r',?\s*CONSTRAINT\s+\w+\s+CHECK\s*\([^)]*REGEXP[^)]*\)', '', sqlite_sql, flags=re.IGNORECASE)
    
    # Remove date-based CHECK constraints (non-deterministic functions not allowed)
    sqlite_sql = re.sub(r',?\s*CONSTRAINT\s+\w+\s+CHECK\s*\([^)]*CURDATE\(\)[^)]*\)', '', sqlite_sql, flags=re.IGNORECASE)
    sqlite_sql = re.sub(r',?\s*CHECK\s*\([^)]*<=\s*DATE\([^)]*\)[^)]*\)', '', sqlite_sql, flags=re.IGNORECASE)
    
    # Clean up trailing commas before closing parenthesis (from removed constraints)
    sqlite_sql = re.sub(r',\s*\)', ')', sqlite_sql)
    sqlite_sql = re.sub(r',(\s*,)+', ',', sqlite_sql)  # Remove double commas
    
    # Remove empty constraint sections (just "-- Constraints" followed by closing paren)
    sqlite_sql = re.sub(r',?\s*--\s*Constraints\s*\)', ')', sqlite_sql, flags=re.IGNORECASE)
    
    # Add IF NOT EXISTS to CREATE TABLE
    sqlite_sql = re.sub(r'CREATE TABLE\s+', 'CREATE TABLE IF NOT EXISTS ', sqlite_sql, flags=re.IGNORECASE)
    
    # Add IF NOT EXISTS to CREATE INDEX
    sqlite_sql = re.sub(r'CREATE INDEX\s+', 'CREATE INDEX IF NOT EXISTS ', sqlite_sql, flags=re.IGNORECASE)
    
    return sqlite_sql

def mysql_to_sqlite_data(mysql_sql):
    """Convert MySQL data inserts to SQLite syntax"""
    sqlite_sql = mysql_sql
    
    # Replace TRUE/FALSE with 1/0
    sqlite_sql = re.sub(r'\bTRUE\b', '1', sqlite_sql, flags=re.IGNORECASE)
    sqlite_sql = re.sub(r'\bFALSE\b', '0', sqlite_sql, flags=re.IGNORECASE)
    
    return sqlite_sql

def mysql_to_sqlite_views(mysql_sql):
    """Convert MySQL VIEW queries to SQLite syntax"""
    sqlite_sql = mysql_sql
    
    # Replace TRUE/FALSE with 1/0
    sqlite_sql = re.sub(r'\bTRUE\b', '1', sqlite_sql, flags=re.IGNORECASE)
    sqlite_sql = re.sub(r'\bFALSE\b', '0', sqlite_sql, flags=re.IGNORECASE)
    
    # Replace DATE_FORMAT with strftime
    # DATE_FORMAT(birth_date, '%m-%d') -> strftime('%m-%d', birth_date)
    sqlite_sql = re.sub(
        r"DATE_FORMAT\((\w+),\s*'([^']+)'\)",
        r"strftime('\2', \1)",
        sqlite_sql
    )
    
    # Replace CURDATE() with DATE('now')
    sqlite_sql = re.sub(r'CURDATE\(\)', "DATE('now')", sqlite_sql, flags=re.IGNORECASE)
    
    # Replace DATE_SUB(CURDATE(), INTERVAL 1 MONTH) with DATE('now', '-1 month')
    sqlite_sql = re.sub(
        r"DATE_SUB\(CURDATE\(\),\s*INTERVAL\s+(\d+)\s+MONTH\)",
        r"DATE('now', '-\1 month')",
        sqlite_sql,
        flags=re.IGNORECASE
    )
    sqlite_sql = re.sub(
        r"DATE_SUB\(DATE\('now'\),\s*INTERVAL\s+(\d+)\s+MONTH\)",
        r"DATE('now', '-\1 month')",
        sqlite_sql,
        flags=re.IGNORECASE
    )
    
    # Replace TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) with 
    # (CAST(strftime('%Y', DATE('now')) AS INTEGER) - CAST(strftime('%Y', birth_date) AS INTEGER))
    sqlite_sql = re.sub(
        r"TIMESTAMPDIFF\(YEAR,\s*(\w+\.?\w*),\s*CURDATE\(\)\)",
        r"(CAST(strftime('%Y', DATE('now')) AS INTEGER) - CAST(strftime('%Y', \1) AS INTEGER))",
        sqlite_sql,
        flags=re.IGNORECASE
    )
    sqlite_sql = re.sub(
        r"TIMESTAMPDIFF\(YEAR,\s*(\w+\.?\w*),\s*DATE\('now'\)\)",
        r"(CAST(strftime('%Y', DATE('now')) AS INTEGER) - CAST(strftime('%Y', \1) AS INTEGER))",
        sqlite_sql,
        flags=re.IGNORECASE
    )
    
    # Replace CONCAT with ||
    # CONCAT(c.first_name, ' ', c.last_name) -> c.first_name || ' ' || c.last_name
    def replace_concat(match):
        args = match.group(1)
        # Split by comma, handling quoted strings
        parts = re.findall(r"(?:[^,']|'[^']*')+", args)
        return ' || '.join(part.strip() for part in parts)
    
    sqlite_sql = re.sub(
        r"CONCAT\(([^)]+)\)",
        replace_concat,
        sqlite_sql,
        flags=re.IGNORECASE
    )
    
    return sqlite_sql

def clean_sql(sql_content):
    """Remove comments and clean up SQL"""
    lines = []
    for line in sql_content.split('\n'):
        # Remove single-line comments
        line = re.sub(r'--.*$', '', line)
        line = line.strip()
        if line:
            lines.append(line)
    return ' '.join(lines)

def load_from_sql_files():
    """Load database from SQL files with MySQL to SQLite translation"""
    
    print("=" * 70)
    print("LOADING DATABASE FROM SQL FILES")
    print("=" * 70)
    
    # Get database path
    db_path = os.path.join('instance', 'database.db')
    
    # Remove old database
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"✓ Removed old database: {db_path}")
        except PermissionError:
            print(f"⚠️  Could not remove database (may be in use)")
            print("Please close any applications using the database and try again.")
            return
    
    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    print("\n" + "=" * 70)
    print("STEP 1: Creating Schema")
    print("=" * 70)
    
    # Read and translate schema
    schema_path = 'database_layer/schema.sql'
    if not os.path.exists(schema_path):
        print(f"❌ Schema file not found: {schema_path}")
        return
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        mysql_schema = f.read()
    
    print(f"✓ Read MySQL schema from {schema_path}")
    
    # Translate to SQLite
    sqlite_schema = mysql_to_sqlite_schema(mysql_schema)
    print("✓ Translated MySQL syntax to SQLite syntax")
    
    # Execute schema - split by semicolon and execute each statement
    statements = sqlite_schema.split(';')
    tables_created = 0
    indexes_created = 0
    
    for statement in statements:
        statement = statement.strip()
        if not statement:
            continue
        
        try:
            cursor.execute(statement)
            if 'CREATE TABLE' in statement.upper():
                # Extract table name
                match = re.search(r'CREATE TABLE IF NOT EXISTS\s+(\w+)', statement, re.IGNORECASE)
                if match:
                    table_name = match.group(1)
                    tables_created += 1
                    print(f"  ✓ Created table: {table_name}")
            elif 'CREATE INDEX' in statement.upper():
                indexes_created += 1
        except sqlite3.Error as e:
            print(f"⚠️  Warning: {e}")
            print(f"Statement: {statement[:100]}...")
    
    conn.commit()
    print(f"\n✓ Created {tables_created} tables and {indexes_created} indexes")
    
    print("\n" + "=" * 70)
    print("STEP 2: Loading Sample Data")
    print("=" * 70)
    
    # Read and translate sample data
    data_path = 'database_layer/sample_data.sql'
    if not os.path.exists(data_path):
        print(f"❌ Sample data file not found: {data_path}")
        return
    
    with open(data_path, 'r', encoding='utf-8') as f:
        mysql_data = f.read()
    
    print(f"✓ Read MySQL sample data from {data_path}")
    
    # Translate to SQLite
    sqlite_data = mysql_to_sqlite_data(mysql_data)
    print("✓ Translated MySQL data syntax to SQLite syntax")
    
    # Remove comments
    sqlite_data = clean_sql(sqlite_data)
    
    # Execute data inserts
    try:
        cursor.executescript(sqlite_data)
        conn.commit()
        print("✓ Executed all INSERT statements")
    except sqlite3.Error as e:
        print(f"⚠️  Error loading data: {e}")
        conn.rollback()
        return
    
    print("\n" + "=" * 70)
    print("STEP 3: Verifying Data")
    print("=" * 70)
    
    # Verify data loaded
    tables = [
        'Customer', 'Ingredient', 'Pizza', 'PizzaIngredient',
        'DeliveryPerson', 'DiscountCode', 'Product', 'Orders',
        'OrderPizza', 'OrderProduct'
    ]
    
    total_records = 0
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            total_records += count
            if count > 0:
                print(f"  ✓ {table}: {count} records")
        except sqlite3.Error:
            print(f"  - {table}: (table doesn't exist or is empty)")
    
    # Show sample pizzas with prices
    print("\n" + "=" * 70)
    print("Sample Pizzas (from PizzaMenu view):")
    print("=" * 70)
    try:
        cursor.execute("""
            SELECT name, price, is_vegetarian, is_vegan 
            FROM PizzaMenu 
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            name, price, is_veg, is_vegan = row
            dietary = []
            if is_vegan:
                dietary.append("🌱 Vegan")
            elif is_veg:
                dietary.append("🥬 Vegetarian")
            dietary_str = " ".join(dietary) if dietary else ""
            print(f"  • {name}: €{price} {dietary_str}")
    except sqlite3.Error as e:
        print(f"  Note: PizzaMenu view not available yet (will be created in Step 4)")
    
    # Show sample products
    print("\n" + "=" * 70)
    print("Sample Products:")
    print("=" * 70)
    cursor.execute("""
        SELECT name, category, cost, is_alcohol 
        FROM Product 
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        name, category, cost, is_alcohol = row
        alcohol = "🍺" if is_alcohol else ""
        print(f"  • {name} ({category}): €{cost} {alcohol}")
    
    print("\n" + "=" * 70)
    print("STEP 4: Creating Business Views")
    print("=" * 70)
    
    # Read and translate business queries
    queries_path = 'database_layer/business_queries.sql'
    if not os.path.exists(queries_path):
        print(f"⚠️  Business queries file not found: {queries_path}")
        print("Skipping view creation...")
    else:
        with open(queries_path, 'r', encoding='utf-8') as f:
            mysql_views = f.read()
        
        print(f"✓ Read MySQL business queries from {queries_path}")
        
        # Translate to SQLite
        sqlite_views = mysql_to_sqlite_views(mysql_views)
        print("✓ Translated MySQL view syntax to SQLite syntax")
        
        # Execute view creation
        views_created = 0
        try:
            cursor.executescript(sqlite_views)
            conn.commit()
            
            # Count created views
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='view'")
            views_created = cursor.fetchone()[0]
            print(f"✓ Created {views_created} views")
            
            # List the views
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
            print("\nCreated views:")
            for row in cursor.fetchall():
                print(f"  ✓ {row[0]}")
                
        except sqlite3.Error as e:
            print(f"⚠️  Error creating views: {e}")
            conn.rollback()
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ DATABASE LOADED SUCCESSFULLY!")
    print("=" * 70)
    print(f"Total records loaded: {total_records}")
    print(f"Database location: {db_path}")
    print("=" * 70)

if __name__ == '__main__':
    load_from_sql_files()
