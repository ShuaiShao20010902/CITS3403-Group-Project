# run from terminal using python3 static/tests/test_latency.py
# This script tests the latency of Open Library's API endpoint by sending a GET request and measuring the time taken to receive a response.

import requests
import time

API_URL = 'https://openlibrary.org/search.json'
PARAMS = {'q': 'romance', 'limit': 10}
TIMEOUT = 10  # seconds

def measure_latency():
    try:
        start = time.time()
        resp = requests.get(API_URL, params=PARAMS, timeout=TIMEOUT)
        elapsed = time.time() - start
        resp.raise_for_status()
        print(f"Request completed in {elapsed:.2f} seconds (status: {resp.status_code})")
    except requests.exceptions.Timeout:
        print(f"Request timed out after {TIMEOUT} seconds")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == '__main__':
    measure_latency()
