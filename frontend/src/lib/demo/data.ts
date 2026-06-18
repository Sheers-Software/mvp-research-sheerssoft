/**
 * Self-contained seeded demo dataset for the investor/buyer demo build.
 *
 * Everything here is fake but internally consistent and tuned to tell a strong
 * ROI story for a fictional business portfolio ("Sarah's Creative Services"). When
 * NEXT_PUBLIC_DEMO_MODE === 'true', lib/api.ts and lib/auth.tsx read from this
 * module instead of hitting a backend — so the entire app runs on Vercel's free
 * tier with zero infrastructure and nothing to break during a live pitch.
 *
 * State is held in module-level mutable objects so demo interactions (replying
 * to a conversation, converting a lead, adding a KB doc) persist for the session.
 */

// ─── Persona ────────────────────────────────────────────────────────────────

export type DemoPersona = 'staff' | 'owner' | 'superadmin';

const PERSONA_KEY = 'nocturn_demo_persona';

export function getPersona(): DemoPersona {
    if (typeof window === 'undefined') return 'owner';
    const p = localStorage.getItem(PERSONA_KEY) as DemoPersona | null;
    return p === 'staff' || p === 'owner' || p === 'superadmin' ? p : 'owner';
}

export function setPersona(p: DemoPersona) {
    if (typeof window !== 'undefined') localStorage.setItem(PERSONA_KEY, p);
}

// ─── Core IDs ─────────────────────────────────────────────────────────────────

export const TENANT_ID = 'demo-tenant-lumiere';
export const BUSINESS_ID = 'demo-prop-lumiere-kl';
export const BUSINESS_ID_2 = 'demo-prop-lumiere-penang';
export const BUSINESS_NAME = 'Sarah Photography';
export const BUSINESS_NAME_2 = 'Sarah Videography';

const now = () => new Date();
const iso = (d: Date) => d.toISOString();
const daysAgo = (n: number) => new Date(Date.now() - n * 86400000);
const hoursAgo = (n: number) => new Date(Date.now() - n * 3600000);
const minsAgo = (n: number) => new Date(Date.now() - n * 60000);

// ─── Demo user (persona-driven) ───────────────────────────────────────────────

export function demoUser(persona: DemoPersona = getPersona()) {
    const base = {
        id: 'demo-user-1',
        email:
            persona === 'superadmin'
                ? 'admin@sheerssoft.com'
                : persona === 'owner'
                ? 'sarah@sarahphotography.com'
                : 'staff@sarahphotography.com',
        full_name:
            persona === 'superadmin'
                ? 'SheersSoft Admin'
                : persona === 'owner'
                ? 'Sarah Jane'
                : 'Daniel Tan',
        phone: '+60 12-345 6789',
        last_login_at: iso(hoursAgo(2)),
        onboarding_completed: true,
    };

    if (persona === 'superadmin') {
        return {
            ...base,
            is_superadmin: true,
            memberships: [],
            role: null as string | null,
            tenant_id: null as string | null,
        };
    }

    const role = persona === 'owner' ? 'owner' : 'staff';
    return {
        ...base,
        is_superadmin: false,
        memberships: [
            {
                id: 'demo-membership-1',
                tenant_id: TENANT_ID,
                tenant_name: "Sarah's Creative Services",
                role,
                accessible_business_ids: null,
            },
        ],
        role,
        tenant_id: TENANT_ID,
    };
}

// ─── Portal home ──────────────────────────────────────────────────────────────

export function portalHome() {
    return {
        tenant: { id: TENANT_ID, name: "Sarah's Creative Services", subscription_tier: 'premium' },
        businesses: [
            {
                id: BUSINESS_ID,
                name: BUSINESS_NAME,
                slug: 'lumiere-kl',
                is_active: true,
                weekly_inquiries: 182,
                weekly_leads: 41,
                weekly_revenue_rm: 58400,
                onboarding_score: 100,
                channel_statuses: { whatsapp: 'active', email: 'active', website: 'active' },
            },
            {
                id: BUSINESS_ID_2,
                name: BUSINESS_NAME_2,
                slug: 'lumiere-penang',
                is_active: true,
                weekly_inquiries: 96,
                weekly_leads: 23,
                weekly_revenue_rm: 27600,
                onboarding_score: 100,
                channel_statuses: { whatsapp: 'active', email: 'active', website: 'configuring' },
            },
        ],
    };
}

