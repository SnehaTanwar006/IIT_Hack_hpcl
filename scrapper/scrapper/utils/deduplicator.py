"""
Enhanced Deduplicator with Source Trust Scoring
Removes duplicates while preserving highest-quality data
"""

import hashlib
import sys
import os

# Import registry
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
try:
    from registry import get_source_metadata, get_trust_score
except:
    def get_trust_score(source):
        return 50


def generate_signal_hash(signal):
    """
    Generate hash from title + URL for duplicate detection
    
    Args:
        signal: Signal dictionary
    
    Returns:
        MD5 hash string
    """
    title = str(signal.get("Title", "")).strip().lower()
    url = str(signal.get("URL", "")).strip().lower()
    
    # Normalize URLs (remove trailing slashes, http/https differences)
    url = url.rstrip('/').replace('https://', '').replace('http://', '')
    
    combined = title + url
    return hashlib.md5(combined.encode()).hexdigest()


def merge_signals(existing, new):
    """
    Merge two duplicate signals, keeping best data from each
    
    Args:
        existing: Existing signal dictionary
        new: New signal dictionary
    
    Returns:
        Merged signal with best data from both
    """
    
    # Get trust scores
    existing_trust = get_trust_score(existing.get("Source", ""))
    new_trust = get_trust_score(new.get("Source", ""))
    
    # Start with higher-trust source as base
    if new_trust > existing_trust:
        merged = new.copy()
        fallback = existing
    else:
        merged = existing.copy()
        fallback = new
    
    # Merge contact information (take non-empty values)
    if not merged.get("Contact_Email") and fallback.get("Contact_Email"):
        merged["Contact_Email"] = fallback["Contact_Email"]
    
    if not merged.get("Contact_Phone") and fallback.get("Contact_Phone"):
        merged["Contact_Phone"] = fallback["Contact_Phone"]
    
    # Merge company name (take non-"Unknown")
    if merged.get("Company_Name") in ["Unknown", "Unknown Organization", ""] and fallback.get("Company_Name"):
        if fallback.get("Company_Name") not in ["Unknown", "Unknown Organization"]:
            merged["Company_Name"] = fallback["Company_Name"]
    
    # Merge organization info
    if not merged.get("Organization_Name") and fallback.get("Organization_Name"):
        merged["Organization_Name"] = fallback["Organization_Name"]
    
    if not merged.get("Organization_Chain") and fallback.get("Organization_Chain"):
        merged["Organization_Chain"] = fallback["Organization_Chain"]
    
    # Merge product info (combine unique products)
    existing_products = set(merged.get("HPCL_Products", "").split(","))
    new_products = set(fallback.get("HPCL_Products", "").split(","))
    all_products = existing_products.union(new_products)
    all_products = {p.strip() for p in all_products if p.strip() and p.strip() != "General Industrial"}
    
    if all_products:
        merged["HPCL_Products"] = ", ".join(sorted(all_products))
    
    # Merge location clues
    existing_locs = set(merged.get("Location_Clues", "").split(";"))
    new_locs = set(fallback.get("Location_Clues", "").split(";"))
    all_locs = existing_locs.union(new_locs)
    all_locs = {loc.strip() for loc in all_locs if loc.strip()}
    
    if all_locs:
        merged["Location_Clues"] = "; ".join(sorted(all_locs))
    
    # Add duplicate source note
    if "Duplicate_Sources" not in merged:
        merged["Duplicate_Sources"] = f"{existing.get('Source', '')}; {new.get('Source', '')}"
    else:
        if new.get('Source', '') not in merged["Duplicate_Sources"]:
            merged["Duplicate_Sources"] += f"; {new.get('Source', '')}"
    
    return merged


def deduplicate(signals):
    """
    Enhanced deduplication with smart merging
    
    Args:
        signals: List of signal dictionaries
    
    Returns:
        List of unique signals with merged data
    """
    
    if not signals:
        return []
    
    seen_hashes = {}
    unique_signals = []
    duplicate_count = 0
    
    for signal in signals:
        # Generate hash
        signal_hash = generate_signal_hash(signal)
        
        if signal_hash in seen_hashes:
            # Duplicate found - merge with existing
            existing_index = seen_hashes[signal_hash]
            existing_signal = unique_signals[existing_index]
            
            # Merge signals
            merged_signal = merge_signals(existing_signal, signal)
            unique_signals[existing_index] = merged_signal
            
            duplicate_count += 1
            
        else:
            # New unique signal
            seen_hashes[signal_hash] = len(unique_signals)
            unique_signals.append(signal)
    
    print(f"   Deduplication: {len(signals):,} → {len(unique_signals):,} ({duplicate_count:,} duplicates merged)")
    
    return unique_signals


def deduplicate_by_category(signals_dict):
    """
    Deduplicate signals organized by category
    
    Args:
        signals_dict: Dictionary of {category_name: [signals]}
    
    Returns:
        Dictionary of deduplicated signals by category
    """
    
    deduplicated = {}
    
    for category, signals in signals_dict.items():
        deduplicated[category] = deduplicate(signals)
    
    return deduplicated


if __name__ == "__main__":
    # Test deduplicator
    test_signals = [
        {
            "Source": "eProcure_CPPP",
            "Title": "Supply of HSD Diesel",
            "URL": "https://example.com/tender/123",
            "Company_Name": "NTPC Limited",
            "Contact_Email": "",
            "HPCL_Products": "HSD"
        },
        {
            "Source": "GoogleNews",
            "Title": "Supply of HSD Diesel",
            "URL": "https://example.com/tender/123",
            "Company_Name": "Unknown",
            "Contact_Email": "info@ntpc.co.in",
            "HPCL_Products": "Diesel"
        },
        {
            "Source": "GeM",
            "Title": "Different Tender",
            "URL": "https://example.com/tender/456",
            "Company_Name": "BHEL",
            "HPCL_Products": "FO"
        }
    ]
    
    print("🧪 Testing Enhanced Deduplicator...\n")
    print(f"Input: {len(test_signals)} signals")
    
    unique = deduplicate(test_signals)
    
    print(f"\nOutput: {len(unique)} unique signals")
    print("\nMerged Signal:")
    if unique:
        for key, value in unique[0].items():
            if value:
                print(f"  {key}: {value}")
