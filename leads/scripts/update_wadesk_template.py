import pandas as pd
import os
import re

# Paths
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
INPUT_CSV = os.path.join(BASE_DIR, 'output', 'nocturn_leads_all.csv')
TEMPLATE_XLSX = os.path.join(BASE_DIR, 'WADesk_SenderTemplate.xlsx')

def clean_phone_for_wa(p):
    # Ensure it's in string format and remove non-numeric chars
    p = re.sub(r'[\s\-\.\(\)\+]','',str(p or ''))
    if p.startswith('0') and len(p)>7: p='60'+p[1:]
    elif p.startswith('60'): pass
    elif p.startswith('1') or p.startswith('7') or p.startswith('9'): 
        p = '60' + p # assume Malaysia if it looks like a local number
    return p

def update_template():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found.")
        return
        
    print(f"Reading leads from {INPUT_CSV}...")
    df_all = pd.read_csv(INPUT_CSV)
    
    # Filter for WhatsApp leads
    df_wa = df_all[df_all['nocturn_has_whatsapp'] == 'YES'].copy()
    print(f"Found {len(df_wa)} WhatsApp leads.")
    
    # Map columns
    # Template columns: ['WhatsApp Number(with country code)', 'First Name', 'Last Name', 'Variable1', 'Variable2', 'Variable3', 'Variable4']
    
    output_data = {
        'WhatsApp Number(with country code)': df_wa['nocturn_whatsapp_number'].apply(clean_phone_for_wa),
        'First Name': df_wa['company'],
        'Last Name': '',
        'Variable1': df_wa['city'],
        'Variable2': df_wa['nocturn_room_count'],
        'Variable3': df_wa['nocturn_pilot_roi_estimate'],
        'Variable4': df_wa['nocturn_icp_tier']
    }
    
    df_output = pd.DataFrame(output_data)
    
    # Save to Excel
    print(f"Updating template {TEMPLATE_XLSX}...")
    df_output.to_excel(TEMPLATE_XLSX, index=False)
    print("Successfully updated the template.")

if __name__ == "__main__":
    update_template()
