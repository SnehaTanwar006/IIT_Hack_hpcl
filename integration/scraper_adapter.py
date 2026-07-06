"""
Scraper Adapter - Converts teammate's scraper output to AI pipeline format
"""

from datetime import datetime
from typing import List, Dict
import sys
from pathlib import Path

# Add scraper to path
scraper_path = Path(__file__).parent.parent / "scraper"
sys.path.insert(0, str(scraper_path))


class ScraperAdapter:
    """Adapts scraper output to AI pipeline input format"""
    
    def __init__(self):
        pass
    
    def convert_to_pipeline_format(self, scraper_signals: List[Dict]) -> List[Dict]:
        """
        Convert scraper output to format expected by AI pipeline
        
        Args:
            scraper_signals: List of signals from teammate's scraper
        
        Returns:
            List of signals in AI pipeline format
        """
        
        converted_signals = []
        
        for signal in scraper_signals:
            # Convert to pipeline format
            pipeline_signal = {
                # Signal information (for AI processing)
                "title": signal.get("Title", ""),
                "description": signal.get("Summary", ""),
                "full_text": self._combine_text_fields(signal),
                
                # Source metadata (for provenance)
                "source_domain": self._extract_domain(signal.get("Source", "")),
                "source_url": signal.get("URL", ""),
                "source_type": self._classify_source_type(signal.get("Source", "")),
                "trust_score": signal.get("Source_Trust", 0.8),
                
                # Company information (for entity resolution)
                "company_name": signal.get("Company_Name", ""),
                "organization_name": signal.get("Organization_Name", ""),
                
                # Location (for proximity scoring)
                "location": self._extract_primary_location(signal.get("Location_Clues", "")),
                
                # Dates (for freshness scoring)
                "signal_date": self._parse_date(signal.get("e_Published_Date") or signal.get("Post_Date")),
                
                # Contact info (already enriched by scraper)
                "contact_email": signal.get("Contact_Email", ""),
                "contact_phone": signal.get("Contact_Phone", ""),
                
                # Original signal (preserve all data)
                "original_signal": signal
            }
            
            converted_signals.append(pipeline_signal)
        
        return converted_signals
    
    def _combine_text_fields(self, signal: Dict) -> str:
        """Combine all text fields for AI processing"""
        
        parts = []
        
        if signal.get("Title"):
            parts.append(signal["Title"])
        
        if signal.get("Summary"):
            parts.append(signal["Summary"])
        
        if signal.get("Full_Reference"):
            parts.append(signal["Full_Reference"])
        
        return " ".join(parts)
    
    def _extract_domain(self, source: str) -> str:
        """Extract domain from source name"""
        
        domain_map = {
            "eProcure_CPPP": "eprocure.gov.in",
            "eProcure_MMP": "mmp.gov.in",
            "GeM": "gem.gov.in",
            "GoogleNews": "news.google.com",
            "TenderDetail": "tenderdetail.com",
            "Tender247": "tender247.com"
        }
        
        return domain_map.get(source, "unknown")
    
    def _classify_source_type(self, source: str) -> str:
        """Classify source type"""
        
        if "eProcure" in source or "GeM" in source or "Tender" in source:
            return "tender"
        elif "News" in source:
            return "news"
        else:
            return "directory"
    
    def _extract_primary_location(self, location_clues: str) -> str:
        """Extract primary location from location clues"""
        
        if not location_clues:
            return ""
        
        # Split by semicolon and take first
        locations = location_clues.split(";")
        return locations[0].strip() if locations else ""
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime"""
        
        if not date_str:
            return datetime.now()
        
        try:
            # Try common formats
            from dateutil import parser
            return parser.parse(date_str)
        except:
            return datetime.now()
    
    def merge_ai_results_back(self, pipeline_signal: Dict, ai_results: Dict) -> Dict:
        """
        Merge AI results back into original scraper format
        
        Args:
            pipeline_signal: Signal in pipeline format
            ai_results: Results from AI processing (products, score, routing)
        
        Returns:
            Enhanced signal with AI results
        """
        
        # Get original signal
        enhanced = pipeline_signal["original_signal"].copy()
        
        # Add AI results
        enhanced["AI_Product_Recommendations"] = ai_results.get("products", [])
        enhanced["AI_Lead_Score"] = ai_results.get("score", {})
        enhanced["AI_Routing"] = ai_results.get("routing", {})
        enhanced["AI_Company_Profile"] = ai_results.get("company_profile", {})
        
        # Add processing metadata
        enhanced["AI_Processed_At"] = datetime.now().isoformat()
        enhanced["AI_Pipeline_Version"] = "1.0"
        
        return enhanced


def test_adapter():
    """Test the adapter"""
    
    # Sample scraper output
    scraper_signal = {
        "Source": "eProcure_CPPP",
        "Title": "Supply of High Speed Diesel for NTPC Plant",
        "Summary": "Tender for supply of 10,000 MT HSD for thermal power plant operations",
        "Company_Name": "NTPC Limited",
        "Location_Clues": "Jamshedpur; Jharkhand",
        "e_Published_Date": "2026-02-07",
        "Contact_Email": "tender@ntpc.co.in",
        "URL": "https://eprocure.gov.in/tender/123",
        "Source_Trust": 95
    }
    
    adapter = ScraperAdapter()
    
    # Convert
    pipeline_signals = adapter.convert_to_pipeline_format([scraper_signal])
    
    print("🧪 Testing Scraper Adapter\n")
    print("Input (Scraper Format):")
    print(f"  Title: {scraper_signal['Title']}")
    print(f"  Company: {scraper_signal['Company_Name']}")
    
    print("\nOutput (Pipeline Format):")
    print(f"  title: {pipeline_signals[0]['title']}")
    print(f"  company_name: {pipeline_signals[0]['company_name']}")
    print(f"  location: {pipeline_signals[0]['location']}")
    print(f"  source_type: {pipeline_signals[0]['source_type']}")


if __name__ == "__main__":
    test_adapter()