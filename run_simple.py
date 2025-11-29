"""
Basit lokal çalıştırma scripti - SocketIO olmadan
"""
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
kataloggia_dir = os.path.join(current_dir, 'kataloggia-main', 'kataloggia-main')
sys.path.insert(0, kataloggia_dir)
parent_dir = os.path.dirname(kataloggia_dir)
sys.path.insert(0, parent_dir)

try:
    from app import create_app
    
    # Create app in development mode
    app = create_app('development')
    
    # Disable SocketIO for simple local run
    if hasattr(app, 'socketio') and app.socketio:
        print("[INFO] SocketIO disabled for simple local run")
    
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    print(f"\n{'='*50}")
    print(f"Wishya Uygulaması Başlatılıyor")
    print(f"{'='*50}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"URL: http://{host}:{port}")
    print(f"{'='*50}\n")
    
    # Run without SocketIO
    app.run(host=host, port=port, debug=True, use_reloader=False)
    
except Exception as e:
    print(f"[ERROR] Hata: {e}")
    import traceback
    traceback.print_exc()