// ─── Live dashboard stats (today) ─────────────────────────────────────────────

export function liveStats() {
    return {
        business_id: BUSINESS_ID,
        business_name: BUSINESS_NAME,
        report_date: iso(now()).split('T')[0],
        total_inquiries: 47,
        after_hours_inquiries: 29,
        after_hours_responded: 29,
        leads_captured: 11,
        avg_response_time_sec: 6.4,
        estimated_revenue_recovered: 18900,
        actual_revenue_recovered: 7400,
        active_conversations: 3,
        handed_off_conversations: 2,
        inquiries_handled_by_ai: 43,
        inquiries_handled_manually: 4,
        cost_savings: 1280,
    };
}

// ─── Period analytics (with generated daily series) ───────────────────────────

interface DailyRow {
    date: string;
    total_inquiries: number;
    after_hours_inquiries: number;
    leads_captured: number;
    handoffs: number;
    inquiries_handled_by_ai: number;
    inquiries_handled_manually: number;
    avg_response_time_sec: number;
    estimated_revenue_recovered: number;
    cost_savings: number;
}

// Deterministic pseudo-variance so charts look organic but stable across renders.
function buildDaily(days: number): DailyRow[] {
    const rows: DailyRow[] = [];
    for (let i = days - 1; i >= 0; i--) {
        const d = daysAgo(i);
        const dow = d.getDay();
        const weekendBoost = dow === 5 || dow === 6 ? 1.35 : 1;
        const wobble = 0.8 + ((i * 37) % 40) / 100;
        const inquiries = Math.round(38 * weekendBoost * wobble);
        const afterHours = Math.round(inquiries * 0.58);
        const leads = Math.round(inquiries * 0.23);
        const handoffs = Math.max(0, Math.round(inquiries * 0.07));
        const ai = inquiries - Math.round(inquiries * 0.08);
        const manual = inquiries - ai;
        rows.push({
            date: iso(d).split('T')[0],
            total_inquiries: inquiries,
            after_hours_inquiries: afterHours,
            leads_captured: leads,
            handoffs,
            inquiries_handled_by_ai: ai,
            inquiries_handled_manually: manual,
            avg_response_time_sec: 5 + (i % 5),
            estimated_revenue_recovered: leads * 1650,
            cost_savings: Math.round(inquiries * 28),
        });
    }
    return rows;
}

export function analytics(businessId: string, from?: string, to?: string) {
    let days = 30;
    if (from && to) {
        const diff = Math.round(
            (new Date(to).getTime() - new Date(from).getTime()) / 86400000,
        );
        if (diff > 0 && diff <= 120) days = diff + 1;
    }
    const daily = buildDaily(days);
    const sum = (k: keyof DailyRow) =>
        daily.reduce((acc, r) => acc + (typeof r[k] === 'number' ? (r[k] as number) : 0), 0);
    const totalInq = sum('total_inquiries');
    return {
        business_id: businessId,
        period: {
            from: from || daily[0].date,
            to: to || daily[daily.length - 1].date,
        },
        totals: {
            total_inquiries: totalInq,
            after_hours_inquiries: sum('after_hours_inquiries'),
            after_hours_responded: sum('after_hours_inquiries'),
            leads_captured: sum('leads_captured'),
            handoffs: sum('handoffs'),
            inquiries_handled_by_ai: sum('inquiries_handled_by_ai'),
            inquiries_handled_manually: sum('inquiries_handled_manually'),
            avg_response_time_sec: 6.4,
            estimated_revenue_recovered: sum('estimated_revenue_recovered'),
            cost_savings: sum('cost_savings'),
        },
        daily,
        performance_fee_balance_rm: 1840,
    };
}

// ─── Insights ─────────────────────────────────────────────────────────────────

