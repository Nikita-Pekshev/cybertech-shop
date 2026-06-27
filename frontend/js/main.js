// ============================================
// 1. ДАННЫЕ БРЕНДОВ
// ============================================

const brands = [
    { name: 'Asus', logo: 'img/asus-svgrepo-com.svg' },
    { name: 'Dell', logo: 'img/dell-svgrepo-com.svg' },
    { name: 'Honor', logo: 'img/Honor_(brand)-Logo.wine.svg' },
    { name: 'HP', logo: 'img/hp-svgrepo-com.svg' },
    { name: 'Lenovo', logo: 'img/apple-black-logo-svgrepo-com.svg' },
    { name: 'LG', logo: 'img/lg-svgrepo-com.svg' },
    { name: 'Nokia', logo: 'img/nokia-svgrepo-com.svg' },
    { name: 'Samsung', logo: 'img/samsung-svgrepo-com.svg' },
    { name: 'Toshiba', logo: 'img/toshiba-svgrepo-com.svg' },
    { name: 'Vivo', logo: 'img/vivo-2-logo-svgrepo-com.svg' },
    { name: 'Xiaomi', logo: 'img/xiaomi-svgrepo-com.svg' }
];

// ============================================
// 2. ПЕРЕМЕННЫЕ СОСТОЯНИЯ
// ============================================

let currentUser = null;
let currentCategory = 'all'; // 'all' или ID категории

// ============================================
// 2.1. НАЗВАНИЯ КАТЕГОРИЙ
// ============================================

const categoryNames = {
    1: 'Бытовая техника',
    2: 'Смартфоны',
    3: 'ПК, ноутбуки, периферия',
    4: 'Сетевое оборудование'
};

// ============================================
// 3. АВТОРИЗАЦИЯ
// ============================================

async function initAuth() {
    const token = localStorage.getItem('token');
    
    if (!token) {
        showUnauthenticatedUI();
        return false;
    }
    
    try {
        console.log(' Проверка авторизации...');
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            showAuthenticatedUI();
            console.log(' Пользователь авторизован:', currentUser.username);
            return true;
        } else {
            localStorage.removeItem('token');
            showUnauthenticatedUI();
            return false;
        }
    } catch (error) {
        console.error(' Ошибка проверки авторизации:', error);
        showUnauthenticatedUI();
        return false;
    }
}

// ============================================
// 4. ИНТЕРФЕЙС
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

function showUnauthenticatedUI() {
    const loginItem = document.querySelector('#login-item');
    if (loginItem) {
        loginItem.className = '';
        loginItem.innerHTML = '<a href="login.html">Войти</a>';
    }
}

