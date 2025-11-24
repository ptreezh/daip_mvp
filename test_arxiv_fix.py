import sys
sys.path.insert(0, './src')

import asyncio
from daip_live.doc.tools.paper_downloader import PaperDownloader

async def test_arxiv_fix():
    print("Testing fixed arXiv functionality...")
    
    downloader = PaperDownloader()
    
    # Test 1: Search for a common topic
    print("\n1. Testing search for 'machine learning'...")
    try:
        results = await downloader.search_papers("machine learning", max_results=2)
        print(f"   Found {len(results)} papers")
        if results:
            print(f"   First paper: {results[0].title[:100]}...")
        else:
            print("   No papers found (might be normal due to API limits)")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Try to download a known paper (if available)
    print("\n2. Testing download for 'quantum computing'...")
    try:
        result = await downloader.download_paper_by_topic("quantum computing", source=downloader.__class__.__annotations__.get('source', None))
        print(f"   Success: {result.success}")
        print(f"   Title: {result.title[:100]}..." if result.success else f"   Error: {result.error_message}")
    except Exception as e:
        print(f"   Error: {e}")
        
    # Test 3: Test with an actual arXiv ID if we know one
    print("\n3. Testing with a specific arXiv ID (if available)...")
    try:
        # Using a well-known arXiv ID
        result = await downloader._download_from_arxiv_by_id("2107.05580", asyncio.get_event_loop().time())
        print(f"   Success: {result.success}")
        if not result.success and "arXiv library not available" in result.error_message:
            print("   This indicates arXiv library is not available in test environment")
        else:
            print(f"   Title: {result.title[:100]}..." if result.success else f"   Error: {result.error_message}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\nTest completed.")

if __name__ == "__main__":
    asyncio.run(test_arxiv_fix())