"""
Collections API endpoints
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.collection_service import CollectionService

bp = Blueprint('collections', __name__)
collection_service = CollectionService()

@bp.route('', methods=['GET'])
@login_required
def get_collections():
    """Tüm koleksiyonları getir"""
    try:
        collections = collection_service.get_user_collections(current_user.id)
        return jsonify({
            'success': True,
            'data': [c.to_dict() for c in collections],
            'count': len(collections)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('', methods=['POST'])
@login_required
def create_collection():
    """Yeni koleksiyon oluştur"""
    try:
        data = request.get_json()
        
        collection = collection_service.create_collection(
            user_id=current_user.id,
            name=data.get('name'),
            description=data.get('description'),
            type=data.get('type', 'custom'),
            is_public=data.get('is_public', True)
        )
        
        return jsonify({
            'success': True,
            'data': collection.to_dict(),
            'message': 'Koleksiyon başarıyla oluşturuldu'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<collection_id>', methods=['GET'])
@login_required
def get_collection(collection_id):
    """Tek bir koleksiyonu getir"""
    try:
        collection = collection_service.get_collection(collection_id, current_user.id)
        if not collection:
            return jsonify({
                'success': False,
                'error': 'Koleksiyon bulunamadı'
            }), 404
        
        return jsonify({
            'success': True,
            'data': collection.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<collection_id>/products/<product_id>', methods=['POST'])
@login_required
def add_product_to_collection(collection_id, product_id):
    """Koleksiyona ürün ekle"""
    try:
        success = collection_service.add_product(
            collection_id=collection_id,
            product_id=product_id,
            user_id=current_user.id
        )
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'İşlem başarısız'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Ürün koleksiyona eklendi'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

