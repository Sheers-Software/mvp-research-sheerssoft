"""
Segment B — Homestay, Villa, Chalet, Inn Knowledge Base (Part 3)
Expanded: BBQ, outdoor cooking, pet policies, long-stay, group rules, cleaning
~40 entries
"""

DOCS = [
    # ═══════════════════════════════════════════════════════════════
    # BBQ & OUTDOOR COOKING (~10)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "self_catering", "title": "BBQ Pit — Usage & Equipment",
     "content": "Q: Can we use the BBQ pit?\nA: Yes! Our BBQ setup includes:\n• Charcoal BBQ pit (cleaned before each guest)\n• BBQ tongs, spatula, and wire brush\n• Charcoal: 1 bag provided free, extras RM12/bag\n• Lighter fluid and matches\n• Outdoor dining table and chairs\nPlease clean grill after use and dispose of ash in the metal bin (not dustbin!). BBQ is allowed until 11 PM. Put out all embers completely before going to bed."},
    {"doc_type": "self_catering", "title": "Kitchen Equipment List",
     "content": "Q: What cooking equipment is in the kitchen?\nA: Our fully equipped kitchen includes:\n• Rice cooker (10-cup), electric kettle\n• Gas stove (2-burner), microwave\n• Wok, frying pan, saucepan, cooking pot\n• Chopping board, knives, peeler\n• Plates, bowls, cups, glasses (for max occupancy)\n• Cutlery set, serving spoons, ladle\n• Dish soap, sponge, drying rack\n• Toaster and blender (select properties)\nBasically everything you need to make a feast!"},
    {"doc_type": "self_catering", "title": "Where to Buy Groceries",
     "content": "Q: Where's the nearest shop for groceries?\nA: Grocery options near the property:\n• Mini-mart: 5 minutes' walk (basics, snacks, drinks)\n• 99 Speedmart: 10 minutes' drive (good range, fair prices)\n• Mydin / Giant hypermarket: 20 minutes' drive (full supermarket)\n• Local morning market (pasar): daily 6–9 AM, 10 min drive (freshest produce!)\n• We can arrange grocery delivery for an extra RM15 service fee\nA shopping list template is in the house guide!"},

    # ═══════════════════════════════════════════════════════════════
    # HOUSE RULES — Extended (~10)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "house_rules", "title": "Noise & Quiet Hours",
     "content": "Q: Are there quiet hours?\nA: Yes, for the comfort of neighbours and the community:\n• Quiet hours: 11 PM – 7 AM\n• No loud music, karaoke, or shouting after 11 PM\n• Pool/garden activities wind down by 10 PM\n• Indoor conversations and TV at reasonable volume are fine\nWe've had occasional complaints from neighbours, so we do enforce this rule. Thank you for being considerate — our community appreciates it!"},
    {"doc_type": "house_rules", "title": "Maximum Occupancy Enforcement",
     "content": "Q: Can we bring more people than the listing says?\nA: Our maximum occupancy is strictly enforced for safety and comfort:\n• Insurance coverage is only valid for the listed max occupancy\n• Extra guests beyond the limit incur RM50/person surcharge\n• Exceeding max by more than 2 is not permitted\n• Day visitors (not staying overnight) are allowed with prior notice\nPlease be honest about guest numbers — it's about safety, not revenue!"},
    {"doc_type": "house_rules", "title": "Rubbish Disposal & Recycling",
     "content": "Q: Where do we throw the rubbish?\nA: Rubbish disposal:\n• General waste: large bin at the driveway (black bag)\n• Recyclables: separate bin (blue bag) — bottles, cans, paper, plastic\n• Food waste: smaller kitchen bin, please bag it before disposal\n• Collection days: Tue/Thu/Sat\nPlease don't leave rubbish outside on non-collection days (attracts animals). If the bin is full, just bag it and leave inside — our cleaner will handle it."},
    {"doc_type": "house_rules", "title": "Shoes Policy — Indoor",
     "content": "Q: Should we remove shoes indoors?\nA: We kindly request shoes-off indoors:\n• Asian custom — keeps the floors clean and hygienic\n• Outdoor shoe shelf at the entrance\n• Indoor slippers provided (2 pairs per bedroom)\n• We deep-clean between guests but shoe-free helps maintain standards\nIf you forget — no worries, but we appreciate the effort! Our floors are cool tile, perfect for bare feet in the tropical heat."},

    # ═══════════════════════════════════════════════════════════════
    # POOL & GARDEN — Private Properties (~10)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "villa", "title": "Private Pool — Maintenance & Rules",
     "content": "Q: How is the private pool maintained?\nA: Our pool maintenance:\n• Cleaned and treated before each guest arrival\n• Pool pump runs automatically (you may hear it, it's normal)\n• Chemical balance checked by our team every 3 days during your stay\n• Pool depth: typically 1.2–1.5m (shallow end 0.8m)\nRules: no glass near pool, no diving (shallow!), children must be supervised, no food in the water, shower before swimming. Pool lights switch off at 11 PM."},
    {"doc_type": "villa", "title": "Garden & Outdoor Maintenance",
     "content": "Q: Who maintains the garden during our stay?\nA: The garden is our pride:\n• Grass is mowed before each guest arrival\n• Basic maintenance by our gardener every 3 days (minimal disruption)\n• Outdoor furniture is weather-resistant — leave it out\n• Please don't pick fruits from the trees without asking (some are neighbours'!)\n• Insect repellent candles and coils available in the utility drawer\nThe tropical garden is perfect for morning coffee and sunset relaxation."},

    # ═══════════════════════════════════════════════════════════════
    # LONG STAY & WORK FROM HOME (~8)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "homestay", "title": "Monthly Rental Rate",
     "content": "Q: Do you offer monthly rates?\nA: Yes! Monthly stays are ideal for:\n• Remote workers seeking a 'workation'\n• Families relocating temporarily\n• Project-based professionals\nMonthly rate: typically 50–60% of the nightly rate x 30 days. Includes: weekly cleaning, linen change, Wi-Fi, and utilities (cap applies). Contact us for a personalised quote — long-stays are our forte!"},
    {"doc_type": "homestay", "title": "Work From Home Setup",
     "content": "Q: Is the property suitable for working from home?\nA: Our properties are WFH-friendly:\n• Stable Wi-Fi (30–50 Mbps)\n• Dedicated work desk and comfortable chair (most units)\n• Natural lighting in living areas\n• Quiet neighbourhood\n• Nearby cafés with Wi-Fi for variety\n• Extension cords and phone chargers provided\nMany digital nomads have given us 5 stars for productivity. The view from the desk beats any office!"},
    {"doc_type": "homestay", "title": "Utility Cap for Long Stays",
     "content": "Q: Are utilities included in the monthly rate?\nA: For monthly stays:\n• Water: included (normal household usage)\n• Electricity: RM200/month cap included; excess charged per TNB bill\n• Wi-Fi: included (unlimited)\n• Gas: included (cooking use)\nThe RM200 electricity cap covers normal aircon usage (set at 24°C for 10–12 hours/day). Running aircon 24/7 at 16°C will exceed the cap! We'll share the meter reading at start and end."},

    # ═══════════════════════════════════════════════════════════════
    # CLEANING & TURNOVER (~6)
    # ═══════════════════════════════════════════════════════════════
    {"doc_type": "housekeeping", "title": "Check-Out Cleaning Expectations",
     "content": "Q: How clean should we leave the property?\nA: We don't expect hotel-level cleaning! Just basic tidiness:\n• Wash and dry dishes, put away\n• Take out rubbish to the bins\n• Sweep obvious messes (sand, food crumbs)\n• Strip used bed linen and pile on bed\n• Check fridge — take your items, leave it clean\nA professional cleaning team comes after every check-out. The RM200 security deposit covers professional cleaning. Just leave it tidy, not spotless!"},
    {"doc_type": "housekeeping", "title": "Mid-Stay Cleaning Service",
     "content": "Q: Can we get cleaning during our stay?\nA: Cleaning during stay:\n• Stays of 3+ nights: one complimentary clean included (on day 2 or 3)\n• Additional cleaning: RM80 per session\n• Includes: bathroom clean, floor sweep/mop, bed-making, bin emptying, kitchen tidy\n• Duration: approximately 1–2 hours\nSchedule with us in advance so our cleaner can plan. Towel and linen exchange included with each clean."},
]
