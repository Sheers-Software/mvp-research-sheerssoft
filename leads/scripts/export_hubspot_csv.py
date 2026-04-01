"""
HubSpot-Ready Lead List Exporter for Nocturn AI
Converts enriched hotel data into a HubSpot-compatible CSV with all fields
for CRM automation, WhatsApp sequences, and email campaigns.

HubSpot Field Mapping:
- Contact-level fields (GM, Revenue Manager, Reservation Manager)
- Company-level fields (Hotel property)
- Deal-level fields (Pilot pipeline)
- Custom Nocturn AI fields for segmentation and automation

Usage:
    python export_hubspot_csv.py --input mah_enriched.json --output nocturn_leads.csv
"""

import json
import csv
import os
import re
import argparse
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# HubSpot standard + custom field definitions
HUBSPOT_FIELDS = [
    # === COMPANY FIELDS ===
    "company",                        # Hotel name (HubSpot Company Name)
    "company_domain_name",           # Website domain
    "phone",                          # Main hotel phone (HubSpot standard)
    "address",                        # Street address
    "city",                           # City
    "state",                          # State/Region
    "country",                        # Country (Malaysia)
    "zip",                            # Postcode
    "industry",                       # Hospitality
    "type",                           # PROSPECT
    "numberofemployees",              # Estimated from room count
    "website",                        # Hotel website URL
    
    # === CONTACT-LEVEL FIELDS ===
    "firstname",                      # Contact first name (if known)
    "lastname",                       # Contact last name (if known)
    "jobtitle",                       # Role: GM / Revenue Manager / Reservation Manager
    "email",                          # Contact email
    "mobilephone",                    # WhatsApp number (HubSpot mobile field)
    
    # === NOCTURN AI CUSTOM FIELDS ===
    "nocturn_icp_score",             # ICP fit score (0-10)
    "nocturn_icp_tier",              # Tier: HOT / WARM / COLD
    "nocturn_star_rating",           # 3 Star / 4 Star
    "nocturn_room_count",            # Number of rooms
    "nocturn_has_whatsapp",         # YES / NO
    "nocturn_whatsapp_number",       # Actual WhatsApp number
    "nocturn_whatsapp_source",       # mah_directory / google_places / manual
    "nocturn_has_email",             # YES / NO
    "nocturn_after_hours_gap",       # YES / NO (AI inferred)
    "nocturn_google_rating",         # Google Maps rating
    "nocturn_google_reviews",        # Review count
    "nocturn_google_maps_url",       # Direct Google Maps link
    "nocturn_member_id",             # MAH member ID
    "nocturn_source",                # Data source (MAH / Google / Manual)
    "nocturn_outreach_priority",     # 1=Highest to 5=Lowest
    "nocturn_outreach_channel",      # WhatsApp / Email / LinkedIn / Phone
    "nocturn_pilot_roi_estimate",    # Estimated monthly revenue recovery (RM)
    "nocturn_adr_estimate",          # Estimated ADR (Average Daily Rate)
    "nocturn_pilot_status",          # Not Started / Contacted / Demo Booked / etc.
    "nocturn_pilot_start_date",      # When pilot begins
    "nocturn_first_touch_template",  # Which template to use (1A/1B/1C/1D)
    "nocturn_notes",                 # Additional context
    "nocturn_data_collected_date",   # When lead was collected
    
    # === LIFECYCLE & PIPELINE ===
    "lifecyclestage",                # subscriber/lead/marketingqualifiedlead/etc.
    "hs_lead_status",                # NEW / IN PROGRESS / OPEN DEAL / etc.
    "lead_source",                   # HOW they were found
    "lead_source_detail",            # Specific source detail
]


# ADR estimates by hotel tier and city (RM)
ADR_ESTIMATES = {
    ("3 Star", "Kuala Lumpur"): 160,
    ("3 Star", "Penang"): 140,
    ("3 Star", "Johor Bahru"): 130,
    ("3 Star", "Kota Kinabalu"): 150,
    ("3 Star", "Other"): 120,
    ("4 Star", "Kuala Lumpur"): 250,
    ("4 Star", "Penang"): 220,
    ("4 Star", "Johor Bahru"): 200,
    ("4 Star", "Kota Kinabalu"): 220,
    ("4 Star", "Other"): 180,
}

def estimate_adr(star_rating: str, state: str, city: str) -> int:
    """Estimate ADR based on star rating and location."""
    city_key = city if city in ["Kuala Lumpur", "Penang", "Johor Bahru", "Kota Kinabalu"] else "Other"
    star_key = star_rating if star_rating in ["3 Star", "4 Star"] else "3 Star"
    return ADR_ESTIMATES.get((star_key, city_key), 150)


