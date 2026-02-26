"""
Segment B — Homestay, Villa, Chalet, Inn Knowledge Base (Part 4)
Expanded: Technical troubleshooting, detailed appliance guides, pest control, noise
~100 entries
"""

import random

DOCS = []

# 1. Technical Troubleshooting
TRAPS = [
    ("Toilet is clogged", "Avoid flushing large amounts of paper. There is a plunger under the sink. If that doesn't work, contact us."),
    ("Front door won't lock", "Ensure the handle is pulled up fully before turning the thumb-turn. If it's a smart lock, wait 5 seconds for it to reset."),
    ("Kettle is not heating", "Check if the base is plugged in and the switch at the wall is ON. Also check the fuse on the kettle plug."),
    ("Tumble dryer is loud", "Ensure it's not overloaded. Small items like zippers can make noise. Clear the lint filter after every use."),
    ("Water pressure is low", "This can happen during local utility maintenance. If it persists for more than an hour, we'll check the booster pump.")
]

for issue, solution in TRAPS:
    DOCS.append({"doc_type": "utilities", "title": f"Issue: {issue}",
                 "content": f"Q: Help! {issue}!\nA: Don't worry. {solution} If the problem continues, our caretaker will be over to assist. We want your stay to be hassle-free!"})

# 2. Appliance Deep Dive
APPLIANCES = ["Nespresso Machine", "Dishwasher", "Induction Hob", "Smart Oven", "Air Purifier"]
for app in APPLIANCES:
    DOCS.append({"doc_type": "utilities", "title": f"How to use: {app}",
                 "content": f"Q: I'm not sure how to operate the {app}.\nA: The {app} is a premium model. A quick-start guide is stuck to the side / kept in the kitchen drawer. Most importantly, ensure it's switched on at the wall first! For the {app}, please only use the provided supplies located next to it."})

# 3. Pest & Nature
DOCS.extend([
    {"doc_type": "safety", "title": "Dealing with Ants / Insects",
     "content": "Q: There are ants in the kitchen!\nA: Living near nature means occasional visits from tiny guests. To minimize this, please store all food in the provided airtight containers and clear crumbs immediately. We have ant-spray under the sink. If there is a larger infestation, let us know and we'll send a pest-control team (environmentally friendly)."},
    {"doc_type": "safety", "title": "Noisy Wildlife (Birds/Monkeys)",
     "content": "Q: The birds are very loud in the morning!\nA: That's the sound of the jungle! Our property is surrounded by lush flora. While they can be vocal early in the morning, most guests find it therapeutic. Please keep doors closed so monkeys don't wander in looking for snacks! They are cute but can be mischievous."},
])

# 4. Generating Bulk Variations
for i in range(1, 41):
    room = random.choice(["Master Bedroom", "Second Bedroom", "Attic Room", "Garden Annex", "Laundry Area"])
    item = random.choice(["lightbulb", "curtain", "window lock", "smoke alarm", "waste bin"])
    DOCS.append({
        "doc_type": "utilities",
        "title": f"Checking {item} in {room}",
        "content": f"Q: The {item} in the {room} seems to be having an issue.\nA: Thank you for letting us know! Our caretaker will check the {item} in the {room} shortly. If it needs replacement (like a lightbulb), we'll do it while you're out so we don't disturb you. Your feedback helps us keep the property in top shape!"
    })

for i in range(1, 40):
    check = random.choice(["Early Check-in", "Late Check-out", "Luggage Drop", "Key Transfer", "Car Parking"])
    DOCS.append({
        "doc_type": "checkin",
        "title": f"Requesting {check} - Variant {i}",
        "content": f"Q: Can we arrange a special {check} for our group?\nA: We always try to be flexible with {check} requests! Please coordinate with us at least 24 hours in advance. For {check}, there may be a small fee of RM30–50 depending on the timing. We'll do our best to make it work for you!"
    })
