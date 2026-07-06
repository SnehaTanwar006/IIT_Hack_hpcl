"""
Enhanced Entity Resolution for HPCL B2B Lead Intelligence
Extracts company names and matches HPCL products
"""

import re

# HPCL Product Portfolio (as per problem statement)
HPCL_PRODUCTS = {
    # Industrial Fuels
    "HSD": ["HSD", "High Speed Diesel", "diesel fuel", "diesel", "gasoil"],
    "MS": ["MS", "motor spirit", "petrol", "gasoline"],
    "LDO": ["LDO", "Light Diesel Oil", "light diesel"],
    "FO": ["FO", "Furnace Oil", "furnace oil", "fuel oil"],
    "LSHS": ["LSHS", "Low Sulphur Heavy Stock", "low sulphur"],
    "SKO": ["SKO", "kerosene", "superior kerosene"],
    
    # Specialty Products
    "Bitumen": ["bitumen", "asphalt", "road tar"],
    "Hexane": ["hexane", "n-hexane"],
    "Solvent_1425": ["solvent 1425", "solvent-1425", "MTO 2445"],
    "Turpentine_Oil": ["turpentine oil", "MTO", "mineral turpentine", "turpentine"],
    "JBO": ["JBO", "Jute Batch Oil", "jute batching oil"],
    "Propylene": ["propylene", "propene"],
    "Sulphur": ["sulphur", "sulfur", "molten sulphur"],
    
    # Marine & Others
    "Marine_Bunker": ["bunker", "marine fuel", "shipping fuel", "bunker fuel"],
    "Aviation_Fuel": ["ATF", "aviation turbine fuel", "jet fuel"],
}

# Industry-to-Product mapping
INDUSTRY_PRODUCT_MAP = {
    "power": ["FO", "LSHS", "HSD", "LDO"],
    "textile": ["FO", "LSHS", "HSD"],
    "chemical": ["Hexane", "Solvent_1425", "Turpentine_Oil", "Propylene"],
    "fertilizer": ["FO", "LSHS", "HSD"],
    "steel": ["FO", "LSHS", "HSD"],
    "cement": ["FO", "LSHS", "HSD"],
    "shipping": ["Marine_Bunker", "HSD"],
    "marine": ["Marine_Bunker"],
    "road": ["Bitumen", "HSD"],
    "construction": ["Bitumen", "HSD"],
    "jute": ["JBO"],
    "aviation": ["Aviation_Fuel"],
    "mining": ["HSD", "LDO"],
}


def extract_company_name(text):
    """
    Extract company/organization name from text
    Enhanced to handle Indian company formats
    """
    if not text:
        return "Unknown Organization"
    
    # Strategy 1: Look for company suffixes
    patterns = [
        # Indian company formats
        r"([A-Z][A-Za-z\s&\-]{3,60}?)\s+(?:Ltd\.?|Limited|Pvt\.?\s*Ltd\.?|Private\s+Limited)",
        r"([A-Z][A-Za-z\s&\-]{3,60}?)\s+(?:Corporation|Corp\.?|Company|Co\.?)",
        
        # Government departments
        r"([A-Z][A-Za-z\s&\-]{3,60}?)\s+(?:Department|Ministry|Directorate|Authority|Board)",
        
        # PSUs and specific formats
        r"([A-Z][A-Za-z\s&\-]{3,60}?)\s+(?:India\s+Limited|Bharat|National|State)",
        
        # Action-based (tender awards)
        r"([A-Z][A-Z\s&\-]{3,50}?)\s+(?:bags|wins|secures|awarded|supplies)",
        
        # Well-known companies (abbreviations)
        r"\b(NTPC|IOCL|BPCL|HPCL|ONGC|GAIL|SAIL|BHEL|L&T|Tata|Adani|Reliance|JSW|Essar|Vedanta|Hindalco|UltraTech|ACC)\b",
    ]
    
    text_sample = text[:400]
    
    for pattern in patterns:
        match = re.search(pattern, text_sample, re.IGNORECASE)
        if match:
            company = match.group(1).strip()
            # Clean up
            company = re.sub(r'\s+', ' ', company)
            if 4 <= len(company) <= 100:
                return company.title()
    
    # Strategy 2: Extract from "Organisation Name" or "Organization Chain"
    org_patterns = [
        r"Organisation\s+Name[:\s]+(.*?)(?:[\n\|]|$)",
        r"Organization[:\s]+(.*?)(?:[\n\|]|$)",
        r"Org[:\s]+(.*?)(?:[\n\|]|$)",
        r"Posted\s+by[:\s]+(.*?)(?:[\n\|]|$)",
        r"Company[:\s]+(.*?)(?:[\n\|]|$)",
    ]
    
    for pattern in org_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            org = match.group(1).strip()
            # Take first part if multiple separated by ||
            org = org.split("||")[0].split("|")[0].strip()
            if len(org) > 4:
                return org[:100]
    
    # Strategy 3: First capitalized phrase
    first_cap_match = re.search(r'([A-Z][A-Za-z\s&\-]{10,60}?)(?:\s|$)', text_sample)
    if first_cap_match:
        return first_cap_match.group(1).strip()
    
    return "Unknown Organization"


