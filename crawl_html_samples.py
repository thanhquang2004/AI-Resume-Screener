#!/usr/bin/env python3
"""
HTML Sample Crawler
Crawl and save full HTML from LinkedIn, TopDev, and ITViec job listing pages.
Uses Playwright to bypass Cloudflare protection.
"""

import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright


SITES = {
    "linkedin": {
        "url": "https://www.linkedin.com/jobs/search?keywords=software%20engineer&location=Vietnam",
        "wait_selector": "div.jobs-search__results-list",
        "wait_time": 5000
    },
    "topdev": {
        "url": "https://topdev.vn/viec-lam-it",
        "wait_selector": "div.job-list",
        "wait_time": 5000
    },
    "itviec": {
        "url": "https://itviec.com/it-jobs",
        "wait_selector": "div.job-card",
        "wait_time": 5000
    }
}


async def crawl_site(page, name: str, config: dict, output_dir: str) -> dict:
    """Crawl a single site and save its HTML."""
    result = {
        "name": name,
        "url": config["url"],
        "success": False,
        "file_path": None,
        "error": None,
        "html_size": 0
    }
    
    try:
        print(f"\n{'='*60}")
        print(f"Crawling: {name.upper()}")
        print(f"URL: {config['url']}")
        print("="*60)
        
        # Navigate to the page
        print("Navigating to page...")
        await page.goto(config["url"], wait_until="domcontentloaded", timeout=60000)
        
        # Wait for content to load
        print(f"Waiting for content (selector: {config['wait_selector']})...")
        try:
            await page.wait_for_selector(config["wait_selector"], timeout=15000)
            print("Main content detected!")
        except Exception as e:
            print(f"Warning: Main selector not found, waiting for page to stabilize...")
        
        # Additional wait for dynamic content
        print(f"Waiting {config['wait_time']}ms for dynamic content...")
        await page.wait_for_timeout(config["wait_time"])
        
        # Scroll down to load more content
        print("Scrolling to load more content...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
        
        # Get the full HTML
        html_content = await page.content()
        result["html_size"] = len(html_content)
        print(f"HTML size: {len(html_content):,} bytes")
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_jobs_{timestamp}.html"
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        result["success"] = True
        result["file_path"] = file_path
        print(f"Saved to: {file_path}")
        
    except Exception as e:
        result["error"] = str(e)
        print(f"Error crawling {name}: {e}")
    
    return result


async def main():
    """Main crawling function."""
    output_dir = "/app/data/raw"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*60)
    print("JOB SITE HTML CRAWLER")
    print("="*60)
    print(f"Output directory: {output_dir}")
    print(f"Sites to crawl: {', '.join(SITES.keys())}")
    
    results = []
    
    async with async_playwright() as p:
        print("\nLaunching browser...")
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        for name, config in SITES.items():
            result = await crawl_site(page, name, config, output_dir)
            results.append(result)
        
        await browser.close()
    
    # Print summary
    print("\n" + "="*60)
    print("CRAWL SUMMARY")
    print("="*60)
    
    for r in results:
        status = "✓ SUCCESS" if r["success"] else "✗ FAILED"
        print(f"\n{r['name'].upper()}: {status}")
        if r["success"]:
            print(f"  File: {r['file_path']}")
            print(f"  Size: {r['html_size']:,} bytes")
        else:
            print(f"  Error: {r['error']}")
    
    # List saved files
    print("\n" + "="*60)
    print("SAVED FILES")
    print("="*60)
    
    for f in os.listdir(output_dir):
        if f.endswith(".html"):
            full_path = os.path.join(output_dir, f)
            size = os.path.getsize(full_path)
            print(f"  {f} ({size:,} bytes)")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
