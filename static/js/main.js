// Utility functions for auth
function setToken(token) {
    localStorage.setItem('jwt_token', token);
}

function getToken() {
    return localStorage.getItem('jwt_token');
}

function removeToken() {
    localStorage.removeItem('jwt_token');
}

function isAuthenticated() {
    return !!getToken();
}

function logout() {
    removeToken();
    window.location.href = '/login';
}

// Setup navigation based on auth state
document.addEventListener('DOMContentLoaded', () => {
    const loginLink = document.getElementById('nav-login');
    const logoutLink = document.getElementById('nav-logout');
    
    if (loginLink && logoutLink) {
        if (isAuthenticated()) {
            loginLink.style.display = 'none';
            logoutLink.style.display = 'inline';
        } else {
            loginLink.style.display = 'inline';
            logoutLink.style.display = 'none';
        }
    }
});

// Common API call wrapper
async function apiCall(url, method = 'GET', body = null) {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (isAuthenticated()) {
        headers['Authorization'] = `Bearer ${getToken()}`;
    }
    
    const options = {
        method,
        headers
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    const response = await fetch(url, options);
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.msg || 'Something went wrong');
    }
    
    return data;
}

// Track behavior
async function trackBehavior(productId, actionType) {
    try {
        await apiCall('/api/track/', 'POST', {
            product_id: productId,
            action_type: actionType
        });
    } catch (error) {
        console.error('Failed to track behavior', error);
    }
}

// Login Form
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorMsg = document.getElementById('error-msg');
        
        try {
            const data = await apiCall('/api/auth/login', 'POST', { username, password });
            setToken(data.access_token);
            window.location.href = '/';
        } catch (error) {
            errorMsg.textContent = error.message;
            errorMsg.style.display = 'block';
        }
    });
}

// Register Form
const registerForm = document.getElementById('register-form');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorMsg = document.getElementById('error-msg');
        
        try {
            await apiCall('/api/auth/register', 'POST', { username, password });
            // Auto login or redirect to login
            const data = await apiCall('/api/auth/login', 'POST', { username, password });
            setToken(data.access_token);
            window.location.href = '/';
        } catch (error) {
            errorMsg.textContent = error.message;
            errorMsg.style.display = 'block';
        }
    });
}

// Recommendation Form
const recForm = document.getElementById('recommendation-form');
if (recForm) {
    recForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const purchases = document.getElementById('purchases').value;
        const needs = document.getElementById('needs').value;
        const shortages = document.getElementById('shortages').value;
        const btn = document.getElementById('submit-btn');
        const loader = document.getElementById('loader-container');
        const resultsSection = document.getElementById('results-section');
        const grid = document.getElementById('product-grid');
        
        btn.style.display = 'none';
        loader.style.display = 'block';
        resultsSection.style.display = 'none';
        
        try {
            const data = await apiCall('/api/recommend/', 'POST', {
                purchases, needs, shortages
            });
            
            grid.innerHTML = '';
            if (data.recommendations && data.recommendations.length > 0) {
                data.recommendations.forEach((product, index) => {
                    const card = document.createElement('div');
                    card.className = 'product-card';
                    card.style.animationDelay = `${index * 0.15}s`;
                    card.innerHTML = `
                        <div class="product-image-wrapper">
                            <img src="${product.image_url}" alt="${product.name}" class="product-image">
                        </div>
                        <div class="product-info">
                            <div class="product-category">${product.category}</div>
                            <h3 class="product-title">${product.name}</h3>
                            <p class="product-desc">${product.description}</p>
                            <div class="product-footer">
                                <div class="product-price">$${product.price.toFixed(2)}</div>
                                <button class="btn btn-primary" onclick="buyProduct(${product.id})">
                                    <i class="ph ph-shopping-cart" style="margin-right: 0.5rem;"></i> Buy
                                </button>
                            </div>
                        </div>
                    `;
                    // Track view
                    trackBehavior(product.id, 'view');
                    grid.appendChild(card);
                });
                resultsSection.style.display = 'block';
                // Scroll to results
                setTimeout(() => {
                    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            } else {
                grid.innerHTML = '<p style="text-align:center; grid-column: 1/-1; color: var(--text-muted);">No recommendations found. Try different inputs.</p>';
                resultsSection.style.display = 'block';
            }
        } catch (error) {
            alert(error.message);
        } finally {
            btn.style.display = 'inline-flex';
            loader.style.display = 'none';
        }
    });
}

// Buy Product
window.buyProduct = function(productId) {
    if(!isAuthenticated()) {
        alert("Please login to purchase items.");
        window.location.href = '/login';
        return;
    }
    trackBehavior(productId, 'purchase');
    alert("Product purchased successfully!");
}

// Dashboard Charts
const categoryChartCanvas = document.getElementById('categoryChart');
const actionChartCanvas = document.getElementById('actionChart');
const timelineChartCanvas = document.getElementById('timelineChart');

if (categoryChartCanvas && actionChartCanvas && timelineChartCanvas) {
    Chart.defaults.color = '#cbd5e1';
    Chart.defaults.font.family = "'Outfit', sans-serif";
    
    async function loadDashboard() {
        try {
            const data = await apiCall('/api/analytics/data');
            
            // Category Chart (Doughnut)
            new Chart(categoryChartCanvas, {
                type: 'doughnut',
                data: {
                    labels: data.categories.labels,
                    datasets: [{
                        data: data.categories.data,
                        backgroundColor: ['#6366f1', '#ec4899', '#8b5cf6', '#10b981', '#f59e0b'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { position: 'right' } }
                }
            });
            
            // Action Chart (Bar)
            new Chart(actionChartCanvas, {
                type: 'bar',
                data: {
                    labels: data.actions.labels,
                    datasets: [{
                        label: 'Interactions',
                        data: data.actions.data,
                        backgroundColor: '#ec4899',
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    scales: { y: { beginAtZero: true } }
                }
            });
            
            // Timeline Chart (Line)
            new Chart(timelineChartCanvas, {
                type: 'line',
                data: {
                    labels: data.timeline.labels,
                    datasets: [{
                        label: 'Activity Over Time',
                        data: data.timeline.data,
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: { y: { beginAtZero: true } }
                }
            });
            
        } catch (error) {
            console.error('Failed to load dashboard', error);
        }
    }
    
    loadDashboard();
}
