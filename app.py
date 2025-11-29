"""
Render.com deployment entry point
Flask uygulaması için Render.com web service
"""
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Try different paths to find app package
# Path 1: kataloggia-main/app (for Render.com)
kataloggia_app_dir_1 = os.path.join(current_dir, 'kataloggia-main', 'app')
# Path 2: kataloggia-main/kataloggia-main/app (for local)
kataloggia_app_dir_2 = os.path.join(current_dir, 'kataloggia-main', 'kataloggia-main', 'app')

if os.path.exists(kataloggia_app_dir_1):
    # Render.com structure
    kataloggia_dir = os.path.join(current_dir, 'kataloggia-main')
    sys.path.insert(0, kataloggia_dir)
    # Also add parent for models.py
    sys.path.insert(0, current_dir)
    print(f"[INFO] Using Render.com structure: {kataloggia_dir}")
elif os.path.exists(kataloggia_app_dir_2):
    # Local structure
    kataloggia_dir = os.path.join(current_dir, 'kataloggia-main', 'kataloggia-main')
    sys.path.insert(0, kataloggia_dir)
    # Also add parent for models.py
    parent_dir = os.path.dirname(kataloggia_dir)
    sys.path.insert(0, parent_dir)
    print(f"[INFO] Using local structure: {kataloggia_dir}")

try:
    # Remove app.py from sys.modules to avoid circular import
    if 'app' in sys.modules and sys.modules['app'].__file__ == __file__:
        del sys.modules['app']
    
    # Import app package (not app.py file)
    if os.path.exists(kataloggia_app_dir_1):
        # Render.com structure
        from app import create_app
    elif os.path.exists(kataloggia_app_dir_2):
        # Local structure - need to import from nested path
        import importlib
        import importlib.util
        app_init_path = os.path.join(kataloggia_dir, 'app', '__init__.py')
        spec = importlib.util.spec_from_file_location("app_package_init", app_init_path)
        app_init_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_init_module)
        create_app = app_init_module.create_app
    else:
        raise ImportError("App package not found in any expected location")
    
    # Import models for database initialization
    try:
        from models import init_db
        from app.utils.database_indexer import DatabaseIndexer
    except ImportError as e:
        print(f"[WARNING] Could not import models or DatabaseIndexer: {e}")
        init_db = None
        DatabaseIndexer = None
    
    # Create app - use production mode for Render.com
    config_mode = os.environ.get('FLASK_ENV', 'production')
    app = create_app(config_mode)
    
    # Initialize database if models are available
    if init_db:
        try:
            init_db()
            print("[INFO] Veritabanı başlatıldı")
        except Exception as e:
            print(f"[WARNING] Veritabanı başlatma hatası: {e}")
    
    # Create indexes for performance
    if DatabaseIndexer:
        try:
            DatabaseIndexer.create_indexes()
            print("[INFO] Database indexler oluşturuldu")
        except Exception as e:
            print(f"[WARNING] Index oluşturma hatası: {e}")
    
    print(f"[INFO] App created successfully in {config_mode} mode")
    
except Exception as e:
    print(f"[ERROR] Import hatası: {e}")
    import traceback
    traceback.print_exc()
    # Fallback minimal app
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return f'''
        <h1>Wishya App - Import Error</h1>
        <p>Import hatası: {str(e)}</p>
        <p>Lütfen konsol loglarını kontrol edin.</p>
        <p>Current dir: {current_dir}</p>
        <p>Python path: {sys.path}</p>
        '''

# Export for Render.com (gunicorn will use this)
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"\n{'='*50}")
    print(f"Wishya Uygulaması Başlatılıyor")
    print(f"{'='*50}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"URL: http://localhost:{port}")
    print(f"{'='*50}\n")
    
    app.run(host=host, port=port, debug=debug)

