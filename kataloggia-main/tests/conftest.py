"""
Pytest configuration
"""
import pytest
import os
import sys
from app import create_app
from models import init_db

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        init_db()
        yield app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test runner"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client):
    """Get authentication headers"""
    # Register test user
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'test@test.com',
        'password': 'testpass123'
    })
    
    if response.status_code == 201:
        data = response.get_json()
        token = data.get('token')
        if token:
            return {'Authorization': f'Bearer {token}'}
    
    return {}

