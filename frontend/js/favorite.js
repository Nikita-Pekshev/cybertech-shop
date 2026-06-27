// ============================================
// favorite.js - Страница избранного
// ============================================
let currentUser = null;
let favoritesItems = [];

// ============================================
// АВТОРИЗАЦИЯ
// ============================================

async function initAuth() {
    const token = localStorage.getItem('token');
    
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            showAuthenticatedUI();
            loadFavorites();
        } else {
            localStorage.removeItem('token');
            window.location.href = 'login.html';
        }
    } catch (error) {
        console.error('❌ Ошибка проверки авторизации:', error);
        window.location.href = 'login.html';
    }
}

// ============================================
// ИНТЕРФЕЙС
// ============================================

function showAuthenticatedUI() {
    const loginItem = document.querySelector('#login-item');
    if (loginItem) {
        loginItem.className = 'account-item';
        loginItem.innerHTML = `
            <a href="#" class="account-link">👤 ${currentUser.username}</a>
            <ul class="account-dropdown">
                <li><a href="#" id="logoutBtn">🚪 Выйти</a></li>
            </ul>
        `;
        
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', function(e) {
                e.preventDefault();
                logout();
            });
        }
    }
}

async function logout() {
    const token = localStorage.getItem('token');
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
    localStorage.removeItem('token');
    window.location.href = 'index.html';
}

// ============================================
// ЗАГРУЗКА ИЗБРАННОГО
// ============================================

async function loadFavorites() {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const response = await fetch(`${API_URL}/favorites`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            favoritesItems = await response.json();
            renderFavorites(favoritesItems);
            updateFavoritesCount();
        } else {
            showError('Не удалось загрузить избранное');
        }
    } catch (error) {
        console.error('❌ Ошибка загрузки избранного:', error);
        showError('Ошибка соединения с сервером');
    }
}

function renderFavorites(items) {
    const container = document.getElementById('favoritesContainer');
    if (!container) return;
    
    if (items.length === 0) {
        container.innerHTML = `
            <div class="empty-message">
                <p>😕 У вас пока нет избранных товаров</p>
                <a href="index.html" class="retry-btn" style="display: inline-block; text-decoration: none; margin-top: 15px;">
                     Перейти на главную страницу
                </a>
            </div>
        `;
        return;
    }
    
    container.innerHTML = items.map(item => `
        <div class="product-card" data-product-id="${item.product_id}">
            <div class="product-image">
                <img src="${item.image_url}" alt="${item.name}" 
                     onerror="this.onerror=null; this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22300%22%3E%3Crect fill=%22%23f0f0f0%22 width=%22300%22 height=%22300%22/%3E%3Ctext x=%2250%%22 y=%2250%%22 font-size=%2220%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22%3ENo Image%3C/text%3E%3C/svg%3E'">
            </div>
            <div class="product-info">
                <h3 class="product-title">${item.name}</h3>
                <p class="product-category">${item.category}</p>
                <p class="product-manufacturer">${item.manufacturer}</p>
                <div class="product-price">${item.price.toFixed(2)} ₽</div>
                <div class="product-actions">
                    <button class="buy-btn" onclick="addToCart(${item.product_id})">
                        В корзину
                    </button>
                    <button class="favorite-btn active" onclick="removeFavorite(event, ${item.product_id})">
                        ♥
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// ============================================
// УДАЛЕНИЕ ИЗ ИЗБРАННОГО
// ============================================

async function removeFavorite(event, productId) {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    const btn = event.target;
    btn.textContent = '⏳';
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/favorites/remove`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ product_id: productId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const card = btn.closest('.product-card');
            if (card) {
                card.style.transition = 'all 0.3s ease';
                card.style.transform = 'scale(0.8)';
                card.style.opacity = '0';
                setTimeout(() => {
                    card.remove();
                    // Проверяем, остались ли товары
                    const remaining = document.querySelectorAll('.product-card');
                    if (remaining.length === 0) {
                        const container = document.getElementById('favoritesContainer');
                        if (container) {
                            container.innerHTML = `
                                <div class="empty-message">
                                    <p>😕 У вас пока нет избранных товаров</p>
                                    <a href="index.html" class="retry-btn" style="display: inline-block; text-decoration: none; margin-top: 15px;">
                                        Перейти на главную страницу
                                    </a>
                                </div>
                            `;
                        }
                    }
                }, 300);
            }
            updateFavoritesCount();
        } else {
            console.error('Ошибка удаления из избранного:', data.error);
            btn.textContent = '♥';
            btn.disabled = false;
        }
    } catch (error) {
        console.error('Ошибка:', error);
        btn.textContent = '♥';
        btn.disabled = false;
    }
}

