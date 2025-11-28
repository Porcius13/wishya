"""
Application entry point
Modern modüler yapı ile uygulama başlatma
"""
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
# Add parent directory for models.py
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import from app package (not app.py)
# Make sure we import from the app package, not app_old.py
try:
    # Remove any cached app modules that might conflict
    modules_to_remove = [k for k in sys.modules.keys() if k.startswith('app')]
    for mod in modules_to_remove:
        del sys.modules[mod]
    
    # Ensure we're importing from the app package directory
    app_package_path = os.path.join(current_dir, 'app')
    if os.path.exists(app_package_path):
        # Import from the app package in current directory
        from app import create_app, get_socketio
    else:
        raise ImportError(f"App package not found at {app_package_path}")
    
    from models import init_db
    from app.utils.database_indexer import DatabaseIndexer
    
    # Create app
    app = create_app('development')
    
    # Initialize database
    init_db()
    print("[INFO] Veritabanı başlatıldı")
    
    # Create indexes for performance
    try:
        DatabaseIndexer.create_indexes()
        print("[INFO] Database indexler oluşturuldu")
    except Exception as e:
        print(f"[WARNING] Index oluşturma hatası: {e}")
    
    if __name__ == "__main__":
        # Port ayarı - ortam değişkeninden veya varsayılan 5000
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        debug = os.environ.get('DEBUG', 'True').lower() == 'true'
        
        print(f"[INFO] Uygulama başlatılıyor...")
        print(f"[INFO] Host: {host}")
        print(f"[INFO] Port: {port}")
        print(f"[INFO] Debug: {debug}")
        print(f"[INFO] URL: http://localhost:{port}")
        
        socketio = get_socketio()
        if socketio:
            # Run with SocketIO
            socketio.run(app, host=host, port=port, debug=debug)
        else:
            # Run without SocketIO
            app.run(host=host, port=port, debug=debug)
except ImportError as e:
    print(f"[ERROR] Import hatası: {e}")
    print("[INFO] Eski app.py kullanılıyor...")
    # Fallback to old app.py
    import app as old_app
    old_app.app.run(host="0.0.0.0", port=5000, debug=True)
