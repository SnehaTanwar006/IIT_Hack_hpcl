"""Entity Matching - Match companies across sources"""

from typing import Dict, List, Optional
try:
    from loguru import logger
except ImportError:  # pragma: no cover
    import logging
    logger = logging.getLogger(__name__)
import json
from pathlib import Path

from .company_normalizer import CompanyNormalizer


class EntityMatcher:
    """Match and resolve company entities across sources"""
    
    def __init__(self, companies_file: str = "data/companies.json"):
        self.companies_file = Path(companies_file)
        self.normalizer = CompanyNormalizer()
        self.companies = self._load_companies()
    
    def _load_companies(self) -> Dict:
        """Load known companies from file"""
        
        if self.companies_file.exists():
            with open(self.companies_file, 'r') as f:
                return json.load(f)
        else:
            return {}
    
    def _save_companies(self):
        """Save companies to file"""
        self.companies_file.parent.mkdir(exist_ok=True)
        with open(self.companies_file, 'w') as f:
            json.dump(self.companies, indent=2, fp=f)
    
    def match_company(
        self,
        company_name: str,
        cin: str = None,
        gstin: str = None,
        website: str = None,
        threshold: float = 0.85
    ) -> Optional[str]:
        """
        Match company to existing entity
        
        Args:
            company_name: Company name from source
            cin: Corporate Identification Number (optional)
            gstin: GST Identification Number (optional)
            website: Company website (optional)
            threshold: Similarity threshold for fuzzy matching
        
        Returns:
            entity_id if match found, None otherwise
        """
        
        # Exact identifier match (CIN/GSTIN)
        if cin:
            for entity_id, company in self.companies.items():
                if company.get('cin') == cin:
                    logger.info(f"Matched by CIN: {company_name} → {entity_id}")
                    return entity_id
        
        if gstin:
            for entity_id, company in self.companies.items():
                if gstin in company.get('gstin', []):
                    logger.info(f"Matched by GSTIN: {company_name} → {entity_id}")
                    return entity_id
        
        # Website domain match
        if website:
            for entity_id, company in self.companies.items():
                if company.get('website') == website:
                    logger.info(f"Matched by website: {company_name} → {entity_id}")
                    return entity_id
        
        # Fuzzy name matching
        best_match = None
        best_score = 0.0
        
        for entity_id, company in self.companies.items():
            # Check canonical name
            score = self.normalizer.similarity_score(
                company_name,
                company['canonical_name']
            )
            
            if score > best_score:
                best_score = score
                best_match = entity_id
            
            # Check aliases
            for alias in company.get('aliases', []):
                score = self.normalizer.similarity_score(company_name, alias)
                if score > best_score:
                    best_score = score
                    best_match = entity_id
        
        if best_score >= threshold:
            logger.info(f"Matched by name similarity ({best_score:.2f}): {company_name} → {best_match}")
            return best_match
        
        logger.info(f"No match found for: {company_name}")
        return None
    
    def create_entity(
        self,
        company_name: str,
        cin: str = None,
        gstin: str = None,
        website: str = None,
        industry: str = None,
        location: str = None
    ) -> str:
        """
        Create new company entity
        
        Returns:
            entity_id: New entity ID
        """
        
        # Generate entity ID
        entity_id = f"ENT_{len(self.companies) + 1:06d}"
        
        # Create entity record
        self.companies[entity_id] = {
            "entity_id": entity_id,
            "canonical_name": company_name,
            "aliases": self.normalizer.extract_variants(company_name),
            "cin": cin,
            "gstin": [gstin] if gstin else [],
            "website": website,
            "industry": industry,
            "locations": [location] if location else [],
            "created_at": "2026-02-07T21:00:00Z"
        }
        
        self._save_companies()
        
        logger.info(f"Created new entity: {entity_id} - {company_name}")
        
        return entity_id
    
    def get_or_create_entity(
        self,
        company_name: str,
        cin: str = None,
        gstin: str = None,
        website: str = None,
        industry: str = None,
        location: str = None
    ) -> str:
        """
        Get existing entity or create new one
        
        Returns:
            entity_id
        """
        
        # Try to match existing
        entity_id = self.match_company(company_name, cin, gstin, website)
        
        if entity_id:
            return entity_id
        
        # Create new entity
        return self.create_entity(
            company_name, cin, gstin, website, industry, location
        )