function showAuthenticatedUI() {
    const loginItem = document.querySelector('#login-item');
    if (loginItem) {
        loginItem.className = 'account-item';
        loginItem.innerHTML = `
            <a href="#" class="account-link">👤 ${currentUser.username}</a>
            <ul class="account-dropdown">
                ${currentUser.role === 'admin' ? '<li><a href="admin.html">⚙️ Админ панель</a></li>' : ''}
                <li><a href="#" id="logoutBtn"> Выйти</a></li>
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

// ============================================
// 5. ВЫХОД
// ============================================

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
    currentUser = null;
    showUnauthenticatedUI();
    window.location.reload();
}

// ============================================
// 6. ТОВАРЫ
// ============================================

async function loadProducts(categoryId = 'all') {
    try {
        console.log(' Загрузка товаров...', categoryId);
        
        let url = `${API_URL}/products`;
        if (categoryId !== 'all') {
            url = `${API_URL}/products/category/${categoryId}`;
        }
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Ошибка загрузки товаров');
        }
        const products = await response.json();
        renderProducts(products);
        
        // Обновляем заголовок категории
        updateCategoryTitle(categoryId);
        
    } catch (error) {
        console.error(' Ошибка загрузки товаров:', error);
        const container = document.querySelector('.products');
        if (container) {
            container.innerHTML = `
                <div class="error-message">
                    <p> Не удалось загрузить товары. Убедитесь, что сервер запущен!</p>
                    <button onclick="loadProducts('${categoryId}')" class="retry-btn">
                         Повторить
                    </button>
                </div>
            `;
        }
    }
}

function renderProducts(products) {
    const container = document.querySelector('.products');
    if (!container) return;
    
    if (products.length === 0) {
        container.innerHTML = `
            <div class="empty-message">
                <p> В этой категории пока нет товаров</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = products.map(product => `
        <div class="product-card" data-product-id="${product.id}">
            <div class="product-image">
                <img src="${product.image_url}" alt="${product.name}" 
                     onerror="this.onerror=null; this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22300%22%3E%3Crect fill=%22%23f0f0f0%22 width=%22300%22 height=%22300%22/%3E%3Ctext x=%2250%%22 y=%2250%%22 font-size=%2220%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22%3ENo Image%3C/text%3E%3C/svg%3E'">
            </div>
            <div class="product-info">
                <h3 class="product-title">${product.name}</h3>
                <p class="product-category">${product.category}</p>
                <p class="product-manufacturer">${product.manufacturer}</p>
                <div class="product-price">${product.price.toFixed(2)} ₽</div>
                <div class="product-actions">
                    <button class="buy-btn" onclick="addToCart(${product.id})">
                         В корзину
                    </button>
                    <button class="favorite-btn" onclick="toggleFavorite(event, ${product.id})">
                        ♡
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    setTimeout(checkFavoritesStatus, 200);
    setTimeout(checkCartStatus, 300); 
}

function updateCategoryTitle(categoryId) {
    const titleElement = document.getElementById('categoryTitle');
    if (!titleElement) return;
    
    if (categoryId === 'all') {
        titleElement.textContent = 'Все товары';
    } else {
        titleElement.textContent = categoryNames[categoryId] || 'Товары';
    }
}

// ============================================
// 7. ФИЛЬТР ПО КАТЕГОРИИ
// ============================================

function setupCategoryFilter() {
    const categoryLinks = document.querySelectorAll('.dropout li a[data-category]');
    
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const categoryId = this.dataset.category;
            currentCategory = categoryId;
            
            // Загружаем товары выбранной категории
            loadProducts(categoryId);
            
            // Убираем активный класс у всех пунктов
            document.querySelectorAll('.dropout li a').forEach(item => {
                item.classList.remove('active');
            });
            // Добавляем активный класс выбранному
            this.classList.add('active');
            
            // Закрываем выпадающее меню
            const catalog = document.querySelector('.catalog');
            if (catalog) {
                catalog.classList.remove('active');
            }
        });
    });
}
// ============================================
// 9. ДОБАВЛЕНИЕ В КОРЗИНУ
// ============================================

async function addToCart(productId) {
    const token = localStorage.getItem('token');
    
    if (!token) {
        alert('Пожалуйста, войдите в систему, чтобы добавить товар в корзину');
        window.location.href = 'login.html';
        return;
    }
    
    // Находим кнопку
    const btn = document.querySelector(`.product-card[data-product-id="${productId}"] .buy-btn`);
    const originalText = btn ? btn.textContent : '';
    
    // Показываем состояние загрузки
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
            // ✅ Меняем кнопку на "В корзине"
            if (btn) {
                btn.textContent = 'В корзине';
                btn.style.background = '#95a5a6';
                btn.style.cursor = 'default';
                btn.style.transform = 'none';
                btn.style.boxShadow = 'none';
                btn.disabled = true;
            }
            
            // Обновляем счетчик корзины
            updateCartCount();
            
        } else {
            // Ошибка — возвращаем кнопку
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
// 9.1. ОБНОВЛЕНИЕ СЧЕТЧИКА КОРЗИНЫ
// ============================================

async function updateCartCount() {
    const token = localStorage.getItem('token');
    if (!token) {
        const cartLink = document.getElementById('cartLink');
        if (cartLink) {
            cartLink.textContent = 'Корзина';
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
// 9.2. ПРОВЕРКА СТАТУСА КОРЗИНЫ ДЛЯ КНОПОК
// ============================================

async function checkCartStatus() {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    const cartButtons = document.querySelectorAll('.buy-btn');
    
    try {
        const response = await fetch(`${API_URL}/cart`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const cartItems = data.items || [];
            const cartProductIds = new Set(cartItems.map(item => item.product_id));
            
            cartButtons.forEach(btn => {
                const productCard = btn.closest('.product-card');
                if (!productCard) return;
                
                const productId = parseInt(productCard.dataset.productId);
                if (cartProductIds.has(productId)) {
                    btn.textContent = 'В корзине';
                    btn.style.background = '#95a5a6';
                    btn.style.cursor = 'default';
                    btn.style.transform = 'none';
                    btn.style.boxShadow = 'none';
                    btn.disabled = true;
                } else {
                    btn.textContent = 'В корзину';
                    btn.style.background = '';
                    btn.style.cursor = '';
                    btn.style.transform = '';
                    btn.style.boxShadow = '';
                    btn.disabled = false;
                }
            });
        }
    } catch (error) {
        console.error('Ошибка проверки корзины:', error);
    }
}
// ============================================
// 10. ИЗБРАННОЕ (обновленная версия с счетчиком)
// ============================================

async function toggleFavorite(event, productId) {
    const token = localStorage.getItem('token');
    
    if (!token) {
        alert('Пожалуйста, войдите в систему');
        window.location.href = 'login.html';
        return;
    }
    
    const btn = event.target;
    const isCurrentlyFavorite = btn.textContent === '♥' && btn.style.color === '#ff4081';
    
    // Показываем состояние загрузки
    btn.textContent = '⏳';
    btn.disabled = true;
    
    try {
        let response;
        let data;
        
        if (isCurrentlyFavorite) {
            // Удаляем из избранного
            response = await fetch(`${API_URL}/favorites/remove`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ product_id: productId })
            });
            data = await response.json();
            
            if (response.ok) {
                btn.textContent = '♡';
                btn.style.color = '';
                btn.classList.remove('active');
                updateFavoritesCount();
            } else {
                console.error('Ошибка удаления из избранного:', data.error);
                btn.textContent = '♥';
                btn.style.color = '#ff4081';
                btn.classList.add('active');
                btn.disabled = false;
            }
        } else {
            // Добавляем в избранное
            response = await fetch(`${API_URL}/favorites/add`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ product_id: productId })
            });
            data = await response.json();
            
            if (response.ok) {
                btn.textContent = '♥';
                btn.style.color = '#ff4081';
                btn.classList.add('active');
                updateFavoritesCount();
            } else {
                console.error('Ошибка добавления в избранное:', data.error);
                btn.textContent = '♡';
                btn.style.color = '';
                btn.classList.remove('active');
                btn.disabled = false;
            }
        }
    } catch (error) {
        console.error('Ошибка:', error);
        // Возвращаем исходное состояние
        if (isCurrentlyFavorite) {
            btn.textContent = '♥';
            btn.style.color = '#ff4081';
            btn.classList.add('active');
        } else {
            btn.textContent = '♡';
            btn.style.color = '';
            btn.classList.remove('active');
        }
        btn.disabled = false;
    }
}

// ============================================
// 10.1. ОБНОВЛЕНИЕ СЧЕТЧИКА ИЗБРАННОГО
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
// 10.2. ПРОВЕРКА СТАТУСА ИЗБРАННОГО ДЛЯ КНОПОК
// ============================================

async function checkFavoritesStatus() {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    
    for (const btn of favoriteButtons) {
        const productCard = btn.closest('.product-card');
        if (!productCard) continue;
        
        const productId = productCard.dataset.productId;
        if (productId) {
            try {
                const response = await fetch(`${API_URL}/favorites/check/${productId}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                if (response.ok) {
                    const data = await response.json();
                    if (data.is_favorite) {
                        btn.textContent = '♥';
                        btn.style.color = '#ff4081';
                        btn.classList.add('active');
                    } else {
                        btn.textContent = '♡';
                        btn.style.color = '';
                        btn.classList.remove('active');
                    }
                }
            } catch (error) {
                console.error('Ошибка проверки статуса:', error);
            }
        }
    }
}
// ============================================
// 11. ПОИСК
// ============================================

