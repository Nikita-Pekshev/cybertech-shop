import json
import pytest

class TestProducts:
    """Тесты товаров"""
    
    def test_get_products(self, client):
        """Тест получения списка товаров"""
        response = client.get('/api/products')
        data = json.loads(response.data)
        assert response.status_code == 200
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Проверяем структуру товара
        product = data[0]
        assert 'id' in product
        assert 'name' in product
        assert 'price' in product
        assert 'category' in product
    
    def test_get_products_guest(self, client):
        """Тест: неавторизованный пользователь может видеть товары"""
        response = client.get('/api/products')
        assert response.status_code == 200
    
    def test_admin_get_products_requires_admin(self, client, auth_token):
        """Тест: обычный пользователь не может получить админ-список"""
        response = client.get('/api/admin/products', headers={
            'Authorization': f'Bearer {auth_token}'
        })
        data = json.loads(response.data)
        assert response.status_code == 403
    
    def test_admin_get_products_with_admin(self, client, admin_token):
        """Тест: админ может получить админ-список"""
        response = client.get('/api/admin/products', headers={
            'Authorization': f'Bearer {admin_token}'
        })
        data = json.loads(response.data)
        assert response.status_code == 200
        assert isinstance(data, list)
    
    def test_admin_create_product(self, client, admin_token):
        """Тест: админ может создать товар"""
        response = client.post('/api/admin/products', 
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'name': 'Новый тестовый товар',
                'category_id': 1,
                'price': 199.99,
                'manufacturer': 'ТестПроизводитель',
                'description': 'Описание нового товара',
                'image_url': ''
            }
        )
        data = json.loads(response.data)
        assert response.status_code == 201
        assert data['success'] == True
        assert 'product_id' in data
    
    def test_admin_create_product_no_name(self, client, admin_token):
        """Тест: создание товара без названия"""
        response = client.post('/api/admin/products',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'category_id': 1,
                'price': 199.99
            }
        )
        data = json.loads(response.data)
        assert response.status_code == 400
        assert 'Название товара обязательно' in data['error']
    
    def test_admin_update_product(self, client, admin_token):
        """Тест: админ может обновить товар"""
        # Сначала создаем товар
        create_response = client.post('/api/admin/products',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'name': 'Товар для обновления',
                'category_id': 1,
                'price': 99.99
            }
        )
        data = json.loads(create_response.data)
        product_id = data['product_id']
        
        # Обновляем товар
        response = client.put(f'/api/admin/products/{product_id}',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'name': 'Обновленный товар',
                'category_id': 1,
                'price': 149.99,
                'manufacturer': 'Новый производитель'
            }
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] == True
    
    def test_admin_delete_product(self, client, admin_token):
        """Тест: админ может удалить товар"""
        # Сначала создаем товар
        create_response = client.post('/api/admin/products',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'name': 'Товар для удаления',
                'category_id': 1,
                'price': 99.99
            }
        )
        data = json.loads(create_response.data)
        product_id = data['product_id']
        
        # Удаляем товар
        response = client.delete(f'/api/admin/products/{product_id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] == True