export function insights(businessId: string) {
    return {
        generated_at: iso(daysAgo(1)),
        period_start: iso(daysAgo(30)).split('T')[0],
        period_end: iso(now()).split('T')[0],
        business_id: businessId,
        top_topics: [
            { topic: 'Room availability & rates', count: 312 },
            { topic: 'Airport transfer / parking', count: 188 },
            { topic: 'Check-in / late check-out', count: 154 },
            { topic: 'Breakfast & dining hours', count: 121 },
            { topic: 'Pool & facilities', count: 98 },
            { topic: 'Cancellation policy', count: 64 },
        ],
        sentiment: { positive: 71, neutral: 22, negative: 7 },
        kb_gaps: [
            { topic: 'Pet-friendly room policy', frequency: 19 },
            { topic: 'Halal kitchen certification', frequency: 14 },
            { topic: 'Long-stay monthly discount', frequency: 11 },
        ],
    };
}

// ─── Business settings ────────────────────────────────────────────────────────

export const settingsState: Record<string, any> = {
    [BUSINESS_ID]: {
        id: BUSINESS_ID,
        name: BUSINESS_NAME,
        notification_email: 'frontoffice@sarahphotography.com',
        operating_hours: { start: '09:00', end: '18:00', timezone: 'Asia/Kuala_Lumpur' },
        timezone: 'Asia/Kuala_Lumpur',
        adr: 420,
        hourly_rate: 18,
        brand_vocabulary: 'Warm, concise, professional. Address guests as "Encik/Puan" when in Malay.',
        whatsapp_number: '+60 3-2710 1234',
        website_url: 'https://sarahphotography.com/kl',
        plan_tier: 'premium',
        is_active: true,
    },
};

// ─── Leads ────────────────────────────────────────────────────────────────────

export const leadsState: any[] = [
    {
        id: 'lead-1', conversation_id: 'conv-1', guest_name: 'Sarah Lim', guest_phone: '+60 16-228 9931',
        guest_email: 'sarah.lim@gmail.com', intent: 'service_booking', status: 'new', estimated_value: 2520,
        actual_revenue: null, priority: 'high', flag_reason: null, captured_at: iso(hoursAgo(3)),
    },
    {
        id: 'lead-2', conversation_id: 'conv-2', guest_name: 'James Wong', guest_phone: '+60 12-771 4420',
        guest_email: 'jwong@outlook.com', intent: 'service_booking', status: 'contacted', estimated_value: 1680,
        actual_revenue: null, priority: 'medium', flag_reason: null, captured_at: iso(hoursAgo(7)),
    },
    {
        id: 'lead-3', conversation_id: 'conv-3', guest_name: 'Priya Nair', guest_phone: '+60 19-334 0021',
        guest_email: 'priya.n@gmail.com', intent: 'event_inquiry', status: 'qualified', estimated_value: 8400,
        actual_revenue: null, priority: 'high', flag_reason: 'High-value group booking', captured_at: iso(daysAgo(1)),
    },
    {
        id: 'lead-4', conversation_id: 'conv-4', guest_name: 'Ahmad Faisal', guest_phone: '+60 13-882 5567',
        guest_email: null, intent: 'service_booking', status: 'converted', estimated_value: 1260,
        actual_revenue: 1380, priority: 'medium', flag_reason: null, captured_at: iso(daysAgo(2)),
    },
    {
        id: 'lead-5', conversation_id: 'conv-5', guest_name: 'Mei Chen', guest_phone: '+60 17-009 1123',
        guest_email: 'meichen@gmail.com', intent: 'service_booking', status: 'converted', estimated_value: 3360,
        actual_revenue: 3360, priority: 'high', flag_reason: null, captured_at: iso(daysAgo(3)),
    },
    {
        id: 'lead-6', conversation_id: 'conv-6', guest_name: 'David Kumar', guest_phone: '+60 11-2245 7788',
        guest_email: null, intent: 'general', status: 'lost', estimated_value: 840,
        actual_revenue: null, priority: 'low', flag_reason: null, captured_at: iso(daysAgo(4)),
    },
];

// ─── Conversations ────────────────────────────────────────────────────────────