def estimate_roi(num_rooms, adr: int, daily_inquiries_estimate: int = None) -> int:
    """
    Estimate monthly revenue recovery potential.
    Formula: daily_inquiries × 0.30 (after-hours) × 0.20 (conversion) × ADR × 30
    """
    if not daily_inquiries_estimate:
        # Estimate daily inquiries from room count
        if not num_rooms:
            num_rooms = 100
        daily_inquiries_estimate = max(10, int(num_rooms * 0.3))
    
    monthly_roi = daily_inquiries_estimate * 0.30 * 0.20 * adr * 30
    return int(monthly_roi)


def determine_icp_tier(icp_score: int) -> str:
    """Map ICP score to tier."""
    if icp_score >= 8:
        return "HOT"
    elif icp_score >= 5:
        return "WARM"
    elif icp_score >= 3:
        return "COLD"
    else:
        return "DISQUALIFIED"


def determine_outreach_priority(hotel: dict) -> int:
    """
    Determine outreach priority (1=highest, 5=lowest).
    Based on ICP score, state, and available contact channels.
    """
    score = hotel.get("icp_score", 0)
    state = hotel.get("state", "")
    has_whatsapp = hotel.get("is_mobile_whatsapp") or is_whatsapp_likely(hotel.get("whatsapp_number", ""))
    has_email = bool(hotel.get("email"))
    
    # Primary states get priority boost
    primary_states = {"Kuala Lumpur", "Selangor"}
    secondary_states = {"Penang", "Johor", "Sabah"}
    
    priority = 5  # Default: lowest
    
    if score >= 8 and has_whatsapp:
        priority = 1
    elif score >= 7 and (has_whatsapp or state in primary_states):
        priority = 2
    elif score >= 5:
        priority = 3
    elif score >= 3:
        priority = 4
    else:
        priority = 5
    
    # Boost if primary state
    if state in primary_states and priority > 2:
        priority -= 1
    elif state in secondary_states and priority > 3:
        priority -= 1
    
    return max(1, priority)


def determine_outreach_channel(hotel: dict) -> str:
    """Determine best first-touch outreach channel."""
    has_whatsapp = is_whatsapp_likely(hotel.get("whatsapp_number", ""))
    has_email = bool(hotel.get("email"))
    
    if has_whatsapp:
        return "WhatsApp"
    elif has_email:
        return "Email"
    else:
        return "Phone"


def determine_template(hotel: dict, outreach_channel: str) -> str:
    """Select the appropriate first-touch template."""
    if outreach_channel == "WhatsApp":
        return "1B"  # WhatsApp cold named contact
    elif outreach_channel == "Email":
        return "1C"  # Email cold outreach
    else:
        return "1D"  # LinkedIn / phone


def is_whatsapp_likely(phone: str) -> bool:
    """Check if phone is a Malaysian mobile number."""
    if not phone:
        return False
    return bool(re.match(r'^\+?601[0-9]', phone.replace(' ', '')))


def extract_domain(website: str) -> str:
    """Extract clean domain from URL."""
    if not website:
        return ""
    # Remove protocol and www
    domain = re.sub(r'^https?://(www\.)?', '', website)
    # Remove path
    domain = domain.split('/')[0]
    return domain.lower()


def extract_postcode(address: str) -> str:
    """Extract Malaysian postcode from address."""
    match = re.search(r'\b(\d{5})\b', address)
    return match.group(1) if match else ""


def estimate_employees(num_rooms) -> int:
    """Estimate number of employees based on room count."""
    if not num_rooms:
        return 50
    # Industry average: ~0.8-1.2 staff per room for 3-4 star
    return int(num_rooms * 1.0)


