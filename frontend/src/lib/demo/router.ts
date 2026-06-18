/**
 * Demo request router.
 *
 * resolveDemo() maps every API path the frontend calls to seeded data from
 * ./data.ts. Used by lib/api.ts when NEXT_PUBLIC_DEMO_MODE === 'true'. Mutations
 * update module-level state so the demo feels interactive within a session.
 *
 * Unknown paths resolve to a sensible empty value so no page ever crashes.
 */

import * as D from './data';

type Method = 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';

function genId(prefix: string) {
    return `${prefix}-${Math.random().toString(36).slice(2, 8)}`;
}

// A KB response that satisfies both consumers: an array (portal) that also
// carries a `.documents` business (admin tenant-detail).
function kbResponse() {
    const arr = [...D.kbState];
    (arr as any).documents = D.kbState;
    return arr;
}

export async function resolveDemo<T = any>(
    method: Method,
    rawPath: string,
    body?: any,
): Promise<T> {
    // Normalise: strip querystring for matching, keep it for parsing.
    const [path, query = ''] = rawPath.split('?');
    const qs = new URLSearchParams(query);

    // Small artificial latency so loading states are visible (feels real).
    await new Promise((r) => setTimeout(r, 180));

    const seg = path.split('/').filter(Boolean); // e.g. ['businesses','id','analytics']

    // ── Auth ──────────────────────────────────────────────────────────────
    if (path === '/auth/me') return D.demoUser() as T;
    if (path === '/auth/magic-link' || path === '/auth/token') return {} as T;

    // ── Portal / tenant context ─────────────────────────────────────────────
    if (path === '/portal/home') return D.portalHome() as T;
    if (path === '/portal/team') {
        if (method === 'POST') return {} as T; // invite — no immediate row
        return D.teamState as T;
    }
    if (path === '/portal/channels') return D.channels() as T;

    // ── Analytics / dashboard ───────────────────────────────────────────────
    if (path === '/analytics/dashboard') return D.liveStats() as T;
    if (path === '/system/info') return D.systemInfo() as T;
    if (path === '/announcements/active') return D.activeAnnouncements() as T;

    // ── Business-scoped ─────────────────────────────────────────────────────
    if (seg[0] === 'businesses' && seg.length >= 3) {
        const pid = seg[1];
        const sub = seg[2];
        if (sub === 'analytics')
            return D.analytics(pid, qs.get('from_date') || undefined, qs.get('to_date') || undefined) as T;
        if (sub === 'insights') return D.insights(pid) as T;
        if (sub === 'settings') {
            if (method === 'PUT') {
                D.settingsState[pid] = { ...(D.settingsState[pid] || D.settingsState[D.BUSINESS_ID]), ...body, id: pid };
                return D.settingsState[pid] as T;
            }
            return (D.settingsState[pid] || D.settingsState[D.BUSINESS_ID]) as T;
        }
        if (sub === 'leads') return D.leadsState as T;
        if (sub === 'kb') {
            if (method === 'POST') {
                const doc = { id: genId('kb'), category: body?.doc_type || 'general', updated_at: new Date().toISOString(), ...body };
                D.kbState.push(doc);
                return doc as T;
            }
            if (method === 'PUT') {
                const id = seg[3];
                const d = D.kbState.find((x) => x.id === id);
                if (d) Object.assign(d, body, { updated_at: new Date().toISOString() });
                return (d || {}) as T;
            }
            if (method === 'DELETE') {
                const id = seg[3];
                const i = D.kbState.findIndex((x) => x.id === id);
                if (i >= 0) D.kbState.splice(i, 1);
                return {} as T;
            }
            return kbResponse() as T;
        }
    }

    // ── Conversations ───────────────────────────────────────────────────────
    if (seg[0] === 'conversations' && seg[1]) {
        const conv = D.conversationsState.find((c) => c.id === seg[1]);
        if (seg[2] === 'reply' && method === 'POST') {
            if (conv) {
                conv.messages.push({ id: genId('m'), role: 'staff', content: body?.content || '', sent_at: new Date().toISOString() });
                conv.message_count = conv.messages.length;
                conv.last_message_at = new Date().toISOString();
            }
            return {} as T;
        }
        if (seg[2] && method === 'POST') {
            // status actions: takeover / resolve / handoff etc.
            if (conv) conv.status = seg[2] === 'resolve' ? 'resolved' : seg[2] === 'takeover' ? 'handed_off' : conv.status;
            return {} as T;
        }
        return (conv || D.conversationsState[0]) as T;
    }

    // ── Leads ───────────────────────────────────────────────────────────────
    if (seg[0] === 'leads' && seg[2] === 'convert' && method === 'POST') {
        const l = D.leadsState.find((x) => x.id === seg[1]);
        if (l) { l.status = 'converted'; l.actual_revenue = l.estimated_value; }
        return {} as T;
    }

    // ── Support ─────────────────────────────────────────────────────────────
    if (path === '/support/tickets') {
        if (method === 'POST') {
            const t = { id: genId('st'), status: 'open', created_at: new Date().toISOString(), ...body };
            D.supportTicketsState.unshift(t);
            return t as T;
        }
        return D.supportTicketsState as T;
    }
    if (path === '/support/chat' && method === 'POST') {
        return { reply: "Thanks for reaching out! This is the SheersSoft support assistant. In the live product I answer setup questions and can open a ticket for our team.", handoff: false } as T;
    }

    // ── Billing ─────────────────────────────────────────────────────────────
    if (seg[0] === 'billing') {
        return { checkout_url: '#demo-checkout' } as T;
    }

    // ── Audit (revenue calculator) ──────────────────────────────────────────
    if (path === '/audit/calculate' && method === 'POST') {
        const rooms = body?.monthly_inquiries || 40;
        const adr = body?.adr || 350;
        const daily = body?.daily_msgs || 15;
        const afterHours = Math.round(daily * 0.55);
        const monthly = afterHours * 30;
        const lost = Math.round(monthly * 0.18);
        const revLost = lost * adr * 2.1;
        const ota = revLost * (body?.ota_commission_rate || 0.18);
        const leakage = revLost + ota;
        return {
            monthly_inquiries: rooms, adr, daily_msgs_used: daily, after_hours_msgs_per_day: afterHours,
            monthly_after_hours_msgs: monthly, lost_bookings_per_month: lost, avg_stay_nights: 2.1,
            revenue_lost_monthly: Math.round(revLost), ota_commission_monthly: Math.round(ota),
            total_monthly_leakage: Math.round(leakage), annual_leakage: Math.round(leakage * 12),
            conservative_annual: Math.round(leakage * 12 * 0.6), annual_net_recovery: Math.round(leakage * 12 * 0.6 - 8400),
            roi_multiple: Math.round((leakage * 12 * 0.6) / 8400),
        } as T;
    }
    if (path === '/audit/records') return (method === 'GET' ? [] : {}) as T;
    if (path === '/audit/submit') return {} as T;
    if (seg[0] === 'audit' && seg[1] === 'records') return {} as T;

    // ── SuperAdmin ──────────────────────────────────────────────────────────
    if (path === '/superadmin/metrics') return D.adminMetrics() as T;
    if (path === '/superadmin/tenants') {
        // Some callers expect { tenants: [...] }, others the array directly.
        const arr = [...D.tenantsState];
        (arr as any).tenants = D.tenantsState;
        return arr as T;
    }
    if (seg[0] === 'superadmin' && seg[1] === 'tenants' && seg[2]) {
        // tenantDetail already carries `.businesses`, satisfying both the
        // tenant-detail page (TenantDetails) and kb-ingestion ({ businesses }).
        return D.tenantDetail(seg[2]) as T;
    }
    if (path === '/superadmin/pipeline') return D.pipeline() as T;
    if (path === '/superadmin/tickets') return D.ticketsState as T;
    if (seg[0] === 'superadmin' && seg[1] === 'tickets' && method === 'PATCH') {
        const t = D.ticketsState.find((x) => x.id === seg[2]);
        if (t && body) Object.assign(t, body);
        return (t || {}) as T;
    }
    if (path === '/superadmin/announcements') {
        if (method === 'POST') {
            const a = { id: genId('ann'), status: 'active', created_at: new Date().toISOString(), updated_at: new Date().toISOString(), target_type: 'all', send_email: false, ...body };
            D.announcementsState.unshift(a);
            return a as T;
        }
        return D.announcementsState as T;
    }
    if (seg[0] === 'superadmin' && seg[1] === 'announcements' && method === 'PATCH') {
        const a = D.announcementsState.find((x) => x.id === seg[2]);
        if (a && body) Object.assign(a, body, { updated_at: new Date().toISOString() });
        return (a || {}) as T;
    }
    if (path === '/superadmin/service-health') return D.serviceHealth() as T;
    if (path === '/superadmin/scheduler-config') {
        if (method === 'PUT') { Object.assign(D.schedulerState, body?.jobs || body); }
        return { jobs: D.schedulerState } as T;
    }
    if (path === '/superadmin/maintenance') {
        if (method === 'PUT') { Object.assign(D.maintenanceState, body); }
        return D.maintenanceState as T;
    }
    if (path === '/superadmin/shadow-pilots') {
        if (method === 'POST') return { business_id: genId('prop') } as T;
        return [] as T;
    }
    if (seg[0] === 'superadmin' && seg[1] === 'shadow-pilots') return {} as T;

    if (path === '/superadmin/applications') return D.applicationsState as T;
    if (seg[0] === 'superadmin' && seg[1] === 'applications' && method === 'PATCH') {
        const a = D.applicationsState.find((x) => x.id === seg[2]);
        if (a && body) Object.assign(a, body);
        return (a || {}) as T;
    }

    // ── Onboarding ──────────────────────────────────────────────────────────
    if (seg[0] === 'onboarding') return {} as T;

    // ── Fallback: never crash a page ────────────────────────────────────────
    if (method === 'GET') return [] as T;
    return {} as T;
}
