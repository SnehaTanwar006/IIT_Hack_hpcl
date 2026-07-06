"""Test Product Inference Engine"""

from loguru import logger
from pathlib import Path
import sys
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from product_inference.inference_engine import ProductInferenceEngine

# Configure logging
Path("logs").mkdir(exist_ok=True)
logger.add("logs/product_inference_{time}.log", rotation="1 day")

def test_product_inference():
    """Test with sample scenarios"""
    
    print("="*60)
    print("HPCL PRODUCT-NEED INFERENCE ENGINE - TEST")
    print("="*60)
    
    # Initialize engine
    engine = ProductInferenceEngine()
    
    # Test cases
    test_cases = [
        {
            'name': 'Steel Plant Expansion',
            'text': """
            Tata Steel announces expansion of blast furnace at Jamshedpur.
            New 2 MTPA capacity. Requires furnace oil for boiler operations
            and steam generation. Commissioning Q4 2026.
            """
        },
        {
            'name': 'Bitumen Tender',
            'text': """
            Tender: Supply of 15,000 MT Bitumen VG-30 for NH-44 highway.
            Urgent requirement for road construction and paving.
            Bid closing: 20-Feb-2026.
            """
        },
        {
            'name': 'Jute Mill Expansion',
            'text': """
            Bengal Jute Mills expanding batching unit with German technology.
            Jute batch oil requirement to increase by 50% for fiber softening.
            """
        },
        {
            'name': 'Power Plant',
            'text': """
            NTPC commissions 500 MW thermal power plant in Gujarat.
            Facility has 3 boilers. Requires LSHS for emission-compliant operations.
            """
        },
        {
            'name': 'Edible Oil Plant',
            'text': """
            New solvent extraction plant for edible oil. Capacity: 100 TPD.
            Requires hexane for oil extraction from oilseeds.
            """
        },
        {
            'name': 'Marine Bunker',
            'text': """
            Shipping company seeks bunker fuel for 10 vessels at Mumbai port.
            Marine fuel requirement: HFO and MGO. Bunkering operations next month.
            """
        },
        {
            'name': 'Diesel Genset',
            'text': """
            Manufacturing facility procuring 5 x 500 KVA diesel gensets.
            HSD requirement: 10,000 liters/month for backup power.
            """
        }
    ]
    
    # Run tests
    for idx, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {idx}: {test['name']}")
        print(f"{'='*60}")
        print(f"\nInput:\n{test['text'].strip()}")
        
        # Get recommendations
        recs = engine.infer_products(test['text'], top_k=3)
        
        print(f"\n{'─'*60}")
        print("TOP 3 RECOMMENDATIONS:")
        print(f"{'─'*60}")
        
        for rank, rec in enumerate(recs, 1):
            print(f"\n#{rank} - {rec.product_name} ({rec.product_code})")
            print(f"   Confidence: {rec.confidence:.2f}")
            print(f"   Uncertainty: {rec.uncertainty}")
            print(f"   Evidence: {rec.evidence}")
            print(f"   Reason Codes:")
            for reason in rec.reason_codes:
                print(f"     • {reason}")
        
        # JSON output
        print(f"\n{'─'*60}")
        print("JSON Output:")
        print(f"{'─'*60}")
        output = {
            'test_case': test['name'],
            'recommendations': [rec.to_dict() for rec in recs]
        }
        print(json.dumps(output, indent=2))
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETED!")
    print("="*60)


if __name__ == "__main__":
    test_product_inference()