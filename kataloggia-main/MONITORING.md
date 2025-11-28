# 📊 Monitoring & Logging

## ✅ Tamamlanan İyileştirmeler

### 1. **Structured Logging**
- ✅ Structlog integration
- ✅ JSON logging format
- ✅ Log rotation
- ✅ Multiple log levels

### 2. **Error Tracking**
- ✅ Sentry integration
- ✅ Error reporting
- ✅ Performance monitoring
- ✅ Release tracking

### 3. **Analytics**
- ✅ Event tracking
- ✅ Usage analytics
- ✅ API call tracking
- ✅ User activity tracking

## 🚀 Kullanım

### Logging

```python
from app.utils.logging_config import get_logger

logger = get_logger('my_module')

logger.info('Info message', extra={'key': 'value'})
logger.error('Error message', exc_info=True)
logger.warning('Warning message')
```

### Error Tracking

```python
# Sentry automatically captures:
# - Unhandled exceptions
# - Flask errors
# - Performance issues
```

### Analytics

```python
from app.services.analytics_service import analytics_service

# Track events
analytics_service.track_product_added(user_id, product_id)
analytics_service.track_scraping(user_id, url, success=True)
analytics_service.track_api_call('/api/v1/products', 'GET', user_id)
```

## 🔧 Configuration

### Environment Variables

```bash
# Logging
export LOG_LEVEL=INFO

# Sentry
export SENTRY_DSN=your-sentry-dsn
export APP_VERSION=1.0.0
export FLASK_ENV=production
```

## 📊 Log Files

- `logs/app.log` - Application logs
- `logs/analytics.jsonl` - Analytics events

## 🎯 Best Practices

1. **Use appropriate log levels**
2. **Include context in logs**
3. **Don't log sensitive data**
4. **Monitor error rates**
5. **Track important events**

