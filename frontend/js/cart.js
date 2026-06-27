// ============================================
// cart.js - Страница корзины с вкладками
// ============================================

let currentUser = null;
let cartItems = [];
let orders = [];
let currentTab = 'cart'; // 'cart' или 'orders'

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
            loadCart();
            loadOrders();
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
                <li><a href="#" id="logoutBtn">Выйти</a></li>
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
// ВКЛАДКИ
// ============================================

function switchTab(tab) {
    currentTab = tab;
    
    // Обновляем активную вкладку
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`.tab-btn[data-tab="${tab}"]`).classList.add('active');
    
    // Показываем соответствующий контент
    if (tab === 'cart') {
        document.getElementById('cartContent').style.display = 'block';
        document.getElementById('ordersContent').style.display = 'none';
        loadCart();
    } else {
        document.getElementById('cartContent').style.display = 'none';
        document.getElementById('ordersContent').style.display = 'block';
        loadOrders();
    }
}

// ============================================
// ЗАГРУЗКА КОРЗИНЫ
// ============================================

async function loadCart() {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const response = await fetch(`${API_URL}/cart`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            cartItems = data.items;
            renderCart(data);
            updateCartCount();
        } else {
            showError('Не удалось загрузить корзину');
        }
    } catch (error) {
        console.error('❌ Ошибка загрузки корзины:', error);
        showError('Ошибка соединения с сервером');
    }
}

function renderCart(data) {
    const container = document.getElementById('cartContent');
    if (!container) return;
    
    const items = data.items;
    
    if (items.length === 0) {
        container.innerHTML = `
            <div class="empty-cart">
                <div class="empty-icon">🛒</div>
                <h2>Корзина пуста</h2>
                <p>Похоже, вы еще не добавили товары в корзину</p>
                <a href="index.html" class="retry-btn">Перейти на главную страницу</a>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="cart-items">
            ${items.map(item => `
                <div class="cart-item" data-cart-id="${item.cart_id}">
                    <div class="cart-item-image">
                        <img src="${item.image_url}" alt="${item.name}" 
                             onerror="this.onerror=null; this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22%3E%3Crect fill=%22%23f0f0f0%22 width=%22100%22 height=%22100%22/%3E%3Ctext x=%2250%%22 y=%2250%%22 font-size=%2220%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22%3ENo Image%3C/text%3E%3C/svg%3E'">
                    </div>
                    <div class="cart-item-info">
                        <h3 class="cart-item-title">${item.name}</h3>
                        <p class="cart-item-category">${item.category}</p>
                        <p class="cart-item-manufacturer">${item.manufacturer}</p>
                        <div class="cart-item-price">${item.price.toFixed(2)} ₽</div>
                    </div>
                    <div class="cart-item-actions">
                        <div class="quantity-control">
                            <button class="qty-btn" onclick="updateQuantity(${item.cart_id}, ${item.quantity - 1})">−</button>
                            <span class="qty-value">${item.quantity}</span>
                            <button class="qty-btn" onclick="updateQuantity(${item.cart_id}, ${item.quantity + 1})">+</button>
                        </div>
                        <div class="cart-item-total">${item.total.toFixed(2)} ₽</div>
                        <button class="remove-btn" onclick="removeItem(${item.cart_id})">🗑️</button>
                    </div>
                </div>
            `).join('')}
        </div>
        <div class="cart-summary">
            <div class="cart-summary-info">
                <span>Товаров: <strong>${data.total_items}</strong></span>
                <span>Всего позиций: <strong>${data.total_quantity}</strong></span>
                <span class="total-price">Итого: <strong>${data.total_price.toFixed(2)} ₽</strong></span>
            </div>
            <div class="cart-summary-actions">
                <button class="clear-cart-btn" onclick="clearCart()"> Очистить корзину</button>
                <button class="checkout-btn" onclick="showCheckoutForm()"> Оформить заказ</button>
            </div>
        </div>
    `;
}

// ============================================
// ЗАГРУЗКА ЗАКАЗОВ
// ============================================

async function loadOrders() {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const response = await fetch(`${API_URL}/orders`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            orders = await response.json();
            renderOrders(orders);
        } else {
            showError('Не удалось загрузить заказы');
        }
    } catch (error) {
        console.error('❌ Ошибка загрузки заказов:', error);
        showError('Ошибка соединения с сервером');
    }
}

