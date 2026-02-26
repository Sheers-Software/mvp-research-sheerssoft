"""
Segment B — Homestay, Villa, Chalet, Inn Knowledge Base (Part 9)
Expanded: Safety & Security Deep Dive, Emergency Contacts, Fire Safety
~100 entries
"""

import random

DOCS = []

# 1. Safety & Security Deep Dive
DOCS.extend([
    {"doc_type": "safety", "title": "Emergency Evacuation Route — Homestay",
     "content": "Q: In case of fire, what is the quickest way out?\nA: Your safety is our priority. A laminated 'Home Safety Map' is located behind the main door. It shows the primary exit (main gate) and secondary exit (kitchen back door). Please ensure keys for the back door are kept in the designated hook near the door. We've provided a fire extinguisher in the kitchen under the sink. Stay safe!"},
    {"doc_type": "safety", "title": "Dealing with Local Wildlife — Safety Tips",
     "content": "Q: What should I do if I see a snake or large insect?\nA: Our property is near nature, so occasional visits from local wildlife can happen. 1. Do NOT approach or try to catch any unfamiliar animals. 2. Close all doors and windows immediately. 3. Contact our caretaker or the local civil defence (APM) via the emergency list on the fridge. 4. We perform regular pest control, but a little caution goes a long way. Safety first!"},
])

# 2. Emergency Contacts & Community
DOCS.extend([
    {"doc_type": "safety", "title": "Local Police & Hospital Contacts",
     "content": "Q: Where are the nearest emergency services?\nA: 1. Police Station (Balai Polis): 5 min drive, Tel: 03-XXXX. 2. Nearest Hospital: 10 min drive (Kuala Lumpur Hospital). 3. Fire Station (Bomba): 8 min drive. A full list of these primary contacts is on the digital guest board and the fridge magnet. We are also available 24/7 for urgent assistance."},
])

# 3. Generating Bulk Variations for Safety & Support
for i in range(1, 41):
    hazard = random.choice(["slippery floor", "low ceiling", "steep stairs", "loose rug", "sharp corner"])
    location = random.choice(["Bathroom", "Attic", "Garden", "Kitchen", "Living Room"])
    DOCS.append({
        "doc_type": "safety",
        "title": f"Safety Advisory: {hazard} in {location}",
        "content": f"Q: I noticed a {hazard} in the {location}. Any advice?\nA: Thank you for pointing that out! We've placed warning signs or non-slip mats where possible. For the {hazard} in the {location}, we recommend extra caution, especially for children and the elderly. If you feel anything is unsafe, please let us know immediately so we can address it. Your safety is our concern!"
    })

for i in range(1, 40):
    item = random.choice(["First Aid Kit", "Flashlight", "Spare Key", "Umbrella", "Fire Blanket"])
    spot = random.choice(["Main Closet", "Kitchen Shelf", "TV Console", "Entryway", "Towel Rack"])
    DOCS.append({
        "doc_type": "safety",
        "title": f"Safety Amenity: Finding the {item}",
        "content": f"Q: Where do you keep the {item}?\nA: The {item} is located in the {spot}. We check these items regularly to ensure they are ready for use. Please let us know if you use anything from the {item} so we can restock it for the next guest. It's always better to be prepared!"
    })
