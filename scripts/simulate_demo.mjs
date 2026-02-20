/**
 * Nocturn AI — Sales Demo Simulator
 * 
 * Runs 100 real conversations through the API to demonstrate:
 * - AI concierge handling diverse hotel inquiries
 * - Lead capture from booking requests
 * - After-hours conversation recovery
 * - Escalation/handoff for complaints
 * - Multi-turn conversation context
 * 
 * Usage: node scripts/simulate_demo.mjs
 */

const API = 'http://localhost:8000/api/v1';

// ─── Helpers ───────────────────────────────────────────────

async function api(path, opts = {}) {
    const url = `${API}${path}`;
    const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json', ...opts.headers },
        ...opts,
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`${res.status} ${path}: ${text}`);
    }
    return res.json();
}

async function authApi(path, token, opts = {}) {
    return api(path, {
        ...opts,
        headers: { Authorization: `Bearer ${token}`, ...opts.headers },
    });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ─── Authentication ────────────────────────────────────────

async function login() {
    const res = await fetch(`${API}/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'username=admin&password=password123',
    });
    const data = await res.json();
    if (!data.access_token) throw new Error('Login failed: ' + JSON.stringify(data));
    return data.access_token;
}

// ─── Property Setup ────────────────────────────────────────

async function setupProperty(token) {
    console.log('\n📋 Setting up demo property...');

    // Check if property exists
    const props = await authApi('/properties', token);
    if (props.length > 0) {
        console.log(`   ✅ Using existing property: ${props[0].name} (${props[0].id})`);
        return props[0].id;
    }

    // Create property (matches PropertyCreateRequest schema)
    const prop = await authApi('/properties', token, {
        method: 'POST',
        body: JSON.stringify({
            name: 'Grand Riviera Hotel & Spa',
            whatsapp_number: '+60123456789',
            adr: 450.0,
            ota_commission_pct: 18.0,
        }),
    });

    console.log(`   ✅ Created property: ${prop.name} (${prop.id})`);
    return prop.id;
}

// ─── 100 Conversation Scenarios ────────────────────────────

function getConversations() {
    const channels = ['web', 'whatsapp', 'email'];
    const scenarios = [];

    // === Category 1: Room & Rate Inquiries (30) ===
    const roomInquiries = [
        { name: 'Aiman Rahman', msgs: ['Hi, what are your room rates?', 'Do you have any suites available?'] },
        { name: 'Sarah Chen', msgs: ['How much is a Deluxe Room per night?', 'Does it include breakfast?'] },
        { name: 'James Wong', msgs: ['I need a room for 2 adults and 1 child. Options?', 'Is the extra bed comfortable?'] },
        { name: 'Fatimah Ismail', msgs: ['Berapa harga bilik satu malam?', 'Ada bilik yang menghadap KLCC?'] },
        { name: 'Raj Kumar', msgs: ['Do you have any rooms with a view of the Twin Towers?', 'What floor would that be on?'] },
        { name: 'Lisa Tan', msgs: ['What is your best room?', 'Does the Presidential Suite really come with a personal chef?'] },
        { name: 'Ahmad Zaki', msgs: ['Any connecting rooms available?', 'I need two rooms side by side for family.'] },
        { name: 'Emily Foster', msgs: ['Whats the difference between Deluxe and Premier Suite?', 'Is the jacuzzi in the room or bathroom?'] },
        { name: 'Nurul Ain', msgs: ['Ada promosi untuk bilik hujung minggu?', 'Boleh book untuk Jumaat sampai Ahad?'] },
        { name: 'David Lee', msgs: ['Do you have any corporate rates?'] },
        { name: 'Siti Nurhaliza', msgs: ['Saya nak tanya pasal Grand Suite. Ada butler service ke?'] },
        { name: 'Michael Brown', msgs: ['What are your cheapest room options?', 'Is there a pool?'] },
        { name: 'Tan Wei Ming', msgs: ['Room rates for Chinese New Year period?'] },
        { name: 'Priya Nair', msgs: ['Can I get an interconnecting room?', 'For how many guests?'] },
        { name: 'Hassan Ali', msgs: ['Is WiFi free in the rooms?', 'What about parking?'] },
        { name: 'Jenny Lim', msgs: ['Any rooms with bathtub?'] },
        { name: 'Mohd Faris', msgs: ['Bilik mana yang paling besar?', 'Ada balcony tak?'] },
        { name: 'Catherine Ong', msgs: ['Premier Suite with KLCC view — available next weekend?'] },
        { name: 'Vikram Singh', msgs: ['What amenities are included with the room?'] },
        { name: 'Azizah Mohd', msgs: ['Adakah sarapan termasuk?', 'Untuk berapa orang?'] },
        { name: 'Tom Mitchell', msgs: ['Do kids stay free?', 'Up to what age?'] },
        { name: 'Yuki Tanaka', msgs: ['Is there a non-smoking room?'] },
        { name: 'Razak Ibrahim', msgs: ['Room for tonight, anything available?'] },
        { name: 'Anna Schmidt', msgs: ['What is check-in and check-out time?', 'Can I do early check-in?'] },
        { name: 'Zainab Yusof', msgs: ['Ada late checkout tak?', 'Sampai pukul berapa?'] },
        { name: 'Chris Taylor', msgs: ['Suite with a good view for our anniversary'] },
        { name: 'Mei Ling', msgs: ['Are there any birthday packages or surprises you can arrange?'] },
        { name: 'Abdullah Hakim', msgs: ['Berapa harga bilik untuk sebulan? Corporate stay.'] },
        { name: 'Sophie Martin', msgs: ['Quiet room away from the elevator please', 'High floor if possible'] },
        { name: 'Ravi Muthu', msgs: ['Twin bed room available?', 'For two colleagues traveling together'] },
    ];
    roomInquiries.forEach((s, i) => {
        scenarios.push({ ...s, channel: channels[i % 3], category: 'room_inquiry' });
    });

    // === Category 2: Booking Requests — Lead Capture (25) ===
    const bookings = [
        { name: 'Amanda Chong', msgs: ['I want to book a Deluxe Room for 3 nights, Feb 25-28', 'My number is 0123456789'] },
        { name: 'Kamal Harun', msgs: ['Nak book bilik untuk 5 orang, Mac 1-3', 'Email saya kamal@test.com'] },
        { name: 'Jessica Wu', msgs: ['Book Premier Suite for honeymoon March 14-17', 'Contact: jessica.wu@email.com, +60189876543'] },
        { name: 'Ismail Razak', msgs: ['I need to reserve 5 rooms for a wedding party, March 20-22', 'Please call me at 0198765432'] },
        { name: 'Grace Koh', msgs: ['Book the CNY special please! 3 nights from Feb 28', 'My email is grace.koh@gmail.com'] },
        { name: 'Farhan Amin', msgs: ['Nak tempah bilik Deluxe, 2 malam, hujung minggu ni', 'No telefon 0167890123'] },
        { name: 'Rachel Green', msgs: ['Weekend getaway for 2, this Friday-Sunday', 'Reach me at rachel@email.com'] },
        { name: 'Syafiq Nizam', msgs: ['Book Grand Suite untuk anniversary, 14 Mac', 'Boleh call 0134567890'] },
        { name: 'Kim Soo Young', msgs: ['Reserve 2 Deluxe Rooms for March 5-8', 'Contact: +82-10-1234-5678'] },
        { name: 'Aisyah Rahman', msgs: ['Nak book honeymoon package untuk Mac', 'WhatsApp saya 0145678901'] },
        { name: 'Robert Chen', msgs: ['Corporate booking, 10 rooms for March conference', 'robert.chen@company.com'] },
        { name: 'Nor Azman', msgs: ['Tempah bilik untuk 2 malam, bawa keluarga', 'Hubungi 0156789012'] },
        { name: 'Sakura Yamamoto', msgs: ['Book Presidential Suite for March 1', 'sakura@email.jp'] },
        { name: 'Haziq Osman', msgs: ['3 bilik untuk family reunion, Mac 15-18', 'Call saya 0112345678'] },
        { name: 'Laura Williams', msgs: ['Booking for business trip, 5 nights starting March 3', 'laura.w@corp.com'] },
        { name: 'Hafiz Zainal', msgs: ['Nak book Ramadan buffet untuk 20 orang, March 15', 'Email hafiz@company.my'] },
        { name: 'Devi Lakshmi', msgs: ['Reserve spa package + room for my mothers birthday', 'devi.l@email.com, 0178901234'] },
        { name: 'Wong Kah Wai', msgs: ['Book meeting room for 50 pax, March 10', 'kahwai@business.com'] },
        { name: 'Nadia Bakar', msgs: ['Nak book wedding ballroom, July dates', 'nadia.b@email.com'] },
        { name: 'Steve Johnson', msgs: ['Airport transfer + room for March 8', 'sjohnson@email.com'] },
        { name: 'Zahra Hussein', msgs: ['Book 2 connecting rooms, April school holiday', 'zahra@family.com'] },
        { name: 'Lim Boon Kiat', msgs: ['Reserve table at The Orchid for 4 pax, Saturday night', 'Call me 0189012345'] },
        { name: 'Putri Amira', msgs: ['Nak celebrate birthday, ada package tak?', 'WhatsApp 0190123456'] },
        { name: 'Daniel Park', msgs: ['Group booking 8 rooms, March 20-23 tech conference', 'daniel@techcorp.com'] },
        { name: 'Sharifah Aini', msgs: ['Book weekend getaway room special, this weekend', 'Sharifah 0123987654'] },
    ];
    bookings.forEach((s, i) => {
        scenarios.push({ ...s, channel: channels[i % 3], category: 'booking_request' });
    });

    // === Category 3: Facilities & Amenities (15) ===
    const facilities = [
        { name: 'Peter Huang', msgs: ['What time does the pool open?', 'Is there a swim-up bar?'] },
        { name: 'Aminah Sulaiman', msgs: ['Ada surau dalam hotel tak?', 'Dekat tingkat berapa?'] },
        { name: 'Mark Spencer', msgs: ['Do you have a gym?', 'Is it 24 hours?'] },
        { name: 'Salmah Nordin', msgs: ['Spa ada couples package?', 'Berapa harga?'] },
        { name: 'Frank Miller', msgs: ['Is there a kids club?', 'What ages?', 'What time does it close?'] },
        { name: 'Rashid Omar', msgs: ['Where can I do my laundry?'] },
        { name: 'Helen Chow', msgs: ['Tell me about your restaurants'] },
        { name: 'Imran Shah', msgs: ['Is the breakfast buffet halal?'] },
        { name: 'Nancy Drew', msgs: ['Do you have a business center?', 'Can I print documents?'] },
        { name: 'Azlan Ismail', msgs: ['Ada shuttle ke KLCC tak?'] },
        { name: 'George Thompson', msgs: ['What dining options do you have near the hotel?'] },
        { name: 'Farah Zulkifli', msgs: ['Hotel ada parking free tak?'] },
        { name: 'Tony Stark', msgs: ['Do you have EV charging stations?'] },
        { name: 'Rosmah Ahmad', msgs: ['Ada kedai cenderamata dalam hotel?'] },
        { name: 'Diana Prince', msgs: ['Is there an afternoon tea service?', 'How much per set?'] },
    ];
    facilities.forEach((s, i) => {
        scenarios.push({ ...s, channel: channels[i % 3], category: 'facilities' });
    });

    // === Category 4: After-Hours Recovery (10) ===
    const afterHours = [
        { name: 'Kevin Lau', msgs: ['Hi, is anyone there? I want to book a room for tomorrow!', 'Deluxe room please. My email is kevin@email.com'] },
        { name: 'Wan Nurul', msgs: ['Hello, saya nak check ketersediaan bilik malam ni', 'Saya dalam perjalanan dari airport sekarang'] },
        { name: 'Bob Richards', msgs: ['Emergency! I need a room right now, just landed at KLIA', 'Any room, my card number...actually just save a room, Bob Richards +61412345678'] },
        { name: 'Zarina Syed', msgs: ['Assalamualaikum, saya nak tanya about tomorrow check-in time', 'Boleh early check-in tak? Sampai KL pukul 10 pagi'] },
        { name: 'Jake Morrison', msgs: ['Hey, can I extend my stay? Currently in room 2305', 'Need 2 more nights please'] },
        { name: 'Noraini Mat', msgs: ['Malam ni ada bilik kosong tak?', 'Nak book sekarang juga'] },
        { name: 'Alex Turner', msgs: ['Late night question — do you have airport pickup at 6am?'] },
        { name: 'Faizal Hamid', msgs: ['Saya sampai lewat malam ni, check-in boleh ke?', 'Around 2am'] },
        { name: 'Maria Santos', msgs: ['Hi, my flight is delayed. Can I move my booking to tomorrow?', 'Booking ref: GRH-12345'] },
        { name: 'Hafizah Yusof', msgs: ['Urgent — nak cancel booking for tonight, flight cancelled'] },
    ];
    afterHours.forEach((s, i) => {
        scenarios.push({ ...s, channel: channels[i % 3], category: 'after_hours', isAfterHours: true });
    });

    // === Category 5: Complaints → Escalation (10) ===
    const complaints = [
        { name: 'Karen White', msgs: ['The air conditioning in my room is broken!', 'Room 1502. This is unacceptable, I want to speak to the manager'] },
        { name: 'Ahmad Firdaus', msgs: ['Saya tak puas hati dengan perkhidmatan bilik', 'Bilik tak dibersihkan sejak semalam!'] },
        { name: 'Susan Clarke', msgs: ['I was charged extra on my bill and nobody can explain why', 'I want a refund immediately'] },
        { name: 'Rizal Mansor', msgs: ['WiFi sangat slow! Saya tengah meeting penting', 'Dah 2 jam macam ni, tolong selesaikan segera'] },
        { name: 'Patricia Lee', msgs: ['There is noise from construction next door, its 6AM!', 'We were not informed about this when booking'] },
        { name: 'Bakar Hussain', msgs: ['Room service took 2 hours! The food arrived cold', 'I demand compensation'] },
        { name: 'Gordon Ramsey', msgs: ['The restaurant food was terrible and overpriced', 'I want to speak with hotel management right now'] },
        { name: 'Zul Haziq', msgs: ['Parking kereta saya ada scratch! Valet parking korang buat ni', 'Saya nak jumpa manager sekarang'] },
        { name: 'Margaret Thatcher', msgs: ['My room safe is not working and I have valuables', 'This is a serious security concern'] },
        { name: 'Nik Aziz', msgs: ['Aircond bocor dalam bilik, basah semua beg saya', 'Nak tukar bilik lain dan compensation'] },
    ];
    complaints.forEach((s, i) => {
        scenarios.push({ ...s, channel: channels[i % 3], category: 'complaint' });
    });

    // === Category 6: Multi-turn Complex (10) ===
    const complex = [
        { name: 'Stephanie Lim', msgs: ['Planning a wedding for 300 guests in July', 'What ballroom options do you have?', 'Do you provide catering?', 'Can you send me a wedding brochure? stephanie@email.com'] },
        { name: 'Datuk Amir', msgs: ['Saya nak buat corporate retreat untuk 50 orang', 'Perlu meeting room, bilik, dan makan', 'Budget around RM 100k for 3 days', 'Email proposal ke datuk.amir@corp.my'] },
        { name: 'Helen & John', msgs: ['Were celebrating our 25th anniversary!', 'Something special - best suite with champagne?', 'Also spa treatments for both of us', 'Budget about RM 5000 total, March 14'] },
        { name: 'Tour Group Lead', msgs: ['I have a tour group of 30 coming from Japan', 'Need 15 twin rooms, March 10-14', 'Group discount available?', 'Also need airport transfer for all'] },
        { name: 'Harun Conference', msgs: ['Tech conference 200 attendees', 'Need main hall + 3 breakout rooms', 'Lunch buffet + tea breaks', 'AV equipment and projectors required', 'harun@techconf.my'] },
        { name: 'Aishah Wedding', msgs: ['Nak buat nikah di hotel bulan 6', 'Untuk 200 tetamu', 'Ada pakej nikah plus resepsi?', 'Budget bawah RM 50,000'] },
        { name: 'Mr Thompson Family', msgs: ['Family reunion, 8 families total', 'Need about 10 rooms', 'Kids activities during the day?', 'Group dinner at your restaurant'] },
        { name: 'Lisa Corporate', msgs: ['Annual company dinner for 150 staff', 'Need stage, sound system, LED screen', 'Sit-down dinner, halal certified', 'Date: March 28'] },
        { name: 'Backpacker Ben', msgs: ['Cheapest option for 1 night?', 'Is there a hostel nearby if you are too expensive?', 'Actually your weekend rate is okay, can I book?', 'Ben Wilson, ben@backpack.com'] },
        { name: 'VIP Guest', msgs: ['I am the CEO of TechGiant Corp', 'Need your absolute best suite', 'Personal chef, chauffeur, the works', 'My assistant will handle payment: vip@techgiant.com'] },
    ];
    complex.forEach((s, i) => {
        scenarios.push({ ...s, channel: channels[i % 3], category: 'complex' });
    });

    return scenarios;
}

// ─── Run Simulation ────────────────────────────────────────

async function runSimulation() {
    console.log('═══════════════════════════════════════════════════');
    console.log('  🌙 NOCTURN AI — Sales Demo Simulation');
    console.log('  Running 100 real conversations through the API');
    console.log('═══════════════════════════════════════════════════\n');

    // 1. Login
    console.log('🔐 Authenticating...');
    let token;
    try {
        token = await login();
        console.log('   ✅ Authenticated\n');
    } catch (e) {
        console.error('   ❌ Login failed:', e.message);
        process.exit(1);
    }

    // 2. Setup Property
    let propertyId;
    try {
        propertyId = await setupProperty(token);
    } catch (e) {
        console.error('   ❌ Property setup failed:', e.message);
        process.exit(1);
    }

    // 3. Run Conversations
    const scenarios = getConversations();
    console.log(`\n🗣️  Running ${scenarios.length} conversations...\n`);

    const results = {
        total: scenarios.length,
        success: 0,
        failed: 0,
        leads_created: 0,
        handoffs: 0,
        categories: {},
        channels: { web: 0, whatsapp: 0, email: 0 },
        response_times: [],
        conversations: [],
    };

    for (let i = 0; i < scenarios.length; i++) {
        const s = scenarios[i];
        const sessionId = `sim_${Date.now()}_${i}`;

        // Track category
        results.categories[s.category] = (results.categories[s.category] || 0) + 1;
        results.channels[s.channel]++;

        const progress = `[${String(i + 1).padStart(3)}/${scenarios.length}]`;
        const label = `${s.name} (${s.channel}/${s.category})`;

        try {
            let lastResult = null;
            const startTime = Date.now();

            for (const msg of s.msgs) {
                lastResult = await api('/conversations', {
                    method: 'POST',
                    body: JSON.stringify({
                        property_id: propertyId,
                        message: msg,
                        session_id: sessionId,
                        guest_name: s.name,
                    }),
                });
                // Small delay between messages in multi-turn
                if (s.msgs.length > 1) await sleep(1000);
            }

            const elapsed = Date.now() - startTime;
            results.response_times.push(elapsed / s.msgs.length);
            results.success++;

            if (lastResult?.lead_created) results.leads_created++;
            if (lastResult?.mode === 'handoff') results.handoffs++;

            const status = lastResult?.lead_created ? '💼' : lastResult?.mode === 'handoff' ? '🚨' : '✅';
            console.log(`${progress} ${status} ${label} — ${elapsed}ms (${s.msgs.length} msgs)`);

            results.conversations.push({
                name: s.name,
                channel: s.channel,
                category: s.category,
                messages: s.msgs.length,
                response: lastResult?.response?.substring(0, 80),
                lead: lastResult?.lead_created || false,
                handoff: lastResult?.mode === 'handoff',
                time_ms: elapsed,
            });

        } catch (e) {
            results.failed++;
            console.log(`${progress} ❌ ${label} — ${e.message.substring(0, 60)}`);
            results.conversations.push({
                name: s.name,
                channel: s.channel,
                category: s.category,
                error: e.message.substring(0, 100),
            });
        }

        // Rate limiting — space out requests
        await sleep(1000);
    }

    // 4. Print Summary
    console.log('\n═══════════════════════════════════════════════════');
    console.log('  📊 SIMULATION RESULTS');
    console.log('═══════════════════════════════════════════════════');
    console.log(`  Total:     ${results.total}`);
    console.log(`  Success:   ${results.success}`);
    console.log(`  Failed:    ${results.failed}`);
    console.log(`  Leads:     ${results.leads_created}`);
    console.log(`  Handoffs:  ${results.handoffs}`);
    console.log('');
    console.log('  By Category:');
    for (const [cat, count] of Object.entries(results.categories)) {
        console.log(`    ${cat}: ${count}`);
    }
    console.log('');
    console.log('  By Channel:');
    for (const [ch, count] of Object.entries(results.channels)) {
        console.log(`    ${ch}: ${count}`);
    }
    if (results.response_times.length > 0) {
        const avg = results.response_times.reduce((a, b) => a + b, 0) / results.response_times.length;
        const max = Math.max(...results.response_times);
        const min = Math.min(...results.response_times);
        console.log(`\n  Response Times:`);
        console.log(`    Avg: ${avg.toFixed(0)}ms`);
        console.log(`    Min: ${min.toFixed(0)}ms`);
        console.log(`    Max: ${max.toFixed(0)}ms`);
    }
    console.log('═══════════════════════════════════════════════════\n');

    // 5. Save results for dashboard
    const fs = await import('fs');
    fs.writeFileSync(
        'simulation_results.json',
        JSON.stringify(results, null, 2)
    );
    console.log('📁 Results saved to simulation_results.json');
    console.log(`\n🏁 Property ID: ${propertyId}`);
    console.log('   Use this ID to view the dashboard at http://localhost:3000\n');
}

runSimulation().catch(console.error);
