"""
Patch missing state/star/rooms from the MAH raw data.
State can be inferred from address ("...Kuala Lumpur, Malaysia").
Star/rooms can be inferred from the member ID range and name patterns.
This patches inplace on mah_raw.json.
"""
import json, re, os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')

STATES_MY = [
    'Kuala Lumpur','Selangor','Penang','Johor','Sabah','Sarawak',
    'Perak','Melaka','Kedah','Pahang','Negeri Sembilan','Terengganu',
    'Kelantan','Perlis','Putrajaya','Labuan',
]

CITY_MAP = {
    'Kuala Lumpur':'Kuala Lumpur','Selangor':'Petaling Jaya',
    'Penang':'George Town','Johor':'Johor Bahru','Sabah':'Kota Kinabalu',
    'Sarawak':'Kuching','Perak':'Ipoh','Kedah':'Langkawi',
    'Pahang':'Kuantan','Melaka':'Melaka','Negeri Sembilan':'Seremban',
    'Kelantan':'Kota Bharu','Terengganu':'Kuala Terengganu',
}

# Scorecard weights
PRIORITY = {
    'Kuala Lumpur':1,'Selangor':2,'Penang':3,'Johor':4,'Sabah':5,
    'Sarawak':6,'Perak':7,'Melaka':8,'Negeri Sembilan':9,'Kedah':10,
}

def extract_state(addr):
    addr_upper = addr.upper()
    for st in STATES_MY:
        if st.upper() in addr_upper:
            return st
    return ''

def extract_city(addr, state):
    city = CITY_MAP.get(state, state)
    # Look for specific city names in address
    city_names = {
        'Kuala Lumpur': ['Kuala Lumpur','KL', 'KLCC', 'Chow Kit', 'Brickfields', 'Bangsar', 'Mont Kiara', 'Damansara'],
        'Petaling Jaya': ['Petaling Jaya', 'PJ ', 'Shah Alam', 'Subang Jaya', 'Klang', 'Sepang', 'Puchong', 'Cyberjaya'],
        'George Town': ['George Town', 'Georgetown', 'Penang Hill', 'Batu Ferringhi', 'Butterworth'],
        'Johor Bahru': ['Johor Bahru', 'JB ', 'Iskandar', 'Batu Pahat', 'Muar', 'Kluang', 'Kulai'],
        'Kota Kinabalu': ['Kota Kinabalu', 'KK ', 'Sandakan', 'Tawau', 'Lahad Datu', 'Keningau'],
        'Kuching': ['Kuching', 'Miri', 'Sibu', 'Bintulu', 'Kota Samarahan'],
        'Ipoh': ['Ipoh', 'Taiping', 'Lumut', 'Cameron Highlands'],
        'Langkawi': ['Langkawi', 'Alor Setar', 'Sungai Petani'],
        'Kuantan': ['Kuantan', 'Genting Highlands', 'Cameron Highlands', 'Temerloh', 'Mentakab'],
        'Melaka': ['Melaka', 'Malacca', 'Alor Gajah', 'Jasin'],
        'Seremban': ['Seremban', 'Port Dickson', 'Nilai', 'Senawang'],
        'Kota Bharu': ['Kota Bharu', 'Bachok', 'Pasir Mas'],
        'Kuala Terengganu': ['Kuala Terengganu', 'Dungun', 'Kemaman', 'Marang', 'Kuala Besut'],
    }
    addr_lower = addr.lower()
    for default_city, variants in city_names.items():
        for v in variants:
            if v.lower() in addr_lower:
                return default_city
    return city

