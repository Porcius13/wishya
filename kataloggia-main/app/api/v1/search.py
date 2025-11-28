"""
Search API
Product and collection search
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.product_service import ProductService
from app.services.collection_service import CollectionService

bp = Blueprint('search', __name__, url_prefix='/api/v1/search')
product_service = ProductService()
collection_service = CollectionService()

@bp.route('/products', methods=['GET'])
@login_required
def search_products():
    """Search products"""
    try:
        query = request.args.get('q', '').strip()
        brand = request.args.get('brand', '').strip()
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        
        if not query and not brand:
            return jsonify({
                'success': False,
                'error': 'Search query or brand required'
            }), 400
        
        # Get all user products
        products = product_service.get_user_products(current_user.id, use_cache=False)
        
        # Filter products
        results = []
        for product in products:
            match = True
            
            # Text search
            if query:
                query_lower = query.lower()
                if query_lower not in product.name.lower() and query_lower not in product.brand.lower():
                    match = False
            
            # Brand filter
            if brand and brand.lower() not in product.brand.lower():
                match = False
            
            # Price filter
            if min_price or max_price:
                try:
                    price_num = float(str(product.price).replace('₺', '').replace('TL', '').replace(',', '').strip())
                    
                    if min_price and price_num < float(min_price):
                        match = False
                    if max_price and price_num > float(max_price):
                        match = False
                except:
                    pass
            
            if match:
                results.append(product.to_dict())
        
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results),
            'query': query,
            'filters': {
                'brand': brand,
                'min_price': min_price,
                'max_price': max_price
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/collections', methods=['GET'])
@login_required
def search_collections():
    """Search collections"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query required'
            }), 400
        
        collections = collection_service.get_user_collections(current_user.id)
        
        results = []
        for collection in collections:
            if query.lower() in collection.name.lower() or \
               (collection.description and query.lower() in collection.description.lower()):
                results.append(collection.to_dict())
        
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results),
            'query': query
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

