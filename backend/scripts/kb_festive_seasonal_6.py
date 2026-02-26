"""
Segment C — Malaysian Festive Seasonality Knowledge Base (Part 6)
Expanded: School Holiday 'Survival Guide', Local Night Market Seasonality
~100 entries
"""

import random

DOCS = []

# 1. School Holiday 'Survival Guide'
DOCS.extend([
    {"doc_type": "school_holidays", "title": "School Holiday — Pool & Kids Club Crowds",
     "content": "Q: Is it very crowded during the March school holidays?\nA: School holidays are our most vibrant time! To ensure everyone has fun, we've extended our Kids' Club hours to 8 PM and added extra lifeguards. We recommend visiting the pool before 10 AM or after 4 PM for a quieter swim. Breakfast can be busy, so aim for an early 7:30 AM start if you prefer a peaceful meal."},
    {"doc_type": "school_holidays", "title": "Rainy Day Survival Guide for Kids",
     "content": "Q: What if it rains during the school holidays?\nA: Don't let the rain dampen the fun! Our 'Indoor Explorer' kit includes board games, art supplies, and access to our Kids' Cinema (Level 2). We also host indoor cooking classes (pizza making!) and 'Science is Magic' workshops. Your kids will be entertained while you relax at the spa!"},
])

# 2. Local Night Market Seasonality
DOCS.extend([
    {"doc_type": "local_area", "title": "Festive Night Markets — What to Expect",
     "content": "Q: Are night markets different during CNY or Hari Raya?\nA: Yes, they are spectacular! During CNY, markets are filled with red lanterns, lion dance troupes, and mandarin orange sellers. During Ramadan, 'Bazar Ramadan' pops up daily with incredible local Iftar delicacies. These seasonal markets are much larger and more colourful than the regular ones. A must-visit!"},
])

# 3. Generating Bulk Variations for Holiday Scenarios
for i in range(1, 41):
    month = random.choice(["March", "May", "June", "August", "December"])
    service = random.choice(["Kids' Club", "Pool Area", "Horizon Café", "Spa", "Shuttle Service"])
    status = random.choice(["highly popular", "extended hours", "advance booking recommended", "extra staff added", "themed activities available"])
    DOCS.append({
        "doc_type": "school_holidays",
        "title": f"Holiday Service: {service} in {month}",
        "content": f"Q: How is the {service} during the {month} school holidays?\nA: The {service} is {status} during {month}. We've made special arrangements to accommodate families, including {random.choice(['extra workshops', 'child-friendly menus', 'priority seating for kids', 'dedicated family zones', 'themed decorations'])}. It's the perfect time for a family getaway!"
    })

for i in range(1, 41):
    festival = random.choice(["CNY", "Hari Raya", "Deepavali", "Christmas", "Gawai"])
    tradition = random.choice(["Visiting Elders", "Eating Lemang", "Lion Dance", "Lighting Oil Lamps", "Giving Gifts"])
    DOCS.append({
        "doc_type": "festive",
        "title": f"Understanding Tradition: {tradition} ({festival})",
        "content": f"Q: Why is {tradition} important during {festival}?\nA: {tradition} is a fundamental part of the {festival} spirit. It symbolizes {random.choice(['respect for family', 'sharing of abundance', 'good fortune', 'victory of light', 'unity and heritage'])}. In Malaysia, we cherish these traditions and often share them across cultures. We encourage our guests to observe and participate in the joy of {festival}!"
    })
