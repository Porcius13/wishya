"""
Error Tracking
Sentry integration for error tracking
"""
import os

# Try to import Sentry
try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    SENTRY_AVAILABLE = True
    
    # Try to import SQLAlchemy integration (optional)
    try:
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        SQLALCHEMY_INTEGRATION_AVAILABLE = True
    except Exception:
        SQLALCHEMY_INTEGRATION_AVAILABLE = False
        SqlalchemyIntegration = None
except ImportError:
    SENTRY_AVAILABLE = False
    SQLALCHEMY_INTEGRATION_AVAILABLE = False
    SqlalchemyIntegration = None
    print("[INFO] sentry-sdk yüklü değil, error tracking devre dışı")

def init_error_tracking(app):
    """Initialize error tracking with Sentry"""
    if not SENTRY_AVAILABLE:
        return
    
    sentry_dsn = os.environ.get('SENTRY_DSN')
    
    if sentry_dsn:
        integrations = [FlaskIntegration()]
        if SQLALCHEMY_INTEGRATION_AVAILABLE and SqlalchemyIntegration:
            integrations.append(SqlalchemyIntegration())
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=integrations,
            traces_sample_rate=1.0,
            environment=os.environ.get('FLASK_ENV', 'development'),
            release=os.environ.get('APP_VERSION', '1.0.0'),
        )
        print("[INFO] Sentry error tracking initialized")
    else:
        print("[INFO] SENTRY_DSN not set, error tracking disabled")

