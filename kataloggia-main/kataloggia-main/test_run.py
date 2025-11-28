"""Test script to check if app can start"""
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
# Add parent directory for models.py
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    print("[TEST] Importing app...")
    from app import create_app, get_socketio
    print("[TEST] App imported successfully")
    
    print("[TEST] Creating app...")
    app = create_app('development')
    print("[TEST] App created successfully")
    
    print("[TEST] Testing routes...")
    with app.test_client() as client:
        response = client.get('/')
        print(f"[TEST] Home route status: {response.status_code}")
        
        response = client.get('/login')
        print(f"[TEST] Login route status: {response.status_code}")
    
    print("[TEST] All tests passed!")
    
except Exception as e:
    print(f"[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()


