# import sqlite3
# import logging
# from contextlib import contextmanager
#
# DB_PATH = 'shop_bot.db'
#
# @contextmanager
# def get_db_connection():
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     try:
#         yield conn
#         conn.commit()
#     except Exception as e:
#         conn.rollback()
#         logging.error(f"Ошибка БД: {e}")
#         raise
#     finally:
#         conn.close()
#
#
# def init_db():
#     print("🎯 init_db() ВЫЗВАНА!")
#     try:
#         with get_db_connection() as conn:
#             conn.execute('''
#                 CREATE TABLE IF NOT EXISTS users(
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     user_id INTEGER UNIQUE,
#                     username TEXT,
#                     first_name TEXT,
#                     price INTEGER DEFAULT 0,
#                     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
#                     referrer_id INTEGER DEFAULT NULL
#                 )
#             ''')
#
#             conn.execute('''
#                 CREATE TABLE IF NOT EXISTS orders(
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     user_id INTEGER,
#                     product TEXT,
#                     quantity INTEGER,
#                     address TEXT,
#                     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
#                     status TEXT DEFAULT 'new',
#                     price INTEGER DEFAULT 0
#                 )
#             ''')
#             conn.execute('''
#                     CREATE TABLE IF NOT EXISTS cart_items(
#                         id INTEGER PRIMARY KEY AUTOINCREMENT,
#                         user_id INTEGER,
#                         product TEXT,
#                         quantity INTEGER,
#                         created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
#                         FOREIGN KEY (user_id) REFERENCES users (user_id)
#                     )
#                 ''')
#             print('✅ Таблица cart_items создана')
#
#             conn.execute('''
#             CREATE TABLE IF NOT EXISTS products(
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT UNIQUE,
#             price INTEGER,
#             category TEXT
#             )
#         ''')
#
#             products = [
#                 ('Пицца Маргарита', 209, 'еда'),
#                 ('Кофе Латте', 70, 'еда'),
#                 ('Бургер Комбо', 189, 'еда'),
#                 ('Салат Цезарь', 120, 'еда'),
#                 ('Футболка', 150, 'товары'),
#                 ('Кружка', 100, 'товары'),
#                 ('Чехол для телефона', 200, 'товары'),
#                 ('Доставка', 40, 'услуги'),
#                 ('Упаковка подарка', 50, 'услуги'),
#                 ('Консультация', 100, 'услуги')
#             ]
#
#             for name,price,category in products:
#                 conn.execute('''
#                 INSERT OR IGNORE INTO products(name, price, category)
#                 VALUES (?, ?, ?)
#             ''', (name, price, category))
#
#             try:
#                 conn.execute('ALTER TABLE orders ADD COLUMN comment TEXT DEFAULT ""')
#                 print('✅ Колонка comment добавлена в таблицу orders')
#             except Exception:
#                 print('ℹ️ Колонка comment уже существует')
#
#         print("✅ Таблицы созданы успешно!")
#     except Exception as e:
#         print(f"❌ Ошибка при создании таблиц: {e}")
#
#
# def get_all_products():
#     with get_db_connection() as conn:
#         result = conn.execute('SELECT name, price FROM products')
#         return [dict(row) for row in result.fetchall()]
#
# def get_products_by_category(category):
#     with get_db_connection() as conn:
#         result = conn.execute(
#             'SELECT name, price FROM products WHERE category = ?',
#             (category,)
#         )
#         return [dict(row) for row in result.fetchall()]
#
# def add_order(user_id, product, quantity, address, comment, price=0):
#     print(f"[DB] Сохраняю заказ: {user_id}, {product}, {quantity}, {address}")
#
#     if not address:
#         raise ValueError("Адрес не может быть пустым")
#     if not product:
#         raise ValueError("Товар не может быть пустым")
#     if not quantity or quantity <= 0:
#         raise ValueError("Количество должно быть больше 0")
#
#     with get_db_connection() as conn:
#        cursor = conn.execute('''
#             INSERT INTO orders (user_id, product, quantity, address, comment, price)
#             VALUES (?, ?, ?, ?, ?, ?)
#         ''', (user_id, product, quantity, address, comment, price))
#
# def add_user(user_id: int, username: str, first_name: str, referrer_id: int = None):
#     with get_db_connection() as conn:
#         conn.execute('''
#             INSERT OR IGNORE INTO users (user_id, username, first_name, referrer_id)
#             VALUES (?, ?, ?, ?)
#         ''', (user_id, username, first_name, referrer_id))
#
# def get_user_orders(user_id):
#     with get_db_connection() as conn:
#         result = conn.execute('''
#             SELECT product, quantity, address, created_at
#             FROM orders
#             WHERE user_id = ?
#             ORDER BY created_at DESC
#         ''', (user_id,))
#         return result.fetchall()
#
# def user_conn_ref(user_id: int) -> int:
#         with get_db_connection() as conn:
#             result = conn.execute('''
#                 SELECT COUNT(*) FROM users WHERE referrer_id = ?
#             ''', (user_id,))
#             return result.fetchone()[0]
#
# def get_all_orders():
#     with get_db_connection() as conn:
#         result = conn.execute('''
#         SELECT o.*, u.username, u.first_name
#             FROM orders o
#             LEFT JOIN users u ON o.user_id = u.user_id
#             ORDER BY o.created_at DESC
#             LIMIT 50
#         ''')
#         return result.fetchall()
#
# def get_users_count():
#     with get_db_connection() as conn:
#         result = conn.execute('SELECT COUNT(*) FROM users')
#         return result.fetchone()[0]
#
# def update_order_status(order_id, status):
#     with get_db_connection() as conn:
#         conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
#
# def get_orders_by_user(username):
#     with get_db_connection() as conn:
#         result = conn.execute('''
#             SELECT o.*, u.username, u.first_name
#             FROM orders o
#             LEFT JOIN users u ON o.user_id = u.user_id
#             WHERE u.username LIKE ? OR u.first_name LIKE ?
#             ORDER BY o.created_at DESC
#         ''', (f'%{username}%', f'%{username}%'))
#         return result.fetchall()
