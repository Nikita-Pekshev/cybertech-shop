// ============================================
// register.js - Логика страницы регистрации
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    const errorDiv = document.getElementById('errorMessage');
    
    // Если пользователь уже авторизован - перенаправляем на главную
    if (isAuthenticated()) {
        window.location.href = 'index.html';
        return;
    }
    
    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value.trim();
        
        // Скрываем старую ошибку
        errorDiv.style.display = 'none';
        
        // Валидация
        if (!username || !email || !password) {
            showError('Заполните все поля');
            return;
        }
        
        if (password.length < 6) {
            showError('Пароль должен содержать минимум 6 символов');
            return;
        }
        
        try {
            const response = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, email, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert('✅ Регистрация успешна! Теперь войдите в систему.');
                window.location.href = 'login.html';
            } else {
                showError(data.error || 'Ошибка регистрации');
            }
        } catch (error) {
            console.error('Ошибка регистрации:', error);
            showError('Ошибка соединения с сервером');
        }
    });
    
    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
});