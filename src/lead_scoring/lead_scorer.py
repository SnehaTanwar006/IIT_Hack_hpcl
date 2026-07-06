"""Main lead scoring engine"""

from datetime import datetime
from typing import Dict
try:
    from loguru import logger
except ImportError:  # pragma: no cover
    import logging
    logger = logging.getLogger(__name__)

from .intent_scorer import IntentScorer
from .freshness_scorer import FreshnessScorer
from .company_size_scorer import CompanySizeScorer
from .proximity_scorer import ProximityScorer


class LeadScore:
    """Lead score result"""
    
    def __init__(self, total_score: int, breakdown: Dict, priority: str):
        self.total_score = total_score
        self.breakdown = breakdown
        self.priority = priority
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'total_score': self.total_score,
            'breakdown': self.breakdown,
            'priority': self.priority
        }


class LeadScorer:
    """Main lead scoring engine"""
    
    def __init__(self):
        self.intent_scorer = IntentScorer()
        self.freshness_scorer = FreshnessScorer()
        self.company_size_scorer = CompanySizeScorer()
        self.proximity_scorer = ProximityScorer()
    
    def score_lead(
        self,
        text: str,
        signal_date: datetime,
        company_name: str = None,
        location: str = None,
        signal_type: str = None
    ) -> LeadScore:
        """
        Calculate comprehensive lead score
        
        Args:
            text: Signal text
            signal_date: When signal was detected
            company_name: Company name (optional)
            location: Location string (optional)
            signal_type: Pre-classified signal type (optional)
        
        Returns:
            LeadScore object with total score and breakdown
        """
        
        logger.info("Scoring lead...")
        
        # Score each component
        intent_result = self.intent_scorer.score_intent(text, signal_type)
        freshness_result = self.freshness_scorer.score_freshness(signal_date)
        size_result = self.company_size_scorer.score_company_size(text, company_name)
        
        # Extract location if not provided
        if not location:
            location = self.proximity_scorer.extract_location(text)
        
        proximity_result = self.proximity_scorer.score_proximity(location)
        
        # Calculate total score (max 90 points)
        total_score = (
            intent_result['score'] +
            freshness_result['score'] +
            size_result['score'] +
            proximity_result['score']
        )
        
        # Determine priority
        priority = self._determine_priority(total_score, intent_result['intent_type'])
        
        # Build breakdown
        breakdown = {
            'intent': {
                'score': intent_result['score'],
                'type': intent_result['intent_type'],
                'evidence': intent_result['evidence']
            },
            'freshness': {
                'score': freshness_result['score'],
                'days_old': freshness_result['days_old'],
                'level': freshness_result['freshness_level']
            },
            'company_size': {
                'score': size_result['score'],
                'category': size_result['size_category'],
                'evidence': size_result['evidence']
            },
            'proximity': {
                'score': proximity_result['score'],
                'nearest_depot': proximity_result['nearest_depot'],
                'distance': proximity_result['distance_category']
            }
        }
        
        logger.info(f"Lead scored: {total_score}/90 - Priority: {priority}")
        
        return LeadScore(total_score, breakdown, priority)
    
    def _determine_priority(self, score: int, intent_type: str) -> str:
        """Determine priority level"""
        
        # Critical: High score OR tender/RFQ
        if score >= 70 or intent_type in ['tender', 'rfq']:
            return 'CRITICAL'
        elif score >= 50:
            return 'HIGH'
        elif score >= 30:
            return 'MEDIUM'
        else:
            return 'LOW'
