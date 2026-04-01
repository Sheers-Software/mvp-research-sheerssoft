"""
Master Pipeline Runner for Nocturn AI Lead List Generation
Orchestrates: Scrape → Enrich → Export → Summary

Run this file to generate the complete 10,000-entry HubSpot lead list.

STEPS:
1. Scrape MAH directory (hotels.org.my/members) → ~1,000 hotels
2. Run Google Places API across 34 Malaysian cities → ~5,000-8,000 hotels
3. Scrape Booking.com, Tourism Malaysia, MAHO → additional ~2,000 hotels
4. Deduplicate and merge all sources
5. Enrich with Google Places API (phone, website, rating, WhatsApp detection)
6. Export HubSpot-ready CSV with ICP scoring and segmentation

SETUP:
    pip install -r leads/requirements.txt
    set GOOGLE_PLACES_API_KEY=your_api_key_here

RUN:
    python leads/scripts/run_pipeline.py
    python leads/scripts/run_pipeline.py --skip-google  # Skip if no API key
    python leads/scripts/run_pipeline.py --resume       # Resume from checkpoint
"""

import os
import sys
import json
import argparse
import time
from datetime import datetime

# Add scripts dir to path
SCRIPTS_DIR = os.path.dirname(__file__)
sys.path.insert(0, SCRIPTS_DIR)

