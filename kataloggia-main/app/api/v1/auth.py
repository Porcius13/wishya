"""
Authentication API endpoints
"""
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.jwt_auth import JWTAuth, JWT_AVAILABLE
from app.middleware.security import SecurityMiddleware

bp = Blueprint('auth', __name__)
auth_service = AuthService()

@bp.route('/login', methods=['GET'])
def login_page():
    """Login sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('login.html')

@bp.route('/login', methods=['POST'])
def login():
    """Login API"""
    try:
        # Debug: Check content type and get data
        content_type = request.content_type or ''
        print(f"[DEBUG] Content-Type: {content_type}")
        print(f"[DEBUG] Request method: {request.method}")
        print(f"[DEBUG] Request form: {dict(request.form)}")
        print(f"[DEBUG] Request JSON: {request.get_json(silent=True)}")
        
        # Check if this is a form submission (HTML form) or JSON request
        is_form_submission = request.form and not request.is_json
        
        # Try to get data from form first (for HTML forms), then JSON
        if request.form:
            data = request.form
        elif request.is_json:
            data = request.get_json()
        else:
            # Try to parse as form data
            data = request.form
        
        username = data.get('username')
        password = data.get('password')
        
        print(f"[DEBUG] Username: {username}, Password: {'*' * len(password) if password else 'None'}")
        print(f"[DEBUG] Is form submission: {is_form_submission}")
        
        if not username or not password:
            if is_form_submission:
                from flask import flash, redirect, url_for
                flash('Kullanıcı adı ve şifre gerekli', 'error')
                return redirect(url_for('auth.login_page'))
            return jsonify({
                'success': False,
                'error': 'Kullanıcı adı ve şifre gerekli'
            }), 400
        
        user = auth_service.authenticate(username, password)
        print(f"[DEBUG] User found: {user is not None}")
        
        # Debug: Check authentication details
        if not user:
            # Try to get user to see if it exists
            test_user = User.get_by_username(username)
            if test_user:
                print(f"[DEBUG] User exists but authentication failed")
                print(f"[DEBUG] Testing password check...")
                password_check = test_user.check_password(password)
                print(f"[DEBUG] Password check result: {password_check}")
            else:
                print(f"[DEBUG] User not found in database")
        
        if user:
            remember = bool(data.get('remember', False)) or (data.get('remember') == '1')
            login_user(user, remember=remember)
            print(f"[DEBUG] User logged in: {user.username}")
            
            # Generate JWT token (optional, for API usage)
            jwt_token = None
            if JWT_AVAILABLE:
                jwt_token = JWTAuth.generate_token(user.id, user.username, user.email)
            
            # If it's a form submission (not AJAX), redirect to dashboard
            if is_form_submission:
                from flask import flash, redirect, url_for
                flash('Giriş başarılı!', 'success')
                return redirect(url_for('dashboard.index'))
            
            response_data = {
                'success': True,
                'message': 'Giriş başarılı',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }
            
            if jwt_token:
                response_data['token'] = jwt_token
            
            return jsonify(response_data), 200
        else:
            print(f"[DEBUG] Authentication failed for username: {username}")
            # If it's a form submission, flash message and redirect
            if is_form_submission:
                from flask import flash, redirect, url_for
                flash('Kullanıcı adı veya şifre hatalı', 'error')
                return redirect(url_for('auth.login_page'))
            
            return jsonify({
                'success': False,
                'error': 'Kullanıcı adı veya şifre hatalı'
            }), 401
            
    except Exception as e:
        print(f"[ERROR] Login error: {e}")
        import traceback
        traceback.print_exc()
        
        # If it's a form submission, flash message and redirect
        is_form_submission = request.form and not request.is_json
        if is_form_submission:
            from flask import flash, redirect, url_for
            flash(f'Giriş hatası: {str(e)}', 'error')
            return redirect(url_for('auth.login_page'))
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/register', methods=['GET'])
def register_page():
    """Register sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('register.html')

@bp.route('/register', methods=['POST'])
def register():
    """Register API"""
    try:
        # Debug: Check content type and get data
        content_type = request.content_type or ''
        print(f"[DEBUG] Register - Content-Type: {content_type}")
        print(f"[DEBUG] Register - Request form: {dict(request.form)}")
        print(f"[DEBUG] Register - Request JSON: {request.get_json(silent=True)}")
        
        # Try to get data from form first (for HTML forms), then JSON
        if request.form:
            data = request.form
        elif request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            # If it's a form submission, flash message and redirect
            if not request.is_json and content_type and 'application/json' not in content_type:
                from flask import flash, redirect, url_for
                flash('Tüm alanlar gerekli', 'error')
                return redirect(url_for('auth.register_page'))
            
            return jsonify({
                'success': False,
                'error': 'Tüm alanlar gerekli'
            }), 400
        
        # Validate email
        if not SecurityMiddleware.validate_email(email):
            # If it's a form submission, flash message and redirect
            if not request.is_json and content_type and 'application/json' not in content_type:
                from flask import flash, redirect, url_for
                flash('Geçersiz email formatı', 'error')
                return redirect(url_for('auth.register_page'))
            
            return jsonify({
                'success': False,
                'error': 'Geçersiz email formatı'
            }), 400
        
        # Sanitize inputs
        username = SecurityMiddleware.sanitize_input(username, max_length=50)
        email = SecurityMiddleware.sanitize_input(email, max_length=100)
        
        user = auth_service.register(username, email, password)
        
        if user:
            login_user(user)
            print(f"[DEBUG] User registered and logged in: {user.username}")
            
            # Generate JWT token
            jwt_token = None
            if JWT_AVAILABLE:
                jwt_token = JWTAuth.generate_token(user.id, user.username, user.email)
            
            # If it's a form submission (not AJAX), redirect to dashboard
            if not request.is_json and content_type and 'application/json' not in content_type:
                from flask import redirect, url_for, flash
                flash('Kayıt başarılı! Hoş geldiniz.', 'success')
                return redirect(url_for('dashboard.index'))
            
            response_data = {
                'success': True,
                'message': 'Kayıt başarılı',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }
            
            if jwt_token:
                response_data['token'] = jwt_token
            
            return jsonify(response_data), 201
        else:
            # If it's a form submission, flash message and redirect
            if not request.is_json and content_type and 'application/json' not in content_type:
                from flask import flash, redirect, url_for
                flash('Kayıt başarısız. Kullanıcı adı veya email zaten kullanılıyor olabilir.', 'error')
                return redirect(url_for('auth.register_page'))
            
            return jsonify({
                'success': False,
                'error': 'Kayıt başarısız'
            }), 400
            
    except Exception as e:
        print(f"[ERROR] Register error: {e}")
        import traceback
        traceback.print_exc()
        
        # If it's a form submission, flash message and redirect
        if not request.is_json and content_type and 'application/json' not in content_type:
            from flask import flash, redirect, url_for
            flash(f'Kayıt hatası: {str(e)}', 'error')
            return redirect(url_for('auth.register_page'))
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout API"""
    logout_user()
    return jsonify({
        'success': True,
        'message': 'Çıkış başarılı'
    }), 200

@bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Mevcut kullanıcı bilgilerini getir"""
    return jsonify({
        'success': True,
        'data': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email
        }
    }), 200
