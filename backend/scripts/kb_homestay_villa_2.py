"""
Segment B — Homestay, Villa, Chalet, Inn Knowledge Base (Part 2)
Expanded: check-in/out, utility, bookings, safety, local experiences, seasonal
~200 entries
"""

DOCS = [
    # ═══════════════════════════════════════════════════════════════
    # CHECK-IN & CHECK-OUT — Private Properties (~30)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "checkin", "title": "Self Check-In — Smart Lock Instructions",
     "content": "Q: How does the smart lock work?\nA: Your door code will be sent via WhatsApp 2 hours before check-in. To enter: press the keypad, enter your 6-digit code, then press the lock button. The code is unique to your stay and automatically expires at check-out. If the keypad doesn't respond, hold the reset button for 3 seconds and try again. Battery backup lasts 8 months."},
    {"doc_type": "checkin", "title": "Check-In Time & Flexibility",
     "content": "Q: What time can we check in?\nA: Standard check-in is from 3 PM. Early check-in from 1 PM is available at RM50 (subject to availability). For arrivals before 1 PM, we can offer luggage storage while you explore. Late-night arrivals are welcome — the smart lock works 24/7. Just let us know your estimated arrival time so we can ensure everything's ready!"},
    {"doc_type": "checkin", "title": "Check-Out Time & Late Departure",
     "content": "Q: What time is check-out?\nA: Check-out is by 11 AM. Late check-out options:\n• Until 1 PM: RM50\n• Until 3 PM: RM100 (half-day rate)\n• Until 6 PM: Full day rate charged\nPlease request late check-out in advance. Ensure all windows are closed, aircon units switched off, and the door locked securely behind you. We appreciate your care for the property!"},
    {"doc_type": "checkin", "title": "Physical Key Handover Process",
     "content": "Q: Where do I pick up the key?\nA: For properties with physical keys, you'll meet our caretaker at the property entrance at your stated check-in time. They'll walk you through the house — water heater, Wi-Fi password, aircon remotes, and any quirks of the property. Allow 15 minutes for the orientation. If you're late, just WhatsApp us and we'll adjust!"},
    {"doc_type": "checkin", "title": "Early Arrival — Luggage Drop",
     "content": "Q: We're arriving at 10 AM but check-in is 3 PM. What do we do?\nA: No worries! You can drop your luggage at the property — our caretaker will meet you briefly to receive it. Then explore the area! We'll send you a message once the property is ready (usually by 2 PM on quiet days). Alternatively, early check-in at RM50 is available if no guest is checking out that morning."},
    {"doc_type": "checkin", "title": "Contactless Check-In Process",
     "content": "Q: Can we check in without meeting anyone?\nA: Absolutely! Our full contactless check-in includes:\n• Smart lock code sent 2 hours before\n• Wi-Fi password and house guide sent via PDF\n• Welcome pack on the kitchen counter (water, snacks)\n• WhatsApp support if you need anything\nPerfect for late arrivals or guests who prefer privacy. You're always just a message away from help!"},

    # ═══════════════════════════════════════════════════════════════
    # UTILITIES & TECHNICAL — Power, Wi-Fi, Water (~30)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "utilities", "title": "Wi-Fi Connection Details",
     "content": "Q: What's the Wi-Fi password?\nA: Wi-Fi details are on a card in the living room:\n• Network: [PropertyName]_WiFi\n• Password: sent via WhatsApp at check-in\nSpeed is typically 30–50 Mbps, sufficient for streaming and video calls. If you experience issues, try power-cycling the router (unplug 10 seconds, plug back in). For work-from-home guests, we recommend using the 5GHz band."},
    {"doc_type": "utilities", "title": "Hot Water — Gas vs Electric",
     "content": "Q: How does the hot water work?\nA: The water heater switch is in the bathroom — it's the switch with the red indicator near the shower. Turn it on 10 minutes before your shower. Some properties have instant gas heaters (hot water immediately). Please switch off after use to conserve energy. If hot water isn't working, check that the switch is ON and message us."},
    {"doc_type": "utilities", "title": "Aircon Operation & Tips",
     "content": "Q: How do I use the aircon?\nA: The aircon remote is on the bedside table. Quick tips:\n• Set to 24–25°C for comfort and efficiency\n• Use 'Cool' mode for daytime, 'Fan' or 'Dry' mode at night\n• Keep windows and doors closed when aircon is running\n• Clean filters are maintained between guests\nPlease switch off aircon when leaving the property — it helps the environment and keeps electricity costs manageable."},
    {"doc_type": "utilities", "title": "Power Outage / TNB Trip",
     "content": "Q: The electricity tripped / went off!\nA: Don't worry — this usually happens when too many high-power appliances run simultaneously. Check the MCB box (usually near the meter or kitchen entrance). Look for a switch that's DOWN and flip it UP. If it trips again, switch off some appliances first. If the entire neighbourhood is dark, it's a TNB outage — usually resolved within 1–2 hours."},
    {"doc_type": "utilities", "title": "TV & Streaming — How to Connect",
     "content": "Q: How do I use the TV? Can I watch Netflix?\nA: The smart TV supports YouTube, Netflix (sign in with your account), and local channels via MyTV. Use the TV remote to select your app from the home screen. HDMI cables are available if you want to connect your laptop. Please log out of all streaming accounts before check-out for your privacy!"},
    {"doc_type": "utilities", "title": "Gas Stove — Safety Instructions",
     "content": "Q: The gas stove won't light.\nA: For our gas stoves: turn the knob, press down, and hold while igniting (some have auto-ignition, others need a lighter). Hold for 5 seconds after the flame catches. If the gas tank is empty, a spare is usually behind the kitchen door — or message us and our caretaker will swap it (RM30, charged to stay). Never leave the stove unattended!"},

    # ═══════════════════════════════════════════════════════════════
    # BOOKINGS & PAYMENTS (~30)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "reservations", "title": "How to Book — Direct vs Platform",
     "content": "Q: How do I book your property?\nA: You can book through:\n• This WhatsApp chat (fastest!)\n• Airbnb / Booking.com (browser fees may apply)\n• Our website (best rates guaranteed)\n• Phone call\nDirect bookings save 10–15% vs OTA platforms and give you more flexibility. We'll confirm availability, send a quotation, and secure your dates with a deposit. Simple!"},
    {"doc_type": "reservations", "title": "Deposit & Payment Flow",
     "content": "Q: How does payment work?\nA: Our payment flow:\n1. Booking confirmation → 50% deposit within 24 hours\n2. Balance → due 7 days before check-in\n3. Security deposit → RM200 (refundable, returned within 48 hrs after check-out)\nPayment methods: bank transfer (Maybank/CIMB), Touch 'n Go eWallet, GrabPay, FPX. We'll send payment details via WhatsApp."},
    {"doc_type": "reservations", "title": "Receipt & Tax Invoice",
     "content": "Q: Can I get a tax invoice for my stay?\nA: Yes! We can provide a proper tax invoice with:\n• Property details and SST registration number\n• Guest name and dates of stay\n• Itemised charges\nJust let us know at check-out (or after) and we'll email it to you within 24 hours. For corporate guests, we can address it to your company with PO number."},
    {"doc_type": "reservations", "title": "Calendar Availability Check",
     "content": "Q: How do I check if dates are available?\nA: Just message us your preferred dates and number of guests right here! We'll check our real-time availability and respond within 30 minutes during operating hours. For faster checking, visit our Airbnb/Booking.com listing where the calendar is always up-to-date. We'll always try to accommodate your preferred dates!"},
    {"doc_type": "reservations", "title": "Minimum Stay Requirements",
     "content": "Q: Is there a minimum stay?\nA: Our minimum stay varies:\n• Weekdays (Sun–Thu): 1 night minimum\n• Weekends (Fri–Sat): 2 nights minimum\n• Public holidays: 2–3 nights minimum\n• Festive seasons (Raya, CNY, year-end): 3 nights minimum\nFor special circumstances, we may allow exceptions — just ask! We're always flexible when we can be."},

    # ═══════════════════════════════════════════════════════════════
    # SAFETY & EMERGENCY — Private Properties (~25)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "safety", "title": "Fire Safety in Homestay",
     "content": "Q: What fire safety measures are in place?\nA: Each property has:\n• Smoke detector in every bedroom and kitchen\n• Fire extinguisher (kitchen area)\n• Emergency exit map on the main door\n• Emergency contact numbers on the fridge\nIn case of fire: evacuate immediately, close doors behind you, call 994 (Bomba/Fire). Do not use the property fire extinguisher unless it's a very small contained fire. Safety first, always!"},
    {"doc_type": "safety", "title": "First Aid Kit Location",
     "content": "Q: Do you have a first aid kit?\nA: Yes — there's a basic first aid kit in the kitchen area (usually top shelf or drawer near the fridge). Contains: plasters, antiseptic wipes, bandages, paracetamol, allergy tablets, and a digital thermometer. For anything more serious, the nearest clinic is 10 minutes by car. For emergencies, dial 999."},
    {"doc_type": "safety", "title": "Flood / Heavy Rain Advisory",
     "content": "Q: Does the area flood during heavy rain?\nA: Our properties are positioned above flood-risk zones. During extended heavy rainfall:\n• Keep ground-floor windows closed\n• Don't park in low-lying areas\n• Check our WhatsApp for weather advisories\n• Road conditions may be affected — drive carefully\nIn 10+ years of operation, none of our properties have experienced flooding. But we monitor conditions closely just in case."},
    {"doc_type": "safety", "title": "Snake / Wildlife Encounter",
     "content": "Q: What if we see a snake?\nA: It's rare but possible in jungle/nature properties. If you spot one:\n• Do NOT approach or try to catch it\n• Move away slowly\n• Call our emergency line immediately\n• Keep children and pets inside\nOur caretaker or local wildlife response team will handle it. 99% of snakes encountered are harmless, but we take every sighting seriously."},

    # ═══════════════════════════════════════════════════════════════
    # LOCAL EXPERIENCES & CULTURAL (~30)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "local_area", "title": "Kampung Tour — Village Experience",
     "content": "Q: Can we visit a traditional Malay village?\nA: Absolutely! Our kampung tour includes:\n• Traditional Malay house visit (with host family)\n• Kuih-making demonstration\n• Rubber tapping experience\n• Paddy field walk (seasonal)\n• Fresh coconut drink under the trees\nRM80/person, 3 hours, includes transport. This is one of the most authentic cultural experiences you can have in Malaysia. Minimum 2 pax."},
    {"doc_type": "local_area", "title": "Fresh Seafood Market Visit",
     "content": "Q: Where can we buy fresh seafood to cook?\nA: The local fish market operates daily 6–10 AM by the jetty (15 min drive). You'll find: prawns, squid, crab, fish (siakap, kembung, tenggiri), and shellfish — all caught the same morning. Prices are significantly cheaper than supermarkets. Our tip: arrive before 7 AM for the best selection. We can share the GPS location!"},
    {"doc_type": "local_area", "title": "Local Fruit Farm Visit",
     "content": "Q: Are there any fruit farms we can visit?\nA: Yes! Several local fruit farms offer guided tours:\n• Durian orchards (June–August): RM50/person, all-you-can-eat session\n• Tropical fruit farm: RM30/person, includes tasting of 8 fruits\n• Coconut plantation: free entry, fresh coconut RM5\nSeasonal availability varies. We can arrange transport and guide. The durian experience is legendary — bring wet wipes!"},
    {"doc_type": "local_area", "title": "Firefly Tour — Evening Activity",
     "content": "Q: I heard about firefly tours. Can you arrange one?\nA: Yes — the firefly boat tour is magical! Operates nightly 7:30–9:30 PM along the river:\n• Boat ride along mangrove-lined river\n• Thousands of synchronised fireflies\n• Silent electric boat for minimal disturbance\n• RM50/adult, RM30/child\n• 45-minute experience\nBest during new moon (darker = more visible). We arrange transport. It's genuinely one of Malaysia's natural wonders!"},
    {"doc_type": "local_area", "title": "Traditional Fishing Experience",
     "content": "Q: Can we go fishing?\nA: Yes! Options:\n• Boat fishing (deep sea): RM300/boat (up to 6 pax), 4 hours with guide and gear\n• River/lake fishing: RM50/person, rod and bait included\n• Beach fishing: free! (we can lend rods)\n• Catch-and-cook: bring your catch to a local restaurant and they'll cook it for RM15/fish\nBest times: early morning or late afternoon. Our caretaker knows the hottest spots!"},
    {"doc_type": "local_area", "title": "Morning Market (Pasar Pagi) Guide",
     "content": "Q: What's the morning market like?\nA: The pasar pagi (morning market) operates daily 6–9 AM, 10 minutes' drive:\n• Fresh vegetables, fruits, and herbs from local farms\n• Kuih-muih (traditional Malay snacks) — try the kuih seri muka and onde-onde!\n• Nasi lemak bungkus (RM2!) — breakfast of champions\n• Fresh juices and air kelapa (coconut water)\n• Household items and local produce\nBring cash (RM30–50 is enough). It's a sensory feast!"},

    # ═══════════════════════════════════════════════════════════════
    # HOST PERKS & REPEAT GUESTS (~15)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "loyalty", "title": "Repeat Guest Discount",
     "content": "Q: We loved it! Do returning guests get a discount?\nA: We love repeat guests! Your loyalty is rewarded:\n• 2nd stay: 10% off\n• 3rd stay: 15% off\n• 5+ stays: 20% off + priority booking during peak season\nWe keep a record of all our guests, so just mention your previous stays when booking. We also maintain your room preferences and special requests. Welcome back always feels extra special!"},
    {"doc_type": "loyalty", "title": "Referral Bonus",
     "content": "Q: Can I recommend you to friends?\nA: Please do! We have a referral programme:\n• For every friend who books a confirmed stay, YOU receive RM50 off your next booking\n• Your friend also gets 5% off their first stay\n• No limit on referrals!\nJust ask your friend to mention your name when booking. Word-of-mouth is our best marketing — we value every recommendation. Thank you!"},
]
