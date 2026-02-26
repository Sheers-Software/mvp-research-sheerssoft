"""
Segment A — Hotel & Resort Knowledge Base (Part 10)
Categories: Spa & Wellness Deep Dive, Local Area Tours, Photography Services
~100 entries
"""

import random

DOCS = []

# 1. Spa & Wellness Deep Dive
DOCS.extend([
    {"doc_type": "spa", "title": "Traditional Malay Massage (Urut Melayu)",
     "content": "Q: What is a Malay Urut? How is it different from Thai massage?\nA: Our signature Malay Urut is a deep-tissue oil massage focusing on 'urat' (nerves) and blood flow. Unlike Thai massage which involves a lot of stretching and compressions, Malay Urut uses long, firm strokes and specialised herbal oils to relieve fatigue and muscle knots. It's deeply grounding and restorative. Recommended for post-travel recovery!"},
    {"doc_type": "spa", "title": "Post-Natal Spa Package",
     "content": "Q: Do you offer spa treatments for new mothers?\nA: Yes, our 'New Bloom' post-natal package is designed for mothers at least 6 weeks post-delivery. Includes: herbal body wrap, gentle massage to restore energy, and a warming ginger tea ritual. We focus on areas like the lower back and shoulders. Please consult your doctor before booking."},
])

# 2. Local Area Tours & Photography
DOCS.extend([
    {"doc_type": "activities", "title": "Sunrise Beach Photography Session",
     "content": "Q: Can we book a professional photographer for a family shoot?\nA: Yes! Our 'Sunlight Memories' package includes a 60-minute session with our in-house photographer at either sunrise or sunset. You'll receive 20 high-resolution edited digital images within 48 hours. RM350 per session. A beautiful way to capture your holiday forever!"},
    {"doc_type": "local_area", "title": "Hidden Gem Tour: Night Market Food Crawl",
     "content": "Q: Are there any local food tours?\nA: Our 'Pasar Malam Crawl' takes you to the most authentic local night markets. Led by our resident foodie staff, you'll sample local specialties like Satay, Apam Balik, and Murtabak. Every Tuesday and Thursday, 7 PM–9 PM. RM60 per person includes transportation and food samples. Limit 8 pax per tour for an intimate experience!"},
])

# 3. Generating Bulk Variations for Tour & Spa
for i in range(1, 41):
    tour = random.choice(["Mangrove Kayaking", "Jungle Trekking", "Paddy Field Bike Tour", "Island Hopping", "Cultural Village Visit"])
    focus = random.choice(["Wildlife spotting", "Photography", "Historical context", "Local legend", "Culinary stop"])
    DOCS.append({
        "doc_type": "activities",
        "title": f"Tour Specialty: {tour} - {focus}",
        "content": f"Q: What is the main focus of the {tour}?\nA: The {tour} focuses heavily on {focus}. Our guides are experts in the area and will provide in-depth {focus} throughout the journey. It's an immersive experience that goes beyond the typical tourist path. Highly recommended for adventure seekers!"
    })

for i in range(1, 46):
    oil = random.choice(["Lemongrass", "Frangipani", "Sandalwood", "Peppermint", "Eucalyptus"])
    benefit = random.choice(["Relaxation", "Detox", "Invigoration", "Muscle relief", "Skin glow"])
    DOCS.append({
        "doc_type": "spa",
        "title": f"Aromatherapy Benefit: {oil} Oil",
        "content": f"Q: What are the benefits of the {oil} oil used in the spa?\nA: {oil} oil is primarily used for {benefit}. When combined with our expert massage techniques, it helps to enhance the overall experience and leave you feeling balanced and refreshed. You can choose your preferred oil during your pre-treatment consultation."
    })
DOCS.append({"doc_type": "spa", "title": "Couple's Spa Retreat", "content": "Q: Can we Have a spa treatment together?\nA: Yes, we have 4 luxurious double treatment rooms specifically for couples. Share the experience of relaxation side-by-side with our 'Togetherness' package, which includes a private floral bath and champagne after the treatment."})
