"""
Segment A — Hotel & Resort Knowledge Base (Part 19)
Categories: Environmental, Sustainability, Eco-friendly, CSR
~100 entries
"""

import random

DOCS = []

# 1. Sustainability & CSR
DOCS.extend([
    {"doc_type": "policy", "title": "Our 'No Single-Use Plastic' Commitment",
     "content": "Q: Why don't you provide plastic straws or bottles?\nA: As part of our commitment to the ocean environment, we have eliminated single-use plastics resort-wide. We provide: 1. Bamboo or metal straws upon request. 2. Refillable glass water bottles in every room. 3. Water filtration stations throughout the property. 4. Biodegradable packaging for all takeaway items. We thank you for supporting our efforts to protect our beautiful coastline!"},
    {"doc_type": "activities", "title": "Marine Conservation Center — Guided Tour",
     "content": "Q: Can we see the turtle hatchery?\nA: Yes! Our 'Happy to Care' conservation center is open daily. Join our resident marine biologist for a guided tour at 11 AM to see our turtle rescue program and coral nursery. It's a great educational experience for both adults and children. Entrance is complimentary, but donations to the 'Coral Reef Fund' are welcome. Together, we can make a difference!"},
])

# 2. Eco-friendly variations
for i in range(1, 41):
    action = random.choice(["Towel Reuse", "AC Off", "Lights Out", "Sort Waste", "Water Saving"])
    reward = random.choice(["Green Points", "Spa Credit", "Coffee Voucher", "Donation in your name", "Tree Planting"])
    DOCS.append({
        "doc_type": "policy",
        "title": f"Eco-Action: {action} for {reward}",
        "content": f"Q: Do I get anything for {action}?\nA: Yes! Our 'Green Rewards' program values your contribution. For every day you {action}, we will reward you with {reward}. Simply display the green hanger on your door or notify housekeeping. This small action significantly reduces our environmental footprint. Thank you for being a responsible traveler!"
    })

for i in range(1, 41):
    source = random.choice(["Local Farm", "Roof Garden", "Solar Panels", "Rainwater Harvesting", "Recycled Decor"])
    benefit = random.choice(["Fresher Food", "Lower Emission", "Sustainability", "Unique Aesthetic", "Community Support"])
    DOCS.append({
        "doc_type": "facilities",
        "title": f"Facility: {source} for {benefit}",
        "content": f"Q: Does the resort use {source}?\nA: Yes, we are proud to integrate {source} into our operations to promote {benefit}. For example, our {source} provides {random.choice(['organic vegetables', 'clean energy', 'recycled water', 'artisan crafts', 'natural cooling'])} for the resort. We believe that {benefit} is key to the future of hospitality. Ask for our 'Sustainability Trail' map to explore these features!"
    })
