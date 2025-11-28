"""
Vercel deployment entry point
Flask uygulaması için Vercel serverless function
Hem Vercel hem lokal çalıştırma için
"""
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Try different paths to find app package
# Path 1: kataloggia-main/kataloggia-main/app (for Vercel)
kataloggia_app_dir_1 = os.path.join(current_dir, 'kataloggia-main', 'app')
# Path 2: kataloggia-main/kataloggia-main/kataloggia-main/app (for local)
kataloggia_app_dir_2 = os.path.join(current_dir, 'kataloggia-main', 'kataloggia-main', 'app')

if os.path.exists(kataloggia_app_dir_1):
    # Vercel structure
    kataloggia_dir = os.path.join(current_dir, 'kataloggia-main')
    sys.path.insert(0, kataloggia_dir)
    print(f"[INFO] Using Vercel structure: {kataloggia_dir}")
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
        # Vercel structure
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
    
    # Create app - use development mode for local, production for Vercel
    config_mode = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_mode)
    
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

# Export for Vercel
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"\n{'='*50}")
    print(f"Wishya Uygulaması Başlatılıyor")
    print(f"{'='*50}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"URL: http://localhost:{port}")
    print(f"{'='*50}\n")
    
    app.run(host=host, port=port, debug=debug)

