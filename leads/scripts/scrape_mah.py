"""
MAH (Malaysian Association of Hotels) Member Directory Scraper
Scrapes hotels.org.my/members for hotel data structured for Nocturn AI ICP lead list.

ICP Filter:
- Star rating: 3 or 4 star
- Room count: 50-400 rooms (using 400 as practical upper bound; exclude known chains >400)
- Location: All Malaysia states (primary: KL, Selangor, Penang, Johor, Sabah)
- Excludes: associate members, farmstays, business suites (non-hotel), suppliers
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import re
import os
from datetime import datetime

BASE_URL = "https://hotels.org.my/members"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://hotels.org.my/",
}

# Priority states for Nocturn AI ICP (v1 focus)
PRIORITY_STATES = {
    "Kuala Lumpur": 1,
    "Selangor": 2,
    "Penang": 3,
    "Johor": 4,
    "Sabah": 5,
    "Sarawak": 6,
    "Perak": 7,
    "Melaka": 8,
    "Negeri Sembilan": 9,
    "Kedah": 10,
    "Kelantan": 11,
    "Terengganu": 12,
    "Pahang": 13,
    "Perlis": 14,
    "Labuan": 15,
    "Putrajaya": 16,
}

# ICP qualifying star ratings
TARGET_STARS = {"3 Star", "4 Star", "3", "4"}

# Known non-hotel member types to exclude
EXCLUDE_KEYWORDS = [
    "SDN BHD", "SDN. BHD.", "RESOURCES", "COSMETICS", "TECHNOLOGY",
    "SYSTEM", "SOLUTIONS", "FARMSTAY", "BUSINESS SUITES", "SUITES @",
    "ASSOCIATES", "ASSOCIATION", "SERVICES",
]

def should_exclude(name: str) -> bool:
    """Exclude non-hotel entries from the member list."""
    name_upper = name.upper()
    return any(kw in name_upper for kw in EXCLUDE_KEYWORDS)

def parse_rooms(room_text: str) -> int | None:
    """Extract numeric room count from text like '213 rooms'."""
    match = re.search(r'(\d+)\s*rooms?', room_text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def parse_star_rating(info_text: str) -> str | None:
    """Extract star rating from text like 'Melaka, 3 Star (42 rooms)'."""
    # Match patterns: "3 Star", "4 Star", "Orchid", "Others"
    match = re.search(r',\s*([\w\s]+Star|Orchid|Others|Associate)', info_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def parse_state(info_text: str) -> str | None:
    """Extract state from text like 'Melaka, 3 Star (42 rooms)'."""
    # State is always the first part before the comma
    match = re.match(r'^([^,]+)', info_text.strip())
    if match:
        return match.group(1).strip()
    return None

def clean_phone(phone: str) -> str:
    """Normalize phone number to Malaysian format."""
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    # Ensure it starts with +60 or 60
    if phone.startswith('0'):
        phone = '+60' + phone[1:]
    elif phone.startswith('60') and not phone.startswith('+60'):
        phone = '+' + phone
    return phone

def is_whatsapp_likely(phone: str) -> bool:
    """Estimate if a phone number is likely a mobile (WhatsApp-enabled)."""
    # Malaysian mobile numbers start with +601x
    return bool(re.match(r'^\+?601[0-9]', phone))

def scrape_mah_directory() -> list[dict]:
    """Main scraper for hotels.org.my/members."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting MAH directory scrape...")
    
    hotels = []
    page = 1
    
    # MAH uses pagination or single-page rendering
    # Try fetching the full page first
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"ERROR: Failed to fetch {BASE_URL}: {e}")
        return hotels
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # MAH renders hotel cards - find all hotel entries
    # Based on structure from read_url_content: h3 headers with member numbers, then details
    hotel_sections = soup.find_all('h3')
    
    print(f"Found {len(hotel_sections)} potential hotel entries")
    
    for section in hotel_sections:
        try:
            hotel_name_raw = section.get_text(strip=True)
            
            # Skip non-hotel entries
            if should_exclude(hotel_name_raw):
                continue
            
            # Extract member ID from parentheses: "HOTEL NAME (1234)"
            member_id_match = re.search(r'\((\d+)\)$', hotel_name_raw)
            member_id = member_id_match.group(1) if member_id_match else ""
            hotel_name = re.sub(r'\s*\(\d+\)$', '', hotel_name_raw).strip()
            
            # Get the sibling/parent container for details
            parent = section.find_parent()
            if not parent:
                parent = section
            
            # Find the info block following this h3
            info_block = section.find_next_sibling()
            details_text = ""
            if info_block:
                details_text = info_block.get_text(separator=' ', strip=True)
            
            # Try to find the list items with location, phone, email, website
            # Looking in the broader section
            container = section.find_parent(['div', 'article', 'section', 'li'])
            if not container:
                container = section
            
            # Extract location info (star rating, state, rooms)
            location_links = []
            for link in container.find_all('a'):
                href = link.get('href', '')
                if '/views/' in href or 'members' in href:
                    location_links.append(link.get_text(strip=True))
            
            location_info = location_links[0] if location_links else details_text
            
            state = parse_state(location_info)
            star_rating = parse_star_rating(location_info)
            num_rooms = parse_rooms(location_info)
            
            # Extract address (text content before phone)
            address_parts = []
            phone = ""
            email = ""
            website = ""
            
            # Parse list items
            list_items = container.find_all('li')
            for li in list_items:
                text = li.get_text(strip=True)
                links_in_li = li.find_all('a')
                
                for a in links_in_li:
                    href = a.get('href', '')
                    link_text = a.get_text(strip=True)
                    
                    if href.startswith('mailto:'):
                        email = href.replace('mailto:', '').strip()
                    elif href.startswith('http') and 'hotels.org.my' not in href:
                        website = href.strip()
                    elif href.startswith('tel:'):
                        phone = href.replace('tel:', '').strip()
                
                # If no href, check if it's a phone or address
                if not any(a.get('href', '').startswith(('mailto:', 'http', 'tel:')) for a in links_in_li):
                    # Check if it looks like a phone
                    if re.match(r'^[\+\d\s\-\(\)]{8,20}$', text):
                        if not phone:
                            phone = text
                    elif text and not text.startswith('http'):
                        address_parts.append(text)
            
            # If phone not found in li, try to find in the full text
            if not phone:
                phone_match = re.search(r'(\+?6?0\d[\d\s\-]{6,14})', details_text)
                if phone_match:
                    phone = phone_match.group(1)
            
            # Clean phone
            if phone:
                phone = clean_phone(phone)
            
            # Determine if mobile/WhatsApp
            is_mobile = is_whatsapp_likely(phone) if phone else False
            
            # Extract address
            address = ", ".join(address_parts) if address_parts else ""
            
            # City detection from address/state
            city = ""
            if state == "Kuala Lumpur":
                city = "Kuala Lumpur"
            elif state == "Selangor":
                city = "Petaling Jaya"  # default, will be refined
            elif state == "Penang":
                city = "George Town"
            elif state == "Johor":
                city = "Johor Bahru"
            elif state == "Sabah":
                city = "Kota Kinabalu"
            elif state == "Sarawak":
                city = "Kuching"
            else:
                city = state or ""
            
            # ICP scoring
            icp_score = 0
            icp_flags = []
            
            # Star rating check
            if star_rating and any(s in star_rating for s in ['3 Star', '4 Star', '3', '4']):
                icp_score += 3
                icp_flags.append(f"{star_rating}")
            elif star_rating in ['Orchid', 'Others']:
                # Orchid = boutique, Others = unclassified - could still qualify
                icp_score += 1
                icp_flags.append("Unclassified")
            
            # Room count check
            if num_rooms:
                if 50 <= num_rooms <= 300:
                    icp_score += 3
                    icp_flags.append(f"{num_rooms} rooms (ICP range)")
                elif 30 <= num_rooms < 50:
                    icp_score += 1
                    icp_flags.append(f"{num_rooms} rooms (small)")
                elif 300 < num_rooms <= 400:
                    icp_score += 2
                    icp_flags.append(f"{num_rooms} rooms (upper range)")
                elif num_rooms > 400:
                    icp_score -= 1
                    icp_flags.append(f"{num_rooms} rooms (too large)")
            
            # State/city priority
            state_priority = PRIORITY_STATES.get(state, 20)
            if state_priority <= 5:
                icp_score += 2
            elif state_priority <= 8:
                icp_score += 1
            
            # Has email
            if email:
                icp_score += 1
                icp_flags.append("Email available")
            
            # Has mobile/WhatsApp
            if is_mobile:
                icp_score += 2
                icp_flags.append("WhatsApp number")
            elif phone:
                icp_score += 1
                icp_flags.append("Phone available")
            
            # Has website
            if website:
                icp_score += 1
            
            hotel = {
                "member_id": member_id,
                "hotel_name": hotel_name,
                "state": state or "",
                "city": city,
                "star_rating": star_rating or "",
                "num_rooms": num_rooms or "",
                "address": address,
                "phone": phone,
                "is_mobile_whatsapp": is_mobile,
                "email": email,
                "website": website,
                "icp_score": icp_score,
                "icp_flags": " | ".join(icp_flags),
                "source": "MAH Directory",
            }
            
            hotels.append(hotel)
            
        except Exception as e:
            print(f"  Warning: Error parsing hotel entry: {e}")
            continue
    
    print(f"Scraped {len(hotels)} hotel entries from MAH directory")
    return hotels


def save_raw(hotels: list[dict], filename: str = "mah_raw.json"):
    """Save raw scraped data as JSON."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(hotels, f, indent=2, ensure_ascii=False)
    print(f"Raw data saved to {filepath}")
    return filepath


if __name__ == "__main__":
    hotels = scrape_mah_directory()
    save_raw(hotels)
    
    # Print summary
    total = len(hotels)
    icp_qualified = [h for h in hotels if h.get('icp_score', 0) >= 5]
    has_email = [h for h in hotels if h.get('email')]
    has_whatsapp = [h for h in hotels if h.get('is_mobile_whatsapp')]
    
    print(f"\n=== SCRAPE SUMMARY ===")
    print(f"Total entries:      {total}")
    print(f"ICP qualified (≥5): {len(icp_qualified)}")
    print(f"Has email:          {len(has_email)}")
    print(f"Has WhatsApp:       {len(has_whatsapp)}")
