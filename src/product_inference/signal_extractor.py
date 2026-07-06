"""Extract product signals from text"""

import re
from typing import List, Dict
try:
    from loguru import logger
except ImportError:  # pragma: no cover
    import logging
    logger = logging.getLogger(__name__)

from .product_catalog import HPCLProductCatalog


class SignalExtractor:
    """Extract product-related signals from text"""
    
    def __init__(self):
        self.catalog = HPCLProductCatalog()
    
    def extract_signals(self, text: str) -> Dict[str, any]:
        """Extract all signals from text"""
        
        if not text:
            return self._empty_signals()
        
        text_lower = text.lower()
        
        return {
            'keywords_found': self._extract_keywords(text_lower),
            'operational_cues': self._extract_cues(text_lower),
            'quantities': self._extract_quantities(text),
            'urgency': self._extract_urgency(text_lower)
        }
    
    def _empty_signals(self) -> Dict:
        """Empty signals structure"""
        return {
            'keywords_found': [],
            'operational_cues': [],
            'quantities': [],
            'urgency': []
        }
    
    def _extract_keywords(self, text: str) -> List[Dict]:
        """Extract product keywords"""
        found = []
        
        for product in self.catalog.get_all_products():
            # Check keywords
            for keyword in product.keywords:
                if keyword in text:
                    found.append({
                        'keyword': keyword,
                        'product_code': product.product_code,
                        'type': 'keyword'
                    })
            
            # Check strong indicators
            for indicator in product.strong_indicators:
                if indicator in text:
                    found.append({
                        'keyword': indicator,
                        'product_code': product.product_code,
                        'type': 'strong_indicator'
                    })
        
        return found
    
    def _extract_cues(self, text: str) -> List[Dict]:
        """Extract operational cues"""
        found = []
        
        for product in self.catalog.get_all_products():
            for cue in product.operational_cues:
                if cue in text:
                    found.append({
                        'cue': cue,
                        'product_code': product.product_code
                    })
        
        return found
    
    def _extract_quantities(self, text: str) -> List[Dict]:
        """Extract quantity mentions (e.g., '10,000 MT')"""
        quantities = []
        
        pattern = r'(\d{1,3}(?:,\d{3})*)\s*(mt|kl|tons?|tonnes?)'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            quantities.append({
                'value': match.group(1).replace(',', ''),
                'unit': match.group(2).lower(),
                'text': match.group(0)
            })
        
        return quantities
    
    def _extract_urgency(self, text: str) -> List[str]:
        """Extract urgency indicators"""
        urgency_words = ['urgent', 'tender', 'rfq', 'bid', 'closing', 'deadline']
        return [word for word in urgency_words if word in text]
