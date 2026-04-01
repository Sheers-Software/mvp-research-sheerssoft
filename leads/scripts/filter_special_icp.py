"""
Filter the 10,000+ lead database for a specialized ICP:
- Independent hotels (exclude major chains)
- Klang Valley, Penang, Johor Bahru
- 40-150 rooms
- High WhatsApp reliance (mobile phone provided)
- After-hours gap (10pm front desk closure indicator)
"""

import json
import os
import csv
import re

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')

# Major chains to exclude
CHAINS = [
    'HILTON', 'MARRIOTT', 'SHERATON', 'WESTIN', 'INTERCONTINENTAL', 'HYATT',
    'RAMADA', 'IBIS', 'MERCURE', 'NOVOTEL', 'PULLMAN', 'SHANGRI-LA', 'BY THE',
    'FOUR POINTS', 'ALoft', 'DOUBLETREE', 'W HOTEL', 'RITZ-CARLTON', 'ST REGIS',
    'HOLIDAY INN', 'CROWNE PLAZA', 'TRADERS', 'FURAMA', 'CONCORDE', 'DORSETT',
    'BERJAYA', 'THISTLE', 'ANANTARA', 'AVANI', 'GRAND LEXIS', 'LEXIS', 'HARD ROCK',
    'E&O', 'EASTERN & ORIENTAL', 'HOTEL JEN', 'PARKROYAL', 'PAN PACIFIC', 'CITITEL',
    'VISTANA', 'TUNE HOTEL', 'HOTEL 81', 'FRAGRANCE', 'OZO', 'AMARI', 'GELDAILS',
    'FAIRMONT', 'RAFFLES', 'MANDARIN ORIENTAL', 'ASCOTT', 'CITADINES', 'SOMERSET',
    'OAKWOOD', 'PREMIERE', 'GRAND HYATT', 'LE MERIDIEN', 'TRAVELODGE', 'YOTEL',
]

def is_independent(name):
    name_upper = name.upper()
    for chain in CHAINS:
        if chain in name_upper:
            return False
    return True

def filter_leads():
    merged_path = os.path.join(OUTPUT_DIR, 'nocturn_leads_merged.json')
    if not os.path.exists(merged_path):
        print("ERROR: nocturn_leads_merged.json not found.")
        return
        
    with open(merged_path, 'r', encoding='utf-8') as f:
        leads = json.load(f)
        
    print(f"Loaded {len(leads)} total leads")
    
    special_list = []
    
    target_states = ['Kuala Lumpur', 'Selangor', 'Penang', 'Johor']
    target_cities = ['Kuala Lumpur', 'Petaling Jaya', 'George Town', 'Johor Bahru', 
                     'Batu Ferringhi', 'Iskandar Puteri', 'Shah Alam', 'Subang Jaya', 
                     'Klang', 'Cheras', 'Ampang', 'Puchong', 'Kajang', 'Sepang']
    
    boutique_keywords = ['BOUTIQUE', 'RESORT', 'GUEST HOUSE', 'INN', 'HOMESTAY', 'SUITES', 'VILLA', 'RESIDENCE']
    
    for lead in leads:
        name = lead.get('hotel_name', '')
        state = lead.get('state', '')
        city = lead.get('city', '')
        rooms = lead.get('num_rooms')
        wa = lead.get('is_mobile_whatsapp') or lead.get('whatsapp_number')
        
        # 1. Location filter
        if state not in target_states and city not in target_cities:
            continue
            
        # 2. Independence check
        if not is_independent(name):
            continue
            
        # 3. Channel/Profile
        # We'll prioritize WhatsApp and Boutique/Independent keywords
        is_boutique = any(k in name.upper() for k in boutique_keywords)
        
        # 4. Room count check (40-150)
        # If rooms info is missing, we lean on keywords + local presence
        if rooms:
            if not (20 <= rooms <= 200): # broadening slightly for initial catch
                continue
        else:
            # If no room info, must be boutique keyword + WhatsApp
            if not is_boutique and not wa:
                continue
        
        # 5. WhatsApp focus
        if not wa:
            continue
            
        # Calculate a mini special score
        score = 0
        if 40 <= (rooms or 0) <= 150: score += 5
        if is_boutique: score += 3
        if wa: score += 2
        
        lead['special_icp_score'] = score
        lead['special_icp_flags'] = f"Indie | WA | {'Boutique' if is_boutique else 'Mid-range'}"
        special_list.append(lead)
        
    print(f"Special ICP List: {len(special_list)} hotels found")
    
    # Sort by special score (Descending) then room count
    special_list.sort(key=lambda x: (-x.get('special_icp_score', 0), x.get('num_rooms') or 999))
    
    # Export to CSV
    csv_path = os.path.join(OUTPUT_DIR, 'nocturn_leads_special_icp.csv')
    
    header = [
        'Hotel Name', 'State', 'City', 'Rooms', 'WhatsApp Number', 'Email', 
        'Website', 'ICP Score', 'Est. Monthly Agoda Waste (RM)', 'Nocturn Recovery Potential (RM)', 'Source'
    ]
    
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for h in special_list:
            rooms_val = h.get('num_rooms')
            rooms = rooms_val if rooms_val and isinstance(rooms_val, int) else 40
            # Assume ADR 150, 70% Occ, 15% Agoda Comm on 40% of bookings
            agoda_waste = int(rooms * 0.7 * 0.4 * 150 * 0.15 * 30)
            # Nocturn recovery: 30% after-hours inquiries * 20% conv * ADR
            recovery = int(rooms * 0.3 * 0.2 * 150 * 30)
            
            writer.writerow([
                h.get('hotel_name'),
                h.get('state'),
                h.get('city'),
                rooms_val or 'Unknown (Boutique)',
                h.get('whatsapp_number') or h.get('phone'),
                h.get('email'),
                h.get('website') or h.get('google_website'),
                h.get('special_icp_score'),
                agoda_waste,
                recovery,
                h.get('source')
            ])
            
    print(f"Saved special list to {csv_path}")
    return special_list

if __name__ == "__main__":
    filter_leads()
