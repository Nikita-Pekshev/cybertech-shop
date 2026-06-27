import json
import pytest

class TestOrders:
    """Тесты заказов"""
    
    def test_create_order_requires_auth(self, client):
        """Тест: создание заказа требует авторизации"""
        response = client.post('/api/orders/create', json={
            'delivery_address': 'ул. Тестовая, д. 1'
        })
        assert response.status_code == 401
    
    def test_create_order_empty_cart(self, client, auth_token):
        """Тест: создание заказа с пустой корзиной"""
        response = client.post('/api/orders/create',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'delivery_address': 'ул. Тестовая, д. 1'
            }
        )
        data = json.loads(response.data)
        assert response.status_code == 400
        assert 'Корзина пуста' in data['error']
    
    def test_create_order_no_address(self, client, auth_token):
        """Тест: создание заказа без адреса"""
        response = client.post('/api/orders/create',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={}
        )
        data = json.loads(response.data)
        assert response.status_code == 400
        assert 'Адрес доставки обязателен' in data['error']
    
    def test_create_order_success(self, client, auth_token):
        """Тест: успешное создание заказа"""
        # Добавляем товар в корзину
        client.post('/api/cart/add',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'product_id': 1, 'quantity': 2}
        )
        
        # Создаем заказ
        response = client.post('/api/orders/create',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'delivery_address': 'ул. Тестовая, д. 1',
                'comment': 'Тестовый комментарий'
            }
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] == True
        assert 'order_number' in data
        assert 'total_price' in data
        assert data['total_price'] > 0
    
    def test_get_orders_requires_auth(self, client):
        """Тест: получение заказов требует авторизации"""
        response = client.get('/api/orders')
        assert response.status_code == 401
    
    def test_get_orders_success(self, client, auth_token):
        """Тест: успешное получение заказов"""
        # Создаем заказ
        client.post('/api/cart/add',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'product_id': 1, 'quantity': 1}
        )
        client.post('/api/orders/create',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'delivery_address': 'ул. Тестовая, д. 1'}
        )
        
        # Получаем заказы
        response = client.get('/api/orders',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert isinstance(data, list)
        assert len(data) > 0
        
        order = data[0]
        assert 'order_number' in order
        assert 'total_price' in order
        assert 'delivery_address' in order
        assert 'status' in order
        assert 'items' in order
    
    def test_update_order_status(self, client, auth_token):
        """Тест: обновление статуса заказа"""
        # Создаем заказ
        client.post('/api/cart/add',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'product_id': 1, 'quantity': 1}
        )
        create_response = client.post('/api/orders/create',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'delivery_address': 'ул. Тестовая, д. 1'}
        )
        order_data = json.loads(create_response.data)
        order_id = order_data['order_id']
        
        # Обновляем статус
        response = client.put(f'/api/orders/{order_id}/status',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'status': 'paid'}
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] == True
        assert data['status'] == 'paid'