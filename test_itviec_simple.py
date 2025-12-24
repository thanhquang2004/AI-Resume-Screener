#!/usr/bin/env python3
"""
Simple test to check what ITViec HTML looks like.
This helps identify the correct CSS selectors.
"""
import requests
from bs4 import BeautifulSoup

url = "https://itviec.com/it-jobs"
print(f"Fetching: {url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

response = requests.get(url, headers=headers, timeout=30)
print(f"Status: {response.status_code}")
print(f"Content length: {len(response.content)} bytes\n")

soup = BeautifulSoup(response.content, 'lxml')

# Save to file for inspection
with open('/tmp/itviec_simple.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())
print("Saved to /tmp/itviec_simple.html")

# Test common selectors
print("\n" + "="*60)
print("Testing selectors:")
print("="*60)

selectors = [
    ('div.job', 'Job divs'),
    ('div.job-card', 'Job cards'),
    ('article', 'Articles'),
    ('a[href*="/it-jobs/"]', 'Job links'),
    ('h3', 'H3 titles'),
    ('.itviec-job', 'ITViec job class'),
]

for selector, desc in selectors:
    elements = soup.select(selector)
    print(f"\n{desc} ({selector}): {len(elements)} found")
    if elements:
        print(f"  First element: {str(elements[0])[:200]}...")
