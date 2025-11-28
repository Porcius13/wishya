"""
Product Routes
"""
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.utils.db_path import get_db_connection

bp = Blueprint('product_routes', __name__)

@bp.route('/<product_id>/tracking-status')
@login_required
def get_tracking_status(product_id):
    """Get price tracking status for a product"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT is_active, last_checked, current_price, original_price, price_change
            FROM price_tracking 
            WHERE product_id = ? AND user_id = ?
        ''', (product_id, current_user.id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return jsonify({
                'is_tracking': bool(row[0]),
                'last_checked': row[1],
                'current_price': row[2],
                'original_price': row[3],
                'price_change': row[4]
            })
        else:
            return jsonify({
                'is_tracking': False,
                'last_checked': None,
                'current_price': None,
                'original_price': None,
                'price_change': 0
            })
            
    except Exception as e:
        print(f"[ERROR] Get tracking status error: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<product_id>/add-to-tracking', methods=['POST'])
@login_required
def add_to_tracking(product_id):
    """Add product to price tracking"""
    try:
        from app.models.product import Product
        from app.models.price_tracking import PriceTracking

        # Check if product exists
        product = Product.get_by_id(product_id)
        if not product:
            return jsonify({'success': False, 'message': 'Ürün bulunamadı'}), 404

        # Check if already tracking
        existing = PriceTracking.get_by_product_and_user(product_id, current_user.id)
        if existing:
            return jsonify({'success': False, 'message': 'Bu ürün zaten takip ediliyor'}), 400

        # Create tracking
        PriceTracking.create(
            user_id=current_user.id,
            product_id=product_id,
            current_price=product.price,
            original_price=product.price
        )

        return jsonify({'success': True, 'message': 'Fiyat takibi başlatıldı'})

    except Exception as e:
        print(f"[ERROR] Add to tracking error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<product_id>/remove-from-tracking', methods=['POST'])
@login_required
def remove_from_tracking(product_id):
    """Remove product from price tracking"""
    try:
        from app.models.price_tracking import PriceTracking

        # Check if tracking exists
        existing = PriceTracking.get_by_product_and_user(product_id, current_user.id)
        if not existing:
            return jsonify({'success': False, 'message': 'Takip kaydı bulunamadı'}), 404

        # Remove tracking (existing is a tuple, id is at index 0)
        tracking_id = existing[0]
        PriceTracking.remove_tracking(tracking_id)

        return jsonify({'success': True, 'message': 'Fiyat takibi durduruldu'})

    except Exception as e:
        print(f"[ERROR] Remove from tracking error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
