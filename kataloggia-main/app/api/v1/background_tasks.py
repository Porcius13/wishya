"""
Background Tasks API
Async task management endpoints
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

try:
    from app.tasks.scraping_tasks import (
        scrape_product_task,
        scrape_batch_task,
        check_prices_task,
        check_product_price_task,
        CELERY_AVAILABLE
    )
except ImportError:
    CELERY_AVAILABLE = False
    def scrape_product_task(url): return None
    def scrape_batch_task(urls): return []
    def check_prices_task(): return {}
    def check_product_price_task(product_id): return {}

bp = Blueprint('background_tasks', __name__, url_prefix='/api/v1/tasks')

@bp.route('/scrape', methods=['POST'])
@login_required
def start_scraping_task():
    """Async scraping task başlat"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL gerekli'
            }), 400
        
        # Start async task
        if hasattr(scrape_product_task, 'delay'):
            # Celery available
            task = scrape_product_task.delay(url)
            return jsonify({
                'success': True,
                'task_id': task.id,
                'status': 'started',
                'message': 'Scraping task başlatıldı'
            }), 202
        else:
            # Synchronous fallback
            result = scrape_product_task(url)
            return jsonify({
                'success': True,
                'data': result,
                'status': 'completed'
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/scrape/batch', methods=['POST'])
@login_required
def start_batch_scraping_task():
    """Async batch scraping task başlat"""
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
        
        # Start async task
        if hasattr(scrape_batch_task, 'delay'):
            task = scrape_batch_task.delay(urls)
            return jsonify({
                'success': True,
                'task_id': task.id,
                'status': 'started',
                'message': 'Batch scraping task başlatıldı'
            }), 202
        else:
            # Synchronous fallback
            result = scrape_batch_task(urls)
            return jsonify({
                'success': True,
                'data': result,
                'status': 'completed'
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/price-check', methods=['POST'])
@login_required
def start_price_check_task():
    """Fiyat kontrolü task'ı başlat"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        
        if product_id:
            # Single product check
            if hasattr(check_product_price_task, 'delay'):
                task = check_product_price_task.delay(product_id)
                return jsonify({
                    'success': True,
                    'task_id': task.id,
                    'status': 'started'
                }), 202
            else:
                result = check_product_price_task(product_id)
                return jsonify({
                    'success': True,
                    'data': result,
                    'status': 'completed'
                }), 200
        else:
            # Check all prices
            if hasattr(check_prices_task, 'delay'):
                task = check_prices_task.delay()
                return jsonify({
                    'success': True,
                    'task_id': task.id,
                    'status': 'started',
                    'message': 'Tüm fiyatlar kontrol ediliyor'
                }), 202
            else:
                result = check_prices_task()
                return jsonify({
                    'success': True,
                    'data': result,
                    'status': 'completed'
                }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<task_id>/status', methods=['GET'])
@login_required
def get_task_status(task_id):
    """Task durumunu kontrol et"""
    try:
        from app.tasks.scraping_tasks import celery_app
        
        if CELERY_AVAILABLE:
            task = celery_app.AsyncResult(task_id)
            return jsonify({
                'success': True,
                'task_id': task_id,
                'status': task.state,
                'result': task.result if task.ready() else None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Celery not available'
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