def hotel_to_hubspot_row(hotel: dict) -> dict:
    """Convert a hotel dict to a HubSpot row."""
    hotel_name = hotel.get("hotel_name", "")
    state = hotel.get("state", "")
    city = hotel.get("city", "")
    star_rating = hotel.get("star_rating", "")
    num_rooms = hotel.get("num_rooms", "")
    phone = hotel.get("phone", "")
    email = hotel.get("email", "")
    website = hotel.get("website") or hotel.get("google_website", "")
    address = hotel.get("address") or hotel.get("google_address", "")
    whatsapp = hotel.get("whatsapp_number", "")
    icp_score = hotel.get("icp_score", 0)
    
    # Calculated fields
    adr = estimate_adr(star_rating, state, city)
    roi = estimate_roi(num_rooms, adr)
    icp_tier = determine_icp_tier(icp_score)
    outreach_channel = determine_outreach_channel(hotel)
    outreach_priority = determine_outreach_priority(hotel)
    template = determine_template(hotel, outreach_channel)
    
    # Main hotel phone (prefer landline for company record, mobile for contact)
    main_phone = phone or whatsapp
    
    # Lifecycle stage based on ICP tier
    lifecycle = "marketingqualifiedlead" if icp_tier in ["HOT", "WARM"] else "lead"
    
    # Lead status
    lead_status = "NEW"
    
    row = {
        # Company fields
        "company": hotel_name,
        "company_domain_name": extract_domain(website),
        "phone": main_phone,
        "address": address,
        "city": city,
        "state": state,
        "country": "Malaysia",
        "zip": extract_postcode(address),
        "industry": "Hospitality",
        "type": "PROSPECT",
        "numberofemployees": estimate_employees(num_rooms),
        "website": website,
        
        # Contact fields (GM-level placeholder - to be enriched with LinkedIn)
        "firstname": "",
        "lastname": "",
        "jobtitle": "General Manager",
        "email": email,
        "mobilephone": whatsapp,
        
        # Nocturn AI custom fields
        "nocturn_icp_score": icp_score,
        "nocturn_icp_tier": icp_tier,
        "nocturn_star_rating": star_rating,
        "nocturn_room_count": num_rooms if num_rooms else "",
        "nocturn_has_whatsapp": "YES" if is_whatsapp_likely(whatsapp) else "NO",
        "nocturn_whatsapp_number": whatsapp,
        "nocturn_whatsapp_source": hotel.get("whatsapp_source", ""),
        "nocturn_has_email": "YES" if email else "NO",
        "nocturn_after_hours_gap": "YES" if hotel.get("has_after_hours_gap", True) else "NO",
        "nocturn_google_rating": hotel.get("google_rating", ""),
        "nocturn_google_reviews": hotel.get("google_reviews", ""),
        "nocturn_google_maps_url": hotel.get("google_maps_url", ""),
        "nocturn_member_id": hotel.get("member_id", ""),
        "nocturn_source": hotel.get("source", "MAH Directory"),
        "nocturn_outreach_priority": outreach_priority,
        "nocturn_outreach_channel": outreach_channel,
        "nocturn_pilot_roi_estimate": roi,
        "nocturn_adr_estimate": adr,
        "nocturn_pilot_status": "Not Started",
        "nocturn_pilot_start_date": "",
        "nocturn_first_touch_template": template,
        "nocturn_notes": hotel.get("icp_flags", ""),
        "nocturn_data_collected_date": datetime.now().strftime("%Y-%m-%d"),
        
        # Lifecycle & pipeline
        "lifecyclestage": lifecycle,
        "hs_lead_status": lead_status,
        "lead_source": "MAH Directory Scrape",
        "lead_source_detail": f"hotels.org.my/members - Scraped {datetime.now().strftime('%Y-%m-%d')}",
    }
    
    return row


def export_to_csv(hotels: list[dict], output_path: str, icp_filter: int = 0) -> tuple[int, int]:
    """
    Export hotels to HubSpot-ready CSV.
    
    Args:
        hotels: List of hotel dicts
        output_path: Output CSV file path
        icp_filter: Minimum ICP score to include (0 = include all)
    
    Returns:
        Tuple of (total_exported, disqualified_count)
    """
    filtered = [h for h in hotels if h.get("icp_score", 0) >= icp_filter] if icp_filter else hotels
    disqualified = len(hotels) - len(filtered)
    
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:  # utf-8-sig for Excel compatibility
        writer = csv.DictWriter(f, fieldnames=HUBSPOT_FIELDS, extrasaction='ignore')
        writer.writeheader()
        
        for hotel in filtered:
            try:
                row = hotel_to_hubspot_row(hotel)
                writer.writerow(row)
            except Exception as e:
                print(f"  Warning: Error exporting {hotel.get('hotel_name', '?')}: {e}")
    
    return len(filtered), disqualified


def export_priority_csv(hotels: list[dict], output_dir: str):
    """Export separate CSVs by priority tier for targeted sequences."""
    tiers = {
        "HOT": lambda h: determine_icp_tier(h.get("icp_score", 0)) == "HOT",
        "WARM": lambda h: determine_icp_tier(h.get("icp_score", 0)) == "WARM",
        "COLD": lambda h: determine_icp_tier(h.get("icp_score", 0)) == "COLD",
    }
    
    for tier_name, filter_fn in tiers.items():
        tier_hotels = [h for h in hotels if filter_fn(h)]
        if tier_hotels:
            filepath = os.path.join(output_dir, f"nocturn_leads_{tier_name.lower()}.csv")
            count, _ = export_to_csv(tier_hotels, filepath, icp_filter=0)
            print(f"  {tier_name} tier: {count} hotels → {filepath}")


