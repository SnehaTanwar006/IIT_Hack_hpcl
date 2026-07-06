"""
Signal Enrichment Module
Fetches URLs, extracts contacts, enriches metadata
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import sys
import os

# Import registry
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
try:
    from registry import get_source_metadata, get_rate_limit
except:
    def get_rate_limit(source):
        return 2.0


def extract_contacts_from_html(html_text):
    """
    Extract emails and phones from HTML text
    
    Args:
        html_text: HTML content as string
    
    Returns:
        Tuple of (emails, phones)
    """
    
    # Email pattern
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    emails = list(set(re.findall(email_pattern, html_text)))[:5]
    
    # Phone pattern (Indian and international)
    phone_pattern = r'[\+]?[0-9][\s\-\(\)]{0,3}[0-9]{9,15}'
    phones = list(set(re.findall(phone_pattern, html_text)))
    
    # Clean and validate phones
    cleaned_phones = []
    for phone in phones:
        # Remove formatting
        clean = re.sub(r'[\s\-\(\)]', '', phone)
        # Must be 10-15 digits
        if 10 <= len(clean) <= 15 and clean.isdigit() or (clean.startswith('+') and clean[1:].isdigit()):
            cleaned_phones.append(phone.strip())
    
    return emails, cleaned_phones[:5]


def extract_location_from_html(html_text):
    """
    Extract Indian location mentions from HTML
    
    Args:
        html_text: HTML content as string
    
    Returns:
        List of location strings
    """
    
    locations = []
    
    # Indian states
    states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
    ]
    
    # Major cities
    cities = [
        "Mumbai", "Delhi", "Bangalore", "Bengaluru", "Hyderabad", "Ahmedabad",
        "Chennai", "Kolkata", "Surat", "Pune", "Jaipur", "Lucknow", "Kanpur",
        "Nagpur", "Indore", "Thane", "Bhopal", "Visakhapatnam", "Pimpri", "Patna",
        "Vadodara", "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad",
        "Meerut", "Rajkot", "Kalyan", "Vasai", "Varanasi", "Srinagar", "Aurangabad",
        "Dhanbad", "Amritsar", "Navi Mumbai", "Allahabad", "Ranchi", "Howrah",
        "Coimbatore", "Jabalpur", "Gwalior", "Vijayawada", "Jodhpur", "Madurai"
    ]
    
    # Search for states
    for state in states:
        if state.lower() in html_text.lower():
            locations.append(state)
    
    # Search for cities
    for city in cities:
        if re.search(r'\b' + re.escape(city) + r'\b', html_text, re.IGNORECASE):
            locations.append(city)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_locations = []
    for loc in locations:
        if loc not in seen:
            seen.add(loc)
            unique_locations.append(loc)
    
    return unique_locations[:10]


def fetch_and_enrich_from_url(url, source_name="Unknown", timeout=10):
    """
    Fetch URL and extract enrichment data
    
    Args:
        url: URL to fetch
        source_name: Source identifier for rate limiting
        timeout: Request timeout in seconds
    
    Returns:
        Dictionary with extracted data
    """
    
    enrichment = {
        "contacts_found": False,
        "emails": [],
        "phones": [],
        "locations": [],
        "additional_text": ""
    }
    
    if not url or not url.startswith("http"):
        return enrichment
    
    try:
        # Rate limiting based on source
        rate_limit = get_rate_limit(source_name)
        time.sleep(rate_limit)
        
        # Fetch URL
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        response = session.get(url, timeout=timeout)
        
        if response.status_code == 200:
            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Get text content
            text_content = soup.get_text()
            
            # Extract contacts
            emails, phones = extract_contacts_from_html(text_content)
            
            # Extract locations
            locations = extract_location_from_html(text_content)
            
            # Get page title for additional context
            title_tag = soup.find("title")
            page_title = title_tag.get_text(strip=True) if title_tag else ""
            
            # Update enrichment
            enrichment["contacts_found"] = bool(emails or phones)
            enrichment["emails"] = emails
            enrichment["phones"] = phones
            enrichment["locations"] = locations
            enrichment["additional_text"] = page_title[:200]
            
    except Exception as e:
        pass
    
    return enrichment


def enrich_with_contacts(signal):
    """
    Enrich a single signal by fetching its URL
    
    Args:
        signal: Signal dictionary
    
    Returns:
        Enriched signal dictionary
    """
    
    # Skip if already has good contacts
    if signal.get("Contact_Email") and signal.get("Contact_Phone"):
        return signal
    
    # Get URL and source
    url = signal.get("URL", "")
    source = signal.get("Source", "Unknown")
    
    # Fetch and enrich
    enrichment = fetch_and_enrich_from_url(url, source)
    
    # Update signal with new data
    if enrichment["contacts_found"]:
        # Add emails if missing
        if not signal.get("Contact_Email") and enrichment["emails"]:
            signal["Contact_Email"] = "; ".join(enrichment["emails"])
        
        # Add phones if missing
        if not signal.get("Contact_Phone") and enrichment["phones"]:
            signal["Contact_Phone"] = "; ".join(enrichment["phones"])
    
    # Add locations if missing
    if not signal.get("Location_Clues") and enrichment["locations"]:
        signal["Location_Clues"] = "; ".join(enrichment["locations"])
    
    # Add page title to summary if very short
    if len(str(signal.get("Summary", ""))) < 50 and enrichment["additional_text"]:
        current_summary = signal.get("Summary", "")
        signal["Summary"] = f"{current_summary} | Page: {enrichment['additional_text']}"
    
    return signal


def enrich_signals_batch(signals, max_signals=100, parallel=False):
    """
    Enrich multiple signals with contact information
    
    Args:
        signals: List of signal dictionaries
        max_signals: Maximum signals to enrich (to control runtime)
        parallel: Use parallel processing (not implemented yet)
    
    Returns:
        List of enriched signals
    """
    
    print(f"   🔍 Enriching signals (max {max_signals})...")
    
    # Find signals that need enrichment
    needs_enrichment = [
        s for s in signals
        if (not s.get("Contact_Email") or not s.get("Contact_Phone"))
        and s.get("URL", "").startswith("http")
    ][:max_signals]
    
    if not needs_enrichment:
        print("   ✅ All signals already enriched")
        return signals
    
    print(f"   Processing {len(needs_enrichment)} signals...")
    
    enriched_count = 0
    
    for i, signal in enumerate(needs_enrichment, 1):
        try:
            # Find signal in original list
            signal_index = signals.index(signal)
            
            # Enrich
            enriched_signal = enrich_with_contacts(signal)
            
            # Check if actually enriched
            if (enriched_signal.get("Contact_Email") and not signal.get("Contact_Email")) or \
               (enriched_signal.get("Contact_Phone") and not signal.get("Contact_Phone")):
                enriched_count += 1
            
            # Update in list
            signals[signal_index] = enriched_signal
            
            # Progress
            if i % 10 == 0:
                print(f"   Progress: {i}/{len(needs_enrichment)} ({enriched_count} enriched)")
                
        except Exception as e:
            continue
    
    print(f"   ✅ Enriched {enriched_count} signals with new data")
    
    return signals


if __name__ == "__main__":
    # Test signal enrichment
    test_signal = {
        "Source": "eProcure_CPPP",
        "Title": "Test Tender",
        "URL": "https://eprocure.gov.in",
        "Contact_Email": "",
        "Contact_Phone": "",
        "Location_Clues": ""
    }
    
    print("🧪 Testing Signal Enrichment...\n")
    print("Before:")
    print(f"  Email: {test_signal.get('Contact_Email', 'None')}")
    print(f"  Phone: {test_signal.get('Contact_Phone', 'None')}")
    print(f"  Location: {test_signal.get('Location_Clues', 'None')}")
    
    enriched = enrich_with_contacts(test_signal)
    
    print("\nAfter:")
    print(f"  Email: {enriched.get('Contact_Email', 'None')}")
    print(f"  Phone: {enriched.get('Contact_Phone', 'None')}")
    print(f"  Location: {enriched.get('Location_Clues', 'None')}")
