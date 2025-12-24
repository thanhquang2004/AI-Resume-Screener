"""Test fetching a real ITViec job detail page"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)

# Use a real ITViec job URL (this is an example - you need to find a current one)
test_urls = [
    "https://itviec.com/it-jobs/senior-python-developer",
    "https://itviec.com/it-jobs/backend-developer", 
    "https://itviec.com/it-jobs/python-developer"
]

for url in test_urls:
    try:
        print(f"\n{'='*80}")
        print(f"Testing: {url}")
        print('='*80)
        
        driver.get(url)
        time.sleep(8)  # Wait for page load
        
        soup = BeautifulSoup(driver.page_source, 'lxml')
        
        # Try to find company
        print("\n🏢 COMPANY:")
        company_selectors = [
            ('div', {'class': lambda x: x and 'company' in str(x).lower()}),
            ('h1', {}),
            ('a', {'class': lambda x: x and 'company' in str(x).lower()}),
        ]
        for tag, attrs in company_selectors:
            elem = soup.find(tag, attrs)
            if elem:
                print(f"  Found with <{tag}>: {elem.get_text(strip=True)[:100]}")
                break
        
        # Try to find description
        print("\n📝 DESCRIPTION:")
        desc = soup.find('div', class_=lambda x: x and 'description' in str(x).lower())
        if desc:
            text = desc.get_text(strip=True)[:200]
            print(f"  Length: {len(desc.get_text(strip=True))} chars")
            print(f"  Preview: {text}...")
        else:
            print("  ❌ Not found")
            
        # Check for any divs with class containing 'job'
        print("\n🔍 ALL DIVS WITH 'job' in class:")
        job_divs = soup.find_all('div', class_=lambda x: x and 'job' in str(x).lower())
        for div in job_divs[:5]:
            classes = div.get('class', [])
            print(f"  - {' '.join(classes)}")
            
        # Save full HTML for inspection
        filename = f"/tmp/itviec_detail_{url.split('/')[-1]}.html"
        with open(filename, 'w') as f:
            f.write(driver.page_source)
        print(f"\n💾 Saved to: {filename}")
        
        break  # Only test first URL that loads
        
    except Exception as e:
        print(f"❌ Error: {e}")
        continue

driver.quit()
