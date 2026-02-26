"""
Segment A — Hotel & Resort Knowledge Base (Part 8)
Categories: Sports & Recreation, Health & Medical, Religious Services, Deep Dive Tech
~100 entries
"""

import random

DOCS = []

# 1. Sports & Recreation
SPORTS = ["Tennis", "Badminton", "Squash", "Archery", "Wall Climbing"]
for sport in SPORTS:
    DOCS.append({"doc_type": "activities", "title": f"{sport} Facility & Gear",
                 "content": f"Q: Do you have a {sport} court? Can I rent gear?\nA: Yes! Our {sport} centre is located near the North wing. Courts are open 8 AM–10 PM. Rental includes high-quality gear for RM30/hour. Lessons with a certified instructor are available for RM150/hour. Book your slot at the Sports Desk."})

# 2. Health & Medical
DOCS.extend([
    {"doc_type": "safety", "title": "On-site Clinic & Doctor",
     "content": "Q: Is there a doctor available on-site?\nA: We have a first-aid station with a registered nurse on-site 24/7. For medical consultations, we can arrange a house-call doctor within 30 minutes (RM250 call fee). The nearest full-service hospital is Gleneagles, approximately 20 minutes away by car. In emergencies, dial extension 77 for immediate assistance."},
    {"doc_type": "safety", "title": "Automated External Defibrillator (AED)",
     "content": "Q: Where are the AEDs located?\nA: For your safety, AEDs are located at the Front Desk, Poolside Bar, and Level 4 lobby. All our security and management staff are certified in CPR and AED usage. Every second counts in a cardiac emergency — don't hesitate to inform a staff member immediately if you see someone in distress."},
])

# 3. Religious-specific Services
DOCS.extend([
    {"doc_type": "faqs", "title": "Qibla Direction & Prayer Times",
     "content": "Q: How do I find the Qibla and prayer times?\nA: Qibla direction is marked with an arrow on the ceiling in every room. Current prayer times are displayed on the digital screen in the lobby and are also available via our in-house TV channel 1. Our Surau (on Level 1) is open 24 hours and provides prayer mats and telekung."},
    {"doc_type": "faqs", "title": "Kosher Meal Availability",
     "content": "Q: Can you provide Kosher meals?\nA: While we do not have a separate Kosher kitchen, we can provide pre-packaged Kosher certified meals with 48 hours' notice. These are heated and served in their original packaging. Alternatively, we can offer a wide selection of fresh fruits, raw vegetables, and whole fish prepared under strict guidance. Please contact our Dining Manager."},
])

# 4. Deep Dive Tech & Connectivity
for tech in ["Smart Mirror", "Voice Assistant", "NFC Entry", "High-Speed Streaming"]:
    DOCS.append({"doc_type": "facilities", "title": f"In-room Tech: {tech}",
                 "content": f"Q: How do I use the {tech} in my room?\nA: Every room is equipped with the latest {tech}. A digital guide is available on the bedside tablet explaining all functions. If you encounter any difficulty, our 'Tech Concierge' can assist you via WhatsApp or by visiting your room. We pride ourselves on being a tech-forward resort!"})

# 5. Expanding with more variations
for i in range(1, 41):
    location = random.choice(["Lobby", "Garden", "Beach", "Sky Bar", "Corridor"])
    facility = random.choice(["vending machine", "sculpture", "charging port", "water fountain", "restroom"])
    DOCS.append({
        "doc_type": "facilities",
        "title": f"Finding {facility} near {location}",
        "content": f"Q: Where is the nearest {facility}? I'm near {location}.\nA: The nearest {facility} is just around the corner from {location}. Look for the signs or ask any of our staff members wearing a 'Help me' badge. We've placed {facility}s conveniently throughout the resort to ensure your comfort."
    })

for i in range(1, 36):
    cuisine = random.choice(["Thai", "Japanese", "Lebanese", "Italian", "Fusion"])
    DOCS.append({
        "doc_type": "dining",
        "title": f"Specialty Cuisine Night: {cuisine}",
        "content": f"Q: Do you serve {cuisine} food?\nA: Yes! On selected nights (check the Weekly Dining Schedule), we host {cuisine} specialty dinners at Horizon Café. Our chefs create an authentic menu featuring {cuisine} classics. {cuisine} dinner is typically RM120/pax. Reservations are recommended as these nights are very popular!"
    })
