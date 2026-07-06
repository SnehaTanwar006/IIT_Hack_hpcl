"""Company Profile Builder - Target Company Card"""

from typing import Dict, List
try:
    from loguru import logger
except ImportError:  # pragma: no cover
    import logging
    logger = logging.getLogger(__name__)

from .entity_matcher import EntityMatcher


class CompanyProfileBuilder:
    """Build comprehensive company profiles (Target Company Card)"""
    
    def __init__(self):
        self.matcher = EntityMatcher()
    
    def build_profile(
        self,
        company_name: str,
        industry: str = None,
        location: str = None,
        cin: str = None,
        gstin: str = None,
        website: str = None,
        additional_data: Dict = None
    ) -> Dict:
        """
        Build Target Company Card
        
        Returns:
            Complete company profile
        """
        
        # Get or create entity
        entity_id = self.matcher.get_or_create_entity(
            company_name=company_name,
            cin=cin,
            gstin=gstin,
            website=website,
            industry=industry,
            location=location
        )
        
        # Get full entity data
        entity = self.matcher.companies.get(entity_id, {})
        
        # Build Target Company Card
        profile = {
            "entity_id": entity_id,
            "canonical_name": entity.get('canonical_name', company_name),
            "aliases": entity.get('aliases', []),
            
            # Identifiers
            "identifiers": {
                "cin": entity.get('cin'),
                "gstin": entity.get('gstin', []),
                "website": entity.get('website')
            },
            
            # Business info
            "industry": entity.get('industry', industry),
            "key_products": entity.get('key_products', []),
            
            # Geography
            "geography": {
                "headquarters": entity.get('locations', [None])[0] if entity.get('locations') else location,
                "plants": entity.get('plants', []),
                "regions": entity.get('regions', [])
            },
            
            # Contacts (only if publicly listed)
            "contacts": {
                "public_email": entity.get('public_email'),
                "public_phone": entity.get('public_phone'),
                "investor_relations": entity.get('investor_relations_url')
            },
            
            # Metadata
            "data_quality": {
                "completeness": self._calculate_completeness(entity),
                "last_updated": entity.get('created_at'),
                "sources_count": 1
            }
        }
        
        logger.info(f"Built profile for: {entity_id} - {company_name}")
        
        return profile
    
    def _calculate_completeness(self, entity: Dict) -> float:
        """Calculate profile completeness (0.0 to 1.0)"""
        
        fields = [
            'canonical_name', 'cin', 'gstin', 'website',
            'industry', 'locations'
        ]
        
        filled = sum(1 for field in fields if entity.get(field))
        
        return filled / len(fields)
