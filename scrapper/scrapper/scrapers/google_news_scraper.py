"""
Enhanced Google News Scraper for HPCL B2B Leads
Searches for industrial fuel, tender, and procurement news across India
"""

import feedparser
from datetime import datetime
import sys
import os

# Import entity resolver
sys.path.insert(0, os.path.dirname(__file__))
try:
    from entity_resolver import enrich_entity
except:
    def enrich_entity(signal):
        return signal


# Comprehensive query list covering all HPCL products and industries
NEWS_QUERIES = [
    # HSD & Diesel
    "HSD diesel tender India",
    "High Speed Diesel supply India",
    "diesel procurement India",
    "diesel fuel contract India",
    "industrial diesel tender",
    
    # Furnace Oil & LSHS
    "furnace oil tender India",
    "LSHS tender India",
    "low sulphur fuel India",
    "boiler fuel procurement",
    "industrial furnace oil",
    
    # Bitumen & Road Construction
    "bitumen tender India",
    "NHAI bitumen tender",
    "road construction bitumen",
    "asphalt supply India",
    "highway bitumen contract",
    
    # LDO
    "LDO tender India",
    "Light Diesel Oil India",
    "boiler diesel tender",
    
    # Power & Energy
    "power plant fuel tender India",
    "captive power fuel",
    "genset fuel procurement",
    "DG set fuel India",
    
    # Marine & Shipping
    "marine bunker fuel India",
    "shipping fuel tender",
    "port bunker supply",
    "vessel fuel India",
    
    # Specialty Chemicals
    "hexane supply India",
    "solvent procurement India",
    "industrial solvent tender",
    "turpentine oil India",
    
    # Industry-Specific
    "textile industry fuel tender",
    "steel plant fuel procurement",
    "cement plant fuel India",
    "fertilizer plant fuel",
    "chemical industry fuel",
    
    # General Industrial
    "industrial fuel tender India",
    "bulk fuel supply India",
    "petroleum products tender",
    "fuel supply contract India",
    "industrial energy tender",
]


def fetch_google_news():
    """
    Fetch news leads from Google News RSS
    
    Returns:
        List of news signal dictionaries with enriched company and product info
    """
    
    print("📰 Fetching Google News (30+ queries)...")
    results = []
    successful_queries = 0
    
    for i, query in enumerate(NEWS_QUERIES, 1):
        try:
            # Build RSS URL
            url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-IN&gl=IN"
            
            # Parse RSS feed
            feed = feedparser.parse(url)
            
            # Extract entries
            count = 0
            for entry in feed.entries[:5]:  # Top 5 per query
                try:
                    # Create base signal
                    signal = {
                        "Source": "GoogleNews",
                        "Source_Governance": "public_RSS",
                        "Signal_Type": "news_lead",
                        "Title": entry.title[:300],
                        "Summary": entry.get("summary", entry.get("description", ""))[:500],
                        "URL": entry.link,
                        "Post_Date": entry.get("published", datetime.now().strftime("%Y-%m-%d"))[:20],
                        "Captured_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Contact_Email": "",
                        "Contact_Phone": "",
                        "Provenance": f"GoogleNews_RSS_{query[:30]}"
                    }
                    
                    # Enrich with company and product info
                    signal = enrich_entity(signal)
                    
                    results.append(signal)
                    count += 1
                    
                except Exception as e:
                    continue
            
            if count > 0:
                successful_queries += 1
                
            # Progress indicator
            if i % 10 == 0:
                print(f"   Progress: {i}/{len(NEWS_QUERIES)} queries ({len(results)} leads)")
                
        except Exception as e:
            continue
    
    print(f"   ✅ {len(results)} news leads from {successful_queries} queries")
    return results


if __name__ == "__main__":
    # Test
    print("🧪 Testing Google News Scraper...")
    leads = fetch_google_news()
    
    if leads:
        print(f"\n📊 Sample Lead:")
        for key, value in list(leads[0].items())[:8]:
            print(f"  {key}: {value}")
        print(f"\n✅ Total: {len(leads)} leads")
