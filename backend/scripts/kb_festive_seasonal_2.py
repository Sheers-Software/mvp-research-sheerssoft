"""
Segment C — Malaysian Festive Seasonality Knowledge Base (Part 2)
Expanded: more festive variants, Bahasa Malaysia queries, seasonal activities, weather
~200 entries
"""

DOCS = [
    # ═══════════════════════════════════════════════════════════════
    # HARI RAYA — Extended Scenarios (~30)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "hari_raya", "title": "Raya Eve Dinner — Malam Raya",
     "content": "Q: Do you have a special dinner on Raya Eve?\nA: Yes! Our Malam Raya dinner buffet is one of our highlights:\n• Traditional rendang, lemang, ketupat, serunding\n• Live satay station and sup tulang\n• Kuih raya spread — 20+ varieties!\n• Entertainment: kompang performance and silat demonstration\n• RM98/adult, RM48/child (4–11), free under 4\nRaya Eve has a magical atmosphere — our lobby is lit with pelita and bunga rampai scents. A night to remember!"},
    {"doc_type": "hari_raya", "title": "Hari Raya Outfit Coordination",
     "content": "Q: Is there somewhere to get baju Raya alterations nearby?\nA: Yes! There's a skilled tailor in the town centre (15 min drive) who does last-minute alterations. Our concierge can also help with:\n• Ironing/pressing your baju raya (complimentary for guests)\n• Flower corsage arrangements (from RM20)\n• Professional photographer for family Raya photos (RM200/30 min session)\nLooking your best for Raya is important — we'll help make it perfect!"},
    {"doc_type": "hari_raya", "title": "Solat Aidilfitri Arrangements",
     "content": "Q: Where do we go for Solat Raya?\nA: The nearest mosque for Solat Aidilfitri is Masjid Jamek (10 min drive). Solat time is typically 8:00–8:30 AM. We arrange complimentary shuttle buses departing 7:30 AM from the lobby. Prayer mats and telekung are available at our surau. After Solat, return for our grand Raya Open House buffet!"},
    {"doc_type": "hari_raya", "title": "Raya Hamper & Gift Services",
     "content": "Q: Can you help me send Raya hampers to family?\nA: Absolutely! We offer curated Raya hampers:\n• Classic hamper (cookies, dates, drinks): RM120\n• Premium hamper (chocolate, nuts, specialty items): RM250\n• Corporate hamper (branded, custom message): from RM180\nDelivery within Peninsular Malaysia included. Order 5+ days before Raya for guaranteed delivery. A beautiful way to spread festive joy!"},
    {"doc_type": "hari_raya", "title": "Raya Bazaar & Shopping",
     "content": "Q: Where can we shop for Raya items nearby?\nA: The nearest Raya bazaar is in the town centre (15 min), operating from 2 weeks before Raya, 10 AM–10 PM:\n• Baju Raya: traditional and modern styles\n• Kuih raya and cookies\n• Home decorations and curtains\n• Pelita and festive lighting\n• Raya cards and gifts\nWe can arrange transport. The atmosphere is buzzing — part of the Raya experience!"},

    # ═══════════════════════════════════════════════════════════════
    # CHINESE NEW YEAR — Extended (~30)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "cny", "title": "CNY Steamboat / Hotpot Night",
     "content": "Q: Can we have a steamboat dinner during CNY?\nA: Yes! Our CNY Steamboat Night runs on the 2nd day of Chinese New Year:\n• Premium seafood, wagyu beef, and chicken slices\n• Mushroom assortment and vegetables\n• 3 soup bases (tom yam, herbal, collagen)\n• Unlimited servings\n• RM108/adult, RM58/child\nPerfect for gathering the family around the table. The bubbling hotpot brings everyone together!"},
    {"doc_type": "cny", "title": "CNY Mandarin Orange Tradition",
     "content": "Q: What's the deal with mandarin oranges?\nA: Mandarin oranges symbolise prosperity and good fortune during CNY. We present 2 oranges to every arriving guest as a welcoming gesture. Oranges are also exchanged between guests as a sign of well-wishes. Our lobby features a beautiful kumquat tree — feel free to take a photo! May your new year be as sweet as these oranges 🍊"},
    {"doc_type": "cny", "title": "CNY Operating Hours",
     "content": "Q: Are all facilities open during CNY?\nA: Operating hours during CNY:\n• Restaurants: normal hours (special CNY menus)\n• Spa: open but reduced hours on Day 1 (12 PM–8 PM)\n• Pool & gym: normal hours\n• Kids' Club: open with special CNY craft activities\n• Concierge: 24/7 as usual\n• Gift shop: extended hours (8 AM–11 PM)\nSome external attractions and restaurants may close for 1–3 days — we can advise on what's open."},
    {"doc_type": "cny", "title": "CNY Family Portrait Session",
     "content": "Q: Can we get family photos taken in our CNY outfits?\nA: Wonderful idea! We offer:\n• In-house photographer: RM200/30 min session (lobby/garden backdrop)\n• Self-service photo booth: free, with CNY props and digital frames\n• Professional studio session (off-site): RM350, 1 hour, includes 10 edited photos\nMany families treasure these annual CNY portraits. Book the photographer early — slots fill quickly!"},
    {"doc_type": "cny", "title": "God of Prosperity Appearance",
     "content": "Q: Do you have a God of Prosperity character?\nA: Yes! Our Choy San (God of Prosperity) makes appearances in the lobby on Day 1 and 2 of CNY (10 AM–12 PM and 3–5 PM). He distributes lucky coins and poses for photos with guests. Children absolutely love it! The lion dance troupe also performs — it's a spectacular and auspicious experience."},

    # ═══════════════════════════════════════════════════════════════
    # DEEPAVALI — Extended (~20)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "deepavali", "title": "Deepavali Oil Bath Tradition",
     "content": "Q: Can we perform the traditional oil bath at the hotel?\nA: We respect this beautiful tradition! For Deepavali morning, we provide:\n• Warm sesame oil (gingelly oil) on request\n• Extra towels for the morning ritual\n• Early hot water availability (from 4 AM)\n• Special turmeric paste if requested 24 hours in advance\nPlease let us know beforehand so we can prepare everything for your family's auspicious morning."},
    {"doc_type": "deepavali", "title": "Deepavali Sweet-Making Workshop",
     "content": "Q: Can we learn to make Deepavali sweets?\nA: How wonderful! Our kitchen team offers a Deepavali sweet-making class:\n• Learn to make laddu, murukku, and kesari\n• 2-hour hands-on session\n• RM80/person (includes ingredients and take-home box)\n• Runs 2 days before Deepavali and on Deepavali Eve\nIt's a joyful, social, and slightly messy experience — perfect for families and friends!"},
    {"doc_type": "deepavali", "title": "Fireworks Display — Deepavali",
     "content": "Q: Are there fireworks during Deepavali?\nA: While large fireworks displays are regulated, our property hosts a supervised sparkler celebration on Deepavali Eve at the garden area (8 PM). We also have LED light displays and candle arrangements throughout the resort. The entire property glows with diyas (oil lamps) — it's absolutely breathtaking. A true Festival of Lights!"},

    # ═══════════════════════════════════════════════════════════════
    # CHRISTMAS & YEAR-END — Extended (~25)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "festive", "title": "Christmas Tree Lighting Ceremony",
     "content": "Q: When is the Christmas tree lighting?\nA: Our annual Christmas Tree Lighting Ceremony is on December 1st at 7 PM in the lobby. Features:\n• 6-metre decorated tree\n• Carol singing by local children's choir\n• Santa's arrival with gifts for children\n• Mulled wine and mince pies for adults\n• Hot chocolate and cookies for kids\nThe festive spirit takes over from this magical evening. All guests welcome!"},
    {"doc_type": "festive", "title": "Christmas Day Brunch Buffet",
     "content": "Q: What's for Christmas lunch?\nA: Our Christmas Day Champagne Brunch (11 AM–3 PM) is a showstopper:\n• Roast turkey with all the trimmings\n• Glazed honey ham and roast beef\n• Fresh seafood bar (oysters, prawns, salmon)\n• International spread with Asian favourites\n• Dessert table with yule log, pavlova, and Christmas pudding\n• Free-flow champagne and juices\n• RM188/adult, RM88/child. Reservations essential!"},
    {"doc_type": "festive", "title": "New Year's Eve Gala Dinner",
     "content": "Q: Tell me about the NYE celebration.\nA: Our New Year's Eve Gala (7 PM–2 AM) is the highlight of the year:\n• 5-course set dinner with wine pairing\n• Live band performing hits from every decade\n• Countdown projection on the building facade\n• Midnight champagne toast\n• Fireworks display at midnight\n• DJ and dancing until 2 AM\n• RM388/person (RM688/couple). Room + NYE packages from RM1,200/night."},
    {"doc_type": "festive", "title": "Year-End Holiday Activities",
     "content": "Q: What activities run during the December holidays?\nA: December is packed with fun:\n• Daily Kids' Club activities (extended hours)\n• Beach games tournament\n• Sandcastle building competition\n• Movie nights by the pool\n• Treasure hunt around the resort\n• Santa's Grotto & gift-giving (Dec 24–25)\n• NYE family countdown party (alcohol-free zone)\nThere's something for every age — families love our December programming!"},

    # ═══════════════════════════════════════════════════════════════
    # MONSOON & WEATHER — Seasonal Guidance (~20)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "peak_season", "title": "East Coast Monsoon Advisory",
     "content": "Q: Is it safe to travel to the East Coast during monsoon?\nA: The East Coast monsoon (Nov–Feb) brings heavy rain and rough seas. Impact:\n• Island resorts close (Perhentian, Redang, Lang Tengah)\n• Beach activities limited\n• Some coastal roads may flood briefly\n• Flight delays possible\nMainland resorts remain open with indoor activities. If you love rain and solitude, it's actually a beautifully moody time. Prices are at their lowest!"},
    {"doc_type": "peak_season", "title": "Best Beach Season — West Coast",
     "content": "Q: When is the best time for beach holidays?\nA: West Coast beaches (Langkawi, Penang, Pangkor) are best year-round with the driest period March–October. East Coast (Terengganu, Kelantan, Pahang coast) is best March–September when seas are calm and water is crystal clear. For island diving, April–August offers the best visibility. We can recommend the perfect destination for your dates!"},
    {"doc_type": "peak_season", "title": "Rainy Day Activities",
     "content": "Q: What if it rains on our holiday?\nA: Don't worry — tropical rain usually passes within 1–2 hours! Meanwhile:\n• Board games and card games (available at front desk)\n• Indoor pool / games room\n• Movie marathon in your room\n• Spa treatments\n• Cooking class\n• Shopping in town\n• Read a book to the sound of rain on the roof (pure bliss!)\nRain is part of the tropical experience — and everything looks greener afterwards!"},
    {"doc_type": "peak_season", "title": "Haze Season Advisory",
     "content": "Q: What about haze season?\nA: Transboundary haze (typically Aug–Oct) can affect air quality. During haze:\n• Check API readings (we'll advise if unhealthy)\n• Outdoor activities may be rescheduled\n• Indoor activities are unaffected\n• Air purifiers available on request\n• N95 masks available at front desk\nSevere haze is unpredictable — we'll communicate proactively and adjust activities accordingly. Your health comes first."},

    # ═══════════════════════════════════════════════════════════════
    # PROMOTIONS — Extended Seasonal Deals (~20)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "promotions", "title": "Merdeka Weekend Special",
     "content": "Q: Any Merdeka deals?\nA: Merdeka! Our Merdeka Weekend Package (Aug 30–Sep 2):\n• 2 nights in Deluxe room\n• Patriotic welcome drink\n• Malaysian food trail dinner\n• Complimentary flag bandana and festive pin\n• Late check-out until 2 PM\n• From RM588 for 2 nights\nCelebrate our nation's independence with a staycation! MyKad holders receive an additional 10% off."},
    {"doc_type": "promotions", "title": "Romantic Anniversary Package",
     "content": "Q: We're celebrating our anniversary!\nA: Congratulations! Our Anniversary Romance Package:\n• Junior Suite upgrade (subject to availability)\n• Rose petal bed decoration and scented candles\n• Champagne and chocolate-dipped strawberries\n• Couples sunset spa treatment (60 min)\n• Candlelit dinner at Sunset Grill\n• Late check-out until 3 PM\n• From RM1,800 for 2 nights. Love deserves celebration!"},
    {"doc_type": "promotions", "title": "Workation Package — Digital Nomads",
     "content": "Q: I work remotely — any long-stay work packages?\nA: Our Workation Package is designed for digital nomads:\n• Stay 7+ nights in a Deluxe Room\n• High-speed Wi-Fi guaranteed\n• Dedicated workspace in room + Business Centre access\n• Daily breakfast and 3× weekly laundry\n• Pool and gym access\n• From RM250/night (standard rate RM380)\n• 14+ nights: RM200/night\nSeveral remote workers have adopted us as their 'office with a view'!"},
    {"doc_type": "promotions", "title": "Flash Sale — Last-Minute Deals",
     "content": "Q: Do you ever have last-minute deals?\nA: Yes! Follow us on Instagram and WhatsApp Broadcast for flash sales — typically announced 3–5 days before the dates, with up to 40% off. These are for remaining unsold inventory and can be incredible value. Subscribe to our WhatsApp Broadcast list by messaging 'SUBSCRIBE' to this number. Deals go fast!"},
    {"doc_type": "promotions", "title": "Teacher's Day Special",
     "content": "Q: Do you have a Teacher's Day promotion?\nA: We appreciate our educators! Around Teacher's Day (May 16), valid teacher ID card holders get:\n• 15% off room rates\n• Complimentary room upgrade (subject to availability)\n• Free dessert at any restaurant\nBecause teachers shape the future. Valid for stays within May 1–31. Thank you for your service to education!"},
]
