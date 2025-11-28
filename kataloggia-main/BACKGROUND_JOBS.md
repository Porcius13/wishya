# 🔄 Background Jobs - Celery Integration

## ✅ Tamamlanan İyileştirmeler

### 1. **Celery Integration**
- ✅ Celery task system
- ✅ Async scraping tasks
- ✅ Price checking tasks
- ✅ Fallback to synchronous (Celery yoksa)

### 2. **Scheduled Tasks**
- ✅ Hourly price checks
- ✅ Daily cleanup tasks
- ✅ Cache cleanup tasks

### 3. **Task Management API**
- ✅ Start async tasks
- ✅ Check task status
- ✅ Task result retrieval

## 🚀 Kullanım

### Celery Setup

```bash
# Install Celery
pip install celery redis

# Start Redis (required for Celery)
redis-server

# Start Celery worker
celery -A app.tasks.scraping_tasks.celery_app worker --loglevel=info

# Start Celery Beat (scheduler)
celery -A app.tasks.scraping_tasks.celery_app beat --loglevel=info
```

### Environment Variables

```bash
export CELERY_BROKER_URL=redis://localhost:6379/0
export CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### API Usage

#### Start Async Scraping

```javascript
// Start async scraping task
fetch('/api/v1/tasks/scrape', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        url: 'https://example.com/product'
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        const taskId = data.task_id;
        // Check task status
        checkTaskStatus(taskId);
    }
});
```

#### Check Task Status

```javascript
function checkTaskStatus(taskId) {
    fetch(`/api/v1/tasks/${taskId}/status`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'SUCCESS') {
                // Task completed
                console.log('Result:', data.result);
            } else if (data.status === 'PENDING') {
                // Still processing
                setTimeout(() => checkTaskStatus(taskId), 2000);
            }
        });
}
```

#### Start Price Check

```javascript
// Check all prices
fetch('/api/v1/tasks/price-check', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({})
})
.then(response => response.json())
.then(data => {
    console.log('Price check started:', data);
});

// Check specific product
fetch('/api/v1/tasks/price-check', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        product_id: 'product-uuid'
    })
})
```

## 📋 Scheduled Tasks

### Hourly Price Checks
- **Schedule**: Every hour (minute 0)
- **Task**: `price_tracking.check_prices`
- **Purpose**: Check all tracked product prices

### Daily Cleanup
- **Schedule**: Daily at 2:00 AM
- **Task**: `maintenance.cleanup_old_data`
- **Purpose**: Clean up old data

### Cache Cleanup
- **Schedule**: Every 6 hours
- **Task**: `maintenance.clear_old_cache`
- **Purpose**: Clear old cache entries

## 🔄 Fallback Mode

Celery yoksa otomatik olarak synchronous mode'a geçer:
- Tasks execute immediately
- No async processing
- Still functional, just slower

## 🎯 Task Types

### 1. Scraping Tasks
- `scraping.scrape_product`: Single product scraping
- `scraping.scrape_batch`: Batch product scraping

### 2. Price Tracking Tasks
- `price_tracking.check_prices`: Check all prices
- `price_tracking.check_product_price`: Check single product

### 3. Maintenance Tasks
- `maintenance.cleanup_old_data`: Clean old data
- `maintenance.clear_old_cache`: Clear old cache

## 📊 Monitoring

### Task Status
- `PENDING`: Task queued
- `STARTED`: Task running
- `SUCCESS`: Task completed
- `FAILURE`: Task failed
- `RETRY`: Task retrying

### Task Results
- Success: Returns task result
- Failure: Returns error message
- Retry: Returns retry count

## 🔮 Future Improvements

1. **Task Monitoring Dashboard**: Web UI for task monitoring
2. **Task Retry Logic**: Automatic retry on failure
3. **Task Priority**: Priority queue for important tasks
4. **Task Chaining**: Chain multiple tasks
5. **Task Notifications**: Email/SMS on completion

