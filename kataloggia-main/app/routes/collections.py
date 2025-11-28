"""
Collection Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.collection import Collection

bp = Blueprint('collections_ui', __name__)

@bp.route('/')
@login_required
def index():
    """Koleksiyonları listele"""
    collections = Collection.get_user_collections(current_user.id)
    return render_template('collections/index.html', collections=collections)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Yeni koleksiyon oluştur"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        is_public = 'is_public' in request.form
        
        if not name:
            flash('Koleksiyon adı gerekli', 'error')
            return redirect(url_for('collections_ui.create'))
            
        try:
            Collection.create(
                user_id=current_user.id,
                name=name,
                description=description,
                type='custom',
                is_public=is_public
            )
            flash('Koleksiyon başarıyla oluşturuldu', 'success')
            return redirect(url_for('profile.collections'))
        except Exception as e:
            flash(f'Hata: {str(e)}', 'error')
            return redirect(url_for('collections_ui.create'))
            
    return render_template('collections/create.html')

@bp.route('/<collection_id>')
@login_required
def view(collection_id):
    """Koleksiyon detayını görüntüle"""
    collection = Collection.get_by_id(collection_id)
    if not collection or collection.user_id != current_user.id:
        flash('Koleksiyon bulunamadı', 'error')
        return redirect(url_for('profile.collections'))
        
    products = collection.get_products()
    return render_template('collections/view.html', collection=collection, products=products)

@bp.route('/<collection_id>/add_product/<product_id>', methods=['POST'])
@login_required
def add_product(collection_id, product_id):
    """Koleksiyona ürün ekle"""
    try:
        collection = Collection.get_by_id(collection_id)
        if not collection or collection.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Koleksiyon bulunamadı'}), 404
            
        success = collection.add_product(product_id)
        if success:
            return jsonify({'success': True, 'message': 'Ürün koleksiyona eklendi'})
        else:
            return jsonify({'success': False, 'message': 'Ürün zaten koleksiyonda veya eklenemedi'})
            
    except Exception as e:
        print(f"[ERROR] Add to collection error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<collection_id>/remove_product/<product_id>', methods=['POST'])
@login_required
def remove_product(collection_id, product_id):
    """Koleksiyondan ürün çıkar"""
    try:
        collection = Collection.get_by_id(collection_id)
        if not collection or collection.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Koleksiyon bulunamadı'}), 404
            
        collection.remove_product(product_id)
        return jsonify({'success': True, 'message': 'Ürün koleksiyondan çıkarıldı'})
            
    except Exception as e:
        print(f"[ERROR] Remove from collection error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<collection_id>/delete', methods=['POST'])
@login_required
def delete(collection_id):
    """Koleksiyonu sil"""
    try:
        collection = Collection.get_by_id(collection_id)
        if not collection or collection.user_id != current_user.id:
            flash('Koleksiyon bulunamadı', 'error')
            return redirect(url_for('profile.collections'))
            
        collection.delete()
        flash('Koleksiyon silindi', 'success')
        return redirect(url_for('profile.collections'))
            
    except Exception as e:
        print(f"[ERROR] Delete collection error: {e}")
        flash(f'Hata: {str(e)}', 'error')
        return redirect(url_for('profile.collections'))
