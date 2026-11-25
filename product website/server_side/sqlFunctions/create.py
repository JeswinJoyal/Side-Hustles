import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def setup_database():
    """Creates the products table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # DDL: Create the table. 
    # Note: PostgreSQL uses SERIAL or BIGSERIAL for auto-incrementing primary keys
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            gender VARCHAR(50),
            category VARCHAR(100),
            subcategory VARCHAR(100),
            sub_subcategory VARCHAR(100),
            price INTEGER NOT NULL, 
            url TEXT
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database table ensured.")