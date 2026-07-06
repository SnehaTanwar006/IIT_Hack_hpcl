"""Score lead intent strength"""

from typing import Dict


class IntentScorer:
    """Score intent strength (0-40 points)"""
    
    def __init__(self):
        # Intent type scores
        self.intent_scores = {
            'tender': 40,           # Explicit tender/RFQ
            'rfq': 35,              # Request for quotation
            'procurement': 30,      # Procurement notice
            'expansion': 20,        # Expansion announcement
            'capacity_addition': 18, # Capacity increase
            'news_mention': 10,     # General news
            'vague': 5              # Vague mention
        }
        
        # Keywords for each intent type
        self.intent_keywords = {
            'tender': ['tender', 'bid', 'quotation', 'rfq', 'eoi', 'expression of interest'],
            'rfq': ['request for quotation', 'rfq', 'quote'],
            'procurement': ['procurement', 'purchase', 'supply required', 'requirement'],
            'expansion': ['expansion', 'new facility', 'setting up', 'establishing'],
            'capacity_addition': ['capacity addition', 'capacity increase', 'scaling up'],
            'news_mention': ['announces', 'plans to', 'considering']
        }
    
    def score_intent(self, text: str, signal_type: str = None) -> Dict[str, any]:
        """
        Score intent strength
        
        Args:
            text: Signal text
            signal_type: Optional pre-classified signal type
        
        Returns:
            Dict with score, intent_type, evidence
        """
        
        text_lower = text.lower()
        
        # If signal_type provided, use it
        if signal_type and signal_type in self.intent_scores:
            return {
                'score': self.intent_scores[signal_type],
                'intent_type': signal_type,
                'evidence': f"Pre-classified as {signal_type}"
            }
        
        # Detect intent from keywords
        detected_intent = 'vague'
        max_score = 0
        evidence = []
        
        for intent_type, keywords in self.intent_keywords.items():
            matches = [kw for kw in keywords if kw in text_lower]
            if matches:
                score = self.intent_scores[intent_type]
                if score > max_score:
                    max_score = score
                    detected_intent = intent_type
                    evidence = matches
        
        return {
            'score': max_score,
            'intent_type': detected_intent,
            'evidence': ', '.join(evidence) if evidence else 'No strong intent signals'
        }