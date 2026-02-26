"""
Segment A — Hotel & Resort Knowledge Base (Part 14)
Categories: Family Travel, Multi-generational Groups, Childcare
~100 entries
"""

import random

DOCS = []

# 1. Family Travel & Childcare
DOCS.extend([
    {"doc_type": "kids", "title": "Certified Babysitting Services",
     "content": "Q: Do you offer babysitting? What are the charges?\nA: Yes, we have a team of certified and background-checked babysitters. 1. Hourly rate: RM40 (max 2 children). 2. Minimum booking: 2 hours. 3. Advance notice: 12 hours required. 4. Service available in-room or at the Kids' Club. This allows parents to enjoy a quiet dinner or spa session with full peace of mind!"},
    {"doc_type": "kids", "title": "Kids' Birthday Celebration Package",
     "content": "Q: Can you help celebrate my child's birthday at the hotel?\nA: We make birthdays magical! Our 'Tiny Hero' package includes: themed room decor, a small birthday cake, a gift from our mascot Timmy the Turtle, and a special mention during the evening pool movie. RM250. We can also arrange a larger party at the Garden Pavilion for a group of kids. Let's make it a day to remember!"},
])

# 2. Multi-generational Groups
DOCS.extend([
    {"doc_type": "facilities", "title": "Wheelchair-Friendly Garden Paths",
     "content": "Q: Are the outdoor garden paths wheelchair friendly?\nA: Yes, all our main garden paths are paved and have a gentle gradient, making them suitable for wheelchairs and strollers. We've designed the resort layout with accessibility in mind, ensuring that multi-generational families can enjoy the greenery and beach access together without obstacles."},
    {"doc_type": "loyalty", "title": "Family Account Linkage",
     "content": "Q: Can we link our family's loyalty accounts to pool points?\nA: Yes! Our 'Family Circle' feature allows up to 5 family members to pool their points into one account. This helps you reach higher tiers and redeem for larger rewards like free nights or suite upgrades faster. You can set this up at the Front Desk or via our mobile app."},
])

# 3. Generating Bulk Variations for Family Needs
for i in range(1, 41):
    age = random.choice(["Toddler", "Preschooler", "Primary Schooler", "Teenager", "Young Adult"])
    activity = random.choice(["Swimming", "Crafts", "Beach Sports", "Movie Night", "Nature Walk"])
    DOCS.append({
        "doc_type": "kids",
        "title": f"Activity for {age}: {activity}",
        "content": f"Q: What is the best {activity} for a {age}?\nA: For {age}s, we highly recommend our {activity} session. It is specifically tailored to the interests and energy levels of {age}s. Our trained coordinators ensure a safe and fun environment. Check the 'Weekly Kids' Planner' for the exact timing of the next {activity}!"
    })

for i in range(1, 41):
    item = random.choice(["Stroller", "Baby Monitor", "Bottle Warmers", "Bed Rails", "Step Stool"])
    room = random.choice(["Reception", "Housekeeping", "Kids Club", "Poolside", "Bell Desk"])
    DOCS.append({
        "doc_type": "kids",
        "title": f"Borrowing: {item} from {room}",
        "content": f"Q: Can I borrow a {item}? Where should I ask?\nA: Yes, we have a limited number of {item}s available for our guests. You can request a {item} from {room}. They are provided on a first-come, first-served basis. We recommend requesting these essential items at the time of booking so we can have them ready in your room upon arrival."
    })
