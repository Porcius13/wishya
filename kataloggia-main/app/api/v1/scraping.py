"""
Scraping API endpoints
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.scraping_service import ScrapingService

bp = Blueprint('scraping', __name__)
scraping_service = ScrapingService()

@bp.route('/scrape', methods=['POST'])
@login_required
def scrape_product():
    """Ürün URL'sinden veri çek"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL gerekli'
            }), 400
        
        result = scraping_service.scrape_product(url)
        
        if not result or not result.get('name'):
            return jsonify({
                'success': False,
                'error': 'Ürün bilgileri çekilemedi'
            }), 404
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/batch', methods=['POST'])
@login_required
def scrape_batch():
    """Toplu ürün çekme"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({
                'success': False,
                'error': 'URL listesi gerekli'
            }), 400
        
        if len(urls) > 10:
            return jsonify({
                'success': False,
                'error': 'Maksimum 10 URL gönderebilirsiniz'
            }), 400
        
        results = scraping_service.scrape_multiple(urls)
        
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

