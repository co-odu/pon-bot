import sqlite3
import json
from datetime import datetime

DB_FILE = "bot.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            username TEXT,
            display_name TEXT,
            role TEXT,
            addresses TEXT,
            registered_at TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            display_name TEXT,
            address TEXT,
            role TEXT,
            category TEXT,
            helped INTEGER,
            created_at TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            display_name TEXT,
            address TEXT,
            role TEXT,
            text TEXT,
            created_at TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            chat_id INTEGER PRIMARY KEY,
            title TEXT,
            chat_type TEXT,
            added_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()


def save_user(user_id, name, username, display_name, role, addresses):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        INSERT OR REPLACE INTO users 
        (user_id, name, username, display_name, role, addresses, registered_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, name, username, display_name, role, 
        json.dumps(addresses), 
        datetime.now().strftime('%H:%M %d.%m.%Y')
    ))
    
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "user_id": row[0],
            "name": row[1],
            "username": row[2],
            "display_name": row[3],
            "role": row[4],
            "addresses": json.loads(row[5]),
            "registered_at": row[6]
        }
    return None


def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('SELECT * FROM users')
    rows = c.fetchall()
    conn.close()
    
    users = {}
    for row in rows:
        users[row[0]] = {
            "user_id": row[0],
            "name": row[1],
            "username": row[2],
            "display_name": row[3],
            "role": row[4],
            "addresses": json.loads(row[5]),
            "registered_at": row[6]
        }
    return users


def save_request(user_id, display_name, address, role, category, helped=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO requests 
        (user_id, display_name, address, role, category, helped, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, display_name, address, role, category, 
        helped,
        datetime.now().strftime('%H:%M %d.%m.%Y')
    ))
    
    conn.commit()
    conn.close()


def save_feedback(user_id, display_name, address, role, text):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO feedback 
        (user_id, display_name, address, role, text, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        user_id, display_name, address, role, text,
        datetime.now().strftime('%H:%M %d.%m.%Y')
    ))
    
    conn.commit()
    conn.close()


def get_all_feedbacks():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        SELECT user_id, display_name, address, role, text, created_at
        FROM feedback
        ORDER BY created_at DESC
    ''')
    rows = c.fetchall()
    conn.close()
    
    feedbacks = []
    for row in rows:
        feedbacks.append({
            "user_id": row[0],
            "display_name": row[1],
            "address": row[2],
            "role": row[3],
            "text": row[4],
            "created_at": row[5]
        })
    return feedbacks


def save_chat(chat_id, title, chat_type):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        INSERT OR REPLACE INTO chats 
        (chat_id, title, chat_type, added_at)
        VALUES (?, ?, ?, ?)
    ''', (
        chat_id, title, chat_type,
        datetime.now().strftime('%H:%M %d.%m.%Y')
    ))
    
    conn.commit()
    conn.close()


def get_all_chat_ids():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('SELECT chat_id FROM chats')
    ids = [row[0] for row in c.fetchall()]
    
    conn.close()
    return ids


def remove_chat(chat_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('DELETE FROM chats WHERE chat_id = ?', (chat_id,))
    
    conn.commit()
    conn.close()


def get_stats():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM requests')
    total = c.fetchone()[0]
    
    today = datetime.now().strftime('%d.%m.%Y')
    c.execute("SELECT COUNT(*) FROM requests WHERE created_at LIKE ?", (f'%{today}',))
    today_count = c.fetchone()[0]
    
    c.execute('SELECT category, COUNT(*) FROM requests GROUP BY category')
    by_category = {row[0]: row[1] for row in c.fetchall()}
    
    c.execute('SELECT address, COUNT(*) FROM requests GROUP BY address')
    by_address = {row[0]: row[1] for row in c.fetchall()}
    
    c.execute('SELECT role, COUNT(*) FROM requests GROUP BY role')
    by_role = {row[0]: row[1] for row in c.fetchall()}
    
    c.execute('SELECT helped, COUNT(*) FROM requests WHERE helped IS NOT NULL GROUP BY helped')
    helped_stats = {row[0]: row[1] for row in c.fetchall()}
    
    conn.close()
    
    return {
        "total": total,
        "today": today_count,
        "by_category": by_category,
        "by_address": by_address,
        "by_role": by_role,
        "helped_yes": helped_stats.get(1, 0),
        "helped_no": helped_stats.get(0, 0)
    }


def get_all_user_ids():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('SELECT user_id FROM users')
    ids = [row[0] for row in c.fetchall()]
    
    conn.close()
    return ids
