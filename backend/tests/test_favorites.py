import json
import pytest

class TestFavorites:
    """Тесты избранного"""
    
    def test_add_to_favorites_requires_auth(self, client):
        """Тест: добавление в избранное требует авторизации"""
        response = client.post('/api/favorites/add', json={
            'product_id': 1
        })
        assert response.status_code == 401
    
    def test_add_to_favorites_success(self, client, auth_token):
        """Тест: успешное добавление в избранное"""
        response = client.post('/api/favorites/add',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'product_id': 1}
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] == True
    
    def test_add_to_favorites_duplicate(self, client, auth_token):
        """Тест: добавление уже существующего в избранном"""
        # Добавляем первый раз
        client.post('/api/favorites/add',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'product_id': 1}
        )
        
        # Добавляем второй раз
        response = client.post('/api/favorites/add',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'product_id': 1}
        )
        data = json.loads(response.data)
        assert response.status_code == 400
        assert 'уже в избранном' in data['error']
    
    def test_get_favorites_requires_auth(self, client):
        """Тест: получение избранного требует авторизации"""
        response = client.get('/api/favorites')
        assert response.status_code == 401
    
    def test_get_favorites_success(self, client, auth_token):
        """Тест: успешное получение избранного"""
        # Добавляем товар в избранное
        client.post('/api/favorites/add',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'product_id': 1}
        )
        
        # Получаем избранное
        response = client.get('/api/favorites',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_remove_from_favorites(self, client, auth_token):
        """Тест: удаление из избранного"""
        # Добавляем в избранное
        client.post('/api/favorites/add',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'product_id': 1}
        )
        
        # Удаляем из избранного
        response = client.delete('/api/favorites/remove',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'product_id': 1}
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] == True
    
    def test_check_favorite_status(self, client, auth_token):
        """Тест: проверка статуса избранного"""
        # Добавляем в избранное
        client.post('/api/favorites/add',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'product_id': 1}
        )
        
        # Проверяем статус
        response = client.get('/api/favorites/check/1',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['is_favorite'] == True
        
        # Проверяем статус для товара, которого нет в избранном
        response = client.get('/api/favorites/check/999',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['is_favorite'] == False