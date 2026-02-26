"""
Segment A — Hotel & Resort Knowledge Base (Part 5)
Categories: Complaints & Service Recovery, Weddings & Events, Kids & Family,
            Transport & Directions, Business & MICE, Sustainability
~50 entries
"""

DOCS = [
    # ═══════════════════════════════════════════════════════════════
    # COMPLAINTS & SERVICE RECOVERY (~15)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "complaints", "title": "Noisy Room Complaint",
     "content": "Q: Our room is very noisy — there's construction next door!\nA: I sincerely apologise for the disturbance. Your comfort is our top priority. I will immediately:\n1. Check for available rooms to relocate you\n2. Arrange a complimentary room move with porter assistance\n3. If no move is possible, provide earplugs and a noise machine\n4. Apply a 20% discount on tonight's room charge\nPlease allow me 15 minutes to find the best solution for you."},
    {"doc_type": "complaints", "title": "Hair Found in Food",
     "content": "Q: I found a hair in my soup!\nA: I'm terribly sorry about this. That is completely unacceptable and I take your complaint very seriously. Please allow me to:\n1. Replace your dish immediately with a fresh one\n2. The dish will be complimentary — no charge\n3. I will inform our Head Chef for immediate attention\n4. Would you like a complimentary dessert as an apology?\nYour dining experience matters deeply to us, and I want to make this right."},
    {"doc_type": "complaints", "title": "Slow Room Service Response",
     "content": "Q: We ordered room service 50 minutes ago and nothing has arrived!\nA: I apologise for the unacceptable delay. Let me check your order status with the kitchen right away. I will:\n1. Personally escalate your order for immediate preparation\n2. Ensure delivery within 10 minutes\n3. Waive the room service charge for this order\n4. Add a complimentary item as our apology\nYou should never have to wait this long. I'm on it now."},
    {"doc_type": "complaints", "title": "Bathroom Hygiene Issue",
     "content": "Q: The bathroom wasn't cleaned properly — there's still hair in the drain.\nA: I sincerely apologise. Our housekeeping standards should be much higher than this. I will:\n1. Send our housekeeping supervisor immediately for a thorough re-clean\n2. Provide fresh towels, toiletries, and bath amenities\n3. Apply a complimentary spa credit of RM50 to your room\nYou deserve a spotless room and we fell short. It won't happen again during your stay."},
    {"doc_type": "complaints", "title": "Wi-Fi Not Working",
     "content": "Q: The Wi-Fi is down and I have a Zoom meeting in 30 minutes!\nA: I understand how urgent this is. Let me help immediately:\n1. Our IT team will check your room's connectivity within 5 minutes\n2. In the meantime, I can provide our backup mobile hotspot device\n3. Our Business Centre has dedicated wired internet (Level 2)\n4. I'll also share the Wi-Fi details for our backup network\nYour work is important — we'll get you connected right away."},
    {"doc_type": "complaints", "title": "Overcharging on Bill",
     "content": "Q: There's a charge on my bill I don't recognise — RM280 for minibar.\nA: I completely understand your concern. Let me look into this immediately:\n1. I'll pull up your room's minibar usage log\n2. If the charge is incorrect, I'll remove it immediately and issue a revised invoice\n3. If it's a system error, I'll escalate to our finance team\nWe never want billing surprises. Transparency is important to us. Give me 10 minutes to investigate."},
    {"doc_type": "complaints", "title": "Lost Property Follow-Up",
     "content": "Q: I left my phone charger in the room after check-out.\nA: Let me help you retrieve it! I'll contact housekeeping to check your former room immediately. If found:\n• We'll keep it at the front desk for collection\n• Or we can courier it to your Malaysian address (RM15 shipping)\n• International shipping is also possible (actual postage cost)\nPlease describe the item and your room number. We hold lost property for 90 days."},

    # ═══════════════════════════════════════════════════════════════
    # WEDDINGS & EVENTS (~15)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "weddings", "title": "Wedding Venue Options",
     "content": "Q: We're planning our wedding. What venues do you offer?\nA: Mabrook and tahniah! Our wedding venues:\n• Grand Ballroom (300 pax): from RM15,000 for ceremony + reception\n• Garden Pavilion (100 pax): from RM8,000 (outdoor, sunset backdrop)\n• Beachfront (150 pax): from RM12,000 (toes-in-sand ceremony)\n• Poolside deck (80 pax): from RM6,000 (intimate gatherings)\nPackages include tables, chairs, basic decor, PA system, and wedding coordinator. Customisation is our specialty!"},
    {"doc_type": "weddings", "title": "Wedding Catering Packages",
     "content": "Q: What's included in your wedding food packages?\nA: Our wedding catering options:\n• Malaysian Set Menu (8-course): from RM100/pax\n• International Buffet: from RM120/pax\n• Premium Buffet with Seafood: from RM160/pax\n• Fine Dining Set Menu: from RM180/pax\nAll packages include welcome drinks, wedding cake cutting (cake provided by you or add RM800), and complimentary food tasting for 4 persons before the event."},
    {"doc_type": "weddings", "title": "Wedding Room Block Rates",
     "content": "Q: Can our wedding guests get a discount on rooms?\nA: Yes! For weddings at our property:\n• Block of 10+ rooms: 20% off best available rate\n• Block of 20+ rooms: 25% off + complimentary bridal suite upgrade\n• Block of 30+ rooms: 30% off + bridal suite + complimentary shuttle\nGuests book using a special code. Room block is held for 30 days before release. We'll assign rooms near each other whenever possible."},
    {"doc_type": "weddings", "title": "Malay Nikah Ceremony Setup",
     "content": "Q: Can we hold a nikah ceremony at the hotel?\nA: Absolutely! We regularly host nikah ceremonies:\n• Private Nikah room (40 pax): from RM3,000\n• Garden Nikah setup: from RM4,000\n• Includes: pelamin (dais), bunga telur arrangement area, PA system, and prayer mat area\n• We can recommend a tok kadi and dulang hantaran supplier\n• Sirih junjung and bunga rampai setup available\nOur team understands Malay wedding customs beautifully."},
    {"doc_type": "weddings", "title": "Indian Wedding Ceremony Support",
     "content": "Q: Do you cater for Indian weddings?\nA: We warmly welcome Indian weddings!\n• Our venues support both ceremony and reception\n• We accommodate the mandap/stage setup\n• Indian vegetarian catering available (from RM80/pax)\n• Banana leaf dining can be arranged\n• Sound system for traditional music\n• Mehendi (henna) parlour can be set up in a meeting room\n• Fire-safe thali ceremony area available\nOur team has experience with Hindu, Sikh, and Christian Indian ceremonies."},
    {"doc_type": "events", "title": "Birthday Party Arrangements",
     "content": "Q: Can you help plan a surprise birthday party?\nA: We love surprises! Our birthday packages:\n• Room decoration: balloons, banner, confetti (RM180)\n• Cake: chocolate/vanilla (RM120), custom cake (from RM200)\n• Private dining setup: from RM400 (min 8 pax)\n• KTV room with party setup: RM500 (3 hours, max 15 pax)\n• Poolside BBQ party: from RM60/pax\nJust tell us their name, favourite colour, and dietary preferences — we'll handle the rest! 'Surprise guaranteed' is our motto 🎂"},

    # ═══════════════════════════════════════════════════════════════
    # KIDS & FAMILY (~10)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "kids", "title": "Kids' Club Programme",
     "content": "Q: What does the Kids' Club offer?\nA: Our Little Explorers Kids' Club (ages 4–12):\n• Open: 9 AM–5 PM daily (extended to 8 PM during school holidays)\n• Activities: arts & crafts, treasure hunts, pool games, nature walks, cooking mini-class\n• Professional childminders (1:5 ratio)\n• Snacks and drinks included\n• Complimentary for in-house guests\nDrop-off service so parents can enjoy their own time. Children adore our mascot, Timmy the Turtle!"},
    {"doc_type": "kids", "title": "Baby Amenities Available",
     "content": "Q: We're travelling with a 6-month-old. What baby equipment do you have?\nA: We're baby-ready! Available at no charge:\n• Baby cot (with mattress and bedding)\n• High chair for restaurants\n• Baby bath tub\n• Bottle steriliser and warmer\n• Baby-safe shampoo and lotion\n• Nappy disposal bags\nPlease request items at booking so we can set up before arrival. Our team loves little guests — they're the stars of every stay!"},
    {"doc_type": "kids", "title": "Teen Activities & Entertainment",
     "content": "Q: What's there for teenagers to do?\nA: We haven't forgotten the teens!\n• Games Room: PlayStation 5, table tennis, foosball (Level 2)\n• Water sports: kayaking, paddleboarding (from age 12)\n• Beach volleyball and soccer\n• Movie nights by the pool (weekends)\n• Photography walk with our in-house photographer\n• WiFi zones with charging stations throughout\nMany teens also enjoy exploring the nearby town independently. We can recommend safe and fun spots!"},

    # ═══════════════════════════════════════════════════════════════
    # TRANSPORT & DIRECTIONS (~10)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "transport", "title": "Airport Transfer Service",
     "content": "Q: Can you arrange airport pickup?\nA: Yes! Our airport transfer service:\n• Sedan (1–2 pax): RM120 one-way\n• MPV (3–5 pax): RM180 one-way\n• Van (6–10 pax): RM280 one-way\n• Premium sedan (Mercedes): RM250 one-way\nDriver will hold a name board at arrivals. Flight tracking included — no extra charge for delays. Book 48 hours in advance. Return transfers available at same rates. Journey time: approximately 45 minutes."},
    {"doc_type": "transport", "title": "Car Rental Through Hotel",
     "content": "Q: Can we rent a car?\nA: We partner with a reputable local car rental company:\n• Proton Saga (manual): RM100/day\n• Perodua Myvi (auto): RM120/day\n• Honda City (auto): RM180/day\n• Toyota Innova MPV: RM250/day\nRates include insurance. Delivery to hotel lobby, deposit via credit card. GPS/Waze recommended for navigation. International driving licence or Malaysian licence required. We can also arrange a driver for RM200/day."},
    {"doc_type": "transport", "title": "Public Transport Options Nearby",
     "content": "Q: How do we get around without a car?\nA: Public transport options:\n• Grab (ride-hailing): widely available, RM8–25 for town trips\n• Local bus: RM2–5, runs every 30 min (limited routes)\n• Hotel shuttle: free to town centre (10 AM, 2 PM, 6 PM)\n• Bicycle rental: from the hotel, first 2 hours free\n• Walking: town centre is 2 km (25 min scenic walk)\nFor island transfers, the jetty is 15 min by car. We can arrange all transport for you!"},

    # ═══════════════════════════════════════════════════════════════
    # SUSTAINABILITY (~8)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "sustainability", "title": "Green Initiatives at the Resort",
     "content": "Q: What sustainability practices do you follow?\nA: We're proud of our green journey:\n• Solar panels supply 30% of our electricity\n• Rainwater harvesting for garden irrigation\n• No single-use plastic (bamboo straws, glass bottles)\n• Towel and linen reuse programme\n• Local sourcing: 70% of food ingredients from within 50 km\n• EV charging stations (4 bays)\n• Composting kitchen waste for our herb garden\n• BREEAM-certified building design\nHelp us keep our planet beautiful!"},
    {"doc_type": "sustainability", "title": "Reef Conservation Programme",
     "content": "Q: Can we join any marine conservation activities?\nA: Yes! Our Reef Guardian Programme:\n• Coral planting experience: RM80/person (90 min)\n• Reef clean-up dive: RM50/person (must be PADI certified)\n• Marine biology talk: free, every Sunday 4 PM\n• Turtle nesting observation: seasonal (Jun–Sep), guided\nWe partner with the local marine park authority. 10% of your room rate during June–September supports reef restoration. Every guest can make a difference!"},
    {"doc_type": "sustainability", "title": "Community Support & Local Hiring",
     "content": "Q: Do you employ local people?\nA: We're deeply rooted in our community:\n• 85% of our 120 staff are from the local district\n• We partner with 15 local suppliers (farms, fishermen, artisans)\n• Scholarship programme for hospitality students (2 per year)\n• Monthly gotong-royong (community clean-up) with local kampung\n• Cultural performances by local artists every weekend\nWhen you stay with us, you support the whole community. Terima kasih!"},
]
