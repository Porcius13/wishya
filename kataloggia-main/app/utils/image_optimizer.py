"""
Image Optimization Utilities
"""
import os
from urllib.parse import urlparse
import requests
from PIL import Image
import io

class ImageOptimizer:
    """Image optimization utilities"""
    
    @staticmethod
    def get_optimized_url(image_url, width=None, height=None, quality=80):
        """
        Optimize image URL (CDN support)
        For now, returns original URL
        Future: Integrate with Cloudinary/Imgix
        """
        # TODO: CDN integration
        # Example: return f"{CDN_URL}/w_{width},h_{height},q_{quality}/{image_url}"
        return image_url
    
    @staticmethod
    def is_valid_image_url(url):
        """Check if URL is a valid image"""
        if not url:
            return False
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        return any(path.endswith(ext) for ext in image_extensions)
    
    @staticmethod
    def get_image_dimensions(url):
        """Get image dimensions (async)"""
        try:
            response = requests.get(url, stream=True, timeout=5)
            response.raise_for_status()
            
            img = Image.open(io.BytesIO(response.content))
            return img.size  # (width, height)
        except Exception as e:
            print(f"Image dimension error: {e}")
            return None, None
    
    @staticmethod
    def generate_thumbnail_url(image_url, size='medium'):
        """Generate thumbnail URL"""
        sizes = {
            'small': (150, 150),
            'medium': (300, 300),
            'large': (600, 600)
        }
        
        width, height = sizes.get(size, (300, 300))
        return ImageOptimizer.get_optimized_url(image_url, width, height)

