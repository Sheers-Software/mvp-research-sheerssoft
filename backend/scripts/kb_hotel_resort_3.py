"""
Segment A — Hotel & Resort Knowledge Base (Part 3)
Categories: Complaints, Concierge, Weddings, Kids, Transport, Policies, Business, Loyalty,
            Accessibility, Safety, Pets, Sustainability, Housekeeping
~250 entries
"""

DOCS = [
    # ═══════════════════════════════════════════════════════════════
    # COMPLAINTS & SERVICE RECOVERY (~40)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "complaints", "title": "Air Conditioning Not Working",
     "content": "Q: My aircond is not working!\nA: I sincerely apologise for the discomfort. I'll alert our maintenance team immediately — they'll be at your room within 15 minutes. In the meantime, I can have a portable fan sent up or arrange a temporary room move if you'd prefer. Your comfort is our top priority."},
    {"doc_type": "complaints", "title": "Room Not Clean on Arrival",
     "content": "Q: My room wasn't properly cleaned when I arrived.\nA: I'm truly sorry about this — that's not the experience we want for you. I'll have our housekeeping supervisor attend to your room right away with a full re-clean. As an apology, please allow us to offer you a complimentary drink at the Poolside Bar while we prepare your room. This shouldn't have happened and I appreciate your patience."},
    {"doc_type": "complaints", "title": "Noisy Neighbours / Room",
     "content": "Q: The room next door is very noisy.\nA: I understand how frustrating that can be. Let me contact the guests immediately to request they keep the noise down. If the issue persists, I can arrange a room change to a quieter floor at no extra charge. Your rest is important to us — please don't hesitate to let me know if it continues."},
    {"doc_type": "complaints", "title": "Hot Water Issue",
     "content": "Q: There's no hot water in my shower!\nA: I apologise for this inconvenience. I'll dispatch our engineering team to your room immediately. While they work on it, I can offer you access to our spa shower facilities, which have unlimited hot water. This should be resolved within 30 minutes — shall I call your room to confirm?"},
    {"doc_type": "complaints", "title": "Food Quality Complaint",
     "content": "Q: The food at dinner was cold and underwhelming.\nA: I'm sorry to hear that — our kitchen team takes great pride in their work and this falls short of our standards. Please allow me to arrange a complimentary re-preparation of your meal or an alternative dish from our menu. I'll also pass your feedback directly to our Head Chef. What would you prefer?"},
    {"doc_type": "complaints", "title": "Slow Service Complaint",
     "content": "Q: We waited 45 minutes for our food.\nA: That's unacceptable and I sincerely apologise. During peak hours we should still deliver within 20–25 minutes. I'll follow up with the restaurant manager right away. As a gesture of apology, please allow us to offer a complimentary dessert or drink for your table. Thank you for your patience and feedback."},
    {"doc_type": "complaints", "title": "Wi-Fi Not Working",
     "content": "Q: The Wi-Fi in my room isn't working.\nA: I'm sorry about that — let me help. First, could you try disconnecting and reconnecting to 'GrandHorizon_WiFi'? If that doesn't work, our IT team can reset your room's access point remotely. This usually resolves it within 5 minutes. If you need urgent internet, our Business Centre has a wired connection available 24/7."},
    {"doc_type": "complaints", "title": "Overcharged on Bill",
     "content": "Q: I think there's an error on my bill.\nA: I understand your concern and I'd like to resolve this right away. Could you share which items look incorrect? I'll cross-check with our records and if there's any discrepancy, we'll correct it immediately. Guest satisfaction is more important to us than any billing issue — we'll make this right."},
    {"doc_type": "complaints", "title": "TV / In-Room Entertainment Issue",
     "content": "Q: The TV in my room isn't working.\nA: I apologise for the inconvenience. Our in-room entertainment team can troubleshoot remotely — this usually takes 5 minutes. If a physical visit is needed, they'll be at your room within 15 minutes. Would you like me to send someone now?"},
    {"doc_type": "complaints", "title": "Insect / Pest in Room",
     "content": "Q: There's a cockroach in my room!\nA: I'm truly sorry — that must be very unpleasant. I'll send housekeeping immediately to address it. If you'd prefer, I can move you to a different room right away at no charge. Our pest control protocol includes regular preventive treatments, and I'll ensure an inspection is carried out on your floor. Deeply sorry for the experience."},
    {"doc_type": "complaints", "title": "General Service Recovery Protocol",
     "content": "Q: I'm not happy with my stay overall.\nA: I appreciate you sharing this with me — your feedback genuinely helps us improve. Could you tell me what specifically wasn't up to standard? I'd like to address each issue directly and ensure your remaining stay is much better. Our management team will also reach out to discuss how we can make things right."},
    {"doc_type": "complaints", "title": "Lost Luggage at Hotel",
     "content": "Q: The hotel porter lost one of my bags!\nA: I completely understand your concern and I'll treat this as our highest priority. I'll immediately alert our duty manager and security team. Could you describe the bag? We'll conduct a thorough search and review CCTV footage. We maintain a detailed log of all luggage handling. I'll keep you updated every 30 minutes until this is resolved."},
    {"doc_type": "complaints", "title": "Construction Noise Complaint",
     "content": "Q: There's construction noise and nobody told me about it.\nA: I sincerely apologise for not informing you beforehand. Maintenance work is scheduled only between 9 AM–5 PM weekdays. Let me move you to a room further from the affected area immediately. I'll also apply a 20% discount on your current night's stay as an apology. This should have been communicated at check-in."},

    # ═══════════════════════════════════════════════════════════════
    # CONCIERGE — General Guest Services (~50)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "concierge", "title": "Airport Transfer",
     "content": "Q: Can you arrange airport pickup?\nA: Absolutely! Our airport transfer service includes:\n• Sedan (1–3 pax): RM120 one-way\n• MPV (4–6 pax): RM180 one-way\n• Van (7–12 pax): RM280 one-way\nYour driver will be waiting at the arrival hall with a name card. Please share your flight details and I'll arrange everything."},
    {"doc_type": "concierge", "title": "Taxi & Ride-Hailing",
     "content": "Q: How do I get a taxi?\nA: Our concierge can call a hotel taxi (metered or fixed rate) or you can use Grab directly from the app. The hotel entrance is a popular pickup point. For longer distances, our hotel car service offers fixed rates — often more comfortable and reliable than ride-hailing. Ask us for a quote anytime!"},
    {"doc_type": "concierge", "title": "Car Rental",
     "content": "Q: Can I rent a car?\nA: We work with two reputable car rental companies that offer drop-off and pick-up at the hotel. Rates from RM120/day for a compact car (Myvi/Vios) to RM350/day for an SUV. International driving permits accepted. Full insurance included. Shall I request a quotation for your dates?"},
    {"doc_type": "concierge", "title": "Baby Cot & Children's Amenities",
     "content": "Q: Can you provide a baby cot?\nA: Of course! Complimentary baby cots, bed guards, bottle warmers, and baby bath tubs are available on request. Just let us know at booking or upon arrival. We also have a baby-sitting referral service (RM50/hour, advance booking required) through a vetted childcare provider."},
    {"doc_type": "concierge", "title": "SIM Card & Mobile Data",
     "content": "Q: Where can I buy a local SIM card?\nA: Our gift shop sells prepaid SIM cards from Celcom and Digi (from RM30, includes data). Our front desk can help with registration (passport required for foreign guests). With complimentary Wi-Fi throughout the property, you may only need data for off-site excursions."},
    {"doc_type": "concierge", "title": "Postal & Courier Service",
     "content": "Q: Can I send a parcel or postcard from the hotel?\nA: The front desk can arrange Pos Malaysia and courier services (Pos Laju, DHL, FedEx). Stamps and postcards are available at the gift shop. International courier takes 3–5 business days. We'll handle the packaging and shipment for you — just drop it off at the front desk."},
    {"doc_type": "concierge", "title": "Florist & Special Arrangements",
     "content": "Q: Can you arrange flowers for my wife's birthday?\nA: What a lovely gesture! We can arrange beautiful bouquets from RM80 (mixed blooms) to RM250 (premium roses). With 24 hours' notice, we can have them placed in your room with a personalised card. Balloons and special room decorations are also available from RM50. She'll be delighted!"},
    {"doc_type": "concierge", "title": "Wake-Up Call Service",
     "content": "Q: Can I get a wake-up call?\nA: Yes! You can set a wake-up call through the in-room phone (press *7 followed by the time) or simply let us know and we'll arrange it from the front desk. We'll call your room at the requested time. For important commitments, we recommend setting a backup alarm as well."},
    {"doc_type": "concierge", "title": "Tour & Activity Booking",
     "content": "Q: Can you help me plan my day trips?\nA: That's exactly what our concierge team is here for! Tell me your interests — nature, culture, adventure, food, shopping — and I'll put together a personalised itinerary. We can arrange transport, entries, guides, and packed meals. We know all the best spots, including hidden gems off the tourist trail!"},
    {"doc_type": "concierge", "title": "Umbrella Loan",
     "content": "Q: It's raining — do you have umbrellas?\nA: Of course! Complimentary umbrellas are available from the front desk and at all exit points. If you're heading out for the day, please feel free to take one. We also have complimentary rain ponchos at the concierge desk. Malaysia's tropical showers are usually brief — sunshine returns quickly!"},
    {"doc_type": "concierge", "title": "Local Area Recommendations",
     "content": "Q: What's nearby to see or do?\nA: There's so much! Within 30 minutes:\n• Mangrove nature reserve (boat tour, RM50)\n• Local fishing village (authentic seafood lunch)\n• Mountain viewpoint (stunning sunrise trek)\n• Artisan pottery village\n• Fresh fruit farms\nI can arrange transport and bookings for all of these. What catches your eye?"},
    {"doc_type": "concierge", "title": "Pharmacy & Medical Needs",
     "content": "Q: Is there a pharmacy nearby?\nA: The nearest pharmacy (Guardian) is a 10-minute drive in the town centre. Our gift shop stocks basic medications (paracetamol, allergy tablets, plasters, motion sickness pills). For urgent needs, our on-call doctor can prescribe and deliver medication. Just call extension 0."},

    # ═══════════════════════════════════════════════════════════════
    # WEDDINGS & EVENTS (~50)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "weddings", "title": "Wedding Venue Options",
     "content": "Q: What venues do you have for weddings?\nA: Congratulations! We offer several stunning options:\n• Grand Ballroom — up to 300 pax, elegant indoor setting\n• Garden Pavilion — up to 150 pax, tropical garden ceremony\n• Beachfront Terrace — up to 100 pax, sunset ceremony\n• Poolside Deck — up to 80 pax, intimate cocktail reception\nEach has its own unique charm. Would you like to visit for a site tour?"},
    {"doc_type": "weddings", "title": "Wedding Package Details",
     "content": "Q: What's included in your wedding packages?\nA: Our packages (from RM15,000 for 100 pax) include:\n• 8-course Chinese dinner OR international buffet\n• Basic floral décor and centre pieces\n• Sound system and microphone\n• Complimentary bridal suite (1 night)\n• Cake cutting ceremony setup\n• Dedicated event coordinator\nCustomisations are endless — we'll tailor everything to your dream!"},
    {"doc_type": "weddings", "title": "Malay Wedding Package",
     "content": "Q: Do you cater for Malay weddings?\nA: Absolutely! Our Malay wedding packages include pelamin setup, complete with bunga manggar, kompang troupe arrangement, and a certified halal menu. We can coordinate with your wedding planner or provide our own team. Nikah ceremony arrangements at the resort surau are also available. From RM20,000 for 200 pax."},
    {"doc_type": "weddings", "title": "Chinese Banquet Wedding",
     "content": "Q: Can you do a Chinese banquet wedding?\nA: Yes! Our Grand Ballroom is perfect for Chinese wedding banquets. 10-course dinner from RM1,500/table (10 pax). We accommodate ang pow boxes, tea ceremony setup, and a dedicated emcee area. Chinese wedding coordinator available. Our kitchen is experienced with traditional multi-course banquet menus."},
    {"doc_type": "weddings", "title": "Indian Wedding Package",
     "content": "Q: Do you accommodate Hindu wedding ceremonies?\nA: Of course! We can arrangement mandap setup, vegetarian menu options, and coordination with your priest for the ceremony. Our Garden Pavilion is especially beautiful for outdoor ceremonies. Packages from RM18,000 for 150 pax. We also accommodate Sangeet and Mehndi pre-wedding events."},
    {"doc_type": "weddings", "title": "Group Room Block for Weddings",
     "content": "Q: Can you block rooms for our wedding guests?\nA: Certainly! For wedding bookings, we offer a room block at 15–20% off standard rates. We'll create a custom booking code that your guests can use. Minimum 10 rooms to qualify. The bridal couple receives a complimentary suite upgrade. Shuttle coordination between venue and rooms is included."},
    {"doc_type": "weddings", "title": "Corporate Event & Conference",
     "content": "Q: Can you host a corporate conference for 200 people?\nA: Absolutely! Our Grand Ballroom accommodates up to 300 in theatre-style seating. Conference packages from RM120/person/day include AV equipment, Wi-Fi, stationery, coffee breaks, and lunch. We can arrange team-building activities, gala dinners, and accommodation packages. Our events team will manage every detail."},
    {"doc_type": "weddings", "title": "Birthday Party Venue",
     "content": "Q: Can I hold a birthday party at the hotel?\nA: Yes! We have several options depending on your party size:\n• Poolside Deck (up to 40 pax): from RM1,500\n• Garden Terrace (up to 60 pax): from RM2,500\n• Private Dining Room (up to 20 pax): from RM800\nIncludes venue, basic décor, and F&B. We can arrange entertainment, cakes, and themed decorations too!"},

    # ═══════════════════════════════════════════════════════════════
    # KIDS & FAMILY (~40)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "kids", "title": "Family-Friendly Property Overview",
     "content": "Q: Is this hotel suitable for families with young children?\nA: Absolutely! We're a family-friendly resort with: Kids' Club (ages 4–12), children's pool with water features, baby cots and bath tubs on request, kids' menu at all restaurants, and family-sized rooms. Many of our team are parents themselves — we understand what travelling with little ones requires!"},
    {"doc_type": "kids", "title": "Kids' Club Details",
     "content": "Q: Tell me about your Kids' Club.\nA: Our Little Explorers Kids' Club operates daily 9 AM–5 PM for ages 4–12. It's supervised by our trained childcare team. Activities include arts & crafts, treasure hunts, sandcastle building, movie screenings, cookie decorating, and nature discovery walks. It's complimentary for in-house guests. Drop-off and pick-up anytime!"},
    {"doc_type": "kids", "title": "Baby Amenities Available",
     "content": "Q: What baby amenities do you provide?\nA: We provide complimentary:\n• Baby cot with linen\n• Baby bath tub\n• Bottle warmer and steriliser\n• Baby high chair (at restaurants)\n• Bed guard rails\n• Baby monitor (on request)\nAll items are professionally sanitised between uses. Just let us know at booking so everything is ready in your room!"},
    {"doc_type": "kids", "title": "Babysitting Service",
     "content": "Q: Do you offer babysitting?\nA: We can arrange a vetted babysitter through our trusted childcare partner. Rate is RM50/hour (minimum 3 hours). Sitters are experienced, certified, and carry a valid first-aid qualification. Please book at least 24 hours in advance through the concierge. Available for children aged 1 year and above."},
    {"doc_type": "kids", "title": "Child-Proofing Room",
     "content": "Q: Can you child-proof our room?\nA: Of course! We have a child-proofing kit that includes socket covers, corner guards, door stoppers, and cabinet locks. We can also remove the minibar contents if you'd prefer. Just let housekeeping know and they'll set everything up before your arrival. Safety first!"},
    {"doc_type": "kids", "title": "Teens Activities",
     "content": "Q: What's there for teenagers to do?\nA: Teens love our: games room (PS5, pool table, foosball), water sports centre, bicycle trails, ATV adventures (age 16+), cooking classes, and beach volleyball. We also have a teen lounge with bean bags, board games, and a big-screen gaming setup. The island hopping tour is consistently rated 'awesome' by our teenage guests!"},

    # ═══════════════════════════════════════════════════════════════
    # TRANSPORT & DIRECTIONS (~40)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "transport", "title": "Getting to the Resort",
     "content": "Q: How do I get to your hotel?\nA: We're located 45 minutes from the nearest airport. Getting here:\n• Airport transfer (pre-arranged): RM120–280\n• Grab/taxi: approx RM80–100\n• Self-drive: GPS coordinates provided upon booking\n• Bus: available to nearby town, then 15-min taxi\nWe recommend the airport transfer — meet & greet, air-conditioned, hassle-free!"},
    {"doc_type": "transport", "title": "Hotel Shuttle Service",
     "content": "Q: Do you have a shuttle?\nA: Yes! We operate a complimentary shuttle to the town centre:\n• Departures: 9 AM, 12 PM, 3 PM, 7 PM\n• Returns: 10 AM, 1 PM, 5 PM, 9 PM\nThe ride is 15 minutes each way. Seats are first come, first served (max 12 pax). Private shuttle can be arranged at RM50/trip. Please book at the front desk."},
    {"doc_type": "transport", "title": "Self-Drive Parking & Navigation",
     "content": "Q: We're driving — any parking tips?\nA: Complimentary parking is available with over 150 spaces. Our GPS coordinates are: [coordinates sent on booking]. The last 5 km is along a scenic coastal road — well-signposted. We recommend Waze for the most accurate navigation. Covered parking is available on a first-come basis."},
    {"doc_type": "transport", "title": "Nearby Petrol Station",
     "content": "Q: Where's the nearest petrol station?\nA: The nearest Petronas station is 5 minutes drive towards town. There's also a Shell station in the town centre (15 minutes). Both are 24-hour stations. If you need an emergency top-up, our maintenance team can assist with a small supply from our backup generator fuel — just ask!"},
    {"doc_type": "transport", "title": "Boat & Ferry Transfers",
     "content": "Q: Do you arrange boat transfers?\nA: Yes! For island-based excursions or nearby jetty transfers, we arrange:\n• Speedboat: RM200/trip (up to 6 pax)\n• Traditional boat: RM100/trip (up to 4 pax)\n• Glass-bottom boat tour: RM80/person\nAll boats are licensed and equipped with life jackets. Departure from our private jetty."},

    # ═══════════════════════════════════════════════════════════════
    # POLICIES — General (~50)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "policies", "title": "Pet Policy",
     "content": "Q: Can I bring my pet?\nA: We love pets! We accept well-behaved dogs and cats (maximum 10 kg) in designated pet-friendly rooms on the ground floor. A pet fee of RM100/night applies. We provide pet beds, bowls, and treats. Pets must be leashed in public areas. Our garden has a small designated off-leash area. Please inform us at booking."},
    {"doc_type": "policies", "title": "No-Show Policy",
     "content": "Q: What happens if I don't show up?\nA: If you don't check in on your arrival date without prior notice, the full stay amount will be charged. We recommend cancelling at least 48 hours before if your plans change — full refund guaranteed. If you're running late, just let us know and we'll hold your room."},
    {"doc_type": "policies", "title": "Damage & Deposit Policy",
     "content": "Q: Do you charge a security deposit?\nA: We place a pre-authorisation hold of RM200 on your credit card at check-in for incidentals (minibar, additional charges). This is released upon check-out. For cash-paying guests, a RM300 cash deposit is required. Any damage to property will be assessed and charged accordingly."},
    {"doc_type": "policies", "title": "Prohibited Items",
     "content": "Q: Are there items I can't bring?\nA: For safety, the following are not permitted: cooking appliances (rice cookers, hotplates), durians (sorry — strong odour policy!), flammable materials, weapons, and illegal substances. Smoking is only permitted in designated areas. We appreciate your cooperation in keeping the resort safe and pleasant for everyone."},
    {"doc_type": "policies", "title": "Durian Policy",
     "content": "Q: Can I eat durian in my room?\nA: We understand the love for durian — it's the King of Fruits! However, due to the strong and lingering aroma, durians are not permitted inside rooms or indoor areas. We have a designated outdoor durian corner near the garden where you can enjoy it to your heart's content. We even provide wet wipes!"},
    {"doc_type": "policies", "title": "Data Privacy & Guest Records",
     "content": "Q: How do you handle my personal data?\nA: We take privacy seriously. Your personal data is protected under the Personal Data Protection Act 2010 (PDPA). Data is used solely for your reservation and hotel services. We do not share information with third parties without consent. You may request data access or deletion through our front desk."},

    # ═══════════════════════════════════════════════════════════════
    # BUSINESS & MEETINGS (~20)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "business", "title": "Business Traveller Amenities",
     "content": "Q: Do you cater for business travellers?\nA: Absolutely! Business guests enjoy: 24/7 Business Centre, printing/scanning services, high-speed Wi-Fi, meeting room access (from RM200/half-day), express laundry, late check-out priority, and a dedicated workspace in Executive rooms. Many guests find our lobby lounge an excellent informal meeting spot."},
    {"doc_type": "business", "title": "Team Building Activities",
     "content": "Q: Can you arrange team building for our company?\nA: We'd love to! Options include:\n• Beach Olympics (half-day, from RM80/pax)\n• Jungle Trekking Challenge (full-day, from RM150/pax)\n• Cooking Team Challenge (half-day, from RM120/pax)\n• Amazing Race through local village (full-day, from RM100/pax)\nAll include facilitators, materials, and refreshments. We can customise for any group size!"},
    {"doc_type": "business", "title": "Printing & Scanning",
     "content": "Q: Can I print documents at the hotel?\nA: Yes! Our Business Centre has printers, scanners, and photocopiers:\n• B&W printing: RM1/page\n• Colour printing: RM3/page\n• Scanning to email: complimentary\n• USB printing: supported\nAvailable 24/7 with keycard access. For large print jobs, our concierge can arrange a commercial print shop in town."},

    # ═══════════════════════════════════════════════════════════════
    # LOYALTY & PROMOTIONS (~20)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "loyalty", "title": "Loyalty Programme Overview",
     "content": "Q: Do you have a loyalty programme?\nA: Yes! Our Grand Horizon Rewards programme is free to join and offers:\n• Earn 10 points per RM1 spent\n• Welcome drink on every stay\n• Birthday month 20% discount\n• Free late check-out (2 PM)\n• Priority room upgrades\n• Exclusive member-only rates\nSign up at the front desk or online — instant benefits from your very first stay!"},
    {"doc_type": "loyalty", "title": "Loyalty Points Redemption",
     "content": "Q: What can I use my points for?\nA: Points can be redeemed for:\n• Free night stays (from 5,000 points)\n• Room upgrades (2,500 points)\n• Spa treatments (30% off with 1,000 points)\n• Dining credits (500 points = RM50)\n• Airport transfers (1,500 points)\nPoints never expire as long as there's activity in the last 24 months. Every point counts!"},

    # ═══════════════════════════════════════════════════════════════
    # ACCESSIBILITY (~15)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "accessibility", "title": "Wheelchair Accessibility Overview",
     "content": "Q: Is the resort wheelchair accessible?\nA: Yes! Our property is designed for accessibility:\n• 6 accessible ground-floor rooms with roll-in showers\n• Ramp access to all public areas\n• Accessible pool hoist\n• Wheelchair-accessible restaurant seating\n• 3 passenger lifts with braille buttons\n• Accessible parking bays near entrance\nPlease let us know your needs at booking so we can ensure everything is perfect."},
    {"doc_type": "accessibility", "title": "Hearing Impairment Support",
     "content": "Q: Do you accommodate hearing-impaired guests?\nA: Absolutely! We provide:\n• Visual fire alarms (strobe lights) in designated rooms\n• Written communication support at all service points\n• Closed captioning on TVs\n• Vibrating alarm clocks on request\nPlease mention this when booking and we'll ensure the right room is assigned and our team is briefed."},
    {"doc_type": "accessibility", "title": "Dietary & Medical Accessibility",
     "content": "Q: My mother has mobility issues and diabetes — can you help?\nA: Of course! For mobility, our ground-floor accessible rooms have grab bars, walk-in/roll-in showers, and wider doorways. For dietary needs, our chefs will prepare diabetic-friendly meals on request — low sugar, controlled carbs, and balanced options. Please share her specific requirements and we'll prepare everything in advance."},

    # ═══════════════════════════════════════════════════════════════
    # SAFETY & EMERGENCY (~15)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "safety", "title": "Emergency Procedures",
     "content": "Q: What are the emergency procedures?\nA: In any emergency, call our front desk (extension 0) or dial 999 (Malaysian emergency services). Fire exits are clearly marked on every floor — an evacuation map is behind your room door. Our team is trained in first aid and emergency response. Fire drills are conducted monthly."},
    {"doc_type": "safety", "title": "Valuables & Safe",
     "content": "Q: Where should I keep my valuables?\nA: Every room has an electronic in-room safe (fits a laptop). For larger valuables, our front desk offers complimentary safe deposit boxes. We recommend not leaving valuables unattended at the pool or beach. In the unfortunate event of loss, please report immediately — we have comprehensive CCTV coverage."},
    {"doc_type": "safety", "title": "Natural Disaster Preparedness",
     "content": "Q: What about earthquakes or storms?\nA: Our building meets all seismic safety standards. During monsoon season (Nov–Feb), we monitor weather closely. In the event of severe weather, our team will communicate via in-room TV alerts and direct guest notification. Emergency supplies and backup generators ensure continued operation."},

    # ═══════════════════════════════════════════════════════════════
    # SUSTAINABILITY (~15)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "sustainability", "title": "Environmental Initiatives",
     "content": "Q: What are you doing for the environment?\nA: We're committed to sustainable hospitality:\n• Solar panels supply 30% of our energy\n• Zero single-use plastic (water refill stations on every floor)\n• Towel & linen reuse programme\n• Food waste composting for our organic garden\n• Rainwater harvesting for landscape irrigation\n• Coral reef conservation partnership\nWe believe luxury and sustainability go hand in hand!"},
    {"doc_type": "sustainability", "title": "Towel Reuse Programme",
     "content": "Q: Do I have to change towels daily?\nA: You have the choice! Our Green Stay programme invites you to hang towels to reuse or leave them on the floor for replacement. Each reused towel saves 75 litres of water. As a thank-you, Green Stay participants earn bonus loyalty points. It's a small act with a big environmental impact!"},
    {"doc_type": "sustainability", "title": "Local Community Support",
     "content": "Q: Do you support local communities?\nA: Yes! We're proud to:\n• Source 70% of our produce from local farms\n• Employ 85% local staff from surrounding communities\n• Sponsor education programmes at two nearby schools\n• Host monthly community clean-up events\n• Sell local artisan products in our gift shop\nWhen you stay with us, you're supporting the local community too!"},

    # ═══════════════════════════════════════════════════════════════
    # HOUSEKEEPING — In-Room Services (~20)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "housekeeping", "title": "Housekeeping Schedule",
     "content": "Q: When is housekeeping done?\nA: Daily housekeeping is between 9 AM and 3 PM. If you'd prefer a specific time, just let the front desk know. Evening turndown service (optional) is between 6 PM and 8 PM. If you have the DND sign on, we'll skip your room and return when it's convenient for you."},
    {"doc_type": "housekeeping", "title": "Extra Towels & Pillows",
     "content": "Q: Can I get extra towels?\nA: Of course! Just call extension 0 or message us here. Extra towels, pillows, blankets, and bathrobes will be delivered to your room within 15 minutes. We're always happy to make your stay more comfortable — no request is too small!"},
    {"doc_type": "housekeeping", "title": "Room Cleaning Preferences",
     "content": "Q: I don't want housekeeping today.\nA: No problem at all! Activate the DND sign on your door panel or let the front desk know. Some guests prefer housekeeping every other day — we're happy to accommodate. If you change your mind, just let us know and we'll send someone up."},
    {"doc_type": "housekeeping", "title": "Stain or Spill Emergency",
     "content": "Q: I spilled wine on the carpet!\nA: Don't worry about it — these things happen! Call extension 0 and our housekeeping team will attend immediately with professional cleaning equipment. We'll handle the rest. Please don't apply any products yourself as some can set the stain. No charges for normal spills — your enjoyment is what matters!"},
    {"doc_type": "housekeeping", "title": "Iron & Ironing Request",
     "content": "Q: Can someone iron my shirt?\nA: Certainly! You can use the in-room iron and board, or our housekeeping team can press items for you at RM8/piece (collected and returned within 2 hours). For a full wardrobe refresh, our laundry service offers wash, dry, and fold from RM10/item with same-day return."},
]
