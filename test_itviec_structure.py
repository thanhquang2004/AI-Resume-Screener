#!/usr/bin/env python3
"""
Quick test to see ITViec's actual HTML structure
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Setup Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    # Load ITViec Python jobs
    url = "https://itviec.com/it-jobs/python"
    print(f"Loading: {url}")
    driver.get(url)
    time.sleep(5)  # Wait for JS to load
    
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    # Find ALL links with /it-jobs/
    all_job_links = soup.find_all('a', href=lambda x: x and '/it-jobs/' in x)
    print(f"\n=== Found {len(all_job_links)} links with '/it-jobs/' ===\n")
    
    # Categorize them
    navigation_links = []
    real_job_links = []
    
    for link in all_job_links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        # Count path segments
        parts = [p for p in href.split('/') if p and p != 'it-jobs' and '?' not in p]
        
        if len(parts) == 1:  # Single segment = category
            navigation_links.append((href, text))
        elif len(parts) >= 2:  # Multiple segments = likely real job
            real_job_links.append((href, text))
    
    print(f"Navigation links ({len(navigation_links)}):")
    for href, text in navigation_links[:10]:
        print(f"  {href[:60]:<60} | {text[:40]}")
    
    print(f"\nReal job links ({len(real_job_links)}):")
    for href, text in real_job_links[:10]:
        print(f"  {href[:80]:<80} | {text[:50]}")
    
    # Now let's see what parent containers look like
    if real_job_links:
        print("\n=== Analyzing first real job link parent structure ===")
        first_job_link = soup.find('a', href=lambda x: x and real_job_links[0][0] in str(x))
        if first_job_link:
            parent = first_job_link.find_parent('div')
            if parent:
                print(f"Parent classes: {parent.get('class', [])}")
                print(f"Parent text (first 200 chars): {parent.get_text(strip=True)[:200]}")
                
                # Look for company info
                company_elem = parent.find(text=lambda x: x and 'company' in str(x).lower())
                print(f"Found company element: {company_elem}")
finally:
    driver.quit()
    print("\nDone!")
