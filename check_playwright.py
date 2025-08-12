#!/usr/bin/env python3
"""
Playwright installation verification script
This script checks if Playwright browsers are properly installed and accessible.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_playwright_installation():
    """Check Playwright installation and browser availability"""
    print("🔍 Checking Playwright installation...")
    
    # Check environment variables
    browsers_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '/ms-playwright')
    print(f"📁 PLAYWRIGHT_BROWSERS_PATH: {browsers_path}")
    
    # Check if browsers directory exists
    browsers_dir = Path(browsers_path)
    if browsers_dir.exists():
        print(f"✅ Browsers directory exists: {browsers_dir}")
        
        # List contents
        print("📋 Directory contents:")
        for item in browsers_dir.iterdir():
            print(f"   - {item.name}")
            if item.is_dir():
                for subitem in item.iterdir():
                    print(f"     - {subitem.name}")
    else:
        print(f"❌ Browsers directory does not exist: {browsers_dir}")
    
    # Check for Chrome executable
    chrome_paths = list(browsers_dir.rglob("chrome"))
    if chrome_paths:
        print(f"✅ Chrome executable found at: {chrome_paths[0]}")
        
        # Check if executable
        if os.access(chrome_paths[0], os.X_OK):
            print("✅ Chrome executable is accessible")
        else:
            print("❌ Chrome executable is not accessible")
    else:
        print("❌ Chrome executable not found")
    
    # Try to import playwright
    try:
        from playwright.async_api import async_playwright
        print("✅ Playwright Python package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Playwright: {e}")
        return False
    
    # Try to start playwright
    try:
        import asyncio
        
        async def test_playwright():
            playwright = await async_playwright().start()
            print("✅ Playwright started successfully")
            
            # Try to launch browser
            try:
                browser = await playwright.chromium.launch(headless=True)
                print("✅ Chromium browser launched successfully")
                await browser.close()
            except Exception as e:
                print(f"❌ Failed to launch browser: {e}")
                return False
            
            await playwright.stop()
            return True
        
        result = asyncio.run(test_playwright())
        if result:
            print("✅ All Playwright tests passed!")
            return True
        else:
            print("❌ Playwright browser test failed")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test Playwright: {e}")
        return False

if __name__ == "__main__":
    success = check_playwright_installation()
    sys.exit(0 if success else 1)
