from bs4 import BeautifulSoup

with open('/tmp/itviec_page1.html', 'r') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')
    
links = soup.find_all('a', href=lambda x: x and '/it-jobs/' in x)
print(f'\nFound {len(links)} links with /it-jobs/\n')

for i, link in enumerate(links[:20]):
    href = link.get('href', '')
    text = link.get_text(strip=True)[:80]
    parts = [p for p in href.split('/') if p and p != 'it-jobs']
    print(f'{i+1}. Parts={len(parts)}: {href}')
    print(f'   Text: "{text}"')
    if parts:
        print(f'   Segments: {parts}')
    print()
