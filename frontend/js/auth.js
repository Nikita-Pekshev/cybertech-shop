// ============================================
// auth.js - Общие функции авторизации
// ============================================

const API_URL = 'http://localhost:5000/api';

// Получить токен из localStorage
function getToken() {
    return localStorage.getItem('token');
}

// Сохранить токен
function setToken(token) {
    localStorage.setItem('token', token);
}

// Удалить токен (выход)
function removeToken() {
    localStorage.removeItem('token');
}

// Проверить, авторизован ли пользователь
function isAuthenticated() {
    return !!getToken();
}

// Получить информацию о текущем пользователе
async function getCurrentUser() {
    const token = getToken();
    if (!token) return null;
    
    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            return data.user;
        } else {
            removeToken();
            return null;
        }
    } catch (error) {
        console.error('Ошибка получения пользователя:', error);
        return null;
    }
}

// Выход из системы
async function logout() {
    const token = getToken();
    
    if (token) {
        try {
            await fetch(`${API_URL}/auth/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        } catch (error) {
            console.error('Ошибка при выходе:', error);
        }
    }
    
    removeToken();
    window.location.href = 'index.html';
}

// Настройка заголовков с токеном для fetch
function getAuthHeaders() {
    const token = getToken();
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}