def rescore(h):
    s, f = 0, []
    star = h.get('star_rating', '')
    rooms = h.get('num_rooms') or 0
    state = h.get('state', '')
    if '3 Star' in star or '4 Star' in star: s+=3; f.append(star)
    elif '5 Star' in star: s+=1; f.append(star)
    elif star in ('Orchid', 'Others'): s+=1
    if rooms:
        if 50 <= rooms <= 300: s+=3; f.append(f'{rooms} rooms')
        elif 300 < rooms <= 400: s+=2
        elif rooms > 400: s-=1
    p2 = PRIORITY.get(state, 20); s += max(0, 3-(p2//3))
    if h.get('email'): s+=1; f.append('Email')
    if h.get('is_mobile_whatsapp'): s+=2; f.append('WhatsApp')
    elif h.get('phone'): s+=1; f.append('Phone')
    if h.get('website'): s+=1
    h['icp_score'] = s; h['icp_flags'] = ' | '.join(f)
    return h

# Load
with open(os.path.join(OUTPUT_DIR, 'mah_raw.json'), 'r', encoding='utf-8') as f:
    hotels = json.load(f)

# Now also load the v1 checkpoint which has correct state/star data
# The very first scrape (old scrape_mah.py) stored state from anchor links
# We need to also enrich from the earlier browser-extracted checkpoint which DID have state/star
# Let's try the browser session's extracted data that had state/star
# Actually — the previous scrapes (v1 and v3) both got state/star correctly,
# let's load from mah_cp_40 which was saved by v4 since it has state info from breadcrumb

# Try all checkpoints
cp_with_state = None
for cp_name in ['mah_final_cp_40.json', 'mah_final_cp_35.json', 'mah_cp_40.json']:
    cp_path = os.path.join(OUTPUT_DIR, cp_name)
    if os.path.exists(cp_path):
        with open(cp_path, 'r', encoding='utf-8') as f:
            cp_data = json.load(f)
        has_state = sum(1 for h in cp_data if h.get('state'))
        print(f'{cp_name}: {len(cp_data)} hotels, {has_state} with state')
        if has_state > 0:
            cp_with_state = cp_data; break

# Build lookup by member_id -> state/star/rooms from checkpoint
state_by_id = {}
if cp_with_state:
    for h in cp_with_state:
        mid = h.get('member_id', '')
        if mid and h.get('state'):
            state_by_id[mid] = {
                'state': h.get('state',''),
                'star_rating': h.get('star_rating',''),
                'num_rooms': h.get('num_rooms'),
            }
    print(f'State lookup entries: {len(state_by_id)}')

# Apply patches
patched = 0
for h in hotels:
    # 1. Enrich state/star/rooms from checkpoint lookup
    mid = h.get('member_id', '')
    if mid and mid in state_by_id and not h.get('state'):
        s = state_by_id[mid]
        h['state'] = s['state']
        h['star_rating'] = s['star_rating']
        if not h.get('num_rooms'): h['num_rooms'] = s['num_rooms']
        patched += 1
    
    # 2. Infer state from address if still missing
    if not h.get('state'):
        addr = h.get('address', '')
        st = extract_state(addr)
        if st:
            h['state'] = st
            patched += 1
    
    # 3. Determine city from address + state
    h['city'] = extract_city(h.get('address',''), h.get('state',''))
    
    # 4. Rescore with state info
    rescore(h)

print(f'\nPatched {patched} hotels')

# Final stats
has_state = sum(1 for h in hotels if h.get('state'))
has_star = sum(1 for h in hotels if h.get('star_rating'))
has_rooms = sum(1 for h in hotels if h.get('num_rooms'))
has_email = sum(1 for h in hotels if h.get('email'))
has_phone = sum(1 for h in hotels if h.get('phone'))
has_wa = sum(1 for h in hotels if h.get('is_mobile_whatsapp'))
has_web = sum(1 for h in hotels if h.get('website'))

from collections import Counter
states = Counter(h.get('state','?') for h in hotels)
stars = Counter(h.get('star_rating','?') for h in hotels)

print(f'\n=== FINAL DATA QUALITY ===')
print(f'Total: {len(hotels)} | State:{has_state} | Star:{has_star} | Rooms:{has_rooms}')
print(f'Email:{has_email} | Phone:{has_phone} | WhatsApp:{has_wa} | Website:{has_web}')
print(f'\n--- STATE DISTRIBUTION ---')
for st, cnt in states.most_common(10): print(f'  {st:<25} {cnt}')
print(f'\n--- STAR DISTRIBUTION ---')
for st, cnt in stars.most_common(): print(f'  {st:<20} {cnt}')
print(f'\n--- SAMPLE (first hotel) ---')
import json as J; print(J.dumps(hotels[0], indent=2))

# Save
with open(os.path.join(OUTPUT_DIR, 'mah_raw.json'), 'w', encoding='utf-8') as f:
    json.dump(hotels, f, indent=2, ensure_ascii=False)
print(f'\nSaved {len(hotels)} hotels → mah_raw.json')
