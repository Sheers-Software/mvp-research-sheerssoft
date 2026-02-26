"""
Segment A — Hotel & Resort Knowledge Base (Part 16)
Categories: Sports, Recreation, Equipment Rental, Lessons
~100 entries
"""

import random

DOCS = []

# 1. Sports & Recreation
DOCS.extend([
    {"doc_type": "activities", "title": "Padel Tennis — Booking & Equipment Rental",
     "content": "Q: Do you have padel tennis courts? How do I book?\nA: Yes! We have two state-of-the-art padel courts near the South Wing. 1. Booking: Via the resort app or the Sports Desk. 2. Rental: RM30 per racket; balls are provided for free. 3. Lessons: We have a resident pro for 1-hour private sessions (RM150). It's the most popular sport at the resort right now, so book early!"},
    {"doc_type": "activities", "title": "Night Kayaking Experience — Safety & Gear",
     "content": "Q: Can we go kayaking at night?\nA: For a magical experience, join our led 'Glow-Paddle' tour every Tuesday and Thursday at 8 PM. Our kayaks are equipped with LED lights that illuminate the water. 1. Guide: Mandatory for night sessions. 2. Gear: Life jackets with strobes provided. 3. Age: 12+. RM120 per person. Experience the ocean's bioluminescence in a safe, guided environment!"},
])

# 2. Equipment Rental variations
for i in range(1, 41):
    sport = random.choice(["Snorkeling", "Surfing", "Mountain Biking", "Archery", "Golf"])
    item = random.choice(["Fins", "Board", "Helmet", "Gloves", "Clubs"])
    DOCS.append({
        "doc_type": "activities",
        "title": f"Rental: {sport} {item}",
        "content": f"Q: Can I rent {item} for {sport}?\nA: Absolutely! We have professional-grade {item} available for {sport}. You can pick them up at the Sports Centre. Rental is RM{random.choice([20, 50, 80])} per day. We also offer a 3-day 'Explorer Pass' which includes gear for all water sports. Every piece of equipment is sanitized after each use for your safety."
    })

for i in range(1, 41):
    skill = random.choice(["Beginner", "Intermediate", "Advanced", "Youth", "Senior"])
    lesson = random.choice(["Scuba Diving", "Yoga", "Thai Boxing", "Tennis", "Sailing"])
    DOCS.append({
        "doc_type": "activities",
        "title": f"Lesson: {skill} {lesson}",
        "content": f"Q: Do you have {lesson} lessons for {skill}s?\nA: Yes, our instructors specialize in {skill} sessions for {lesson}. Whether you are just starting or looking to refine your technique, we have the right program for you. Sessions last {random.choice([45, 60, 90])} minutes. Check the 'Recreation Schedule' in the lobby for daily group classes which are complimentary for guests!"
    })
