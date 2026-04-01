"""
Merge all lead sources (MAH, Google Places) and deduplicate.
Deduplication logic:
1. Exact match on member_id (if available)
2. Normalised name match + City match
3. Google Place ID match
"""

import json
import os
import re

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')

def normalize_name(name):
    if not name: return ""
    # Remove special characters, handle common suffixes
    name = name.upper()
    name = re.sub(r'[^A-Z0-9\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def merge_leads():
    mah_path = os.path.join(OUTPUT_DIR, 'mah_raw.json')
    # Try expanded output first, then checkpoint, then raw
    gp_options = ['google_places_expanded.json', 'google_places_checkpoint.json', 'google_places_raw.json']
    gp_path = None
    for opt in gp_options:
        p = os.path.join(OUTPUT_DIR, opt)
        if os.path.exists(p):
            gp_path = p
            break
            
    mah_leads = []
    if os.path.exists(mah_path):
        with open(mah_path, 'r', encoding='utf-8') as f:
            mah_leads = json.load(f)
            
    gp_leads = []
    if os.path.exists(gp_path):
        with open(gp_path, 'r', encoding='utf-8') as f:
            gp_leads = json.load(f)
            
    print(f"Loaded {len(mah_leads)} MAH leads")
    print(f"Loaded {len(gp_leads)} Google Places leads")
    
    merged = []
    seen_ids = set() # member_id or place_id
    seen_names = {} # name -> list of cities
    
    # Process MAH first (higher quality contact data)
    for lead in mah_leads:
        mid = lead.get('member_id')
        if mid:
            seen_ids.add(f"MAH_{mid}")
        
        name = normalize_name(lead.get('hotel_name'))
        city = (lead.get('city') or "").upper()
        if name:
            if name not in seen_names:
                seen_names[name] = []
            seen_names[name].append(city)
            
        merged.append(lead)
        
    # Process Google Places leads
    new_gp = 0
    duplicate_gp = 0
    
    for lead in gp_leads:
        pid = lead.get('google_place_id')
        name = normalize_name(lead.get('hotel_name'))
        city = (lead.get('city') or "").upper()
        
        is_duplicate = False
        
        # Check by Place ID (if somehow already in MAH or duplicate in GP)
        if pid and pid in seen_ids:
            is_duplicate = True
            
        # Check by Name + City
        if not is_duplicate and name in seen_names:
            if any(c == city or not c or not city for c in seen_names[name]):
                is_duplicate = True
        
        if is_duplicate:
            # Try to enrich existing MAH lead if it matches
            # For now, just skip to avoid duplicates in the CSV
            duplicate_gp += 1
            continue
        
        if pid:
            seen_ids.add(pid)
        if name:
            if name not in seen_names:
                seen_names[name] = []
            seen_names[name].append(city)
            
        merged.append(lead)
        new_gp += 1
        
    print(f"Merged Result: {len(merged)} unique hotels")
    print(f"Duplicates skipped: {duplicate_gp}")
    
    output_path = os.path.join(OUTPUT_DIR, 'nocturn_leads_merged.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    
    print(f"Saved merged leads to {output_path}")
    return merged

if __name__ == "__main__":
    merge_leads()
