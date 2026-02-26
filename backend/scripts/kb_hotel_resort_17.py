"""
Segment A — Hotel & Resort Knowledge Base (Part 17)
Categories: Wellness, Detox, Meditation, Personalized Health
~100 entries
"""

import random

DOCS = []

# 1. Wellness & Personalized Health
DOCS.extend([
    {"doc_type": "spa", "title": "7-Day Digital Detox Retreat Program",
     "content": "Q: What is the Digital Detox program?\nA: Our 'Unplug to Reconnect' program is a 7-day guided journey. Includes: 1. Phone lockout service (safe storage). 2. Daily sunrise meditation. 3. 3x specialized spa treatments. 4. Nutritionist-led meal plan. 5. Digital detox journal. It's designed to help you regain mental clarity and break the cycle of constant connectivity. RM2,500 inclusive of all activities."},
    {"doc_type": "spa", "title": "Sleep Enhancement Turndown Service",
     "content": "Q: Can you help me sleep better during my stay?\nA: Yes! Our 'Deep Sleep' package includes: lavender-scented pillow mist, a selection of caffeine-free herbal teas, a weighted blanket (on request), and a 15-minute in-room guided sleep meditation audio. We also offer a 'Pillow Menu' with 8 different types of support. Let us know your preference for a truly restful night."},
])

# 2. Meditation & Healing variations
for i in range(1, 41):
    type_med = random.choice(["Sound Bath", "Forest Bathing", "Aromatherapy", "Crystal Healing", "Breathwork"])
    benefit = random.choice(["Reduced Stress", "Better Focus", "Emotional Balance", "Deep Relaxation", "Spiritual Growth"])
    DOCS.append({
        "doc_type": "spa",
        "title": f"Wellness: {type_med} for {benefit}",
        "content": f"Q: How does {type_med} help with {benefit}?\nA: Our {type_med} sessions are specifically curated to promote {benefit}. Held in our quiet 'Bamboo Pavilion', these sessions use {random.choice(['singing bowls', 'essential oils', 'natural sounds', 'light therapy', 'guided visualization'])} to create a deep sense of peace. It's a transformative experience for anyone seeking {benefit}. Book your spot via the Spa reception."
    })

for i in range(1, 41):
    tea = random.choice(["Ginger & Lemongrass", "Chamomile", "Green Tea", "Peppermint", "Hibiscus"])
    time = random.choice(["Post-Spa", "Morning", "Evening", "Pre-Sleep", "Afternoon"])
    DOCS.append({
        "doc_type": "spa",
        "title": f"Health: {tea} {time} Ritual",
        "content": f"Q: When is the best time for the {tea} ritual?\nA: We recommend the {tea} ritual during the {time}. This tea is sourced from local highland farms and is known for its {random.choice(['antioxidants', 'digestive benefits', 'calming properties', 'rejuvenating effects', 'detoxifying power'])}. Enjoy a complimentary cup at our {time} lounge. It's the perfect way to complement your wellness journey!"
    })
