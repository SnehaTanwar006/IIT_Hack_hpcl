"""
Pipeline Orchestrator - Runs scraper + AI pipeline together
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "scrapper"))
sys.path.insert(0, str(project_root / "src"))

# Import AI components ONLY
from entity_resolution.company_profile import CompanyProfileBuilder
from product_inference.inference_engine import ProductInferenceEngine
from lead_scoring.lead_scorer import LeadScorer
from lead_scoring.territory_router import TerritoryRouter

# Import adapter
from integration.scraper_adapter import ScraperAdapter


class IntegratedPipeline:
    """Orchestrates scraper + AI pipeline"""
    
    def __init__(self):
        # Initialize adapter
        self.adapter = ScraperAdapter()
        
        # Initialize AI components
        self.profile_builder = CompanyProfileBuilder()
        self.product_engine = ProductInferenceEngine()
        self.lead_scorer = LeadScorer()
        self.territory_router = TerritoryRouter()
    
    def run_full_pipeline(self, max_signals: int = 100):
        """
        Run complete integrated pipeline
        
        Args:
            max_signals: Maximum signals to process (for demo)
        
        Returns:
            List of fully processed leads
        """
        
        print("="*70)
        print("INTEGRATED PIPELINE: SCRAPER + AI")
        print("="*70)
        print()
        
        # PHASE 1: Web Scraping
        print("PHASE 1: WEB SCRAPING")
        print("─"*70)
        
        raw_signals = self._run_scraper(max_signals)
        
        print(f"Scraped {len(raw_signals)} signals")
        print()
        
        # PHASE 2: Convert to pipeline format
        print("PHASE 2: FORMAT CONVERSION")
        print("─"*70)
        
        pipeline_signals = self.adapter.convert_to_pipeline_format(raw_signals)
        
        print(f"Converted {len(pipeline_signals)} signals to AI format")
        print()
        
        # PHASE 3: AI Processing
        print("PHASE 3: AI PROCESSING")
        print("─"*70)
        
        processed_leads = []
        
        for i, signal in enumerate(pipeline_signals[:max_signals], 1):
            try:
                # Entity Resolution
                company_profile = self.profile_builder.build_profile(
                    company_name=signal["company_name"],
                    industry=None,
                    location=signal["location"]
                )
                
                # Product Inference
                product_recs = self.product_engine.infer_products(
                    text=signal["full_text"],
                    top_k=3
                )
                
                # Lead Scoring
                lead_score = self.lead_scorer.score_lead(
                    text=signal["full_text"],
                    signal_date=signal["signal_date"],
                    company_name=signal["company_name"],
                    location=signal["location"]
                )
                
                # Routing
                routing = self.territory_router.route_lead(
                    location=signal["location"],
                    industry=company_profile.get("industry"),
                    nearest_depot=lead_score.breakdown["proximity"]["nearest_depot"]
                )
                
                # Combine results
                ai_results = {
                    "company_profile": company_profile,
                    "products": [rec.to_dict() for rec in product_recs],
                    "score": lead_score.to_dict(),
                    "routing": routing
                }
                
                # Merge back to original format
                enhanced_signal = self.adapter.merge_ai_results_back(signal, ai_results)
                
                processed_leads.append(enhanced_signal)
                
                # Progress
                if i % 10 == 0:
                    print(f"  Processed {i}/{min(len(pipeline_signals), max_signals)} signals...")
                
            except Exception as e:
                print(f"Error processing signal {i}: {e}")
                continue
        
        print(f"AI processing complete: {len(processed_leads)} leads")
        print()
        
        return processed_leads
    
    def _run_scraper(self, max_signals: int) -> List[Dict]:
        """Run scraper and return signals (with fallback to simulated data)"""
        
        print("Attempting to run scraper...")
        
        # Try to import and run scraper
        try:
            # Dynamic imports (inside function to avoid import errors)
            from scrapers.eprocure_scraper import fetch_eprocure_tenders
            from scrapers.gem_scraper import fetch_gem_tenders
            from scrapers.google_news_scraper import fetch_google_news
            from utils.deduplicator import deduplicate
            
            print("    - Running eProcure scraper...")
            eprocure_signals = fetch_eprocure_tenders(max_pages_per_portal=2)
            
            print("    - Running GeM scraper...")
            gem_signals = fetch_gem_tenders()
            
            print("    - Running Google News scraper...")
            news_signals = fetch_google_news()
            
            # Combine
            all_signals = eprocure_signals + gem_signals + news_signals
            
            # Deduplicate
            all_signals = deduplicate(all_signals)
            
            print(f"Live scraper successful!")
            return all_signals[:max_signals]
        
        except Exception as e:
            print(f"Scraper not available: {e}")
            print(f"Using simulated data for demo...")
            return self._get_simulated_data()[:max_signals]
    
    def _get_simulated_data(self) -> List[Dict]:
        """Fallback: Return simulated scraper data"""
        
        return [
            {
                "Source": "eProcure_CPPP",
                "Title": "Supply of High Speed Diesel for NTPC Plant",
                "Summary": "Tender for supply of 10,000 MT HSD for thermal power plant operations",
                "Full_Reference": "NTPC invites bids for HSD supply",
                "Company_Name": "NTPC Limited",
                "Organization_Name": "NTPC",
                "Location_Clues": "Jamshedpur; Jharkhand",
                "e_Published_Date": "2026-02-07",
                "Contact_Email": "tender@ntpc.co.in",
                "URL": "https://eprocure.gov.in/tender/123",
                "Source_Trust": 95
            },
            {
                "Source": "GeM",
                "Title": "Tender for Bitumen VG-30 for NH-44 Highway Project",
                "Summary": "Supply of 15,000 MT Bitumen for road construction",
                "Full_Reference": "NHAI requires Bitumen VG-30 for highway project",
                "Company_Name": "NHAI",
                "Organization_Name": "National Highways Authority",
                "Location_Clues": "Vadodara; Gujarat",
                "e_Published_Date": "2026-02-07",
                "Contact_Email": "tenders@nhai.gov.in",
                "URL": "https://gem.gov.in/tender/456",
                "Source_Trust": 100
            },
            {
                "Source": "GoogleNews",
                "Title": "Tata Steel announces ₹5,000 crore expansion",
                "Summary": "New blast furnace to add 2 MTPA capacity",
                "Full_Reference": "Tata Steel expansion with new blast furnace",
                "Company_Name": "Tata Steel Limited",
                "Organization_Name": "Tata Steel",
                "Location_Clues": "Jamshedpur; Jharkhand",
                "Post_Date": "2026-02-06",
                "URL": "https://economictimes.com/article/12345",
                "Source_Trust": 95
            },
            {
                "Source": "eProcure_MMP",
                "Title": "Jute Batch Oil requirement for Bengal Jute Mills",
                "Summary": "Supply of JBO for jute processing",
                "Full_Reference": "Bengal Jute Mills expanding batching unit",
                "Company_Name": "Bengal Jute Mills",
                "Organization_Name": "Bengal Jute",
                "Location_Clues": "Kolkata; West Bengal",
                "e_Published_Date": "2026-01-31",
                "URL": "https://mmp.gov.in/tender/789",
                "Source_Trust": 90
            },
            {
                "Source": "TenderDetail",
                "Title": "Marine Bunker Fuel for Shipping Corporation",
                "Summary": "Supply of LSHS and HSD for vessels",
                "Full_Reference": "Shipping Corporation requires marine bunker fuel",
                "Company_Name": "Shipping Corporation of India",
                "Organization_Name": "SCI",
                "Location_Clues": "Mumbai; Maharashtra",
                "e_Published_Date": "2026-02-05",
                "URL": "https://tenderdetail.com/tender/999",
                "Source_Trust": 85
            }
        ]   