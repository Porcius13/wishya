"""
Farklı port ve ayarlarla çalıştırma scripti
Kullanım: python run_local.py --port 8080
"""
import argparse
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    parser = argparse.ArgumentParser(description='Favit uygulamasını çalıştır')
    parser.add_argument('--port', type=int, default=5000, help='Port numarası (varsayılan: 5000)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host adresi (varsayılan: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true', help='Debug modunu aktifleştir')
    parser.add_argument('--no-debug', action='store_true', help='Debug modunu kapat')
    
    args = parser.parse_args()
    
    # Ortam değişkenlerini ayarla
    os.environ['PORT'] = str(args.port)
    os.environ['HOST'] = args.host
    if args.debug:
        os.environ['DEBUG'] = 'True'
    elif args.no_debug:
        os.environ['DEBUG'] = 'False'
    
    # run.py'yi import et ve çalıştır
    try:
        from app import create_app, get_socketio
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
        
        debug_mode = not args.no_debug if args.no_debug else (args.debug or True)
        
        print(f"\n{'='*50}")
        print(f"🚀 Favit Uygulaması Başlatılıyor")
        print(f"{'='*50}")
        print(f"📍 Host: {args.host}")
        print(f"🔌 Port: {args.port}")
        print(f"🐛 Debug: {debug_mode}")
        print(f"🌐 URL: http://localhost:{args.port}")
        print(f"{'='*50}\n")
        
        socketio = get_socketio()
        if socketio:
            socketio.run(app, host=args.host, port=args.port, debug=debug_mode)
        else:
            app.run(host=args.host, port=args.port, debug=debug_mode)
            
    except ImportError as e:
        print(f"[ERROR] Import hatası: {e}")
        print("[INFO] Eski app.py kullanılıyor...")
        import app_old as old_app
        old_app.app.run(host=args.host, port=args.port, debug=debug_mode)

if __name__ == "__main__":
    main()