function setupSearch() {
    const searchInput = document.querySelector('.search-input');
    const searchButton = document.querySelector('.search-button');
    
    if (!searchInput || !searchButton) return;
    
    async function performSearch() {
        const query = searchInput.value.trim();
        console.log(`🔍 Поиск: "${query}"`);
        
        if (query === '') {
            loadProducts(currentCategory);
            return;
        }
        
        try {
            const container = document.querySelector('.products');
            if (container) {
                container.innerHTML = `<p class="loading-message">⏳ Поиск...</p>`;
            }
            
            const response = await fetch(`${API_URL}/products/search?q=${encodeURIComponent(query)}`);
            if (!response.ok) {
                throw new Error('Ошибка поиска');
            }
            const products = await response.json();
            renderProducts(products);
            
            // Обновляем заголовок
            const titleElement = document.getElementById('categoryTitle');
            if (titleElement) {
                if (products.length === 0) {
                    titleElement.textContent = `Результаты поиска: "${query}" (ничего не найдено)`;
                } else {
                    titleElement.textContent = `Результаты поиска: "${query}" (${products.length} товаров)`;
                }
            }
            
        } catch (error) {
            console.error(' Ошибка поиска:', error);
            const container = document.querySelector('.products');
            if (container) {
                container.innerHTML = `
                    <div class="error-message">
                        <p> Ошибка поиска. Попробуйте позже.</p>
                        <button onclick="loadProducts('${currentCategory}')" class="retry-btn">
                             Показать все товары
                        </button>
                    </div>
                `;
            }
        }
    }
    
    // Поиск по кнопке
    searchButton.addEventListener('click', performSearch);
    
    // Поиск по Enter
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch();
        }
    });
    
    // Очистка поиска по Escape
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            searchInput.value = '';
            loadProducts(currentCategory);
        }
    });
}

