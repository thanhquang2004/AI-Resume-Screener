import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

print("Testing undetected-chromedriver...")

options = uc.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')

print("Initializing undetected Chrome...")
driver = uc.Chrome(options=options, version_main=None, use_subprocess=True)

# Test real ITViec job URL with UUID
url = "https://itviec.com/it-jobs/software-engineer-embedded-c-mcu-rtos-lg-electronics-development-vietnam-lgedv-5803-db80d8b5-7925-47dd-8e21-d92fd23bedcb"

print(f"Fetching: {url[:80]}...")
driver.get(url)
time.sleep(15)  # Wait for Cloudflare challenge to complete

soup = BeautifulSoup(driver.page_source, 'lxml')

# Check if Cloudflare blocked us
if "Just a moment" in driver.page_source or "Cloudflare" in driver.page_source:
    print("\n❌ STILL BLOCKED BY CLOUDFLARE")
    print("Page title:", soup.find('title').get_text() if soup.find('title') else "No title")
else:
    print("\n✅ BYPASSED CLOUDFLARE!")
    
    # Check for actual job content
    h1 = soup.find('h1')
    print(f"\n🏢 H1 tag: {h1.get_text(strip=True)[:100] if h1 else 'NOT FOUND'}")
    
    h2s = soup.find_all('h2')
    if h2s:
        print(f"\n📋 H2 tags found: {len(h2s)}")
        for i, h2 in enumerate(h2s[:5]):
            print(f"  {i+1}. {h2.get_text(strip=True)[:60]}")
    
    # Check for job divs
    job_divs = soup.find_all('div', class_=lambda x: x and 'job' in str(x).lower())
    print(f"\n🔍 Divs with 'job': {len(job_divs)}")
    
    # Save HTML
    with open('/tmp/undetected_job_page.html', 'w') as f:
        f.write(driver.page_source)
    print(f"\n💾 Saved to /tmp/undetected_job_page.html")

driver.quit()
