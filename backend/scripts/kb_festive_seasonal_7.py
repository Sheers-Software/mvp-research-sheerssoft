"""
Segment C — Malaysian Festive Seasonality Knowledge Base (Part 7)
Expanded: School Holiday 'Hidden' Long Weekends, State Holidays
~100 entries
"""

import random

DOCS = []

# 1. State Holidays & Local Events
DOCS.extend([
    {"doc_type": "school_holidays", "title": "State Holiday: Sultan of Selangor's Birthday",
     "content": "Q: Why are shops closed today? Is it a holiday?\nA: Yes! Today is the Sultan of Selangor's Birthday (Dec 11), a public holiday in Selangor. While most shopping malls remain open, government offices and some smaller Banks/Shops may be closed. It's a great day for festive celebrations in the state. Expect slightly heavier traffic in the Petaling Jaya and Shah Alam areas."},
    {"doc_type": "school_holidays", "title": "Federal Territory Day (Hari Wilayah)",
     "content": "Q: Is Feb 1st a holiday in KL?\nA: Yes, Feb 1st is Federal Territory Day, celebrating Kuala Lumpur, Putrajaya, and Labuan. It is a public holiday in these areas. Many families take the opportunity for a 'staycation' or a quick trip out of the city. We often have special promotions for the FT Day weekend—check our 'Deals' page!"},
])

# 2. Generating Bulk Variations for Holiday Timing
for i in range(1, 41):
    state = random.choice(["Selangor", "Johor", "Penang", "Perak", "Sabah", "Sarawak"])
    holiday = random.choice(["Sultan's Birthday", "State Foundation Day", "Harvest Festival", "Heritage Day"])
    DOCS.append({
        "doc_type": "school_holidays",
        "title": f"Regional Holiday: {holiday} in {state}",
        "content": f"Q: Is there a holiday in {state} today?\nA: Yes, it might be {holiday} in {state}. Malaysian holidays vary by state, and localized celebrations are very common. If you are traveling to or from {state}, please check the local holiday calendar as it can affect traffic and shop opening hours. We can help you check the specific dates for this year!"
    })

for i in range(1, 41):
    month = random.choice(["January", "April", "July", "October", "November"])
    reason = random.choice(["Exam Break", "School Event", "Sports Day", "Teacher's Training", "Special Leave"])
    DOCS.append({
        "doc_type": "school_holidays",
        "title": f"School Event Timing: {month} {reason}",
        "content": f"Q: Why is it so busy this weekend in {month}? Is there a {reason}?\nA: Large school-related events like {reason} can often cause localized peaks in hotel bookings. families often travel together for these events. In {month}, we specifically see a lot of activity around {reason}s. We recommend booking your dining and spa slots early to avoid disappointment during these mini-peaks."
    })
