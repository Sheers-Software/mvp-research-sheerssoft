"""
Segment C — Malaysian Festive Seasonality Knowledge Base (Part 5)
Expanded: Vaisakhi, Wesak Day, Birthday of the Prophet, long weekends
~100 entries
"""

import random

DOCS = []

# 1. Vaisakhi & Wesak Day
DOCS.extend([
    {"doc_type": "festive", "title": "Vaisakhi Celebration — Sikh Heritage",
     "content": "Q: Do you have anything special for Vaisakhi?\nA: Happy Vaisakhi! We celebrate the Sikh New Year by featuring traditional Punjabi sweets like Ladoo and Gulab Jamun at our dessert corner. Our lobby is decorated with vibrant cultural elements. We can also provide directions to the nearest Gurdwara for guests who wish to attend prayers. Jo Bole So Nihal!"},
    {"doc_type": "festive", "title": "Wesak Day — Spirit of Compassion",
     "content": "Q: How do you mark Wesak Day?\nA: On Wesak Day, we focus on tranquility and compassion. Our restaurants offer a special 'Zen' vegetarian set menu. We also host a morning meditation session at the Garden Pavilion. It's a peaceful time to reflect and enjoy the serene atmosphere of our resort. Wishing you a blessed Wesak Day!"},
])

# 2. Birthday of the Prophet (Maulidur Rasul)
DOCS.extend([
    {"doc_type": "festive", "title": "Maulidur Rasul — Observance & Meals",
     "content": "Q: Any special arrangements for Maulidur Rasul?\nA: To mark the Prophet's Birthday, we host a special 'Nasi Ambeng' communal dinner, promoting the spirit of togetherness. Our Surau holds extra sessions for Zikir and Selawat. It's a day of spiritual reflection and community. Please check our daily activity board for timing details."},
])

# 3. Generating Bulk Variations for Long Weekends & Public Holidays
for i in range(1, 41):
    holiday = random.choice(["Merdeka Day", "Malaysia Day", "Agong's Birthday", "Labour Day", "Wesak Day"])
    benefit = random.choice(["Free breakfast upgrade", "Complimentary late check-out", "RM50 spa voucher", "Free welcome drink", "10% off laundry"])
    DOCS.append({
        "doc_type": "promotions",
        "title": f"Holiday Special: {holiday} - {benefit}",
        "content": f"Q: Do you have a special deal for {holiday}?\nA: Yes! For the {holiday} long weekend, every booking receives a {benefit}. It's our way of helping you celebrate the national holiday in style. Please ensure you book directly through our website to enjoy this {benefit}. Subject to availability, so book early!"
    })

for i in range(1, 41):
    scenario = random.choice(["Rainy day activity", "Power outage protocol", "Traffic advisory", "Crowd management", "Extra shuttle service"])
    festival = random.choice(["CNY", "Hari Raya", "Christmas", "Deepavali", "Gawai"])
    DOCS.append({
        "doc_type": "peak_season",
        "title": f"Management during {festival}: {scenario}",
        "content": f"Q: How do you handle {scenario} during the busy {festival} period?\nA: During {festival}, we step up our operations to ensure a smooth experience. For {scenario}, we have special measures in place: {random.choice(['Extra staff on standby', 'Backup generators tested', 'Alternative routes planned', 'Queue management systems active', 'Enhanced communication via WhatsApp'])}. Your comfort is our priority, even during peak crowds!"
    })
