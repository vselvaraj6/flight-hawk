import sqlite3
import os
import hashlib
import secrets

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, 'flights.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def _hash_password(password, salt=None):
    """Hash a password with a salt using SHA-256."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return salt, hashed

def init_db():
    """Initializes the database schema if it does not exist."""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS destinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            departure_city_code TEXT NOT NULL,
            destination_city_code TEXT NOT NULL,
            target_price REAL NOT NULL,
            lowest_price_seen REAL DEFAULT NULL,
            date_from TEXT,
            date_to TEXT,
            nights_in_dst_from INTEGER DEFAULT 1,
            nights_in_dst_to INTEGER DEFAULT 14
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination_id INTEGER NOT NULL,
            price REAL NOT NULL,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(destination_id) REFERENCES destinations(id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        INSERT OR IGNORE INTO settings (key, value) VALUES ('check_frequency_minutes', '60')
    ''')
    
    conn.commit()
    conn.close()

def add_destination(dep_code, dest_code, target_price, date_from=None, date_to=None):
    """Adds a new destination to track."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO destinations 
        (departure_city_code, destination_city_code, target_price, date_from, date_to) 
        VALUES (?, ?, ?, ?, ?)
    ''', (dep_code.upper(), dest_code.upper(), target_price, date_from, date_to))
    conn.commit()
    conn.close()

def get_all_destinations():
    """Fetches all tracked destinations."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row 
    c = conn.cursor()
    c.execute('SELECT * FROM destinations')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_lowest_price(destination_id, new_lowest_price):
    """Updates the lowest price seen."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE destinations SET lowest_price_seen = ? WHERE id = ?',
              (new_lowest_price, destination_id))
    conn.commit()
    conn.close()

def get_setting(key):
    """Gets a setting value by key."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT value FROM settings WHERE key = ?', (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_setting(key, value):
    """Sets a setting value (creates or updates)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, str(value)))
    conn.commit()
    conn.close()

# ============================================================
# USER MANAGEMENT
# ============================================================

def user_exists(username):
    """Check if a username is already taken."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username.lower(),))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def create_user(username, password):
    """Create a new user with a hashed password. Returns (success, message)."""
    if user_exists(username):
        return False, "Username already taken."
    salt, hashed = _hash_password(password)
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password_hash, password_salt) VALUES (?, ?, ?)',
              (username.lower(), hashed, salt))
    conn.commit()
    conn.close()
    return True, "Account created!"

def authenticate_user(username, password):
    """Verify username/password. Returns (success, message)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT password_hash, password_salt FROM users WHERE username = ?', (username.lower(),))
    row = c.fetchone()
    conn.close()
    if not row:
        return False, "User not found."
    stored_hash, salt = row
    _, input_hash = _hash_password(password, salt)
    if input_hash == stored_hash:
        return True, "Login successful!"
    return False, "Incorrect password."

def reset_password(username, new_password):
    """Reset a user's password. Returns (success, message)."""
    if not user_exists(username):
        return False, "User not found."
    salt, hashed = _hash_password(new_password)
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE users SET password_hash = ?, password_salt = ? WHERE username = ?',
              (hashed, salt, username.lower()))
    conn.commit()
    conn.close()
    return True, "Password reset successfully!"

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", os.path.abspath(DB_PATH))
