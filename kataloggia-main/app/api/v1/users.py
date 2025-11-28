"""
Users API endpoints
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

bp = Blueprint('users', __name__)

@bp.route('/me', methods=['GET'])
@login_required
def get_profile():
    """Kullanıcı profil bilgileri"""
    return jsonify({
        'success': True,
        'data': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'created_at': current_user.created_at.isoformat() if hasattr(current_user.created_at, 'isoformat') else str(current_user.created_at)
        }
    }), 200

@bp.route('/me', methods=['PUT'])
@login_required
def update_profile():
    """Profil güncelle"""
    try:
        data = request.get_json()
        # Update logic here
        return jsonify({
            'success': True,
            'message': 'Profil güncellendi'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

