# BM/Manglish Test Suite — Nocturn AI
## P0.6 Acceptance Gate · 50 Questions · Pass Rate Required: ≥ 80%
### Property: Vivatel Kuala Lumpur · Updated: 17 Mar 2026

---

## How to Run This Test

1. Send each question to the Vivatel WhatsApp number (Twilio sandbox) exactly as written — no corrections, no rewording
2. Record the AI response verbatim
3. Score each response: **PASS / FAIL / PARTIAL**
4. Log failures with the category and failure mode
5. If pass rate < 80% (< 40 of 50): stop, fix prompt/KB, re-run before Phase 1

**Pass criteria per question are in the rightmost column. A response PASSES if it meets all criteria listed.**

---

## Scoring Sheet

| # | Category | Question | Pass Criteria | Result | Notes |
|---|----------|----------|---------------|--------|-------|
| | | | | | |

*(Fill in Result and Notes during test execution)*

---

## Category Breakdown

| Category | Questions | Target Pass |
|----------|-----------|-------------|
| A — Standard Room Inquiries (BM) | 1–8 | ≥ 7/8 |
| B — Rate & Pricing (BM/Manglish) | 9–14 | ≥ 5/6 |
| C — After-Hours Messages | 15–20 | ≥ 5/6 |
| D — Complaints | 21–25 | ≥ 4/5 |
| E — Group Bookings (Manglish) | 26–30 | ≥ 4/5 |
| F — Code-Switching Mid-Sentence | 31–36 | ≥ 5/6 |
| G — Directions & Location (BM) | 37–40 | ≥ 3/4 |
| H — Facilities (BM) | 41–44 | ≥ 3/4 |
| I — Polite Refusal / Unavailability | 45–47 | ≥ 2/3 |
| J — Ambiguous / Informal Input | 48–50 | ≥ 2/3 |

---

## Category A — Standard Room Inquiries (BM)
*Tests: Can the AI understand and respond to standard booking questions in Bahasa Malaysia?*

---

**Q1**
```
Ada bilik kosong untuk 2 malam tak? Nak masuk 20 March, keluar 22 March.
```
**Pass criteria:**
- Responds in BM (or bilingual BM+EN)
- Asks for number of guests OR confirms room availability context
- Does NOT respond in English only
- Does NOT hallucinate specific room availability (no live PMS connection)

---

**Q2**
```
Berapa jenis bilik yang ada di hotel ni?
```
**Pass criteria:**
- Lists room types available at Vivatel (Superior / Deluxe / Suite or whatever KB says)
- Responds in BM
- If KB not yet populated: gracefully says it will check and asks for contact details, does NOT make up room types

---

**Q3**
```
Saya nak tempah bilik untuk 2 orang dewasa dan 1 kanak-kanak. Ada bilik yang sesuai?
```
**Pass criteria:**
- Acknowledges the request (2 adults + 1 child)
- Asks for check-in/check-out dates OR directs to reservation
- Responds in BM
- Does NOT give a definitive "yes we have it" without KB data to back it up

---

**Q4**
```
Bilik paling murah berapa sekarang?
```
**Pass criteria:**
- Provides a rate from KB, OR says rates vary and offers to help find the best option
- Responds in BM
- Does NOT say "I don't know" without offering a next step
- If rate not in KB: asks for dates and guest count before answering

---

**Q5**
```
Ada tak bilik yang ada pemandangan kolam renang? Nak tahu berapa harganya.
```
**Pass criteria:**
- Addresses the pool view request specifically
- If KB has pool view rooms: mentions them with rate
- If not: says it will check and captures contact details
- Responds in BM

---

**Q6**
```
Boleh tak check in awal? Saya sampai pukul 8 pagi.
```
**Pass criteria:**
- Addresses early check-in request
- States policy from KB (e.g., "Early check-in subject to availability, extra charge may apply")
- If policy not in KB: says it needs to check and captures contact info
- Responds in BM

---

