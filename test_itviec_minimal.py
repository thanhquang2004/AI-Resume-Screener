"""Minimal test to see what ITViec actually returns"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Setup Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)

try:
    print("Fetching ITViec...")
    driver.get("https://itviec.com/it-jobs/python")
    time.sleep(5)
    
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    # Find all links
    all_links = soup.find_all('a', href=True)
    job_links = [l for l in all_links if '/it-jobs/' in l.get('href', '')]
    
    print(f"\n✅ Found {len(job_links)} links with /it-jobs/\n")
    
    for i, link in enumerate(job_links[:10], 1):
        href = link.get('href', '')
        text = link.get_text(strip=True)[:80]
        parts = [p for p in href.split('/') if p and p != 'it-jobs']
        print(f"{i}. URL parts: {len(parts)}")
        print(f"   {href}")
        print(f"   Text: \"{text}\"")
        print()
        
finally:
    driver.quit()