def export_by_state(hotels: list[dict], output_dir: str):
    """Export separate CSVs by state for geographic targeting."""
    primary_states = ["Kuala Lumpur", "Selangor", "Penang", "Johor", "Sabah"]
    
    # KL + Selangor combined (same metro area)
    klang_valley = [h for h in hotels if h.get("state") in ["Kuala Lumpur", "Selangor"]]
    penang = [h for h in hotels if h.get("state") == "Penang"]
    johor = [h for h in hotels if h.get("state") == "Johor"]
    sabah = [h for h in hotels if h.get("state") == "Sabah"]
    sarawak = [h for h in hotels if h.get("state") == "Sarawak"]
    others = [h for h in hotels if h.get("state") not in primary_states + ["Sarawak"]]
    
    groups = [
        ("klang_valley", klang_valley),
        ("penang", penang),
        ("johor", johor),
        ("sabah", sabah),
        ("sarawak", sarawak),
        ("others", others),
    ]
    
    for name, group in groups:
        if group:
            filepath = os.path.join(output_dir, f"nocturn_leads_{name}.csv")
            count, _ = export_to_csv(group, filepath, icp_filter=0)
            print(f"  {name.replace('_', ' ').title()}: {count} hotels → {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Export hotel leads to HubSpot CSV")
    parser.add_argument("--input", default="mah_enriched.json", help="Input JSON file (in output dir)")
    parser.add_argument("--output", default="nocturn_leads_all.csv", help="Main output CSV filename")
    parser.add_argument("--icp-min", type=int, default=0, help="Minimum ICP score filter (default: 0 = all)")
    parser.add_argument("--split-tiers", action="store_true", help="Also export split by ICP tier")
    parser.add_argument("--split-states", action="store_true", help="Also export split by state")
    args = parser.parse_args()
    
    # Load input
    # Try enriched first, fall back to raw
    input_options = [args.input, "mah_enriched.json", "mah_raw.json"]
    hotels = None
    for option in input_options:
        input_path = os.path.join(OUTPUT_DIR, option)
        if os.path.exists(input_path):
            with open(input_path, 'r', encoding='utf-8') as f:
                hotels = json.load(f)
            print(f"Loaded {len(hotels)} hotels from {input_path}")
            break
    
    if not hotels:
        print("ERROR: No input data found. Run scrape_mah.py first.")
        return
    
    # Main export
    output_path = os.path.join(OUTPUT_DIR, args.output)
    count, disqualified = export_to_csv(hotels, output_path, args.icp_min)
    print(f"\nMain CSV exported: {count} hotels → {output_path}")
    print(f"Excluded (below ICP min {args.icp_min}): {disqualified}")
    
    # Split exports
    if args.split_tiers:
        print("\nExporting by ICP tier...")
        export_priority_csv(hotels, OUTPUT_DIR)
    
    if args.split_states:
        print("\nExporting by state/region...")
        export_by_state(hotels, OUTPUT_DIR)
    
    # Print summary stats
    hot = sum(1 for h in hotels if determine_icp_tier(h.get("icp_score", 0)) == "HOT")
    warm = sum(1 for h in hotels if determine_icp_tier(h.get("icp_score", 0)) == "WARM")
    cold = sum(1 for h in hotels if determine_icp_tier(h.get("icp_score", 0)) == "COLD")
    has_whatsapp = sum(1 for h in hotels if is_whatsapp_likely(h.get("whatsapp_number", "")))
    has_email = sum(1 for h in hotels if h.get("email"))
    
    print(f"\n=== LEAD LIST SUMMARY ===")
    print(f"Total leads:        {len(hotels)}")
    print(f"HOT (score ≥8):    {hot}")
    print(f"WARM (score ≥5):   {warm}")
    print(f"COLD (score ≥3):   {cold}")
    print(f"Has WhatsApp:       {has_whatsapp}")
    print(f"Has Email:          {has_email}")
    print(f"\nHubSpot import: Go to Contacts → Import → CSV file → select '{args.output}'")
    print(f"Map columns: 'company'→Company Name, 'email'→Email, 'mobilephone'→Mobile Phone")


if __name__ == "__main__":
    main()
