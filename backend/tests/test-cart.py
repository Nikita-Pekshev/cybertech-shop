import json
import pytest

class TestCart:
    """Тесты корзины"""
    
    def test_add_to_cart_requires_auth(self, client):
        """Тест: добавление в корзину требует авторизации"""
        response = client.post('/api/cart/add', json={
            'product_id': 1,
            'quantity': 1
        })
        assert response.status_code == 401
    
    def test_add_to_cart_success(self, client, auth_token):
        """Тест: успешное добавление в корзину"""
        response = client.post('/api/cart/add',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'product_id': 1,
                'quantity': 1
            }
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] == True
        assert 'total_items' in data
    
    def test_add_to_cart_no_product(self, client, auth_token):
        """Тест: добавление без product_id"""
        response = client.post('/api/cart/add',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'quantity': 1
            }
        )
        data = json.loads(response.data)
        assert response.status_code == 400
        assert 'product_id обязателен' in data['error']
    
    def test_get_cart_requires_auth(self, client):
        """Тест: получение корзины требует авторизации"""
        response = client.get('/api/cart')
        assert response.status_code == 401
    
    def test_get_cart_success(self, client, auth_token):
        """Тест: успешное получение корзины"""
        # Добавляем товар
        client.post('/api/cart/add',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'product_id': 1, 'quantity': 1}
        )
        
        # Получаем корзину
        response = client.get('/api/cart',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert 'items' in data
        assert 'total_items' in data
        assert 'total_price' in data
        assert len(data['items']) > 0
    
    def test_remove_from_cart(self, client, auth_token):
        """Тест: удаление из корзины"""
        # Добавляем товар
        add_response = client.post('/api/cart/add',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'product_id': 1, 'quantity': 1}
        )
        
        # Получаем корзину
        cart_response = client.get('/api/cart',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        cart_data = json.loads(cart_response.data)
        cart_id = cart_data['items'][0]['cart_id']
        
        # Удаляем товар
        response = client.delete(f'/api/cart/remove/{cart_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] == True
    
    def test_clear_cart(self, client, auth_token):
        """Тест: очистка корзины"""
        # Добавляем товары
        client.post('/api/cart/add',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'product_id': 1, 'quantity': 2}
        )
        
        # Очищаем корзину
        response = client.delete('/api/cart/clear',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] == True
        
        # Проверяем, что корзина пуста
        cart_response = client.get('/api/cart',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        cart_data = json.loads(cart_response.data)
        assert len(cart_data['items']) == 0