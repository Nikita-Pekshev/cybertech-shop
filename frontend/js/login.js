// ============================================
// login.js - Логика страницы входа
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const errorDiv = document.getElementById('errorMessage');
    
    // Если пользователь уже авторизован - перенаправляем на главную
    if (isAuthenticated()) {
        window.location.href = 'index.html';
        return;
    }
    
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value.trim();
        
        // Скрываем старую ошибку
        errorDiv.style.display = 'none';
        
        // Простая валидация
        if (!email || !password) {
            showError('Заполните все поля');
            return;
        }
        
        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Сохраняем токен
                setToken(data.token);
                
                // Перенаправляем на главную
                window.location.href = 'index.html';
            } else {
                showError(data.error || 'Неверный email или пароль');
            }
        } catch (error) {
            console.error('Ошибка входа:', error);
            showError('Ошибка соединения с сервером');
        }
    });
    
    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
});