OUTPUT_DIR = os.path.join(SCRIPTS_DIR, "..", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

GOOGLE_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")


def load_json(path: str) -> list:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_json(data: list, path: str):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║          NOCTURN AI — LEAD LIST GENERATION PIPELINE          ║
║               Target: 10,000 ICP-Qualified Hotels            ║
║           ICP: 3-4★ Malaysian hotels, 50-300 rooms           ║
╚══════════════════════════════════════════════════════════════╝
    """)


def step1_scrape_mah():
    """Step 1: Scrape MAH member directory."""
    print("\n" + "="*60)
    print("STEP 1: MAH Directory Scrape (hotels.org.my/members)")
    print("="*60)
    
    output_path = os.path.join(OUTPUT_DIR, "mah_raw.json")
    
    if os.path.exists(output_path):
        existing = load_json(output_path)
        print(f"  Found existing MAH data: {len(existing)} hotels")
        resp = input("  Re-scrape? (y/N): ").strip().lower()
        if resp != 'y':
            return existing
    
    from scrape_mah import scrape_mah_directory, save_raw
    hotels = scrape_mah_directory()
    save_raw(hotels, "mah_raw.json")
    return hotels


def step2_scrape_multi_source(existing: list, skip_google: bool = False):
    """Step 2: Scrape additional sources."""
    print("\n" + "="*60)
    print("STEP 2: Multi-Source Scrape")
    print("="*60)
    
    output_path = os.path.join(OUTPUT_DIR, "combined_raw.json")
    
    if os.path.exists(output_path):
        existing_combined = load_json(output_path)
        print(f"  Found existing combined data: {len(existing_combined)} hotels")
        resp = input("  Re-scrape? (y/N): ").strip().lower()
        if resp != 'y':
            return existing_combined
    
    from scrape_multi_source import (
        run_google_places_scrape,
        scrape_booking_com,
        scrape_maho_directory,
        scrape_tourism_malaysia,
        dedupe_hotels,
        MALAYSIA_SEARCH_LOCATIONS,
    )
    
    all_hotels = list(existing)
    
    # Google Places (largest source)
    if not skip_google and GOOGLE_API_KEY:
        print("\n  [Google Places API] Starting systematic scrape...")
        google_hotels = run_google_places_scrape(GOOGLE_API_KEY, all_hotels)
        new_google = dedupe_hotels(google_hotels, all_hotels)
        all_hotels.extend(new_google)
        print(f"  Google Places added {len(new_google)} unique hotels. Total: {len(all_hotels)}")
        save_json(all_hotels, os.path.join(OUTPUT_DIR, "after_google.json"))
    elif skip_google:
        print("  [Google Places] Skipped (--skip-google flag)")
    else:
        print("  [Google Places] Skipped (no GOOGLE_PLACES_API_KEY set)")
    
    # Booking.com
    print("\n  [Booking.com] Scraping top cities...")
    booking_hotels = []
    for loc in MALAYSIA_SEARCH_LOCATIONS[:20]:
        print(f"    {loc['city']}...")
        bh = scrape_booking_com(loc['city'], loc['state'])
        booking_hotels.extend(bh)
        time.sleep(1)
    
    new_booking = dedupe_hotels(booking_hotels, all_hotels)
    all_hotels.extend(new_booking)
    print(f"  Booking.com added {len(new_booking)} unique hotels. Total: {len(all_hotels)}")
    save_json(all_hotels, os.path.join(OUTPUT_DIR, "after_booking.json"))
    
    # MAHO
    print("\n  [MAHO Directory] Scraping...")
    maho_hotels = scrape_maho_directory()
    new_maho = dedupe_hotels(maho_hotels, all_hotels)
    all_hotels.extend(new_maho)
    print(f"  MAHO added {len(new_maho)} unique hotels. Total: {len(all_hotels)}")
    
    # Tourism Malaysia
    print("\n  [Tourism Malaysia] Scraping...")
    tourism_hotels = scrape_tourism_malaysia()
    new_tourism = dedupe_hotels(tourism_hotels, all_hotels)
    all_hotels.extend(new_tourism)
    print(f"  Tourism Malaysia added {len(new_tourism)} unique hotels. Total: {len(all_hotels)}")
    
    save_json(all_hotels, output_path)
    print(f"\n  Combined raw data: {len(all_hotels)} hotels → {output_path}")
    return all_hotels


def step3_enrich_google_places(hotels: list, limit: int = None):
    """Step 3: Enrich with Google Places detail data."""
    print("\n" + "="*60)
    print("STEP 3: Google Places Enrichment (phone, website, rating)")
    print("="*60)
    
    output_path = os.path.join(OUTPUT_DIR, "mah_enriched.json")
    
    if os.path.exists(output_path):
        existing = load_json(output_path)
        print(f"  Found existing enriched data: {len(existing)} hotels")
        resp = input("  Re-enrich? (y/N): ").strip().lower()
        if resp != 'y':
            return existing
    
    if not GOOGLE_API_KEY:
        print("  SKIP: No GOOGLE_PLACES_API_KEY set")
        print("  Hotels will be exported without Google Places enrichment")
        # Add empty enrichment fields
        for h in hotels:
            if "google_found" not in h:
                h.update({
                    "google_found": False,
                    "google_place_id": "",
                    "google_name": "",
                    "google_address": "",
                    "google_phone": "",
                    "google_website": "",
                    "google_maps_url": "",
                    "google_rating": "",
                    "google_reviews": "",
                    "google_business_status": "",
                    "has_after_hours_gap": True,
                    "whatsapp_number": h.get("phone", ""),
                    "whatsapp_source": "mah_directory" if h.get("phone") else "",
                })
        return hotels
    
    from enrich_google_places import enrich_batch
    enriched = enrich_batch(hotels, GOOGLE_API_KEY, limit)
    save_json(enriched, output_path)
    print(f"  Enriched data saved: {len(enriched)} hotels")
    return enriched


def step4_export_csv(hotels: list):
    """Step 4: Export to HubSpot-ready CSV."""
    print("\n" + "="*60)
    print("STEP 4: Export HubSpot CSV")
    print("="*60)
    
    from export_hubspot_csv import export_to_csv, export_priority_csv, export_by_state
    
    # Main complete list
    output_path = os.path.join(OUTPUT_DIR, "nocturn_leads_complete.csv")
    count, disqualified = export_to_csv(hotels, output_path, icp_filter=0)
    print(f"  Complete list: {count} hotels → {output_path}")
    
    # ICP-qualified only (score ≥ 3 = 3-4 star, has contact info)
    qualified_path = os.path.join(OUTPUT_DIR, "nocturn_leads_icp_qualified.csv")
    qualified_count, _ = export_to_csv(hotels, qualified_path, icp_filter=3)
    print(f"  ICP qualified (≥3): {qualified_count} hotels → {qualified_path}")
    
    # By tier
    print("\n  Exporting by ICP tier...")
    export_priority_csv(hotels, OUTPUT_DIR)
    
    # By state/region
    print("\n  Exporting by state/region...")
    export_by_state(hotels, OUTPUT_DIR)
    
    return count


def print_final_summary(hotels: list, csv_count: int):
    """Print comprehensive summary of the lead generation run."""
    from export_hubspot_csv import determine_icp_tier, is_whatsapp_likely
    
    hot = sum(1 for h in hotels if determine_icp_tier(h.get("icp_score", 0)) == "HOT")
    warm = sum(1 for h in hotels if determine_icp_tier(h.get("icp_score", 0)) == "WARM")
    cold = sum(1 for h in hotels if determine_icp_tier(h.get("icp_score", 0)) == "COLD")
    
    has_whatsapp = sum(1 for h in hotels if is_whatsapp_likely(h.get("whatsapp_number", "")))
    has_email = sum(1 for h in hotels if h.get("email"))
    has_both = sum(1 for h in hotels if is_whatsapp_likely(h.get("whatsapp_number", "")) and h.get("email"))
    
    # State breakdown
    from collections import Counter
    states = Counter(h.get("state", "Unknown") for h in hotels)
    
    # Source breakdown
    sources = Counter(h.get("source", "Unknown") for h in hotels)
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    LEAD LIST COMPLETE                        ║
╠══════════════════════════════════════════════════════════════╣
║  VOLUME                                                      ║
║  Total hotels discovered:  {len(hotels):>6,}                         ║
║  Exported to CSV:          {csv_count:>6,}                         ║
║                                                              ║
║  ICP TIERS                                                   ║
║  🔴 HOT  (score ≥8):       {hot:>6,}  → Outreach immediately    ║
║  🟡 WARM (score ≥5):       {warm:>6,}  → Outreach within 1 week  ║
║  🟢 COLD (score ≥3):       {cold:>6,}  → Nurture sequence        ║
║                                                              ║
║  CONTACT COVERAGE                                            ║
║  Has WhatsApp number:      {has_whatsapp:>6,}                         ║
║  Has email address:        {has_email:>6,}                         ║
║  Has both WA + email:      {has_both:>6,}                         ║
╠══════════════════════════════════════════════════════════════╣
║  TOP STATES                                                  ║""")
    
    for state, count in states.most_common(5):
        print(f"║  {state:<20} {count:>6,}                         ║")
    
    print(f"""╠══════════════════════════════════════════════════════════════╣
║  SOURCES                                                     ║""")
    
    for source, count in sources.most_common():
        print(f"║  {source:<30} {count:>6,}                   ║")
    
    print(f"""╠══════════════════════════════════════════════════════════════╣
║  OUTPUT FILES (in leads/output/)                             ║
║  nocturn_leads_complete.csv     → All hotels                 ║
║  nocturn_leads_icp_qualified.csv→ ICP score ≥ 3              ║
║  nocturn_leads_hot.csv          → Immediate outreach         ║
║  nocturn_leads_warm.csv         → 1-week sequence            ║
║  nocturn_leads_cold.csv         → Nurture sequence           ║
║  nocturn_leads_klang_valley.csv → KL/Selangor segment        ║
║  nocturn_leads_penang.csv       → Penang segment             ║
║  nocturn_leads_johor.csv        → Johor segment              ║
║                                                              ║
║  HUBSPOT IMPORT: Contacts → Import → From file → Select CSV  ║
╚══════════════════════════════════════════════════════════════╝
    """)


