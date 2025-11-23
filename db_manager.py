import sqlite3
import logging

class DBManager:
    def __init__(self, db_path='my_database.db'):
        self.db_path = db_path
        self._create_tables()
        print(f'🟢Подключено к {db_path}')

    def _create_tables(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            conn.execute('PRAGMA foreign_keys = ON')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP               
         )
        ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart_items(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        product TEXT,
                        quantity INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                    ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price INTEGER,
            category TEXT
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    product TEXT,
                    quantity INTEGER, 
                    address TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'new',
                    price INTEGER DEFAULT 0
                )
                ''')

            conn.commit()

        except Exception as e:
            logging.error(f'Ошибка при создании таблиц: {e}')

        finally:
            if conn:
                conn.close()

    def save_cart_to_db(self, user_id, items):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id, ))

            for item in items:
                cursor.execute('''
                INSERT INTO cart_items (user_id, product, quantity) VALUES (?, ?, ?)
                ''', (user_id, item['product'], item['quantity']))

            conn.commit()

        except Exception as e:
            logging.error(f'Ошибка при сохранении карточки пользователя {user_id}: {e}')
            if conn:
                conn.rollback()

        finally:
            if conn:
                conn.close()

    def load_cart_from_db(self, user_id):
        conn = None
        result = []
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
            SELECT * FROM cart_items WHERE user_id=?
            ''', (user_id,))

            result = [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logging.error(f'Ошибка при загрузке картчоки пользователя {user_id}: {e}')
            if conn:
                conn.rollback()

        finally:
            if conn:
                conn.close()

            return result

    def clear_cart_from_db(self, user_id):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
            DELETE FROM cart_items WHERE user_id=?
            ''', (user_id,))

            conn.commit()
        except Exception as e:
            logging.error(f'Ошибка при очистке корзины пользователя {user_id}: {e}')
            if conn:
                conn.rollback()

        finally:
            if conn:
                conn.close()

    def add_user(self, user_id: int, username: str, first_name= str, referrer_id: int = None):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name, referrer_id) 
                VALUES (?, ?, ?, ?)''', (user_id, username, first_name, referrer_id))

            conn.commit()
        except Exception as e:
            logging.error(f'Ошибка при добавлении пользователя: {e}')
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()

    def get_order_user_id(self, order_id: int) -> int:
        conn = None
        user_id = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT user_id FROM orders WHERE id = ?', (order_id,))

            result = cursor.fetchone()

            if result:
                user_id = result[0]

        except Exception as e:
            logging.error(f'Ошибка при получении user_id для заказа {order_id}: {e}')

        finally:
            if conn:
                conn.close()
            return user_id

    def get_orders_by_user(self, search_term: str):
        conn = None
        orders = []
        try:
            conn = sqlite3.connect(self.db_path)

            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
            SELECT o.*, u.username, u.first_name 
            FROM orders o 
            LEFT JOIN users u ON o.user_id = u.user_id
            WHERE u.username LIKE ? OR u.first_name LIKE ?
            ORDER BY o.created_at DESC
            ''', (f'%{search_term}%', f'%{search_term}%'))

            orders = [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logging.error(f'Произошла ошибка при получении информации про заказ {search_term}: {e}')

        finally:
            if conn:
                conn.close()
            return orders

    def get_product_price(self, product_name):
        conn = None
        price = 0
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT price FROM orders WHERE name = ?', (product_name,))

            result = cursor.fetchall()

            if result:
                price = result[0][0]
            else:
                price = 0

        except Exception as e:
            logging.error(f'Произошла ошибка в получении цены: {e}')
        finally:
            if conn:
                conn.close()
            return price


    def user_conn_ref(self, user_id: int) -> int:
        conn = None
        count = 0
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
            SELECT COUNT(*) FROM users WHERE referrer_id = ?
            ''', (user_id,))

            count = cursor.fetchone()[0]

        except Exception as e:
            logging.error(f'Ошибка в реферальной системе пользователя {user_id}: {e}')
            if conn:
                conn.rollback()

        finally:
            if conn:
                conn.close()

if __name__ == '__main__':
    db = DBManager()

    my_items = [{'product': 'Книга', 'quantity': 1}, {'product': 'Ручка', 'quantity': 5}]
    db.save_cart_to_db(1, my_items)

    cart_data = db.load_cart_from_db(user_id=1)
    print('Загружены данные:', cart_data)

    clear_data = db.load_cart_from_db(user_id=1)
    print('Загружены данные:')

    add_data = db.load_cart_from_db(user_id=1)
    print("Добавление с БД:", add_data)