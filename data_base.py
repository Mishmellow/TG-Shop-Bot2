import sqlite3
import logging
from contextlib import contextmanager

DB_PATH = 'bot.db'

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logging.error(f"Ошибка БД: {e}")
        raise
    finally:
        conn.close()

def init_db():
    print("🎯 init_db() ВЫЗВАНА!")
    try:
        with get_db_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    username TEXT,
                    first_name TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    referrer_id INTEGER DEFAULT NULL
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS orders(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    product TEXT,
                    quantity INTEGER, 
                    address TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    referrer_id INTEGER DEFAULT NULL
                )
            ''')
        print("✅ Таблицы созданы успешно!")
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")


def add_order(user_id, product, quantity, address):
    print(f"[DB] Сохраняю заказ: {user_id}, {product}, {quantity}, {address}")
    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO orders (user_id, product, quantity, address)
            VALUES (?, ?, ?, ?)
        ''', (user_id, product, quantity, address))
        print("✅ Заказ сохранён в БД!")


def add_user(user_id: int, username: str, first_name: str, referrer_id: int = None):
    with get_db_connection() as conn:
        conn.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, referrer_id) 
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, referrer_id))

def get_user_orders(user_id):
    with get_db_connection() as conn:
        result = conn.execute('''
            SELECT product, quantity, address, created_at 
            FROM orders 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        return result.fetchall()

def user_conn_ref(user_id: int) -> int:
        with get_db_connection() as conn:
            result = conn.execute('''
                SELECT COUNT(*) FROM users WHERE referrer_id = ?
            ''', (user_id,))
            return result.fetchone()[0]