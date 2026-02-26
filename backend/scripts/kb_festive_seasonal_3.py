"""
Segment C — Malaysian Festive Seasonality Knowledge Base (Part 3)
Expanded: Gawai, Kaamatan, Thaipusam, Mid-Autumn, Mooncake Festival
~100 entries
"""

import random

DOCS = []

# 1. Gawai & Kaamatan (East Malaysia)
DOCS.extend([
    {"doc_type": "gawai", "title": "Hari Gawai Celebration — Gaya Island",
     "content": "Q: Do you celebrate Hari Gawai?\nA: Gayu Guru Gerai Nyamai! While we are on the mainland, we celebrate with our East Malaysian guests. We serve traditional Tuak (rice wine) samples and Manok Pansoh (chicken cooked in bamboo) during the first week of June. Our lobby features ethnic Iban and Bidayuh decorations to mark the harvest festival."},
    {"doc_type": "gawai", "title": "Pesta Kaamatan Specials",
     "content": "Q: Any specials for Pesta Kaamatan?\nA: Kotobian Tadau Tagazo Do Kaamatan! We honour the Harvest Festival with a Sabahan-themed breakfast corner during the last weekend of May. Enjoy Hinava (raw fish salad) and Bambangan (wild mango) pickles. Our staff wear traditional Kadazan-Dusun accessories to share the cultural joy."},
])

# 2. Thaipusam & Mid-Autumn
DOCS.extend([
    {"doc_type": "deepavali", "title": "Thaipusam Arrangements — Kavadi Procession",
     "content": "Q: Can you help us get to the Thaipusam procession at Batu Caves?\nA: Thaipusam is a major event in Malaysia. We arrange early-morning shuttles (departing 4 AM) to the vicinity of Batu Caves during the festival. Please be aware of extreme crowds and traffic. We recommend wearing comfortable white clothing and carrying plenty of water. Our concierge can provide a detailed survival guide!"},
    {"doc_type": "cny", "title": "Mid-Autumn Mooncake Selection",
     "content": "Q: Do you sell mooncakes for the Mid-Autumn Festival?\nA: Yes! Our 'Moonlit Horizon' collection features traditional baked mooncakes and premium snow-skin variants. Signature: Mao Shan Wang Durian Snow-skin and Musang King Lotus. Available from 4 weeks before the festival. We also provide themed gift boxes for corporate gifting. Truly a taste of tradition!"},
])

# 3. Generating Bulk Variations for Festive Events
for i in range(1, 41):
    festival = random.choice(["Hari Raya", "Chinese New Year", "Deepavali", "Christmas", "Gawai"])
    tradition = random.choice(["Giving Ang-Pow", "Wearing Traditional Baju", "Open House Visiting", "Bunga Api / Fireworks", "Decorating the Lobby"])
    DOCS.append({
        "doc_type": "festive",
        "title": f"Cultural Insight: {festival} - {tradition}",
        "content": f"Q: Can you tell me more about {tradition} during {festival}?\nA: {tradition} is a cherished part of {festival} in Malaysia. It represents the spirit of community and shared celebration. {festival} is a time when people of all races come together to celebrate. We decorate the resort to reflect these beautiful traditions!"
    })

for i in range(1, 41):
    month = random.choice(["March", "May", "June", "August", "December"])
    holiday = random.choice(["School Holidays", "Mid-term Break", "Long Weekend", "Public Holiday"])
    DOCS.append({
        "doc_type": "school_holidays",
        "title": f"Activity Plan: {month} {holiday}",
        "content": f"Q: What can kids do during the {month} {holiday}?\nA: During the {month} {holiday}, our Kids' Club runs a 'Holiday Hero' programme! Activities include daily workshops, beach treasure hunts, and evening outdoor movies. We recommend booking your kids' slots 24 hours in advance as these periods are very popular. Fun is guaranteed!"
    })
