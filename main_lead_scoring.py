"""Test Lead Scoring & Routing Engine"""

from loguru import logger
from pathlib import Path
import sys
from datetime import datetime, timedelta
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lead_scoring.lead_scorer import LeadScorer
from lead_scoring.territory_router import TerritoryRouter

# Configure logging
Path("logs").mkdir(exist_ok=True)
logger.add("logs/lead_scoring_{time}.log", rotation="1 day")


def test_lead_scoring():
    """Test lead scoring and routing"""
    
    print("="*70)
    print("HPCL LEAD SCORING & ROUTING ENGINE - TEST")
    print("="*70)
    
    # Initialize engines
    scorer = LeadScorer()
    router = TerritoryRouter()
    
    # Test cases
    test_cases = [
        {
            'name': 'Critical Tender - Bitumen',
            'text': """
            Tender Notice: Supply of 15,000 MT Bitumen VG-30 for NH-44 highway
            widening project in Vadodara, Gujarat. Bid closing: 20-Feb-2026.
            Urgent requirement for road construction.
            """,
            'signal_date': datetime.now() - timedelta(hours=2),
            'company_name': 'NHAI',
            'location': 'Vadodara, Gujarat',
            'industry': 'Construction'
        },
        {
            'name': 'High Priority - Steel Expansion',
            'text': """
            Tata Steel announces ₹5,000 crore expansion of blast furnace at
            Jamshedpur, Jharkhand. New 2 MTPA capacity. Requires furnace oil
            for boiler operations.
            """,
            'signal_date': datetime.now() - timedelta(days=1),
            'company_name': 'Tata Steel',
            'location': 'Jamshedpur, Jharkhand',
            'industry': 'Steel'
        },
        {
            'name': 'Medium Priority - Jute Mill',
            'text': """
            Bengal Jute Mills expanding batching unit. Jute batch oil
            requirement expected to increase. Located in Kolkata, West Bengal.
            """,
            'signal_date': datetime.now() - timedelta(days=7),
            'company_name': 'Bengal Jute Mills',
            'location': 'Kolkata, West Bengal',
            'industry': 'Jute'
        },
        {
            'name': 'Low Priority - Old News',
            'text': """
            Company considering setting up new facility. Plans announced
            3 months ago. Location: Pune, Maharashtra.
            """,
            'signal_date': datetime.now() - timedelta(days=90),
            'company_name': 'ABC Industries',
            'location': 'Pune, Maharashtra',
            'industry': 'Manufacturing'
        },
        {
            'name': 'High Priority - Power Plant RFQ',
            'text': """
            RFQ for LSHS supply to 500 MW thermal power plant in Chennai.
            Capacity: 500 MW. Requirement: 10,000 MT/month. NTPC project.
            """,
            'signal_date': datetime.now() - timedelta(hours=12),
            'company_name': 'NTPC',
            'location': 'Chennai, Tamil Nadu',
            'industry': 'Power'
        }
    ]
    
    # Run tests
    for idx, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST {idx}: {test['name']}")
        print(f"{'='*70}")
        print(f"\nCompany: {test['company_name']}")
        print(f"Location: {test['location']}")
        print(f"Industry: {test['industry']}")
        print(f"Signal Date: {test['signal_date'].strftime('%Y-%m-%d %H:%M')}")
        print(f"\nText:\n{test['text'].strip()}")
        
        # Score lead
        score_result = scorer.score_lead(
            text=test['text'],
            signal_date=test['signal_date'],
            company_name=test['company_name'],
            location=test['location']
        )
        
        # Route lead
        routing_result = router.route_lead(
            location=test['location'],
            industry=test['industry'],
            nearest_depot=score_result.breakdown['proximity']['nearest_depot']
        )
        
        # Display results
        print(f"\n{'─'*70}")
        print("LEAD SCORE:")
        print(f"{'─'*70}")
        print(f"Total Score: {score_result.total_score}/90")
        print(f"Priority: {score_result.priority}")
        
        print(f"\nScore Breakdown:")
        print(f"  Intent Strength:  {score_result.breakdown['intent']['score']}/40")
        print(f"    Type: {score_result.breakdown['intent']['type']}")
        print(f"    Evidence: {score_result.breakdown['intent']['evidence']}")
        
        print(f"\n  Freshness:        {score_result.breakdown['freshness']['score']}/20")
        print(f"    Days Old: {score_result.breakdown['freshness']['days_old']}")
        print(f"    Level: {score_result.breakdown['freshness']['level']}")
        
        print(f"\n  Company Size:     {score_result.breakdown['company_size']['score']}/20")
        print(f"    Category: {score_result.breakdown['company_size']['category']}")
        print(f"    Evidence: {score_result.breakdown['company_size']['evidence']}")
        
        print(f"\n  Proximity:        {score_result.breakdown['proximity']['score']}/10")
        print(f"    Nearest Depot: {score_result.breakdown['proximity']['nearest_depot']}")
        print(f"    Distance: {score_result.breakdown['proximity']['distance']}")
        
        print(f"\n{'─'*70}")
        print("ROUTING:")
        print(f"{'─'*70}")
        print(f"Assigned Officer: {routing_result['assigned_officer']}")
        print(f"Email: {routing_result['email']}")
        print(f"Phone: {routing_result['phone']}")
        print(f"Depot: {routing_result['depot']}")
        print(f"Region: {routing_result['region']}")
        print(f"Match Reason: {routing_result['match_reason']}")
        
        # JSON output
        print(f"\n{'─'*70}")
        print("JSON Output:")
        print(f"{'─'*70}")
        output = {
            'test_case': test['name'],
            'score': score_result.to_dict(),
            'routing': routing_result
        }
        print(json.dumps(output, indent=2))
    
    print("\n" + "="*70)
    print("LEAD SCORING & ROUTING TEST COMPLETED!")
    print("="*70)


if __name__ == "__main__":
    test_lead_scoring()