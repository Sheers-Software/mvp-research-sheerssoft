"""
Segment B — Homestay, Villa, Chalet, Inn Knowledge Base (Part 6)
Expanded: Smart Home Guide, Remote Check-in Troubleshooting, Security Cameras
~100 entries
"""

import random

DOCS = []

# 1. Smart Home Guide
DOCS.extend([
    {"doc_type": "utilities", "title": "Smart Lock — Detailed Operation",
     "content": "Q: The digital lock isn't accepting my code.\nA: Please ensure you are entering the code slowly. 1. Press any key to wake the screen. 2. Enter your 6-digit code. 3. Press the '#' or '*' key as instructed in your check-in message. If the lock beeps 3 times, the code was incorrect. After 5 failed attempts, the lock will freeze for 2 minutes. Contact us if you need a remote unlock!"},
    {"doc_type": "utilities", "title": "Smart TV & Streaming Accounts",
     "content": "Q: How do I watch Netflix on the Smart TV?\nA: Our TV is set up with a 'Guest' Netflix account. Simply select the Netflix app and the Guest profile. Please do NOT log out of this account. If you wish to use your own account, remember to log out before you check-out! To return to local TV, press the 'Source' button and select 'Live TV'."},
])

# 2. Remote Check-in Troubleshooting
DOCS.extend([
    {"doc_type": "checkin", "title": "Locating the Key Lockbox",
     "content": "Q: I can't find the lockbox at the property.\nA: The lockbox is located behind the white pillar on the right side of the main gate. It is a black box with a silver dial. Please refer to the photos sent in your 'Check-in Instructions' via WhatsApp. Use the code provided to open it. If you still can't find it, our caretaker is only 5 minutes away!"},
    {"doc_type": "checkin", "title": "Digital ID Verification Process",
     "content": "Q: Why do I need to upload my ID for a homestay?\nA: For security and local council regulation compliance, we require a digital copy of the primary guest's ID (MyKad or Passport). This is handled via our secure platform and is only used for guest verification and safety. Your data is protected under the Malaysian PDPA. Thank you for your cooperation!"},
])

# 3. Generating Bulk Variations for Smart Home & Check-in
for i in range(1, 41):
    feature = random.choice(["Aircon Remote", "Water Heater", "Auto Gate", "CCTV Monitor", "WiFi Extender"])
    issue = random.choice(["not responding", "flashing light", "low battery", "wrong setting", "making noise"])
    DOCS.append({
        "doc_type": "utilities",
        "title": f"Smart Feature: {feature} {issue}",
        "content": f"Q: The {feature} is {issue}. How do I fix it?\nA: We apologize for the inconvenience. For the {feature}, please try resetting the power at the main switch first. If it's {issue} because of batteries, there are spares in the kitchen drawer. If the problem persists, please message us and we'll send someone over to assist you immediately."
    })

for i in range(1, 41):
    request = random.choice(["Extra Pillow", "Floor Mat", "Towel Exchange", "Ironing Board", "Prayer Mat"])
    bedroom = random.choice(["Master Room", "Twin Room", "Living Area", "Store Room", "Attic"])
    DOCS.append({
        "doc_type": "utilities",
        "title": f"Finding {request} in {bedroom}",
        "content": f"Q: Can I find a {request} in the {bedroom}?\nA: Typically, {request}s are kept in the storage wardrobe of the {bedroom}. If you don't find one there, please check the main utility cabinet near the kitchen. We provide basic amenities for your comfort. Let us know if you need anything else!"
    })
