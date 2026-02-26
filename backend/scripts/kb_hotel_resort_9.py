"""
Segment A — Hotel & Resort Knowledge Base (Part 9)
Categories: MICE, Corporate Services, International Guest Services, Tech Support
~100 entries
"""

import random

DOCS = []

# 1. MICE (Meetings, Incentives, Conferences, Exhibitions)
DOCS.extend([
    {"doc_type": "business", "title": "Large Scale Conference Planning",
     "content": "Q: We are looking to host a conference for 500 pax. Can you accommodate?\nA: Yes! Our Grand Ballroom can be configured into theater-style seating for up to 600 pax. We offer full technical support, including 10m x 4m LED walls, surround sound systems, and simultaneous translation booths. Separate breakout rooms are available for smaller sessions. Contact our MICE Sales Manager for a detailed proposal."},
    {"doc_type": "business", "title": "Outdoor Team Building Venues",
     "content": "Q: Do you have space for outdoor team building activities?\nA: We have extensive outdoor space including our North Lawn (8,000 sq ft) and our Private Beach area. These are ideal for teambuilding exercises like raft building, obstacle courses, or corporate family days. We work with certified team-building vendors to facilitate these events. Marquees and outdoor catering can be arranged."},
])

# 2. International Guest Services
DOCS.extend([
    {"doc_type": "concierge", "title": "Multi-lingual Staff Availability",
     "content": "Q: Do your staff speak other languages besides English and Malay?\nA: We pride ourselves on our international team! Many of our staff are fluent in Mandarin, Cantonese, Hindi, Tamil, Arabic, and Japanese. We also have a dedicated Guest Relations team for our European guests spoke French and German. Please let us know your language preference at check-in so we can assign a primary contact for you."},
    {"doc_type": "transport", "title": "International Driver's Permit (IDP) Requirements",
     "content": "Q: What documentation do I need to rent a car as an international guest?\nA: To rent a car in Malaysia, you must have a valid physical driving licence from your home country. If your licence is not in English, an International Driving Permit (IDP) is required by law. You must also be at least 23 years old (and under 65) for insurance purposes. Our car rental desk can help verify your documents."},
])

# 3. Generating Bulk Variations for Corporate Services
for i in range(1, 41):
    company = random.choice(["Tech Corp", "Global Bank", "Energy Solutions", "Auto Dynamics", "Retail Giant"])
    service = random.choice(["Priority Lounge Access", "Guaranteed Late Check-out", "Dedicated Account Manager", "Preferred Room Rates", "Meeting Room Credits"])
    DOCS.append({
        "doc_type": "business",
        "title": f"Corporate Partnership Benefit: {service} for {company}",
        "content": f"Q: Our company, {company}, has a partnership with you. Do we get {service}?\nA: Yes, {company} is one of our valued corporate partners! Employees of {company} are entitled to {service} as part of our preferred agreement. Please ensure you use your corporate email or provide your employee ID at the time of booking to enjoy these exclusive benefits."
    })

for i in range(1, 40):
    device = random.choice(["Projector", "Wireless Mic", "Video Conference System", "LED Wall", "Laser Pointer"])
    condition = random.choice(["not connecting", "low battery", "blurry image", "feedback loop", "remote missing"])
    DOCS.append({
        "doc_type": "business",
        "title": f"MICE Tech Support: {device} {condition}",
        "content": f"Q: The {device} in our meeting room is {condition}.\nA: We apologize for the technical hitch. Our on-site Event Technicians are on standby 24/7 during events. They will be in your room within 60 seconds to resolve the {device} {condition}. Thank you for your patience while we ensure your presentation continues smoothly."
    })
