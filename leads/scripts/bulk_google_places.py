"""
Bulk Google Places API Hotel Scraper for Malaysia
Systematically searches 34+ cities × star ratings × search types to hit 8,000+ hotels.
Handles pagination (3 pages/query × 20 results = 60 per query).
Deduplicates by place_id and hotel name.

Prerequisites:
    set GOOGLE_PLACES_API_KEY=AIza...your_key...
    pip install requests

Usage:
    python bulk_google_places.py                # full run
    python bulk_google_places.py --cities "Kuala Lumpur,Penang"  # specific cities
    python bulk_google_places.py --limit 1000   # first 1000 results only
    python bulk_google_places.py --resume       # resume from last checkpoint

API usage estimate per full run:
    - 34 locations × 4 searches × (nearby + text) = ~272 "find" calls = ~0.017 USD each = ~$5
    - 8,000 detail lookups at $0.017 = ~$136 (skip with --no-details to save cost)
    - Recommended: run with --no-details first, then enrich top ICP leads only
"""

import requests, json, time, os, re, argparse
from datetime import datetime

API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY', '')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

NEARBY_URL  = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
TEXT_URL    = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
DETAIL_URL  = 'https://maps.googleapis.com/maps/api/place/details/json'
GEOCODE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

LOCATIONS = [
    # (city, state, lat, lng, radius_m)
    # --- KUALA LUMPUR & PUTRAJAYA ---
    ('Kuala Lumpur',     'Kuala Lumpur',       3.1390,  101.6869, 10000),
    ('Bukit Bintang',    'Kuala Lumpur',       3.1478,  101.7126,  3000),
    ('KLCC',             'Kuala Lumpur',       3.1579,  101.7116,  3000),
    ('Chow Kit',         'Kuala Lumpur',       3.1667,  101.6980,  3000),
    ('Mont Kiara',       'Kuala Lumpur',       3.1735,  101.6513,  3000),
    ('Bangsar',          'Kuala Lumpur',       3.1287,  101.6781,  3000),
    ('Cheras',           'Kuala Lumpur',       3.1068,  101.7259,  5000),
    ('Setiawangsa',      'Kuala Lumpur',       3.1798,  101.7450,  4000),
    ('Putrajaya',        'Putrajaya',          2.9264,  101.6964,  8000),
    ('Cyberjaya',        'Selangor',           2.9213,  101.6559,  5000),

    # --- SELANGOR ---
    ('Petaling Jaya',    'Selangor',           3.1073,  101.6067, 8000),
    ('Shah Alam',        'Selangor',           3.0738,  101.5183, 8000),
    ('Subang Jaya',      'Selangor',           3.0565,  101.5837, 6000),
    ('Klang',            'Selangor',           3.0449,  101.4479, 8000),
    ('Sepang KLIA',      'Selangor',           2.7344,  101.6898, 8000),
    ('Puchong',          'Selangor',           2.9935,  101.6215, 6000),
    ('Kajang',           'Selangor',           2.9896,  101.7885, 7000),
    ('Rawang',           'Selangor',           3.3225,  101.5770, 7000),
    ('Semenyih',         'Selangor',           2.9515,  101.8465, 5000),
    ('Banting',          'Selangor',           2.8136,  101.5018, 5000),
    ('Morib',            'Selangor',           2.7500,  101.4400, 5000),
    ('Batu Caves',       'Selangor',           3.2374,  101.6830, 4000),
    ('Gombak',           'Selangor',           3.2429,  101.7132, 5000),
    ('Ampang',           'Selangor',           3.1492,  101.7634, 5000),
    ('Seri Kembangan',   'Selangor',           3.0230,  101.7036, 6000),

    # --- PENANG ---
    ('George Town',      'Penang',             5.4141,  100.3288, 8000),
    ('Batu Ferringhi',   'Penang',             5.4665,  100.2587, 5000),
    ('Butterworth',      'Penang',             5.3991,  100.3634, 6000),
    ('Bukit Mertajam',   'Penang',             5.3636,  100.4571, 7000),
    ('Bayan Lepas',      'Penang',             5.2952,  100.2588, 6000),
    ('Seberang Jaya',    'Penang',             5.3942,  100.3984, 5000),
    ('Kepala Batas',     'Penang',             5.5171,  100.4265, 5000),
    ('Nibong Tebal',     'Penang',             5.1700,  100.4780, 5000),

    # --- JOHOR ---
    ('Johor Bahru',      'Johor',              1.4927,  103.7414, 10000),
    ('Iskandar Puteri',  'Johor',              1.4200,  103.6280, 8000),
    ('Skudai',           'Johor',              1.5469,  103.6624, 6000),
    ('Pasir Gudang',     'Johor',              1.4725,  103.9056, 7000),
    ('Batu Pahat',       'Johor',              1.8564,  102.9333, 8000),
    ('Muar',             'Johor',              2.0442,  102.5689, 6000),
    ('Kluang',           'Johor',              2.0251,  103.3328, 7000),
    ('Kulai',            'Johor',              1.6621,  103.6025, 6000),
    ('Segamat',          'Johor',              2.5029,  102.8158, 6000),
    ('Pontian',          'Johor',              1.4866,  103.3896, 5000),
    ('Kota Tinggi',      'Johor',              1.7314,  103.8993, 5000),
    ('Mersing',          'Johor',              2.4312,  103.8405, 10000),
    ('Desaru',           'Johor',              1.5458,  104.2458, 8000),
    ('Yong Peng',        'Johor',              2.0125,  103.0651, 4000),

    # --- PERAK ---
    ('Ipoh',             'Perak',              4.5975,  101.0901, 10000),
    ('Taiping',          'Perak',              4.8514,  100.7351, 6000),
    ('Teluk Intan',      'Perak',              4.0242,  101.0215, 6000),
    ('Sitiawan',         'Perak',              4.2155,  100.6975, 5000),
    ('Manjung',          'Perak',              4.1950,  100.6650, 7000),
    ('Lumut',            'Perak',              4.2325,  100.6295, 5000),
    ('Pangkor Island',   'Perak',              4.2185,  100.5512, 6000),
    ('Kuala Kangsar',    'Perak',              4.7675,  100.9415, 5000),
    ('Batu Gajah',       'Perak',              4.4715,  101.0425, 4000),
    ('Kampar',           'Perak',              4.3075,  101.1515, 5000),
    ('Tapah',            'Perak',              4.1833,  101.2667, 4000),
    ('Tanjung Malim',    'Perak',              3.6825,  101.5215, 4000),
    ('Sungkai',          'Perak',              3.9967,  101.3093, 4000),

    # --- KEDAH & PERLIS ---
    ('Alor Setar',       'Kedah',              6.1208,  100.3685, 8000),
    ('Sungai Petani',    'Kedah',              5.6433,  100.4917, 8000),
    ('Kulim',            'Kedah',              5.3700,  100.5500, 6000),
    ('Langkawi Kuah',    'Kedah',              6.3265,   99.8432, 8000),
    ('Langkawi Pantai Cenang','Kedah',         6.2942,   99.7289, 6000),
    ('Kangar',           'Perlis',             6.4409,  100.1979, 6000),
    ('Arau',             'Perlis',             6.4297,  100.2764, 4000),
    ('Kuala Perlis',     'Perlis',             6.4000,  100.1333, 4000),

    # --- PAHANG ---
    ('Kuantan',          'Pahang',             3.8226,  103.3256, 10000),
    ('Temerloh',         'Pahang',             3.4477,  102.4172, 6000),
    ('Bentong',          'Pahang',             3.5222,  101.9075, 5000),
    ('Raub',             'Pahang',             3.7917,  101.8583, 5000),
    ('Kuala Lipis',      'Pahang',             4.1833,  102.0500, 4000),
    ('Jerantut',         'Pahang',             3.9333,  102.3500, 5000),
    ('Pekan',            'Pahang',             3.4833,  103.3833, 5000),
    ('Rompin',           'Pahang',             2.8167,  103.4833, 6000),
    ('Cameron Highlands','Pahang',             4.4714,  101.3865, 12000),
    ('Genting Highlands','Pahang',             3.4231,  101.7936, 8000),
    ('Bukit Tinggi',     'Pahang',             3.3500,  101.8333, 4000),
    ('Frasers Hill',     'Pahang',             3.7167,  101.7333, 4000),
    ('Tioman Island',    'Pahang',             2.8115,  104.1666, 10000),

    # --- NEGERI SEMBILAN & MELAKA ---
    ('Seremban',         'Negeri Sembilan',    2.7297,  101.9381, 8000),
    ('Port Dickson',     'Negeri Sembilan',    2.5219,  101.7955, 10000),
    ('Nilai',            'Negeri Sembilan',    2.8167,  101.7972, 6000),
    ('Bahau',            'Negeri Sembilan',    2.8078,  102.4103, 5000),
    ('Kuala Pilah',      'Negeri Sembilan',    2.7389,  102.2486, 4000),
    ('Melaka City',      'Melaka',             2.1896,  102.2501, 10000),
    ('Ayer Keroh',       'Melaka',             2.2694,  102.3000, 5000),
    ('Alor Gajah',       'Melaka',             2.3833,  102.2167, 5000),
    ('Jasin',            'Melaka',             2.3083,  102.4314, 4000),

    # --- KELANTAN & TERENGGANU ---
    ('Kota Bharu',       'Kelantan',           6.1254,  102.2526, 8000),
    ('Pasir Mas',        'Kelantan',           6.0417,  102.1417, 5000),
    ('Tumpat',           'Kelantan',           6.1953,  102.1628, 5000),
    ('Gua Musang',       'Kelantan',           4.8833,  101.9667, 5000),
    ('Machang',          'Kelantan',           5.7667,  102.2167, 4000),
    ('Kuala Terengganu', 'Terengganu',         5.3296,  103.1370, 8000),
    ('Chukai',           'Terengganu',         4.2500,  103.4167, 6000),
    ('Kemaman',          'Terengganu',         4.2250,  103.4250, 6000),
    ('Dungun',           'Terengganu',         4.7500,  103.4167, 5000),
    ('Besut',            'Terengganu',         5.8333,  102.5500, 5000),
    ('Marang',           'Terengganu',         5.2000,  103.2000, 4000),
    ('Redang Island',    'Terengganu',         5.7831,  102.9985, 8000),
    ('Perhentian',       'Terengganu',         5.9048,  102.7720, 8000),

    # --- SABAH ---
    ('Kota Kinabalu',    'Sabah',              5.9788,  116.0753, 10000),
    ('Sandakan',         'Sabah',              5.8402,  118.1179, 8000),
    ('Tawau',            'Sabah',              4.2449,  117.8910, 6000),
    ('Lahad Datu',       'Sabah',              5.0333,  118.3333, 6000),
    ('Semporna',         'Sabah',              4.4811,  118.6111, 8000),
    ('Kudat',            'Sabah',              6.8833,  116.8333, 5000),
    ('Beaufort',         'Sabah',              5.3472,  115.7481, 4000),
    ('Keningau',         'Sabah',              5.3333,  116.1667, 5000),
    ('Ranau',            'Sabah',              5.9500,  116.6667, 5000),
    ('Kundasang',        'Sabah',              5.9861,  116.5764, 5000),
    ('Labuan',           'Labuan',             5.2833,  115.2333, 8000),

    # --- SARAWAK ---
    ('Kuching',          'Sarawak',            1.5497,  110.3592, 10000),
    ('Miri',             'Sarawak',            4.3995,  113.9914, 8000),
    ('Sibu',             'Sarawak',            2.2893,  111.8285, 7000),
    ('Bintulu',          'Sarawak',            3.1699,  113.0397, 6000),
    ('Limbang',          'Sarawak',            4.7500,  115.0000, 5000),
    ('Sarikei',          'Sarawak',            2.1167,  111.5167, 5000),
    ('Sri Aman',         'Sarawak',            1.2333,  111.4500, 4000),
    ('Kapit',            'Sarawak',            2.0167,  112.9333, 4000),
    ('Betong',           'Sarawak',            1.4167,  111.5333, 4000),
    ('Mukah',            'Sarawak',            2.9000,  112.0833, 4000),
    ('Lawas',            'Sarawak',            4.8500,  115.4000, 4000),
]

