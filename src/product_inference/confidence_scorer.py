"""Calculate confidence scores for recommendations"""

from typing import Dict


class ConfidenceScorer:
    """Calculate confidence scores"""
    
    def __init__(self):
        self.weights = {
            'strong_indicator': 0.4,
            'keyword': 0.3,
            'operational_cue': 0.2,
            'quantity': 0.1
        }
    
    def calculate_confidence(
        self,
        product_code: str,
        signals: Dict
    ) -> Dict:
        """Calculate confidence score"""
        
        # Count evidence
        strong_count = sum(
            1 for kw in signals.get('keywords_found', [])
            if kw.get('product_code') == product_code and kw.get('type') == 'strong_indicator'
        )
        
        keyword_count = sum(
            1 for kw in signals.get('keywords_found', [])
            if kw.get('product_code') == product_code and kw.get('type') == 'keyword'
        )
        
        cue_count = sum(
            1 for cue in signals.get('operational_cues', [])
            if cue.get('product_code') == product_code
        )
        
        has_quantity = len(signals.get('quantities', [])) > 0
        
        # Calculate score
        score = 0.0
        score += min(strong_count * self.weights['strong_indicator'], 0.4)
        score += min(keyword_count * self.weights['keyword'], 0.3)
        score += min(cue_count * self.weights['operational_cue'], 0.2)
        if has_quantity:
            score += self.weights['quantity']
        
        # Uncertainty flag
        if strong_count > 0 and score >= 0.6:
            uncertainty = 'LOW'
        elif (keyword_count + cue_count) >= 2 and score >= 0.4:
            uncertainty = 'MEDIUM'
        else:
            uncertainty = 'HIGH'
        
        return {
            'score': round(score, 2),
            'uncertainty': uncertainty,
            'evidence': {
                'strong_indicators': strong_count,
                'keywords': keyword_count,
                'operational_cues': cue_count,
                'quantity_mentioned': has_quantity
            }
        }