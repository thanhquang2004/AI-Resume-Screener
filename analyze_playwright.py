"""Analyze ITViec HTML structure from Playwright output."""
from bs4 import BeautifulSoup

with open('/tmp/itviec_playwright.html') as f:
    soup = BeautifulSoup(f.read(), 'lxml')

cards = soup.find_all('div', class_=lambda x: x and 'job-card' in str(x))
print(f'Found {len(cards)} job cards')

if cards:
    card = cards[0]
    print('\n=== First Job Card ===')
    
    title = card.find('h3')
    print(f'Title: {title.get_text(strip=True)[:80] if title else "NOT FOUND"}')
    
    # Find all links
    print('\n=== Links in card ===')
    links = card.find_all('a')
    for link in links[:5]:
        href = link.get('href', '')
        text = link.get_text(strip=True)[:50]
        print(f'Link: {text} -> {href[:60]}')
    
    # Find all spans
    print('\n=== Spans in card ===')
    spans = card.find_all('span')
    for span in spans[:10]:
        text = span.get_text(strip=True)[:50]
        classes = ' '.join(span.get('class', []))
        if text:
            print(f'Span [{classes}]: {text}')

print('\n=== Sample Job URLs ===')
job_links = soup.find_all('a', href=lambda x: x and '/it-jobs/' in str(x) and len(str(x)) > 40)
for link in job_links[:5]:
    href = link.get('href', '')
    text = link.get_text(strip=True)[:60]
    print(f'{text}')
    print(f'  -> {href}')