**Q7**
```
Check out pukul berapa?
```
**Pass criteria:**
- States check-out time from KB (e.g., "12:00 tengah hari")
- Short, direct answer
- Responds in BM
- Does NOT give wrong time

---

**Q8**
```
Saya nak bilik honeymoon. Ada ke?
```
**Pass criteria:**
- Responds warmly (appropriate tone for romantic occasion)
- If honeymoon package in KB: describes it
- If not: suggests closest equivalent (Suite, Deluxe) and captures contact details
- Responds in BM
- Does NOT respond coldly / robotically

---

## Category B — Rate & Pricing (BM/Manglish)
*Tests: Can the AI handle pricing questions across BM and Manglish variations?*

---

**Q9**
```
Harga bilik standard untuk weekend berapa ye?
```
**Pass criteria:**
- Provides weekend rate from KB OR says it depends on dates and availability
- Responds in BM
- Does NOT give a made-up number not in KB

---

**Q10**
```
Got any special package or promo tak? Honeymoon ke, anniversary ke.
```
*(Manglish: BM "tak" at the end of an English sentence)*
**Pass criteria:**
- Responds in the same code-switching style OR in BM/English
- Mentions packages from KB if available
- Does NOT ignore the question

---

**Q11**
```
Kalau book terus dengan hotel, lebih murah ke dari Booking.com?
```
**Pass criteria:**
- Addresses direct booking advantage (typically "yes, direct booking offers better rates or no booking fee")
- If this is in KB: quotes the advantage
- Does NOT say "I don't know" without redirecting
- Responds in BM

---

**Q12**
```
Ada breakfast included tak dalam harga tu?
```
**Pass criteria:**
- States breakfast inclusion policy from KB
- If two room types (with/without breakfast) exist: explains the difference
- Responds in BM

---

**Q13**
```
Macam mana nak dapat harga corporate? Company saya nak buat agreement.
```
**Pass criteria:**
- Acknowledges corporate rate request
- Asks for company name / contact / email
- Captures as a lead — this is a high-value inquiry
- Responds in BM

---

**Q14**
```
Last minute deal ada tak? Nak masuk esok.
```
**Pass criteria:**
- Addresses last-minute booking context
- Asks for check-in/check-out dates and room type preference
- Does NOT refuse to help
- Responds in BM or Manglish

---

## Category C — After-Hours Messages
*Tests: Does the AI respond appropriately at night / off-hours? This is the core product use case.*

---

**Q15** *(Sent at 11:30pm)*
```
Hello, nak tanya pasal bilik available tak malam ni?
```
**Pass criteria:**
- Responds promptly (within timeout, not "office is closed, call tomorrow")
- Acknowledges after-hours context gracefully
- Attempts to capture guest name and requirement
- Does NOT say "sorry we are closed"

---

**Q16** *(Sent at 2:00am)*
```
Saya dah sampai hotel tapi tak boleh check in. Kaunter tutup. Tolong.
```
**Pass criteria:**
- Recognises this is an urgent / real-time issue
- Provides emergency contact or night manager information from KB
- Does NOT give a generic booking response
- Escalates / captures as handoff if no emergency contact in KB

---

**Q17** *(Sent at 7:30pm, operating hours end at 11pm)*
```
Boleh tak book bilik untuk next week? Saya telefon tadi tapi tak ada orang jawab.
```
**Pass criteria:**
- Acknowledges missed call frustration empathetically
- Offers to help via this channel (WhatsApp)
- Begins booking flow (asks for dates, room type, guest count)
- Does NOT re-route back to calling

---

**Q18** *(Sent at 6:00am)*
```
Good morning, ada bilik available untuk hari ni? Check in petang ni boleh?
```
**Pass criteria:**
- Responds in English or bilingual (guest initiated in English)
- Addresses same-day check-in request
- Asks for arrival time and guest count
- Does NOT respond in BM if guest wrote in English (mirror language)

---

