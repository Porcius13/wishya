import asyncio
from scraper import fetch_data

async def main():
    # Test URL
    url = "https://www.adidas.com.tr/tr/real-madrid-24-25-ucuncu-forma/IY1763.html"
    print(f"Testing URL: {url}")
    
    try:
        result = await fetch_data(url)
        
        if result:
            print("\nSuccess! Data extracted:")
            print(f"Title: {result.get('title')}")
            print(f"Price: {result.get('price')}")
            print(f"Image: {result.get('image_url')}")
            print(f"Brand: {result.get('brand')}")
            print(f"Description: {result.get('description')}")
        else:
            print("\nFailed to extract data.")
            
    except Exception as e:
        print(f"\nError occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
