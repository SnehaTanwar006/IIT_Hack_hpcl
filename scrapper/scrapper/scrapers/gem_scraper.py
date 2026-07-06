"""
GeM (Government e-Marketplace) Portal Scraper
Scrapes bidplus.gem.gov.in for government procurement opportunities
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
import sys
import os

# Import entity resolver
sys.path.insert(0, os.path.dirname(__file__))
try:
    from entity_resolver import enrich_entity
except:
    def enrich_entity(signal):
        return signal


GEM_URLS = [
    "https://bidplus.gem.gov.in/all-bids",
    "https://bidplus.gem.gov.in/bidresultlists",
    "https://bidplus.gem.gov.in/all-bids?page=2",
    "https://bidplus.gem.gov.in/all-bids?page=3",
]


class GeMScraper:
    """Scraper for GeM (Government e-Marketplace)"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def extract_contacts(self, text):
        """Extract emails and phones from text"""
        emails = list(set(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)))[:2]
        phones = list(set(re.findall(r'[\+]?[0-9][\s\-\(\)]{0,3}[0-9]{9,15}', text)))[:2]
        return emails, phones
    
    def scrape_gem_page(self, url):
        """Scrape a GeM page for tenders"""
        results = []
        
        try:
            time.sleep(3)  # GeM rate limiting
            resp = self.session.get(url, timeout=25)
            
            if resp.status_code != 200:
                return results
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Find tender links
            all_links = soup.find_all("a", href=True)
            
            for link in all_links[:50]:
                try:
                    title = link.get_text(strip=True)
                    
                    # Skip navigation/menu links
                    if len(title) < 15:
                        continue
                    
                    # Skip non-tender links
                    if any(skip in title.lower() for skip in ['home', 'login', 'register', 'about', 'contact', 'help']):
                        continue
                    
                    href = link.get('href', '')
                    
                    # Make URL absolute
                    if href.startswith('/'):
                        gem_url = 'https://bidplus.gem.gov.in' + href
                    elif href.startswith('http'):
                        gem_url = href
                    else:
                        continue
                    
                    # Extract any organization from nearby text
                    parent_text = link.parent.get_text() if link.parent else title
                    
                    # Extract contacts
                    emails, phones = self.extract_contacts(parent_text)
                    
                    # Create signal
                    signal = {
                        "Source": "GeM",
                        "Source_Governance": "government_portal",
                        "Signal_Type": "gem_tender",
                        "Title": f"GeM Tender: {title[:200]}",
                        "Summary": "Government eMarketplace procurement opportunity",
                        "URL": gem_url,
                        "Post_Date": "Active",
                        "Contact_Email": "; ".join(emails),
                        "Contact_Phone": "; ".join(phones),
                        "Captured_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Provenance": "GeM_Portal",
                        "Source_Trust": 95
                    }
                    
                    signal = enrich_entity(signal)
                    results.append(signal)
                    
                except:
                    continue
                    
        except Exception as e:
            pass
        
        return results


def fetch_gem_tenders():
    """
    Main function to fetch GeM portal tenders
    
    Returns:
        List of tender signal dictionaries
    """
    
    print("🛒 Scraping GeM (Government e-Marketplace)...")
    scraper = GeMScraper()
    all_results = []
    
    for i, url in enumerate(GEM_URLS, 1):
        print(f"   GeM page {i}/{len(GEM_URLS)}...", end=" ")
        
        try:
            results = scraper.scrape_gem_page(url)
            all_results.extend(results)
            print(f"✅ {len(results)} tenders")
            
        except Exception as e:
            print(f"❌ Error")
            continue
    
    # Deduplicate by URL
    seen_urls = set()
    unique_results = []
    for result in all_results:
        if result['URL'] not in seen_urls:
            seen_urls.add(result['URL'])
            unique_results.append(result)
    
    print(f"   ✅ {len(unique_results)} unique GeM tenders")
    return unique_results


if __name__ == "__main__":
    # Test
    print("🧪 Testing GeM Scraper...")
    tenders = fetch_gem_tenders()
    
    if tenders:
        print(f"\n📊 Sample Tender:")
        for key, value in list(tenders[0].items())[:10]:
            print(f"  {key}: {value}")
        print(f"\n✅ Total: {len(tenders)} tenders")
