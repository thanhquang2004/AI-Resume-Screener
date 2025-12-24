"""
Test Playwright with stealth mode to bypass Cloudflare.
Uses the default browser path.
"""
from playwright.sync_api import sync_playwright
import time

print("=" * 80)
print("TESTING PLAYWRIGHT CLOUDFLARE BYPASS (Stealth Mode)")
print("=" * 80)

with sync_playwright() as p:
    # Launch with more stealth options
    browser = p.chromium.launch(
        headless=True,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-infobars',
            '--disable-background-networking',
            '--disable-breakpad',
            '--disable-component-update',
            '--no-first-run',
            '--disable-default-apps',
        ]
    )
    
    # Create context with very realistic settings
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale='vi-VN',  # Vietnamese locale for ITViec
        timezone_id='Asia/Ho_Chi_Minh',  # Vietnam timezone
        geolocation={'longitude': 106.6297, 'latitude': 10.8231},  # Ho Chi Minh City
        permissions=['geolocation'],
        color_scheme='light',
        has_touch=False,
        is_mobile=False,
        java_script_enabled=True,
    )
    
    # Add stealth scripts to hide automation
    context.add_init_script("""
        // Overwrite navigator.webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Overwrite plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
                {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                {name: 'Native Client', filename: 'internal-nacl-plugin'}
            ]
        });
        
        // Overwrite languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['vi-VN', 'vi', 'en-US', 'en']
        });
        
        // Hide automation detection
        window.chrome = {
            runtime: {}
        };
        
        // Remove Playwright/Selenium traces
        delete window.__playwright;
        delete window.__selenium_evaluate;
        delete window.__webdriver_script_fn;
    """)
    
    page = context.new_page()
    
    # Navigate to ITViec
    url = "https://itviec.com/it-jobs?q=python"
    print(f"\n🔍 Loading: {url}")
    
    try:
        # Go to page
        response = page.goto(url, wait_until='domcontentloaded', timeout=60000)
        print(f"✅ Initial load - Status: {response.status if response else 'N/A'}")
        print(f"   Title: {page.title()}")
        
        # Wait for Cloudflare challenge (it usually takes 5-10 seconds)
        print("\n⏳ Waiting for Cloudflare challenge (20 seconds)...")
        
        for i in range(4):  # Check every 5 seconds
            time.sleep(5)
            title = page.title()
            content = page.content()
            
            print(f"   Check {i+1}: Title = '{title[:50]}'")
            
            if "Just a moment" not in title and "cloudflare" not in content.lower()[:1000]:
                print(f"   ✅ Cloudflare passed!")
                break
            else:
                print(f"   ⏳ Still on Cloudflare...")
        
        # Final check
        content = page.content()
        title = page.title()
        
        print(f"\n📄 Final state:")
        print(f"   Title: {title}")
        print(f"   Content length: {len(content)} chars")
        
        # Check for Cloudflare
        if "Just a moment" in content or "Verify you are human" in content:
            print("   ❌ Still blocked by Cloudflare")
        else:
            print("   ✅ Cloudflare bypassed!")
            
            # Look for job links
            job_links = page.query_selector_all('a[href*="/it-jobs/"]')
            print(f"\n🔗 Found {len(job_links)} job links")
            
            if len(job_links) > 0:
                print("\n📋 Sample jobs found:")
                for i, link in enumerate(job_links[:10]):
                    href = link.get_attribute('href') or ''
                    text = link.inner_text().strip()[:60]
                    if '/it-jobs/' in href and text:
                        print(f"   {i+1}. {text}")
                        print(f"      URL: {href[:80]}")
        
        # Save HTML for inspection
        with open('/tmp/itviec_playwright.html', 'w') as f:
            f.write(content)
        print(f"\n💾 Saved HTML to: /tmp/itviec_playwright.html")
        
        # Print text sample
        text_content = page.inner_text('body')[:800]
        print(f"\n📝 Page text sample:")
        print(text_content)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        browser.close()

print("\n" + "=" * 80)
print("PLAYWRIGHT TEST COMPLETE")
print("=" * 80)
