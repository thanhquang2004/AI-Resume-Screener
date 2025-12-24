from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

opts = Options()
opts.add_argument('--headless')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=opts)

# Real ITViec job URL with UUID
url = "https://itviec.com/it-jobs/software-engineer-embedded-c-mcu-rtos-lg-electronics-development-vietnam-lgedv-5803-db80d8b5-7925-47dd-8e21-d92fd23bedcb"

print(f"Fetching REAL job URL...")
print(f"URL: {url[:90]}...")

driver.get(url)
time.sleep(10)

soup = BeautifulSoup(driver.page_source, 'lxml')

# Test different selectors
print("\n" + "="*80)
print("TESTING SELECTORS:")
print("="*80)

# Company
company = soup.find('div', class_=lambda x: x and 'company' in str(x).lower())
print(f"\n🏢 Company (div with 'company'): {company.get_text(strip=True)[:100] if company else 'NOT FOUND'}")

# Try h2 for company
h2s = soup.find_all('h2')
if h2s:
    print(f"   H2 tags found: {[h.get_text(strip=True)[:50] for h in h2s[:3]]}")

# Description
desc = soup.find('div', class_=lambda x: x and 'description' in str(x).lower())
print(f"\n📝 Description (div with 'description'): {len(desc.get_text(strip=True)) if desc else 0} chars")

# Try other description selectors
desc2 = soup.find('div', {'id': 'job-description'})
print(f"   By ID 'job-description': {len(desc2.get_text(strip=True)) if desc2 else 0} chars")

# Job divs
job_divs = soup.find_all('div', class_=lambda x: x and 'job' in str(x).lower())
print(f"\n🔍 Divs with 'job' in class: {len(job_divs)}")
if job_divs:
    for d in job_divs[:5]:
        classes = ' '.join(d.get('class', []))
        text_preview = d.get_text(strip=True)[:80]
        print(f"   - {classes}: {text_preview}")

# Save HTML for manual inspection
with open('/tmp/real_job_page.html', 'w') as f:
    f.write(driver.page_source)
print(f"\n💾 Saved HTML to /tmp/real_job_page.html")

driver.quit()