function renderOrders(ordersList) {
    const container = document.getElementById('ordersContent');
    if (!container) return;
    
    if (ordersList.length === 0) {
        container.innerHTML = `
            <div class="empty-orders">
                <div class="empty-icon">📦</div>
                <h2>У вас пока нет заказов</h2>
                <p>Перейдите на главнуб страницу и сделайте свой первый заказ!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = ordersList.map(order => `
        <div class="order-card" data-order-id="${order.id}">
            <div class="order-header">
                <div class="order-info">
                    <span class="order-number"> ${order.order_number}</span>
                    <span class="order-date"> ${formatDate(order.order_date)}</span>
                </div>
                <div class="order-status ${order.status}">
                    ${order.status === 'paid' ? '✅ Оплачен' : '⏳ Ожидает оплаты'}
                </div>
            </div>
            
            <div class="order-items">
                ${order.items.map(item => `
                    <div class="order-item">
                        <img src="${item.image_url}" alt="${item.name}" 
                             onerror="this.src='https://via.placeholder.com/60x60?text=No+Image'">
                        <div class="order-item-info">
                            <span class="order-item-name">${item.name}</span>
                            <span class="order-item-qty">${item.quantity} шт.</span>
                            <span class="order-item-price">${item.price.toFixed(2)} ₽</span>
                        </div>
                    </div>
                `).join('')}
            </div>
            
            <div class="order-footer">
                <div class="order-address">
                    📍 ${order.delivery_address}
                </div>
                <div class="order-total">
                    Итого: <strong>${order.total_price.toFixed(2)} ₽</strong>
                </div>
                ${order.status !== 'paid' ? `
                    <button class="pay-btn" onclick="payOrder(${order.id})">
                        💳 Оплатить
                    </button>
                ` : `
                    <span class="paid-badge">✅ Оплачено</span>
                `}
            </div>
        </div>
    `).join('');
}

// ============================================
// ОПЛАТА ЗАКАЗА
// ============================================

async function payOrder(orderId) {
    if (!confirm('Оплатить этот заказ?')) return;
    
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const response = await fetch(`${API_URL}/orders/${orderId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ status: 'paid' })
        });
        
        if (response.ok) {
            alert('✅ Заказ оплачен! Спасибо за покупку! 🎉');
            loadOrders();
        } else {
            const data = await response.json();
            alert('❌ ' + (data.error || 'Ошибка оплаты'));
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('❌ Ошибка соединения с сервером');
    }
}

// ============================================
// ФОРМА ОФОРМЛЕНИЯ ЗАКАЗА
// ============================================

function showCheckoutForm() {
    if (cartItems.length === 0) {
        alert('Корзина пуста');
        return;
    }
    
    const container = document.getElementById('cartContent');
    if (!container) return;
    
    const total = cartItems.reduce((sum, item) => sum + item.total, 0);
    
    container.innerHTML = `
        <div class="checkout-form">
            <h2>Оформление заказа</h2>
            <p class="checkout-total">Итого: <strong>${total.toFixed(2)} ₽</strong></p>
            <form id="checkoutForm">
                <div class="form-group">
                    <label for="deliveryAddress">Адрес доставки *</label>
                    <input type="text" id="deliveryAddress" placeholder="Введите адрес доставки" required>
                </div>
                <div class="form-group">
                    <label for="orderComment">Комментарий к заказу</label>
                    <textarea id="orderComment" placeholder="Дополнительные пожелания..."></textarea>
                </div>
                <div class="checkout-actions">
                    <button type="button" class="back-btn" onclick="switchTab('cart')">← Назад</button>
                    <button type="submit" class="submit-order-btn">✅ Подтвердить заказ</button>
                </div>
            </form>
        </div>
    `;
    
    document.getElementById('checkoutForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        await createOrder();
    });
}

