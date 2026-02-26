"""
Segment B — Homestay, Villa, Chalet, Inn Knowledge Base (Part 5)
Expanded: Guest reviews, local 'taboos', hidden charges, long-term parking
~100 entries
"""

import random

DOCS = []

# 1. Local 'Taboos' & Etiquette
DOCS.extend([
    {"doc_type": "house_rules", "title": "Local Community Etiquette",
     "content": "Q: Is there anything specific we should know about the local neighborhood?\nA: Our property is located in a family-oriented residential area. We kindly ask you to dress modestly when walking through the neighborhood (covering shoulders and knees is appreciated). Please avoid loud music outdoors after 10 PM. A friendly 'Salam' or a wave to neighbors goes a long way in showing respect!"},
    {"doc_type": "house_rules", "title": "Strict No-Alcohol Areas (if applicable)",
     "content": "Q: Are we allowed to drink alcohol on the premises?\nA: While you are free to enjoy your own drinks inside the property, we kindly ask that alcohol is not consumed in plain sight of the neighbors on the front porch or driveway. This is to respect the local community's cultural sensitivities. Restraint and discretion are highly appreciated."},
])

# 2. Hidden Charges & Refunds
DOCS.extend([
    {"doc_type": "policies", "title": "Security Deposit Refund Timeline",
     "content": "Q: When will I get my security deposit back?\nA: After check-out, our caretaker will inspect the property within 24 hours. If everything is in good order, your deposit will be refunded via your original payment method or bank transfer within 3–5 business days. You will receive a notification once the process is complete."},
    {"doc_type": "policies", "title": "Extra Cleaning Fee Details",
     "content": "Q: Under what circumstances do you charge an extra cleaning fee?\nA: The standard cleaning fee is included in your booking. Extras are only charged for: heavy stains on fabric/carpets, excessive waste left behind (not in bins), or traces of smoking indoors. Our goal is to maintain a high standard for all guests, and we appreciate you leaving the place tidy!"},
])

# 3. Generating Bulk Variations
for i in range(1, 41):
    spot = random.choice(["Driveway", "Roadside", "Designated Lot", "Covered Area", "Visitor Parking"])
    limit = random.choice(["1 car", "2 cars", "No trucks", "No caravans", "First come first served"])
    DOCS.append({
        "doc_type": "local_area",
        "title": f"Parking Spot: {spot} - {limit}",
        "content": f"Q: Is there parking available in the {spot}? Is there a limit?\nA: Yes, you can park in the {spot}. The limit is {limit}. Please ensure your vehicle doesn't block any neighboring driveways. We recommend parking within the property gates whenever possible for added security. For larger vehicles, please consult us in advance."
    })

for i in range(1, 41):
    item = random.choice(["hairdryer", "ironing board", "emergency light", "first aid kit", "fire extinguisher"])
    room = random.choice(["Utility Room", "Master Wardrobe", "Kitchen Cabinet", "Under Stairs", "Entryway"])
    DOCS.append({
        "doc_type": "utilities",
        "title": f"Finding the {item} in the {room}",
        "content": f"Q: I can't find the {item}. Is it in the {room}?\nA: Yes, the {item} is kept in the {room}. If it's not there, it might have been moved by a previous guest — please let us know immediately so we can locate it or provide a replacement for you. Your comfort is our priority!"
    })
DOCS.append({"doc_type": "local_area", "title": "Mosque Proximity & Call to Prayer", "content": "Q: Can we hear the Adhan (Call to Prayer) from the property?\nA: Yes, there is a local mosque nearby. Most guests find the Adhan to be a peaceful and cultural part of the experience. It happens 5 times a day. If you are a light sleeper, we've provided earplugs in the bedside drawer for the early morning call."})
