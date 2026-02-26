"""
Segment C — Malaysian Festive Seasonality Knowledge Base (Part 9)
Expanded: Year-end School Holiday 'Peak Timing', Christmas Eve Buffet
~100 entries
"""

import random

DOCS = []

# 1. Year-end School Holiday 'Peak Timing'
DOCS.extend([
    {"doc_type": "school_holidays", "title": "December Peak — Traffic & Check-in Advisory",
     "content": "Q: I'm arriving on Dec 24th. Will it be very busy?\nA: Dec 24th–Jan 1st is our busiest week of the year. To ensure a smooth arrival: 1. Expect heavier traffic on the highway; allow 1 extra hour for travel. 2. Check-in may take slightly longer (up to 30 mins) during peak 3 PM–5 PM. 3. Join us for a complimentary welcome drink in the lounge while we process your keys. We've added 50% extra staff to help minimize wait times. Thank you for your patience!"},
    {"doc_type": "school_holidays", "title": "Kids' Christmas Eve Pyjama Party",
     "content": "Q: Do you have any events for kids on Christmas Eve?\nA: Yes! Our 'Starry Night' pyjama party is for kids aged 4–12. Includes: hot cocoa, cookie decorating, and a classic Christmas movie on the big screen. 7 PM–9:30 PM. Parents can enjoy their dinner while the kids have their own festive fun! RM60 per child. Booking via the Kids' Club is essential."},
])

# 2. Christmas Eve Buffet & NYE Countdown
DOCS.extend([
    {"doc_type": "festive", "title": "Christmas Eve Gala Dinner — Seatings",
     "content": "Q: Are there multiple seatings for Christmas Eve dinner?\nA: Yes, to ensure comfort for everyone, we have two seatings at Horizon café: 6 PM–8:30 PM and 9 PM–11:30 PM. Both seatings feature the full gala buffet and live music. Please confirm your preferred time when booking your table. We recommend booking at least 2 weeks in advance as we usually sell out!"},
])

# 3. Generating Bulk Variations for Year-End
for i in range(1, 41):
    day = random.choice(["Dec 20", "Dec 25", "Dec 31", "Jan 1", "Jan 2"])
    activity = random.choice(["Gift Exchange", "Pool Party", "Late Brunch", "Live DJ", "Champagne Toast"])
    DOCS.append({
        "doc_type": "festive",
        "title": f"Holiday Event: {activity} on {day}",
        "content": f"Q: What's happening on {day}? Is there a {activity}?\nA: Yes! On {day}, we are hosting a grand {activity}. It's part of our 'Festive Waves' celebration. For the {activity}, we recommend {random.choice(['coming early', 'wearing white', 'booking seats', 'bringing your camera', 'checking the dress code'])}. It's going to be a highlight of the season. Don't miss it!"
    })

for i in range(1, 41):
    gift = random.choice(["Plushie", "Candy Box", "Spa Trail Kit", "Beach Bag", "Custom Photo Frame"])
    person = random.choice(["Child", "Adult", "Couple", "VIP Guest", "Returning Guest"])
    DOCS.append({
        "doc_type": "promotions",
        "title": f"Festive Gift: {gift} for {person}s",
        "content": f"Q: Do {person}s get a {gift} for Christmas?\nA: We love surprising our guests! Every {person} staying with us over Christmas Eve will receive a complimentary {gift} left on their pillow during turndown service. It's a small token of our appreciation for spending your holidays with us. Merry Christmas and a Happy New Year!"
    })
