from flask import Flask, jsonify, request, g
from flask_cors import CORS
import sqlite3
import os
import datetime
from functools import wraps

try:
    import jwt
except ImportError:
    exit(1)

try:
    import bcrypt
except ImportError:
    exit(1)

app = Flask(__name__)


CORS(app, resources={r"/*": {"origins": "*"}})

# Секретный ключ для JWT
app.config['SECRET_KEY'] = 'your-secret-key-here-cybertech-2024'

# Путь к БД
if os.path.exists('/app/database/shop.db'):
    DATABASE = '/app/database/shop.db'
else:
    DATABASE = os.path.join(os.path.dirname(__file__), '../database/shop.db')

print(f" Путь к БД: {DATABASE}")
print(f" Файл существует: {os.path.exists(DATABASE)}")
print(f" Текущая директория: {os.getcwd()}")

# ============================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С БД
# ============================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# ДЕКОРАТОР ДЛЯ ПРОВЕРКИ ТОКЕНА
# ============================================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]
        
        if not token:
            return jsonify({'error': 'Требуется авторизация'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            conn = get_db_connection()
            user = conn.execute(
                'SELECT id, username, email, role FROM users WHERE id = ?',
                (current_user_id,)
            ).fetchone()
            conn.close()
            
            if not user:
                return jsonify({'error': 'Пользователь не найден'}), 401
            
            g.current_user = dict(user)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Токен истек'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Неверный токен'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 401
        
        return f(*args, **kwargs)
    return decorated

# ============================================
# API: РЕГИСТРАЦИЯ
# ============================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Отсутствуют данные'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not email or not password:
            return jsonify({'error': 'Все поля обязательны'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Пароль должен быть не менее 6 символов'}), 400
        
        conn = get_db_connection()
        
        # Проверяем email
        existing = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            conn.close()
            return jsonify({'error': 'Пользователь с таким email уже существует'}), 400
        
        # Проверяем username
        existing = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if existing:
            conn.close()
            return jsonify({'error': 'Пользователь с таким именем уже существует'}), 400
        
        # Хешируем пароль и сохраняем как строку
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        password_hash_str = password_hash.decode('utf-8')
        
        # Создаем пользователя
        conn.execute('''
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, 'user')
        ''', (username, email, password_hash_str))
        conn.commit()
        
        # Получаем ID созданного пользователя
        user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Регистрация успешна!',
            'user': {
                'id': user_id,
                'username': username,
                'email': email,
                'role': 'user'
            }
        }), 201
        
    except Exception as e:
        print(f" Ошибка регистрации: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# API: ЛОГИН (ВХОД) - С ОТЛАДКОЙ
# ============================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        print(" Получен запрос на вход")
        
        data = request.get_json()
        print(f" Полученные данные: {data}")
        
        if not data:
            print(" Нет данных в запросе")
            return jsonify({'error': 'Отсутствуют данные'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        print(f" Email: {email}")
        print(f" Пароль: {'*' * len(password)}")
        
        if not email or not password:
            print(" Email или пароль пустые")
            return jsonify({'error': 'Email и пароль обязательны'}), 400
        
        conn = get_db_connection()
        
        # Ищем пользователя по email
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if not user:
            print(f" Пользователь с email {email} не найден")
            return jsonify({'error': 'Неверный email или пароль'}), 401
        
        print(f" Пользователь найден: {user['username']}")
        print(f" Хеш пароля из БД: {user['password_hash'][:30]}...")
        
        # Проверяем пароль
        password_hash_bytes = user['password_hash']
        
        # Если это строка, преобразуем в байты
        if isinstance(password_hash_bytes, str):
            password_hash_bytes = password_hash_bytes.encode('utf-8')
        
        # Проверяем пароль
        try:
            password_check = bcrypt.checkpw(password.encode('utf-8'), password_hash_bytes)
            print(f" Результат проверки пароля: {password_check}")
        except Exception as e:
            print(f" Ошибка проверки пароля: {e}")
            return jsonify({'error': f'Ошибка проверки пароля: {str(e)}'}), 500
        
        if not password_check:
            print(" Пароль не совпадает")
            return jsonify({'error': 'Неверный email или пароль'}), 401
        
        # Создаем JWT токен
        print(" Создание JWT токена...")
        token = jwt.encode({
            'user_id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        print(" Токен создан успешно!")
        
        return jsonify({
            'success': True,
            'message': 'Вход выполнен успешно!',
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        })
        
    except Exception as e:
        print(f" ОШИБКА ВХОДА: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ============================================
# API: ПРОВЕРКА ТОКЕНА (кто я)
# ============================================

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user():
    return jsonify({
        'user': g.current_user,
        'is_authenticated': True
    })

# ============================================
# API: ВЫХОД
# ============================================

@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout():
    return jsonify({
        'success': True,
        'message': 'Выход выполнен успешно'
    })

# ============================================
# API: ПОЛУЧЕНИЕ ВСЕХ ТОВАРОВ
# ============================================

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = None
    try:
        conn = get_db_connection()
        
        products = conn.execute('''
            SELECT 
                p.id,
                p.category_id,
                p.name,
                p.description,
                p.price,
                p.image_url,
                p.manufacturer,
                c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.id DESC
        ''').fetchall()
        
        result = []
        for row in products:
            result.append({
                'id': row['id'],
                'category_id': row['category_id'],
                'name': row['name'],
                'description': row['description'] or '',
                'price': row['price'],
                'image_url': row['image_url'] or 'https://via.placeholder.com/300x300?text=No+Image',
                'manufacturer': row['manufacturer'] or 'Не указан',
                'category': row['category_name'] or 'Без категории'
            })
        
        return jsonify(result)
    
    except Exception as e:
        print(f" Ошибка получения товаров: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()
# ============================================
# API: ПОЛУЧЕНИЕ ТОВАРОВ ПО КАТЕГОРИИ
# ============================================

@app.route('/api/products/category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    conn = None
    try:
        conn = get_db_connection()
        
        products = conn.execute('''
            SELECT 
                p.id,
                p.category_id,
                p.name,
                p.description,
                p.price,
                p.image_url,
                p.manufacturer,
                c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.category_id = ?
            ORDER BY p.id DESC
        ''', (category_id,)).fetchall()
        
        result = []
        for row in products:
            result.append({
                'id': row['id'],
                'category_id': row['category_id'],
                'name': row['name'],
                'description': row['description'] or '',
                'price': row['price'],
                'image_url': row['image_url'] or 'https://via.placeholder.com/300x300?text=No+Image',
                'manufacturer': row['manufacturer'] or 'Не указан',
                'category': row['category_name'] or 'Без категории'
            })
        
        return jsonify(result)
    
    except Exception as e:
        print(f" Ошибка получения товаров по категории: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()
# ============================================
# API: ПОИСК ТОВАРОВ (регистронезависимый через Python)
# ============================================

@app.route('/api/products/search', methods=['GET'])
def search_products():
    conn = None
    try:
        query = request.args.get('q', '').strip().lower()
        print(f"🔍 Поиск: '{query}'")
        
        conn = get_db_connection()
        
        # Получаем все товары
        products = conn.execute('''
            SELECT 
                p.id,
                p.category_id,
                p.name,
                p.description,
                p.price,
                p.image_url,
                p.manufacturer,
                c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.id DESC
        ''').fetchall()
        
        # Фильтруем в Python (регистронезависимо)
        result = []
        for row in products:
            name = row['name'].lower() if row['name'] else ''
            description = row['description'].lower() if row['description'] else ''
            manufacturer = row['manufacturer'].lower() if row['manufacturer'] else ''
            category = row['category_name'].lower() if row['category_name'] else ''
            
            if query in name or query in description or query in manufacturer or query in category:
                result.append({
                    'id': row['id'],
                    'category_id': row['category_id'],
                    'name': row['name'],
                    'description': row['description'] or '',
                    'price': row['price'],
                    'image_url': row['image_url'] or 'https://via.placeholder.com/300x300?text=No+Image',
                    'manufacturer': row['manufacturer'] or 'Не указан',
                    'category': row['category_name'] or 'Без категории'
                })
        
        print(f"✅ Найдено товаров: {len(result)}")
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()
# ============================================
# API: ИЗБРАННОЕ (добавление)
# ============================================

@app.route('/api/favorites/add', methods=['POST'])
@token_required
def add_to_favorites():
    """
    Добавляет товар в избранное текущего пользователя
    """
    conn = None
    try:
        data = request.get_json()
        user_id = g.current_user['id']
        product_id = data.get('product_id')
        
        if not product_id:
            return jsonify({'error': 'product_id обязателен'}), 400
        
        conn = get_db_connection()
        
        # Проверяем, есть ли уже в избранном
        existing = conn.execute('''
            SELECT id FROM favorites 
            WHERE user_id = ? AND product_id = ?
        ''', (user_id, product_id)).fetchone()
        
        if existing:
            conn.close()
            return jsonify({'error': 'Товар уже в избранном'}), 400
        
        # Добавляем в избранное
        conn.execute('''
            INSERT INTO favorites (user_id, product_id)
            VALUES (?, ?)
        ''', (user_id, product_id))
        conn.commit()
        
        # Получаем общее количество избранного
        count = conn.execute('''
            SELECT COUNT(*) as total FROM favorites WHERE user_id = ?
        ''', (user_id,)).fetchone()['total']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Товар добавлен в избранное',
            'total': count
        })
    
    except Exception as e:
        print(f"❌ Ошибка добавления в избранное: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================
# API: ИЗБРАННОЕ (удаление)
# ============================================

@app.route('/api/favorites/remove', methods=['DELETE'])
@token_required
def remove_from_favorites():
    """
    Удаляет товар из избранного
    """
    conn = None
    try:
        data = request.get_json()
        user_id = g.current_user['id']
        product_id = data.get('product_id')
        
        if not product_id:
            return jsonify({'error': 'product_id обязателен'}), 400
        
        conn = get_db_connection()
        
        # Проверяем, есть ли в избранном
        existing = conn.execute('''
            SELECT id FROM favorites 
            WHERE user_id = ? AND product_id = ?
        ''', (user_id, product_id)).fetchone()
        
        if not existing:
            conn.close()
            return jsonify({'error': 'Товар не найден в избранном'}), 404
        
        # Удаляем из избранного
        conn.execute('''
            DELETE FROM favorites 
            WHERE user_id = ? AND product_id = ?
        ''', (user_id, product_id))
        conn.commit()
        
        # Получаем общее количество избранного
        count = conn.execute('''
            SELECT COUNT(*) as total FROM favorites WHERE user_id = ?
        ''', (user_id,)).fetchone()['total']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Товар удален из избранного',
            'total': count
        })
    
    except Exception as e:
        print(f"❌ Ошибка удаления из избранного: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================
# API: ПОЛУЧЕНИЕ ИЗБРАННОГО
# ============================================

@app.route('/api/favorites', methods=['GET'])
@token_required
def get_favorites():
    """
    Возвращает список избранных товаров пользователя
    """
    conn = None
    try:
        user_id = g.current_user['id']
        conn = get_db_connection()
        
        favorites = conn.execute('''
            SELECT 
                favorites.id as favorite_id,
                favorites.product_id,
                products.name,
                products.price,
                products.image_url,
                products.manufacturer,
                categories.name as category_name
            FROM favorites
            JOIN products ON favorites.product_id = products.id
            LEFT JOIN categories ON products.category_id = categories.id
            WHERE favorites.user_id = ?
            ORDER BY favorites.id DESC
        ''', (user_id,)).fetchall()
        
        result = []
        for row in favorites:
            result.append({
                'favorite_id': row['favorite_id'],
                'product_id': row['product_id'],
                'name': row['name'],
                'price': row['price'],
                'image_url': row['image_url'] or 'https://via.placeholder.com/300x300?text=No+Image',
                'manufacturer': row['manufacturer'] or 'Не указан',
                'category': row['category_name'] or 'Без категории'
            })
        
        conn.close()
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Ошибка получения избранного: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================
# API: ПРОВЕРКА ИЗБРАННОГО (для кнопок)
# ============================================

@app.route('/api/favorites/check/<int:product_id>', methods=['GET'])
@token_required
def check_favorite(product_id):
    """
    Проверяет, есть ли товар в избранном у пользователя
    """
    conn = None
    try:
        user_id = g.current_user['id']
        conn = get_db_connection()
        
        existing = conn.execute('''
            SELECT id FROM favorites 
            WHERE user_id = ? AND product_id = ?
        ''', (user_id, product_id)).fetchone()
        
        conn.close()
        return jsonify({'is_favorite': bool(existing)})
    
    except Exception as e:
        print(f"❌ Ошибка проверки избранного: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================
# API: КОРЗИНА (добавление)
# ============================================

@app.route('/api/cart/add', methods=['POST'])
@token_required
def add_to_cart():
    """
    Добавляет товар в корзину текущего пользователя
    """
    conn = None
    try:
        data = request.get_json()
        user_id = g.current_user['id']
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return jsonify({'error': 'product_id обязателен'}), 400
        
        if quantity <= 0:
            return jsonify({'error': 'Количество должно быть больше 0'}), 400
        
        conn = get_db_connection()
        
        # Проверяем, есть ли уже товар в корзине
        existing = conn.execute('''
            SELECT id, quantity FROM cart 
            WHERE user_id = ? AND product_id = ?
        ''', (user_id, product_id)).fetchone()
        
        if existing:
            # Обновляем количество
            new_quantity = existing['quantity'] + quantity
            conn.execute('''
                UPDATE cart SET quantity = ? 
                WHERE id = ?
            ''', (new_quantity, existing['id']))
        else:
            # Добавляем новый товар
            conn.execute('''
                INSERT INTO cart (user_id, product_id, quantity)
                VALUES (?, ?, ?)
            ''', (user_id, product_id, quantity))
        
        conn.commit()
        
        # Получаем общее количество товаров в корзине
        total = conn.execute('''
            SELECT SUM(quantity) as total FROM cart WHERE user_id = ?
        ''', (user_id,)).fetchone()['total'] or 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Товар добавлен в корзину',
            'total_items': total
        })
    
    except Exception as e:
        print(f"❌ Ошибка добавления в корзину: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================
# API: КОРЗИНА (получение)
# ============================================

@app.route('/api/cart', methods=['GET'])
@token_required
def get_cart():
    """
    Возвращает содержимое корзины пользователя
    """
    conn = None
    try:
        user_id = g.current_user['id']
        conn = get_db_connection()
        
        cart_items = conn.execute('''
            SELECT 
                cart.id as cart_id,
                cart.product_id,
                cart.quantity,
                products.name,
                products.price,
                products.image_url,
                products.manufacturer,
                categories.name as category_name
            FROM cart
            JOIN products ON cart.product_id = products.id
            LEFT JOIN categories ON products.category_id = categories.id
            WHERE cart.user_id = ?
            ORDER BY cart.id DESC
        ''', (user_id,)).fetchall()
        
        result = []
        total_price = 0
        
        for row in cart_items:
            item_total = row['price'] * row['quantity']
            total_price += item_total
            
            result.append({
                'cart_id': row['cart_id'],
                'product_id': row['product_id'],
                'name': row['name'],
                'price': row['price'],
                'quantity': row['quantity'],
                'image_url': row['image_url'] or 'https://via.placeholder.com/100x100?text=No+Image',
                'manufacturer': row['manufacturer'] or 'Не указан',
                'category': row['category_name'] or 'Без категории',
                'total': round(item_total, 2)
            })
        
        conn.close()
        
        return jsonify({
            'items': result,
            'total_items': len(result),
            'total_quantity': sum(item['quantity'] for item in result),
            'total_price': round(total_price, 2)
        })
    
    except Exception as e:
        print(f"❌ Ошибка получения корзины: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================
# API: КОРЗИНА (обновление количества)
# ============================================

@app.route('/api/cart/update', methods=['PUT'])
@token_required
def update_cart_item():
    """
    Обновляет количество товара в корзине
    """
    conn = None
    try:
        data = request.get_json()
        user_id = g.current_user['id']
        cart_id = data.get('cart_id')
        quantity = data.get('quantity')
        
        if not cart_id:
            return jsonify({'error': 'cart_id обязателен'}), 400
        
        if quantity is None or quantity < 0:
            return jsonify({'error': 'Неверное количество'}), 400
        
        conn = get_db_connection()
        
        # Проверяем, принадлежит ли товар пользователю
        existing = conn.execute('''
            SELECT id FROM cart 
            WHERE id = ? AND user_id = ?
        ''', (cart_id, user_id)).fetchone()
        
        if not existing:
            conn.close()
            return jsonify({'error': 'Товар не найден в корзине'}), 404
        
        if quantity == 0:
            # Удаляем товар
            conn.execute('DELETE FROM cart WHERE id = ?', (cart_id,))
        else:
            # Обновляем количество
            conn.execute('''
                UPDATE cart SET quantity = ? 
                WHERE id = ?
            ''', (quantity, cart_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Корзина обновлена'
        })
    
    except Exception as e:
        print(f"❌ Ошибка обновления корзины: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================
# API: КОРЗИНА (удаление товара)
# ============================================

@app.route('/api/cart/remove/<int:cart_id>', methods=['DELETE'])
@token_required
def remove_from_cart(cart_id):
    """
    Удаляет товар из корзины
    """
    conn = None
    try:
        user_id = g.current_user['id']
        conn = get_db_connection()
        
        # Проверяем, принадлежит ли товар пользователю
        existing = conn.execute('''
            SELECT id FROM cart 
            WHERE id = ? AND user_id = ?
        ''', (cart_id, user_id)).fetchone()
        
        if not existing:
            conn.close()
            return jsonify({'error': 'Товар не найден в корзине'}), 404
        
        conn.execute('DELETE FROM cart WHERE id = ?', (cart_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Товар удален из корзины'
        })
    
    except Exception as e:
        print(f"❌ Ошибка удаления из корзины: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================
# API: КОРЗИНА (очистка)
# ============================================

@app.route('/api/cart/clear', methods=['DELETE'])
@token_required
def clear_cart():
    """
    Очищает всю корзину пользователя
    """
    conn = None
    try:
        user_id = g.current_user['id']
        conn = get_db_connection()
        
        conn.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Корзина очищена'
        })
    
    except Exception as e:
        print(f"❌ Ошибка очистки корзины: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()
# ============================================
# API: СОЗДАНИЕ ЗАКАЗА
# ============================================

@app.route('/api/orders/create', methods=['POST'])
@token_required
def create_order():
    """
    Оформляет заказ: создает запись в таблице orders
    и переносит товары из cart в order_items
    """
    conn = None
    try:
        user_id = g.current_user['id']
        data = request.get_json()
        
        delivery_address = data.get('delivery_address', '').strip()
        comment = data.get('comment', '').strip()
        
        if not delivery_address:
            return jsonify({'error': 'Адрес доставки обязателен'}), 400
        
        conn = get_db_connection()
        
        # Получаем товары из корзины
        cart_items = conn.execute('''
            SELECT 
                cart.product_id,
                cart.quantity,
                products.price
            FROM cart
            JOIN products ON cart.product_id = products.id
            WHERE cart.user_id = ?
        ''', (user_id,)).fetchall()
        
        if not cart_items:
            conn.close()
            return jsonify({'error': 'Корзина пуста'}), 400
        
        # Рассчитываем итоговую сумму
        total_price = sum(item['price'] * item['quantity'] for item in cart_items)
        
        # Генерируем номер заказа
        from datetime import datetime
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{user_id}-{datetime.now().strftime('%H%M%S')}"
        
        # Создаем заказ
        cursor = conn.execute('''
            INSERT INTO orders (
                user_id, 
                order_number, 
                total_price, 
                delivery_address,
                comment,
                status,
                order_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            order_number,
            round(total_price, 2),
            delivery_address,
            comment,
            'pending',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        order_id = cursor.lastrowid
        
        # Переносим товары в order_items
        for item in cart_items:
            conn.execute('''
                INSERT INTO order_items (
                    order_id,
                    product_id,
                    quantity,
                    price_at_moment
                ) VALUES (?, ?, ?, ?)
            ''', (
                order_id,
                item['product_id'],
                item['quantity'],
                item['price']
            ))
        
        # Очищаем корзину
        conn.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Заказ оформлен успешно!',
            'order_id': order_id,
            'order_number': order_number,
            'total_price': round(total_price, 2)
        })
    
    except Exception as e:
        print(f"❌ Ошибка оформления заказа: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================
# API: ПОЛУЧЕНИЕ ЗАКАЗОВ ПОЛЬЗОВАТЕЛЯ
# ============================================

@app.route('/api/orders', methods=['GET'])
@token_required
def get_orders():
    """
    Возвращает все заказы текущего пользователя
    """
    conn = None
    try:
        user_id = g.current_user['id']
        conn = get_db_connection()
        
        orders = conn.execute('''
            SELECT 
                id,
                order_number,
                order_date,
                total_price,
                delivery_address,
                status,
                comment
            FROM orders 
            WHERE user_id = ?
            ORDER BY order_date DESC
        ''', (user_id,)).fetchall()
        
        result = []
        for row in orders:
            # Получаем товары для каждого заказа
            items = conn.execute('''
                SELECT 
                    order_items.product_id,
                    order_items.quantity,
                    order_items.price_at_moment,
                    products.name,
                    products.image_url
                FROM order_items
                JOIN products ON order_items.product_id = products.id
                WHERE order_items.order_id = ?
            ''', (row['id'],)).fetchall()
            
            items_list = []
            for item in items:
                items_list.append({
                    'product_id': item['product_id'],
                    'name': item['name'],
                    'quantity': item['quantity'],
                    'price': item['price_at_moment'],
                    'image_url': item['image_url'] or 'https://via.placeholder.com/100x100?text=No+Image'
                })
            
            result.append({
                'id': row['id'],
                'order_number': row['order_number'],
                'order_date': row['order_date'],
                'total_price': row['total_price'],
                'delivery_address': row['delivery_address'],
                'status': row['status'],
                'comment': row['comment'] or '',
                'items': items_list
            })
        
        conn.close()
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Ошибка получения заказов: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================
# API: ОБНОВЛЕНИЕ СТАТУСА ЗАКАЗА
# ============================================

@app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
@token_required
def update_order_status(order_id):
    """
    Обновляет статус заказа (например, paid/pending)
    """
    conn = None
    try:
        user_id = g.current_user['id']
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Статус обязателен'}), 400
        
        conn = get_db_connection()
        
        # Проверяем, принадлежит ли заказ пользователю
        order = conn.execute('''
            SELECT id FROM orders 
            WHERE id = ? AND user_id = ?
        ''', (order_id, user_id)).fetchone()
        
        if not order:
            conn.close()
            return jsonify({'error': 'Заказ не найден'}), 404
        
        conn.execute('''
            UPDATE orders SET status = ? WHERE id = ?
        ''', (new_status, order_id))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Статус заказа обновлен',
            'status': new_status
        })
    
    except Exception as e:
        print(f"❌ Ошибка обновления статуса: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================
# ДЕКОРАТОР ДЛЯ ПРОВЕРКИ АДМИНА
# ============================================

def admin_required(f):
    """Декоратор для проверки прав администратора"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Сначала проверяем токен
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]
        
        if not token:
            return jsonify({'error': 'Требуется авторизация'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            conn = get_db_connection()
            user = conn.execute(
                'SELECT id, username, email, role FROM users WHERE id = ?',
                (current_user_id,)
            ).fetchone()
            conn.close()
            
            if not user:
                return jsonify({'error': 'Пользователь не найден'}), 401
            
            if user['role'] != 'admin':
                return jsonify({'error': 'Доступ запрещен. Требуются права администратора'}), 403
            
            g.current_user = dict(user)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Токен истек'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Неверный токен'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 401
        
        return f(*args, **kwargs)
    return decorated

# ============================================
# API: ПОЛУЧЕНИЕ ВСЕХ ТОВАРОВ (админ)
# ============================================

@app.route('/api/admin/products', methods=['GET'])
@admin_required
def admin_get_products():
    """
    Получить все товары (с полной информацией для админа)
    """
    conn = None
    try:
        conn = get_db_connection()
        
        products = conn.execute('''
            SELECT 
                p.id,
                p.category_id,
                p.name,
                p.description,
                p.price,
                p.image_url,
                p.manufacturer,
                c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.id DESC
        ''').fetchall()
        
        result = []
        for row in products:
            result.append({
                'id': row['id'],
                'category_id': row['category_id'],
                'name': row['name'],
                'description': row['description'] or '',
                'price': row['price'],
                'image_url': row['image_url'] or '',
                'manufacturer': row['manufacturer'] or '',
                'category_name': row['category_name'] or 'Без категории'
            })
        
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Ошибка получения товаров: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================
# API: СОЗДАНИЕ ТОВАРА (админ)
# ============================================

@app.route('/api/admin/products', methods=['POST'])
@admin_required
def admin_create_product():
    """
    Создание нового товара
    """
    conn = None
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        category_id = data.get('category_id')
        price = data.get('price')
        description = data.get('description', '').strip()
        image_url = data.get('image_url', '').strip()
        manufacturer = data.get('manufacturer', '').strip()
        
        if not name:
            return jsonify({'error': 'Название товара обязательно'}), 400
        
        if not category_id:
            return jsonify({'error': 'Категория обязательна'}), 400
        
        if not price or price <= 0:
            return jsonify({'error': 'Цена должна быть больше 0'}), 400
        
        conn = get_db_connection()
        
        # Проверяем, существует ли категория
        category = conn.execute(
            'SELECT id FROM categories WHERE id = ?', (category_id,)
        ).fetchone()
        
        if not category:
            conn.close()
            return jsonify({'error': 'Категория не найдена'}), 404
        
        conn.execute('''
            INSERT INTO products (name, category_id, price, description, image_url, manufacturer)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, category_id, price, description, image_url, manufacturer))
        
        conn.commit()
        product_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Товар создан успешно',
            'product_id': product_id
        }), 201
    
    except Exception as e:
        print(f"❌ Ошибка создания товара: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================
# API: ОБНОВЛЕНИЕ ТОВАРА (админ)
# ============================================

@app.route('/api/admin/products/<int:product_id>', methods=['PUT'])
@admin_required
def admin_update_product(product_id):
    """
    Обновление товара
    """
    conn = None
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        category_id = data.get('category_id')
        price = data.get('price')
        description = data.get('description', '').strip()
        image_url = data.get('image_url', '').strip()
        manufacturer = data.get('manufacturer', '').strip()
        
        if not name:
            return jsonify({'error': 'Название товара обязательно'}), 400
        
        if not category_id:
            return jsonify({'error': 'Категория обязательна'}), 400
        
        if not price or price <= 0:
            return jsonify({'error': 'Цена должна быть больше 0'}), 400
        
        conn = get_db_connection()
        
        # Проверяем, существует ли товар
        product = conn.execute(
            'SELECT id FROM products WHERE id = ?', (product_id,)
        ).fetchone()
        
        if not product:
            conn.close()
            return jsonify({'error': 'Товар не найден'}), 404
        
        # Проверяем, существует ли категория
        category = conn.execute(
            'SELECT id FROM categories WHERE id = ?', (category_id,)
        ).fetchone()
        
        if not category:
            conn.close()
            return jsonify({'error': 'Категория не найдена'}), 404
        
        conn.execute('''
            UPDATE products 
            SET name = ?, category_id = ?, price = ?, description = ?, 
                image_url = ?, manufacturer = ?
            WHERE id = ?
        ''', (name, category_id, price, description, image_url, manufacturer, product_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Товар обновлен успешно'
        })
    
    except Exception as e:
        print(f"❌ Ошибка обновления товара: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================
# API: УДАЛЕНИЕ ТОВАРА (админ)
# ============================================

@app.route('/api/admin/products/<int:product_id>', methods=['DELETE'])
@admin_required
def admin_delete_product(product_id):
    """
    Удаление товара
    """
    conn = None
    try:
        conn = get_db_connection()
        
        # Проверяем, существует ли товар
        product = conn.execute(
            'SELECT id FROM products WHERE id = ?', (product_id,)
        ).fetchone()
        
        if not product:
            conn.close()
            return jsonify({'error': 'Товар не найден'}), 404
        
        conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Товар удален успешно'
        })
    
    except Exception as e:
        print(f"❌ Ошибка удаления товара: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================
# API: ПОЛУЧЕНИЕ ВСЕХ КАТЕГОРИЙ (админ)
# ============================================

@app.route('/api/admin/categories', methods=['GET'])
@admin_required
def admin_get_categories():
    """
    Получить все категории для админки
    """
    conn = None
    try:
        conn = get_db_connection()
        categories = conn.execute('SELECT * FROM categories ORDER BY name').fetchall()
        conn.close()
        
        return jsonify([dict(row) for row in categories])
    
    except Exception as e:
        print(f"❌ Ошибка получения категорий: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()
# ============================================
# ЗАПУСК СЕРВЕРА
# ============================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)