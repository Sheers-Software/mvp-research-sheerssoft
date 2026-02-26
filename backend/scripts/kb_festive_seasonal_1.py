"""
Segment C — Malaysian Festive Seasonality Knowledge Base (Part 1)
Categories: Hari Raya, CNY, Deepavali, Gawai, School Holidays, Peak Season, Festive F&B
~250 entries
"""

DOCS = [
    # ═══════════════════════════════════════════════════════════════
    # HARI RAYA AIDILFITRI (~100)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "hari_raya", "title": "Hari Raya Dates & Availability",
     "content": "Q: Do you have availability during Hari Raya?\nA: Selamat Hari Raya in advance! Hari Raya is our busiest period — bookings typically fill up 2–3 months ahead. We strongly recommend booking as early as possible. Peak rates apply during the Raya period (typically 7–10 days around Syawal). Would you like me to check availability for your dates?"},
    {"doc_type": "hari_raya", "title": "Hari Raya Rate Surcharge",
     "content": "Q: How much more expensive is it during Hari Raya?\nA: During the Hari Raya period, a peak season surcharge of 40–60% applies above normal rates. A minimum stay of 2–3 nights is also required. We know it's a premium, but the festive atmosphere, special meals, and celebrations make it worth every ringgit! Early bird discounts of 15% are available for bookings made 60+ days ahead."},
    {"doc_type": "hari_raya", "title": "Hari Raya Menu — Rendang & Ketupat",
     "content": "Q: Will you serve Hari Raya specialties?\nA: Of course! Our Hari Raya buffet is legendary — featuring ketupat, rendang daging, lemang, serunding, satay, kuih raya, and much more. It's a feast fit for the occasion! The buffet runs throughout the Raya period at our Horizon Café. RM88/person or complimentary for in-house guests on selected packages."},
    {"doc_type": "hari_raya", "title": "Hari Raya Activities & Open House",
     "content": "Q: Do you have Raya activities at the hotel?\nA: Yes! We celebrate with:\n• Hari Raya Open House (open to all guests & public)\n• Traditional kuih-making workshop\n• Baju Raya photo booth corner\n• Kompang welcome procession\n• Raya hamper giveaways\n• Special surau prayer arrangements\nIt's a wonderful way to experience Malaysian hospitality at its finest!"},
    {"doc_type": "hari_raya", "title": "Balik Kampung Season — Traffic Advice",
     "content": "Q: We're driving during Hari Raya — any traffic tips?\nA: Balik kampung traffic can be significant! Tips:\n• Depart very early (before 5 AM) or late at night\n• Avoid the eve and first day of Raya for highway travel\n• Pack snacks and entertainment for the kids\n• Use Waze/Google Maps for real-time traffic updates\n• Our estimated drive time may double during peak\nWe're here to welcome you whenever you arrive!"},
    {"doc_type": "hari_raya", "title": "Hari Raya Room Decoration",
     "content": "Q: Can you decorate our room for Raya?\nA: Selamat Hari Raya! We can arrange festive room decorations including pelita lights, ketupat ornaments, and fresh bunga rampai. Our standard Raya decoration package is RM80. Premium packages with hamper and traditional sweets from RM150. A lovely touch for celebrating away from home!"},
    {"doc_type": "hari_raya", "title": "Surau & Prayer Arrangements — Raya",
     "content": "Q: Where can we perform Solat Raya?\nA: Our surau is available for daily prayers and Solat Sunat Aidilfitri. For the main Solat Raya, the nearest mosque is 10 minutes away. We can arrange transport for interested guests. Prayer mats, telekung, and directions to qibla are available in your room on request during the festive period."},
    {"doc_type": "hari_raya", "title": "Hari Raya Minimum Stay",
     "content": "Q: Is there a minimum stay during Hari Raya?\nA: Yes, during the Hari Raya period (Eve to Day 3), we require a minimum 2-night stay. For our villas and larger properties, a 3-night minimum applies. This ensures all guests can enjoy the full festive experience. Single-night stays may be available from Day 4 onwards, subject to availability."},
    {"doc_type": "hari_raya", "title": "Hari Raya Haji Availability",
     "content": "Q: How about Hari Raya Haji?\nA: Hari Raya Haji is also a popular travel period, though usually less intense than Aidilfitri. A 20–30% peak surcharge applies. Our restaurant serves special Raya Haji menu including lamb and beef dishes. We recommend booking at least 2 weeks ahead. Selamat Hari Raya Haji!"},
    {"doc_type": "hari_raya", "title": "Hari Raya Cancellation Policy",
     "content": "Q: What if I need to cancel my Raya booking?\nA: Peak season cancellation terms:\n• 30+ days before: Full refund\n• 15–29 days: 50% refund\n• Less than 15 days: No refund\n• Date changes: Subject to availability, one change allowed\nWe understand emergencies happen — please reach out and we'll try to be as accommodating as possible."},

    # ═══════════════════════════════════════════════════════════════
    # CHINESE NEW YEAR (~100)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "cny", "title": "CNY Dates & Availability",
     "content": "Q: Do you have rooms during Chinese New Year?\nA: Gong Xi Fa Cai! Chinese New Year is extremely popular — many families book 3–6 months ahead. Peak rates apply from CNY Eve through Day 5 (and sometimes up to Chap Goh Mei). I'd recommend securing your booking as soon as possible. Shall I check what's available?"},
    {"doc_type": "cny", "title": "CNY Rate Premium",
     "content": "Q: Are CNY rates higher?\nA: Yes, a peak season surcharge of 50–80% applies during Chinese New Year (typically the highest of the year). Minimum stay of 2–3 nights is required. For the best value, book early for our early-bird CNY rates (20% discount for bookings 90+ days in advance). It's the biggest celebration of the year!"},
    {"doc_type": "cny", "title": "Reunion Dinner at Hotel",
     "content": "Q: Can we have our reunion dinner at your restaurant?\nA: We would be honoured! Our Grand Reunion Dinner menu features:\n• 8-course Chinese dinner: from RM128/pax\n• 10-course premium dinner: from RM188/pax\n• Special Yee Sang (Lou Hei) to start\n• Complimentary oranges and red packets for children\nReservations are essential — we sell out every year. Book early for the best selection of tables!"},
    {"doc_type": "cny", "title": "CNY Yee Sang Tossing Ceremony",
     "content": "Q: Do you do Yee Sang?\nA: Of course — it's not CNY without Lou Hei! Our chef prepares a spectacular prosperity toss (Yee Sang) with premium ingredients including abalone, salmon, and traditional fortune garnishes. Available at RM68 (standard) and RM138 (premium with abalone). Group tossing sessions are arranged during dinner service. Huat ah!"},
    {"doc_type": "cny", "title": "Lion Dance Performance",
     "content": "Q: Will there be a lion dance?\nA: Yes! We arrange a traditional lion dance troupe performance on the first and second day of CNY — complete with drums, cymbals, and firecrackers (where permitted). The lion will bless each floor of the hotel for prosperity. It's spectacular for children and adults alike. Performance times will be posted in the lobby."},
    {"doc_type": "cny", "title": "CNY Angpow / Red Packets",
     "content": "Q: Do you give angpow to guests?\nA: Every guest checking in during the CNY period receives a welcome angpow with hotel credits (RM18–88 luck draw) and complimentary mandarin oranges. Children receive special angpow kits. It's our way of wishing you 新年快乐 and making your celebration extra auspicious!"},
    {"doc_type": "cny", "title": "CNY Room Decorations",
     "content": "Q: Can you decorate our room for Chinese New Year?\nA: Gong Xi! We can arrange festive room setups:\n• Standard: red lanterns, spring couplets, mandarin oranges (RM60)\n• Premium: full décor + prosperity flowers + CNY treats hamper (RM150)\nOur lobby and restaurants are fully decorated for the season — very Instagram-worthy! The festive atmosphere is magical."},
    {"doc_type": "cny", "title": "CNY Fireworks & Activities",
     "content": "Q: Are there fireworks during CNY?\nA: While fireworks regulations vary by location, we typically arrange sparklers and LED celebrations on CNY Eve. Other activities include:\n• Calligraphy workshops\n• Fortune cookie making\n• Paper lantern crafting\n• CNY-themed kids' activities\n• Best dressed family photo competition\nThe whole resort embraces the festive spirit!"},
    {"doc_type": "cny", "title": "Vegetarian Menu for CNY",
     "content": "Q: We eat vegetarian during the first day of CNY — can you accommodate?\nA: Absolutely! This is a beautiful tradition. Our kitchen prepares a full vegetarian menu including vegetarian Yee Sang, mock meat dishes, and a dedicated vegetarian buffet section. Just let us know in advance and our chefs will ensure every dish is 100% vegetarian."},
    {"doc_type": "cny", "title": "Chap Goh Mei Celebration",
     "content": "Q: Do you celebrate Chap Goh Mei?\nA: Yes! On the 15th night (Chap Goh Mei), we host a special lantern night by the pool with tangerine tossing into the sea/pool for single ladies (Malaysian Valentine's tradition!). A special dinner menu and live entertainment make it a wonderful finale to the CNY celebrations. Great fun for everyone!"},

    # ═══════════════════════════════════════════════════════════════
    # DEEPAVALI (~80)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "deepavali", "title": "Deepavali Dates & Availability",
     "content": "Q: Are you available during Deepavali?\nA: Happy Deepavali! The Festival of Lights is a lovely time to stay with us. It falls in October–November and is typically a 3–5 day holiday period. A moderate peak surcharge (20–30%) applies. We usually have good availability if you book 2–3 weeks ahead. The resort is beautifully lit up — you'll love it!"},
    {"doc_type": "deepavali", "title": "Deepavali Menu & Cuisine",
     "content": "Q: Do you serve special Deepavali food?\nA: Yes! Our Deepavali dinner buffet features a spectacular spread of South Indian and North Indian cuisine — biryani, tandoori, masala dosa, paneer dishes, mutton varuval, plus an incredible array of traditional sweets (laddu, murukku, payasam). Vegetarian options are abundant. RM88/person or included in select packages."},
    {"doc_type": "deepavali", "title": "Deepavali Kolam & Decorations",
     "content": "Q: Will the hotel be decorated for Deepavali?\nA: Absolutely! Our lobby will feature a grand kolam (rice flour art), oil lamp displays, marigold garlands, and rangoli patterns. Each floor has festive lighting. For room decorations, we can arrange a Deepavali setup with diyas and flowers at RM50. The atmosphere is truly magical!"},
    {"doc_type": "deepavali", "title": "Deepavali Activities for Guests",
     "content": "Q: Are there Deepavali activities?\nA: We celebrate with:\n• Kolam-drawing workshop (learn the traditional art)\n• Henna/Mehndi artist sessions\n• Traditional Indian dance performance\n• Oil lamp lighting ceremony at dusk\n• Bollywood movie screenings\n• Kids' diya-painting activity\nAll are complimentary for in-house guests. It's a beautiful cultural experience!"},
    {"doc_type": "deepavali", "title": "Deepavali Vegetarian Options",
     "content": "Q: Can you cater for a vegetarian Deepavali celebration?\nA: Absolutely! Many of our Deepavali menu items are naturally vegetarian. We can prepare a fully vegetarian spread including paneer tikka, dal makhani, aloo gobi, chana masala, vegetable biryani, and a range of sweets. Just let us know and our chefs will create a dedicated vegetarian feast."},

    # ═══════════════════════════════════════════════════════════════
    # GAWAI DAYAK & KAAMATAN (~60)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "gawai", "title": "Gawai Dayak Celebrations",
     "content": "Q: Do you celebrate Gawai Dayak?\nA: Gayu Guru Gerai Nyamai! Gawai Dayak (June 1–2) is the Dayak harvest festival — hugely celebrated in Sarawak. If you're visiting Borneo during this period, expect vibrant longhouse visits, ngajat dance performances, and tuak (rice wine) tasting. We can arrange authentic Gawai cultural experiences for our guests!"},
    {"doc_type": "gawai", "title": "Gawai Dayak — Longhouse Visit",
     "content": "Q: Can you arrange a longhouse visit during Gawai?\nA: Yes! During Gawai season, many longhouses open their doors to visitors. We partner with local communities to arrange respectful, authentic visits including:\n• Traditional welcome ceremony\n• Tuak tasting and traditional food\n• Ngajat dance participation\n• Story-sharing with longhouse elders\nRM150/person including transport. A once-in-a-lifetime cultural experience!"},
    {"doc_type": "gawai", "title": "Kaamatan Festival — Sabah",
     "content": "Q: What is Kaamatan and do you celebrate it?\nA: Kotobian Tadau Tagazo do Kaamatan! Kaamatan is the harvest festival celebrated by the Kadazandusun people of Sabah (May 30–31). Festivities include the Unduk Ngadau beauty pageant, traditional sports, and tapai (rice wine) tasting. If you're in Sabah, it's a magnificent cultural celebration!"},
    {"doc_type": "gawai", "title": "Gawai / Kaamatan Availability",
     "content": "Q: Is it busy during Gawai?\nA: In East Malaysia (Sabah & Sarawak), Gawai and Kaamatan are major holidays — occupancy is high and a 30% peak surcharge applies. In Peninsular Malaysia, impact is minimal (not a public holiday). For East Malaysia stays, book at least 1 month in advance. It's an incredible time to experience Borneo culture!"},
    {"doc_type": "gawai", "title": "Borneo Cultural Cuisine — Gawai Special",
     "content": "Q: What special food is served during Gawai?\nA: Our Gawai menu features authentic Dayak cuisine:\n• Manok pansuh (chicken cooked in bamboo)\n• Umai (Sarawakian raw fish salad)\n• Tuak rice wine\n• Laksa Sarawak\n• Midin (wild jungle fern) stir-fry\n• Kek lapis Sarawak (layered cake)\nThese dishes showcase the incredible diversity of Borneo's food heritage!"},

    # ═══════════════════════════════════════════════════════════════
    # SCHOOL HOLIDAYS (~120)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "school_holidays", "title": "Malaysian School Holiday Calendar",
     "content": "Q: When are the school holidays in Malaysia?\nA: Malaysian school holiday periods (approximate):\n• Term 1 break: Mid-March (1 week)\n• Mid-year break: Late May – Mid-June (2–3 weeks)\n• Term 3 break: Mid-August (1 week)\n• Year-end: Mid-November – Early January (6–7 weeks)\nPeak rates apply during all school holidays. The June and year-end breaks are busiest. Book early for the best rates and availability!"},
    {"doc_type": "school_holidays", "title": "March School Holiday Rates",
     "content": "Q: Are rates higher during March school break?\nA: The March break is a short 1-week holiday — rates are 15–20% above standard. Availability is usually good with 2 weeks' advance booking. It's a great sweet spot: school holiday atmosphere without the extreme peak pricing of June or December. Families love it!"},
    {"doc_type": "school_holidays", "title": "June School Holiday — Peak Season",
     "content": "Q: How busy is June?\nA: June is our second busiest month! The 2–3 week mid-year school holiday means families flock to resorts and holiday homes. Peak surcharge of 30–50% applies. Minimum stay of 2 nights on weekends. We recommend booking 1–2 months ahead. Activities and kids' programmes run at full capacity — lots of fun!"},
    {"doc_type": "school_holidays", "title": "Year-End Holiday — November to January",
     "content": "Q: What about the year-end holidays?\nA: Mid-November to early January is our absolute peak season — school holidays plus Christmas plus New Year! Rates are at their highest (50–80% above standard). Properties book out completely. We cannot stress this enough: book as early as possible, ideally 3–6 months ahead. It's the most wonderful (and most expensive!) time of the year."},
    {"doc_type": "school_holidays", "title": "School Holiday Family Packages",
     "content": "Q: Do you have family packages for school holidays?\nA: Yes! Our School Holiday Family Bundle includes:\n• Family Suite or 3-Bedroom unit\n• Daily breakfast for 2 adults + 2 kids\n• Kids' Club access (full day)\n• 1× family activity voucher (choose from island hopping, cooking class, or nature walk)\n• Late check-out (2 PM)\nFrom RM1,200 for 2 nights. Great value for the whole family!"},
    {"doc_type": "school_holidays", "title": "Childcare During School Holidays",
     "content": "Q: We need some adult time during the holidays — any childcare?\nA: We completely understand! Our Kids' Club operates 9 AM–5 PM daily during school holidays with extended programming. For evening babysitting, our vetted babysitter service is available at RM50/hour (book 24 hours ahead). Parents deserve a date night — even on family holidays!"},

    # ═══════════════════════════════════════════════════════════════
    # PEAK SEASON & PRICING (~80)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "peak_season", "title": "Peak Season Calendar Overview",
     "content": "Q: When are your peak seasons?\nA: Our peak periods and typical surcharges:\n• Chinese New Year: 50–80%↑\n• Hari Raya Aidilfitri: 40–60%↑\n• School Holidays (June): 30–50%↑\n• Year-end (Nov–Jan): 50–80%↑\n• Deepavali: 20–30%↑\n• Gawai/Kaamatan: 30%↑ (East Malaysia)\n• Long weekends: 20–30%↑\nShoulder season (Feb, Apr, Sep–Oct) offers the best value."},
    {"doc_type": "peak_season", "title": "Off-Peak Best Value Periods",
     "content": "Q: When is the cheapest time to stay?\nA: Our best value periods are:\n• February (post-CNY): 10–15% below standard\n• April: Quiet, beautiful weather\n• September – October: Shoulder season, great rates\nDuring these months, you'll enjoy standard or discounted rates, fewer crowds, and full availability. The weather is typically excellent. It's the insider's secret!"},
    {"doc_type": "peak_season", "title": "Long Weekend Rates",
     "content": "Q: Are rates higher on long weekends?\nA: Yes, a 20–30% weekend/long weekend surcharge applies. Malaysia has about 15 public holidays that often create 3-day or 4-day weekends. These fill up quickly! For the best rates, arrive midweek or book 3+ weeks ahead. We also offer 'Stay 3 Pay 2' deals on selected long weekends — ask us!"},
    {"doc_type": "peak_season", "title": "Early Bird Peak Season Discount",
     "content": "Q: How early should I book for peak season?\nA: For the best peak-season rates:\n• 90+ days ahead: 20% early-bird discount\n• 60+ days ahead: 15% early-bird discount\n• 30+ days ahead: 10% early-bird discount\n• Last minute: Full peak rate (if available!)\nWe genuinely recommend booking 2–3 months ahead for major festive periods. Many properties sell out completely."},
    {"doc_type": "peak_season", "title": "Minimum Stay During Peak",
     "content": "Q: Is there a minimum stay during holidays?\nA: Yes, during peak/festive periods:\n• Standard rooms/homestays: 2-night minimum\n• Villas and chalets: 3-night minimum\n• CNY & Year-end peak: 3-night minimum for all\nThis ensures fair access for all guests and reduces turnover costs. Single-night stays may become available closer to the date if gaps remain."},
    {"doc_type": "peak_season", "title": "Deposit Policy — Peak Season",
     "content": "Q: Do I need to pay more deposit during peak season?\nA: For peak season bookings, we require a 50% deposit upon confirmation (vs 1-night deposit for standard). The balance is due 14 days before check-in. This helps us manage capacity fairly. Full payment may be required for non-refundable promotional rates."},

    # ═══════════════════════════════════════════════════════════════
    # PROMOTIONS & DEALS (~40)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "promotions", "title": "Cuti-Cuti Malaysia Deals",
     "content": "Q: Do you have any Malaysian specials?\nA: Yes! Our 'Cuti-Cuti Malaysia' rate is exclusively for MyKad holders — enjoy 20% off standard rates on selected dates. This is our way of encouraging Malaysians to explore our beautiful country. Just present your MyKad at check-in. Follow us on social media for flash Cuti-Cuti deals!"},
    {"doc_type": "promotions", "title": "Honeymooner Package",
     "content": "Q: Do you have a honeymoon deal?\nA: Congratulations! Our Honeymoon Package includes:\n• Executive Suite upgrade\n• Rose petal turndown & sparkling wine\n• Couples spa treatment (60 min)\n• Private dinner for two\n• Late check-out (2 PM)\n• Complimentary anniversary stay discount card\nFrom RM1,500 for 2 nights. A perfect start to your journey together!"},
    {"doc_type": "promotions", "title": "Birthday Month Offer",
     "content": "Q: I'm celebrating my birthday this month!\nA: Happy Birthday! Birthday guests enjoy 20% off room rates when staying during their birthday month (MyKad/passport verification required). We'll also prepare a complimentary slice of cake and a birthday card in your room. Life's too short not to celebrate — let us make it special!"},
    {"doc_type": "promotions", "title": "Weekday Escape Package",
     "content": "Q: Any deals for weekday stays?\nA: Our Weekday Escape (Sun–Thu) offers 25% off standard rates plus a complimentary room upgrade (subject to availability). Includes late check-out until 2 PM. It's perfect for remote workers, retirees, or anyone who can travel midweek. Same beautiful resort, significantly better rates!"},
    {"doc_type": "promotions", "title": "Group & Reunion Discount",
     "content": "Q: We're planning a family reunion — any group deals?\nA: How wonderful! For groups booking 5+ rooms/units:\n• 5–9 rooms: 10% off + welcome drinks\n• 10–14 rooms: 15% off + 1 complimentary room\n• 15+ rooms: 20% off + 2 complimentary rooms + private event space\nWe can also arrange matching activities, group dining, and a memorable gathering. Family reunions are our joy!"},

    # ═══════════════════════════════════════════════════════════════
    # FESTIVE — General & Other Festivals (~50)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "festive", "title": "Christmas & New Year Celebration",
     "content": "Q: What do you do for Christmas?\nA: Merry Christmas! Our celebrations include:\n• Christmas Eve dinner: 5-course set menu (RM168/pax)\n• Christmas Day brunch buffet with live carving station\n• Santa visit and gift-giving for children\n• Christmas tree lighting ceremony\n• Carolling performance by local choir\n• New Year's Eve countdown party with DJ\n• NYE fireworks display (where permitted)\nIt's the most wonderful time at Grand Horizon!"},
    {"doc_type": "festive", "title": "New Year's Eve Countdown",
     "content": "Q: What's happening on New Year's Eve?\nA: Our NYE celebration is legendary:\n• Grand Buffet Dinner: RM228/pax (all you can eat & drink)\n• Live band and DJ from 9 PM\n• Midnight countdown with fireworks\n• Complimentary champagne toast at midnight\n• Party runs until 2 AM\nRoom packages including the countdown party start from RM650/night. Book early — this sells out every year!"},
    {"doc_type": "festive", "title": "Thaipusam Holiday Period",
     "content": "Q: Are you open during Thaipusam?\nA: Yes, we're open! Thaipusam is a public holiday (usually January–February). A moderate 15–20% surcharge applies if it falls on a long weekend. We can arrange transport to nearby Thaipusam celebrations for interested guests. It's a powerful and colourful cultural experience."},
    {"doc_type": "festive", "title": "Merdeka & Malaysia Day",
     "content": "Q: What about Merdeka holidays?\nA: Merdeka Day (August 31) and Malaysia Day (September 16) are patriotic holidays. If they create a long weekend, expect 20–30% peak rates. We celebrate with:\n• Malaysian flag displays and themed decorations\n• Patriotic cultural performances\n• Special 'Taste of Malaysia' food festival\n• Merdeka merchandise at the gift shop\nMerdeka! 🇲🇾"},
    {"doc_type": "festive", "title": "Valentine's Day Special",
     "content": "Q: Do you have Valentine's Day packages?\nA: Yes! Our Valentine's Package includes:\n• Deluxe room with sea view\n• Rose petal turndown\n• Candlelit dinner for two at Sunset Grill\n• Couples spa (30-minute head & shoulder massage)\n• Late check-out until 2 PM\nFrom RM888/night (lucky number!). Also available for anniversaries and special occasions. Love is in the air!"},
    {"doc_type": "festive", "title": "Nuzul Quran & Islamic Holidays",
     "content": "Q: Are you operating during Islamic holidays?\nA: We operate as normal during all Islamic holidays (Nuzul Quran, Israk & Mikraj, Maulidur Rasul, Awal Muharram). Our surau is available for prayers. Special Islamic holiday buffets are prepared with additional traditional dishes. Public holiday surcharges may apply if they create a long weekend."},
    {"doc_type": "festive", "title": "Monsoon Season Travel Advisory",
     "content": "Q: Should I avoid travelling during monsoon season?\nA: The East Coast monsoon (Nov–Feb) can bring heavy rain and rough seas, affecting beach activities and island access. The West Coast is generally fine year-round. Our property operates normally during monsoon — we just adjust outdoor activities. Indoor experiences (spa, dining, cooking classes) become even more popular. Rainy days can be incredibly cosy!"},
    {"doc_type": "festive", "title": "Ramadan Dining Arrangements",
     "content": "Q: How does dining work during Ramadan?\nA: During Ramadan, we make special arrangements:\n• Sahur (pre-dawn) meal: 4:30 AM–5:30 AM (packed or buffet)\n• Regular lunch service continues for all guests\n• Iftar (breaking fast) buffet: from 7:15 PM, RM68/pax\n• Extended restaurant hours\nFasting guests receive complimentary dates and zamzam water. Non-fasting guests can dine as normal throughout the day."},
    {"doc_type": "festive", "title": "Festive Season Group Booking Tips",
     "content": "Q: Any tips for booking during festive seasons?\nA: Top tips from our team:\n1. Book 2–3 months ahead for major festivals\n2. Be flexible with dates — shifting by 1–2 days can save 20%\n3. Ask about early-bird discounts\n4. Consider midweek arrival to avoid traffic\n5. Join our loyalty programme for priority access\n6. Follow us on social media for flash sales\n7. Direct bookings get the best cancellation flexibility!"},
]
