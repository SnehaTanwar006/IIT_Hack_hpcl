"""Full Pipeline Integration - Parts 1-4"""

from loguru import logger
from pathlib import Path
import sys
from datetime import datetime, timedelta
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from web_intelligence.rss_fetcher import RSSFetcher
from entity_resolution.company_profile import CompanyProfileBuilder
from product_inference.inference_engine import ProductInferenceEngine
from lead_scoring.lead_scorer import LeadScorer
from lead_scoring.territory_router import TerritoryRouter

# Configure logging
Path("logs").mkdir(exist_ok=True)
logger.add("logs/full_pipeline_{time}.log", rotation="1 day")


def run_full_pipeline():
    """Run complete lead intelligence pipeline"""
    
    print("="*70)
    print("HPCL LEAD INTELLIGENCE - FULL PIPELINE")
    print("="*70)
    
    # Initialize all components
    logger.info("Initializing pipeline components...")
    
    rss_fetcher = RSSFetcher()
    profile_builder = CompanyProfileBuilder()
    product_engine = ProductInferenceEngine()
    lead_scorer = LeadScorer()
    territory_router = TerritoryRouter()
    
    # STEP 1: Fetch signals from web (Part 1)
    print("\n" + "─"*70)
    print("STEP 1: WEB INTELLIGENCE - Fetching signals...")
    print("─"*70)
    
    # Simulate fetched news (in real scenario, this would fetch from RSS)
    simulated_signals = [
        {
            "title": "Tata Steel announces ₹5,000 crore expansion in Jamshedpur",
            "description": """
            Tata Steel Limited has announced a major expansion of its blast furnace
            capacity at the Jamshedpur plant in Jharkhand. The ₹5,000 crore project
            will add 2 MTPA capacity and is expected to be commissioned by Q4 2026.
            The facility will require furnace oil for boiler operations.
            """,
            "link": "https://economictimes.com/article/12345",
            "published": datetime.now().isoformat(),
            "source_domain": "economictimes.indiatimes.com",
            "provenance_id": "PROV_20260207_001",
            "trust_score": 0.95
        },
        {
            "title": "NHAI tenders 15,000 MT Bitumen for NH-44 project",
            "description": """
            Tender Notice: National Highways Authority of India (NHAI) invites bids
            for supply of 15,000 MT Bitumen VG-30 for NH-44 highway widening project
            in Vadodara, Gujarat. Bid closing date: 20-Feb-2026. Urgent requirement.
            """,
            "link": "https://gem.gov.in/tender/67890",
            "published": datetime.now().isoformat(),
            "source_domain": "gem.gov.in",
            "provenance_id": "PROV_20260207_002",
            "trust_score": 1.0
        }
    ]
    
    print(f"✅ Fetched {len(simulated_signals)} signals")
    for signal in simulated_signals:
        print(f"   • {signal['title'][:60]}... (Trust: {signal['trust_score']})")
    
    # STEP 2: Entity Resolution (Part 2)
    print("\n" + "─"*70)
    print("STEP 2: ENTITY RESOLUTION - Building company profiles...")
    print("─"*70)
    
    enriched_signals = []
    
    for signal in simulated_signals:
        # Extract company name via NER
        if "Tata Steel" in signal['title']:
            company_name = "Tata Steel Limited"
            industry = "Steel"
            location = "Jamshedpur, Jharkhand"
        elif "NHAI" in signal['title']:
            company_name = "NHAI"
            industry = "Construction"
            location = "Vadodara, Gujarat"
        else:
            continue
        
        # Build company profile
        profile = profile_builder.build_profile(
            company_name=company_name,
            industry=industry,
            location=location
        )
        
        print(f"\n Company Profile: {profile['canonical_name']}")
        print(f"   Entity ID: {profile['entity_id']}")
        print(f"   Industry: {profile['industry']}")
        print(f"   Location: {profile['geography']['headquarters']}")
        print(f"   Completeness: {profile['data_quality']['completeness']:.0%}")
        
        # Add to signal
        signal['company_profile'] = profile
        enriched_signals.append(signal)
    
    # STEP 3: Product Inference (Part 3)
    print("\n" + "─"*70)
    print("STEP 3: PRODUCT INFERENCE - Recommending products...")
    print("─"*70)
    
    for signal in enriched_signals:
        text = signal['title'] + " " + signal['description']
        
        # Infer products
        recommendations = product_engine.infer_products(text, top_k=3)
        
        print(f"\n Signal: {signal['title'][:50]}...")
        print(f"   Top 3 Products:")
        for rank, rec in enumerate(recommendations, 1):
            print(f"   {rank}. {rec.product_name} ({rec.product_code})")
            print(f"      Confidence: {rec.confidence:.2f}")
            print(f"      Reason: {rec.reason_codes[0] if rec.reason_codes else 'N/A'}")
        
        signal['product_recommendations'] = recommendations
    
    # STEP 4: Lead Scoring & Routing (Part 4)
    print("\n" + "─"*70)
    print("STEP 4: LEAD SCORING & ROUTING - Prioritizing & assigning...")
    print("─"*70)
    
    leads = []
    
    for signal in enriched_signals:
        # Score lead
        score_result = lead_scorer.score_lead(
            text=signal['title'] + " " + signal['description'],
            signal_date=datetime.fromisoformat(signal['published']),
            company_name=signal['company_profile']['canonical_name'],
            location=signal['company_profile']['geography']['headquarters']
        )
        
        # Route lead
        routing_result = territory_router.route_lead(
            location=signal['company_profile']['geography']['headquarters'],
            industry=signal['company_profile']['industry'],
            nearest_depot=score_result.breakdown['proximity']['nearest_depot']
        )
        
        # Create lead
        lead = {
            "lead_id": f"LEAD_{len(leads) + 1:06d}",
            "company": signal['company_profile'],
            "signal": {
                "title": signal['title'],
                "source": signal['source_domain'],
                "provenance_id": signal['provenance_id'],
                "trust_score": signal['trust_score']
            },
            "products": [rec.to_dict() for rec in signal['product_recommendations']],
            "score": score_result.to_dict(),
            "routing": routing_result,
            "created_at": datetime.now().isoformat()
        }
        
        leads.append(lead)
        
        print(f"\nLEAD CREATED: {lead['lead_id']}")
        print(f"   Company: {lead['company']['canonical_name']}")
        print(f"   Score: {lead['score']['total_score']}/90")
        print(f"   Priority: {lead['score']['priority']}")
        print(f"   Top Product: {lead['products'][0]['product_name']}")
        print(f"   Assigned To: {lead['routing']['assigned_officer']}")
        print(f"   Depot: {lead['routing']['depot']}")
    
    # FINAL OUTPUT
    print("\n" + "="*70)
    print("PIPELINE COMPLETE - LEADS GENERATED")
    print("="*70)
    
    for lead in leads:
        print(f"\n{'─'*70}")
        print(f"LEAD: {lead['lead_id']} - {lead['score']['priority']} PRIORITY")
        print(f"{'─'*70}")
        print(json.dumps(lead, indent=2))
    
    print("\n" + "="*70)
    print(f"GENERATED {len(leads)} QUALIFIED LEADS")
    print("="*70)
    
    return leads

if __name__ == "__main__":
    run_full_pipeline()