def main():
    parser = argparse.ArgumentParser(description="Nocturn AI Lead List Generation Pipeline")
    parser.add_argument("--skip-google", action="store_true", help="Skip Google Places API calls")
    parser.add_argument("--skip-enrich", action="store_true", help="Skip detail enrichment step")
    parser.add_argument("--resume", action="store_true", help="Resume from latest checkpoint")
    parser.add_argument("--enrich-limit", type=int, default=None, help="Limit enrichment to N hotels")
    parser.add_argument("--export-only", action="store_true", help="Skip scraping, only export from existing data")
    args = parser.parse_args()
    
    print_banner()
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Google API Key: {'✓ SET' if GOOGLE_API_KEY else '✗ NOT SET (set GOOGLE_PLACES_API_KEY)'}")
    print(f"  Output dir: {OUTPUT_DIR}")
    
    if args.export_only:
        # Load best available data
        for fname in ["mah_enriched.json", "combined_raw.json", "mah_raw.json"]:
            fpath = os.path.join(OUTPUT_DIR, fname)
            if os.path.exists(fpath):
                hotels = load_json(fpath)
                print(f"\nLoaded {len(hotels)} hotels from {fname}")
                break
        else:
            print("ERROR: No data files found. Run without --export-only first.")
            return
    else:
        # Full pipeline
        mah_hotels = step1_scrape_mah()
        all_hotels = step2_scrape_multi_source(mah_hotels, skip_google=args.skip_google)
        
        if not args.skip_enrich:
            hotels = step3_enrich_google_places(all_hotels, args.enrich_limit)
        else:
            hotels = all_hotels
    
    csv_count = step4_export_csv(hotels if not args.export_only else locals().get('hotels', []))
    print_final_summary(hotels if not args.export_only else locals().get('hotels', []), csv_count)
    
    print(f"\n  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
