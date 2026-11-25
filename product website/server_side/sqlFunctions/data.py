import os
import mysql.connector
from dotenv import load_dotenv
from psycopg2 import IntegrityError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

load_dotenv()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")       #! maybe we might need to keep this in the request handler file itself


def get_db_connection():
    return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "polyglot")
        )


#======================================================================


# The allow-list of fields. Update this tuple when you modify your table in your modify.py script.
PRODUCT_FIELDS = (
    'name', 'gender', 'category', 'subcategory', 
    'sub_subcategory', 'price', 'url'
)

def setup_database():
    """Creates the products table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            gender VARCHAR(50),
            category VARCHAR(100),
            subcategory VARCHAR(100),
            sub_subcategory VARCHAR(100),
            price DECIMAL(10, 2) NOT NULL, 
            url TEXT
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database table ensured.")


def insert_product(product_data: dict) -> int:
    """
    Dynamically generates the INSERT statement based on the provided dictionary.
    """
    # 1. Security Check: Filter the dictionary to ONLY include keys present in PRODUCT_FIELDS
    # This completely prevents SQL injection via malicious column names.
    valid_data = {key: value for key, value in product_data.items() if key in PRODUCT_FIELDS}
    
    if not valid_data:
        raise ValueError("No valid fields provided for insertion.")


    columns = list(valid_data.keys())
    values = tuple(valid_data.values())
    col_string = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    query = f"INSERT INTO products ({col_string}) VALUES ({placeholders}) ;"
    
    # 4. Execute the query
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, values)
        conn.commit()
        product_id = cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"Database error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
    
    return product_id

#======================================================================

def setup_admin_database():
    """Creates the admin table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            ID int auto_increment PRIMARY KEY,
            user_name varchar(50) not null unique,
            hashed_password varchar(255)
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Admin table ensured.")


def create_admin(username: str, plaintext_password: str) -> int | None:
    """
    Hashes the password and inserts the new admin into the database.
    Returns the new admin ID, or None if creation fails.
    """
    # 1. Scramble the password BEFORE opening the database connection
    hashed_pw = pwd_context.hash(plaintext_password)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 2. Insert using parameterized queries (%s)
        cursor.execute('''
            INSERT INTO admins (user_name, hashed_password)
            VALUES (%s, %s);
        ''', (username, hashed_pw))
        
        # 3. Retrieve the newly generated ID
        conn.commit()
        admin_id = cursor.lastrowid
        
        print(f"✅ Admin '{username}' created successfully. ID: {admin_id}")
        return admin_id
        
    except mysql.connector.IntegrityError:
        # This catches the UNIQUE constraint violation
        conn.rollback()
    #===================================
    #TODO -> INFORM THE ERROR TO FRONTEND IF NEEDED 
    #===================================
        print(f"❌ Error: The username '{username}' is already taken.")
        return None
        
    except Exception as e:
        # Catch any other database issues (e.g., connection dropped)
        conn.rollback()
        print(f"❌ Database error: {e}")
        return None
        
    finally:
        # Always close the connection, even if an error occurred
        cursor.close()
        conn.close()

def is_username_taken(username: str) -> bool:
    """
    Checks if a username exists in the admins table.
    Returns True if taken, False if available.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT 1 FROM admins WHERE user_name = %s LIMIT 1;', (username,))
        result = cursor.fetchone()
        
        # If result is not None, the username exists.
        return result is not None
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        # Fail secure: If the database crashes during the check, assume the name is taken so you don't accidentally try to create duplicates.
        return True 
        
    finally:
        cursor.close()
        conn.close()


def get_admin_hash(username: str) -> str | None:
    """
    Fetches the hashed password for a given username.
    Returns None if the user does not exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT hashed_password FROM admins WHERE user_name = %s LIMIT 1;', (username,))
        result = cursor.fetchone()
        
        if result:
            return result[0] # Return the hash string
        return None
        
    except Exception as e:
        print(f"Database error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def password_to_hash(password : str) -> str:
    """converts the plaintext password into hashed password"""
    return  pwd_context.hash(password)

def get_id(username: str):
    """
    returns thee id number for a particular username
    Returns the integer ID if found, or None if the user doesn't exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # LIMIT 1 ensures the database stops scanning once it finds the match
        cursor.execute('SELECT id FROM admins WHERE user_name = %s LIMIT 1;', (username,))
        result = cursor.fetchone()
        
        if result:
            return result[0]  #Note: fetchone() returns a tuple like (1,), so we extract the first element
        return None
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None
        
    finally:
        cursor.close()
        conn.close()

def verify_password(plaintext_password: str, hashed_password: str) -> bool:
    """
    Checks if the plaintext password matches the stored hash.
    Returns True if they match, False otherwise.
    """
    return pwd_context.verify(plaintext_password, hashed_password)

#======================================================================

def setup_session_table():
    """Creates the session table if it doesn't exist for admins and users."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            token VARCHAR(64) PRIMARY KEY,
            admin_id INTEGER,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE CASCADE
        );
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    print("session table ensured.")

def create_session(admin_id: int, token: str, minutes_valid: int = 24) -> bool:
    """
    Inserts a new session token into the database with an expiration timestamp.
    """
    # Calculate expiration time in UTC
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=minutes_valid)).strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO sessions (token, admin_id, expires_at)
            VALUES (%s, %s, %s)
        ''', (token, admin_id, expires_at))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Failed to create session: {e}")
        #TODO: maybe also give the admin some message if the session token couldnt be registered in the database
        #TODO: or else do some alternative  storage like storing the thing in a dictionary maybe.
        #TODO: or maybe just  inform the user that login was successful but something went wrong in the server side
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def cleanup_user_sessions(admin_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Only deletes expired tokens for this specific user
        cursor.execute('''
            DELETE FROM sessions 
            WHERE admin_id = %s AND expires_at < UTC_TIMESTAMP()
        ''', (admin_id,))
        conn.commit()
    except Exception as e:
        print(f"❌ Failed to clean up sessions: {e}")
        conn.rollback() 
    finally:
        cursor.close()
        conn.close()

#======================================================================
