"""
Test script to check if app can start
"""
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
# Add parent directory for models.py
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print("[TEST] Starting import test...")

try:
    print("[TEST] Importing app...")
    from app import create_app, get_socketio
    from models import init_db
    print("[TEST] Imports successful!")
    
    print("[TEST] Creating app...")
    app = create_app('development')
    print("[TEST] App created!")
    
    print("[TEST] Initializing database...")
    init_db()
    print("[TEST] Database initialized!")
    
    print("[TEST] Getting socketio...")
    socketio = get_socketio()
    print(f"[TEST] SocketIO: {socketio}")
    
    print("\n[SUCCESS] All tests passed! App should start correctly.")
    print("[INFO] To start the app, run: python run.py")
    
except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

