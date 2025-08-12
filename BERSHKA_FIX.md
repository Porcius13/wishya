# Bershka Image Extraction Fix Guide

## Problem Description
Bershka URLs were experiencing two main issues on Render:
1. **Navigation Timeout**: `Site-specific navigation hatası: Timeout 15000ms exceeded`
2. **Image Extraction Failure**: `Çekilen görsel: None` despite successful scraping

## Implemented Fixes

### 1. Enhanced Site-Specific Navigation (`handle_site_specific_navigation`)
- **Extended Timeout**: Increased from 15s to 30s for Bershka homepage navigation
- **Cookie Banner Handling**: Added comprehensive cookie acceptance logic
- **Human-like Behavior**: Implemented mouse movements and scrolling to bypass bot detection
- **Extended Wait Times**: Increased initial wait from 3s to 5s

### 2. Improved Product Page Navigation (`navigate_to_product_page`)
- **Dedicated Bershka Block**: Added specific navigation logic for Bershka URLs
- **Extended Loading**: 8-second wait time for page loading
- **Network Idle Wait**: 30-second timeout for network idle state
- **Gallery Activation**: Attempts to activate image galleries if present
- **Enhanced Scrolling**: Multiple scroll operations to trigger lazy-loaded images

### 3. Bershka-Specific Selectors (`extract_enhanced_data`)
Added comprehensive selector set for Bershka:
```python
"title_selectors": [
    'h1.product-name',
    'h1.product-title',
    'h1.title',
    'h1',
    '.product-name',
    '.product-title',
    '[data-testid="product-title"]',
    '[data-testid="product-name"]'
],
"price_selectors": [
    '.product-price',
    '.price',
    '.current-price',
    '.final-price',
    '[data-testid="product-price"]',
    '[data-testid="price"]',
    '.product-price-current',
    '.price-current'
],
"image_selectors": [
    'img.product-image',
    'img.product-main-image',
    'img.main-product-image',
    'img[class*="product"][class*="image"]',
    'img[class*="main"][class*="image"]',
    'img[class*="detail"][class*="image"]',
    'img[class*="gallery"]',
    'img[class*="carousel"]',
    'img[class*="slider"]',
    'img[class*="pdp"]',
    'img[src*="product"]',
    'img[src*="main"]',
    'img[src*="detail"]',
    'img[src*="image"]',
    'img[src*="gallery"]',
    'img[src*="pdp"]',
    'img'
]
```

### 4. Dedicated Image Extraction Logic (`extract_image`)
- **Bershka-Specific Block**: Added dedicated image extraction for Bershka URLs
- **Enhanced Selectors**: Comprehensive list of Bershka-specific image selectors
- **Scrolling Integration**: Automatic scrolling during image search
- **Detailed Logging**: Enhanced debug output for troubleshooting
- **Fallback Methods**: Multiple fallback strategies for image extraction

## Testing Tools

### 1. Dedicated Test Script (`test_bershka.py`)
- **Comprehensive Testing**: Tests the complete Bershka scraping workflow
- **Debug Output**: Detailed logging of each step
- **File Generation**: Creates screenshot, HTML, and JSON result files
- **Error Handling**: Robust error handling and reporting

### 2. Usage Instructions
```bash
# Test script çalıştırma
python test_bershka.py

# Çıktı dosyaları:
# - bershka_test_screenshot.png (sayfa görüntüsü)
# - bershka_test_page.html (sayfa HTML'i)
# - bershka_test_result.json (detaylı sonuçlar)
```

## Bershka-Specific Features

### 1. Bot Protection
- **Cookie Management**: Handles various cookie banner formats
- **Human Simulation**: Mouse movements and scrolling patterns
- **Extended Timeouts**: Longer wait times to avoid detection

### 2. Image Gallery Structure
- **Gallery Activation**: Attempts to activate image carousels
- **Multiple Image Sources**: Handles both main images and gallery images
- **Responsive Design**: Adapts to different screen sizes and layouts

### 3. Dynamic Content Loading
- **Lazy Loading**: Handles images that load on scroll
- **Network Idle Wait**: Ensures all content is loaded before extraction
- **Progressive Enhancement**: Multiple attempts with different strategies

## Troubleshooting Tips

### 1. If Images Still Not Found
1. **Check Screenshot**: Review `bershka_test_screenshot.png` for page state
2. **Analyze HTML**: Examine `bershka_test_page.html` for image elements
3. **Review JSON Results**: Check `bershka_test_result.json` for detailed findings
4. **Selector Updates**: Update selectors based on actual page structure

### 2. If Navigation Timeouts Persist
1. **Increase Timeouts**: Extend wait times in navigation functions
2. **Add Retry Logic**: Implement retry mechanism for failed navigation
3. **Proxy Rotation**: Consider using different IP addresses
4. **User Agent Rotation**: Try different browser user agents

### 3. Performance Optimization
1. **Memory Management**: Monitor memory usage during scraping
2. **Concurrent Limits**: Limit concurrent scraping operations
3. **Resource Cleanup**: Ensure proper browser cleanup after each operation

## Monitoring and Maintenance

### 1. Regular Testing
- Run `test_bershka.py` weekly to ensure functionality
- Monitor for changes in Bershka's website structure
- Update selectors as needed based on test results

### 2. Error Tracking
- Monitor logs for timeout and image extraction failures
- Track success rates over time
- Implement alerting for significant failure increases

### 3. Continuous Improvement
- Analyze successful vs failed scraping attempts
- Refine selectors based on real-world usage
- Optimize performance based on monitoring data

## Expected Results

After implementing these fixes, Bershka scraping should:
- ✅ Successfully navigate to product pages without timeouts
- ✅ Extract product images consistently
- ✅ Handle cookie banners and bot protection
- ✅ Provide detailed debug information for troubleshooting
- ✅ Maintain high success rates in production environment

## Next Steps

1. **Deploy Changes**: Deploy the updated code to Render
2. **Monitor Results**: Track success rates and error patterns
3. **Iterate**: Make additional improvements based on real-world performance
4. **Scale**: Apply similar patterns to other problematic brands
