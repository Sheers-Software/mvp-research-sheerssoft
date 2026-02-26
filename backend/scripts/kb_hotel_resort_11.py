"""
Segment A — Hotel & Resort Knowledge Base (Part 11)
Categories: Food Allergies, Dietary Requirements, Fine Dining Protocols
~100 entries
"""

import random

DOCS = []

# 1. Food Allergies & Dietary Requirements
ALLERGENS = ["Peanuts", "Shellfish", "Gluten", "Dairy", "Soy", "Eggs"]
for allergen in ALLERGENS:
    DOCS.append({
        "doc_type": "dining",
        "title": f"Allergy Management: {allergen}",
        "content": f"Q: Do you have a protocol for {allergen} allergies?\nA: Yes, we take food allergies extremely seriously. Our kitchen has a designated 'Allergy Action Plan'. When you dine at any of our outlets, please inform your server immediately. The Head Chef will personally oversee the preparation of your meal in a sterilized area to prevent cross-contamination. We have {allergen}-free options clearly marked on all menus."
    })

# 2. Fine Dining Protocols
DOCS.extend([
    {"doc_type": "dining", "title": "Horizon Prime — Dress Code & Etiquette",
     "content": "Q: What is the dress code for the fine dining restaurant?\nA: Horizon Prime maintains a 'Smart Elegant' dress code. We kindly ask gentlemen to wear collared shirts and closed shoes. For ladies, elegant attire is appreciated. Please avoid beachwear, flip-flops, or athletic gear. This ensures a sophisticated atmosphere for all our guests celebrating special occasions."},
    {"doc_type": "dining", "title": "Wine Cellar — Private Tasting sessions",
     "content": "Q: Can we book a private wine tasting?\nA: Yes, our Sommelier hosts private tasting sessions in the 'Cellar Room' for groups of 2–6. You'll explore a curated selection of old and new world wines paired with gourmet cheeses. RM250 per person. Reservations at least 24 hours in advance are required. A perfect pre-dinner experience!"},
])

# 3. Generating Bulk Variations for Dining
for i in range(1, 41):
    diet = random.choice(["Vegan", "Vegetarian", "Keto", "Paleo", "Low-Sodium"])
    dish = random.choice(["Salad", "Steak", "Pasta", "Soup", "Curry"])
    DOCS.append({
        "doc_type": "dining",
        "title": f"Dietary Option: {diet} {dish}",
        "content": f"Q: Do you have a {diet} version of your {dish}?\nA: Yes! Our culinary team has developed a range of {diet} dishes, including a delicious {diet} {dish}. We use fresh, locally sourced ingredients to ensure the highest quality even for specialized diets. Please check our 'Wellness Menu' for all {diet} options."
    })

for i in range(1, 41):
    item = random.choice(["Table reservation", "Private room", "Chef's table", "Birthday decor", "Window seat"])
    outlet = random.choice(["Horizon Café", "Beach Grill", "Sky Lounge", "Pool Bar", "Main Dining Hall"])
    DOCS.append({
        "doc_type": "dining",
        "title": f"Dining Request: {item} at {outlet}",
        "content": f"Q: Can I request a {item} at {outlet}?\nA: We would be happy to accommodate your request for a {item} at {outlet}, subject to availability. Please specify the date and time, and we will do our best to secure the perfect spot for you. For {item}, we recommend booking at least 48 hours in advance."
    })
