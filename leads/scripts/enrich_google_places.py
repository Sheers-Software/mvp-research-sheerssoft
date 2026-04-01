"""
Google Places API Enrichment for Hotel Lead List
Enriches each hotel with:
- Verified phone number (often mobile/WhatsApp-enabled)
- Website URL
- Google Maps URL (useful for outreach personalization)
- Rating and review count (quality signal)
- Business status (OPERATIONAL vs CLOSED)
- Opening hours patterns (detect after-hours gap)

Requirements:
- GOOGLE_PLACES_API_KEY environment variable
- pip install googlemaps requests

Usage:
    python enrich_google_places.py --input mah_raw.json --output mah_enriched.json
    python enrich_google_places.py --input mah_raw.json --limit 100  # for testing
"""

import os
import json
import time
import argparse
import re
from datetime import datetime

try:
    import googlemaps
    GOOGLEMAPS_AVAILABLE = True
except ImportError:
    print("WARNING: googlemaps not installed. Run: pip install googlemaps")
    GOOGLEMAPS_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    print("WARNING: requests not installed. Run: pip install requests")
    REQUESTS_AVAILABLE = False

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")

# Rate limiting: 10 requests/second for Places API
REQUEST_DELAY = 0.12  # seconds between requests
MAX_RETRIES = 3


def clean_phone(phone: str) -> str:
    """Normalize to international Malaysian format."""
    phone = re.sub(r'[\s\-\(\)\.]', '', phone)
    if phone.startswith('0'):
        phone = '+60' + phone[1:]
    elif phone.startswith('60') and not phone.startswith('+60'):
        phone = '+' + phone
    return phone


def is_whatsapp_likely(phone: str) -> bool:
    """Check if phone is a Malaysian mobile number (WhatsApp-enabled)."""
    return bool(re.match(r'^\+?601[0-9]', phone.replace(' ', '')))


def search_place(gmaps_client, hotel_name: str, state: str, city: str) -> dict | None:
    """Search for hotel on Google Places API."""
    query = f"{hotel_name} hotel {city} {state} Malaysia"
    
    for attempt in range(MAX_RETRIES):
        try:
            result = gmaps_client.find_place(
                input=query,
                input_type="textquery",
                fields=["place_id", "name", "formatted_address", "geometry"],
                language="en"
            )
            
            candidates = result.get("candidates", [])
            if candidates:
                return candidates[0]
            
            # Fallback: text search
            result2 = gmaps_client.places(
                query=query,
                language="en",
                type="lodging"
            )
            results = result2.get("results", [])
            if results:
                return results[0]
            
            return None
            
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  Error searching for {hotel_name}: {e}")
                return None


def get_place_details(gmaps_client, place_id: str) -> dict:
    """Get detailed information for a place."""
    fields = [
        "name", "formatted_address", "formatted_phone_number",
        "international_phone_number", "website", "url",
        "rating", "user_ratings_total", "business_status",
        "opening_hours", "types", "vicinity"
    ]
    
    for attempt in range(MAX_RETRIES):
        try:
            result = gmaps_client.place(
                place_id=place_id,
                fields=fields,
                language="en"
            )
            return result.get("result", {})
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  Error getting details for place {place_id}: {e}")
                return {}
    
    return {}


def infer_after_hours_gap(opening_hours: dict) -> bool:
    """
    Infer if property likely has after-hours gap.
    Returns True if closing time is before 10pm on weekdays.
    """
    if not opening_hours:
        return True  # Assume gap if no hours available
    
    periods = opening_hours.get("periods", [])
    for period in periods:
        close = period.get("close", {})
        close_time = close.get("time", "2300")
        # If closes before 22:00 (10pm), likely has after-hours gap
        try:
            if int(close_time) < 2200:
                return True
        except:
            pass
    
    return False


def enrich_hotel(gmaps_client, hotel: dict) -> dict:
    """Enrich a single hotel entry with Google Places data."""
    hotel_name = hotel.get("hotel_name", "")
    state = hotel.get("state", "")
    city = hotel.get("city", "")
    
    if not hotel_name:
        return hotel
    
    print(f"  Searching: {hotel_name} ({city}, {state})")
    
    # Search for the place
    place = search_place(gmaps_client, hotel_name, state, city)
    time.sleep(REQUEST_DELAY)
    
    if not place:
        hotel["google_found"] = False
        hotel["google_place_id"] = ""
        hotel["google_name"] = ""
        hotel["google_address"] = ""
        hotel["google_phone"] = ""
        hotel["google_website"] = ""
        hotel["google_maps_url"] = ""
        hotel["google_rating"] = ""
        hotel["google_reviews"] = ""
        hotel["google_business_status"] = ""
        hotel["has_after_hours_gap"] = True  # Assume gap
        hotel["whatsapp_number"] = hotel.get("phone", "")
        hotel["whatsapp_source"] = "mah_directory" if hotel.get("phone") else ""
        return hotel
    
    place_id = place.get("place_id", "")
    
    # Get detailed info
    details = get_place_details(gmaps_client, place_id) if place_id else {}
    time.sleep(REQUEST_DELAY)
    
    # Extract phone
    google_phone = details.get("international_phone_number", "") or details.get("formatted_phone_number", "")
    if google_phone:
        google_phone = clean_phone(google_phone)
    
    # Determine best WhatsApp number
    # Priority: Google mobile > MAH mobile > Google landline > MAH landline
    mah_phone = hotel.get("phone", "")
    mah_is_mobile = hotel.get("is_mobile_whatsapp", False)
    google_is_mobile = is_whatsapp_likely(google_phone) if google_phone else False
    
    if google_is_mobile:
        whatsapp_number = google_phone
        whatsapp_source = "google_places"
    elif mah_is_mobile:
        whatsapp_number = mah_phone
        whatsapp_source = "mah_directory"
    elif google_phone:
        whatsapp_number = google_phone
        whatsapp_source = "google_places_landline"
    elif mah_phone:
        whatsapp_number = mah_phone
        whatsapp_source = "mah_directory_landline"
    else:
        whatsapp_number = ""
        whatsapp_source = ""
    
    # After-hours gap analysis
    opening_hours = details.get("opening_hours", {})
    has_gap = infer_after_hours_gap(opening_hours)
    
    # Google Maps URL
    google_maps_url = details.get("url", "")
    if not google_maps_url and place_id:
        google_maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
    
    # Update hotel with enriched data
    hotel["google_found"] = True
    hotel["google_place_id"] = place_id
    hotel["google_name"] = details.get("name", "")
    hotel["google_address"] = details.get("formatted_address", details.get("vicinity", ""))
    hotel["google_phone"] = google_phone
    hotel["google_website"] = details.get("website", "")
    hotel["google_maps_url"] = google_maps_url
    hotel["google_rating"] = details.get("rating", "")
    hotel["google_reviews"] = details.get("user_ratings_total", "")
    hotel["google_business_status"] = details.get("business_status", "")
    hotel["has_after_hours_gap"] = has_gap
    hotel["whatsapp_number"] = whatsapp_number
    hotel["whatsapp_source"] = whatsapp_source
    
    # Update website if empty
    if not hotel.get("website") and details.get("website"):
        hotel["website"] = details["website"]
    
    return hotel


