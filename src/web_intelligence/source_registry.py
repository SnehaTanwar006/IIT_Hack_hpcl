"""Source Registry - Track all data sources with governance rules"""

from typing import Dict, List
from datetime import datetime
try:
    from loguru import logger
except ImportError:  # pragma: no cover
    import logging
    logger = logging.getLogger(__name__)
import json
from pathlib import Path


class SourceRegistry:
    """Maintain registry of all data sources with governance rules"""
    
    def __init__(self, registry_file: str = "data/source_registry.json"):
        self.registry_file = Path(registry_file)
        self.sources = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Load source registry from file"""
        
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        else:
            # Create default registry
            default_registry = self._create_default_registry()
            self._save_registry(default_registry)
            return default_registry
    
    def _create_default_registry(self) -> Dict:
        """Create default source registry"""
        
        return {
            "economictimes.indiatimes.com": {
                "domain": "economictimes.indiatimes.com",
                "category": "news",
                "access_method": "RSS",
                "rss_url": "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
                "allowed_crawl_frequency": "hourly",
                "rate_limit_requests_per_hour": 100,
                "trust_score": 0.95,
                "robots_txt_compliant": True,
                "tos_reviewed": "2026-01-15",
                "tos_allows_scraping": True,
                "last_crawl": None,
                "status": "active"
            },
            "gem.gov.in": {
                "domain": "gem.gov.in",
                "category": "tender",
                "access_method": "API",
                "api_endpoint": "https://gem.gov.in/api/tenders",
                "allowed_crawl_frequency": "daily",
                "rate_limit_requests_per_hour": 50,
                "trust_score": 1.0,
                "robots_txt_compliant": True,
                "tos_reviewed": "2026-01-15",
                "tos_allows_scraping": True,
                "last_crawl": None,
                "status": "active"
            },
            "business-standard.com": {
                "domain": "business-standard.com",
                "category": "news",
                "access_method": "RSS",
                "rss_url": "https://www.business-standard.com/rss/home_page_top_stories.rss",
                "allowed_crawl_frequency": "hourly",
                "rate_limit_requests_per_hour": 100,
                "trust_score": 0.90,
                "robots_txt_compliant": True,
                "tos_reviewed": "2026-01-15",
                "tos_allows_scraping": True,
                "last_crawl": None,
                "status": "active"
            },
            "moneycontrol.com": {
                "domain": "moneycontrol.com",
                "category": "news",
                "access_method": "RSS",
                "rss_url": "https://www.moneycontrol.com/rss/latestnews.xml",
                "allowed_crawl_frequency": "hourly",
                "rate_limit_requests_per_hour": 100,
                "trust_score": 0.88,
                "robots_txt_compliant": True,
                "tos_reviewed": "2026-01-15",
                "tos_allows_scraping": True,
                "last_crawl": None,
                "status": "active"
            }
        }
    
    def _save_registry(self, registry: Dict):
        """Save registry to file"""
        self.registry_file.parent.mkdir(exist_ok=True)
        with open(self.registry_file, 'w') as f:
            json.dump(registry, indent=2, fp=f)
    
    def get_source(self, domain: str) -> Dict:
        """Get source configuration"""
        return self.sources.get(domain)
    
    def get_active_sources(self, category: str = None) -> List[Dict]:
        """Get all active sources, optionally filtered by category"""
        
        active = [
            source for source in self.sources.values()
            if source['status'] == 'active'
        ]
        
        if category:
            active = [s for s in active if s['category'] == category]
        
        return active
    
    def update_last_crawl(self, domain: str):
        """Update last crawl timestamp"""
        
        if domain in self.sources:
            self.sources[domain]['last_crawl'] = datetime.now().isoformat()
            self._save_registry(self.sources)
    
    def can_crawl(self, domain: str) -> bool:
        """Check if source can be crawled now (respects frequency limits)"""
        
        source = self.get_source(domain)
        if not source or source['status'] != 'active':
            return False
        
        # Check last crawl time
        if not source['last_crawl']:
            return True
        
        last_crawl = datetime.fromisoformat(source['last_crawl'])
        now = datetime.now()
        
        frequency = source['allowed_crawl_frequency']
        
        if frequency == 'hourly':
            return (now - last_crawl).total_seconds() >= 3600
        elif frequency == 'daily':
            return (now - last_crawl).total_seconds() >= 86400
        elif frequency == 'weekly':
            return (now - last_crawl).total_seconds() >= 604800
        
        return True
