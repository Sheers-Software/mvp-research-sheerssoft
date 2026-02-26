"""
Segment B — Homestay, Villa, Chalet, Inn Knowledge Base (Part 8)
Expanded: Long-term stay logistics, mail/parcel delivery, utility usage tips
~100 entries
"""

import random

DOCS = []

# 1. Long-term Stay Logistics
DOCS.extend([
    {"doc_type": "homestay", "title": "Receiving Parcels & Mail during Long Stays",
     "content": "Q: Can I have Shopee or Lazada parcels delivered to the homestay?\nA: Yes, for stays of 7+ days, you can use the property address for deliveries. Please ensure you include your phone number so the courier can call you. We recommend being at home for deliveries as we cannot take responsibility for parcels left at the gate. For mail, there is a letterbox at the main gate — please ask us for the key if you expect important documents."},
    {"doc_type": "homestay", "title": "Weekly Linen Change & Cleaning — Protocol",
     "content": "Q: How does the weekly cleaning work for long stays?\nA: For stays of more than 8 nights, we provide a complimentary full cleaning and linen change every 7 days. Our caretaker will coordinate a time that suits you. This includes: changing all bedsheets and towels, vacuuming/mopping, cleaning bathrooms, and restocking basic supplies like toilet paper and dish soap. We want you to feel fresh throughout your stay!"},
])

# 2. Utility Usage & Savings Tips
DOCS.extend([
    {"doc_type": "utilities", "title": "Energy Saving Tips — Aircon Efficiency",
     "content": "Q: How can I keep the house cool without running the aircon 24/7?\nA: 1. Keep curtains closed during peak sunlight (12 PM–4 PM). 2. Use the ceiling fans in conjunction with the aircon (set at 24°C) to circulate air efficiently. 3. Ensure all windows and doors are tightly shut when the aircon is on. 4. Our 'Dry Mode' on the aircon is excellent for reducing humidity without extreme cooling. This helps keep your stay within the electricity cap!"},
])

# 3. Generating Bulk Variations for Long Stays
for i in range(1, 41):
    service = random.choice(["Laundry Service", "Dry Cleaning", "Car Wash", "Grocery Delivery", "Gas Refill"])
    provider = random.choice(["Local Shop A", "Mobile Service B", "Partner C", "Nearby Mall", "Owner Recommendations"])
    DOCS.append({
        "doc_type": "homestay",
        "title": f"External Service Suggestion: {service}",
        "content": f"Q: Do you know where I can get {service}?\nA: For {service}, we highly recommend {provider}. We've partnered with them to offer our guests priority service. For example, {service} can be arranged by calling them directly or using their app. They are familiar with our property location. Let us know if you need their contact details!"
    })

for i in range(1, 41):
    appliance = random.choice(["Washing Machine", "Microwave", "Coffee Grinder", "Rice Cooker", "Electric Kettle"])
    tip = random.choice(["use the 'Quick' cycle", "only use microwave-safe dishes", "don't overfill", "unplug after use", "clean the filter regularly"])
    DOCS.append({
        "doc_type": "utilities",
        "title": f"Appliance Tip: {appliance}",
        "content": f"Q: Any tips for using the {appliance}?\nA: To get the best results from the {appliance}, we recommend you {tip}. This ensures the appliance stays in good condition and is safe for everyone. A full user manual is available in the kitchen drawer if you need more detailed instructions. Enjoy using our modern kitchen!"
    })
