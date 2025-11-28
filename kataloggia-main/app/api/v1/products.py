"""
Products API endpoints
RESTful API for product management
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.product import Product
from app.services.product_service import ProductService

bp = Blueprint('products', __name__)
product_service = ProductService()

@bp.route('', methods=['GET'])
@login_required
def get_products():
    """Tüm ürünleri getir"""
    try:
        products = product_service.get_user_products(current_user.id)
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in products],
            'count': len(products)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('', methods=['POST'])
@login_required
def create_product():
    """Yeni ürün ekle"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['name', 'price', 'url', 'brand']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'{field} gerekli'
                }), 400
        
        product = product_service.create_product(
            user_id=current_user.id,
            name=data['name'],
            price=data['price'],
            image=data.get('image'),
            brand=data['brand'],
            url=data['url'],
            old_price=data.get('old_price'),
            current_price=data.get('current_price'),
            discount_percentage=data.get('discount_percentage')
        )
        
        return jsonify({
            'success': True,
            'data': product.to_dict(),
            'message': 'Ürün başarıyla eklendi'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<product_id>', methods=['GET'])
@login_required
def get_product(product_id):
    """Tek bir ürünü getir"""
    try:
        product = product_service.get_product(product_id, current_user.id)
        if not product:
            return jsonify({
                'success': False,
                'error': 'Ürün bulunamadı'
            }), 404
        
        return jsonify({
            'success': True,
            'data': product.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    """Ürün güncelle"""
    try:
        data = request.get_json()
        product = product_service.update_product(
            product_id=product_id,
            user_id=current_user.id,
            **data
        )
        
        if not product:
            return jsonify({
                'success': False,
                'error': 'Ürün bulunamadı veya yetkiniz yok'
            }), 404
        
        return jsonify({
            'success': True,
            'data': product.to_dict(),
            'message': 'Ürün başarıyla güncellendi'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    """Ürün sil"""
    try:
        success = product_service.delete_product(product_id, current_user.id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Ürün bulunamadı veya yetkiniz yok'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Ürün başarıyla silindi'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

