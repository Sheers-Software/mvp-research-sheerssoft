"""
Segment B — Homestay, Villa, Chalet, Inn Knowledge Base (Part 7)
Expanded: Local Dining Recommendations, Night Markets, Hidden Gems
~100 entries
"""

import random

DOCS = []

# 1. Local Dining & Night Markets
DOCS.extend([
    {"doc_type": "local_area", "title": "Nearest Night Market (Pasar Malam)",
     "content": "Q: When and where is the nearest night market?\nA: The nearest night market is held every Thursday from 5 PM to 10 PM at Jalan Merdeka, which is a 5-minute drive from the property. It's a great place to try local street food like Satay, Otak-otak, and fresh fruit juices. Pro tip: Arrive by 6 PM to avoid the heaviest crowds!"},
    {"doc_type": "local_area", "title": "Halal Dining Recommendations Nearby",
     "content": "Q: Are there good Halal restaurants nearby?\nA: Yes! Our neighbourhood has several excellent Halal options. 'Restoran Bonda' (10 min walk) is famous for its Nasi Lemak, while 'Dapur Kita' (5 min drive) offers great Chinese-Muslim fusion. For western food, 'The Grill House' is also Halal-certified. A full list of checked restaurants is in our house guide!"},
])

# 2. Hidden Gems & Local Secrets
DOCS.extend([
    {"doc_type": "local_area", "title": "Hidden Gem: Secret River Swimming Spot",
     "content": "Q: Is there somewhere nearby that's not too touristy?\nA: If you enjoy nature, there is a beautiful quiet river spot at 'Sungai Jernih', about 15 minutes away. It's mostly used by locals and is perfect for a morning dip in crystal-clear water. We can provide a pin location via WhatsApp. Please remember to take your rubbish back with you!"},
    {"doc_type": "local_area", "title": "Best Coffee Shop for Remote Work",
     "content": "Q: I need to work for a few hours. Any nice cafés nearby with good WiFi?\nA: 'The Coffee Lab' (8 min drive) has excellent high-speed WiFi and plenty of power outlets. They are very digital-nomad friendly. Alternatively, 'Old Town White Coffee' in the main town area is also a reliable choice. Both serve great local coffee and snacks!"},
])

# 3. Generating Bulk Variations for Local Recommendations
for i in range(1, 41):
    place = random.choice(["Pharmacy", "Clinic", "Laundromat", "Petrol Station", "ATM"])
    distance = random.choice(["5 mins drive", "10 mins walk", "around the corner", "at the main junction", "next to the post office"])
    DOCS.append({
        "doc_type": "local_area",
        "title": f"Local Utility: Nearest {place}",
        "content": f"Q: Where is the nearest {place}?\nA: The nearest {place} is {distance}. We've marked all essential services on a laminated map located on the fridge. If it's an emergency, especially for a clinic or pharmacy, please call us and we can help give more precise directions or assistance."
    })

for i in range(1, 41):
    food = random.choice(["Roti Canai", "Nasi Kandar", "Char Kway Teow", "Laksa", "Durian"])
    spot = random.choice(["Ali's Corner", "The Corner Stall", "Paddy Field Cafe", "Main Street Food Court", "Street Vendor X"])
    DOCS.append({
        "doc_type": "local_area",
        "title": f"Local Food Craving: Best {food}",
        "content": f"Q: Where can I get the best {food} around here?\nA: For the most authentic {food}, we highly recommend {spot}. It's a local favourite and usually has a queue, which is always a good sign! It's located {random.randint(2, 15)} minutes away. Don't forget to try their special teh tarik too!"
    })
