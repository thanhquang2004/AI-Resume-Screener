#!/usr/bin/env python3
"""
Debug script to inspect ITViec HTML structure.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def inspect_itviec():
    """Inspect ITViec page structure."""
    print("Initializing Chrome WebDriver...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        url = "https://itviec.com/it-jobs?q=python"
        print(f"\nFetching: {url}")
        driver.get(url)
        
        print("Waiting for page to load...")
        time.sleep(5)
        
        # Save page source
        with open('/tmp/itviec_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("Page source saved to /tmp/itviec_page.html")
        
        soup = BeautifulSoup(driver.page_source, 'lxml')
        
        # Try different selectors
        print("\n" + "="*60)
        print("Testing different selectors:")
        print("="*60)
        
        selectors_to_test = [
            ("div.job", "div with class 'job'"),
            ("div.job-item", "div with class 'job-item'"),
            ("div[data-job-id]", "div with data-job-id attribute"),
            ("article", "article tags"),
            (".job-list .job", ".job-list .job"),
            (".jobs-list .job", ".jobs-list .job"),
            ("div.job-card", "div with class 'job-card'"),
            (".search-result", "elements with class 'search-result'"),
            ("a[href*='/it-jobs/']", "links containing '/it-jobs/'"),
        ]
        
        for selector, description in selectors_to_test:
            elements = soup.select(selector)
            print(f"\n{description}: {len(elements)} found")
            if elements and len(elements) > 0:
                print(f"  First element classes: {elements[0].get('class', [])}")
                print(f"  First element id: {elements[0].get('id', 'N/A')}")
                # Print first 200 chars of element
                elem_str = str(elements[0])[:200]
                print(f"  Preview: {elem_str}...")
        
        # Look for common job-related patterns
        print("\n" + "="*60)
        print("Searching for job-related patterns:")
        print("="*60)
        
        # Find all divs with 'job' in class name
        job_divs = soup.find_all('div', class_=lambda x: x and 'job' in x.lower())
        print(f"\nDivs with 'job' in class name: {len(job_divs)}")
        if job_divs:
            for i, div in enumerate(job_divs[:3]):
                print(f"\n  Div {i+1} classes: {div.get('class', [])}")
        
        # Find all links that might be job postings
        job_links = soup.find_all('a', href=lambda x: x and '/it-jobs/' in x)
        print(f"\nLinks with '/it-jobs/' in href: {len(job_links)}")
        if job_links:
            for i, link in enumerate(job_links[:5]):
                print(f"  Link {i+1}: {link.get('href', 'N/A')[:80]}")
                print(f"    Text: {link.get_text(strip=True)[:60]}")
        
        # Look for h3 tags (often used for job titles)
        h3_tags = soup.find_all('h3')
        print(f"\nH3 tags found: {len(h3_tags)}")
        if h3_tags:
            for i, h3 in enumerate(h3_tags[:5]):
                print(f"  H3 {i+1} classes: {h3.get('class', [])}")
                print(f"    Text: {h3.get_text(strip=True)[:60]}")
        
        print("\n" + "="*60)
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        print("="*60)
        
    finally:
        driver.quit()
        print("\nWebDriver closed")

if __name__ == "__main__":
    try:
        inspect_itviec()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
