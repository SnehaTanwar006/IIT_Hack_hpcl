"""Score geographic proximity to HPCL depots"""

from typing import Dict, List, Tuple
import re


class ProximityScorer:
    """Score geographic proximity (0-10 points)"""
    
    def __init__(self):
        # HPCL depot locations (simplified - major depots)
        self.depots = {
            'Mumbai': {'state': 'Maharashtra', 'region': 'West'},
            'Delhi': {'state': 'Delhi', 'region': 'North'},
            'Kolkata': {'state': 'West Bengal', 'region': 'East'},
            'Chennai': {'state': 'Tamil Nadu', 'region': 'South'},
            'Bangalore': {'state': 'Karnataka', 'region': 'South'},
            'Hyderabad': {'state': 'Telangana', 'region': 'South'},
            'Ahmedabad': {'state': 'Gujarat', 'region': 'West'},
            'Pune': {'state': 'Maharashtra', 'region': 'West'},
            'Visakhapatnam': {'state': 'Andhra Pradesh', 'region': 'South'},
            'Jaipur': {'state': 'Rajasthan', 'region': 'North'}
        }
        
        # State to region mapping
        self.state_regions = {
            'Maharashtra': 'West', 'Gujarat': 'West', 'Goa': 'West',
            'Delhi': 'North', 'Punjab': 'North', 'Haryana': 'North', 'Rajasthan': 'North',
            'West Bengal': 'East', 'Odisha': 'East', 'Bihar': 'East', 'Jharkhand': 'East',
            'Tamil Nadu': 'South', 'Karnataka': 'South', 'Andhra Pradesh': 'South', 
            'Telangana': 'South', 'Kerala': 'South'
        }
    
    def score_proximity(self, location: str) -> Dict[str, any]:
        """
        Score based on proximity to HPCL depots
        
        Args:
            location: Location string (e.g., "Jamshedpur, Jharkhand")
        
        Returns:
            Dict with score, nearest_depot, distance_category
        """
        
        if not location:
            return {
                'score': 5,
                'nearest_depot': 'Unknown',
                'distance_category': 'UNKNOWN',
                'evidence': 'No location provided'
            }
        
        location_lower = location.lower()
        
        # Check if location is a depot city (direct match)
        for depot_city in self.depots.keys():
            if depot_city.lower() in location_lower:
                return {
                    'score': 10,
                    'nearest_depot': depot_city,
                    'distance_category': 'DEPOT_CITY',
                    'evidence': f'Located in depot city: {depot_city}'
                }
        
        # Extract state from location
        detected_state = None
        for state in self.state_regions.keys():
            if state.lower() in location_lower:
                detected_state = state
                break
        
        if detected_state:
            region = self.state_regions[detected_state]
            
            # Find nearest depot in same region
            regional_depots = [
                depot for depot, info in self.depots.items()
                if info['region'] == region
            ]
            
            if regional_depots:
                return {
                    'score': 7,
                    'nearest_depot': regional_depots[0],
                    'distance_category': 'SAME_REGION',
                    'evidence': f'Same region ({region}): {detected_state}'
                }
        
        # Default: Far from depots
        return {
            'score': 4,
            'nearest_depot': 'Delhi',  # Default
            'distance_category': 'FAR',
            'evidence': 'Location not near major depots'
        }
    
    def extract_location(self, text: str) -> str:
        """Extract location from text"""
        
        # Common location patterns
        patterns = [
            r'(?:in|at|near)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),?\s*([A-Z][a-z]+)',
            r'([A-Z][a-z]+),\s*([A-Z][a-z]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return None