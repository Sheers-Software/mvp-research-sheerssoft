'use client';

import { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'next/navigation';

interface DailyRow {
    date: string;
    total_inquiries: number;
    after_hours_unanswered: number;
    daily_revenue_leakage: number;
    avg_response_time_minutes: number;
}

interface SampleConv {
    time_received: string;
    topic: string;
    intent: string;
    estimated_value_rm: number;
    preview: string;
    response: string;
}

interface WeeklyRollup {
    period_start: string;
    period_end: string;
    days_observed: number;
    total_inquiries: number;
    after_hours_inquiries: number;
    booking_intent_inquiries: number;
    responded_count: number;
    unanswered_count: number;
    after_hours_unanswered: number;
    avg_response_time_minutes: number;
    avg_response_time_after_hours: number;
    response_time_over_4hr: number;
    response_time_over_24hr: number;
    weekly_revenue_leakage: number;
    ota_commission_equivalent: number;
    annualised_revenue_leakage: number;
    nocturn_year_1_net_recovery: number;
    peak_inquiry_hour: number;
    top_inquiry_topics: string[];
    top_unanswered_topics: string[];
    inquiries_by_hour: Record<string, number>;
    sample_abandoned_conversations: SampleConv[];
}

interface ShadowSummary {
    property_name: string;
    property_slug: string;
    shadow_pilot_start_date: string | null;
    rollup: WeeklyRollup;
    daily_rows: DailyRow[];
}

function fmtRM(val: number) {
    return `RM ${Math.round(val).toLocaleString()}`;
}

function fmtHrs(minutes: number) {
    if (!minutes) return '—';
    if (minutes < 60) return `${Math.round(minutes)}m`;
    return `${(minutes / 60).toFixed(1)} hrs`;
}

function HourBarChart({ data }: { data: Record<string, number> }) {
    const maxVal = Math.max(...Object.values(data), 1);
    return (
        <div style={{ display: 'flex', alignItems: 'flex-end', height: 80, gap: 2, padding: '0 4px' }}>
            {Array.from({ length: 24 }, (_, h) => {
                const cnt = data[String(h)] || 0;
                const pct = (cnt / maxVal) * 100;
                const isAH = h < 9 || h >= 18;
                return (
                    <div key={h} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        <div
                            title={`${h}:00 — ${cnt} inquiries`}
                            style={{
                                width: '100%',
                                height: `${Math.max(pct, 2)}%`,
                                background: isAH ? '#E24B4A' : '#1D9E75',
                                borderRadius: 2,
                                minHeight: cnt > 0 ? 3 : 1,
                            }}
                        />
                        {h % 4 === 0 && (
                            <div style={{ fontSize: 8, color: '#888', marginTop: 2 }}>{h}</div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}

export default function ShadowDashboardPage() {
    const params = useParams();
    const searchParams = useSearchParams();
    const slug = params?.slug as string;
    const token = searchParams?.get('token');

    const [data, setData] = useState<ShadowSummary | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    useEffect(() => {
        if (!slug || !token) {
            setError('Invalid dashboard link. Contact ahmad@sheerssoft.com for a new link.');
            setLoading(false);
            return;
        }
        fetch(`${apiBase}/api/v1/shadow/${slug}/summary?token=${encodeURIComponent(token)}`)
            .then(async res => {
                if (!res.ok) {
                    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
                    throw new Error(err.detail || 'Failed to load dashboard');
                }
                return res.json();
            })
            .then(setData)
            .catch(e => setError(e.message))
            .finally(() => setLoading(false));
    }, [slug, token, apiBase]);

    if (loading) {
        return (
            <div style={{ minHeight: '100vh', background: '#0e0e10', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#e8e6e0' }}>
                <div>Loading your WhatsApp performance data...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ minHeight: '100vh', background: '#0e0e10', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
                <div style={{ maxWidth: 480, textAlign: 'center', color: '#e8e6e0' }}>
                    <div style={{ fontSize: 40, marginBottom: 16 }}>⚠</div>
                    <div style={{ fontSize: 16, marginBottom: 8, fontWeight: 500 }}>Dashboard link expired or invalid</div>
                    <div style={{ fontSize: 13, color: '#888', marginBottom: 24 }}>{error}</div>
                    <a href="mailto:basyir@sheerssoft.com" style={{ background: '#1D9E75', color: 'white', padding: '12px 24px', borderRadius: 6, textDecoration: 'none', fontSize: 13 }}>
                        Request a new link
                    </a>
                </div>
            </div>
        );
    }

    if (!data) return null;
    const r = data.rollup;

    const kpis = [
        { label: 'Inquiries Received', value: r.total_inquiries.toLocaleString(), sub: `${r.after_hours_inquiries} after-hours` },
        { label: 'After-Hours Unanswered', value: r.after_hours_unanswered.toLocaleString(), sub: 'No staff reply', accent: '#E24B4A' },
        { label: 'Revenue Leaked', value: fmtRM(r.weekly_revenue_leakage), sub: 'Conservative est.', accent: '#E24B4A' },
        { label: 'Avg After-Hours Response', value: fmtHrs(r.avg_response_time_after_hours), sub: 'When they did reply' },
        { label: 'Annualised Leakage', value: fmtRM(r.annualised_revenue_leakage), sub: 'If pattern continues', accent: '#EF9F27' },
        { label: 'Booking Intent Rate', value: `${Math.round((r.booking_intent_inquiries / Math.max(r.total_inquiries, 1)) * 100)}%`, sub: 'Of unanswered msgs', accent: '#EF9F27' },
    ];

    return (
        <div style={{ background: '#0e0e10', minHeight: '100vh', color: '#e8e6e0', fontFamily: '-apple-system, "Segoe UI", system-ui, sans-serif' }}>
            {/* Header */}
            <div style={{ borderBottom: '0.5px solid rgba(255,255,255,0.08)', padding: '20px 24px' }}>
                <div style={{ maxWidth: 960, margin: '0 auto', display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#1D9E75' }} />
                    <span style={{ fontSize: 11, fontWeight: 600, color: '#1D9E75', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                        Nocturn AI · Shadow Pilot Report
                    </span>
                </div>
            </div>

            <div style={{ maxWidth: 960, margin: '0 auto', padding: '32px 24px 80px' }}>
                {/* Title */}
                <div style={{ marginBottom: 32 }}>
                    <h1 style={{ fontSize: 22, fontWeight: 500, margin: '0 0 6px', color: '#e8e6e0' }}>{data.property_name}</h1>
                    <p style={{ fontSize: 13, color: '#9e9c96', margin: 0 }}>
                        WhatsApp Performance · {new Date(r.period_start).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })} – {new Date(r.period_end).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })} · {r.days_observed} days observed
                    </p>
                </div>

                {/* KPI Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 32 }}>
                    {kpis.map((k, i) => (
                        <div key={i} style={{ background: '#161618', border: '0.5px solid rgba(255,255,255,0.08)', borderRadius: 10, padding: '16px 20px' }}>
                            <div style={{ fontSize: 24, fontWeight: 500, color: k.accent || '#e8e6e0', marginBottom: 4 }}>{k.value}</div>
                            <div style={{ fontSize: 12, fontWeight: 500, color: '#e8e6e0', marginBottom: 2 }}>{k.label}</div>
                            <div style={{ fontSize: 11, color: '#5a5856' }}>{k.sub}</div>
                        </div>
                    ))}
                </div>

                {/* Hour Chart */}
                <div style={{ background: '#161618', border: '0.5px solid rgba(255,255,255,0.08)', borderRadius: 10, padding: '20px 20px 16px', marginBottom: 20 }}>
                    <div style={{ fontSize: 11, fontWeight: 600, color: '#5a5856', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>
                        When They Messaged — Inquiries by Hour
                    </div>
                    <HourBarChart data={r.inquiries_by_hour} />
                    <div style={{ display: 'flex', gap: 16, marginTop: 12 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#888' }}>
                            <div style={{ width: 8, height: 8, background: '#1D9E75', borderRadius: 2 }} /> Business hours (replied)
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#888' }}>
                            <div style={{ width: 8, height: 8, background: '#E24B4A', borderRadius: 2 }} /> After hours (unanswered)
                        </div>
                    </div>
                </div>

                {/* Sample Unanswered Conversations */}
                {r.sample_abandoned_conversations.length > 0 && (
                    <div style={{ background: '#161618', border: '0.5px solid rgba(255,255,255,0.08)', borderRadius: 10, marginBottom: 20, overflow: 'hidden' }}>
                        <div style={{ padding: '14px 20px', borderBottom: '0.5px solid rgba(255,255,255,0.08)', fontSize: 11, fontWeight: 600, color: '#5a5856', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            What They Were Asking — That Went Unanswered
                        </div>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ borderBottom: '0.5px solid rgba(255,255,255,0.08)' }}>
                                    {['Time', 'Type', 'Message preview', 'Est. value', 'Response'].map(h => (
                                        <th key={h} style={{ padding: '10px 16px', fontSize: 10, color: '#5a5856', fontWeight: 600, textAlign: 'left', textTransform: 'uppercase' }}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {r.sample_abandoned_conversations.map((c, i) => (
                                    <tr key={i} style={{ borderBottom: '0.5px solid rgba(255,255,255,0.06)' }}>
                                        <td style={{ padding: '10px 16px', fontSize: 12, color: '#9e9c96' }}>{c.time_received}</td>
                                        <td style={{ padding: '10px 16px', fontSize: 12 }}>{c.intent.replace(/_/g, ' ')}</td>
                                        <td style={{ padding: '10px 16px', fontSize: 12, color: '#9e9c96', maxWidth: 200 }}>"{c.preview.substring(0, 60)}..."</td>
                                        <td style={{ padding: '10px 16px', fontSize: 12, fontWeight: 500, color: '#1D9E75' }}>{fmtRM(c.estimated_value_rm)}</td>
                                        <td style={{ padding: '10px 16px', fontSize: 12, color: '#E24B4A' }}>{c.response}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {/* What If comparison */}
                <div style={{ background: '#161618', border: '0.5px solid rgba(255,255,255,0.08)', borderRadius: 10, padding: '20px', marginBottom: 24 }}>
                    <div style={{ fontSize: 11, fontWeight: 600, color: '#5a5856', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>
                        What If Nocturn AI Had Been Active This Week
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                        <div style={{ background: '#1e1e21', borderRadius: 8, padding: '14px 16px' }}>
                            <div style={{ fontSize: 11, color: '#5a5856', marginBottom: 10, fontWeight: 600 }}>THIS WEEK (ACTUAL)</div>
                            {[
                                [`${r.after_hours_unanswered} unanswered inquiries`, true],
                                [r.avg_response_time_after_hours ? `Avg ${fmtHrs(r.avg_response_time_after_hours)} response time` : 'No after-hours replies', true],
                                [fmtRM(r.weekly_revenue_leakage) + ' revenue leaked', true],
                            ].map(([txt, bad], i) => (
                                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, fontSize: 13 }}>
                                    <span style={{ color: '#E24B4A' }}>✗</span>
                                    <span style={{ color: '#9e9c96' }}>{txt}</span>
                                </div>
                            ))}
                        </div>
                        <div style={{ background: 'rgba(29,158,117,0.08)', border: '0.5px solid rgba(29,158,117,0.2)', borderRadius: 8, padding: '14px 16px' }}>
                            <div style={{ fontSize: 11, color: '#1D9E75', marginBottom: 10, fontWeight: 600 }}>WITH NOCTURN AI</div>
                            {[
                                `All ${r.after_hours_inquiries} inquiries answered in <30 seconds`,
                                'Response time: under 30 seconds',
                                `Est. ${fmtRM(r.weekly_revenue_leakage * 0.6)} in captured bookings`,
                                `${r.unanswered_count} warm leads in your morning queue`,
                            ].map((txt, i) => (
                                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, fontSize: 13 }}>
                                    <span style={{ color: '#1D9E75' }}>✓</span>
                                    <span style={{ color: '#e8e6e0' }}>{txt}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* CTA */}
                <div style={{ border: '0.5px solid rgba(29,158,117,0.3)', borderRadius: 10, padding: '24px', background: 'rgba(29,158,117,0.05)', textAlign: 'center' }}>
                    <div style={{ fontSize: 18, fontWeight: 500, color: '#e8e6e0', marginBottom: 6 }}>
                        Start 48-Hour Implementation
                    </div>
                    <div style={{ fontSize: 13, color: '#9e9c96', marginBottom: 20, lineHeight: 1.6 }}>
                        RM 999 one-time setup. RM 199/month. 3% only on confirmed bookings.<br />
                        30-day revenue recovery guarantee — if we don't prove it, next month is free.
                    </div>
                    <a
                        href="/apply"
                        style={{
                            display: 'inline-block', background: '#1D9E75', color: 'white',
                            padding: '14px 32px', borderRadius: 6, textDecoration: 'none',
                            fontWeight: 600, fontSize: 14, letterSpacing: '0.02em'
                        }}
                    >
                        Start 48-Hour Implementation — RM 999
                    </a>
                    <div style={{ marginTop: 12, fontSize: 11, color: '#5a5856' }}>No contract. No lock-in. Cancellable anytime.</div>
                </div>
            </div>
        </div>
    );
}