async function createOrder() {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    const address = document.getElementById('deliveryAddress').value.trim();
    const comment = document.getElementById('orderComment').value.trim();
    
    if (!address) {
        alert('Пожалуйста, введите адрес доставки');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/orders/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                delivery_address: address,
                comment: comment
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(`✅ Заказ оформлен!\nНомер заказа: ${data.order_number}\nСумма: ${data.total_price.toFixed(2)} ₽`);
            switchTab('orders');
            loadOrders();
            updateCartCount();
        } else {
            alert('❌ ' + (data.error || 'Ошибка оформления заказа'));
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('❌ Ошибка соединения с сервером');
    }
}

// ============================================
// УПРАВЛЕНИЕ КОРЗИНОЙ
// ============================================

async function updateQuantity(cartId, newQuantity) {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    if (newQuantity < 0) return;
    
    try {
        const response = await fetch(`${API_URL}/cart/update`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ 
                cart_id: cartId, 
                quantity: newQuantity 
            })
        });
        
        if (response.ok) {
            loadCart();
            updateCartCount();
        } else {
            const data = await response.json();
            console.error('Ошибка обновления:', data.error);
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

async function removeItem(cartId) {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    const cartItem = document.querySelector(`.cart-item[data-cart-id="${cartId}"]`);
    
    if (cartItem) {
        cartItem.style.transition = 'all 0.3s ease';
        cartItem.style.transform = 'translateX(100%)';
        cartItem.style.opacity = '0';
    }
    
    try {
        const response = await fetch(`${API_URL}/cart/remove/${cartId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            setTimeout(() => {
                loadCart();
                updateCartCount();
            }, 300);
        } else {
            const data = await response.json();
            console.error('Ошибка удаления:', data.error);
            if (cartItem) {
                cartItem.style.transform = 'translateX(0)';
                cartItem.style.opacity = '1';
            }
        }
    } catch (error) {
        console.error('Ошибка:', error);
        if (cartItem) {
            cartItem.style.transform = 'translateX(0)';
            cartItem.style.opacity = '1';
        }
    }
}

async function clearCart() {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    const cartItems = document.querySelectorAll('.cart-item');
    cartItems.forEach(item => {
        item.style.transition = 'all 0.3s ease';
        item.style.transform = 'scale(0.8)';
        item.style.opacity = '0';
    });
    
    try {
        const response = await fetch(`${API_URL}/cart/clear`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            setTimeout(() => {
                loadCart();
                updateCartCount();
            }, 300);
        } else {
            const data = await response.json();
            console.error('Ошибка очистки:', data.error);
            cartItems.forEach(item => {
                item.style.transform = 'scale(1)';
                item.style.opacity = '1';
            });
        }
    } catch (error) {
        console.error('Ошибка:', error);
        cartItems.forEach(item => {
            item.style.transform = 'scale(1)';
            item.style.opacity = '1';
        });
    }
}

// ============================================
// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
// ============================================

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showError(message) {
    const container = document.getElementById('cartContent');
    if (container) {
        container.innerHTML = `
            <div class="error-message">
                <p>❌ ${message}</p>
                <button onclick="loadCart()" class="retry-btn">🔄 Повторить</button>
            </div>
        `;
    }
}

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
// ИНИЦИАЛИЗАЦИЯ
// ============================================

document.addEventListener('DOMContentLoaded', async function() {
    console.log('🛒 Загрузка страницы корзины...');
    await initAuth();
    await updateCartCount();
    // По умолчанию показываем корзину
    switchTab('cart');
    console.log('✅ Страница корзины загружена');
});