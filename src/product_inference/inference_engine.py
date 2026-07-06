"""Main product inference engine"""

from typing import List, Dict
try:
    from loguru import logger
except ImportError:  # pragma: no cover - exercised only in minimal local runtimes
    import logging
    logger = logging.getLogger(__name__)

from .product_catalog import HPCLProductCatalog
from .signal_extractor import SignalExtractor
from .confidence_scorer import ConfidenceScorer


class ProductRecommendation:
    """Product recommendation with reasoning"""
    
    def __init__(self, product_code: str, product_name: str, confidence: float,
                 reason_codes: List[str], evidence: Dict, uncertainty: str):
        self.product_code = product_code
        self.product_name = product_name
        self.confidence = confidence
        self.reason_codes = reason_codes
        self.evidence = evidence
        self.uncertainty = uncertainty
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'product_code': self.product_code,
            'product_name': self.product_name,
            'confidence': self.confidence,
            'reason_codes': self.reason_codes,
            'evidence': self.evidence,
            'uncertainty_flag': self.uncertainty
        }


class ProductInferenceEngine:
    """Main inference engine"""
    
    def __init__(self):
        self.catalog = HPCLProductCatalog()
        self.extractor = SignalExtractor()
        self.scorer = ConfidenceScorer()
    
    def infer_products(self, text: str, top_k: int = 3) -> List[ProductRecommendation]:
        """Infer product needs from text"""
        
        logger.info(f"Inferring products from text (length: {len(text)})")
        
        # Extract signals
        signals = self.extractor.extract_signals(text)
        
        # Score all products
        recommendations = []
        
        for product in self.catalog.get_all_products():
            # Calculate confidence
            confidence_result = self.scorer.calculate_confidence(
                product.product_code,
                signals
            )
            
            # Skip low scores
            if confidence_result['score'] < 0.1:
                continue
            
            # Generate reason codes
            reason_codes = self._generate_reasons(product, signals, confidence_result)
            
            # Create recommendation
            rec = ProductRecommendation(
                product_code=product.product_code,
                product_name=product.product_name,
                confidence=confidence_result['score'],
                reason_codes=reason_codes,
                evidence=confidence_result['evidence'],
                uncertainty=confidence_result['uncertainty']
            )
            
            recommendations.append(rec)
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        
        return recommendations[:top_k]
    
    def _generate_reasons(self, product, signals: Dict, confidence: Dict) -> List[str]:
        """Generate human-readable reason codes"""
        
        reasons = []
        
        # Strong indicators
        strong = [
            kw['keyword'] for kw in signals.get('keywords_found', [])
            if kw.get('product_code') == product.product_code 
            and kw.get('type') == 'strong_indicator'
        ]
        if strong:
            reasons.append(f"Matched: {', '.join(strong[:2])}")
        
        # Operational cues
        cues = [
            cue['cue'] for cue in signals.get('operational_cues', [])
            if cue.get('product_code') == product.product_code
        ]
        if cues:
            reasons.append(f"Operational cue: {', '.join(cues[:2])}")
        
        # Keywords
        keywords = [
            kw['keyword'] for kw in signals.get('keywords_found', [])
            if kw.get('product_code') == product.product_code 
            and kw.get('type') == 'keyword'
        ]
        if keywords:
            reasons.append(f"Product keyword: {', '.join(keywords[:2])}")
        
        # Quantity
        if signals.get('quantities'):
            reasons.append(f"Quantity: {signals['quantities'][0]['text']}")
        
        # Urgency
        if signals.get('urgency'):
            reasons.append(f"Urgency: {', '.join(signals['urgency'][:2])}")
        
        return reasons if reasons else ["General context match"]
