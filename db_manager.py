import sqlite3
import logging
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DBManager:

    def __init__(self, db_path='my_database.db'):
        self.db_path = db_path
        self._create_tables()

        self._insert_initial_products()
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
            referrer_id INTEGER,
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
                    price INTEGER DEFAULT 0 -- Цена на момент заказа
                )
                ''')

            conn.commit()
            logging.info("Таблицы успешно созданы или уже существуют.")

        except Exception as e:
            logging.error(f'Ошибка при создании таблиц: {e}')

        finally:
            if conn:
                conn.close()

    def _insert_initial_products(self):
        products_data = [
            ('Латте', 70, 'Кава'),
            ('Двойной Латте', 95, 'Кава'),
            ('Пицца Пепперони', 220, 'Піцца'),
            ('Пицца Гавайская', 250, 'Піцца'),
            ('Большой Бургер', 150, 'Бургери'),
            ('Чикен Бургер', 120, 'Бургери'),
        ]

        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.executemany('''
                INSERT OR IGNORE INTO products (name, price, category) VALUES (?, ?, ?)
            ''', products_data)

            conn.commit()
            logging.info("Стартовые продукты вставлены или уже существуют.")

        except Exception as e:
            logging.error(f'Ошибка при вставке стартовых продуктов: {e}')
        finally:
            if conn:
                conn.close()


    def add_user(self, user_id: int, username: str, first_name=str, referrer_id: int = None):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name, referrer_id) 
                VALUES (?, ?, ?, ?)''', (user_id, username, first_name, referrer_id))

            conn.commit()
            logging.info(f"Пользователь {user_id} добавлен (или уже существовал).")
        except Exception as e:
            logging.error(f'Ошибка при добавлении пользователя: {e}')
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()

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

        finally:
            if conn:
                conn.close()
            return count


    def get_all_categories(self) -> List[str]:
        conn = None
        categories = []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT DISTINCT category FROM products ORDER BY category')
            categories = [row[0] for row in cursor.fetchall()]

        except Exception as e:
            logging.error(f'Ошибка при получении категорий: {e}')
        finally:
            if conn:
                conn.close()
            return categories

    def get_products_by_category(self, category: str) -> List[Dict]:
        conn = None
        products = []
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT name, price 
                FROM products 
                WHERE category = ?
                ORDER BY price
            ''', (category,))

            products = [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logging.error(f'Ошибка при получении продуктов для категории {category}: {e}')
        finally:
            if conn:
                conn.close()
            return products

    def get_product_price(self, product_name: str) -> int:
        conn = None
        price = 0
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT price FROM products WHERE name = ?', (product_name,))

            result = cursor.fetchone()

            if result:
                price = result[0]
            else:
                logging.warning(f"Продукт '{product_name}' не найден в таблице products.")

        except Exception as e:
            logging.error(f'Произошла ошибка в получении цены: {e}')
        finally:
            if conn:
                conn.close()
            return price

    def save_cart_to_db(self, user_id: int, items: List[Dict]):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))

            items_to_insert = [(user_id, item['name'], item['quantity']) for item in items]

            cursor.executemany('''
                INSERT INTO cart_items (user_id, product, quantity) VALUES (?, ?, ?)
            ''', items_to_insert)

            conn.commit()
            logging.info(f"Корзина пользователя {user_id} сохранена.")

        except Exception as e:
            logging.error(f'Ошибка при сохранении корзины пользователя {user_id}: {e}')
            if conn:
                conn.rollback()

        finally:
            if conn:
                conn.close()

    def load_cart_from_db(self, user_id: int) -> List[Dict]:
        conn = None
        result = []
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
            SELECT ci.product as name, ci.quantity, p.price, p.category
            FROM cart_items ci
            JOIN products p ON ci.product = p.name
            WHERE ci.user_id=?
            ''', (user_id,))

            result = [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logging.error(f'Ошибка при загрузке корзины пользователя {user_id}: {e}')

        finally:
            if conn:
                conn.close()

            return result

    def clear_cart_from_db(self, user_id):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
            DELETE FROM cart_items WHERE user_id=?
            ''', (user_id,))

            conn.commit()
            logging.info(f"Корзина пользователя {user_id} очищена.")
        except Exception as e:
            logging.error(f'Ошибка при очистке корзины пользователя {user_id}: {e}')
            if conn:
                conn.rollback()

        finally:
            if conn:
                conn.close()

    def place_order(self, user_id: int, address: str) -> Optional[int]:
        cart_items = self.load_cart_from_db(user_id)
        if not cart_items:
            logging.warning(f"Пользователь {user_id} попытался создать пустой заказ.")
            return None

        conn = None
        order_id = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            order_data = [
                (user_id, item['name'], item['quantity'], address, item['price'])
                for item in cart_items
            ]

            cursor.executemany('''
                INSERT INTO orders (user_id, product, quantity, address, price) 
                VALUES (?, ?, ?, ?, ?)
            ''', order_data)

            # Получаем ID первого элемента заказа (или просто последнего вставленного ID)
            # В SQLite это будет ID последней вставленной записи,
            # но для бота, обрабатывающего заказ, достаточно знать, что он создан.
            # Если вам нужен уникальный ID для всего заказа (группировка),
            # нужно добавить отдельную таблицу orders_header.
            # Пока вернем ID первой вставленной строки:
            first_item_id = cursor.lastrowid - (len(order_data) - 1)
            order_id = first_item_id

            cursor.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))

            conn.commit()
            logging.info(f"Заказ от пользователя {user_id} оформлен. ID: {order_id}")

        except Exception as e:
            logging.error(f'Ошибка при оформлении заказа для пользователя {user_id}: {e}')
            if conn:
                conn.rollback()
            order_id = None

        finally:
            if conn:
                conn.close()
            return order_id

    def get_order_user_id(self, order_id: int) -> Optional[int]:
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

    def get_orders_by_user(self, search_term: str) -> List[Dict]:
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
            logging.error(
                f'Произошла ошибка при получении информации про заказ по поисковому запросу "{search_term}": {e}')

        finally:
            if conn:
                conn.close()
            return orders