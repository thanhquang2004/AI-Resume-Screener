"""Find actual job detail URLs from Playwright HTML."""
from bs4 import BeautifulSoup
import re

with open('/tmp/itviec_playwright.html') as f:
    soup = BeautifulSoup(f.read(), 'lxml')

cards = soup.find_all('div', class_=lambda x: x and 'job-card' in str(x))
print(f'Found {len(cards)} job cards\n')

uuid_pattern = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')

for i, card in enumerate(cards[:5]):
    print(f'=== Job {i+1} ===')
    
    # Title from h3
    title = card.find('h3')
    print(f'Title: {title.get_text(strip=True) if title else "N/A"}')
    
    # Company from link to /companies/
    company_link = card.find('a', href=lambda x: x and '/companies/' in str(x))
    if company_link:
        company = company_link.get_text(strip=True)
        print(f'Company: {company}')
    
    # Find ALL links and look for job detail URL (with UUID)
    all_links = card.find_all('a', href=True)
    for link in all_links:
        href = link.get('href', '')
        if '/it-jobs/' in href and uuid_pattern.search(href):
            print(f'Job URL (with UUID): {href[:80]}...')
            break
    else:
        # If no UUID link, look for sign_in link which has job param
        for link in all_links:
            href = link.get('href', '')
            if '/sign_in?job=' in href:
                # Extract job slug from sign_in URL
                import urllib.parse
                parsed = urllib.parse.urlparse(href)
                params = urllib.parse.parse_qs(parsed.query)
                job_slug = params.get('job', [''])[0]
                if job_slug:
                    print(f'Job slug from sign_in: {job_slug}')
                break
    
    # Salary
    salary_span = card.find('span', class_=lambda x: x and 'salary' in str(x).lower())
    if salary_span:
        print(f'Salary: {salary_span.get_text(strip=True)}')
    
    # Location - look for city names
    location_elem = card.find(text=lambda x: x and ('Ho Chi Minh' in str(x) or 'Ha Noi' in str(x) or 'Da Nang' in str(x)))
    if location_elem:
        print(f'Location: {location_elem.strip()[:50]}')
    
    print()

# Find ALL job links with UUIDs in the entire page
print('\n=== All Job URLs with UUIDs ===')
uuid_links = soup.find_all('a', href=lambda x: x and '/it-jobs/' in str(x) and uuid_pattern.search(str(x)))
for link in uuid_links[:10]:
    href = link.get('href', '')
    text = link.get_text(strip=True)[:50]
    print(f'{text}: {href[:100]}')
