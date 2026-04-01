"""
WhatsApp Formatter for Lead List
Converts the specialized lead list into a format ready for import into 
WhatsApp automation tools (Wati, Zoko, Twilio).

Target Format:
- Full Name (Hotel Name)
- Phone (Cleaned international format)
- Attribute: State
- Attribute: City
- Attribute: Rooms
- Attribute: Agoda_Waste
- Attribute: ROI_Potential
"""

import csv
import os
import re

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')

def clean_phone_for_wa(p):
    # Ensure it starts with +60 (Malaysia) and has no spaces
    p = re.sub(r'[\s\-\.\(\)]','',str(p or ''))
    if p.startswith('0') and len(p)>7: p='60'+p[1:]
    elif p.startswith('+60'): p=p[1:]
    elif p.startswith('60'): pass
    else: p = '60' + p # assume Malaysia if missing
    return p

def format_for_wati():
    input_path = os.path.join(OUTPUT_DIR, 'nocturn_leads_special_icp.csv')
    if not os.path.exists(input_path):
        print(f"ERROR: {input_path} not found.")
        return
        
    output_path = os.path.join(OUTPUT_DIR, 'nocturn_leads_whatsapp_ready.csv')
    
    with open(input_path, 'r', encoding='utf-8-sig') as f_in, \
         open(output_path, 'w', newline='', encoding='utf-8') as f_out:
        
        reader = csv.DictReader(f_in)
        # Wati/Zoko standard headers
        fieldnames = ['name', 'phone', 'state', 'city', 'rooms', 'agoda_waste', 'roi_potential']
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        
        count = 0
        for row in reader:
            phone = clean_phone_for_wa(row.get('WhatsApp Number') or row.get('Phone'))
            if not phone: continue
            
            writer.writerow({
                'name': row.get('Hotel Name'),
                'phone': phone,
                'state': row.get('State'),
                'city': row.get('City'),
                'rooms': row.get('Rooms'),
                'agoda_waste': row.get('Est. Monthly Agoda Waste (RM)'),
                'roi_potential': row.get('Nocturn Recovery Potential (RM)')
            })
            count += 1
            
    print(f"Successfully formatted {count} leads for WhatsApp import.")
    print(f"Output: {output_path}")

if __name__ == "__main__":
    format_for_wati()
