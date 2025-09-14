from dotenv import load_dotenv
import os
import mysql.connector  # fix the import

# Load environment variables from .env
load_dotenv()

# Database configuration
config = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),  # If DB_PORT does not exist in .env (or is empty), Python will use default 3306 instead.
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "ssl_disabled": False
}

try:
    # Connect to the database
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    # Execute SHOW TABLES
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    if tables:
        print("Tables in the database:")
        for table in tables:
            print(table[0])
    else:
        print("No tables found in the database.")

    # Close connection
    cursor.close()
    conn.close()

except mysql.connector.Error as err:
    print("Error:", err)