function mkMessages(pairs: [string, string][], baseMinsAgo: number) {
    const msgs: any[] = [];
    let t = baseMinsAgo;
    let idx = 0;
    for (const [role, content] of pairs) {
        msgs.push({ id: `m-${idx++}`, role, content, sent_at: iso(minsAgo(t)) });
        t -= 1;
    }
    return msgs;
}

export const conversationsState: any[] = [
    {
        id: 'conv-1', channel: 'whatsapp', guest_name: 'Sarah Lim', guest_identifier: '+60 16-228 9931',
        status: 'handed_off', ai_mode: 'lead_capture', is_after_hours: true, message_count: 6,
        started_at: iso(hoursAgo(3)), last_message_at: iso(minsAgo(40)), has_lead: true, lead_intent: 'service_booking',
        messages: mkMessages([
            ['user', 'Hi, do you have a deluxe room available this Friday to Sunday?'],
            ['assistant', 'Good evening! Yes — our Portrait Session is available Fri–Sun at RM420/night. Would you like me to hold it for you?'],
            ['user', 'Yes please. Does it include breakfast?'],
            ['assistant', 'It does — breakfast for two at our rooftop café is included. May I have your name and email to send the confirmation?'],
            ['user', 'Sarah Lim, sarah.lim@gmail.com'],
            ['assistant', "Thank you, Sarah! I've noted your details and our front office will confirm shortly. Total for 2 nights: RM840 + breakfast included."],
        ], 180),
        lead: { id: 'lead-1', guest_name: 'Sarah Lim', guest_email: 'sarah.lim@gmail.com', guest_phone: '+60 16-228 9931', intent: 'service_booking', status: 'new', estimated_value: 2520 },
    },
    {
        id: 'conv-2', channel: 'web', guest_name: 'James Wong', guest_identifier: 'web-session-8821',
        status: 'active', ai_mode: 'concierge', is_after_hours: false, message_count: 4,
        started_at: iso(hoursAgo(7)), last_message_at: iso(minsAgo(120)), has_lead: true, lead_intent: 'service_booking',
        messages: mkMessages([
            ['user', 'What time is check-in and can I park overnight?'],
            ['assistant', 'Check-in is from 3pm. Complimentary covered parking is available for all room guests. Are you planning a stay with us?'],
            ['user', 'Maybe next week for 2 nights'],
            ['assistant', 'Lovely! Our Mini Session is RM340/night next week. Shall I check exact availability for your dates?'],
        ], 420),
        lead: { id: 'lead-2', guest_name: 'James Wong', guest_email: 'jwong@outlook.com', guest_phone: '+60 12-771 4420', intent: 'service_booking', status: 'contacted', estimated_value: 1680 },
    },
    {
        id: 'conv-3', channel: 'whatsapp', guest_name: 'Priya Nair', guest_identifier: '+60 19-334 0021',
        status: 'handed_off', ai_mode: 'handoff', is_after_hours: true, message_count: 5,
        started_at: iso(daysAgo(1)), last_message_at: iso(daysAgo(1)), has_lead: true, lead_intent: 'event_inquiry',
        messages: mkMessages([
            ['user', 'Do you host corporate events? We need a venue for ~40 people in December.'],
            ['assistant', 'Absolutely — our Photo Studio seats up to 60 banquet-style. For a 40-pax corporate event we offer half-day and full-day packages.'],
            ['user', 'Full day with lunch. What is the cost?'],
            ['assistant', 'Full-day with buffet lunch starts at RM210/pax. For 40 guests that is approximately RM8,400. I will connect you with our events manager for a tailored quote.'],
            ['user', 'Great, please do. Priya Nair, priya.n@gmail.com'],
        ], 1440),
        lead: { id: 'lead-3', guest_name: 'Priya Nair', guest_email: 'priya.n@gmail.com', guest_phone: '+60 19-334 0021', intent: 'event_inquiry', status: 'qualified', estimated_value: 8400 },
    },
    {
        id: 'conv-7', channel: 'email', guest_name: 'Lina Hassan', guest_identifier: 'lina.h@gmail.com',
        status: 'active', ai_mode: 'concierge', is_after_hours: false, message_count: 2,
        started_at: iso(minsAgo(25)), last_message_at: iso(minsAgo(24)), has_lead: false, lead_intent: null,
        messages: mkMessages([
            ['user', 'Is the swimming pool open during Ramadan, and what are the hours?'],
            ['assistant', 'Yes! Our rooftop pool stays open daily 7am–10pm throughout Ramadan. Towels are provided poolside. Anything else I can help with?'],
        ], 25),
        lead: null,
    },
];

