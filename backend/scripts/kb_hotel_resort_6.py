"""
Segment A — Hotel & Resort Knowledge Base (Part 6)
Categories: Policies, Loyalty, Accessibility, Business/MICE, Housekeeping, Multilingual
~50 entries
"""

DOCS = [
    # ═══════════════════════════════════════════════════════════════
    # POLICIES — Extended (~15)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "policies", "title": "Cancellation Policy — Standard",
     "content": "Q: What is your cancellation policy?\nA: Our standard cancellation policy:\n• Flexible rate: Free cancellation up to 48 hours before check-in\n• Non-refundable rate: No cancellation or changes (discounted rate reflects this)\n• Group bookings (10+ rooms): 14 days notice required\n• Peak season: 7 days notice required\nCancellations within the penalty window are charged 1 night's stay. We understand plans change — we'll always try to accommodate!"},
    {"doc_type": "policies", "title": "Cancellation Policy — Special Events",
     "content": "Q: What if I need to cancel my Hari Raya / CNY booking?\nA: Festive season bookings have a special policy:\n• More than 14 days before: Full refund\n• 7–14 days: 50% refund or free date change (subject to availability)\n• Less than 7 days: No refund\nWe recommend booking with our flexible rate if your plans might change. Travel insurance is also available through our partners."},
    {"doc_type": "policies", "title": "Pet Policy",
     "content": "Q: Can I bring my pet?\nA: We understand pets are family! However:\n• Indoor pets: not permitted in hotel rooms or restaurants\n• Service animals: always welcome (documentation may be requested)\n• Pet-friendly homestays: we can recommend partner properties that welcome pets\nWe're exploring a pet-friendly wing for the future! For now, we can recommend a trusted pet hotel (RM80/night) 15 minutes from us."},
    {"doc_type": "policies", "title": "Damage & Security Deposit",
     "content": "Q: What happens if something gets damaged in the room?\nA: Minor wear and tear is expected and not charged. For significant damage:\n• We document with photos and contact you within 24 hours\n• A fair repair/replacement cost is charged (receipts provided)\n• Pre-auth holds on credit cards are used as security (released within 7 days if no damage)\n• Our goal is fairness — accidents happen, and we handle them kindly."},
    {"doc_type": "policies", "title": "Guest Age Policy",
     "content": "Q: What is the minimum check-in age?\nA: The primary guest checking in must be at least 18 years old with a valid government-issued ID (MyKad, passport, or driving licence). For groups of under-18s, a parent/guardian must be the registered guest and present at check-in. All guests aged 12 and above are counted as adults for occupancy purposes."},
    {"doc_type": "policies", "title": "Photography & Drone Policy",
     "content": "Q: Can I fly my drone at the resort?\nA: Recreational drone flights:\n• Not permitted within 200m of the building/pool areas\n• Beach and garden flights require prior permission from management\n• Commercial/professional shoots: require written approval + RM500 permit fee\n• Malaysia CAAM drone regulations must be followed\nWe want everyone to enjoy their stay without noise/privacy concerns. If you need drone footage, let's discuss — we may help arrange it!"},

    # ═══════════════════════════════════════════════════════════════
    # LOYALTY PROGRAMME (~10)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "loyalty", "title": "Loyalty Programme — Registration",
     "content": "Q: How do I join the loyalty programme?\nA: Our Grand Rewards programme is free to join!\n• Register online at grandhorizon.com/rewards or at the front desk\n• Earn 10 points per RM1 spent on room, dining, and spa\n• Points can be redeemed for free nights, upgrades, and dining credits\n• No expiry date for active members (at least 1 stay per 24 months)\n• Instant RM50 welcome credit on first stay after joining!"},
    {"doc_type": "loyalty", "title": "Loyalty Tiers & Benefits",
     "content": "Q: What are the loyalty tier benefits?\nA: Our loyalty tiers:\n• Silver (0–4,999 points): 10% off dining, birthday reward, early check-in request\n• Gold (5,000–14,999): 15% off dining, room upgrade priority, late check-out guaranteed\n• Platinum (15,000+): 20% off everything, complimentary breakfast, suite upgrade, personal concierge\nTiers reset annually based on calendar year earnings. Every tier gets our newsletter with exclusive flash deals."},
    {"doc_type": "loyalty", "title": "Points Redemption Guide",
     "content": "Q: How do I use my loyalty points?\nA: Redemption options:\n• Free night (Deluxe): 5,000 points\n• Free night (Suite): 10,000 points\n• Room upgrade: 2,000 points\n• Dining credit (RM100): 1,500 points\n• Spa treatment credit (RM200): 2,500 points\n• Airport transfer: 1,200 points\nRedeem at booking or at the front desk. Points cannot be converted to cash. Combine points + cash for partial redemptions too!"},

    # ═══════════════════════════════════════════════════════════════
    # ACCESSIBILITY (~8)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "accessibility", "title": "Wheelchair Access — Full Details",
     "content": "Q: Is the entire resort wheelchair accessible?\nA: We strive for full accessibility:\n• Lobby, restaurants, and pool area: fully wheelchair accessible\n• Ramp access to all public areas\n• Accessible rooms available (ground floor, wider doors, roll-in shower)\n• Pool hoist available on request\n• Wheelchair rental: complimentary (limited units)\n• Parking: 2 designated wheelchair bays near entrance\nPlease inform us at booking so we can prepare everything for your comfort."},
    {"doc_type": "accessibility", "title": "Hearing/Visual Impairment Support",
     "content": "Q: What support is available for hearing-impaired guests?\nA: We offer:\n• Visual fire alarm systems in accessible rooms\n• Text-based communication via WhatsApp (this channel!)\n• Written check-in instructions available\n• TTY compatible front desk phone\n• Assistive listening devices for meetings (on request)\nFor visually impaired guests: large-print menus, tactile room number plates, and guide-dog friendly throughout the property."},

    # ═══════════════════════════════════════════════════════════════
    # BUSINESS & MICE (~10)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "business", "title": "Meeting Room Options",
     "content": "Q: What meeting rooms do you have?\nA: Our business facilities:\n• Boardroom (12 pax): RM500/half-day, RM800/full-day\n• Meeting Room A (30 pax): RM800/half-day, RM1,200/full-day\n• Meeting Room B (50 pax): RM1,200/half-day, RM1,800/full-day\n• Grand Ballroom (300 pax): from RM5,000/day\nAll include: projector, whiteboard, Wi-Fi, water, and stationery. Coffee breaks and lunch can be added from RM35/pax."},
    {"doc_type": "business", "title": "Corporate Retreat Package",
     "content": "Q: Can you put together a team-building retreat?\nA: Our Corporate Retreat Package (min 20 pax):\n• 2D1N or 3D2N packages available\n• Accommodation, meals, meeting room, and team building activities\n• Activities: beach Olympics, cooking challenge, treasure hunt, raft building\n• AV setup, printing, and secretarial support included\n• From RM350/pax (2D1N) or RM600/pax (3D2N)\nOur events team creates customised itineraries. We've hosted retreats for companies from 15 to 150 people!"},
    {"doc_type": "business", "title": "Business Centre Services",
     "content": "Q: Do you have a business centre?\nA: Our 24-hour Business Centre (Level 2) offers:\n• Workstations with high-speed wired internet\n• Printing: RM0.50/page (B&W), RM2/page (colour)\n• Scanning and faxing services\n• Meeting pods (2–4 pax, first come first served)\n• Complimentary coffee and tea\n• Stationery supplies\nIdeal for quick emails, printing boarding passes, or working between sessions. Open to all in-house guests."},

    # ═══════════════════════════════════════════════════════════════
    # HOUSEKEEPING (~6)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "housekeeping", "title": "Daily Housekeeping Schedule",
     "content": "Q: When does housekeeping come?\nA: Daily housekeeping is between 9 AM–3 PM:\n• Main service: bed-making, bathroom clean, towel replacement, waste removal, minibar restock\n• Turndown service (Suites only): 6–8 PM\n• DND (Do Not Disturb): place the card on your door handle; we'll check again later\n• Extra housekeeping request: call extension 0 or message us here\nWe use eco-friendly cleaning products and offer a towel/linen reuse programme."},
    {"doc_type": "housekeeping", "title": "Extra Amenities Request",
     "content": "Q: Can I get extra towels and toiletries?\nA: Of course! Just ask via:\n• Room phone: dial 0 for housekeeping\n• WhatsApp: message us here\nAvailable items: towels, bathrobes, slippers, shampoo, conditioner, body wash, dental kit, sewing kit, shoe shine kit, shower cap, comb, cotton buds. Iron and ironing board available on loan. Delivery within 15 minutes!"},
    {"doc_type": "housekeeping", "title": "Eco-Linen Programme",
     "content": "Q: Do you change sheets every day?\nA: As part of our green initiative:\n• Sheets are changed every 3 days (or upon request)\n• Towels: hung up = reuse; on floor = replace\n• Fresh pillowcases daily\nGuests who participate in our Eco-Linen Programme receive a RM10 dining credit per night. It's a small step that makes a big environmental difference. Thank you for helping us save water and energy!"},
]