// ============================================
// ДОБАВЛЕНИЕ В КОРЗИНУ (с обновлением счетчика)
// ============================================

async function addToCart(productId) {
    const token = localStorage.getItem('token');
    
    if (!token) {
        alert('Пожалуйста, войдите в систему');
        window.location.href = 'login.html';
        return;
    }
    
    const btn = document.querySelector(`.product-card[data-product-id="${productId}"] .buy-btn`);
    
    if (btn) {
        btn.textContent = '⏳...';
        btn.disabled = true;
    }
    
    try {
        const response = await fetch(`${API_URL}/cart/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ product_id: productId, quantity: 1 })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (btn) {
                btn.textContent = 'В корзине';
                btn.style.background = '#95a5a6';
                btn.style.cursor = 'default';
                btn.style.transform = 'none';
                btn.style.boxShadow = 'none';
                btn.disabled = true;
            }
            await updateCartCount();
        } else {
            if (btn) {
                btn.textContent = 'В корзину';
                btn.disabled = false;
                btn.style.background = '';
                btn.style.cursor = '';
                btn.style.transform = '';
                btn.style.boxShadow = '';
            }
            console.error('Ошибка добавления:', data.error);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        if (btn) {
            btn.textContent = 'В корзину';
            btn.disabled = false;
            btn.style.background = '';
            btn.style.cursor = '';
            btn.style.transform = '';
            btn.style.boxShadow = '';
        }
    }
}

// ============================================
// ОБНОВЛЕНИЕ СЧЕТЧИКА КОРЗИНЫ
// ============================================

async function updateCartCount() {
    const token = localStorage.getItem('token');
    if (!token) {
        const cartLink = document.getElementById('cartLink');
        if (cartLink) {
            cartLink.textContent = 'Корзина (0)';
        }
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/cart`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const cartLink = document.getElementById('cartLink');
            if (cartLink) {
                const total = data.total_quantity || 0;
                cartLink.textContent = `Корзина (${total})`;
            }
        }
    } catch (error) {
        console.error('Ошибка обновления корзины:', error);
    }
}

// ============================================
// ОБНОВЛЕНИЕ СЧЕТЧИКА ИЗБРАННОГО
// ============================================

async function updateFavoritesCount() {
    const token = localStorage.getItem('token');
    if (!token) {
        const favLink = document.getElementById('favoritesLink');
        if (favLink) {
            favLink.textContent = 'Избранное';
        }
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/favorites`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const favorites = await response.json();
            const favLink = document.getElementById('favoritesLink');
            if (favLink) {
                if (favorites.length > 0) {
                    favLink.innerHTML = `Избранное <span class="favorites-badge">${favorites.length}</span>`;
                } else {
                    favLink.textContent = 'Избранное';
                }
            }
        }
    } catch (error) {
        console.error('Ошибка обновления избранного:', error);
    }
}

// ============================================
// СООБЩЕНИЯ ОБ ОШИБКАХ
// ============================================

function showError(message) {
    const container = document.getElementById('favoritesContainer');
    if (container) {
        container.innerHTML = `
            <div class="error-message">
                <p>❌ ${message}</p>
                <button onclick="loadFavorites()" class="retry-btn">🔄 Повторить</button>
            </div>
        `;
    }
}

// ============================================
// ИНИЦИАЛИЗАЦИЯ
// ============================================

document.addEventListener('DOMContentLoaded', async function() {
    console.log('Загрузка страницы избранного...');
    await initAuth();
    await updateCartCount();  
    console.log('✅ Страница избранного загружена');
});