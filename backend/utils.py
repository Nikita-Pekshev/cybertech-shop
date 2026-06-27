import re
import bcrypt
import jwt
import datetime

def validate_password(password):
    """Проверяет пароль (из register)"""
    if not password:
        return False
    return len(password) >= 6

def hash_password(password):
    """Хеширует пароль (из register)"""
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')

def check_password(password, password_hash):
    """Проверяет пароль (из login)"""
    if isinstance(password_hash, str):
        password_hash = password_hash.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), password_hash)

def generate_order_number(user_id):
    """Генерирует номер заказа (из create_order)"""
    from datetime import datetime
    return f"ORD-{datetime.now().strftime('%Y%m%d')}-{user_id}-{datetime.now().strftime('%H%M%S')}"

def validate_email(email):
    """Валидация email (используется в тестах)"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{1,}$'
    return re.match(pattern, email) is not None

def is_valid_username(username):
    """Валидация username (используется в тестах)"""
    if not username:
        return False
    if len(username) < 3:
        return False
    return re.match(r'^[a-zA-Z0-9_]+$', username) is not None

def calculate_cart_total(items):
    """Рассчитывает сумму корзины (используется в тестах)"""
    if not items:
        return 0.0
    total = sum(item.get('price', 0) * item.get('quantity', 0) for item in items)
    return round(total, 2)