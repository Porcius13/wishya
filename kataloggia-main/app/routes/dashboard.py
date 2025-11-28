"""
Dashboard routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.product import Product
from app.services.scraping_service import ScrapingService
from app.services.product_service import ProductService

bp = Blueprint('dashboard', __name__)
scraping_service = ScrapingService()
product_service = ProductService()

@bp.route('/dashboard')
@login_required
def index():
    """Dashboard ana sayfa"""
    products = Product.get_by_user_id(current_user.id)
    return render_template('dashboard.html', products=products)

@bp.route('/add_product', methods=['POST'])
@login_required
def add_product():
    """Ürün ekle (URL'den scrape ederek)"""
    try:
        # Debug: Check what we're receiving
        print(f"[DEBUG] Request method: {request.method}")
        print(f"[DEBUG] Content-Type: {request.content_type}")
        print(f"[DEBUG] Request form: {dict(request.form)}")
        print(f"[DEBUG] Request JSON: {request.get_json(silent=True)}")
        print(f"[DEBUG] Request args: {dict(request.args)}")
        
        # Try multiple ways to get the URL
        product_url = None
        
        # Try form data first
        if request.form:
            product_url = request.form.get('product_url') or request.form.get('url')
        
        # Try JSON
        if not product_url and request.is_json:
            json_data = request.get_json(silent=True)
            if json_data:
                product_url = json_data.get('product_url') or json_data.get('url')
        
        # Try args (query parameters)
        if not product_url:
            product_url = request.args.get('product_url') or request.args.get('url')
        
        print(f"[DEBUG] Extracted product_url: {product_url}")
        
        if not product_url:
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'URL gerekli'
                }), 400
            flash('URL gerekli', 'error')
            return redirect(url_for('dashboard.index'))
        
        # URL'den ürün bilgilerini çek
        print(f"[DEBUG] Scraping URL: {product_url}")
        scraped_data = scraping_service.scrape_product(product_url)
        print(f"[DEBUG] Scraped data: {scraped_data}")
        
        if not scraped_data:
            error_msg = 'Ürün bilgileri çekilemedi. Lütfen geçerli bir e-ticaret sitesi URL\'si girin.'
            print(f"[ERROR] Scraping failed for URL: {product_url}")
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 404
            flash(error_msg, 'error')
            return redirect(url_for('dashboard.index'))
        
        if not scraped_data.get('name'):
            error_msg = 'Ürün adı bulunamadı. Lütfen geçerli bir ürün URL\'si girin.'
            print(f"[ERROR] Product name not found in scraped data: {scraped_data}")
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 404
            flash(error_msg, 'error')
            return redirect(url_for('dashboard.index'))
        
        # Ürünü oluştur
        product = product_service.create_product(
            user_id=current_user.id,
            name=scraped_data.get('name', 'Bilinmeyen Ürün'),
            price=scraped_data.get('price', '0'),
            image=scraped_data.get('image'),
            brand=scraped_data.get('brand', 'Bilinmeyen'),
            url=product_url,
            old_price=scraped_data.get('old_price'),
            current_price=scraped_data.get('price'),
            discount_percentage=scraped_data.get('discount_percentage'),
            images=scraped_data.get('images')
        )
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Ürün başarıyla eklendi',
                'data': product.to_dict() if hasattr(product, 'to_dict') else None
            }), 201
        
        flash('Ürün başarıyla eklendi!', 'success')
        return redirect(url_for('dashboard.index') + '?added=1')
        
    except Exception as e:
        print(f"[ERROR] Add product error: {e}")
        import traceback
        traceback.print_exc()
        
        if request.is_json:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
        
        flash(f'Ürün eklenirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

@bp.route('/delete_product/<product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    """Ürün sil"""
    try:
        success = product_service.delete_product(product_id, current_user.id)
        
        if request.is_json:
            if success:
                return jsonify({'success': True, 'message': 'Ürün başarıyla silindi'}), 200
            else:
                return jsonify({'success': False, 'error': 'Ürün bulunamadı veya silinemedi'}), 404
        
        if success:
            flash('Ürün başarıyla silindi', 'success')
        else:
            flash('Ürün silinirken hata oluştu veya ürün bulunamadı', 'error')
            
        return redirect(url_for('dashboard.index'))
        
    except Exception as e:
        print(f"[ERROR] Delete product error: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
            
        flash(f'Ürün silinirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

