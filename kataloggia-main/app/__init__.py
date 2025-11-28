"""
Flask Application Factory
Modern modüler yapı ile uygulama başlatma
"""
from flask import Flask
from flask_login import LoginManager
import os

# Try to import SocketIO
try:
    from flask_socketio import SocketIO
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    print("[INFO] Flask-SocketIO yüklü değil, real-time features devre dışı")

# Login Manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Lütfen giriş yapın'
login_manager.login_message_category = 'info'

# SocketIO instance (will be initialized in create_app)
socketio = None

def create_app(config_name='development'):
    """Application factory pattern"""
    global socketio
    
    # Get the base directory (kataloggia-main/kataloggia-main)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Get parent directory where templates and static are located
    parent_dir = os.path.dirname(base_dir)
    template_dir = os.path.join(parent_dir, 'templates')
    static_dir = os.path.join(parent_dir, 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'favit-secret-key-2025')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///favit.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    login_manager.init_app(app)
    
    # Initialize SocketIO
    socketio_instance = None
    if SOCKETIO_AVAILABLE:
        socketio_instance = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
        from app.socketio import events
        events.register_socketio_events(socketio_instance)
        socketio = socketio_instance
        print("[INFO] SocketIO initialized")
    else:
        socketio = None
    
    # Initialize logging
    from app.utils.logging_config import setup_logging
    setup_logging(app)
    
    # Initialize error tracking
    from app.utils.error_tracking import init_error_tracking
    init_error_tracking(app)
    
    # Register blueprints
    from app.api.v1 import auth, products, collections, scraping, users, background_tasks, export, search
    from app.routes import main, dashboard, profile, notifications, price_tracking, product_routes, collections as collections_ui
    
    app.register_blueprint(main.bp)
    # Register auth routes without prefix for direct access (/login, /register, etc.)
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(profile.bp, url_prefix='/profile')
    app.register_blueprint(notifications.bp)
    app.register_blueprint(price_tracking.bp)
    app.register_blueprint(product_routes.bp, url_prefix='/product')
    app.register_blueprint(collections_ui.bp, url_prefix='/collections')
    app.register_blueprint(products.bp, url_prefix='/api/v1/products')
    app.register_blueprint(collections.bp, url_prefix='/api/v1/collections')
    app.register_blueprint(scraping.bp, url_prefix='/api/v1/scraping')
    app.register_blueprint(users.bp, url_prefix='/api/v1/users')
    app.register_blueprint(background_tasks.bp)
    app.register_blueprint(export.bp)
    app.register_blueprint(search.bp)
    
    # User loader
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)
    
    # Store socketio in app context
    app.socketio = socketio
    
    return app

def get_socketio():
    """Get SocketIO instance"""
    return socketio

