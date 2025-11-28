"""
API Error Handlers
"""
from flask import jsonify, Blueprint

bp = Blueprint('errors', __name__)

@bp.errorhandler(404)
def not_found(error):
    """404 Error Handler"""
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404

@bp.errorhandler(500)
def internal_error(error):
    """500 Error Handler"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

@bp.errorhandler(400)
def bad_request(error):
    """400 Error Handler"""
    return jsonify({
        'success': False,
        'error': 'Bad request'
    }), 400

