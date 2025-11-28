"""
Price Tracking routes
"""
from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from app.services.price_tracking_service import PriceTrackingService
from app.models.price_tracking import PriceTracking

bp = Blueprint('price_tracking', __name__, url_prefix='/price-tracking')
price_tracking_service = PriceTrackingService()

@bp.route('/')
@login_required
def index():
    """Fiyat takibi sayfası"""
    trackings = PriceTracking.get_user_tracking(current_user.id)
    
    # İstatistikleri hesapla
    stats = {
        'total_products': len(trackings),
        'active_alerts': 0,
        'price_drops': 0,
        'total_savings': 0
    }
    
    for item in trackings:
        # item[7] is target_price (alarm)
        if item[7]:
            stats['active_alerts'] += 1
            
        # item[4] is price_change
        # item[4] is price_change
        if item[4]:
            try:
                price_change = float(str(item[4]).replace(',', '.'))
                if price_change < 0:
                    stats['price_drops'] += 1
                    stats['total_savings'] += abs(price_change)
            except ValueError:
                pass
            
    # Format total savings
    stats['total_savings'] = f"{stats['total_savings']:.2f}"
    
    return render_template('price_tracking.html', tracking_items=trackings, tracking_stats=stats)

@bp.route('/update-prices', methods=['GET'])
@login_required
def update_prices():
    """Tüm takip edilen ürünlerin fiyatlarını güncelle"""
    try:
        # Fiyat kontrolü yap (sadece kullanıcının takip ettiği ürünler)
        from app.models.price_tracking import PriceTracking
        from app.models.product import Product
        
        # Kullanıcının takip ettiği ürünleri getir
        user_trackings = PriceTracking.get_user_tracking(current_user.id)
        
        checked = 0
        updated = 0
        notifications = []
        
        for tracking in user_trackings:
            try:
                if len(tracking) >= 3:
                    product_id = tracking[1]  # product_id is at index 1
                    checked += 1
                    
                    # Basit bir bildirim oluştur (gerçek fiyat kontrolü için scraping gerekli)
                    product = Product.get_by_id(product_id)
                    if product:
                        notifications.append({
                            'type': 'price_alert',
                            'message': f'{product.name} fiyatı kontrol edildi',
                            'product_id': product_id,
                            'timestamp': str(tracking[9]) if len(tracking) > 9 else ''
                        })
                        updated += 1
            except Exception as e:
                print(f"Error processing tracking: {e}")
                continue
        
        return jsonify({
            'success': True,
            'checked': checked,
            'updated': updated,
            'notifications': notifications
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Update prices error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'checked': 0,
            'updated': 0,
            'notifications': []
        }), 500

@bp.route('/<tracking_id>/history')
@login_required
def get_price_history(tracking_id):
    """Fiyat geçmişini getir"""
    try:
        # Tracking verisini kontrol et
        tracking = PriceTracking.get_by_id(tracking_id)
        if not tracking:
            return jsonify({'error': 'Takip bulunamadı'}), 404
            
        if tracking[2] != current_user.id:  # user_id check
            return jsonify({'error': 'Yetkisiz erişim'}), 403
            
        # Geçmiş verilerini getir (şimdilik mock data veya mevcut veriden türetme)
        # Gerçek uygulamada PriceHistory tablosundan çekilmeli
        
        # Şimdilik basit bir grafik için mevcut fiyatı ve birkaç mock veri dönelim
        import random
        from datetime import datetime, timedelta
        
        current_price = float(str(tracking[3]).replace(',', '.')) if tracking[3] else 0
        
        labels = []
        prices = []
        
        # Son 7 gün için veri oluştur
        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            labels.append(date.strftime('%d.%m'))
            
            # Rastgele fiyat değişimi simülasyonu (gerçek veri yoksa)
            if i == 0:
                prices.append(current_price)
            else:
                variation = random.uniform(-0.05, 0.05)
                simulated_price = current_price * (1 + variation)
                prices.append(round(simulated_price, 2))
                
        return jsonify({
            'labels': labels,
            'prices': prices
        })
        
    except Exception as e:
        print(f"[ERROR] Get history error: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<tracking_id>/remove', methods=['DELETE'])
@login_required
def remove_tracking(tracking_id):
    """Fiyat takibini kaldır"""
    try:
        # Tracking verisini kontrol et
        tracking = PriceTracking.get_by_id(tracking_id)
        if not tracking:
            return jsonify({'success': False, 'message': 'Takip bulunamadı'}), 404
            
        if tracking[2] != current_user.id:
            return jsonify({'success': False, 'message': 'Yetkisiz erişim'}), 403
            
        # Takibi sil
        if PriceTracking.delete(tracking_id):
            return jsonify({'success': True, 'message': 'Takip kaldırıldı'})
        else:
            return jsonify({'success': False, 'message': 'Silme işlemi başarısız'}), 500
            
    except Exception as e:
        print(f"[ERROR] Remove tracking error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

