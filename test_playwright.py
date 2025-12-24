"""
Test Playwright with stealth mode to bypass Cloudflare.
Playwright often works better than Selenium for Cloudflare bypass.
"""
from playwright.sync_api import sync_playwright
import time

print("=" * 80)
print("TESTING PLAYWRIGHT CLOUDFLARE BYPASS")
print("=" * 80)

with sync_playwright() as p:
    # Launch browser with stealth settings
    browser = p.chromium.launch(
        headless=True,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-dev-shm-usage',
        ]
    )
    
    # Create context with realistic settings
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale='en-US',
        timezone_id='America/New_York',
    )
    
    page = context.new_page()
    
    # Try to load ITViec
    url = "https://itviec.com/it-jobs?q=python"
    print(f"\n🔍 Loading: {url}")
    
    try:
        page.goto(url, wait_until='networkidle', timeout=60000)
        print(f"✅ Page loaded: {page.title()}")
        
        # Wait for Cloudflare challenge
        print("⏳ Waiting 15 seconds for Cloudflare challenge...")
        time.sleep(15)
        
        # Check page content
        content = page.content()
        print(f"\n📄 Page content length: {len(content)} chars")
        
        # Check for Cloudflare
        if "Just a moment" in content or "cloudflare" in content.lower():
            print("⚠️ Still on Cloudflare challenge page")
            
            # Wait longer
            print("⏳ Waiting another 15 seconds...")
            time.sleep(15)
            content = page.content()
            
            if "Just a moment" in content:
                print("❌ Cloudflare bypass FAILED")
            else:
                print("✅ Cloudflare bypass SUCCESS!")
        else:
            print("✅ No Cloudflare detected!")
        
        # Look for job links
        job_links = page.query_selector_all('a[href*="/it-jobs/"]')
        print(f"\n🔗 Found {len(job_links)} job links")
        
        if len(job_links) > 0:
            print("\n📋 Sample job links:")
            for link in job_links[:10]:
                href = link.get_attribute('href')
                text = link.inner_text()[:50]
                print(f"   - {href}: {text}")
        
        # Save HTML for inspection
        with open('/tmp/itviec_playwright.html', 'w') as f:
            f.write(content)
        print(f"\n💾 Saved HTML to: /tmp/itviec_playwright.html")
        
        # Print text sample
        text = page.inner_text('body')
        print(f"\n📝 Page text sample (first 500 chars):")
        print(text[:500])
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        browser.close()

print("\n" + "=" * 80)
print("PLAYWRIGHT TEST COMPLETE")
print("=" * 80)
