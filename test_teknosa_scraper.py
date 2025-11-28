import asyncio
from scraper import fetch_data
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_teknosa():
    url = "https://www.teknosa.com/grundig-55gju7505-55-139-ekran-4k-uhd-smart-google-tv-p-110018133?shopId=teknosa"
    print(f"Testing Teknosa URL: {url}")
    
    result = await fetch_data(url)
    
    if result:
        print("\nScraping Successful!")
        print(f"Title: {result.get('title')}")
        print(f"Price: {result.get('price')}")
        print(f"Original Price: {result.get('original_price')}")
        print(f"Image: {result.get('image')}")
        print(f"Brand: {result.get('brand')}")
    else:
        print("\nScraping Failed!")

if __name__ == "__main__":
    asyncio.run(test_teknosa())