# Text search queries per city
SEARCH_QUERIES = [
    '3 star hotel {city} Malaysia',
    '4 star hotel {city} Malaysia',
    'boutique hotel {city} Malaysia',
    'business hotel {city} Malaysia',
    'resort {city} Malaysia',
    'homestay {city} Malaysia',
    'guest house {city} Malaysia',
    'serviced apartment {city} Malaysia',
    'motel {city} Malaysia',
    'inn {city} Malaysia',
    'vacation rental {city} Malaysia',
]

DETAIL_FIELDS = [
    'name','formatted_address','formatted_phone_number',
    'international_phone_number','website','url',
    'rating','user_ratings_total','business_status','opening_hours','types',
]

def clean_phone(p):
    p = re.sub(r'[\s\-\.\(\)]','',str(p or ''))
    if p.startswith('0') and len(p)>7: p='+60'+p[1:]
    elif p.startswith('60') and not p.startswith('+60') and len(p)>8: p='+'+p
    return p

def is_mobile(p):
    return bool(re.match(r'^\+?601[0-9]', (p or '').replace(' ','')))

def _get(url, params, retries=3):
    for i in range(retries):
        try:
            r = requests.get(url, params=params, timeout=15)
            data = r.json()
            if data.get('status') in ('OK','ZERO_RESULTS','NOT_FOUND'):
                return data
            if data.get('status') == 'OVER_QUERY_LIMIT':
                print('  RATE LIMIT — sleeping 10s')
                time.sleep(10)
            else:
                time.sleep(1)
        except Exception as e:
            if i==retries-1: print(f'  request error: {e}')
            time.sleep(2**i)
    return {}

