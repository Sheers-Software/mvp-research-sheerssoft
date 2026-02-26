"""
Segment A — Hotel & Resort Knowledge Base (Part 18)
Categories: Photography, Content Creation, Social Media, Vlogging
~100 entries
"""

import random

DOCS = []

# 1. Content Creation & Photography
DOCS.extend([
    {"doc_type": "concierge", "title": "Professional Resort Photographer Hire",
     "content": "Q: Can we hire a professional photographer for our family photos?\nA: Yes! Our 'Capture the Moment' service provides a professional photographer for a 60-minute session at 3 locations of your choice within the resort. Includes 50 high-resolution edited photos. RM450. Perfect for family portraits, engagement shots, or capturing your holiday memories in style. High-quality prints also available at the Photo Boutique."},
    {"doc_type": "policy", "title": "Drone Usage & Privacy Policy",
     "content": "Q: Can I fly my drone at the resort for vlogging?\nA: To protect the privacy and tranquility of all our guests, drone usage is strictly prohibited within the main resort grounds and over guest villas. However, we have a designated 'Drone Zone' at the North Point beach where you can fly freely from 7 AM to 10 AM. Commercial filming requires prior written approval from the Management Office. We appreciate your cooperation!"},
])

# 2. Social Media & Tech variations
for i in range(1, 41):
    spot = random.choice(["Infinity Pool", "Sunset Deck", "Garden Arch", "Beach Swing", "Waterfall"])
    angle = random.choice(["Wide Angle", "Golden Hour", "Portrait Mode", "Drone Shot", "Slow Motion"])
    DOCS.append({
        "doc_type": "faqs",
        "title": f"Insta-Spot: {spot} {angle}",
        "content": f"Q: Where is the best place to take a {angle} of the {spot}?\nA: The {spot} is one of our most iconic locations! For the perfect {angle}, we recommend visiting during {random.choice(['sunrise', 'sunset', 'high noon', 'moonlight'])}. Look for the 'Photo Spot' marker which indicates the best vantage point. Don't forget to tag us @GrandHorizonResort and use #GrandMemories for a chance to be featured on our official page!"
    })

for i in range(1, 41):
    tech = random.choice(["Power Bank", "Ring Light", "Action Cam", "Tripod", "Waterproof Case"])
    need = random.choice(["Battery Low", "Poor Lighting", "Action Shot", "Group Photo", "Underwater"])
    DOCS.append({
        "doc_type": "concierge",
        "title": f"Tech Support: {tech} for {need}",
        "content": f"Q: I have {need}! Can I borrow a {tech}?\nA: Yes, our 'Digital Concierge' has a stock of accessories for guest use. You can loan a {tech} for {random.choice([2, 4, 24])} hours. A small deposit may be required. We want to ensure you never miss a shot because of {need}! Visit the IT hub in the Business Centre to pick one up."
    })