// ============================================
// 12. КАРУСЕЛЬ БРЕНДОВ
// ============================================

let carouselPosition = 0;
let speed = 0.5;
let isAnimating = true;
let animationId = null;
const itemWidth = 170;
let isManualScroll = false;
let manualTimeout = null;

function renderBrands() {
    const track = document.querySelector('.carousel-track');
    if (!track) return;
    
    const extendedBrands = [...brands, ...brands, ...brands];
    
    track.innerHTML = '';
    extendedBrands.forEach((brand) => {
        const div = document.createElement('div');
        div.className = 'brand-item';
        div.innerHTML = `
            <img src="${brand.logo}" alt="${brand.name}" class="brand-logo-img" 
                 onerror="this.style.display='none'">
        `;
        track.appendChild(div);
    });
}

function animate() {
    if (!isAnimating) return;
    
    const track = document.querySelector('.carousel-track');
    if (!track) return;
    
    if (!isManualScroll) {
        carouselPosition -= speed;
    }
    
    if (carouselPosition <= -(brands.length * itemWidth)) {
        carouselPosition = 0;
    }
    if (carouselPosition > 0) {
        carouselPosition = -(brands.length * itemWidth);
    }
    
    track.style.transform = `translateX(${carouselPosition}px)`;
    animationId = requestAnimationFrame(animate);
}

function startAnimation() {
    isAnimating = true;
    if (animationId) {
        cancelAnimationFrame(animationId);
    }
    animate();
}

function stopAnimation() {
    isAnimating = false;
    if (animationId) {
        cancelAnimationFrame(animationId);
        animationId = null;
    }
}

function manualSlide(direction) {
    isManualScroll = true;
    
    const step = direction * itemWidth;
    const targetPosition = carouselPosition + step;
    const startPosition = carouselPosition;
    const startTime = performance.now();
    const duration = 300;
    
    function smoothScroll(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        const currentPosition = startPosition + (step * ease);
        
        const track = document.querySelector('.carousel-track');
        if (track) {
            track.style.transform = `translateX(${currentPosition}px)`;
        }
        
        if (progress < 1) {
            requestAnimationFrame(smoothScroll);
        } else {
            carouselPosition = targetPosition;
            
            if (carouselPosition <= -(brands.length * itemWidth)) {
                carouselPosition = 0;
            }
            if (carouselPosition > 0) {
                carouselPosition = -(brands.length * itemWidth);
            }
            
            const track = document.querySelector('.carousel-track');
            if (track) {
                track.style.transform = `translateX(${carouselPosition}px)`;
            }
            
            clearTimeout(manualTimeout);
            manualTimeout = setTimeout(() => {
                isManualScroll = false;
            }, 2000);
        }
    }
    
    requestAnimationFrame(smoothScroll);
}

function setupCarousel() {
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    const track = document.querySelector('.carousel-track');
    
    if (!prevBtn || !nextBtn || !track) return;
    
    renderBrands();
    
    prevBtn.addEventListener('click', () => {
        manualSlide(1);
    });
    
    nextBtn.addEventListener('click', () => {
        manualSlide(-1);
    });
    
    track.addEventListener('mouseenter', () => {
        stopAnimation();
    });
    
    track.addEventListener('mouseleave', () => {
        if (!isManualScroll) {
            startAnimation();
        }
    });
    
    startAnimation();
}

// ============================================
// 13. АДАПТАЦИЯ
// ============================================

let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        carouselPosition = 0;
        const track = document.querySelector('.carousel-track');
        if (track) {
            track.style.transform = `translateX(${carouselPosition}px)`;
        }
    }, 200);
});

// ============================================
// 14. ИНИЦИАЛИЗАЦИЯ
// ============================================

document.addEventListener('DOMContentLoaded', async function() {
    console.log(' CyberTech загружается...');
    
    await initAuth();
    await loadProducts('all');
    setupCarousel();
    setupSearch();
    setupCategoryFilter();
    updateFavoritesCount();
    updateCartCount();  
    
    setTimeout(checkFavoritesStatus, 500);
    console.log('✅ CyberTech загружен!');
});