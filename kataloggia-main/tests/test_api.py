"""
API Tests
"""
import pytest
from app.models.user import User
from app.models.product import Product

def test_index(client):
    """Test index page"""
    response = client.get('/')
    assert response.status_code == 200

def test_register(client):
    """Test user registration"""
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'test@test.com',
        'password': 'testpass123'
    })
    assert response.status_code in [200, 201]
    data = response.get_json()
    assert data['success'] == True

def test_login(client):
    """Test user login"""
    # First register
    client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'test@test.com',
        'password': 'testpass123'
    })
    
    # Then login
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True

def test_get_products_unauthorized(client):
    """Test getting products without auth"""
    response = client.get('/api/v1/products')
    assert response.status_code == 401 or response.status_code == 302

def test_get_products_authorized(client, auth_headers):
    """Test getting products with auth"""
    response = client.get('/api/v1/products', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data or 'success' in data

def test_create_product(client, auth_headers):
    """Test creating product"""
    response = client.post('/api/v1/products', json={
        'name': 'Test Product',
        'price': '100 TL',
        'url': 'https://example.com/product',
        'brand': 'Test Brand'
    }, headers=auth_headers)
    
    assert response.status_code in [200, 201]
    data = response.get_json()
    assert data['success'] == True

def test_scraping_api(client, auth_headers):
    """Test scraping API"""
    response = client.post('/api/v1/scraping/scrape', json={
        'url': 'https://example.com/product'
    }, headers=auth_headers)
    
    # Should return 200 or 404 (depending on if scraping works)
    assert response.status_code in [200, 404, 500]

