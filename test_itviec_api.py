"""
Test if ITViec has a JSON API endpoint we can use instead of HTML scraping.
Check common API patterns used by job boards.
"""
import requests
import json

# Test various potential API endpoints
test_urls = [
    # Common API patterns
    "https://itviec.com/api/v1/jobs",
    "https://itviec.com/api/jobs",
    "https://itviec.com/api/v1/search",
    "https://api.itviec.com/jobs",
    "https://api.itviec.com/v1/jobs",
    
    # Search/filter patterns
    "https://itviec.com/api/v1/jobs/search?q=python",
    "https://itviec.com/api/jobs/search?keyword=python",
    "https://itviec.com/rails/active_storage/blobs",  # Check Rails backend
    
    # GraphQL endpoint
    "https://itviec.com/graphql",
    "https://api.itviec.com/graphql",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://itviec.com/it-jobs',
}

print("=" * 80)
print("TESTING ITVIEC API ENDPOINTS")
print("=" * 80)

for url in test_urls:
    print(f"\n🔍 Testing: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            print(f"   Content-Type: {content_type}")
            
            # Check if JSON
            if 'json' in content_type:
                try:
                    data = response.json()
                    print(f"   ✅ JSON Response! Keys: {list(data.keys())[:10]}")
                    print(f"   Preview: {json.dumps(data, indent=2)[:500]}...")
                    
                    # Save full response
                    filename = url.split('/')[-1].replace('?', '_') + '.json'
                    with open(f'/tmp/itviec_api_{filename}', 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"   💾 Saved to: /tmp/itviec_api_{filename}")
                except Exception as e:
                    print(f"   ⚠️ Not valid JSON: {e}")
            else:
                print(f"   Response length: {len(response.text)} chars")
                if len(response.text) < 500:
                    print(f"   Content: {response.text}")
        elif response.status_code == 403:
            print(f"   ⚠️ Forbidden - Cloudflare blocking")
        elif response.status_code == 404:
            print(f"   ❌ Not found")
        else:
            print(f"   ⚠️ Status {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"   ⏱️ Timeout")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print("API ENDPOINT DISCOVERY COMPLETE")
print("=" * 80)

# Also test if we can get job data from a known job URL
print("\n🔍 Testing direct job URL (might reveal API pattern)...")
job_url = "https://itviec.com/it-jobs/python-developer"
try:
    response = requests.get(job_url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    # Look for API calls in the HTML
    if 'api' in response.text.lower():
        import re
        api_patterns = re.findall(r'(https?://[^\s"\'<>]+api[^\s"\'<>]+)', response.text)
        if api_patterns:
            print(f"✅ Found API references in HTML:")
            for pattern in set(api_patterns[:10]):
                print(f"   - {pattern}")
except Exception as e:
    print(f"Error: {e}")
