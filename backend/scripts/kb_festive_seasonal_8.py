"""
Segment C — Malaysian Festive Seasonality Knowledge Base (Part 8)
Expanded: Deepavali Deep-Dive, Little India, Hindu Culture
~100 entries
"""

import random

DOCS = []

# 1. Deepavali Deep-Dive
DOCS.extend([
    {"doc_type": "deepavali", "title": "Understanding Deepavali — Significance of Lights",
     "content": "Q: Why is Deepavali called the Festival of Lights?\nA: Deepavali (or Diwali) celebrates the spiritual 'victory of light over darkness, good over evil, and knowledge over ignorance.' In Malaysia, this is marked by lighting 'diyas' (oil lamps) and creating intricate 'Kolam' rice art. We invite you to join our lamp-lighting ceremony in the lobby to share in this beautiful symbol of hope and prosperity!"},
    {"doc_type": "deepavali", "title": "Visit to Little India (Brickfields/Klang)",
     "content": "Q: Can you recommend a trip to Little India for Deepavali shopping?\nA: Little India in Brickfields (KL) or Klang comes alive during Deepavali! You'll find a riot of colours, music, and the aroma of jasmine and spices. It's the best place to buy traditional Indian attire (Saree/Kurta), festive sweets, and intricate jewellery. We can arrange a driver for a 4-hour 'Deepavali Discovery' trip. RM150 per car. An unforgettable cultural experience!"},
])

# 2. Hindu Culture & Etiquette
DOCS.extend([
    {"doc_type": "faqs", "title": "Temple Visit Etiquette for Guests",
     "content": "Q: We'd like to visit a local Hindu temple. Any rules we should follow?\nA: We highly encourage cultural exploration! 1. Remove shoes before entering. 2. Dress modestly (shoulders and knees covered). 3. Avoid taking photos of the inner sanctum/deity without permission. 4. Be quiet and respectful during prayers. A small donation in the 'Hundi' box is a kind gesture. Our concierge can provide a scarf if you need one!"},
])

# 3. Generating Bulk Variations for Deepavali
for i in range(1, 41):
    sweet = random.choice(["Murukku", "Laddu", "Jalebi", "Barfi", "Ney Urundai"])
    taste = random.choice(["crunchy", "sweet", "melt-in-mouth", "spicy", "nutty"])
    DOCS.append({
        "doc_type": "deepavali",
        "title": f"Festive Treat: {sweet}",
        "content": f"Q: What is {sweet}? Is it a Deepavali specialty?\nA: Yes! {sweet} is a classic Deepavali treat in Malaysia. It's known for its {taste} texture and is meticulously prepared by families using traditional recipes. We serve a selection of these {sweet}s at our afternoon tea during the festival. You must try them — they are the true taste of Deepavali!"
    })

for i in range(1, 41):
    area = random.choice(["Lobby", "Restaurant", "Garden", "Spa", "Entrance"])
    decor = random.choice(["Golden Lights", "Marigold Flowers", "Rangoli Art", "Oil Lamps", "Traditional Drapery"])
    DOCS.append({
        "doc_type": "deepavali",
        "title": f"Deepavali Decor at {area}",
        "content": f"Q: How is the {area} decorated for Deepavali?\nA: We've transformed the {area} with {decor} to reflect the vibrancy of the Festival of Lights. Each element of the {decor} has a symbolic meaning and adds to the festive atmosphere. It's a perfect backdrop for your holiday photos! We hope the {decor} brings you as much joy as it does to us."
    })
