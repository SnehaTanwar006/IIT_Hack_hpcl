"""Company Name Normalization"""

import re
from typing import Dict, List
try:
    from fuzzywuzzy import fuzz
except ImportError:  # pragma: no cover - minimal local runtime fallback
    from difflib import SequenceMatcher

    class _FuzzFallback:
        @staticmethod
        def ratio(name1: str, name2: str) -> int:
            return int(SequenceMatcher(None, name1, name2).ratio() * 100)

    fuzz = _FuzzFallback()


class CompanyNormalizer:
    """Normalize company names across sources"""
    
    def __init__(self):
        # Common suffixes to remove for matching
        self.suffixes = [
            'limited', 'ltd', 'pvt', 'private', 'public',
            'corporation', 'corp', 'inc', 'llc', 'llp',
            'company', 'co', 'industries', 'group'
        ]
    
    def normalize(self, company_name: str) -> str:
        """
        Normalize company name for matching
        
        Examples:
            "Tata Steel Limited" → "tata steel"
            "JSW Steel Ltd." → "jsw steel"
            "RELIANCE INDUSTRIES LTD" → "reliance industries"
        """
        
        if not company_name:
            return ""
        
        # Convert to lowercase
        normalized = company_name.lower()
        
        # Remove punctuation
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        
        # Remove common suffixes
        for suffix in self.suffixes:
            normalized = re.sub(rf'\b{suffix}\b', '', normalized)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized.strip()
    
    def extract_variants(self, company_name: str) -> List[str]:
        """
        Generate common variants of a company name
        
        Returns:
            List of possible name variants
        """
        
        variants = [company_name]
        
        # normalized version
        normalized = self.normalize(company_name)
        if normalized not in variants:
            variants.append(normalized)
        
        # acronym if applicable
        words = normalized.split()
        if len(words) >= 2:
            acronym = ''.join([w[0] for w in words if w])
            if len(acronym) >= 2:
                variants.append(acronym)
        
        return variants
    
    def similarity_score(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two company names
        
        Returns:
            Similarity score (0.0 to 1.0)
        """
        
        norm1 = self.normalize(name1)
        norm2 = self.normalize(name2)
        
        # Exact match
        if norm1 == norm2:
            return 1.0
        
        # Fuzzy match (Levenshtein distance)
        similarity = fuzz.ratio(norm1, norm2) / 100.0
        
        return similarity
