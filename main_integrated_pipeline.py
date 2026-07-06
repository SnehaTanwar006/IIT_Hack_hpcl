"""
HPCL Lead Intelligence - COMPLETE INTEGRATED SYSTEM
Combines scraper data with AI/ML pipeline
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add integration to path
sys.path.insert(0, str(Path(__file__).parent))

from integration.pipeline_orchestrator import IntegratedPipeline


def main():
    """Run complete integrated pipeline"""
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     HPCL B2B LEAD INTELLIGENCE - INTEGRATED SYSTEM v1.0         ║
║                                                                  ║
║  Scraper (Teammate) + AI/ML Pipeline (You) = Complete Solution  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize pipeline
    pipeline = IntegratedPipeline()
    
    # Run with demo limits (change for production)
    MAX_SIGNALS = 100  # Process up to 100 signals
    
    leads = pipeline.run_full_pipeline(max_signals=MAX_SIGNALS)
    
    # Save results
    print("\nSAVING RESULTS")
    print("─"*70)
    
    # Create output directory
    Path("output").mkdir(exist_ok=True)
    
    # Save as JSON
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"output/leads_with_AI_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(leads, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\nComplete! Output: {output_file}")
    print(f"Total leads: {len(leads)}")
    
    # Display summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    # Count by priority
    priorities = {}
    for lead in leads:
        priority = lead.get("AI_Lead_Score", {}).get("priority", "UNKNOWN")
        priorities[priority] = priorities.get(priority, 0) + 1
    
    print("\nLeads by Priority:")
    for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = priorities.get(priority, 0)
        if count > 0:
            print(f"  {priority}: {count}")
    
    # Show sample leads
    print("\nSample Leads:")
    for i, lead in enumerate(leads[:3], 1):
        print(f"\n{i}. {lead.get('Company_Name', 'Unknown')}")
        print(f"   Title: {lead.get('Title', '')[:60]}...")
        
        if lead.get("AI_Product_Recommendations"):
            top = lead["AI_Product_Recommendations"][0]
            print(f"   Product: {top['product_name']} ({top['confidence']:.0%})")
        
        if lead.get("AI_Lead_Score"):
            score = lead['AI_Lead_Score']
            print(f"   Score: {score['total_score']}/90 ({score['priority']})")
        
        if lead.get("AI_Routing"):
            print(f"   Assigned: {lead['AI_Routing']['assigned_officer']}")
    
    print("\n" + "="*70)
    print("PIPELINE COMPLETE!")
    print("="*70)
    print(f"\nOutput file: {output_file}")
    print(f"Total leads processed: {len(leads)}")
    
    # Show file location
    full_path = Path(output_file).absolute()
    print(f"Full path: {full_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)