"""
Other Tender Portals Scraper for HPCL B2B Leads
Scrapes TenderDetail, Tender247, eTenders portals
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import time
import sys
import os

# Import entity resolver
sys.path.insert(0, os.path.dirname(__file__))
try:
    from entity_resolver import enrich_entity
except:
    def enrich_entity(signal):
        return signal


TENDER_PORTALS = [
    "https://www.tenderdetail.com/global-tenders",
    "https://www.tenderdetail.com/india-tenders",
    "https://tender247.com/activerfp",
    "https://etenders.gov.in/eprocure/app",
]


class TenderPortalScraper:
    """Scraper for various tender portals"""
    
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
    
    def scrape_portal(self, url, portal_name):
        """Generic tender portal scraper"""
        results = []
        
        try:
            time.sleep(2)
            resp = self.session.get(url, timeout=20)
            
            if resp.status_code != 200:
                return results
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Multiple selector strategies
            tender_selectors = [
                "a[href*='tender']",
                "a[href*='bid']",
                "tr.tender",
                "tr.odd",
                "tr.even",
                "div.tender",
                "[class*='tender']",
                "[class*='bid']"
            ]
            
            tenders = []
            for selector in tender_selectors:
                found = soup.select(selector)
                tenders.extend(found)
                if len(tenders) >= 30:
                    break
            
            # Deduplicate
            tenders = list({str(t): t for t in tenders}.values())[:30]
            
            for tender_elem in tenders:
                try:
                    # Extract title and URL
                    if tender_elem.name == 'a':
                        title = tender_elem.get_text(strip=True)
                        href = tender_elem.get("href", "")
                    else:
                        link = tender_elem.find("a")
                        if not link:
                            continue
                        title = link.get_text(strip=True)
                        href = link.get("href", "")
                    
                    # Skip if title too short
                    if len(title) < 15:
                        continue
                    
                    # Make URL absolute
                    if href:
                        if href.startswith("http"):
                            tender_url = href
                        elif href.startswith("/"):
                            base_domain = url.split("/")[0] + "//" + url.split("/")[2]
                            tender_url = base_domain + href
                        else:
                            tender_url = url
                    else:
                        tender_url = url
                    
                    # Extract any dates
                    elem_text = tender_elem.get_text()
                    date_match = re.search(r'\d{1,2}[-/]\w{3,}[-/]\d{2,4}', elem_text)
                    post_date = date_match.group(0) if date_match else "Active Tender"
                    
                    # Extract contacts
                    emails, phones = self.extract_contacts(elem_text)
                    
                    # Create signal
                    signal = {
                        "Source": f"Tender-{portal_name}",
                        "Source_Governance": "public_tender",
                        "Signal_Type": "tender_opportunity",
                        "Title": f"TENDER: {title[:250]}",
                        "Summary": f"Tender opportunity from {portal_name}",
                        "URL": tender_url,
                        "Post_Date": post_date,
                        "Contact_Email": "; ".join(emails),
                        "Contact_Phone": "; ".join(phones),
                        "Captured_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Provenance": f"{portal_name}_Portal"
                    }
                    
                    signal = enrich_entity(signal)
                    results.append(signal)
                    
                except:
                    continue
                    
        except Exception as e:
            pass
        
        return results


def fetch_tender_portals():
    """
    Main function to fetch tender portal leads
    
    Returns:
        List of tender signal dictionaries
    """
    
    print("📋 Scraping Other Tender Portals...")
    scraper = TenderPortalScraper()
    all_results = []
    
    for i, url in enumerate(TENDER_PORTALS, 1):
        portal_name = url.split("/")[2].split(".")[0].upper()
        print(f"   Portal {i}/{len(TENDER_PORTALS)}: {portal_name[:20]}...", end=" ")
        
        try:
            results = scraper.scrape_portal(url, portal_name)
            all_results.extend(results)
            print(f"✅ {len(results)} tenders")
            
        except Exception as e:
            print(f"❌ Error")
            continue
    
    print(f"   ✅ {len(all_results)} total tenders")
    return all_results


if __name__ == "__main__":
    # Test
    print("🧪 Testing Tender Portals Scraper...")
    tenders = fetch_tender_portals()
    
    if tenders:
        print(f"\n📊 Sample Tender:")
        for key, value in list(tenders[0].items())[:10]:
            print(f"  {key}: {value}")
        print(f"\n✅ Total: {len(tenders)} tenders")
