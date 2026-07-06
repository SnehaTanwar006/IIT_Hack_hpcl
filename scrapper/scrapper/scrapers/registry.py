"""
Central Source Registry
Controls trust, crawl rules, and metadata for all intelligence sources
"""

SOURCE_REGISTRY = {
    # eProcure Government Portals
    "eProcure_CPPP": {
        "domains": ["eprocure.gov.in"],
        "full_url": "https://eprocure.gov.in/cppp/latestactivetendersnew/cpppdata",
        "category": "government_tender",
        "access_method": "scrape",
        "allowed_crawl_frequency_hours": 24,
        "rate_limit_seconds": 2.0,
        "trust_score": 98,
        "governance": "government",
        "robots_txt": "allowed",
        "description": "Central Public Procurement Portal - CPPP Data"
    },

    "eProcure_MMP": {
        "domains": ["eprocure.gov.in"],
        "full_url": "https://eprocure.gov.in/cppp/latestactivetendersnew/mmpdata",
        "category": "government_tender",
        "access_method": "scrape",
        "allowed_crawl_frequency_hours": 24,
        "rate_limit_seconds": 2.0,
        "trust_score": 98,
        "governance": "government",
        "robots_txt": "allowed",
        "description": "Make in India Portal - MMP Data"
    },

    "eProcure_GEMData": {
        "domains": ["eprocure.gov.in"],
        "full_url": "https://eprocure.gov.in/cppp/latestactivetendersnew/gemdata",
        "category": "government_tender",
        "access_method": "scrape",
        "allowed_crawl_frequency_hours": 24,
        "rate_limit_seconds": 2.0,
        "trust_score": 98,
        "governance": "government",
        "robots_txt": "allowed",
        "description": "GeM Data Portal (via eProcure)"
    },

    "GeM": {
        "domains": ["bidplus.gem.gov.in", "gem.gov.in"],
        "full_url": "https://bidplus.gem.gov.in/all-bids",
        "category": "government_tender",
        "access_method": "scrape",
        "allowed_crawl_frequency_hours": 12,
        "rate_limit_seconds": 3.0,
        "trust_score": 96,
        "governance": "government",
        "robots_txt": "allowed",
        "description": "Government e-Marketplace"
    },

    "GoogleNews": {
        "domains": ["news.google.com"],
        "full_url": "https://news.google.com/rss/search",
        "category": "news",
        "access_method": "rss",
        "allowed_crawl_frequency_hours": 6,
        "rate_limit_seconds": 1.0,
        "trust_score": 75,
        "governance": "aggregator",
        "robots_txt": "allowed",
        "description": "Google News RSS Feeds"
    },

    "IndiaMART": {
        "domains": ["dir.indiamart.com"],
        "full_url": "https://dir.indiamart.com/search.mp",
        "category": "business_directory",
        "access_method": "scrape",
        "allowed_crawl_frequency_hours": 168,  # 1 week
        "rate_limit_seconds": 2.0,
        "trust_score": 88,
        "governance": "private",
        "robots_txt": "allowed",
        "description": "IndiaMART Business Directory"
    },

    "TradeIndia": {
        "domains": ["www.tradeindia.com"],
        "full_url": "https://www.tradeindia.com/Seller/",
        "category": "business_directory",
        "access_method": "scrape",
        "allowed_crawl_frequency_hours": 168,
        "rate_limit_seconds": 2.0,
        "trust_score": 85,
        "governance": "private",
        "robots_txt": "allowed",
        "description": "TradeIndia Business Directory"
    },

    "ExportersIndia": {
        "domains": ["www.exportersindia.com"],
        "full_url": "https://www.exportersindia.com/indian-suppliers/",
        "category": "business_directory",
        "access_method": "scrape",
        "allowed_crawl_frequency_hours": 168,
        "rate_limit_seconds": 2.0,
        "trust_score": 82,
        "governance": "private",
        "robots_txt": "allowed",
        "description": "ExportersIndia Business Directory"
    },

    "TenderDetail": {
        "domains": ["www.tenderdetail.com"],
        "full_url": "https://www.tenderdetail.com/global-tenders",
        "category": "tender_portal",
        "access_method": "scrape",
        "allowed_crawl_frequency_hours": 24,
        "rate_limit_seconds": 2.0,
        "trust_score": 92,
        "governance": "private",
        "robots_txt": "allowed",
        "description": "TenderDetail Tender Portal"
    },

    "Tender247": {
        "domains": ["tender247.com"],
        "full_url": "https://tender247.com/activerfp",
        "category": "tender_portal",
        "access_method": "scrape",
        "allowed_crawl_frequency_hours": 24,
        "rate_limit_seconds": 2.0,
        "trust_score": 80,
        "governance": "private",
        "robots_txt": "allowed",
        "description": "Tender247 Portal"
    },

    "eTenders": {
        "domains": ["etenders.gov.in"],
        "full_url": "https://etenders.gov.in/eprocure/app",
        "category": "government_tender",
        "access_method": "scrape",
        "allowed_crawl_frequency_hours": 24,
        "rate_limit_seconds": 2.0,
        "trust_score": 95,
        "governance": "government",
        "robots_txt": "allowed",
        "description": "National e-Procurement Portal"
    },
}


def get_source_metadata(source_name):
    """
    Fetch registry metadata safely
    
    Args:
        source_name: Source identifier (e.g., "eProcure_CPPP", "GeM")
    
    Returns:
        Dictionary with source metadata, or defaults if not found
    """
    return SOURCE_REGISTRY.get(source_name, {
        "domains": [],
        "category": "unknown",
        "access_method": "unknown",
        "allowed_crawl_frequency_hours": 24,
        "rate_limit_seconds": 2.0,
        "trust_score": 50,
        "governance": "unknown",
        "robots_txt": "unknown",
        "description": "Unknown Source"
    })


def get_all_sources_by_category(category):
    """
    Get all sources in a specific category
    
    Args:
        category: One of: government_tender, news, business_directory, tender_portal
    
    Returns:
        Dictionary of sources in that category
    """
    return {
        name: metadata 
        for name, metadata in SOURCE_REGISTRY.items() 
        if metadata.get("category") == category
    }


def get_rate_limit(source_name):
    """Get rate limit for a source in seconds"""
    metadata = get_source_metadata(source_name)
    return metadata.get("rate_limit_seconds", 2.0)


def get_trust_score(source_name):
    """Get trust score for a source (0-100)"""
    metadata = get_source_metadata(source_name)
    return metadata.get("trust_score", 50)


def get_governance_type(source_name):
    """Get governance type: government, private, aggregator, unknown"""
    metadata = get_source_metadata(source_name)
    return metadata.get("governance", "unknown")


if __name__ == "__main__":
    # Test registry
    print("📊 SOURCE REGISTRY TEST\n")
    
    print("All Sources:")
    for source_name in SOURCE_REGISTRY.keys():
        meta = get_source_metadata(source_name)
        print(f"  {source_name:20} | Trust: {meta['trust_score']:3} | {meta['category']:20} | {meta['governance']}")
    
    print("\n\nGovernment Tenders:")
    gov_sources = get_all_sources_by_category("government_tender")
    for name in gov_sources:
        print(f"  - {name}")
    
    print("\n\nBusiness Directories:")
    dir_sources = get_all_sources_by_category("business_directory")
    for name in dir_sources:
        print(f"  - {name}")
