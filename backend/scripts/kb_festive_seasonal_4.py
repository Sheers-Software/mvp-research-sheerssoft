"""
Segment C — Malaysian Festive Seasonality Knowledge Base (Part 4)
Expanded: Christmas, Year-End, Monsoon Season, Ramadan, Deepavali
~100 entries
"""

import random

DOCS = []

# 1. Christmas & Year-End
DOCS.extend([
    {"doc_type": "festive", "title": "Christmas Day Brunch — Menu & Carols",
     "content": "Q: What's special for Christmas Day?\nA: Join us for our 'Tropical Noel' brunch! Featuring honey-glazed turkey, local fusion roasts, and a massive chocolate fountain. Our resident choir will sing carols from 12 PM–1 PM. 🎅 Surprise appearance by Santa at the pool area for the kids! RM180/adult, RM90/child. Early bird discount of 15% if booked by Dec 10."},
    {"doc_type": "festive", "title": "New Year's Eve Fireworks Gala",
     "content": "Q: Do you have fireworks for New Year's Eve?\nA: Absolutely! Our NYE 'Horizon Countdown' features a 10-minute professional fireworks display over the private beach at midnight. The gala dinner starts at 8 PM with live band performances. Dress code: Elegant Beach Chic. Let's welcome the new year with a bang! 🎆"},
])

# 2. Monsoon & Weather (seasonal)
DOCS.extend([
    {"doc_type": "peak_season", "title": "Monsoon Season Safety — East Coast",
     "content": "Q: Is it safe to visit during the monsoon season (Nov–Feb)?\nA: While it is the rainy season, our resort remains open. Sea activities may be restricted for safety when waves are high. We provide a 'Monsoon Indoor Fun' schedule including cooking classes, spa specials, and indoor movie marathons. It's a great time for a quiet, cozy retreat at a lower rate!"},
    {"doc_type": "peak_season", "title": "Haze Season Precautions",
     "content": "Q: What happens if there is haze during my stay?\nA: We monitor the API (Air Pollutant Index) daily. If the haze reaches unhealthy levels, we provide complimentary N95 masks at the front desk and move all outdoor activities indoors. Our rooms are equipped with high-quality air filtration. Your health and comfort are our priority during environmental changes."},
])

# 3. Ramadan & Deepavali Deep Dive
DOCS.extend([
    {"doc_type": "hari_raya", "title": "Ramadan Sahur & Iftar Arrangements",
     "content": "Q: Do you provide Sahur during Ramadan?\nA: Yes! For our fasting guests, we provide Sahur (pre-dawn meal) from 4 AM–5 AM at Horizon Café. For Iftar (breaking fast), we host a lavish 'Citarasa Malaysia' buffet featuring 100+ local dishes like Rendang, Lemang, and Kambing Bakar. Prayer mats and dates are provided in all rooms during the holy month."},
    {"doc_type": "deepavali", "title": "Deepavali Kolam & Lighting Ceremony",
     "content": "Q: Any events for Deepavali?\nA: We celebrate the Festival of Lights with a grand 'Kolam' (rice art) competition in the lobby. Join us for our evening lamp-lighting ceremony on the eve of Deepavali. Enjoy traditional Indian sweets (Mithai) and a special Bollywood-themed dinner at the poolside. A truly vibrant celebration of light over darkness!"},
])

# 4. Generating Bulk Variations for Year-round events
for i in range(1, 41):
    reason = random.choice(["Wedding Anniversary", "Graduation", "Retirement", "Promotion", "New Hire"])
    gift = random.choice(["Cake", "Flower Bouquet", "Fruit Basket", "Balloon Bunch", "Handwritten Card"])
    DOCS.append({
        "doc_type": "promotions",
        "title": f"Celebration Setup: {reason} - {gift}",
        "content": f"Q: We are celebrating a {reason}. Can you arrange a {gift}?\nA: Congratulations on your {reason}! We would love to help you celebrate. We can arrange a beautiful {gift} to be placed in your room upon arrival or during dinner. Prices start from RM50. Please let us know the details at least 24 hours in advance. Making memories is what we do best!"
    })

for i in range(1, 41):
    activity = random.choice(["Yoga by the Beach", "Zumba in the Pool", "Morning Stretching", "Guided Meditation", "Art Class"])
    day = random.choice(["Monday", "Wednesday", "Friday", "Saturday", "Sunday"])
    DOCS.append({
        "doc_type": "activities",
        "title": f"Weekly Activity: {activity} on {day}",
        "content": f"Q: When can I join the {activity}?\nA: Our {activity} takes place every {day} at 8 AM. It's complimentary for all in-house guests and suitable for all levels. Please meet at the Activity Lawn 5 minutes before the start. Bring your water bottle and comfortable attire. A great way to start your day!"
    })
