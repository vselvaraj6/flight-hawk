import sqlite3
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, 'flights.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initializes the database schema if it does not exist."""
    conn = get_connection()
    c = conn.cursor()
    
    # Table to store user's desired destinations and flight configurations
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
    
    # Optional: Table to store flight history if we want to visualize trends
    c.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination_id INTEGER NOT NULL,
            price REAL NOT NULL,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(destination_id) REFERENCES destinations(id)
        )
    ''')
    
    # Settings table for app configuration
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    
    # Set default check frequency to 60 minutes if not already set
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
    # Return rows as dictionaries for easier usage
    conn.row_factory = sqlite3.Row 
    c = conn.cursor()
    c.execute('SELECT * FROM destinations')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_lowest_price(destination_id, new_lowest_price):
    """Updates the lowest price seen history to prevent duplicate notifications."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE destinations 
        SET lowest_price_seen = ? 
        WHERE id = ?
    ''', (new_lowest_price, destination_id))
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

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", os.path.abspath(DB_PATH))
