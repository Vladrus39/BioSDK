"""Test DANDI Archive open API connectivity."""
import urllib.request
import json

try:
    r = urllib.request.urlopen('https://api.dandiarchive.org/api/dandisets/?page_size=3', timeout=15)
    data = json.loads(r.read())
    print(f"DANDI API OK")
    print(f"Total dandisets: {data.get('count', 'unknown')}")
    print(f"Results this page: {len(data.get('results', []))}")
    for ds in data.get('results', []):
        print(f"  - {ds.get('identifier', '?')}: {ds.get('name', '?')[:80]}")
except Exception as e:
    print(f"DANDI API FAILED: {type(e).__name__}: {e}")

# Also try OpenNeuro
try:
    r = urllib.request.urlopen('https://openneuro.org/api/datasets/?page_size=3', timeout=15)
    data = json.loads(r.read())
    print(f"\nOpenNeuro API OK")
    print(f"Total datasets: {data.get('totalCount', data.get('count', 'unknown'))}")
except Exception as e:
    print(f"\nOpenNeuro API FAILED: {type(e).__name__}: {e}")
