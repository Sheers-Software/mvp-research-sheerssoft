"""
Segment B — Homestay, Villa, Chalet, Inn Knowledge Base (Part 1)
Categories: Property Types, Self-Catering, House Rules, Key Handover, Cleaning
~250 entries
"""

DOCS = [
    # ═══════════════════════════════════════════════════════════════
    # HOMESTAY — Property Types & Layouts (~80)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "homestay", "title": "Homestay Overview — What to Expect",
     "content": "Q: What's the difference between a homestay and a hotel?\nA: A homestay offers a more authentic, home-like experience! You'll have an entire house or apartment to yourselves — kitchen, living room, bedrooms, and often a garden. It's perfect for families, groups, and longer stays. You get privacy and flexibility to cook, do laundry, and live at your own pace. Welcome home!"},
    {"doc_type": "homestay", "title": "2-Bedroom Homestay — Family Layout",
     "content": "Q: Describe your 2-bedroom homestay.\nA: Our 2-bedroom homestay (approx 900 sqft) comfortably sleeps 4–5 guests. Features: master bedroom with queen bed, second bedroom with twin beds, shared bathroom with hot shower, fully equipped kitchen (rice cooker, gas stove, fridge), living area with TV, ceiling fans + aircon in bedrooms, and a covered parking bay. From RM180/night."},
    {"doc_type": "homestay", "title": "3-Bedroom Homestay — Group Layout",
     "content": "Q: How big is the 3-bedroom unit?\nA: Our 3-bedroom homestay (approx 1,200 sqft) is ideal for 6–8 guests. It has a master with queen bed and attached bathroom, two rooms with twin beds, shared bathroom, full kitchen, washing machine, living room with TV, and a small garden. From RM250/night — great for extended families or friend groups!"},
    {"doc_type": "homestay", "title": "Studio / 1-Bedroom for Couples",
     "content": "Q: Do you have something small for just the two of us?\nA: Our cosy 1-bedroom studio (approx 500 sqft) is perfect for couples! Features a queen bed, kitchenette with microwave and mini-fridge, attached bathroom, small balcony, Wi-Fi, and aircon. It's private, quiet, and wonderfully romantic. From RM120/night."},
    {"doc_type": "homestay", "title": "Kampung-Style Traditional Homestay",
     "content": "Q: Do you have a traditional Malay house?\nA: Yes! Our kampung-style homestay is a beautifully restored traditional wooden house with:\n• Open-concept living with original timber floors\n• 2 bedrooms (mattress on platform, traditional style)\n• Outdoor kitchen area\n• Surrounded by fruit trees and a paddy field view\nA truly authentic Malaysian experience from RM150/night!"},
    {"doc_type": "homestay", "title": "Maximum Guest Capacity",
     "content": "Q: How many people can stay?\nA: Our properties accommodate:\n• Studio: 2 guests max\n• 2-Bedroom: 4–5 guests (extra mattress available)\n• 3-Bedroom: 6–8 guests\n• 4-Bedroom Villa: 8–10 guests\n• 5-Bedroom Villa: 10–14 guests\nAdditional guests beyond capacity incur RM30/person/night. This ensures comfort and neighbour considerations."},
    {"doc_type": "homestay", "title": "Mattress on Floor / Extra Sleeping",
     "content": "Q: Can we bring our own mattress or sleeping bag?\nA: Absolutely! If you'd like to bring extra sleeping arrangements, you're welcome to. We also provide floor mattresses at RM30/night each. Please note the maximum occupancy for each property — this is set for comfort and safety. Just let us know your total headcount when booking."},
    {"doc_type": "homestay", "title": "Linen & Towels Provided",
     "content": "Q: Do you provide bedsheets and towels?\nA: Yes! All linen, bed sheets, pillows, blankets, and bath towels are provided and freshly laundered. We also include hand towels and a basic toiletry set (soap, shampoo). For stays of 4+ nights, we offer a mid-stay linen change at no extra charge. Just let us know!"},
    {"doc_type": "homestay", "title": "Homestay with Private Pool",
     "content": "Q: Do any of your properties have a private pool?\nA: Yes! Our premium homestays and villas come with private plunge pools (3m x 5m, 1.2m depth). These are fenced for child safety and maintained weekly. Pool usage is at your own risk — no lifeguard provided. Properties with private pools start from RM350/night."},
    {"doc_type": "homestay", "title": "Garden & Outdoor Space",
     "content": "Q: Is there outdoor space?\nA: Most of our properties have either a covered porch, small garden, or both. Perfect for morning coffee, evening BBQ, or kids running around safely. Some properties also have a car porch for covered parking and a clothes drying area."},

    # ═══════════════════════════════════════════════════════════════
    # VILLA — Features & Premium Properties (~80)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "villa", "title": "Villa Overview — Luxury Private Stay",
     "content": "Q: Tell me about your villas.\nA: Our villas are standalone private homes offering luxury and space — think of it as your own holiday mansion! Features include: multiple bedrooms (3–5), private pool, full kitchen, BBQ area, landscaped garden, daily housekeeping, and premium amenities. Ideal for families, celebrations, or groups wanting privacy with resort-quality comforts. From RM550/night."},
    {"doc_type": "villa", "title": "4-Bedroom Villa — Family Gathering",
     "content": "Q: What does the 4-bedroom villa look like?\nA: Our 4-bedroom villa (approx 2,500 sqft) includes:\n• Master suite with king bed & ensuite\n• 3 guest bedrooms (queen/twin configs)\n• 3 bathrooms total\n• Spacious living & dining area\n• Full kitchen with oven and dishwasher\n• Private pool (4x8m) + garden\n• Covered BBQ pavilion\n• 2 parking spaces\nFrom RM700/night. Perfect for multi-generational holidays!"},
    {"doc_type": "villa", "title": "5-Bedroom Villa — Large Group",
     "content": "Q: We're 12 people — what do you have?\nA: Our 5-bedroom villa is ideal for you! It sleeps up to 14 guests with:\n• 5 bedrooms (king, queen, and twin options)\n• 4 bathrooms\n• Large open-plan kitchen, dining, and living area\n• Private infinity pool\n• BBQ area with outdoor dining for 14\n• Karaoke room\n• 3 parking bays\nFrom RM1,100/night. Family reunions are our speciality!"},
    {"doc_type": "villa", "title": "Villa Private Pool Details",
     "content": "Q: Tell me about the private pool.\nA: Our villa pools are maintained weekly (2–3 times during your stay for longer bookings). Pool specs:\n• Size: 4m x 8m, depth 1.2m–1.5m\n• Chlorinated & pH-balanced\n• Pool lights for evening swimming\n• Sun loungers and pool towels provided\n• Child safety fence available\nSwimming is at your own risk — we recommend supervision for children at all times."},
    {"doc_type": "villa", "title": "Villa vs Hotel — Why Choose a Villa?",
     "content": "Q: Should we stay at a villa or a hotel?\nA: Great question! Choose a villa if you want:\n• More space and privacy\n• Ability to cook your own meals\n• Private pool\n• Flexible check-in/out\n• Better value for groups (cost-per-person)\nChoose a hotel if you prefer daily housekeeping, on-site restaurants, and a concierge team. Many families do a split stay — hotel for relaxation, villa for the group gathering!"},
    {"doc_type": "villa", "title": "Villa Amenities Checklist",
     "content": "Q: What's provided in the villa?\nA: Every villa includes:\n• Kitchen: fridge, stove, oven, microwave, rice cooker, kettle, cookware, cutlery/crockery\n• Living: TV (smart/cable), Wi-Fi, aircon, ceiling fans, sofa\n• Bedrooms: quality linen, towels, wardrobe, aircon\n• Bathroom: hot shower, toiletries, hairdryer\n• Outdoor: BBQ grill, garden furniture, pool towels\n• Extras: iron, washing machine, first-aid kit\nFeel at home!"},
    {"doc_type": "villa", "title": "Villa Daily Housekeeping",
     "content": "Q: Does the villa come with housekeeping?\nA: Standard villas include housekeeping on check-out day. Our premium villas include daily housekeeping (9 AM–12 PM) covering basic cleaning, bed-making, and towel refresh. Additional housekeeping visits can be arranged at RM80/visit. We want you to enjoy your holiday, not worry about cleaning!"},
    {"doc_type": "villa", "title": "Villa Private Chef Service",
     "content": "Q: Can we hire a private chef?\nA: Absolutely! Our private chef service brings restaurant-quality dining to your villa.\n• Dinner for up to 10 pax: from RM800 (3-course)\n• BBQ night: from RM600 (inclusive of ingredients)\n• Full-day chef: from RM1,200\nMenus are customisable — Malaysian, Western, or fusion. Chef arrives with all ingredients and cleans up after. Truly an elevated villa experience!"},

    # ═══════════════════════════════════════════════════════════════
    # CHALET — Cabin & Nature Stay (~60)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "chalet", "title": "Chalet Overview — Nature Retreat",
     "content": "Q: What's a chalet like?\nA: Our chalets are cosy standalone cabins set within nature — think wooden interiors, surrounded by trees, mountain or river views, and clean air. Each chalet sleeps 2–4 guests with attached bathroom, basic kitchenette, and a verandah with seating. Perfect for a jungle escape without roughing it! From RM150/night."},
    {"doc_type": "chalet", "title": "A-Frame Chalet — Instagram Worthy",
     "content": "Q: Do you have an A-frame chalet?\nA: Yes! Our A-frame chalets are among our most popular — the striking triangular design with large windows creates a stunning backdrop for photos. Features: loft-style bedroom, cosy ground floor with kitchenette, outdoor deck, and mountain views. From RM220/night. Perfect for couples or small families!"},
    {"doc_type": "chalet", "title": "Chalet Kitchen Facilities",
     "content": "Q: Can I cook in the chalet?\nA: Yes! Our chalets have a basic kitchenette with:\n• Mini fridge\n• Kettle\n• Microwave\n• Toaster\n• Basic cookware and utensils\nFor full cooking facilities, we have a communal outdoor kitchen with gas stoves. The nearest grocery shop is 10 minutes by car. We can provide a list of local produce shops!"},
    {"doc_type": "chalet", "title": "Chalet Insect & Wildlife",
     "content": "Q: Are there insects? I'm worried about bugs.\nA: As we're in a natural setting, occasional insects are part of the experience — harmless and generally stay outside. We provide mosquito coils/repellent, and all windows have insect screens. Rooms are regularly treated. You might spot monkeys, squirrels, or even hornbills! It's part of the charm of staying in nature."},
    {"doc_type": "chalet", "title": "Chalet Rainy Season Accessibility",
     "content": "Q: Is the chalet accessible during rainy season?\nA: Yes! Our chalets are built on elevated platforms and all access roads are paved. During heavy rain (Nov–Feb), rivers may swell — we monitor conditions closely and will advise on any activity changes. The sound of rain on the roof is actually one of the most peaceful experiences — many guests love it!"},
    {"doc_type": "chalet", "title": "Chalet River View / Waterfront",
     "content": "Q: Do any chalets overlook the river?\nA: Three of our premium chalets are positioned right along the riverbank with unobstructed views. You can hear the gentle sounds of flowing water from your verandah. These are our most requested units — from RM280/night. Book early to secure one!"},

    # ═══════════════════════════════════════════════════════════════
    # INN — Boutique & Small Stays (~50)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "inn", "title": "Inn Overview — Boutique Experience",
     "content": "Q: What kind of inn is this?\nA: We're a charming boutique inn with just 12 rooms — small enough to know every guest by name! Each room is uniquely designed with local art and heritage touches. Benefits: personal service, home-cooked breakfast, intimate common areas, and insider local tips from your host. It's like staying with a well-connected friend. From RM140/night."},
    {"doc_type": "inn", "title": "Inn Breakfast — Home-cooked",
     "content": "Q: Is breakfast included?\nA: Yes! Our home-cooked breakfast is one of our highlights — served fresh between 8 AM and 10 AM. Expect local favourites like nasi lemak, roti canai, half-boiled eggs and kaya toast, or Western options. Dietary accommodations happily made. Many guests tell us our breakfast alone is worth the stay!"},
    {"doc_type": "inn", "title": "Common Area & Social Spaces",
     "content": "Q: Are there common areas?\nA: Absolutely! Our inn features a communal living room with library shelves, board games, and a record player (yes, vinyl!). The garden patio is perfect for evening conversations. Many guests bond over shared stories — it's the beauty of a small inn. Solo travellers especially love the sense of community!"},
    {"doc_type": "inn", "title": "Inn Pet Policy",
     "content": "Q: Can I bring my dog to the inn?\nA: We love furry guests! Small dogs (under 8 kg) are welcome with prior notice. A pet fee of RM40/night applies. Pets must be well-behaved and housebroken. We provide a pet bowl and blanket. Pets are welcome in the garden but not in common indoor areas, out of consideration for other guests."},
    {"doc_type": "inn", "title": "Inn Heritage & Story",
     "content": "Q: Tell me the story of this place.\nA: Our inn is housed in a beautifully restored 1920s shophouse — originally a fabric merchant's home. We've preserved the original timber beams, Peranakan floor tiles, and louvre windows while adding modern comforts. Every room is named after a local heritage figure. It's living history with Wi-Fi and aircon!"},

    # ═══════════════════════════════════════════════════════════════
    # SELF-CATERING & KITCHEN (~60)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "self_catering", "title": "Kitchen Equipment Inventory",
     "content": "Q: What kitchen equipment is available?\nA: Our full kitchen includes:\n• Gas stove (2 burner) or induction cooktop\n• Fridge with small freezer\n• Rice cooker (essential!)\n• Kettle & toaster\n• Microwave\n• Pots, pans, wok, and baking tray\n• Full cutlery & crockery set (for max occupancy)\n• Chopping boards, knives, spatulas\n• Basic condiments (oil, salt, pepper, soy sauce)\nCook to your heart's content!"},
    {"doc_type": "self_catering", "title": "Where to Buy Groceries",
     "content": "Q: Where's the nearest supermarket?\nA: The nearest options:\n• Segi Fresh Market: 10 min drive (fresh produce & meat, daily 6am–6pm)\n• Mydin/Giant hypermart: 20 min drive (everything under one roof)\n• Local sundry shop (kedai runcit): 5 min drive (basics & kampung essentials)\nWe can share exact locations via WhatsApp GPS pin. Pro tip: the wet market has the freshest seafood — arrive before 8 AM!"},
    {"doc_type": "self_catering", "title": "BBQ Pit — How to Use",
     "content": "Q: Can we use the BBQ pit?\nA: Yes! The BBQ pit is free to use. We provide:\n• Charcoal BBQ grill (pre-cleaned)\n• Grill tongs and spatula\n• First bag of charcoal (complimentary)\n• Dining table and chairs nearby\nAdditional charcoal is RM15/bag (available on-site). Please clean the grill after use and dispose of ashes in the provided bin. Happy grilling!"},
    {"doc_type": "self_catering", "title": "Water Quality & Drinking Water",
     "content": "Q: Is the tap water safe to drink?\nA: Tap water is treated and safe for bathing and cooking. For drinking, we recommend using the provided water dispenser (hot & cold) or the complimentary bottled water (2 bottles/day). A water filter jug is also available in the kitchen. Additional bottled water is RM3/bottle from our mini pantry."},
    {"doc_type": "self_catering", "title": "Bringing Own Food & Cooking",
     "content": "Q: Can we bring our own food to cook?\nA: Absolutely! That's one of the best things about a self-catering stay. Bring anything you like. The fridge is cleared and cleaned before each guest. We just ask that you dispose of any leftover food before check-out and leave the kitchen in a reasonable condition. Cooking is half the fun!"},
    {"doc_type": "self_catering", "title": "Washing Machine & Laundry",
     "content": "Q: Is there a washing machine?\nA: Yes! All 2+ bedroom properties have a semi-auto or fully automatic washing machine. Detergent is provided. There's a covered drying area (or foldable drying rack for indoor use). Perfect for families on longer stays — no need to pack a week's worth of clothes!"},
    {"doc_type": "self_catering", "title": "Outdoor Cooking Area",
     "content": "Q: Is there an outdoor kitchen?\nA: Our communal outdoor kitchen (for chalet guests) has:\n• 4-burner gas stove\n• Large prep counter\n• Sink with running water\n• Dining tables seating 20\n• Covered roof for all-weather cooking\nPerfect for group cook-outs! Individual chalets have a basic kitchenette inside. Rice cookers are available for loan."},

    # ═══════════════════════════════════════════════════════════════
    # HOUSE RULES & ETIQUETTE (~80)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "house_rules", "title": "Noise & Quiet Hours",
     "content": "Q: Are there quiet hours?\nA: Yes — quiet hours are 11 PM to 7 AM. We're located in a residential neighbourhood and respect for our neighbours is important. Music and loud activities should be indoors with windows closed after 11 PM. Outdoor gatherings should wind down by 10 PM. Thank you for being considerate!"},
    {"doc_type": "house_rules", "title": "Smoking Rules",
     "content": "Q: Can we smoke in the property?\nA: Smoking is strictly not allowed indoors. You're welcome to smoke in the outdoor/garden area — we provide ashtrays. Please dispose of cigarette butts properly. A cleaning fee of RM200 will be charged if evidence of indoor smoking is found (it's very persistent!). Thank you for understanding."},
    {"doc_type": "house_rules", "title": "Shoes Off Policy",
     "content": "Q: Do we need to remove shoes indoors?\nA: Yes please! As is customary in Malaysian homes, we kindly ask that shoes be removed before entering the house. A shoe rack is provided at the entrance. This keeps the floors clean and is a cultural sign of respect. Indoor slippers are available for your comfort."},
    {"doc_type": "house_rules", "title": "Maximum Occupancy",
     "content": "Q: Can we bring extra guests for a day visit?\nA: Day visitors are welcome during operating hours (before 10 PM), but please inform us beforehand. If overnight guests exceed the booked occupancy, an additional charge of RM30/person/night applies. Maximum occupancy limits are set for fire safety and neighbour consideration."},
    {"doc_type": "house_rules", "title": "Party & Event Policy",
     "content": "Q: Can we throw a birthday party at the homestay?\nA: Small indoor gatherings (under 15 pax) are generally fine, subject to noise rules. Larger parties or events require prior approval and may incur an event fee. Public music must end by 10 PM. If you're planning something special, let us know and we'll help you celebrate within the guidelines!"},
    {"doc_type": "house_rules", "title": "Pet Policy — Private Properties",
     "content": "Q: Can we bring our pet to the homestay?\nA: Pets are allowed at selected properties only (marked as 'pet-friendly'). A pet fee of RM50/night applies. Pets must be housebroken and not left unattended. You're responsible for cleaning up after your pet. Please inform us at booking — we'll ensure you get a pet-suitable property."},
    {"doc_type": "house_rules", "title": "Check-Out Cleaning Expectations",
     "content": "Q: Do we need to clean before leaving?\nA: We don't expect you to deep clean! Just please:\n• Wash or load dishes into the sink/dishwasher\n• Dispose of food and rubbish\n• Leave the BBQ area tidy\n• Place used towels in the bathroom\n• Let us know of any breakages\nOur cleaning team handles the rest. A professional cleaning fee is included in your booking."},
    {"doc_type": "house_rules", "title": "Key Return & Lock-Up",
     "content": "Q: How do I return the keys at check-out?\nA: Most properties use a keypad/smart lock — no physical key needed! For properties with keys, please leave them on the dining table and close the main door firmly. Gate padlock should be secured. If you need flexible check-out timing, just message us and we'll sort it out."},
    {"doc_type": "house_rules", "title": "Garbage Disposal",
     "content": "Q: Where do we throw the rubbish?\nA: Rubbish bins are in the kitchen and outdoor area. Please bag all waste securely (especially food waste to avoid ants). Wheelie bins are outside the gate for collection. For recycling, separate bins are provided. Please don't leave food waste in open bins — our furry friends (monkeys!) get curious!"},
    {"doc_type": "house_rules", "title": "Fireworks & Open Flame Policy",
     "content": "Q: Can we light sparklers or fireworks?\nA: Sparklers are allowed in the outdoor area with adult supervision. Fireworks and sky lanterns are strictly not permitted for fire safety. For celebrations, we can arrange safe alternatives like LED balloons or confetti poppers. Safety first, fun always!"},

    # ═══════════════════════════════════════════════════════════════
    # LOCAL AREA & ATTRACTIONS (~80)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "local_area", "title": "Nearest Town & Shops",
     "content": "Q: How far is the nearest town?\nA: The nearest town is approximately 15 minutes by car. There you'll find supermarkets (Mydin, 99 Speedmart), restaurants, a petrol station, ATMs, clinic, and pharmacy. A smaller sundry shop (kedai runcit) is just 5 minutes away for basic needs. We'll share GPS pins with all key locations!"},
    {"doc_type": "local_area", "title": "Restaurant Recommendations",
     "content": "Q: Where's good to eat nearby?\nA: Our local favourites:\n• Pak Ali's Seafood: 10 min, incredible grilled fish (from RM15)\n• Kak Jah Nasi Campur: 8 min, legendary home-style Malay food\n• Ah Beng Corner: 12 min, best laksa in the area\n• Restoran Rasa Sayang: 15 min, Indian mamak open 24 hours\nAll budget-friendly and absolutely delicious. We can share exact locations!"},
    {"doc_type": "local_area", "title": "Nearest Hospital & Clinic",
     "content": "Q: Where's the nearest hospital?\nA: The nearest government clinic (Klinik Kesihatan) is 10 minutes away and operates during office hours. The district hospital is 25 minutes by car. For emergencies, dial 999. We have a basic first-aid kit at the property. We can also recommend private clinics in town if needed."},
    {"doc_type": "local_area", "title": "ATM & Banking",
     "content": "Q: Where's the nearest ATM?\nA: The nearest ATMs are in town (15 minutes): Maybank, CIMB, and Bank Islam. There's also a Petronas station with Touch 'n Go reload 5 minutes away. Many small shops accept cash only, so we recommend withdrawing enough before heading to the property."},
    {"doc_type": "local_area", "title": "Waterfalls & Nature Attractions",
     "content": "Q: Are there waterfalls nearby?\nA: Yes! Within 30 minutes:\n• Sungai Chiling Falls: 2-hour jungle trek, river crossings, stunning 7-tier falls\n• Rainbow Waterfall: easy 30-min walk, family-friendly\n• Kampung Ulu Falls: hidden gem, less crowded\nWe can arrange a local guide (RM100/group) who knows the safest routes. Bring water shoes!"},
    {"doc_type": "local_area", "title": "Beaches & Islands Nearby",
     "content": "Q: How far is the nearest beach?\nA: The nearest beach is 20 minutes by car — clean sandy shore with calm waters, perfect for families. For island hopping, the main jetty is 30 minutes away. Snorkelling and diving tours depart daily. We can arrange transport and book tours for you — just let me know your preferred dates!"},
    {"doc_type": "local_area", "title": "Night Market Schedule",
     "content": "Q: When is the pasar malam?\nA: The local pasar malam operates:\n• Wednesday evening: town market (5pm–10pm)\n• Saturday evening: kampung market (4pm–9pm)\nExpect amazing street food (satay, murtabak, ABC, cendol), fresh produce, and local snacks. Budget RM20–30/person for a full feast. It's an experience you shouldn't miss!"},
    {"doc_type": "local_area", "title": "Hiking Trails & Outdoor Activities",
     "content": "Q: Are there good hiking spots?\nA: The area is a hiker's paradise! Options:\n• Bukit Panorama: 1.5 hours, moderate, amazing 360° views\n• River Trail: 45 min, easy, suitable for families\n• Summit Trail: 3–4 hours, challenging, for experienced hikers\n• Bamboo Walk: 30 min, flat, wheelchair-accessible\nWe recommend starting early (before 8 AM) to beat the heat. Guides available at RM80/trip."},

    # ═══════════════════════════════════════════════════════════════
    # OWNER COMMUNICATION & OPERATIONS (~50)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "owner_comms", "title": "How to Contact the Owner/Host",
     "content": "Q: How do I reach the owner if I need help?\nA: You're chatting with us right now! This is the easiest way to reach your host. We're available via WhatsApp from 8 AM to 10 PM. For after-hours emergencies (water leak, lockout, safety), we have an emergency line that's always on. Response time is within 15 minutes during operating hours."},
    {"doc_type": "owner_comms", "title": "Check-In Process — Self-Check-In",
     "content": "Q: How do I check in? Is anyone there to meet us?\nA: Most of our properties offer self-check-in via smart lock (door code sent 2 hours before check-in). If you prefer a meet-and-greet, our local caretaker can welcome you and show you around the property. Just let us know your estimated arrival time and preference!"},
    {"doc_type": "owner_comms", "title": "Maintenance Issue Reporting",
     "content": "Q: The shower is leaking / something is broken.\nA: I'm sorry about that! Please send a photo via WhatsApp and I'll arrange our maintenance person to fix it as quickly as possible. For urgent issues (water leak, electrical, lockout), we'll have someone there within 30 minutes. For non-urgent repairs, within 4 hours. Your comfort is our priority!"},
    {"doc_type": "owner_comms", "title": "Extending the Stay",
     "content": "Q: Can we extend our stay by one more night?\nA: We'd love to have you longer! Let me check availability. If the property is available, I'll confirm the rate (same as your current booking) and update your reservation. Please let us know at least 12 hours before your original check-out time so we can adjust housekeeping."},
    {"doc_type": "owner_comms", "title": "Damage Reporting & Deposit",
     "content": "Q: We accidentally broke a glass/plate.\nA: No worries — accidents happen! Thank you for letting us know. Minor breakages of standard kitchenware (glasses, plates) are covered and won't be charged. For any significant damage, we'll assess fairly and only charge replacement cost. Honesty is always appreciated and we never overcharge."},
    {"doc_type": "owner_comms", "title": "Refund & Cancellation Policy",
     "content": "Q: We need to cancel our booking. Do we get a refund?\nA: We understand plans change! Our policy:\n• 14+ days before check-in: Full refund\n• 7–13 days: 50% refund\n• Less than 7 days: No refund (but we'll try to rebook)\n• Date changes: Free if moved within 30 days\nWe're always flexible for genuine emergencies — just talk to us."},
    {"doc_type": "owner_comms", "title": "Review & Feedback Request",
     "content": "Q: Where can I leave a review?\nA: We truly appreciate your feedback! You can leave a review on the platform you booked through (Airbnb, Booking.com), Google Maps, or simply share your thoughts with us here on WhatsApp. Honest feedback helps us improve and helps future guests choose confidently. Thank you for staying with us!"},
    {"doc_type": "owner_comms", "title": "Lost Items After Check-Out",
     "content": "Q: I think I left my charger at the homestay.\nA: Let me check with our cleaning team right away! If found, we can arrange to post it to you (postage costs apply) or hold it for your next visit. Please describe the item and approximately where you left it. We check thoroughly after every check-out."},
]
