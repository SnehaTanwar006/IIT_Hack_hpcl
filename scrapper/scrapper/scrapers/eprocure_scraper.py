"""
Enhanced eProcure Government Tender Scraper
Scrapes ALL pages from:
- https://eprocure.gov.in/cppp/latestactivetendersnew/cpppdata (31,000+ tenders)
- https://eprocure.gov.in/cppp/latestactivetendersnew/mmpdata
- https://eprocure.gov.in/cppp/latestactivetendersnew/gemdata
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
from urllib.parse import urljoin

class EProcureScraper:
    """Enhanced scraper for all eProcure portals with full pagination"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
        self.base_url = "https://eprocure.gov.in"
        
    def extract_contacts_from_text(self, text):
        """Extract emails and phones from text"""
        emails = list(set(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)))[:3]
        phones = list(set(re.findall(r'[\+]?[0-9][\s\-\()\d]{9,20}', text)))[:3]
        return emails, phones
    
    def extract_organization_details(self, org_text):
        """Extract organization name and hierarchy"""
        if not org_text:
            return "Unknown", ""
        
        # Split by common delimiters
        parts = re.split(r'\s*[\|,]\s*', org_text)
        primary_org = parts[0].strip() if parts else org_text[:100]
        
        return primary_org, org_text[:300]
    
    def parse_tender_row(self, row, source_name="CPPP"):
        """Parse a single tender row from the table"""
        try:
            cells = row.find_all("td")
            if len(cells) < 6:
                return None
            
            # Extract serial number
            sl_no = cells[0].get_text(strip=True).replace(".", "")
            
            # Extract dates
            e_published = cells[1].get_text(strip=True) or "N/A"
            closing_date = cells[2].get_text(strip=True) or "N/A"
            opening_date = cells[3].get_text(strip=True) or "N/A"
            
            # Extract title and tender link
            title_cell = cells[4]
            link_tag = title_cell.find("a")
            
            if not link_tag:
                return None
            
            title = link_tag.get_text(strip=True)
            tender_url = link_tag.get("href", "")
            
            # Make URL absolute
            if tender_url and not tender_url.startswith("http"):
                tender_url = urljoin(self.base_url, tender_url)
            
            # Extract reference numbers from title cell text
            full_title_text = title_cell.get_text(separator=" / ", strip=True)
            
            # Extract organization
            org_cell_text = cells[5].get_text(strip=True) if len(cells) > 5 else ""
            org_name, org_chain = self.extract_organization_details(org_cell_text)
            
            # Extract corrigendum
            corrigendum = cells[6].get_text(strip=True) if len(cells) > 6 else "--"
            
            # Try to extract contact info from the page (best effort)
            emails, phones = self.extract_contacts_from_text(org_cell_text + " " + title)
            
            return {
                "Serial_Number": sl_no,
                "Source": f"eProcure-{source_name}",
                "Source_Governance": "government_portal",
                "Signal_Type": "government_tender",
                "Title": f"{title[:300]}",
                "Full_Reference": full_title_text[:500],
                "Organization_Name": org_name[:200],
                "Organization_Chain": org_chain,
                "Summary": f"Tender by {org_name}",
                "URL": tender_url,
                "e_Published_Date": e_published,
                "Closing_Date": closing_date,
                "Opening_Date": opening_date,
                "Corrigendum": corrigendum,
                "Contact_Email": "; ".join(emails) if emails else "",
                "Contact_Phone": "; ".join(phones) if phones else "",
                "Captured_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Provenance": f"eProcure_{source_name}"
            }
            
        except Exception as e:
            print(f"    ⚠️ Row parse error: {str(e)[:50]}")
            return None
    
    def get_total_pages(self, soup):
        """Extract total number of pages from pagination"""
        try:
            # Look for pagination links
            pagination = soup.find("div", class_="pagination")
            if not pagination:
                return 1
            
            # Find all page links
            page_links = pagination.find_all("a", class_="paginate_button")
            if not page_links:
                return 1
            
            # Get the second-to-last link (last is usually "Next")
            page_numbers = []
            for link in page_links:
                text = link.get_text(strip=True)
                if text.isdigit():
                    page_numbers.append(int(text))
            
            return max(page_numbers) if page_numbers else 1
            
        except Exception as e:
            print(f"    ⚠️ Pagination parse error: {str(e)[:50]}")
            return 1
    
    def scrape_portal(self, portal_name, base_path, max_pages=None, delay=2.0):
        """
        Scrape a single eProcure portal with full pagination
        
        Args:
            portal_name: Name identifier (e.g., "CPPP", "MMP", "GEM")
            base_path: URL path (e.g., "/cppp/latestactivetendersnew/cpppdata")
            max_pages: Maximum pages to scrape (None = all pages)
            delay: Delay between requests in seconds
        """
        results = []
        base_url = self.base_url + base_path
        
        print(f"\n🏛️ SCRAPING: {portal_name} Portal")
        print(f"   URL: {base_url}")
        
        # Get first page to determine total pages
        try:
            print(f"   Fetching page 1...", end=" ", flush=True)
            resp = self.session.get(base_url, timeout=30)
            
            if resp.status_code != 200:
                print(f"❌ Failed (Status: {resp.status_code})")
                return results
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Get total pages
            total_pages = self.get_total_pages(soup)
            print(f"✅ Found {total_pages:,} pages")
            
            # Limit pages if specified
            if max_pages:
                total_pages = min(total_pages, max_pages)
                print(f"   ⚙️ Limited to {max_pages} pages")
            
            # Parse first page
            tender_rows = soup.find_all("tr", style=re.compile("border-bottom"))
            page_count = 0
            
            for row in tender_rows:
                tender = self.parse_tender_row(row, portal_name)
                if tender:
                    results.append(tender)
                    page_count += 1
            
            print(f"   Page 1: {page_count} tenders")
            
            # Scrape remaining pages
            for page_num in range(2, total_pages + 1):
                time.sleep(delay)  # Rate limiting
                
                page_url = f"{base_url}?page={page_num}"
                print(f"   Fetching page {page_num}/{total_pages}...", end=" ", flush=True)
                
                try:
                    resp = self.session.get(page_url, timeout=30)
                    
                    if resp.status_code != 200:
                        print(f"❌ Failed")
                        continue
                    
                    soup = BeautifulSoup(resp.text, "html.parser")
                    tender_rows = soup.find_all("tr", style=re.compile("border-bottom"))
                    
                    page_count = 0
                    for row in tender_rows:
                        tender = self.parse_tender_row(row, portal_name)
                        if tender:
                            results.append(tender)
                            page_count += 1
                    
                    print(f"✅ {page_count} tenders")
                    
                except Exception as e:
                    print(f"❌ Error: {str(e)[:50]}")
                    continue
            
            print(f"\n   ✅ {portal_name}: {len(results):,} total tenders scraped")
            
        except Exception as e:
            print(f"\n   ❌ Portal error: {str(e)[:100]}")
        
        return results
    
    def scrape_all_portals(self, max_pages_per_portal=10):
        """
        Scrape all three eProcure portals
        
        Args:
            max_pages_per_portal: Maximum pages per portal (None = all)
        """
        all_results = []
        
        portals = [
            ("CPPP", "/cppp/latestactivetendersnew/cpppdata"),
            ("MMP", "/cppp/latestactivetendersnew/mmpdata"),
            ("GEM", "/cppp/latestactivetendersnew/gemdata"),
        ]
        
        print("🚀 ePROCURE COMPREHENSIVE SCRAPER")
        print("=" * 60)
        
        for portal_name, portal_path in portals:
            portal_results = self.scrape_portal(
                portal_name, 
                portal_path, 
                max_pages=max_pages_per_portal,
                delay=2.0  # 2 second delay between requests
            )
            all_results.extend(portal_results)
            time.sleep(3)  # Extra delay between portals
        
        print("\n" + "=" * 60)
        print(f"✅ TOTAL SCRAPED: {len(all_results):,} tenders from all portals")
        
        return all_results


def fetch_eprocure_tenders(max_pages_per_portal=10):
    """
    Main function to fetch eProcure tenders
    
    Args:
        max_pages_per_portal: Max pages to scrape per portal (None = all pages, use with caution!)
    
    Returns:
        List of tender dictionaries
    """
    scraper = EProcureScraper()
    
    # For production: scrape limited pages
    # For full scrape: use max_pages_per_portal=None (will take hours!)
    results = scraper.scrape_all_portals(max_pages_per_portal=max_pages_per_portal)
    
    return results


if __name__ == "__main__":
    # Test scraper
    print("Testing eProcure Scraper...")
    tenders = fetch_eprocure_tenders(max_pages_per_portal=2)
    
    print(f"\n📊 Sample Tender:")
    if tenders:
        for key, value in list(tenders[0].items())[:10]:
            print(f"  {key}: {value}")
