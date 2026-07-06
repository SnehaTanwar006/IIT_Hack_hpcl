"""RSS Fetcher - Policy-safe news fetching"""

import feedparser
import requests
from typing import List, Dict
from datetime import datetime
try:
    from loguru import logger
except ImportError:  # pragma: no cover
    import logging
    logger = logging.getLogger(__name__)

from .source_registry import SourceRegistry
from .provenance_logger import ProvenanceLogger


class RSSFetcher:
    """Fetch news from RSS feeds (policy-safe)"""
    
    def __init__(self):
        self.registry = SourceRegistry()
        self.provenance = ProvenanceLogger()
    
    def fetch_news(self, category: str = "news", max_items: int = 10) -> List[Dict]:
        """
        Fetch news from RSS feeds
        
        Args:
            category: Source category (news/tender)
            max_items: Max items to fetch per source
        
        Returns:
            List of news items with provenance
        """
        
        logger.info(f"Fetching {category} from RSS feeds...")
        
        sources = self.registry.get_active_sources(category)
        all_items = []
        
        for source in sources:
            if source['access_method'] != 'RSS':
                continue
            
            # Check if we can crawl
            if not self.registry.can_crawl(source['domain']):
                logger.warning(f"Skipping {source['domain']} - crawl frequency limit")
                continue
            
            # Fetch RSS feed
            try:
                logger.info(f"Fetching RSS: {source['domain']}")
                
                feed = feedparser.parse(source['rss_url'])
                
                for entry in feed.entries[:max_items]:
                    # Extract data
                    item_data = {
                        "title": entry.get('title', ''),
                        "description": entry.get('summary', ''),
                        "link": entry.get('link', ''),
                        "published": entry.get('published', ''),
                        "source_domain": source['domain']
                    }
                    
                    # Log provenance
                    provenance_id = self.provenance.log_extraction(
                        source_domain=source['domain'],
                        source_url=entry.get('link', ''),
                        extracted_data=item_data,
                        extraction_method='RSS',
                        confidence=source['trust_score']
                    )
                    
                    item_data['provenance_id'] = provenance_id
                    item_data['trust_score'] = source['trust_score']
                    
                    all_items.append(item_data)
                
                # Update last crawl
                self.registry.update_last_crawl(source['domain'])
                
                logger.info(f"Fetched {len(feed.entries[:max_items])} items from {source['domain']}")
            
            except Exception as e:
                logger.error(f"Error fetching {source['domain']}: {e}")
        
        logger.info(f"Total items fetched: {len(all_items)}")
        
        return all_items
