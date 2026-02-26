"""
Segment A — Hotel & Resort Knowledge Base (Part 4)
Expanded categories with deeper coverage: Rooms, Rates, Dining, Spa, Pools, Sports
~200 entries
"""

DOCS = [
    # ═══════════════════════════════════════════════════════════════
    # ROOMS — Extended Variants (~40)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "rooms", "title": "Superior Twin Room",
     "content": "Q: What's your most affordable twin room?\nA: Our Superior Twin Room (30 sqm) features two single beds, city view, en-suite bathroom with rain shower, work desk, 43-inch smart TV, complimentary Wi-Fi, minibar, and tea/coffee facilities. Perfect for friends travelling together or business colleagues. From RM280/night including breakfast for two."},
    {"doc_type": "rooms", "title": "Junior Suite",
     "content": "Q: Tell me about the Junior Suite.\nA: Our Junior Suite (55 sqm) is a step up from the Deluxe — featuring a separate living area with sofa, king bed, marble bathroom with bathtub and rain shower, Nespresso machine, premium minibar, 55-inch TV, and a furnished balcony with garden or pool view. From RM680/night. Ideal for honeymooners or guests who appreciate extra space."},
    {"doc_type": "rooms", "title": "Penthouse Suite",
     "content": "Q: Do you have a penthouse?\nA: Our Penthouse Suite (120 sqm) is the pinnacle of luxury — panoramic views, private terrace, separate living and dining area, king bed with premium linen, dual marble bathrooms, walk-in wardrobe, butler service, and a private jacuzzi on the terrace. From RM2,800/night. Maximum 2 adults. A truly unforgettable experience."},
    {"doc_type": "rooms", "title": "Accessible Room Details",
     "content": "Q: Tell me about your wheelchair-accessible rooms.\nA: Our accessible rooms (35 sqm, ground floor) feature wider doorways (90 cm), roll-in shower with fold-down bench and grab bars, lowered vanity and closet rails, visual fire alarm, and emergency pull cord. Queen or twin bed configurations available. Same rate as our Deluxe rooms — RM380/night. Please request at booking."},
    {"doc_type": "rooms", "title": "Connecting Rooms for Families",
     "content": "Q: Do you have connecting rooms?\nA: Yes! We have 8 pairs of connecting rooms — a Deluxe King and a Superior Twin linked by an internal door. Perfect for families who want privacy and proximity. Book both rooms and receive 10% off the second room. Available on floors 3–5. Please request specifically during booking."},
    {"doc_type": "rooms", "title": "Room Upgrade Policy",
     "content": "Q: How do upgrades work?\nA: Room upgrades are subject to availability at check-in. Loyalty members get priority. You can also request a guaranteed upgrade for an additional RM100–300/night depending on the category jump. Walk-in upgrade requests are best made at the front desk — our team loves to surprise guests when possible!"},
    {"doc_type": "rooms", "title": "Smoking vs Non-Smoking Rooms",
     "content": "Q: Do you have smoking rooms?\nA: All indoor areas are non-smoking per Malaysian law. We have designated outdoor smoking areas on each floor balcony and at ground-level garden spots. A RM500 deep-cleaning fee applies if smoking evidence is found indoors. Ashtrays and lighters are available at the designated areas."},
    {"doc_type": "rooms", "title": "In-Room Safe Details",
     "content": "Q: How does the room safe work?\nA: Your in-room electronic safe can be set with a 4-digit personal code. It fits a 15-inch laptop, passport, and valuables. To set: press C, enter your code, press A. To open: enter your code, press A. If locked out, the front desk can assist with a master override. For larger items, use our lobby safe deposit boxes (complimentary)."},
    {"doc_type": "rooms", "title": "Minibar Contents & Pricing",
     "content": "Q: What's in the minibar?\nA: Your complimentary minibar includes 2 bottles of mineral water and 2 local snacks daily (replenished). Chargeable items: soft drinks (RM8), local beers (RM18), wine splits (RM35), Pringles (RM12), chocolate (RM10), instant noodles (RM6). A full price list is in the room compendium. Charges are posted to your room account."},
    {"doc_type": "rooms", "title": "Pillow Menu",
     "content": "Q: I'm fussy about pillows. Do you have options?\nA: We love guests who know what they want! Our pillow menu includes: memory foam, buckwheat hull, latex, down-feather, hypoallergenic synthetic, bolster, and even a body pillow. Just call housekeeping and we'll deliver your preferred option within 15 minutes. Sweet dreams guaranteed!"},
    {"doc_type": "rooms", "title": "Room View Options",
     "content": "Q: What views are available?\nA: Our room views come in four categories:\n• City View: overlooking the town skyline (standard)\n• Garden View: lush tropical landscaping (RM50 supplement)\n• Pool View: overlooking the infinity pool (RM80 supplement)\n• Sea View: panoramic ocean vistas (RM150 supplement)\nHigher floors generally have better views. Request your preference at booking!"},
    {"doc_type": "rooms", "title": "Late Night Room Service",
     "content": "Q: Can I order food to my room late at night?\nA: Our 24-hour room service offers a condensed late-night menu (11 PM–6 AM) featuring nasi goreng, mee goreng, sandwiches, soups, and desserts. Hot beverages and cold drinks are always available. A 15% late-night surcharge applies. Delivery within 30 minutes. Perfect for jet-lagged arrivals!"},

    # ═══════════════════════════════════════════════════════════════
    # RATES — Extended Scenarios (~40)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "rates", "title": "Best Rate Guarantee",
     "content": "Q: Will I get the best rate booking direct?\nA: Absolutely! Our Best Rate Guarantee means if you find a lower publicly available rate within 24 hours of booking, we'll match it AND give you an additional 10% off. Direct bookings also get: free cancellation up to 48 hours, complimentary room upgrade priority, and loyalty points. Always book direct!"},
    {"doc_type": "rates", "title": "Corporate Rate Programme",
     "content": "Q: Do you offer corporate rates?\nA: We partner with businesses to offer negotiated corporate rates — typically 20–30% below standard. Benefits include: guaranteed late check-out, express check-in, complimentary laundry (2 pieces/day), and meeting room credits. Minimum 50 room nights/year to qualify. Contact our sales team at sales@grandhorizon.com."},
    {"doc_type": "rates", "title": "Government Rate",
     "content": "Q: Do you have government rates?\nA: Yes! We offer special rates for government employees travelling on official business. Rates comply with federal/state per diem limits. Valid government ID/travel order required at check-in. Please contact us directly for current government rates and availability — we're happy to assist."},
    {"doc_type": "rates", "title": "Senior Citizen Discount",
     "content": "Q: Is there a discount for senior citizens?\nA: We offer a 15% discount for guests aged 60 and above (MyKad/passport verification required). This applies to our standard published rates and can be combined with our Weekday Escape offer. We also provide priority seating at restaurants and additional pillows/amenities on request. Seniors are special to us!"},
    {"doc_type": "rates", "title": "OTA vs Direct Booking Comparison",
     "content": "Q: Should I book through Booking.com or direct?\nA: We appreciate all bookings, but direct booking offers significant advantages:\n• Same or lower price (Best Rate Guarantee)\n• Free cancellation up to 48 hours\n• Room upgrade priority\n• Loyalty points earning\n• Direct communication for special requests\n• No third-party commission means we can offer extras\nBook direct at grandhorizon.com or message us here!"},
    {"doc_type": "rates", "title": "Day-Use Rate",
     "content": "Q: Can I book a room just for the day?\nA: Yes! Our Day-Use rate is perfect for travellers with layovers or anyone needing a few hours of rest. Available 10 AM–6 PM at 50% of the nightly rate. Includes full room access, pool, and gym. Subject to availability — best booked a day in advance. Great for refresh stops on road trips too!"},
    {"doc_type": "rates", "title": "Extended Stay Discount",
     "content": "Q: Any discount for a longer stay?\nA: Absolutely! Long stays are our sweet spot:\n• 3–6 nights: 10% off\n• 7–13 nights: 15% off\n• 14–29 nights: 20% off\n• 30+ nights: 25% off + weekly housekeeping + complimentary laundry\nExtended stay guests also enjoy welcome fruit basket and priority room selection. Many digital nomads make this their home!"},
    {"doc_type": "rates", "title": "Payment Methods Accepted",
     "content": "Q: What payment methods do you accept?\nA: We accept:\n• Credit/Debit cards: Visa, Mastercard, AMEX (JCB upon request)\n• FPX / Online banking transfer\n• Touch 'n Go eWallet, GrabPay, Boost\n• Cash (MYR only)\n• Wire transfer (for corporate/group bookings)\nFor online bookings, payment is processed via secure SSL encryption. All major e-wallets accepted at our restaurants and spa."},
    {"doc_type": "rates", "title": "Deposit & Pre-Authorisation",
     "content": "Q: Do you need a deposit when I book?\nA: Standard bookings require a 1-night deposit to confirm. This is charged at time of booking for non-refundable rates, or can be a pre-authorisation (hold) for flexible rates. The balance is settled at check-out. Peak season bookings require 50% deposit. We'll always communicate clearly before charging anything."},

    # ═══════════════════════════════════════════════════════════════
    # DINING — Extended Menu & Restaurant Details (~40)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "dining", "title": "Horizon Café — All-Day Dining",
     "content": "Q: What's the main restaurant like?\nA: Horizon Café is our all-day dining venue serving breakfast (6:30–10:30 AM), lunch (12–2:30 PM), and dinner (6:30–10 PM). Features: international buffet and à la carte menu, live cooking stations, local and Western dishes, halal-certified kitchen, outdoor terrace seating overlooking the pool. Casual dress code."},
    {"doc_type": "dining", "title": "Sunset Grill — Beachfront Dining",
     "content": "Q: Do you have a beachfront restaurant?\nA: Sunset Grill is our signature beachfront restaurant, open for dinner only (6 PM–10 PM, closed Mondays). Specialises in grilled seafood, steaks, and wood-fired pizza. Famous for our live-catch seafood — choose your fish from the display and we'll grill it to perfection. Reservations recommended. Smart casual dress code."},
    {"doc_type": "dining", "title": "Poolside Bar — Cocktails & Light Bites",
     "content": "Q: Is there a bar by the pool?\nA: Our Poolside Bar serves from 10 AM to 10 PM daily. Menu includes: tropical cocktails (from RM28), mocktails (from RM15), local beers (RM18), wines by the glass (from RM25), and light bites (satay, fries, nachos, fruit platters). Happy Hour is 5–7 PM with buy-1-free-1 on selected drinks. Swim up to our pool bar counter!"},
    {"doc_type": "dining", "title": "Breakfast Hours & Options",
     "content": "Q: What time is breakfast served?\nA: Breakfast buffet: 6:30–10:30 AM daily at Horizon Café. Our spread includes:\n• Local favourites: nasi lemak, roti canai, dim sum, congee\n• Continental: pastries, cold cuts, cheese, cereals\n• Hot station: eggs any style, bacon, sausages, pancakes\n• Healthy corner: fresh fruits, yogurt, granola, juices\n• Live station: rotating daily (laksa, mee rebus, etc.)\nIn-house guests included; walk-ins RM48/adult, RM24/child."},
    {"doc_type": "dining", "title": "Halal Certification Status",
     "content": "Q: Is your food halal?\nA: All our restaurants hold JAKIM halal certification (certification number displayed at each outlet). Our kitchen maintains strict halal compliance — separate preparation areas, dedicated utensils for halal cooking. We do not serve pork in any outlet. Alcohol is available only at the bar and can be served at table upon request."},
    {"doc_type": "dining", "title": "Dietary Accommodations",
     "content": "Q: My wife is vegetarian and I'm gluten-free. Can you accommodate?\nA: Absolutely! Our chefs are experienced with dietary requirements:\n• Vegetarian / Vegan: extensive options at every meal\n• Gluten-free: dedicated GF options, separate preparation\n• Nut allergies: all dishes can be modified\n• Dairy-free: alternatives available\n• Diabetic-friendly: low-sugar, controlled carb menu\nPlease inform us at booking and remind your server at each meal. Your health is our priority!"},
    {"doc_type": "dining", "title": "Private Dining Experience",
     "content": "Q: Can we have a private dinner just for us?\nA: We'd love to arrange that! Options:\n• Beach dinner for 2: RM680 (4-course, candles, personal waiter)\n• Garden pavilion dinner: RM450 (min 4 pax, customised menu)\n• In-room dining experience: RM250 (special setup + 3-course)\n• Yacht dinner cruise: RM1,200/couple (sunset, 3 hours, 5-course)\nAll include personalised menu, décor, and a memorable setting. 48 hours advance booking required."},
    {"doc_type": "dining", "title": "Kids' Menu at Restaurants",
     "content": "Q: Do you have a children's menu?\nA: Yes! Our kids' menu (ages 4–12) is available at all outlets:\n• Breakfast: included with adult dining\n• Lunch/Dinner: from RM18 per dish\n• Options: chicken nuggets, fish fingers, pasta, fried rice, mini burgers, fruit platters, ice cream\n• All portions are kid-sized with fun presentation\nHighchairs and booster seats available. Children under 4 eat free from the buffet!"},
    {"doc_type": "dining", "title": "Room Service Menu & Hours",
     "content": "Q: What's available via room service?\nA: Room service operates 6:30 AM–11 PM (condensed late-night menu until 6 AM). Our menu mirrors the best of Horizon Café plus exclusive room service items (club sandwiches, pasta, local favourites). Average delivery: 25 minutes. A 15% service charge applies. The in-room dining setup includes proper tableware and presentation."},
    {"doc_type": "dining", "title": "Afternoon Tea Experience",
     "content": "Q: Do you serve afternoon tea?\nA: Our High Tea at the Lobby Lounge is a beloved tradition! Served 3–5 PM daily:\n• Classic set (2 pax): RM88 — scones, finger sandwiches, pastries, local kuih, premium tea selection\n• Premium set (2 pax): RM128 — adds oysters, foie gras, champagne\nLive piano music on weekends. The perfect indulgence on a lazy afternoon. Reservations recommended for weekends."},

    # ═══════════════════════════════════════════════════════════════
    # SPA & WELLNESS — Extended Treatments (~30)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "spa", "title": "Spa Treatment Menu Overview",
     "content": "Q: What spa treatments do you offer?\nA: Our Serenity Spa menu includes:\n• Balinese massage (60/90 min): RM180/250\n• Traditional Malay urut: RM200 (90 min)\n• Hot stone therapy: RM280 (90 min)\n• Aromatherapy massage: RM200 (60 min)\n• Deep tissue / Sports massage: RM220 (60 min)\n• Facial treatments: from RM150\n• Body scrubs & wraps: from RM160\n• Couples packages: from RM450\nAll treatments use premium organic products. Book early — we fill up fast!"},
    {"doc_type": "spa", "title": "Couples Spa Package",
     "content": "Q: What's included in the couples spa?\nA: Our Couples Harmony Package (2.5 hours, RM680/couple) includes:\n• Side-by-side massage (60 min, choice of style)\n• Shared flower bath soak (30 min)\n• Body scrub treatment (30 min)\n• Herbal tea and fruit platter\n• Access to steam room and relaxation lounge\nAlternatively, our Mini Couples Escape (90 min, RM450) includes massage and flower bath. Advance booking recommended!"},
    {"doc_type": "spa", "title": "Gym & Fitness Centre",
     "content": "Q: Do you have a gym?\nA: Our fitness centre operates 6 AM–10 PM daily. Equipment includes: treadmills, ellipticals, stationary bikes, free weights (up to 30 kg), cable machines, yoga mats, and stability balls. Complimentary towels and water. Personal training sessions available at RM120/hour. Morning yoga classes (7 AM, Tue/Thu/Sat) are complimentary for guests."},
    {"doc_type": "spa", "title": "Spa Booking & Availability",
     "content": "Q: When should I book my spa session?\nA: We recommend booking at least 24 hours in advance, especially during weekends and holidays. Walk-ins are welcome but subject to therapist availability. Please arrive 15 minutes early to complete a consultation form and enjoy the relaxation lounge. Cancellation less than 4 hours before is charged at 50%."},
    {"doc_type": "spa", "title": "Spa Products & Gift Shop",
     "content": "Q: Can I buy your spa products to take home?\nA: Yes! Our spa boutique sells our signature organic products — massage oils, body scrubs, aromatherapy oils, bath salts, and handmade soaps. All sourced from local Malaysian producers. Gift sets from RM80. The perfect memento or gift. Our therapist can recommend products based on your skin type."},

    # ═══════════════════════════════════════════════════════════════
    # POOL & RECREATION (~30)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "activities", "title": "Main Pool — Details & Rules",
     "content": "Q: Tell me about the swimming pool.\nA: Our infinity pool (25m x 12m, 1.2–1.8m depth) is open 7 AM–9 PM daily. Features: sun loungers, pool towels (free), poolside food & beverage service, change rooms with showers. Pool rules: no diving, no glass containers, children under 12 must be accompanied, no running on deck. Lifeguard on duty 9 AM–6 PM."},
    {"doc_type": "activities", "title": "Children's Pool & Water Playground",
     "content": "Q: Is there a pool for kids?\nA: Our children's pool area includes: a shallow splash pool (0.3–0.5m depth), mini water slides, mushroom fountain, and a separate toddler splash pad. Located next to the main pool with full view for parents. Open 8 AM–7 PM. Swim diapers required for children under 3. Our pool team regularly checks water quality — safety is paramount!"},
    {"doc_type": "activities", "title": "Water Sports — Kayaking, Snorkelling",
     "content": "Q: What water sports are available?\nA: Our water sports centre operates 9 AM–5 PM daily (weather permitting):\n• Kayak rental: RM50/hour (single), RM80/hour (double)\n• Stand-up paddleboard: RM60/hour\n• Snorkelling gear rental: RM40/half-day\n• Glass-bottom boat: RM80/person (45 min)\n• Jet ski: RM180/30 min\n• Banana boat: RM50/person (15 min ride)\nAll include safety briefing and life jackets. Minimum age varies by activity."},
    {"doc_type": "activities", "title": "Island Hopping Tour",
     "content": "Q: How do I book island hopping?\nA: Our most popular excursion! A full-day island hopping tour includes:\n• 3 islands visited (snorkelling, beach time, lunch)\n• Speedboat transfer, life jacket, snorkelling gear\n• Packed lunch and drinking water\n• Professional guide\n• RM180/adult, RM100/child (4–11), free under 4\n• Departs 9 AM, returns 4 PM\nBook at least 1 day in advance. Minimum 4 pax. Pure paradise!"},
    {"doc_type": "activities", "title": "Bicycle Rental",
     "content": "Q: Can we rent bicycles?\nA: Yes! We have 20 bicycles available (adults and children's sizes). Complimentary for the first 2 hours, then RM15/hour. Helmets provided. Our cycling route map highlights scenic paths along the coast and through the nearby fishing village (5 km loop, flat terrain). Perfect for a morning ride before the heat kicks in!"},
    {"doc_type": "activities", "title": "Golfing Nearby",
     "content": "Q: Is there a golf course nearby?\nA: The nearest 18-hole championship course is 20 minutes away. We can arrange:\n• Green fees: from RM180 (weekday) / RM280 (weekend)\n• Club rental: from RM80/set\n• Caddie: RM80\n• Hotel shuttle: RM50 return\nWe also have a putting green on-site for practice. Ask our concierge for tee time bookings — member rates available through our partnership!"},
    {"doc_type": "activities", "title": "Cooking Class — Malaysian Cuisine",
     "content": "Q: Do you offer cooking classes?\nA: Our Malaysian Cooking Class is every Wednesday and Saturday, 10 AM–1 PM:\n• Learn 3 signature dishes (nasi lemak, rendang, satay)\n• Market visit for fresh ingredients (optional add-on)\n• Hands-on cooking with our Head Chef\n• Eat what you cook for lunch\n• Recipe booklet to take home\n• RM120/person (min 4 pax)\nGuests consistently rate this as a highlight of their stay. Apron and chef hat included!"},

    # ═══════════════════════════════════════════════════════════════
    # FACILITIES — Extended (~30)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "facilities", "title": "Laundry & Dry Cleaning Service",
     "content": "Q: Do you have laundry service?\nA: Yes! Our laundry services:\n• Wash & fold: from RM10/item\n• Dry cleaning: from RM25/item\n• Express (same-day): 50% surcharge\n• Pressing only: RM8/item\nDrop-off before 9 AM for same-day return by 6 PM. Laundry bags and forms are in your wardrobe. Self-service launderette also available (RM15/load) for budget-conscious guests."},
    {"doc_type": "facilities", "title": "Gift Shop & Souvenirs",
     "content": "Q: What can I buy at the gift shop?\nA: Our gift shop (open 8 AM–10 PM) stocks:\n• Local handicrafts and batik items\n• Malaysian snacks and chocolates\n• Sunscreen, toiletries, first-aid essentials\n• Postcards, stamps, and travel essentials\n• Resort-branded merchandise\n• SIM cards and phone chargers\n• Newspapers and magazines\nGreat for last-minute gifts and forgotten travel items!"},
    {"doc_type": "facilities", "title": "Library & Reading Room",
     "content": "Q: Is there somewhere quiet to read?\nA: Our Library Lounge on Level 2 is a peaceful retreat with over 500 books (fiction, non-fiction, travel guides, children's books), daily newspapers, comfortable armchairs, and a Tea & Coffee corner (complimentary). Open 8 AM–10 PM. Borrow books to your room and return before check-out. Perfect for rainy afternoons."},
    {"doc_type": "facilities", "title": "Chapel & Prayer Room",
     "content": "Q: Is there a prayer room?\nA: Our multi-faith prayer room (surau) is on Level 1, open 24 hours. Equipped with prayer mats, telekung, kopiah, and qibla direction marker. Separate sections for men and women. For Christian worship, the nearest church is 15 minutes away — our concierge can provide details and arrange transport. All faiths are welcome and respected."},
    {"doc_type": "facilities", "title": "Electric Vehicle Charging",
     "content": "Q: Do you have EV charging stations?\nA: Yes! We have 4 EV charging bays (2x AC Type 2 at 7kW, 2x DC CCS2 at 50kW) located in our covered car park. Charging is complimentary for in-house guests. Please register your vehicle at the front desk for access. The DC fast charger can reach 80% in approximately 45 minutes. We're committed to supporting sustainable travel!"},
    {"doc_type": "facilities", "title": "Photography Spots on Property",
     "content": "Q: Where are the best photo spots?\nA: Our top 5 Instagram-worthy spots:\n1. Infinity pool edge (sunset golden hour)\n2. Garden pavilion with bougainvillea arch\n3. Beachfront swing (iconic!)\n4. Lobby grand staircase\n5. Rooftop sky bar panoramic view\nOur staff are happy to take photos for you. Professional photography sessions can be arranged at RM300/hour with a local photographer."},
]