// ─── KB documents ─────────────────────────────────────────────────────────────

export const kbState: any[] = [
    { id: 'kb-1', doc_type: 'rooms', category: 'rooms', title: 'Portrait Session', content: 'Portrait Session room, 32sqm, king bed, city view. RM420/night incl. breakfast for two.', updated_at: iso(daysAgo(6)) },
    { id: 'kb-2', doc_type: 'rooms', category: 'rooms', title: 'Mini Session', content: 'Mini Session, 26sqm, queen bed. RM340/night. Breakfast add-on RM45/pax.', updated_at: iso(daysAgo(6)) },
    { id: 'kb-3', doc_type: 'faqs', category: 'faqs', title: 'Check-in / Check-out', content: 'Check-in 3pm, check-out 12pm. Early check-in subject to availability.', updated_at: iso(daysAgo(10)) },
    { id: 'kb-4', doc_type: 'faqs', category: 'faqs', title: 'Parking', content: 'Complimentary covered parking for all room guests.', updated_at: iso(daysAgo(10)) },
    { id: 'kb-5', doc_type: 'policies', category: 'policies', title: 'Cancellation', content: 'Free cancellation up to 48 hours before arrival. Late cancellation charged 1 night.', updated_at: iso(daysAgo(12)) },
    { id: 'kb-6', doc_type: 'facilities', category: 'facilities', title: 'Facilities', content: 'Rooftop infinity pool, 24h gym, rooftop café, business centre, free high-speed WiFi.', updated_at: iso(daysAgo(8)) },
];

// ─── Portal: team, channels, support ──────────────────────────────────────────

export const teamState: any[] = [
    { id: 'tm-1', user_id: 'demo-user-1', full_name: 'Sarah Jane', email: 'sarah@sarahphotography.com', role: 'owner', last_login: iso(hoursAgo(2)) },
    { id: 'tm-2', user_id: 'u-2', full_name: 'Daniel Tan', email: 'daniel.tan@sarahphotography.com', role: 'staff', last_login: iso(hoursAgo(9)) },
    { id: 'tm-3', user_id: 'u-3', full_name: 'Nurul Izzah', email: 'nurul@sarahphotography.com', role: 'admin', last_login: iso(daysAgo(1)) },
];

export function channels() {
    return [
        {
            business_id: BUSINESS_ID, business_name: BUSINESS_NAME, business_slug: 'lumiere-kl',
            channels: {
                whatsapp: { status: 'active' },
                email: { status: 'active' },
                website: { status: 'active', embed_slug: 'lumiere-kl' },
            },
        },
        {
            business_id: BUSINESS_ID_2, business_name: BUSINESS_NAME_2, business_slug: 'lumiere-penang',
            channels: {
                whatsapp: { status: 'active' },
                email: { status: 'active' },
                website: { status: 'configuring' },
            },
        },
    ];
}

export const supportTicketsState: any[] = [
    { id: 'st-1', subject: 'Add a second WhatsApp number for Penang', description: 'We want a dedicated line for the Penang business.', priority: 'medium', status: 'open', created_at: iso(daysAgo(2)) },
    { id: 'st-2', subject: 'Export leads to CSV', description: 'Can we get a CSV export of monthly leads?', priority: 'low', status: 'resolved', created_at: iso(daysAgo(9)) },
];

// ─── SuperAdmin data ──────────────────────────────────────────────────────────

export function adminMetrics() {
    return {
        total_tenants: 14,
        active_tenants: 11,
        total_businesses: 23,
        total_conversations_alltime: 48217,
        total_conversations_mtd: 6142,
        total_leads_mtd: 1387,
        open_support_tickets: 3,
        pending_applications: 5,
    };
}

