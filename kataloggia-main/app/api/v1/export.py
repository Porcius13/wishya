"""
Export API
Export products and collections
"""
from flask import Blueprint, jsonify, send_file
from flask_login import login_required, current_user
from app.services.product_service import ProductService
from app.services.collection_service import CollectionService
import json
import csv
import io
from datetime import datetime

bp = Blueprint('export', __name__, url_prefix='/api/v1/export')
product_service = ProductService()
collection_service = CollectionService()

@bp.route('/products/json', methods=['GET'])
@login_required
def export_products_json():
    """Export products as JSON"""
    try:
        products = product_service.get_user_products(current_user.id, use_cache=False)
        
        products_data = [p.to_dict() for p in products]
        
        # Create JSON file in memory
        json_data = json.dumps(products_data, indent=2, ensure_ascii=False)
        json_bytes = json_data.encode('utf-8')
        
        # Create file-like object
        output = io.BytesIO(json_bytes)
        output.seek(0)
        
        filename = f"products_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return send_file(
            output,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/products/csv', methods=['GET'])
@login_required
def export_products_csv():
    """Export products as CSV"""
    try:
        products = product_service.get_user_products(current_user.id, use_cache=False)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Name', 'Brand', 'Price', 'Old Price', 'URL', 'Image', 'Created At'])
        
        # Write data
        for product in products:
            writer.writerow([
                product.id,
                product.name,
                product.brand,
                product.price,
                product.old_price or '',
                product.url,
                product.image or '',
                str(product.created_at)
            ])
        
        # Convert to bytes
        csv_bytes = output.getvalue().encode('utf-8')
        output = io.BytesIO(csv_bytes)
        output.seek(0)
        
        filename = f"products_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/collections/json', methods=['GET'])
@login_required
def export_collections_json():
    """Export collections as JSON"""
    try:
        collections = collection_service.get_user_collections(current_user.id)
        
        collections_data = []
        for collection in collections:
            collection_dict = collection.to_dict()
            collection_dict['products'] = [p.to_dict() for p in collection.get_products()]
            collections_data.append(collection_dict)
        
        json_data = json.dumps(collections_data, indent=2, ensure_ascii=False)
        json_bytes = json_data.encode('utf-8')
        
        output = io.BytesIO(json_bytes)
        output.seek(0)
        
        filename = f"collections_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return send_file(
            output,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

