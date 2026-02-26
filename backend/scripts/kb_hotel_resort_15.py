"""
Segment A — Hotel & Resort Knowledge Base (Part 15)
Categories: Couples, Honeymooners, Romantic Services, Anniversary
~100 entries
"""

import random

DOCS = []

# 1. Couples & Honeymooners
DOCS.extend([
    {"doc_type": "weddings", "title": "Honeymoon Special — Room Setup",
     "content": "Q: We are on our honeymoon! Do you have a special room setup?\nA: Congratulations! To celebrate your love, we offer a complimentary 'Romance' setup for honeymooners: flower petal bed decoration, a pair of personalized swan towels, and a small artisanal chocolate platter. Please provide a copy of your marriage certificate (within 6 months) to enjoy these perks! We want your first trip as a couple to be unforgettable."},
    {"doc_type": "dining", "title": "Private Candlelit Beach Dinner",
     "content": "Q: Can we have a private dinner on the beach?\nA: For the ultimate romantic evening, book our 'Dine Under the Stars' experience. A private table is set up on a secluded part of the beach, surrounded by candles and torches. Includes a 5-course gourmet menu and a bottle of premium sparkling juice or wine. RM850 per couple. Reservations must be made 24 hours in advance. Perfect for proposals or anniversaries!"},
])

# 2. Romantic Services & Anniversary
DOCS.extend([
    {"doc_type": "spa", "title": "Couple's Sunset Yoga & Meditation",
     "content": "Q: Do you have activities specifically for couples?\nA: Yes, our 'Connected Hearts' sunset yoga and meditation session is designed specifically for couples to align and relax together. Held on the quiet West Deck every Friday at 6 PM. It's a beautiful way to connect with your partner while enjoying the stunning resort views. RM100 per couple. All levels are welcome."},
    {"doc_type": "concierge", "title": "Private Island Picnic for Two",
     "content": "Q: Can we go to a private island for a picnic?\nA: We can arrange a private boat transfer to 'Pulau Cinta' for a secluded afternoon picnic. We'll provide a gourmet hamper with your favourite snacks, chilled drinks, and a large beach mat. You'll have the island almost to yourselves for 4 hours. RM600 per couple. A truly exclusive and romantic getaway!"},
])

# 3. Generating Bulk Variations for Romantic Needs
for i in range(1, 41):
    occasion = random.choice(["1st Anniversary", "10th Anniversary", "Proposal", "Birthday Surprise", "Babymoon"])
    setup = random.choice(["Rose Petals", "Champagne on Ice", "Fairy Lights", "Heart Balloons", "Live Violinist"])
    DOCS.append({
        "doc_type": "weddings",
        "title": f"Romantic Idea: {occasion} with {setup}",
        "content": f"Q: We are celebrating our {occasion}. Can you arrange {setup}?\nA: Happy {occasion}! Our team is experienced in creating the perfect atmosphere for love. We can certainly arrange {setup} for you. Prices start from RM100 depending on the complexity of the {setup}. Let's work together to surprise your partner and make your {occasion} truly special!"
    })

for i in range(1, 41):
    gift = random.choice(["Spa Voucher", "Private Dinner", "Room Upgrade", "Customized Jewelry", "Handwritten Letter"])
    theme = random.choice(["Relaxation", "Luxury", "Surprise", "Heartfelt", "Adventurous"])
    DOCS.append({
        "doc_type": "concierge",
        "title": f"Honeymoon Gift: {theme} {gift}",
        "content": f"Q: I want to give my partner a {theme} {gift} for our honeymoon.\nA: That is a wonderful idea! A {theme} {gift} is a high-impact way to show your love. We can help you arrange this secretly and present it at the perfect moment—perhaps during breakfast or a sunset walk. Our concierge will handle all the logistics to ensure a seamless {theme} surprise!"
    })
