import requests
import time
import random

class PolicySafeScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
    
    def safe_request(self, url, delay=2.0):
        time.sleep(random.uniform(delay, delay + 0.5))
        try:
            resp = self.session.get(url, timeout=20)
            return resp if resp.status_code == 200 else None
        except:
            return None