export const tenantsState: any[] = [
    { id: TENANT_ID, name: "Sarah's Creative Services", slug: 'lumiere', subscription_tier: 'premium', subscription_status: 'active', is_active: true, business_count: 2, assigned_account_manager: 'Farah Aziz', created_at: iso(daysAgo(120)) },
    { id: 'tn-2', name: 'Nail Art Studio', slug: 'tropika', subscription_tier: 'independent', subscription_status: 'active', is_active: true, business_count: 4, assigned_account_manager: 'Farah Aziz', created_at: iso(daysAgo(88)) },
    { id: 'tn-3', name: 'Boutique Bakery', slug: 'heritage-melaka', subscription_tier: 'boutique', subscription_status: 'trialing', is_active: true, business_count: 1, assigned_account_manager: 'Kavin Rao', created_at: iso(daysAgo(21)) },
    { id: 'tn-4', name: 'Freelance Designer', slug: 'borneo-eco', subscription_tier: 'pilot', subscription_status: 'active', is_active: true, business_count: 3, assigned_account_manager: 'Kavin Rao', created_at: iso(daysAgo(40)) },
    { id: 'tn-5', name: 'Local Plumber', slug: 'city-inn', subscription_tier: 'boutique', subscription_status: 'past_due', is_active: false, business_count: 1, assigned_account_manager: 'Farah Aziz', created_at: iso(daysAgo(200)) },
];

export function tenantDetail(id: string) {
    const t = tenantsState.find((x) => x.id === id) || tenantsState[0];
    return {
        ...t,
        pilot_start_date: iso(daysAgo(110)),
        pilot_end_date: iso(daysAgo(96)),
        businesses: [
            { id: BUSINESS_ID, name: BUSINESS_NAME, slug: 'lumiere-kl', is_active: true },
            { id: BUSINESS_ID_2, name: BUSINESS_NAME_2, slug: 'lumiere-penang', is_active: true },
        ],
        users: [
            { id: 'demo-user-1', email: 'sarah@sarahphotography.com', full_name: 'Sarah Jane', role: 'owner' },
            { id: 'u-2', email: 'daniel.tan@sarahphotography.com', full_name: 'Daniel Tan', role: 'staff' },
        ],
        onboarding: [
            { business_id: BUSINESS_ID, whatsapp_status: 'active', email_status: 'active', website_status: 'active', kb_populated: true, first_inquiry_received: true, channel_errors: null },
            { business_id: BUSINESS_ID_2, whatsapp_status: 'active', email_status: 'active', website_status: 'configuring', kb_populated: true, first_inquiry_received: true, channel_errors: null },
        ],
        stats: { total_conversations: 8217, total_leads: 1942, business_count: 2, user_count: 2 },
    };
}

export function pipeline() {
    const mk = (tenant_name: string, n: number) => ({
        tenant_id: `tn-${n}`, tenant_name, business_id: `prop-${n}`, created_at: iso(daysAgo(n * 2)),
    });
    return {
        provisioned: [mk('Boutique Bakery', 3)],
        channels_setup: [mk('Freelance Designer', 4)],
        live: [mk('Nail Art Studio', 2)],
        first_week_review: [mk('Tech Fixes LLC', 6)],
        fully_onboarded: [mk("Sarah's Creative Services", 1)],
    };
}

export const ticketsState: any[] = [
    { id: 'tk-1', tenant_id: 'tn-2', tenant_name: 'Nail Art Studio', subject: 'WhatsApp not receiving messages', description: 'Guests report no replies since this morning.', status: 'open', priority: 'high', created_by_name: 'Ravi (Tropika)', created_at: iso(hoursAgo(5)) },
    { id: 'tk-2', tenant_id: 'tn-3', tenant_name: 'Boutique Bakery', subject: 'How to add a new room type?', description: 'Need help updating the KB.', status: 'open', priority: 'low', created_by_name: 'Mei (Heritage)', created_at: iso(daysAgo(1)) },
    { id: 'tk-3', tenant_id: TENANT_ID, tenant_name: "Sarah's Creative Services", subject: 'Add second WhatsApp number', description: 'Dedicated line for Penang.', status: 'in_progress', priority: 'medium', created_by_name: 'Aisha (Lumière)', created_at: iso(daysAgo(2)) },
];

