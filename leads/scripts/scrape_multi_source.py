"""
Multi-Source Hotel Lead Scraper for Nocturn AI Lead Generation
Sources:
1. MAH (Malaysian Association of Hotels) - hotels.org.my/members (~1,000 hotels)
2. Google Places API text search by city/state (~3,000+ hotels)  
3. Booking.com / Agoda metadata scrape (public search results)
4. TripAdvisor hotel listings (public data)
5. Malaysia Hotel Association directory variations

Target: 10,000 unique hotel entries with contact data (phone, email, WhatsApp)
ICP: 3-4 star, 50-300 rooms, Malaysian, independent/small chain

Usage:
    python scrape_multi_source.py --sources all --output combined_hotels.json
    python scrape_multi_source.py --sources google --limit 500 --city "Penang"
    python scrape_multi_source.py --sources booking --state Johor
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
import os
import argparse
import random
from datetime import datetime
from urllib.parse import urlencode, quote_plus

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

GOOGLE_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")

# Malaysian cities/areas to cover systematically
MALAYSIA_SEARCH_LOCATIONS = [
    # Klang Valley / KL
    {"city": "Kuala Lumpur", "state": "Kuala Lumpur", "lat": 3.1390, "lng": 101.6869, "radius": 15000},
    {"city": "Petaling Jaya", "state": "Selangor", "lat": 3.1073, "lng": 101.6067, "radius": 10000},
    {"city": "Shah Alam", "state": "Selangor", "lat": 3.0738, "lng": 101.5183, "radius": 10000},
    {"city": "Subang Jaya", "state": "Selangor", "lat": 3.0565, "lng": 101.5837, "radius": 8000},
    {"city": "Klang", "state": "Selangor", "lat": 3.0449, "lng": 101.4479, "radius": 10000},
    {"city": "Sepang", "state": "Selangor", "lat": 2.7266, "lng": 101.7112, "radius": 15000},
    # Penang
    {"city": "George Town", "state": "Penang", "lat": 5.4141, "lng": 100.3288, "radius": 12000},
    {"city": "Batu Ferringhi", "state": "Penang", "lat": 5.4665, "lng": 100.2587, "radius": 8000},
    {"city": "Butterworth", "state": "Penang", "lat": 5.3991, "lng": 100.3634, "radius": 8000},
    # Johor
    {"city": "Johor Bahru", "state": "Johor", "lat": 1.4927, "lng": 103.7414, "radius": 15000},
    {"city": "Iskandar Puteri", "state": "Johor", "lat": 1.4200, "lng": 103.6280, "radius": 10000},
    {"city": "Batu Pahat", "state": "Johor", "lat": 1.8564, "lng": 102.9333, "radius": 8000},
    {"city": "Kluang", "state": "Johor", "lat": 2.0240, "lng": 103.3186, "radius": 8000},
    {"city": "Muar", "state": "Johor", "lat": 2.0442, "lng": 102.5689, "radius": 8000},
    # Sabah
    {"city": "Kota Kinabalu", "state": "Sabah", "lat": 5.9788, "lng": 116.0753, "radius": 15000},
    {"city": "Sandakan", "state": "Sabah", "lat": 5.8402, "lng": 118.1179, "radius": 10000},
    {"city": "Tawau", "state": "Sabah", "lat": 4.2449, "lng": 117.8910, "radius": 8000},
    {"city": "Lahad Datu", "state": "Sabah", "lat": 5.0283, "lng": 118.3275, "radius": 8000},
    # Sarawak
    {"city": "Kuching", "state": "Sarawak", "lat": 1.5497, "lng": 110.3592, "radius": 15000},
    {"city": "Miri", "state": "Sarawak", "lat": 4.3995, "lng": 113.9914, "radius": 10000},
    {"city": "Sibu", "state": "Sarawak", "lat": 2.2893, "lng": 111.8285, "radius": 8000},
    {"city": "Bintulu", "state": "Sarawak", "lat": 3.1699, "lng": 113.0397, "radius": 8000},
    # Perak
    {"city": "Ipoh", "state": "Perak", "lat": 4.5975, "lng": 101.0901, "radius": 12000},
    {"city": "Taiping", "state": "Perak", "lat": 4.8514, "lng": 100.7351, "radius": 8000},
    # Kedah / Langkawi
    {"city": "Langkawi", "state": "Kedah", "lat": 6.3500, "lng": 99.8000, "radius": 20000},
    {"city": "Alor Setar", "state": "Kedah", "lat": 6.1208, "lng": 100.3685, "radius": 8000},
    # Pahang / Cameron Highlands / Genting
    {"city": "Cameron Highlands", "state": "Pahang", "lat": 4.4714, "lng": 101.3865, "radius": 15000},
    {"city": "Kuantan", "state": "Pahang", "lat": 3.8226, "lng": 103.3256, "radius": 10000},
    {"city": "Genting Highlands", "state": "Pahang", "lat": 3.4231, "lng": 101.7936, "radius": 8000},
    # Melaka
    {"city": "Melaka", "state": "Melaka", "lat": 2.1896, "lng": 102.2501, "radius": 12000},
    # Negeri Sembilan
    {"city": "Seremban", "state": "Negeri Sembilan", "lat": 2.7297, "lng": 101.9381, "radius": 10000},
    {"city": "Port Dickson", "state": "Negeri Sembilan", "lat": 2.5219, "lng": 101.7955, "radius": 10000},
    # Kelantan
    {"city": "Kota Bharu", "state": "Kelantan", "lat": 6.1254, "lng": 102.2526, "radius": 10000},
    # Terengganu
    {"city": "Kuala Terengganu", "state": "Terengganu", "lat": 5.3296, "lng": 103.1370, "radius": 10000},
    {"city": "Redang Island", "state": "Terengganu", "lat": 5.7831, "lng": 102.9985, "radius": 15000},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def clean_phone(phone: str) -> str:
    phone = re.sub(r'[\s\-\(\)\.]', '', str(phone))
    if phone.startswith('0'):
        phone = '+60' + phone[1:]
    elif phone.startswith('60') and not phone.startswith('+60'):
        phone = '+' + phone
    return phone


def is_mobile(phone: str) -> bool:
    return bool(re.match(r'^\+?601[0-9]', phone.replace(' ', '')))


def dedupe_hotels(hotels: list[dict], existing: list[dict] = None) -> list[dict]:
    """Remove duplicates based on hotel name + city."""
    seen = set()
    
    # Add existing entries to seen set
    if existing:
        for h in existing:
            key = (
                re.sub(r'\s+', ' ', h.get("hotel_name", "").upper().strip()),
                h.get("city", "").upper().strip()
            )
            seen.add(key)
    
    unique = []
    for h in hotels:
        key = (
            re.sub(r'\s+', ' ', h.get("hotel_name", "").upper().strip()),
            h.get("city", "").upper().strip()
        )
        if key not in seen:
            seen.add(key)
            unique.append(h)
    
    return unique


# ============================================================
# SOURCE 1: Google Places API - Nearby Search
# ============================================================

def scrape_google_places_nearby(api_key: str, location: dict, hotel_type: str = "lodging") -> list[dict]:
    """
    Scrape hotels near a location using Google Places Nearby Search.
    Returns up to 60 results (3 pages of 20) per location.
    """
    if not api_key:
        print("  SKIP: No Google API key")
        return []
    
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    hotels = []
    
    params = {
        "location": f"{location['lat']},{location['lng']}",
        "radius": location.get("radius", 10000),
        "type": hotel_type,
        "keyword": "hotel",
        "key": api_key,
        "language": "en"
    }
    
    page_token = None
    page = 0
    
    while page < 3:  # Max 3 pages = 60 results
        if page_token:
            params_paged = {"pagetoken": page_token, "key": api_key}
            time.sleep(2)  # Required delay for page tokens
        else:
            params_paged = params
        
        try:
            resp = requests.get(base_url, params=params_paged, timeout=15)
            data = resp.json()
            
            if data.get("status") not in ["OK", "ZERO_RESULTS"]:
                print(f"    API error: {data.get('status')} - {data.get('error_message', '')}")
                break
            
            results = data.get("results", [])
            
            for place in results:
                name = place.get("name", "")
                place_id = place.get("place_id", "")
                address = place.get("vicinity", "")
                rating = place.get("rating", "")
                review_count = place.get("user_ratings_total", "")
                business_status = place.get("business_status", "")
                
                # Skip closed businesses
                if business_status == "CLOSED_PERMANENTLY":
                    continue
                
                # Get coordinates
                geometry = place.get("geometry", {}).get("location", {})
                
                hotel = {
                    "hotel_name": name,
                    "state": location["state"],
                    "city": location["city"],
                    "star_rating": "",  # Will be enriched
                    "num_rooms": "",
                    "address": address,
                    "phone": "",
                    "is_mobile_whatsapp": False,
                    "email": "",
                    "website": "",
                    "icp_score": 3,  # Base score, will be updated
                    "icp_flags": f"Google Places | {location['city']}",
                    "source": "Google Places",
                    "google_found": True,
                    "google_place_id": place_id,
                    "google_name": name,
                    "google_address": address,
                    "google_phone": "",
                    "google_website": "",
                    "google_maps_url": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                    "google_rating": rating,
                    "google_reviews": review_count,
                    "google_business_status": business_status,
                    "has_after_hours_gap": True,
                    "whatsapp_number": "",
                    "whatsapp_source": "",
                    "member_id": "",
                }
                
                hotels.append(hotel)
            
            page_token = data.get("next_page_token")
            if not page_token:
                break
            
            page += 1
            
        except Exception as e:
            print(f"    Error: {e}")
            break
    
    return hotels


def scrape_google_places_text(api_key: str, query: str, state: str, city: str) -> list[dict]:
    """Search for hotels using text search (more targeted than nearby)."""
    if not api_key:
        return []
    
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    hotels = []
    
    params = {
        "query": query,
        "type": "lodging",
        "key": api_key,
        "language": "en",
        "region": "my"
    }
    
    page_token = None
    page = 0
    
    while page < 3:
        if page_token:
            p = {"pagetoken": page_token, "key": api_key}
            time.sleep(2)
        else:
            p = params
        
        try:
            resp = requests.get(base_url, params=p, timeout=15)
            data = resp.json()
            
            if data.get("status") == "ZERO_RESULTS":
                break
            
            if data.get("status") != "OK":
                break
            
            for place in data.get("results", []):
                name = place.get("name", "")
                place_id = place.get("place_id", "")
                
                if place.get("business_status") == "CLOSED_PERMANENTLY":
                    continue
                
                hotel = {
                    "hotel_name": name,
                    "state": state,
                    "city": city,
                    "star_rating": "",
                    "num_rooms": "",
                    "address": place.get("formatted_address", ""),
                    "phone": "",
                    "is_mobile_whatsapp": False,
                    "email": "",
                    "website": "",
                    "icp_score": 3,
                    "icp_flags": f"Google Text Search | {city}",
                    "source": "Google Places Text Search",
                    "google_found": True,
                    "google_place_id": place_id,
                    "google_name": name,
                    "google_address": place.get("formatted_address", ""),
                    "google_phone": "",
                    "google_website": "",
                    "google_maps_url": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                    "google_rating": place.get("rating", ""),
                    "google_reviews": place.get("user_ratings_total", ""),
                    "google_business_status": place.get("business_status", ""),
                    "has_after_hours_gap": True,
                    "whatsapp_number": "",
                    "whatsapp_source": "",
                    "member_id": "",
                }
                hotels.append(hotel)
            
            page_token = data.get("next_page_token")
            if not page_token:
                break
            
            page += 1
            
        except Exception as e:
            print(f"    Text search error: {e}")
            break
    
    return hotels


def run_google_places_scrape(api_key: str, existing: list[dict] = None) -> list[dict]:
    """Run systematic Google Places scrape across all Malaysian locations."""
    all_hotels = []
    existing = existing or []
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting Google Places systematic scrape...")
    print(f"  Locations to cover: {len(MALAYSIA_SEARCH_LOCATIONS)}")
    
    for i, location in enumerate(MALAYSIA_SEARCH_LOCATIONS):
        city = location["city"]
        state = location["state"]
        
        print(f"  [{i+1}/{len(MALAYSIA_SEARCH_LOCATIONS)}] {city}, {state}...")
        
        # Nearby search for hotels
        nearby = scrape_google_places_nearby(api_key, location)
        print(f"    Nearby search: {len(nearby)} places")
        all_hotels.extend(nearby)
        time.sleep(0.5)
        
        # Text searches for specific star ratings
        for query in [
            f"3 star hotel {city} Malaysia",
            f"4 star hotel {city} Malaysia",
            f"boutique hotel {city} Malaysia",
        ]:
            text_results = scrape_google_places_text(api_key, query, state, city)
            all_hotels.extend(text_results)
            time.sleep(0.3)
        
        print(f"    Running total: {len(all_hotels)}")
        
        # Save checkpoint every 5 locations
        if (i + 1) % 5 == 0:
            checkpoint_path = os.path.join(OUTPUT_DIR, f"google_checkpoint_{i+1}.json")
            unique = dedupe_hotels(all_hotels)
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(unique, f, indent=2, ensure_ascii=False)
            print(f"    Checkpoint: {len(unique)} unique hotels")
    
    # Deduplicate against existing
    unique = dedupe_hotels(all_hotels, existing)
    print(f"\nGoogle Places scrape complete: {len(unique)} unique new hotels")
    return unique


# ============================================================
# SOURCE 2: TripAdvisor Hotels (Public HTML)
# ============================================================

TRIPADVISOR_CITIES = [
    ("Kuala-Lumpur", "Kuala Lumpur", "Kuala Lumpur"),
    ("George-Town", "George Town", "Penang"),
    ("Johor-Bahru", "Johor Bahru", "Johor"),
    ("Kota-Kinabalu", "Kota Kinabalu", "Sabah"),
    ("Melaka", "Melaka", "Melaka"),
    ("Ipoh", "Ipoh", "Perak"),
    ("Kuching", "Kuching", "Sarawak"),
    ("Langkawi", "Langkawi", "Kedah"),
    ("Cameron-Highlands", "Cameron Highlands", "Pahang"),
]

def scrape_tripadvisor_hotels(city_slug: str, city: str, state: str, pages: int = 5) -> list[dict]:
    """
    Scrape hotel listings from TripAdvisor.
    Note: TripAdvisor may block/rate-limit; use with caution.
    """
    hotels = []
    base_url = f"https://www.tripadvisor.com/Hotels-g{city_slug}-Hotels.html"
    
    # TripAdvisor uses offset-based pagination (offset by 20 or 25)
    for page in range(pages):
        offset = page * 25
        if offset == 0:
            url = base_url
        else:
            url = base_url.replace(".html", f"-oa{offset}.html")
        
        try:
            time.sleep(random.uniform(2, 4))  # Polite delay
            resp = requests.get(url, headers=HEADERS, timeout=30)
            
            if resp.status_code != 200:
                print(f"    TripAdvisor returned {resp.status_code} for {city}")
                break
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find hotel cards - TripAdvisor structure varies; target data attributes
            hotel_cards = soup.find_all(['div', 'article'], attrs={'data-element-name': re.compile('hotel', re.I)})
            if not hotel_cards:
                hotel_cards = soup.find_all('div', class_=re.compile('listing', re.I))
            
            if not hotel_cards:
                break
            
            for card in hotel_cards:
                name_elem = card.find(['h3', 'h2', 'a'], class_=re.compile('name|title', re.I))
                if not name_elem:
                    continue
                    
                hotel_name = name_elem.get_text(strip=True)
                
                # Extract rating bubbles (TripAdvisor-specific)
                rating_elem = card.find(['span', 'div'], attrs={'class': re.compile('rating|bubble', re.I)})
                rating = ""
                if rating_elem:
                    rating = rating_elem.get('aria-label', '') or rating_elem.get_text(strip=True)
                
                hotel = {
                    "hotel_name": hotel_name,
                    "state": state,
                    "city": city,
                    "star_rating": "",
                    "num_rooms": "",
                    "address": f"{city}, {state}, Malaysia",
                    "phone": "",
                    "is_mobile_whatsapp": False,
                    "email": "",
                    "website": "",
                    "icp_score": 2,
                    "icp_flags": f"TripAdvisor | {city}",
                    "source": "TripAdvisor",
                    "google_found": False,
                    "google_place_id": "",
                    "google_name": "",
                    "google_address": "",
                    "google_phone": "",
                    "google_website": "",
                    "google_maps_url": "",
                    "google_rating": rating,
                    "google_reviews": "",
                    "google_business_status": "",
                    "has_after_hours_gap": True,
                    "whatsapp_number": "",
                    "whatsapp_source": "",
                    "member_id": "",
                }
                hotels.append(hotel)
            
        except Exception as e:
            print(f"    TripAdvisor error for {city}: {e}")
            break
    
    return hotels


# ============================================================
# SOURCE 3: Booking.com Search Results (Public HTML)
# ============================================================

def scrape_booking_com(city: str, state: str, star_ratings: list = None) -> list[dict]:
    """
    Scrape Booking.com hotel listings for a city.
    Uses public search pages without auth.
    """
    if star_ratings is None:
        star_ratings = ["3", "4"]
    
    hotels = []
    
    for stars in star_ratings:
        # Booking.com search URL pattern
        search_url = f"https://www.booking.com/searchresults.html"
        params = {
            "ss": f"{city}, Malaysia",
            "class_interval": f"{stars},{stars}",
            "rows": 25,
            "offset": 0,
        }
        
        try:
            time.sleep(random.uniform(1.5, 3))
            url = f"{search_url}?{urlencode(params)}"
            resp = requests.get(url, headers=HEADERS, timeout=30)
            
            if resp.status_code != 200:
                continue
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find property cards
            property_cards = soup.find_all('div', attrs={'data-testid': 'property-card'})
            if not property_cards:
                property_cards = soup.find_all('div', class_=re.compile(r'sr_property_block|hotel-card', re.I))
            
            for card in property_cards:
                # Hotel name
                name_elem = card.find(['div', 'span', 'h1', 'h2', 'h3'], attrs={'data-testid': 'title'})
                if not name_elem:
                    name_elem = card.find(['h3', 'span'], class_=re.compile(r'hotel_name|sr-hotel__name', re.I))
                
                if not name_elem:
                    continue
                
                hotel_name = name_elem.get_text(strip=True)
                
                # Address/location
                address_elem = card.find(['span', 'div'], attrs={'data-testid': re.compile('address', re.I)})
                address = address_elem.get_text(strip=True) if address_elem else f"{city}, {state}"
                
                # Rating
                rating_elem = card.find(['div', 'span'], attrs={'data-testid': re.compile('rating|score', re.I)})
                rating = rating_elem.get_text(strip=True) if rating_elem else ""
                
                hotel = {
                    "hotel_name": hotel_name,
                    "state": state,
                    "city": city,
                    "star_rating": f"{stars} Star",
                    "num_rooms": "",
                    "address": address,
                    "phone": "",
                    "is_mobile_whatsapp": False,
                    "email": "",
                    "website": "",
                    "icp_score": 4 if stars == "4" else 3,  # Base ICP
                    "icp_flags": f"Booking.com {stars}★ | {city}",
                    "source": "Booking.com",
                    "google_found": False,
                    "google_place_id": "",
                    "google_name": "",
                    "google_address": "",
                    "google_phone": "",
                    "google_website": "",
                    "google_maps_url": "",
                    "google_rating": rating,
                    "google_reviews": "",
                    "google_business_status": "",
                    "has_after_hours_gap": True,
                    "whatsapp_number": "",
                    "whatsapp_source": "",
                    "member_id": "",
                }
                hotels.append(hotel)
            
        except Exception as e:
            print(f"    Booking.com error for {city} {stars}★: {e}")
    
    return hotels


# ============================================================
# SOURCE 4: Additional Malaysian Hotel Directories
# ============================================================

def scrape_maho_directory() -> list[dict]:
    """
    Scrape MAHO (Malaysian Association of Hotel Owners) directory.
    URL: maho.org.my
    """
    hotels = []
    
    urls_to_try = [
        "https://maho.org.my/members",
        "https://maho.org.my/member-hotels",
        "https://maho.org.my/directory",
    ]
    
    for url in urls_to_try:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Parse MAHO directory structure
                # Structure varies - attempt generic extraction
                entries = soup.find_all(['tr', 'div', 'li'], class_=re.compile(r'member|hotel|property', re.I))
                
                for entry in entries:
                    text = entry.get_text(separator=' ', strip=True)
                    name_match = re.match(r'^([A-Z][^,\n]{5,60})', text)
                    if name_match:
                        hotel = {
                            "hotel_name": name_match.group(1).strip(),
                            "state": "",
                            "city": "",
                            "star_rating": "",
                            "num_rooms": "",
                            "address": text[:200],
                            "phone": "", "is_mobile_whatsapp": False,
                            "email": "", "website": "",
                            "icp_score": 2,
                            "icp_flags": "MAHO Directory",
                            "source": "MAHO Directory",
                            "google_found": False, "google_place_id": "",
                            "google_name": "", "google_address": "",
                            "google_phone": "", "google_website": "",
                            "google_maps_url": "",
                            "google_rating": "", "google_reviews": "",
                            "google_business_status": "",
                            "has_after_hours_gap": True,
                            "whatsapp_number": "", "whatsapp_source": "",
                            "member_id": "",
                        }
                        hotels.append(hotel)
                break
        except Exception as e:
            print(f"  MAHO {url}: {e}")
    
    print(f"MAHO: {len(hotels)} hotels")
    return hotels


def scrape_tourism_malaysia() -> list[dict]:
    """
    Scrape Tourism Malaysia hotel directory.
    """
    hotels = []
    base_url = "https://www.tourism.gov.my/listings/all-hotels"
    
    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=20)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            entries = soup.find_all(['div', 'li', 'article'], class_=re.compile(r'hotel|listing|property', re.I))
            
            for entry in entries:
                name_elem = entry.find(['h1', 'h2', 'h3', 'h4', 'strong'])
                if name_elem:
                    hotel_name = name_elem.get_text(strip=True)
                    
                    # Extract phone/email
                    text = entry.get_text(separator=' ')
                    phone_match = re.search(r'(\+?6?0\d[\d\s\-]{6,14})', text)
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
                    
                    hotel = {
                        "hotel_name": hotel_name,
                        "state": "", "city": "",
                        "star_rating": "", "num_rooms": "",
                        "address": "",
                        "phone": clean_phone(phone_match.group(1)) if phone_match else "",
                        "is_mobile_whatsapp": is_mobile(phone_match.group(1)) if phone_match else False,
                        "email": email_match.group(0) if email_match else "",
                        "website": "",
                        "icp_score": 2,
                        "icp_flags": "Tourism Malaysia",
                        "source": "Tourism Malaysia",
                        "google_found": False, "google_place_id": "",
                        "google_name": "", "google_address": "",
                        "google_phone": "", "google_website": "",
                        "google_maps_url": "",
                        "google_rating": "", "google_reviews": "",
                        "google_business_status": "",
                        "has_after_hours_gap": True,
                        "whatsapp_number": clean_phone(phone_match.group(1)) if phone_match and is_mobile(phone_match.group(1)) else "",
                        "whatsapp_source": "tourism_malaysia" if phone_match and is_mobile(phone_match.group(1)) else "",
                        "member_id": "",
                    }
                    hotels.append(hotel)
    except Exception as e:
        print(f"  Tourism Malaysia error: {e}")
    
    print(f"Tourism Malaysia: {len(hotels)} hotels")
    return hotels


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_all_sources(api_key: str = "", existing_mah: str = None) -> list[dict]:
    """Run all scraping sources and combine results."""
    all_hotels = []
    
    # Load existing MAH data if available
    if existing_mah:
        mah_path = os.path.join(OUTPUT_DIR, existing_mah)
        if os.path.exists(mah_path):
            with open(mah_path, 'r', encoding='utf-8') as f:
                mah_data = json.load(f)
            all_hotels.extend(mah_data)
            print(f"Loaded {len(mah_data)} hotels from MAH scrape")
    
    # Google Places (largest volume source)
    if api_key:
        print("\n--- Google Places API Scrape ---")
        google_hotels = run_google_places_scrape(api_key, all_hotels)
        all_hotels_unique = dedupe_hotels(google_hotels, all_hotels)
        all_hotels.extend(all_hotels_unique)
        print(f"After Google Places: {len(all_hotels)} total unique hotels")
        
        # Save intermediate
        save_path = os.path.join(OUTPUT_DIR, "google_places_raw.json")
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(google_hotels, f, indent=2, ensure_ascii=False)
    
    # Booking.com
    print("\n--- Booking.com Scrape ---")
    booking_hotels = []
    for loc in MALAYSIA_SEARCH_LOCATIONS[:15]:  # Top 15 cities
        city = loc["city"]
        state = loc["state"]
        print(f"  Booking.com: {city}")
        bh = scrape_booking_com(city, state)
        booking_hotels.extend(bh)
        print(f"    Found {len(bh)} hotels")
        time.sleep(1)
    
    new_booking = dedupe_hotels(booking_hotels, all_hotels)
    all_hotels.extend(new_booking)
    print(f"Booking.com added {len(new_booking)} new hotels. Total: {len(all_hotels)}")
    
    # MAHO Directory
    print("\n--- MAHO Directory Scrape ---")
    maho_hotels = scrape_maho_directory()
    new_maho = dedupe_hotels(maho_hotels, all_hotels)
    all_hotels.extend(new_maho)
    print(f"MAHO added {len(new_maho)} new hotels. Total: {len(all_hotels)}")
    
    # Tourism Malaysia
    print("\n--- Tourism Malaysia Scrape ---")
    tourism_hotels = scrape_tourism_malaysia()
    new_tourism = dedupe_hotels(tourism_hotels, all_hotels)
    all_hotels.extend(new_tourism)
    print(f"Tourism Malaysia added {len(new_tourism)} new hotels. Total: {len(all_hotels)}")
    
    return all_hotels


def main():
    parser = argparse.ArgumentParser(description="Multi-source Malaysian hotel scraper")
    parser.add_argument("--sources", default="all", choices=["all", "google", "booking", "maho", "tourism"],
                        help="Which sources to scrape")
    parser.add_argument("--output", default="combined_hotels.json", help="Output JSON filename")
    parser.add_argument("--mah-input", default="mah_raw.json", help="Existing MAH data to merge with")
    parser.add_argument("--api-key", default="", help="Google Places API key")
    args = parser.parse_args()
    
    api_key = args.api_key or GOOGLE_API_KEY
    
    if args.sources == "all":
        hotels = run_all_sources(api_key, args.mah_input)
    elif args.sources == "google":
        hotels = run_google_places_scrape(api_key)
    elif args.sources == "booking":
        hotels = []
        for loc in MALAYSIA_SEARCH_LOCATIONS:
            bh = scrape_booking_com(loc["city"], loc["state"])
            hotels.extend(bh)
    elif args.sources == "maho":
        hotels = scrape_maho_directory()
    elif args.sources == "tourism":
        hotels = scrape_tourism_malaysia()
    else:
        hotels = []
    
    # Deduplicate final list
    unique = dedupe_hotels(hotels)
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== MULTI-SOURCE SCRAPE COMPLETE ===")
    print(f"Total unique hotels: {len(unique)}")
    print(f"Saved to: {output_path}")
    
    # Source breakdown
    source_counts = {}
    for h in unique:
        src = h.get("source", "Unknown")
        source_counts[src] = source_counts.get(src, 0) + 1
    
    for src, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"  {src}: {count}")


if __name__ == "__main__":
    main()
