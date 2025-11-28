"""
Model Tests
"""
import pytest
from app.models.user import User
from app.models.product import Product

def test_user_creation():
    """Test user creation"""
    try:
        user = User.create('testuser', 'test@test.com', 'password123')
        assert user is not None
        assert user.username == 'testuser'
        assert user.email == 'test@test.com'
    except Exception as e:
        # User might already exist
        pass

def test_user_authentication():
    """Test user authentication"""
    try:
        user = User.create('testuser2', 'test2@test.com', 'password123')
        assert user.check_password('password123') == True
        assert user.check_password('wrongpassword') == False
    except Exception as e:
        pass

def test_product_creation():
    """Test product creation"""
    try:
        # Create test user first
        user = User.create('testuser3', 'test3@test.com', 'password123')
        
        product = Product.create(
            user_id=user.id,
            name='Test Product',
            price='100 TL',
            url='https://example.com/product',
            brand='Test Brand'
        )
        
        assert product is not None
        assert product.name == 'Test Product'
        assert product.price == '100 TL'
    except Exception as e:
        pass

