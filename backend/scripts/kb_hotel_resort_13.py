"""
Segment A — Hotel & Resort Knowledge Base (Part 13)
Categories: Solo Travelers, Budgeting, Rewards, Tech Support
~100 entries
"""

import random

DOCS = []

# 1. Solo Travelers
DOCS.extend([
    {"doc_type": "faqs", "title": "Safety for Solo Female Travelers",
     "content": "Q: Is the resort safe for solo female travelers?\nA: Yes, we prioritize the safety and comfort of all our guests. Our resort has 24/7 security patrolling the grounds. We can assign rooms near the elevators or the lobby upon request. Our staff are trained to be respectful and helpful. We also have a 'Lobby Social' every Wednesday for guests to meet and mingle in a safe environment."},
    {"doc_type": "faqs", "title": "Single Supplement for Tours",
     "content": "Q: Do I have to pay a single supplement for your guided tours?\nA: For most of our group tours (Mangrove, Island Hopping), there is NO single supplement! You'll join a small group of other guests. For private tours, the price is per vehicle/guide, regardless of the number of people. We want our solo guests to enjoy all our activities without extra burden."},
])

# 2. Budgeting & Financials
DOCS.extend([
    {"doc_type": "policies", "title": "Foreign Currency Exchange Rates",
     "content": "Q: Can I exchange money at the hotel? What are the rates?\nA: We offer currency exchange at the Front Desk for major currencies (USD, EUR, SGD, AUD, GBP). Please note that our rates include a small convenience fee and may be slightly lower than city money changers. For the best rates, we recommend using the ATM in the lobby or visiting a licensed money changer in the town centre (10 min drive)."},
    {"doc_type": "policies", "title": "Invoicing for Corporate Tax Filing",
     "content": "Q: Can you provide a detailed tax invoice for my company?\nA: Certainly! We can provide a comprehensive invoice including your company's name, address, and tax ID. Please provide these details at check-in or anytime during your stay. We can email the PDF invoice to you upon check-out for easy filing. Our invoices comply with Malaysian SST requirements."},
])

# 3. Generating Bulk Variations
for i in range(1, 41):
    traveller = random.choice(["Solo Business", "Backpacker", "Digital Nomad", "Senior Traveler", "Student"])
    need = random.choice(["Fast WiFi", "Quiet Zone", "Early Breakfast", "Shared Table", "Local Map"])
    DOCS.append({
        "doc_type": "faqs",
        "title": f"Tip for {traveller}: {need}",
        "content": f"Q: I'm a {traveller}. Do you have {need}?\nA: We welcome all types of travelers! For {traveller}s, we recommend utilizing our {need}, which is specifically designed to enhance your experience. For example, our {need} is located {random.choice(['near the pool', 'in the library', 'near the main lobby', 'on every floor'])}. Enjoy your stay!"
    })

for i in range(1, 40):
    reward = random.choice(["Free Coffee", "Spa Discount", "Late Checkout", "Room Upgrade", "Points Bonus"])
    status = random.choice(["Silver", "Gold", "Platinum", "Diamond", "Lifetime"])
    DOCS.append({
        "doc_type": "loyalty",
        "title": f"Loyalty Perk: {reward} for {status} Members",
        "content": f"Q: As a {status} member, can I get {reward}?\nA: Absolutely! Our loyalty programme highly values our {status} members. You are entitled to {reward} on every stay. Simply present your digital membership card at the relevant outlet or the front desk. We appreciate your continued loyalty and look forward to rewarding you!"
    })
