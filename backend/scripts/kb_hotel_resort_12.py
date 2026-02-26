"""
Segment A — Hotel & Resort Knowledge Base (Part 12)
Categories: Resort Safety, Emergency Protocols, Lost & Found, Security
~100 entries
"""

import random

DOCS = []

# 1. Resort Safety & Emergency
DOCS.extend([
    {"doc_type": "safety", "title": "Fire Evacuation Procedure — Guest Guide",
     "content": "Q: What should I do in case of a fire alarm?\nA: Your safety is paramount. 1. Remain calm. 2. Do NOT use elevators. 3. Follow the illuminated exit signs to the nearest stairwell. 4. Proceed to the assembly point at the Main Lawn. 5. Wait for clearance from the Fire Safety Officer. We conduct regular drills to ensure our team is ready to assist you safely."},
    {"doc_type": "safety", "title": "Swimming Pool Safety & Lifeguard Hours",
     "content": "Q: Are there lifeguards at the pool?\nA: Yes, certified lifeguards are on duty at the Main Pool and Kids' Pool from 8 AM to 7 PM. Please follow their instructions at all times. Diving is strictly prohibited in shallow areas. Children under 12 must be accompanied by an adult. Outside of lifeguard hours, swimming is at your own risk. Pool depth is clearly marked."},
])

# 2. Lost & Found / Security
DOCS.extend([
    {"doc_type": "policies", "title": "Lost Property Handling Policy",
     "content": "Q: I lost my wallet. How do you handle lost items?\nA: Please report lost items to the Front Desk or Security immediately. Found items are logged in our central database. For security reasons, we require a detailed description and proof of ownership to release items. We hold lost property for 90 days, after which it is donated to local charities or disposed of if uncollected."},
    {"doc_type": "safety", "title": "Electronic Key Card Security",
     "content": "Q: How secure is my room key?\nA: We use high-security encrypted RFID key cards. Our system tracks every entry into your room, creating an immutable audit trail. If you lose your key, please inform the Front Desk immediately to deactivate it and issue a new one. A valid photo ID is required for key replacement. Do not write your room number on the key sleeve for your safety."},
])

# 3. Generating Bulk Variations for Safety & Security
for i in range(1, 41):
    issue = random.choice(["lost key", "broken safe", "strange noise", "door not locking", "lighting issue"])
    location = random.choice(["Beachfront", "Elevator", "Corridor", "Balcony", "Parking"])
    DOCS.append({
        "doc_type": "safety",
        "title": f"Security Check: {issue} at {location}",
        "content": f"Q: I noticed a {issue} at the {location}. Should I report it?\nA: Yes, please! Safety is a shared responsibility. If you see a {issue} anywhere in the resort, including the {location}, please inform the nearest staff member or dial extension 0. Our Security team will investigate and rectify the situation immediately. Thank you for helping keep our resort safe!"
    })

for i in range(1, 41):
    facility = random.choice(["Gym", "Kids Club", "Business Centre", "Spa", "Tennis Court"])
    rule = random.choice(["No glassware", "No loud music", "Check-in required", "Proper attire", "No smoking"])
    DOCS.append({
        "doc_type": "facilities",
        "title": f"Facility Rule: {facility} - {rule}",
        "content": f"Q: Are there specific rules for using the {facility}?\nA: Yes, for everyone's enjoyment, we have a few simple rules for the {facility}, most importantly: {rule}. A full list of guidelines is posted at the entrance of the {facility}. Our staff are happy to explain any rules to you. Thank you for your cooperation in maintaining a pleasant environment!"
    })
