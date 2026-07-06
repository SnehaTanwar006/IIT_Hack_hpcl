"""Score company size proxy"""

import re
from typing import Dict


class CompanySizeScorer:
    """Score company size (0-20 points)"""
    
    def score_company_size(self, text: str, company_name: str = None) -> Dict[str, any]:
        """
        Score based on company size indicators
        
        Args:
            text: Signal text
            company_name: Company name (for known companies)
        
        Returns:
            Dict with score, size_category, evidence
        """
        
        text_lower = text.lower()
        
        # Check for known large companies
        large_companies = [
            'tata', 'reliance', 'adani', 'birla', 'jsw', 'essar',
            'vedanta', 'hindalco', 'ultratech', 'acc', 'ambuja',
            'ntpc', 'ongc', 'iocl', 'bpcl', 'sail', 'bhel'
        ]
        
        if company_name:
            company_lower = company_name.lower()
            if any(large in company_lower for large in large_companies):
                return {
                    'score': 20,
                    'size_category': 'LARGE',
                    'evidence': f'Known large company: {company_name}'
                }
        
        # Extract turnover/revenue mentions
        turnover_pattern = r'(?:turnover|revenue|sales).*?(?:₹|rs\.?|inr)\s*(\d+(?:,\d+)*)\s*(crore|cr|lakh|million|billion)'
        turnover_match = re.search(turnover_pattern, text_lower)
        
        if turnover_match:
            value = int(turnover_match.group(1).replace(',', ''))
            unit = turnover_match.group(2)
            
            # Convert to crores for comparison
            if unit in ['crore', 'cr']:
                crores = value
            elif unit in ['lakh']:
                crores = value / 100
            elif unit == 'million':
                crores = value / 10
            elif unit == 'billion':
                crores = value * 100
            else:
                crores = 0
            
            if crores >= 1000:
                return {
                    'score': 20,
                    'size_category': 'LARGE',
                    'evidence': f'Turnover: ₹{value} {unit}'
                }
            elif crores >= 100:
                return {
                    'score': 15,
                    'size_category': 'MEDIUM',
                    'evidence': f'Turnover: ₹{value} {unit}'
                }
            else:
                return {
                    'score': 10,
                    'size_category': 'SMALL',
                    'evidence': f'Turnover: ₹{value} {unit}'
                }
        
        # Extract capacity mentions
        capacity_pattern = r'(\d+(?:,\d+)*)\s*(mt|mtpa|mw|tpd|kl)'
        capacity_match = re.search(capacity_pattern, text_lower)
        
        if capacity_match:
            value = int(capacity_match.group(1).replace(',', ''))
            unit = capacity_match.group(2)
            
            # Large capacity indicators
            if (unit in ['mt', 'mtpa'] and value >= 1000) or \
               (unit == 'mw' and value >= 100) or \
               (unit == 'tpd' and value >= 500):
                return {
                    'score': 18,
                    'size_category': 'LARGE',
                    'evidence': f'Capacity: {value} {unit.upper()}'
                }
            elif (unit in ['mt', 'mtpa'] and value >= 100) or \
                 (unit == 'mw' and value >= 10) or \
                 (unit == 'tpd' and value >= 50):
                return {
                    'score': 12,
                    'size_category': 'MEDIUM',
                    'evidence': f'Capacity: {value} {unit.upper()}'
                }
        
        # Default: Unknown size
        return {
            'score': 8,
            'size_category': 'UNKNOWN',
            'evidence': 'No size indicators found'
        }