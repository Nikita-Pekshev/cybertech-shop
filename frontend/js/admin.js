// ============================================
// admin.js - Админ панель
// ============================================

let currentUser = null;
let products = [];
let categories = [];

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
            
            // Проверяем, что пользователь админ
            if (currentUser.role !== 'admin') {
                alert('⛔ Доступ запрещен. Требуются права администратора.');
                window.location.href = 'index.html';
                return;
            }
            
            showAuthenticatedUI();
            loadCategories();
            loadProducts();
        } else {
            localStorage.removeItem('token');
            window.location.href = 'login.html';
        }
    } catch (error) {
        console.error('❌ Ошибка проверки авторизации:', error);
        window.location.href = 'login.html';
    }
}

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
// ЗАГРУЗКА КАТЕГОРИЙ
// ============================================

async function loadCategories() {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const response = await fetch(`${API_URL}/admin/categories`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            categories = await response.json();
            populateCategorySelect();
        }
    } catch (error) {
        console.error('❌ Ошибка загрузки категорий:', error);
    }
}

function populateCategorySelect() {
    const select = document.getElementById('productCategory');
    select.innerHTML = '<option value="">Выберите категорию</option>';
    categories.forEach(cat => {
        select.innerHTML += `<option value="${cat.id}">${cat.name}</option>`;
    });
}

// ============================================
// ЗАГРУЗКА ТОВАРОВ
// ============================================

async function loadProducts() {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const response = await fetch(`${API_URL}/admin/products`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            products = await response.json();
            renderProducts(products);
        } else {
            showError('Не удалось загрузить товары');
        }
    } catch (error) {
        console.error('❌ Ошибка загрузки товаров:', error);
        showError('Ошибка соединения с сервером');
    }
}

function renderProducts(productsList) {
    const tbody = document.getElementById('productsTableBody');
    if (!tbody) return;
    
    if (productsList.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6">Товаров пока нет</td></tr>`;
        return;
    }
    
    tbody.innerHTML = productsList.map(product => `
        <tr>
            <td>${product.id}</td>
            <td>${product.name}</td>
            <td>${product.category_name}</td>
            <td>${product.price.toFixed(2)} ₽</td>
            <td>${product.manufacturer || '-'}</td>
            <td class="actions">
                <button class="edit-btn" onclick="editProduct(${product.id})">✏️</button>
                <button class="delete-btn" onclick="deleteProduct(${product.id})">🗑️</button>
            </td>
        </tr>
    `).join('');
}

// ============================================
// ДОБАВЛЕНИЕ ТОВАРА
// ============================================

function showAddForm() {
    document.getElementById('modalTitle').textContent = '➕ Добавить товар';
    document.getElementById('editProductId').value = '';
    document.getElementById('productForm').reset();
    document.getElementById('productModal').style.display = 'block';
    populateCategorySelect();
}

// ============================================
// РЕДАКТИРОВАНИЕ ТОВАРА
// ============================================

function editProduct(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    document.getElementById('modalTitle').textContent = '✏️ Редактировать товар';
    document.getElementById('editProductId').value = product.id;
    document.getElementById('productName').value = product.name;
    document.getElementById('productCategory').value = product.category_id;
    document.getElementById('productPrice').value = product.price;
    document.getElementById('productManufacturer').value = product.manufacturer || '';
    document.getElementById('productImage').value = product.image_url || '';
    document.getElementById('productDescription').value = product.description || '';
    
    document.getElementById('productModal').style.display = 'block';
}

// ============================================
// СОХРАНЕНИЕ ТОВАРА
// ============================================

document.getElementById('productForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const token = localStorage.getItem('token');
    if (!token) return;
    
    const productId = document.getElementById('editProductId').value;
    const name = document.getElementById('productName').value.trim();
    const category_id = parseInt(document.getElementById('productCategory').value);
    const price = parseFloat(document.getElementById('productPrice').value);
    const manufacturer = document.getElementById('productManufacturer').value.trim();
    const image_url = document.getElementById('productImage').value.trim();
    const description = document.getElementById('productDescription').value.trim();
    
    if (!name || !category_id || !price) {
        alert('Заполните все обязательные поля');
        return;
    }
    
    const data = { name, category_id, price, manufacturer, image_url, description };
    const url = productId ? `${API_URL}/admin/products/${productId}` : `${API_URL}/admin/products`;
    const method = productId ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('✅ ' + result.message);
            closeModal();
            loadProducts();
        } else {
            alert('❌ ' + (result.error || 'Ошибка сохранения'));
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('❌ Ошибка соединения с сервером');
    }
});

// ============================================
// УДАЛЕНИЕ ТОВАРА
// ============================================

async function deleteProduct(productId) {
    if (!confirm('Удалить этот товар?')) return;
    
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const response = await fetch(`${API_URL}/admin/products/${productId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('✅ ' + result.message);
            loadProducts();
        } else {
            alert('❌ ' + (result.error || 'Ошибка удаления'));
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('❌ Ошибка соединения с сервером');
    }
}

// ============================================
// МОДАЛЬНОЕ ОКНО
// ============================================

function closeModal() {
    document.getElementById('productModal').style.display = 'none';
}

// Закрытие по клику вне модального окна
window.onclick = function(event) {
    const modal = document.getElementById('productModal');
    if (event.target === modal) {
        closeModal();
    }
}

function showError(message) {
    const tbody = document.getElementById('productsTableBody');
    if (tbody) {
        tbody.innerHTML = `<tr><td colspan="6">❌ ${message}</td></tr>`;
    }
}

// ============================================
// ОБНОВЛЕНИЕ СЧЕТЧИКОВ
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
// ИНИЦИАЛИЗАЦИЯ
// ============================================

document.addEventListener('DOMContentLoaded', async function() {
    console.log('⚙️ Загрузка админ панели...');
    await initAuth();
    await updateCartCount();
    await updateFavoritesCount();
    console.log('✅ Админ панель загружена');
});