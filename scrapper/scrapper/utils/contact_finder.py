"""
Contact Enrichment Module
Fetches actual tender/company pages to extract contact information
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def extract_contacts_from_text(text):
    """Extract emails and phones from text"""
    # Email pattern
    emails = list(set(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)))[:3]
    
    # Phone pattern (Indian and international)
    phones = list(set(re.findall(r'[\+]?[0-9][\s\-\(\)]{0,3}[0-9]{9,15}', text)))[:3]
    
    # Clean phones
    cleaned_phones = []
    for phone in phones:
        # Remove formatting
        clean = re.sub(r'[\s\-\(\)]', '', phone)
        # Must be 10-15 digits
        if 10 <= len(clean) <= 15:
            cleaned_phones.append(phone)
    
    return emails, cleaned_phones[:3]


def fetch_page_contacts(url, timeout=10):
    """Fetch a URL and extract contacts"""
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        resp = session.get(url, timeout=timeout)
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Get visible text
            text = soup.get_text()
            
            # Extract contacts
            emails, phones = extract_contacts_from_text(text)
            
            return emails, phones
        
    except:
        pass
    
    return [], []


def enrich_signal_contacts(signal):
    """Enrich a single signal with contact info from its URL"""
    
    # Skip if already has contacts
    if signal.get("Contact_Email") and signal.get("Contact_Phone"):
        return signal
    
    # Get URL
    url = signal.get("URL", "")
    if not url or not url.startswith("http"):
        return signal
    
    # Fetch and extract
    emails, phones = fetch_page_contacts(url, timeout=8)
    
    # Update signal
    if emails and not signal.get("Contact_Email"):
        signal["Contact_Email"] = "; ".join(emails)
    
    if phones and not signal.get("Contact_Phone"):
        signal["Contact_Phone"] = "; ".join(phones)
    
    return signal


def enrich_contacts(signals, max_workers=5, max_enrich=100):
    """
    Enrich signals with contact information by fetching their URLs
    
    Args:
        signals: List of signal dictionaries
        max_workers: Number of parallel workers
        max_enrich: Maximum signals to enrich (to avoid long waits)
    
    Returns:
        List of enriched signals
    """
    
    print("   📞 Enhanced Contact Enrichment...")
    
    # Find signals without contacts
    needs_enrichment = [
        s for s in signals 
        if (not s.get("Contact_Email") or not s.get("Contact_Phone")) 
        and s.get("URL", "").startswith("http")
    ][:max_enrich]
    
    if not needs_enrichment:
        print("   ✅ All signals already have contacts")
        return signals
    
    print(f"   Enriching {len(needs_enrichment)} signals (max {max_enrich})...")
    
    enriched_count = 0
    
    # Process in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_signal = {
            executor.submit(enrich_signal_contacts, signal): signal 
            for signal in needs_enrichment
        }
        
        # Process completed tasks
        for i, future in enumerate(as_completed(future_to_signal), 1):
            try:
                enriched_signal = future.result()
                
                # Check if contacts were added
                original_signal = future_to_signal[future]
                if (enriched_signal.get("Contact_Email") and not original_signal.get("Contact_Email")) or \
                   (enriched_signal.get("Contact_Phone") and not original_signal.get("Contact_Phone")):
                    enriched_count += 1
                
                # Update in original list
                signal_index = signals.index(original_signal)
                signals[signal_index] = enriched_signal
                
                # Progress
                if i % 20 == 0:
                    print(f"   Progress: {i}/{len(needs_enrichment)} ({enriched_count} enriched)")
                    
            except Exception as e:
                continue
    
    print(f"   ✅ Enriched {enriched_count} signals with new contacts")
    
    return signals


if __name__ == "__main__":
    # Test
    test_signals = [
        {
            "Title": "Test Tender",
            "URL": "https://eprocure.gov.in/cppp/",
            "Contact_Email": "",
            "Contact_Phone": ""
        }
    ]
    
    print("🧪 Testing Contact Enrichment...")
    enriched = enrich_contacts(test_signals, max_enrich=1)
    
    print("\nResult:")
    print(f"Email: {enriched[0].get('Contact_Email', 'None')}")
    print(f"Phone: {enriched[0].get('Contact_Phone', 'None')}")
