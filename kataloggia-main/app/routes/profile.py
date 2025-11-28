"""
Profile routes
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user

# DİKKAT: url_prefix BURAYA YAZMIYORUZ!
bp = Blueprint('profile', __name__)

@bp.route('/')
@login_required
def index():
    """Profil ana sayfa"""
    return render_template('profile.html', user=current_user)

@bp.route('/settings')
@login_required
def settings():
    """Profil ayarları"""
    return render_template('profile_settings.html', user=current_user)

@bp.route('/collections')
@login_required
def collections():
    """Kullanıcı koleksiyonları"""
    return render_template('profile_collections.html', user=current_user)

@bp.route('/favorites')
@login_required
def favorites():
    """Favoriler sayfası"""
    return render_template('profile_favorites.html', user=current_user)

@bp.route('/preferences')
@login_required
def preferences():
    """Tercihler sayfası"""
    return render_template('profile_preferences.html', user=current_user)

@bp.route('/tracking')
@login_required
def tracking():
    """Fiyat takip özeti sayfası"""
    return render_template('profile_tracking.html', user=current_user)
