"""
Agoda Public Search Scraper for Malaysian Hotels
Scrapes Agoda search results pages (public HTML, no JS required for base results)
as supplementary source alongside MAH and Google Places.

Agoda shows hotel name, star rating, area, and review data in search HTML.
We extract these and merge into the lead pipeline.
"""

import requests, json, re, os, time, random
from datetime import datetime
from bs4 import BeautifulSoup

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
}

# City IDs from Agoda (confirmed working)
# Format: (city_name, state, agoda_city_id, agoda_country_id)
AGODA_CITIES = [
    ('Kuala Lumpur',     'Kuala Lumpur',  1607,   201),
    ('Penang',           'Penang',         1645,   201),
    ('Johor Bahru',      'Johor',          1606,   201),
    ('Kota Kinabalu',    'Sabah',          1617,   201),
    ('Kuching',          'Sarawak',        1621,   201),
    ('Melaka',           'Melaka',         1620,   201),
    ('Ipoh',             'Perak',          1609,   201),
    ('Langkawi',         'Kedah',          1616,   201),
    ('Cameron Highlands','Pahang',         1604,   201),
    ('Kuantan',          'Pahang',         1633,   201),
    ('Shah Alam',        'Selangor',       1648,   201),
    ('Petaling Jaya',    'Selangor',       1644,   201),
    ('Sandakan',         'Sabah',          1647,   201),
    ('Miri',             'Sarawak',        1635,   201),
    ('Kota Bharu',       'Kelantan',       1615,   201),
    ('Kuala Terengganu', 'Terengganu',     1618,   201),
]

def scrape_agoda_city(city, state, city_id, country_id=201, pages=5):
    """Scrape Agoda search results for a city."""
    hotels = []
    base_url = 'https://www.agoda.com/search'

    for page in range(1, pages+1):
        params = {
            'city': city_id,
            'countryId': country_id,
            'page': page,
            'los': 1,
            'adults': 2,
            'children': 0,
            'rooms': 1,
            'locale': 'en-us',
        }
        try:
            time.sleep(random.uniform(1.5, 3.0))
            resp = requests.get(base_url, params=params, headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                break
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Try multiple selectors for hotel cards
            cards = (
                soup.find_all('div', attrs={'data-selenium': 'hotel-item'}) or
                soup.find_all('li', class_=re.compile(r'hotel|property')) or
                soup.find_all('div', class_=re.compile(r'PropertyCard|hotel-card'))
            )
            if not cards:
                break
            
            for card in cards:
                # Hotel name
                name_el = (
                    card.find(attrs={'data-selenium': 'hotel-name'}) or
                    card.find(['h3','h4'], class_=re.compile(r'name|title')) or
                    card.find(['h3','h4'])
                )
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)
                
                # Star rating from aria-label or class
                star_el = card.find(class_=re.compile(r'star|rating'))
                star_text = star_el.get('aria-label','') if star_el else ''
                star_match = re.search(r'(\d)\s*star', star_text, re.I)
                star = f'{star_match.group(1)} Star' if star_match else ''
                
                # Area/location
                area_el = card.find(attrs={'data-selenium': 'area-city-text'})
                area = area_el.get_text(strip=True) if area_el else ''
                
                # Review score
                score_el = card.find(class_=re.compile(r'review-score|score'))
                score = score_el.get_text(strip=True) if score_el else ''
                
                hotel = {
                    'hotel_name': name,
                    'hotel_name_upper': name.upper(),
                    'state': state, 'city': city,
                    'star_rating': star,
                    'num_rooms': None,
                    'postcode': '',
                    'address': f'{area}, {city}, {state}' if area else f'{city}, {state}',
                    'phone': '', 'is_mobile_whatsapp': False,
                    'email': '', 'website': '',
                    'icp_score': 3 + (1 if star in ('3 Star','4 Star') else 0),
                    'icp_flags': f'Agoda | {city} | {star}',
                    'source': 'Agoda',
                    'google_found': False, 'google_place_id': '',
                    'google_name': '', 'google_address': area or city,
                    'google_phone': '', 'google_website': '',
                    'google_maps_url': '',
                    'google_rating': score, 'google_reviews': '',
                    'google_business_status': '',
                    'has_after_hours_gap': True,
                    'whatsapp_number': '', 'whatsapp_source': '',
                    'member_id': '',
                }
                hotels.append(hotel)
        
        except Exception as e:
            print(f'  Agoda {city} p{page}: {e}')
            break
    
    return hotels


def run_agoda_scrape():
    all_hotels = []
    print(f'[{datetime.now():%H:%M:%S}] Starting Agoda scrape ({len(AGODA_CITIES)} cities)...')
    
    for city, state, city_id, country_id in AGODA_CITIES:
        print(f'  {city}...', end=' ')
        hotels = scrape_agoda_city(city, state, city_id, country_id)
        print(f'{len(hotels)} hotels')
        all_hotels.extend(hotels)
    
    # Deduplicate
    seen = set()
    unique = []
    for h in all_hotels:
        k = h['hotel_name_upper']
        if k not in seen:
            seen.add(k)
            unique.append(h)
    
    print(f'Agoda total unique: {len(unique)}')
    return unique


if __name__ == '__main__':
    hotels = run_agoda_scrape()
    out = os.path.join(OUTPUT_DIR, 'agoda_raw.json')
    with open(out,'w',encoding='utf-8') as f:
        json.dump(hotels,f,indent=2,ensure_ascii=False)
    print(f'Saved {len(hotels)} hotels → {out}')
