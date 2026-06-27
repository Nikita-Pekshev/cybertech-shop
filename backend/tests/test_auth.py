import json
import pytest

class TestAuth:
    """Тесты регистрации и авторизации"""
    
    def test_register_success(self, client):
        """Тест успешной регистрации"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': '123456'
        })
        data = json.loads(response.data)
        assert response.status_code == 201
        assert data['success'] == True
        assert data['user']['username'] == 'newuser'
    
    def test_register_duplicate_email(self, client):
        """Тест регистрации с уже существующим email"""
        # Первая регистрация
        client.post('/api/auth/register', json={
            'username': 'user1',
            'email': 'duplicate@test.com',
            'password': '123456'
        })
        
        # Вторая регистрация с тем же email
        response = client.post('/api/auth/register', json={
            'username': 'user2',
            'email': 'duplicate@test.com',
            'password': '123456'
        })
        data = json.loads(response.data)
        assert response.status_code == 400
        assert 'уже существует' in data['error']
    
    def test_register_duplicate_username(self, client):
        """Тест регистрации с уже существующим username"""
        client.post('/api/auth/register', json={
            'username': 'duplicate_user',
            'email': 'user1@test.com',
            'password': '123456'
        })
        
        response = client.post('/api/auth/register', json={
            'username': 'duplicate_user',
            'email': 'user2@test.com',
            'password': '123456'
        })
        data = json.loads(response.data)
        assert response.status_code == 400
        assert 'уже существует' in data['error']
    
    def test_register_short_password(self, client):
        """Тест регистрации с коротким паролем"""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@test.com',
            'password': '123'  # Меньше 6 символов
        })
        data = json.loads(response.data)
        assert response.status_code == 400
        assert 'менее 6 символов' in data['error']
    
    def test_login_success(self, client):
        """Тест успешного входа"""
        # Сначала регистрируем пользователя
        client.post('/api/auth/register', json={
            'username': 'loginuser',
            'email': 'login@test.com',
            'password': '123456'
        })
        
        # Пытаемся войти
        response = client.post('/api/auth/login', json={
            'email': 'login@test.com',
            'password': '123456'
        })
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] == True
        assert 'token' in data
    
    def test_login_wrong_password(self, client):
        """Тест входа с неправильным паролем"""
        client.post('/api/auth/register', json={
            'username': 'wrongpass',
            'email': 'wrong@test.com',
            'password': '123456'
        })
        
        response = client.post('/api/auth/login', json={
            'email': 'wrong@test.com',
            'password': 'wrongpassword'
        })
        data = json.loads(response.data)
        assert response.status_code == 401
        assert 'Неверный email или пароль' in data['error']
    
    def test_login_nonexistent_user(self, client):
        """Тест входа с несуществующим пользователем"""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@test.com',
            'password': '123456'
        })
        data = json.loads(response.data)
        assert response.status_code == 401
        assert 'Неверный email или пароль' in data['error']
    
    def test_me_endpoint_requires_auth(self, client):
        """Тест: эндпоинт /me требует авторизации"""
        response = client.get('/api/auth/me')
        data = json.loads(response.data)
        assert response.status_code == 401
        assert 'Требуется авторизация' in data['error']
    
    def test_me_endpoint_with_valid_token(self, client, auth_token):
        """Тест: /me с валидным токеном"""
        response = client.get('/api/auth/me', headers={
            'Authorization': f'Bearer {auth_token}'
        })
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['user']['username'] == 'testuser'