def enrich_batch(hotels: list[dict], api_key: str, limit: int = None) -> list[dict]:
    """Enrich a batch of hotels with Google Places data."""
    if not GOOGLEMAPS_AVAILABLE:
        print("ERROR: googlemaps library not available. Install: pip install googlemaps")
        return hotels
    
    if not api_key:
        print("ERROR: GOOGLE_PLACES_API_KEY environment variable not set.")
        print("Set it with: set GOOGLE_PLACES_API_KEY=your_api_key_here")
        # Return hotels with empty enrichment fields
        for hotel in hotels:
            hotel["google_found"] = False
            hotel["google_place_id"] = ""
            hotel["google_name"] = ""
            hotel["google_address"] = ""
            hotel["google_phone"] = ""
            hotel["google_website"] = ""
            hotel["google_maps_url"] = ""
            hotel["google_rating"] = ""
            hotel["google_reviews"] = ""
            hotel["google_business_status"] = ""
            hotel["has_after_hours_gap"] = True
            hotel["whatsapp_number"] = hotel.get("phone", "")
            hotel["whatsapp_source"] = "mah_directory" if hotel.get("phone") else ""
        return hotels
    
    gmaps = googlemaps.Client(key=api_key)
    
    to_process = hotels[:limit] if limit else hotels
    already_done = hotels[limit:] if limit else []
    
    enriched = []
    total = len(to_process)
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Enriching {total} hotels via Google Places API...")
    
    for i, hotel in enumerate(to_process):
        print(f"[{i+1}/{total}] ", end="")
        try:
            hotel = enrich_hotel(gmaps, hotel)
        except Exception as e:
            print(f"  ERROR enriching {hotel.get('hotel_name', '?')}: {e}")
            hotel["google_found"] = False
        
        enriched.append(hotel)
        
        # Save checkpoint every 50 hotels
        if (i + 1) % 50 == 0:
            checkpoint_file = os.path.join(OUTPUT_DIR, f"checkpoint_{i+1}.json")
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(enriched + already_done, f, indent=2, ensure_ascii=False)
            print(f"  Checkpoint saved: {checkpoint_file}")
    
    return enriched + already_done


def main():
    parser = argparse.ArgumentParser(description="Enrich hotel leads with Google Places API")
    parser.add_argument("--input", default="mah_raw.json", help="Input JSON file (in output dir)")
    parser.add_argument("--output", default="mah_enriched.json", help="Output JSON file (in output dir)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of hotels to process (for testing)")
    parser.add_argument("--api-key", default="", help="Google Places API key (or set GOOGLE_PLACES_API_KEY env var)")
    args = parser.parse_args()
    
    api_key = args.api_key or API_KEY
    
    # Load input
    input_path = os.path.join(OUTPUT_DIR, args.input)
    if not os.path.exists(input_path):
        print(f"ERROR: Input file not found: {input_path}")
        print("Run scrape_mah.py first to generate the raw data.")
        return
    
    with open(input_path, 'r', encoding='utf-8') as f:
        hotels = json.load(f)
    
    print(f"Loaded {len(hotels)} hotels from {input_path}")
    
    # Enrich
    enriched = enrich_batch(hotels, api_key, args.limit)
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)
    
    print(f"\nEnriched data saved to {output_path}")
    
    # Summary
    google_found = sum(1 for h in enriched if h.get("google_found"))
    has_whatsapp = sum(1 for h in enriched if h.get("whatsapp_number"))
    has_mobile = sum(1 for h in enriched if is_whatsapp_likely(h.get("whatsapp_number", "")))
    
    print(f"\n=== ENRICHMENT SUMMARY ===")
    print(f"Hotels processed:     {len(enriched)}")
    print(f"Found on Google:      {google_found}")
    print(f"Has phone/WhatsApp:   {has_whatsapp}")
    print(f"Confirmed mobile:     {has_mobile}")


if __name__ == "__main__":
    main()