def nearby_search(lat, lng, radius, api_key):
    """Nearby search — returns up to 60 results (3 pages)."""
    results, token = [], None
    for _ in range(3):
        params = {'location':f'{lat},{lng}','radius':radius,'type':'lodging',
                  'key':api_key,'language':'en'}
        if token: params = {'pagetoken':token,'key':api_key}; time.sleep(2)
        data = _get(NEARBY_URL, params)
        results.extend(data.get('results',[]))
        token = data.get('next_page_token')
        if not token: break
    return results

def text_search(query, api_key):
    """Text search — returns up to 60 results (3 pages)."""
    results, token = [], None
    for _ in range(3):
        params = {'query':query,'type':'lodging','key':api_key,'language':'en','region':'my'}
        if token: params = {'pagetoken':token,'key':api_key}; time.sleep(2)
        data = _get(TEXT_URL, params)
        results.extend(data.get('results',[]))
        token = data.get('next_page_token')
        if not token: break
    return results

def get_details(place_id, api_key):
    params = {'place_id':place_id,'fields':','.join(DETAIL_FIELDS),'key':api_key,'language':'en'}
    data = _get(DETAIL_URL, params)
    return data.get('result', {})

def place_to_hotel(place, city, state, details=None):
    name = place.get('name','')
    place_id = place.get('place_id','')
    addr = place.get('formatted_address','') or place.get('vicinity','')
    rating = place.get('rating','')
    reviews = place.get('user_ratings_total','')
    status = place.get('business_status','')
    if status == 'CLOSED_PERMANENTLY': return None

    phone = ''
    website = ''
    gmaps_url = f'https://www.google.com/maps/place/?q=place_id:{place_id}'

    if details:
        phone = clean_phone(details.get('international_phone_number','') or details.get('formatted_phone_number',''))
        website = details.get('website','')
        gmaps_url = details.get('url', gmaps_url)
        rating = details.get('rating', rating)
        reviews = details.get('user_ratings_total', reviews)

    mobile = is_mobile(phone)

    # ICP scoring
    score, flags = 0, []
    p = {'Kuala Lumpur':1,'Selangor':2,'Penang':3,'Johor':4,'Sabah':5,'Sarawak':6,'Perak':7,'Melaka':8}.get(state,10)
    score += max(0, 3-(p//3))
    if phone: score+=1+int(mobile); flags.append('WhatsApp' if mobile else 'Phone')
    if website: score+=1

    return {
        'hotel_name': name,
        'hotel_name_upper': name.upper(),
        'state': state, 'city': city,
        'star_rating': '', 'num_rooms': None,
        'postcode': (re.search(r'\b(\d{5})\b', addr) or [None,None])[1] or '',
        'address': addr,
        'phone': phone, 'is_mobile_whatsapp': mobile,
        'email': '', 'website': website,
        'icp_score': score, 'icp_flags': ' | '.join(flags),
        'source': 'Google Places',
        'google_found': True,
        'google_place_id': place_id,
        'google_name': name,
        'google_address': addr,
        'google_phone': phone,
        'google_website': website,
        'google_maps_url': gmaps_url,
        'google_rating': rating,
        'google_reviews': reviews,
        'google_business_status': status,
        'has_after_hours_gap': True,
        'whatsapp_number': phone if mobile else '',
        'whatsapp_source': 'google_places' if mobile else '',
        'member_id': '',
    }

def run(api_key, city_filter=None, limit=None, get_details_flag=True, resume=False):
    if not api_key:
        print('ERROR: Set GOOGLE_PLACES_API_KEY environment variable')
        return []

    seen_ids = set()
    seen_names = set()
    hotels = []

    processed_cities = set()
    # Resume from checkpoint
    if resume:
        cp = os.path.join(OUTPUT_DIR, 'google_places_checkpoint.json')
        if os.path.exists(cp):
            with open(cp, 'r', encoding='utf-8') as f: prev = json.load(f)
            hotels = prev
            seen_ids = {h['google_place_id'] for h in prev if h.get('google_place_id')}
            seen_names = {h['hotel_name_upper'] for h in prev}
            # Infer processed cities from the data
            processed_cities = {h.get('city') for h in prev if h.get('city')}
            print(f'Resumed from checkpoint: {len(hotels)} hotels, {len(processed_cities)} cities already processed')

    locs = [l for l in LOCATIONS if not city_filter or l[0] in city_filter]
    total_locs = len(locs)

    for i, (city, state, lat, lng, radius) in enumerate(locs):
        if resume and city in processed_cities:
            print(f'[{i+1}/{total_locs}] Skipping {city} (already in checkpoint)')
            continue
            
        print(f'\n[{i+1}/{total_locs}] {city}, {state}')

        # Nearby search
        nearby = nearby_search(lat, lng, radius, api_key)
        print(f'  Nearby: {len(nearby)} raw results')
        time.sleep(0.2)

        # Text searches
        text_results = []
        for q_tmpl in SEARCH_QUERIES:
            q = q_tmpl.format(city=city)
            tr = text_search(q, api_key)
            text_results.extend(tr)
            time.sleep(0.2)
        print(f'  Text: {len(text_results)} raw results')

        # Merge and deduplicate
        all_places = {p['place_id']: p for p in (nearby + text_results) if p.get('place_id')}.values()
        new_count = 0

        for place in all_places:
            pid = place.get('place_id','')
            if pid in seen_ids: continue
            nm = (place.get('name','') or '').upper()
            if nm in seen_names: continue

            details = {}
            if get_details_flag and pid:
                details = get_details(pid, api_key)
                time.sleep(0.12)

            h = place_to_hotel(place, city, state, details if details else None)
            if h:
                seen_ids.add(pid)
                seen_names.add(nm)
                hotels.append(h)
                new_count += 1

        print(f'  Added {new_count} new hotels. Total: {len(hotels)}')

        # Save checkpoint every location
        if (i+1) % 3 == 0:
            cp = os.path.join(OUTPUT_DIR, 'google_places_checkpoint.json')
            with open(cp,'w',encoding='utf-8') as f: json.dump(hotels,f,indent=2,ensure_ascii=False)

        if limit and len(hotels) >= limit:
            print(f'  Reached limit of {limit}')
            break

    return hotels

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cities', default='', help='Comma-separated cities to include')
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--no-details', action='store_true', help='Skip detail API calls (cost saving)')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--output', default='google_places_raw.json')
    parser.add_argument('--api-key', default='')
    args = parser.parse_args()

    api_key = args.api_key or API_KEY
    city_filter = set(c.strip() for c in args.cities.split(',') if c.strip()) or None

    print(f'Google Places Bulk Scraper — {len(LOCATIONS)} locations')
    print(f'API key: {"SET ✓" if api_key else "NOT SET ✗"}')
    print(f'Detail lookup: {"OFF (--no-details)" if args.no_details else "ON"}')
    print(f'Started: {datetime.now():%Y-%m-%d %H:%M:%S}\n')

    hotels = run(api_key, city_filter=city_filter, limit=args.limit,
                 get_details_flag=not args.no_details, resume=args.resume)

    out = os.path.join(OUTPUT_DIR, args.output)
    with open(out,'w',encoding='utf-8') as f:
        json.dump(hotels,f,indent=2,ensure_ascii=False)

    has_phone = sum(1 for h in hotels if h.get('phone'))
    has_mobile = sum(1 for h in hotels if h.get('is_mobile_whatsapp'))
    has_web = sum(1 for h in hotels if h.get('website'))

    print(f'\n=== COMPLETE ===')
    print(f'Total unique hotels: {len(hotels):,}')
    print(f'Has phone:           {has_phone:,}')
    print(f'Has mobile/WhatsApp: {has_mobile:,}')
    print(f'Has website:         {has_web:,}')
    print(f'Saved to: {out}')

if __name__ == '__main__':
    main()
