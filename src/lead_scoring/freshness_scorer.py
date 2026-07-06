"""Score signal freshness"""

from datetime import datetime, timedelta
from typing import Dict
from dateutil import parser


class FreshnessScorer:
    """Score signal freshness (0-20 points)"""
    
    def score_freshness(self, signal_date: datetime) -> Dict[str, any]:
        """
        Score based on how recent the signal is
        
        Args:
            signal_date: When the signal was detected
        
        Returns:
            Dict with score, days_old, freshness_level
        """
        
        now = datetime.now()
        days_old = (now - signal_date).days
        
        # Scoring tiers
        if days_old <= 1:
            score = 20
            level = 'VERY_FRESH'
        elif days_old <= 7:
            score = 15
            level = 'FRESH'
        elif days_old <= 30:
            score = 10
            level = 'RECENT'
        elif days_old <= 90:
            score = 5
            level = 'OLD'
        else:
            score = 2
            level = 'STALE'
        
        return {
            'score': score,
            'days_old': days_old,
            'freshness_level': level,
            'signal_date': signal_date.strftime('%Y-%m-%d')
        }
    
    def parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime"""
        try:
            return parser.parse(date_str)
        except:
            return datetime.now()