def classify_products(text):
    """
    Classify HPCL products mentioned in text
    Returns comma-separated list of matched products
    """
    if not text:
        return "General Industrial"
    
    text_lower = text.lower()
    matched_products = []
    
    # Direct keyword matching
    for product, keywords in HPCL_PRODUCTS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                if product not in matched_products:
                    matched_products.append(product)
                break
    
    # If no direct match, try industry-based inference
    if not matched_products:
        for industry, products in INDUSTRY_PRODUCT_MAP.items():
            if industry in text_lower:
                matched_products.extend(products[:2])  # Add top 2 products
                break
    
    # Deduplicate and return
    matched_products = list(dict.fromkeys(matched_products))  # Preserve order
    
    return ", ".join(matched_products) if matched_products else "General Industrial"


def extract_location(text):
    """
    Extract location clues from text
    """
    if not text:
        return ""
    
    # Indian states and major cities
    locations = []
    
    location_patterns = [
        r'\b(Mumbai|Delhi|Bangalore|Bengaluru|Hyderabad|Chennai|Kolkata|Pune|Ahmedabad|Surat|Jaipur|Lucknow|Kanpur|Nagpur|Indore|Bhopal|Visakhapatnam|Vadodara|Coimbatore)\b',
        r'\b(Maharashtra|Gujarat|Karnataka|Tamil Nadu|Uttar Pradesh|Rajasthan|West Bengal|Madhya Pradesh|Andhra Pradesh|Telangana|Kerala|Punjab|Haryana|Bihar|Odisha|Jharkhand|Chhattisgarh)\b',
        r'\b(\w+)\s+(?:District|Dist\.?|City|State)\b',
    ]
    
    for pattern in location_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        locations.extend(matches)
    
    # Deduplicate and limit
    locations = list(dict.fromkeys(locations))[:5]
    
    return "; ".join(locations)


def enrich_entity(signal):
    """
    Main enrichment function
    Adds:
    - Company_Name
    - HPCL_Products (matched products)
    - HPCL_Keyword_Match (primary product)
    - Location_Clues
    """
    # Combine text for analysis
    combined_text = " ".join([
        str(signal.get("Title", "")),
        str(signal.get("Summary", "")),
        str(signal.get("Organization_Name", "")),
        str(signal.get("Organization_Chain", "")),
        str(signal.get("Full_Reference", ""))
    ])
    
    # Extract company if not already present
    if not signal.get("Company_Name") or signal.get("Company_Name") == "Unknown":
        signal["Company_Name"] = extract_company_name(combined_text)
    
    # Classify products
    products = classify_products(combined_text)
    signal["HPCL_Products"] = products
    
    # Primary product (first in list)
    primary_product = products.split(",")[0].strip() if products != "General Industrial" else "Tender"
    signal["HPCL_Keyword_Match"] = primary_product
    
    # Extract location
    signal["Location_Clues"] = extract_location(combined_text)
    
    return signal


if __name__ == "__main__":
    # Test cases
    test_signals = [
        {
            "Title": "Supply of High Speed Diesel for NTPC Power Plant",
            "Summary": "Tender for HSD supply",
            "Organization_Name": "NTPC Limited"
        },
        {
            "Title": "Bitumen supply for NH-44 road construction",
            "Summary": "NHAI tender for road construction materials",
            "Organization_Name": "National Highways Authority of India"
        },
        {
            "Title": "Marine bunker fuel supply at Mumbai Port",
            "Summary": "Shipping fuel requirement",
            "Organization_Name": "Mumbai Port Trust"
        }
    ]
    
    print("🧪 Testing Entity Resolver...\n")
    for i, signal in enumerate(test_signals, 1):
        enriched = enrich_entity(signal.copy())
        print(f"Test {i}:")
        print(f"  Company: {enriched['Company_Name']}")
        print(f"  Products: {enriched['HPCL_Products']}")
        print(f"  Primary: {enriched['HPCL_Keyword_Match']}")
        print()
