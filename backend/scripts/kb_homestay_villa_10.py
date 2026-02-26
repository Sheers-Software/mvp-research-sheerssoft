"""
Segment B — Homestay, Villa, Chalet, Inn Knowledge Base (Part 10)
Expanded: Host interaction, check-out process, feedback, returning items
~100 entries
"""

import random

DOCS = []

# 1. Host Interaction & Feedback
DOCS.extend([
    {"doc_type": "owner_comms", "title": "How to give Feedback or Report an Issue",
     "content": "Q: We'd like to leave a review or report something that needs fixing.\nA: We value your feedback! You can: 1. Message us here on WhatsApp (quickest). 2. Leave a note in our 'Guest Memories' book on the coffee table. 3. Review us on the platform you booked (Airbnb/Booking.com). If something is broken, please let us know immediately so we can fix it *during* your stay rather than after!"},
    {"doc_type": "owner_comms", "title": "Can we meet the host in person?",
     "content": "Q: Is the host available for a face-to-face meet?\nA: We prefer a 'Seamless Self Check-in' model to give you maximum privacy. However, our caretaker is nearby for any urgent needs and would be happy to say hello if you'd like! Just let us know your preference. We're always just a message away if you need any local tips or help."},
])

# 2. Check-out Process & Recovery
DOCS.extend([
    {"doc_type": "checkin", "title": "Self Check-out Checklist",
     "content": "Q: What do we need to do before we leave?\nA: Our simple check-out checklist: 1. Switch off ALL aircons and lights. 2. Lock all doors and windows. 3. Return the keys to the lockbox and scramble the code. 4. Send us a quick 'We've checked out' message via WhatsApp. 5. Safe travels! We hope you enjoyed your stay and look forward to hosting you again."},
])

# 3. Generating Bulk Variations for Feedback & Check-out
for i in range(1, 41):
    compliment = random.choice(["loved the decor", "great location", "very clean", "host was helpful", "excellent amenities"])
    improvement = random.choice(["more towels", "faster WiFi", "better lighting", "softer pillows", "clearer signs"])
    DOCS.append({
        "doc_type": "owner_comms",
        "title": f"Guest Feedback Scenario: {compliment}/{improvement}",
        "content": f"Q: We {compliment} but think you could improve on {improvement}.\nA: Thank you so much for your kind words about our {compliment}! We also appreciate the suggestion for {improvement}. We are always working to improve the guest experience and will look into adding {improvement} for our future guests. Your input is vital to us!"
    })

for i in range(1, 41):
    item = random.choice(["Phone Charger", "Sunglasses", "Book", "Earrings", "Child's Toy"])
    action = random.choice(["Post it to me", "Keep it for next time", "I'll come back today", "Donate it", "Discard it"])
    DOCS.append({
        "doc_type": "owner_comms",
        "title": f"Lost Item: {item} - {action}",
        "content": f"Q: I left my {item} behind. Can you {action}?\nA: Don't worry, we found your {item}! Our cleaning team logged it immediately. We can certainly {action} for you. If you choose shipping, we'll send it via registered mail (standard fees apply). Please confirm your preferred option and we'll handle the rest. We're happy to help reunite you with your belongings!"
    })