**Q19**
```
Malam ni ada last minute room tak? Sekejap je, nak singgah lepas balik dari KL.
```
**Pass criteria:**
- Understands "singgah" (brief stopover) — treats as short-stay booking
- Asks for check-in time and duration
- Captures contact details
- Responds in BM

---

**Q20**
```
Esok pagi ada bilik tak? Lagi satu, sarapan included ke?
```
**Pass criteria:**
- Handles two questions in one message (availability + breakfast)
- Responds to BOTH questions
- Asks for dates/guest count before confirming
- Responds in BM

---

## Category D — Complaints
*Tests: Does the AI handle guest complaints with empathy and escalate appropriately?*

---

**Q21**
```
Aircond bilik saya rosak. Dah sejam tunggu tapi tak ada siapa datang baiki.
```
**Pass criteria:**
- Expresses genuine empathy (NOT robotic "I am sorry for the inconvenience")
- Asks for room number
- Escalates to staff / handoff — this MUST NOT be handled by AI alone
- Urgency flag: marks as handoff or priority

---

**Q22**
```
Bilik saya kotor. Lantai ada kotoran, tilam pun nampak tak bersih. Tak acceptable langsung.
```
**Pass criteria:**
- Apologises sincerely
- Asks for room number and guest name
- Escalates to housekeeping or front desk
- Does NOT try to resolve alone or make excuses

---

**Q23**
```
Wi-Fi hotel ni sangat slow. Tak boleh kerja langsung. Bila nak fix?
```
**Pass criteria:**
- Acknowledges the complaint
- Provides troubleshooting tip from KB if available (e.g., "please try connecting to VIVATEL_5G network")
- If not in KB: escalates and captures room number
- Tone: helpful, not dismissive

---

**Q24**
```
Room service lambat gila. Dah order 1 jam lalu, makanan masih tak sampai.
```
**Pass criteria:**
- Apologises
- Asks for room number and order details
- Escalates to F&B / room service staff immediately
- Does NOT say "please contact the front desk" — the guest is already in the room

---

**Q25**
```
Jiran bilik sebelah bising sangat, tak boleh tidur. Dah pukul 12 malam ni.
```
**Pass criteria:**
- Empathetic, not bureaucratic
- Asks for room number and neighbouring room number if possible
- Escalates to night manager / security
- Urgency flag: time-sensitive, late night

---

## Category E — Group Bookings (Manglish)
*Tests: Can the AI recognise and capture high-value group booking inquiries?*

---

**Q26**
```
Hi, we want to book 20 rooms for a company trip. End of next month. Boleh bagi harga special tak?
```
**Pass criteria:**
- Recognises group booking (20 rooms = high-value lead)
- Asks for exact dates, group size, room type preference
- Captures contact: name, company, phone/email
- Flags as high-value lead (intent: group_booking)

---

**Q27**
```
Nak buat majlis perkahwinan. Ada function room? Berapa orang boleh muat? Ada package kawin tak?
```
**Pass criteria:**
- Addresses wedding / events inquiry
- Provides function room capacity from KB if available
- Mentions wedding package if in KB
- Captures contact details — HIGH VALUE lead
- Escalates to events team

---

**Q28**
```
Saya organiser trip sekolah. Nak bawa 3 kelas, dalam 100 pelajar. Ada group rate tak?
```
**Pass criteria:**
- Handles school/student group context
- Asks for dates, ages (for appropriate room configuration)
- Captures organiser contact details
- Does NOT dismiss because it's a school group

---

**Q29**
```
Corporate event nak buat kat hotel korang. 2 hari 1 malam, dalam 50 orang. What's the package?
```
*(Code-switching: Manglish corporate inquiry)*
**Pass criteria:**
- Recognises MICE (Meetings, Incentives, Conferences, Events) inquiry
- Asks for event date, type of event, requirements
- Captures name, company, contact
- Routes to events/sales team

---

**Q30**
```
Family reunion nak celebrate kat sini. Around 15-20 bilik, 3 malam. Ada diskaun group tak?
```
**Pass criteria:**
- Identifies group booking (15-20 rooms over 3 nights = very high value)
- Asks for preferred dates
- Mentions group rate availability or says will check
- Captures contact details immediately

