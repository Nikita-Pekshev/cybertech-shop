import pytest
import os
import tempfile
import json
from app import app, get_db_connection

@pytest.fixture
def client():
    """Создает тестовый клиент для API"""
    app.config['TESTING'] = True
    
    # Создаем временную БД для тестов
    with tempfile.NamedTemporaryFile(suffix='.db') as tmp:
        app.config['DATABASE'] = tmp.name
        
        # Инициализируем тестовую БД
        with app.app_context():
            conn = get_db_connection()
            
            # ✅ Добавляем IF NOT EXISTS
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user'
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    image_url TEXT,
                    manufacturer TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cart (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL CHECK(quantity > 0),
                    UNIQUE(user_id, product_id)
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    UNIQUE(user_id, product_id)
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    order_number TEXT UNIQUE NOT NULL,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_price REAL NOT NULL,
                    delivery_address TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    comment TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    price_at_moment REAL NOT NULL
                )
            ''')
            
            # Очищаем таблицы перед каждым тестом
            conn.execute('DELETE FROM order_items')
            conn.execute('DELETE FROM orders')
            conn.execute('DELETE FROM cart')
            conn.execute('DELETE FROM favorites')
            conn.execute('DELETE FROM users')
            conn.execute('DELETE FROM products')
            conn.execute('DELETE FROM categories')
            
            # Добавляем тестовые данные
            conn.execute('INSERT INTO categories (id, name) VALUES (1, "Тестовая категория")')
            conn.execute('''
                INSERT INTO products (id, category_id, name, description, price, image_url, manufacturer)
                VALUES (1, 1, "Тестовый товар", "Описание тестового товара", 99.99, "", "ТестПроизводитель")
            ''')
            conn.commit()
            conn.close()
        
        with app.test_client() as client:
            yield client

@pytest.fixture
def auth_token(client):
    """Создает тестового пользователя и возвращает токен"""
    # Регистрация
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@test.com',
        'password': '123456'
    })
    
    # Логин
    response = client.post('/api/auth/login', json={
        'email': 'test@test.com',
        'password': '123456'
    })
    data = json.loads(response.data)
    return data.get('token')

@pytest.fixture
def admin_token(client):
    """Создает тестового администратора и возвращает токен"""
    # Регистрация админа
    client.post('/api/auth/register', json={
        'username': 'admin',
        'email': 'admin@test.com',
        'password': '123456'
    })
    
    # Вручную меняем роль на admin в БД
    conn = get_db_connection()
    conn.execute('UPDATE users SET role = "admin" WHERE email = "admin@test.com"')
    conn.commit()
    conn.close()
    
    # Логин
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': '123456'
    })
    data = json.loads(response.data)
    return data.get('token')