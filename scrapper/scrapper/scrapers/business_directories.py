"""
Business Directory Scraper for HPCL B2B Leads
Scrapes IndiaMART, TradeIndia, ExportersIndia for supplier contacts
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


# Directory URLs covering HPCL products
DIRECTORY_URLS = [
    # IndiaMART
    "https://dir.indiamart.com/search.mp?ss=high+speed+diesel",
    "https://dir.indiamart.com/search.mp?ss=HSD+supplier",
    "https://dir.indiamart.com/search.mp?ss=furnace+oil",
    "https://dir.indiamart.com/search.mp?ss=bitumen+supplier",
    "https://dir.indiamart.com/search.mp?ss=diesel+fuel",
    "https://dir.indiamart.com/search.mp?ss=industrial+fuel",
    "https://dir.indiamart.com/search.mp?ss=LDO+supplier",
    "https://dir.indiamart.com/search.mp?ss=marine+fuel",
    
    # TradeIndia
    "https://www.tradeindia.com/Seller/diesel-oil/",
    "https://www.tradeindia.com/Seller/furnace-oil/",
    "https://www.tradeindia.com/Seller/bitumen/",
    "https://www.tradeindia.com/Seller/industrial-fuel/",
    
    # ExportersIndia
    "https://www.exportersindia.com/indian-suppliers/diesel-fuel.htm",
    "https://www.exportersindia.com/indian-suppliers/furnace-oil.htm",
    "https://www.exportersindia.com/indian-suppliers/bitumen.htm",
]


class DirectoryScraper:
    """Scraper for business directories"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def extract_contacts(self, text):
        """Extract emails and phones from text"""
        emails = list(set(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)))[:3]
        phones = list(set(re.findall(r'[\+]?[0-9][\s\-\(\)]{0,3}[0-9]{9,15}', text)))[:3]
        
        # Clean phone numbers
        phones = [p.strip() for p in phones if len(p.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')) >= 10]
        
        return emails, phones
    
    def scrape_indiamart(self, url):
        """Scrape IndiaMART directory"""
        results = []
        
        try:
            time.sleep(2)
            resp = self.session.get(url, timeout=15)
            
            if resp.status_code != 200:
                return results
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Find company listings
            listings = soup.find_all("div", class_=lambda x: x and "company" in x.lower())[:20]
            
            if not listings:
                # Alternative selectors
                listings = soup.find_all("div", class_=lambda x: x and "listing" in x.lower())[:20]
            
            for listing in listings:
                try:
                    # Extract company name
                    name_tag = listing.find(["h2", "h3", "span"], class_=lambda x: x and ("name" in str(x).lower() or "title" in str(x).lower()))
                    
                    if not name_tag:
                        name_tag = listing.find("a")
                    
                    if not name_tag:
                        continue
                    
                    company_name = name_tag.get_text(strip=True)
                    
                    if len(company_name) < 3:
                        continue
                    
                    # Extract URL
                    link = listing.find("a")
                    company_url = link.get("href", url) if link else url
                    if company_url.startswith("/"):
                        company_url = "https://dir.indiamart.com" + company_url
                    
                    # Extract contacts
                    listing_text = listing.get_text()
                    emails, phones = self.extract_contacts(listing_text)
                    
                    # Create signal
                    signal = {
                        "Source": "IndiaMART",
                        "Source_Governance": "public_directory",
                        "Signal_Type": "directory_supplier",
                        "Title": f"Supplier: {company_name[:150]}",
                        "Summary": f"Industrial supplier from IndiaMART - {len(emails)} email(s), {len(phones)} phone(s)",
                        "Company_Name": company_name[:150],
                        "URL": company_url,
                        "Contact_Email": "; ".join(emails),
                        "Contact_Phone": "; ".join(phones),
                        "Post_Date": "Active Listing",
                        "Captured_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Provenance": "IndiaMART_Directory"
                    }
                    
                    signal = enrich_entity(signal)
                    results.append(signal)
                    
                except:
                    continue
                    
        except Exception as e:
            pass
        
        return results
    
    def scrape_tradeindia(self, url):
        """Scrape TradeIndia directory"""
        results = []
        
        try:
            time.sleep(2)
            resp = self.session.get(url, timeout=15)
            
            if resp.status_code != 200:
                return results
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Find company listings
            listings = soup.find_all(["div", "li"], class_=lambda x: x and ("seller" in str(x).lower() or "company" in str(x).lower()))[:20]
            
            for listing in listings:
                try:
                    # Extract company name
                    name_tag = listing.find(["h2", "h3", "a", "span"], class_=lambda x: x and "name" in str(x).lower())
                    
                    if not name_tag:
                        name_tag = listing.find("a")
                    
                    if not name_tag:
                        continue
                    
                    company_name = name_tag.get_text(strip=True)
                    
                    if len(company_name) < 3:
                        continue
                    
                    # Extract URL
                    link = listing.find("a")
                    company_url = link.get("href", url) if link else url
                    if company_url.startswith("/"):
                        company_url = "https://www.tradeindia.com" + company_url
                    
                    # Extract contacts
                    listing_text = listing.get_text()
                    emails, phones = self.extract_contacts(listing_text)
                    
                    signal = {
                        "Source": "TradeIndia",
                        "Source_Governance": "public_directory",
                        "Signal_Type": "directory_supplier",
                        "Title": f"Supplier: {company_name[:150]}",
                        "Summary": f"Industrial supplier from TradeIndia - {len(emails)} email(s), {len(phones)} phone(s)",
                        "Company_Name": company_name[:150],
                        "URL": company_url,
                        "Contact_Email": "; ".join(emails),
                        "Contact_Phone": "; ".join(phones),
                        "Post_Date": "Active Listing",
                        "Captured_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Provenance": "TradeIndia_Directory"
                    }
                    
                    signal = enrich_entity(signal)
                    results.append(signal)
                    
                except:
                    continue
                    
        except Exception as e:
            pass
        
        return results


def fetch_business_directories():
    """
    Main function to fetch business directory leads
    
    Returns:
        List of supplier signal dictionaries with contact information
    """
    
    print("🏢 Scraping Business Directories...")
    scraper = DirectoryScraper()
    all_results = []
    
    for i, url in enumerate(DIRECTORY_URLS, 1):
        print(f"   Directory {i}/{len(DIRECTORY_URLS)}: {url.split('/')[2][:20]}...", end=" ")
        
        try:
            if "indiamart" in url:
                results = scraper.scrape_indiamart(url)
            elif "tradeindia" in url:
                results = scraper.scrape_tradeindia(url)
            elif "exportersindia" in url:
                results = scraper.scrape_tradeindia(url)  # Similar structure
            else:
                results = []
            
            all_results.extend(results)
            print(f"✅ {len(results)} suppliers")
            
        except Exception as e:
            print(f"❌ Error")
            continue
    
    print(f"   ✅ {len(all_results)} total suppliers with contacts")
    return all_results


if __name__ == "__main__":
    # Test
    print("🧪 Testing Business Directory Scraper...")
    suppliers = fetch_business_directories()
    
    if suppliers:
        print(f"\n📊 Sample Supplier:")
        for key, value in list(suppliers[0].items())[:10]:
            print(f"  {key}: {value}")
        print(f"\n✅ Total: {len(suppliers)} suppliers")
