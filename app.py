"""
Vercel deployment entry point
Flask uygulaması için Vercel serverless function
"""
import sys
import os

# Add kataloggia-main/kataloggia-main directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
kataloggia_dir = os.path.join(current_dir, 'kataloggia-main')
sys.path.insert(0, kataloggia_dir)

try:
    from app import create_app
    
    # Create app without database initialization for Vercel
    # Note: Database operations are disabled, using localStorage on frontend instead
    app = create_app('production')
    
    # Vercel expects the app object
    
except ImportError as e:
    print(f"[ERROR] Import hatası: {e}")
    import traceback
    traceback.print_exc()
    # Fallback minimal app
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return 'Wishya App - Deployment in progress. Check logs for import errors.'

# Export for Vercel
if __name__ == "__main__":
    app.run(debug=True)

