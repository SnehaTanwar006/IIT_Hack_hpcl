"""
HPCL B2B Lead Intelligence System - Production v6.1
ENHANCED: Separate output files for different source types
"""

import os
import sys
from datetime import datetime

# Add scrapers to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scrapers'))

from scrapers.eprocure_scraper import fetch_eprocure_tenders
from scrapers.google_news_scraper import fetch_google_news
from scrapers.business_directories import fetch_business_directories
from scrapers.tender_portals_scraper import fetch_tender_portals
from scrapers.gem_scraper import fetch_gem_tenders
from utils.deduplicator import deduplicate
from utils.excel_writer import write_excel
from utils.contact_finder import enrich_contacts


def main():
    """Main execution function"""
    
    print("=" * 70)
    print("🚀 HPCL B2B LEAD INTELLIGENCE v6.1 - PRODUCTION READY")
    print("=" * 70)
    print("✅ Enhanced eProcure Scraper with FULL pagination support")
    print("✅ FIXED: All scrapers now fully functional")
    print("✅ NEW: Separate output files by source type")
    print("=" * 70)
    print()
    
    # Configuration
    EPROCURE_PAGES_PER_PORTAL = 20  # Adjust based on needs (None = all pages)
    MAX_CONTACT_ENRICHMENT = 50     # Max signals to enrich (to avoid long waits)
    
    # Storage for different source types
    eprocure_signals = []
    other_tender_signals = []
    news_signals = []
    directory_signals = []
    
    print("📥 PHASE 1: DATA COLLECTION\n")
    
    # 1. eProcure (Priority - Government Tenders)
    print("🏛️ Source 1: eProcure Government Portals")
    print(f"   Scraping {EPROCURE_PAGES_PER_PORTAL} pages per portal...")
    eprocure_signals = fetch_eprocure_tenders(max_pages_per_portal=EPROCURE_PAGES_PER_PORTAL)
    print(f"   ✅ Collected: {len(eprocure_signals):,} tenders\n")
    
    # 2. GeM Portal
    print("🛒 Source 2: GeM (Government e-Marketplace)")
    gem_signals = fetch_gem_tenders()
    other_tender_signals.extend(gem_signals)
    print(f"   ✅ Collected: {len(gem_signals):,} tenders\n")
    
    # 3. Other Tender Portals
    print("📋 Source 3: Other Tender Portals")
    portal_signals = fetch_tender_portals()
    other_tender_signals.extend(portal_signals)
    print(f"   ✅ Collected: {len(portal_signals):,} leads\n")
    
    # 4. Google News
    print("📰 Source 4: Google News RSS")
    news_signals = fetch_google_news()
    print(f"   ✅ Collected: {len(news_signals):,} leads\n")
    
    # 5. Business Directories
    print("🏢 Source 5: Business Directories")
    directory_signals = fetch_business_directories()
    print(f"   ✅ Collected: {len(directory_signals):,} leads\n")
    
    # Combine all
    all_signals = eprocure_signals + other_tender_signals + news_signals + directory_signals
    
    print("=" * 70)
    print(f"📊 RAW DATA COLLECTED: {len(all_signals):,} total signals")
    print(f"   - eProcure: {len(eprocure_signals):,}")
    print(f"   - Other Tenders: {len(other_tender_signals):,}")
    print(f"   - News: {len(news_signals):,}")
    print(f"   - Directories: {len(directory_signals):,}")
    print("=" * 70)
    print()
    
    # PHASE 2: Data Cleaning
    print("⚙️ PHASE 2: DATA CLEANING & DEDUPLICATION\n")
    
    # Deduplicate each category separately
    eprocure_signals = deduplicate([s for s in eprocure_signals if len(str(s.get("Title", ""))) > 10])
    other_tender_signals = deduplicate([s for s in other_tender_signals if len(str(s.get("Title", ""))) > 10])
    news_signals = deduplicate([s for s in news_signals if len(str(s.get("Title", ""))) > 10])
    directory_signals = deduplicate([s for s in directory_signals if len(str(s.get("Title", ""))) > 10])
    
    print(f"   After cleaning & deduplication:")
    print(f"   - eProcure: {len(eprocure_signals):,}")
    print(f"   - Other Tenders: {len(other_tender_signals):,}")
    print(f"   - News: {len(news_signals):,}")
    print(f"   - Directories: {len(directory_signals):,}")
    print()
    
    # PHASE 3: Contact Enrichment
    print("=" * 70)
    print("📞 PHASE 3: CONTACT ENRICHMENT")
    print("=" * 70)
    
    # Enrich each category (prioritize tenders)
    print("\n1. Enriching eProcure tenders...")
    eprocure_signals = enrich_contacts(eprocure_signals, max_enrich=MAX_CONTACT_ENRICHMENT)
    
    print("\n2. Enriching other tenders...")
    other_tender_signals = enrich_contacts(other_tender_signals, max_enrich=MAX_CONTACT_ENRICHMENT)
    
    print("\n3. Enriching news leads...")
    news_signals = enrich_contacts(news_signals, max_enrich=MAX_CONTACT_ENRICHMENT)
    
    print("\n4. Enriching directory leads...")
    directory_signals = enrich_contacts(directory_signals, max_enrich=MAX_CONTACT_ENRICHMENT)
    
    print()
    
    # PHASE 4: Save Results
    print("=" * 70)
    print("💾 PHASE 4: SAVING RESULTS")
    print("=" * 70)
    
    os.makedirs("data", exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    output_files = []
    
    # 1. Combined eProcure file (merged CPPP, MMP, GEM)
    if eprocure_signals:
        eprocure_file = f"data/government_tenders_eprocure_{timestamp}.xlsx"
        write_excel(eprocure_signals, eprocure_file)
        output_files.append(eprocure_file)
        print(f"   ✅ eProcure file: {eprocure_file}")
    
    # 2. Other tenders file (GeM portal + TenderDetail + Tender247, etc.)
    if other_tender_signals:
        other_file = f"data/other_tender_portals_{timestamp}.xlsx"
        write_excel(other_tender_signals, other_file)
        output_files.append(other_file)
        print(f"   ✅ Other tenders file: {other_file}")
    
    # 3. News & Market Intelligence file
    if news_signals:
        news_file = f"data/news_and_market_intelligence_{timestamp}.xlsx"
        write_excel(news_signals, news_file)
        output_files.append(news_file)
        print(f"   ✅ News file: {news_file}")
    
    # 4. Business Directory Contacts file
    if directory_signals:
        directory_file = f"data/business_directory_contacts_{timestamp}.xlsx"
        write_excel(directory_signals, directory_file)
        output_files.append(directory_file)
        print(f"   ✅ Directory file: {directory_file}")
    
    # 5. Master combined file (all sources)
    all_signals = eprocure_signals + other_tender_signals + news_signals + directory_signals
    master_file = f"data/MASTER_all_leads_combined_{timestamp}.xlsx"
    write_excel(all_signals, master_file)
    output_files.append(master_file)
    print(f"   ✅ MASTER file: {master_file}")
    
    print()
    
    # PHASE 5: Analytics
    print("=" * 70)
    print("📈 PHASE 5: ANALYTICS & INSIGHTS")
    print("=" * 70)
    print_detailed_analytics(all_signals)
    
    print()
    print("=" * 70)
    print("🎉 PROCESSING COMPLETE!")
    print("=" * 70)
    print(f"\n📂 OUTPUT FILES ({len(output_files)} files created):")
    for i, file in enumerate(output_files, 1):
        print(f"   {i}. {file}")
    print(f"\n📊 Total leads: {len(all_signals):,}")
    print("=" * 70)


def print_detailed_analytics(signals):
    """Print comprehensive analytics"""
    
    # Initialize counters
    by_source = {}
    by_company = {}
    by_product = {}
    by_location = {}
    has_contact = 0
    has_email = 0
    has_phone = 0
    
    for signal in signals:
        # Source distribution
        source = signal.get("Source", "Unknown")
        by_source[source] = by_source.get(source, 0) + 1
        
        # Company distribution
        company = signal.get("Company_Name", "Unknown")[:40]
        if company and company != "Unknown Organization":
            by_company[company] = by_company.get(company, 0) + 1
        
        # Product distribution
        products = signal.get("HPCL_Products", "General Industrial")
        if products and products != "General Industrial":
            for product in products.split(","):
                product = product.strip()
                if product:
                    by_product[product] = by_product.get(product, 0) + 1
        
        # Location distribution
        locations = signal.get("Location_Clues", "")
        for loc in locations.split(";"):
            loc = loc.strip()
            if loc and len(loc) > 2:
                by_location[loc] = by_location.get(loc, 0) + 1
        
        # Contact coverage
        if signal.get("Contact_Email") or signal.get("Contact_Phone"):
            has_contact += 1
        if signal.get("Contact_Email"):
            has_email += 1
        if signal.get("Contact_Phone"):
            has_phone += 1
    
    # Print analytics
    print("\n📊 SOURCE DISTRIBUTION:")
    for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
        print(f"   {source:30}: {count:5,} ({count/len(signals)*100:5.1f}%)")
    
    if by_company:
        print("\n🏢 TOP 15 COMPANIES:")
        for company, count in sorted(by_company.items(), key=lambda x: x[1], reverse=True)[:15]:
            print(f"   {company:40}: {count:4,}")
    
    if by_product:
        print("\n🎯 HPCL PRODUCT DISTRIBUTION:")
        for product, count in sorted(by_product.items(), key=lambda x: x[1], reverse=True)[:15]:
            print(f"   {product:25}: {count:4,}")
    
    if by_location:
        print("\n📍 TOP LOCATIONS:")
        for location, count in sorted(by_location.items(), key=lambda x: x[1], reverse=True)[:15]:
            print(f"   {location:30}: {count:4,}")
    
    print("\n📞 CONTACT COVERAGE:")
    print(f"   Leads with any contact: {has_contact:,} ({has_contact/len(signals)*100:.1f}%)")
    print(f"   Leads with email:       {has_email:,} ({has_email/len(signals)*100:.1f}%)")
    print(f"   Leads with phone:       {has_phone:,} ({has_phone/len(signals)*100:.1f}%)")
    
    print(f"\n📈 TOTAL LEADS: {len(signals):,}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