---

## Category F — Code-Switching Mid-Sentence
*Tests: Can the AI handle the natural Malaysian way of mixing BM and English in one sentence?*

---

**Q31**
```
Can I check in early? Saya sampai pukul 10 pagi dari airport.
```
**Pass criteria:**
- Responds to BOTH languages naturally
- Addresses early check-in request
- States policy or asks for more details
- Does NOT force into English-only or BM-only response

---

**Q32**
```
Bilik ada bathtub tak? Because my wife really wants one, dia suka mandi dalam bathtub.
```
**Pass criteria:**
- Answers the bathtub question from KB
- Tone: friendly, accommodating
- If bathtub rooms in KB: mentions which room types
- Does NOT get confused by the personal context

---

**Q33**
```
Parking ada tak? Free ke kena bayar? I'm coming by car from Subang.
```
**Pass criteria:**
- Addresses parking availability and fee from KB
- Responds naturally in Manglish (mirrors guest's style)
- Provides parking instructions/directions if in KB

---

**Q34**
```
Swimming pool buka pukul berapa? My kids nak berenang petang ni.
```
**Pass criteria:**
- States pool hours from KB
- Tone: friendly, family-appropriate
- If kids' pool or restrictions: mentions them
- Short, clear answer

---

**Q35**
```
Room service ada ke? Nak order makan, lapar ni. Menu boleh tengok tak?
```
**Pass criteria:**
- Confirms room service availability from KB
- Provides menu highlights or hours if in KB
- If no KB data: escalates or directs to in-room dining menu
- Tone: responsive to hunger = urgency

---

**Q36**
```
Gym ada tak? Best ke? Saya biasa workout tiap pagi before breakfast.
```
**Pass criteria:**
- Confirms gym availability from KB
- States hours if available
- Brief description of facilities if in KB
- Tone: positive about fitness amenity

---

## Category G — Directions & Location (BM)
*Tests: Can the AI give helpful location/directions information?*

---

**Q37**
```
Hotel ni dekat dengan apa? Kalau nak pergi KLCC, jauh tak?
```
**Pass criteria:**
- Provides distance/travel time to KLCC from KB
- Mentions nearby landmarks from KB
- Suggests transport option (LRT, taxi, Grab)
- Responds in BM

---

**Q38**
```
Macam mana nak pergi ke hotel dari KL Sentral? Naik apa?
```
**Pass criteria:**
- Provides directions from KL Sentral from KB
- States public transport option (LRT, monorail, taxi)
- Clear, step-by-step if possible
- Responds in BM

---

**Q39**
```
Ada tak servis airport transfer? Saya landing KLIA2 pukul 9 malam.
```
**Pass criteria:**
- Confirms whether airport transfer is available from KB
- If available: states price or says will arrange
- If not: suggests alternatives (Grab, taxi from KLIA2)
- Captures contact details if transfer booking needed

---

**Q40**
```
Hotel parking macam mana? Nak drive masuk dari mana?
```
**Pass criteria:**
- Provides parking entrance directions from KB
- States parking fee and availability
- If KB has this info: answers directly
- If not: says will check and capture contact

---

## Category H — Facilities (BM)
*Tests: Facilities questions in BM — pool, gym, spa, restaurant, meeting rooms.*

---

**Q41**
```
Restoran hotel buka sampai pukul berapa malam ni?
```
**Pass criteria:**
- States restaurant closing time from KB
- If multiple F&B outlets: clarifies which one
- Responds in BM
- Does NOT make up hours not in KB

---

**Q42**
```
Ada spa ke kat hotel ni? Nak buat appointment untuk esok.
```
**Pass criteria:**
- Confirms spa availability from KB
- If yes: provides booking process or direct contact
- If no: suggests nearest alternative or apologises gracefully
- Captures contact for appointment if spa is available

---

**Q43**
```
Bilik mesyuarat ada berapa? Boleh accommodate berapa orang?
```
**Pass criteria:**
- Answers meeting room availability from KB
- States capacity if in KB
- Asks for date, time, and group size
- Captures contact for follow-up

---

**Q44**
```
Ada kolam renang untuk budak-budak tak? Anak saya baru 5 tahun.
```
**Pass criteria:**
- States children's pool availability from KB
- If no separate kids pool: mentions if main pool is child-friendly
- Age-appropriate safety acknowledgement
- Tone: reassuring for a parent

---

## Category I — Polite Refusal / Unavailability
*Tests: When the AI can't help or something isn't available, does it handle gracefully?*

---

**Q45**
```
Ada bilik yang ada dapur tak? Nak masak sendiri.
```
*(Vivatel likely doesn't have kitchenettes — tests graceful refusal)*
**Pass criteria:**
- If no kitchen rooms: politely says so
- Offers alternatives (nearby grocery, room service, restaurant)
- Does NOT just say "No, we don't have that" and stop
- Tone: helpful even when declining

---

**Q46**
```
Boleh tak bawa haiwan peliharaan? Saya ada kucing, dia tak bising pun.
```
**Pass criteria:**
- States pet policy from KB
- If no pets allowed: politely declines with reason
- If pet-friendly: states conditions
- Does NOT give wrong information — pet policy is specific

---

**Q47**
```
Nak extend stay tapi kena bayar sampai esok je dulu. Boleh bayar separuh dulu?
```
**Pass criteria:**
- Acknowledges payment arrangement request
- Directs to front desk for payment terms (AI cannot confirm financial arrangements)
- Does NOT make promises about payment flexibility
- Escalates to front desk / manager

---

## Category J — Ambiguous / Informal Input
*Tests: Can the AI handle vague, very informal, or single-word messages that real guests actually send?*

---

**Q48**
```
ok ke tempat ni?
```
*(Very informal, Malaysian slang — "is this place okay / good?")*
**Pass criteria:**
- Understands this as a general enquiry about the hotel
- Responds positively with 1-2 highlights from KB
- Does NOT give a confused or literal response ("I'm not sure what you mean")
- Tone: natural, conversational

---

**Q49**
```
harga?
```
*(Single word — no context)*
**Pass criteria:**
- Does NOT crash or give an error
- Asks for clarification: what type of room and dates?
- Does NOT assume the cheapest room
- Short, friendly clarification question

---

**Q50**
```
Best tak hotel ni? Teman nak bagi hadiah stay dekat sini untuk girlfriend dia.
```
**Pass criteria:**
- Recognises romantic gift context (present for girlfriend)
- Responds warmly with hotel highlights
- Mentions romantic/couple-friendly aspects from KB
- Captures contact details to help arrange a special experience
- Tone: enthusiastic, warm — this is a gift purchase, treat it as such

---

## Results Log

*Fill in after running each question*

| # | Q (short) | AI Response Summary | PASS / FAIL / PARTIAL | Failure Mode |
|---|-----------|--------------------|-----------------------|--------------|
| 1 | Bilik kosong 2 malam? | | | |
| 2 | Jenis bilik ada? | | | |
| 3 | 2 dewasa 1 kanak-kanak | | | |
| 4 | Bilik paling murah? | | | |
| 5 | Pemandangan kolam renang? | | | |
| 6 | Check in awal pukul 8? | | | |
| 7 | Check out pukul berapa? | | | |
| 8 | Bilik honeymoon ada? | | | |
| 9 | Harga bilik standard weekend? | | | |
| 10 | Special package promo? | | | |
| 11 | Lebih murah dari Booking.com? | | | |
| 12 | Breakfast included? | | | |
| 13 | Corporate rate? | | | |
| 14 | Last minute deal esok? | | | |
| 15 | Bilik available malam ni? (11:30pm) | | | |
| 16 | Sampai, kaunter tutup (2am) | | | |
| 17 | Telefon tadi tak ada orang | | | |
| 18 | Good morning same day (6am) | | | |
| 19 | Last minute singgah | | | |
| 20 | Esok pagi + sarapan? | | | |
| 21 | Aircond rosak | | | |
| 22 | Bilik kotor | | | |
| 23 | Wi-Fi slow | | | |
| 24 | Room service lambat | | | |
| 25 | Jiran bising 12 malam | | | |
| 26 | 20 rooms company trip | | | |
| 27 | Majlis perkahwinan | | | |
| 28 | Trip sekolah 100 pelajar | | | |
| 29 | Corporate event 2D1N 50 orang | | | |
| 30 | Family reunion 15-20 bilik | | | |
| 31 | Check in early dari airport | | | |
| 32 | Bilik ada bathtub? | | | |
| 33 | Parking free ke kena bayar? | | | |
| 34 | Swimming pool buka pukul? | | | |
| 35 | Room service ada menu? | | | |
| 36 | Gym ada? | | | |
| 37 | Dekat dengan apa? KLCC jauh? | | | |
| 38 | Dari KL Sentral macam mana? | | | |
| 39 | Airport transfer dari KLIA2 | | | |
| 40 | Parking macam mana nak masuk? | | | |
| 41 | Restoran buka sampai pukul berapa? | | | |
| 42 | Ada spa? Nak appointment | | | |
| 43 | Bilik mesyuarat berapa? | | | |
| 44 | Kolam renang untuk budak 5 tahun? | | | |
| 45 | Ada dapur tak? | | | |
| 46 | Boleh bawa kucing? | | | |
| 47 | Bayar separuh dulu? | | | |
| 48 | ok ke tempat ni? | | | |
| 49 | harga? | | | |
| 50 | Hadiah girlfriend, best tak? | | | |

---

## Scoring Summary

After completing all 50 questions, fill in:

| Category | Passed | Total | Rate |
|----------|--------|-------|------|
| A — Standard Room Inquiries (BM) | | 8 | |
| B — Rate & Pricing | | 6 | |
| C — After-Hours | | 6 | |
| D — Complaints | | 5 | |
| E — Group Bookings | | 5 | |
| F — Code-Switching | | 6 | |
| G — Directions | | 4 | |
| H — Facilities | | 4 | |
| I — Polite Refusal | | 3 | |
| J — Ambiguous Input | | 3 | |
| **TOTAL** | | **50** | |

**PASS GATE: ≥ 40/50 (80%) required before Phase 1 go-live.**

---

## Failure Classification

Log all failures by type:

| Failure Type | Count | Examples |
|--------------|-------|---------|
| Wrong language (responded EN when BM expected) | | |
| Hallucinated KB fact (made up room/rate not in KB) | | |
| Refused to help / dead end | | |
| Failed to capture lead on high-value inquiry | | |
| Missing escalation (complaint not handed off) | | |
| Tone mismatch (robotic on emotional context) | | |
| Did not handle code-switching | | |
| Wrong information (stated wrong time/price/policy) | | |

---

## Post-Test Actions

**If pass rate ≥ 80%:**
- Document results, mark P0.6 as complete
- Brief marketing: bilingual claim is substantiated (if ≥ 90%: "Fully bilingual"; 80–89%: "English and Bahasa Malaysia supported")
- Proceed to Phase 1

**If pass rate 70–79%:**
- Log all failures by category
- Fix the top-failing category first (patch KB or system prompt)
- Re-run the failed questions only before proceeding
- Do not proceed to Phase 1 until ≥ 80%

**If pass rate < 70%:**
- Full stop. Do not go live with Vivatel.
- Root cause analysis: is it KB (missing data) or prompt (wrong instructions)?
- Fix prompt first (faster), then KB
- Full re-run required before proceeding

---

*Test designed for Vivatel Kuala Lumpur. Questions reflect real guest inquiry patterns from 8 hotel GM interviews (Feb 2026). Language complexity reflects MYT Malaysian WhatsApp usage patterns.*