export const applicationsState: any[] = [
    { id: 'app-1', business_name: 'Tech Fixes LLC', contact_name: 'Marcus Lee', email: 'marcus@sunsetbay.com', phone: '+60 12-555 7788', monthly_inquiries: 64, status: 'new', notes: null, converted_to_tenant_id: null, created_at: iso(hoursAgo(8)) },
    { id: 'app-2', business_name: 'Marketing Pro', contact_name: 'Wei Jie', email: 'weijie@klcapsule.com', phone: '+60 16-220 1199', monthly_inquiries: 120, status: 'contacted', notes: 'Interested in pilot tier.', converted_to_tenant_id: null, created_at: iso(daysAgo(2)) },
    { id: 'app-3', business_name: 'FitLife Coaching', contact_name: 'Siti Aminah', email: 'siti@cameroninn.com', phone: null, monthly_inquiries: 28, status: 'qualified', notes: 'Demo scheduled.', converted_to_tenant_id: null, created_at: iso(daysAgo(4)) },
];

export function serviceHealth() {
    return {
        overall: 'ok',
        checked_at: iso(minsAgo(1)),
        services: [
            { name: 'Database (Supabase)', status: 'ok', latency_ms: 42 },
            { name: 'Gemini API', status: 'ok', latency_ms: 318 },
            { name: 'OpenAI (fallback)', status: 'ok', latency_ms: 256 },
            { name: 'WhatsApp Cloud API', status: 'ok', latency_ms: 134 },
            { name: 'SendGrid Email', status: 'ok', latency_ms: 88 },
            { name: 'Stripe Billing', status: 'ok', latency_ms: 167 },
            { name: 'Redis Cache', status: 'ok', latency_ms: 12 },
        ],
    };
}

export const maintenanceState = { enabled: false, message: '', eta: null as string | null };
export const schedulerState = { daily_report: true, followups: true, insights: true, cleanup: true };

export function systemInfo() {
    return {
        version: '0.7.0',
        environment: 'demo',
        maintenance: maintenanceState,
    };
}

// ─── Announcements ────────────────────────────────────────────────────────────

export const announcementsState: any[] = [
    {
        id: 'ann-1', type: 'feature', status: 'active', title: 'New: Monthly guest sentiment insights',
        body: 'Your dashboard now surfaces top guest topics and sentiment trends each month.',
        target_type: 'all', target_tier: null, target_tenant_id: null, scheduled_at: null, resolved_at: null,
        send_email: false, created_at: iso(daysAgo(3)), updated_at: iso(daysAgo(3)),
    },
];

export function activeAnnouncements() {
    return announcementsState
        .filter((a) => a.status === 'active')
        .map((a) => ({ id: a.id, type: a.type, title: a.title, body: a.body, created_at: a.created_at }));
}

// ─── Scripted landing-page chat (zero LLM cost) ───────────────────────────────

export interface DemoChatTurn {
    user: string;
    ai: string;
}

export const demoChatScript: DemoChatTurn[] = [
    {
        user: 'Hi! Do you have a room available this weekend?',
        ai: "Good evening, and welcome to Sarah Photography! 🌙 Yes — we have our Portrait Session available Fri–Sun at RM420/night, breakfast for two included. Would you like me to hold it?",
    },
    {
        user: 'Yes please. Is the pool open late?',
        ai: 'Wonderful! Our rooftop infinity pool is open daily 7am–10pm. May I take your name and email so our front office can confirm your booking?',
    },
    {
        user: "Sure — Sarah Lim, sarah.lim@gmail.com",
        ai: "Thank you, Sarah! ✅ I've captured your details and flagged this as a hot lead for our team. You'll get a confirmation shortly. Estimated value of this booking: RM840. Anything else I can help with tonight?",
    },
];

export const demoChatSuggestions = [
    'Do you have a room available this weekend?',
    'Yes please. Is the pool open late?',
    "Sure — Sarah Lim, sarah.lim@gmail.com",
];
