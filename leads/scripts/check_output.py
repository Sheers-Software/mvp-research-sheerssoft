import json, os
from collections import Counter

with open('output/mah_raw.json', 'r', encoding='utf-8') as f:
    hotels = json.load(f)

total = len(hotels)
star34 = sum(1 for h in hotels if any(s in h.get('star_rating','') for s in ['3 Star','4 Star']))
hot = sum(1 for h in hotels if h.get('icp_score',0) >= 8)
warm = sum(1 for h in hotels if 5 <= h.get('icp_score',0) < 8)
cold = sum(1 for h in hotels if 3 <= h.get('icp_score',0) < 5)
with_email = sum(1 for h in hotels if h.get('email'))
with_whatsapp = sum(1 for h in hotels if h.get('is_mobile_whatsapp'))
with_phone = sum(1 for h in hotels if h.get('phone'))
with_website = sum(1 for h in hotels if h.get('website'))

states = Counter(h.get('state','?') for h in hotels)
stars = Counter(h.get('star_rating','?') for h in hotels)

print('=== LEAD LIST STATS ===')
print(f'Total hotels:        {total}')
print(f'3-4 Star:            {star34}')
print(f'HOT (score >= 8):    {hot}')
print(f'WARM (score 5-7):    {warm}')
print(f'COLD (score 3-4):    {cold}')
print(f'With email:          {with_email}')
print(f'With phone:          {with_phone}')
print(f'With WhatsApp mob.:  {with_whatsapp}')
print(f'With website:        {with_website}')
print()
print('--- BY STATE ---')
for state, count in states.most_common(10):
    print(f'  {state:<25} {count}')
print()
print('--- BY STAR RATING ---')
for star, count in stars.most_common():
    print(f'  {star:<20} {count}')
print()
print('--- SAMPLE HOT LEADS ---')
for h in [x for x in hotels if x.get('icp_score',0) >= 8][:5]:
    print(f'  [{h.get("icp_score")}] {h.get("hotel_name")} | {h.get("city")}, {h.get("state")}')
    print(f'       Email: {h.get("email")} | Phone: {h.get("phone")}')
    print(f'       Rooms: {h.get("num_rooms")} | Star: {h.get("star_rating")}')
print()
print('--- EXPORTED CSV FILES ---')
for fn in sorted(os.listdir('output')):
    if fn.endswith('.csv'):
        size = os.path.getsize(f'output/{fn}') // 1024
        print(f'  {fn:<55} {size} KB')
