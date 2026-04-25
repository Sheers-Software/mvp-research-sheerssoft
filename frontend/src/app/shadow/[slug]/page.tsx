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
                                background: isAH ? 'var(--red)' : 'var(--teal)',
                                borderRadius: 2,
                                minHeight: cnt > 0 ? 3 : 1,
                            }}
                        />
                        {h % 4 === 0 && (
                            <div style={{ fontSize: 8, color: 'var(--text3)', marginTop: 2 }}>{h}</div>
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
            <div style={{ minHeight: '100vh', background: 'var(--bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text)' }}>
                <div style={{ textAlign: 'center' }}>
                    <div className="loader" style={{ margin: '0 auto 12px' }} />
                    <div style={{ fontSize: 13, color: 'var(--text2)' }}>Loading your WhatsApp performance data...</div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ minHeight: '100vh', background: 'var(--bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
                <div style={{ maxWidth: 460, textAlign: 'center', color: 'var(--text)' }}>
                    <div style={{ fontSize: 32, marginBottom: 14, color: 'var(--text3)' }}>⚠</div>
                    <div style={{ fontSize: 15, marginBottom: 8, fontWeight: 500 }}>Dashboard link expired or invalid</div>
                    <div style={{ fontSize: 13, color: 'var(--text3)', marginBottom: 22 }}>{error}</div>
                    <a
                        href="mailto:basyir@sheerssoft.com"
                        style={{
                            background: 'var(--teal)',
                            color: 'white',
                            padding: '11px 24px',
                            borderRadius: 'var(--radius-sm)',
                            textDecoration: 'none',
                            fontSize: 13,
                            fontWeight: 600,
                        }}
                    >
                        Request a new link
                    </a>
                </div>
            </div>
        );
    }

    if (!data) return null;
    const r = data.rollup;

    const periodLabel = `${new Date(r.period_start).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })} – ${new Date(r.period_end).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })} · ${r.days_observed} days`;

    const kpis = [
        { label: 'Inquiries Received', value: r.total_inquiries.toLocaleString(), sub: `${r.after_hours_inquiries} after-hours` },
        { label: 'After-Hours Unanswered', value: r.after_hours_unanswered.toLocaleString(), sub: 'No staff reply', accent: 'var(--red)' },
        { label: 'Revenue Leaked', value: fmtRM(r.weekly_revenue_leakage), sub: 'Conservative est.', accent: 'var(--red)' },
        { label: 'Avg After-Hours Response', value: fmtHrs(r.avg_response_time_after_hours), sub: 'When they did reply' },
        { label: 'Annualised Leakage', value: fmtRM(r.annualised_revenue_leakage), sub: 'If pattern continues', accent: 'var(--amber)' },
        { label: 'Booking Intent Rate', value: `${Math.round((r.booking_intent_inquiries / Math.max(r.total_inquiries, 1)) * 100)}%`, sub: 'Of unanswered msgs', accent: 'var(--amber)' },
    ];

    const cardStyle: React.CSSProperties = {
        background: 'var(--bg2)',
        border: '0.5px solid var(--border)',
        borderRadius: 'var(--radius)',
        padding: '16px 20px',
    };

    const sectionLabelStyle: React.CSSProperties = {
        fontSize: 10,
        fontWeight: 600,
        color: 'var(--text3)',
        textTransform: 'uppercase',
        letterSpacing: '0.06em',
        marginBottom: 14,
    };

    return (
        <div style={{ background: 'var(--bg)', minHeight: '100vh', color: 'var(--text)', fontFamily: 'Inter, -apple-system, "Segoe UI", system-ui, sans-serif', fontSize: 13 }}>
            {/* Wordmark header */}
            <div style={{ borderBottom: '0.5px solid var(--border)', padding: '16px 24px', background: 'var(--bg2)' }}>
                <div style={{ maxWidth: 960, margin: '0 auto', display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--teal)', flexShrink: 0 }} />
                    <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--teal)', letterSpacing: '-0.01em' }}>
                        Nocturn AI
                    </span>
                    <span style={{ fontSize: 10, color: 'var(--text3)', paddingLeft: 10, borderLeft: '1px solid var(--border2)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                        Shadow Pilot Report
                    </span>
                </div>
            </div>

            <div style={{ maxWidth: 960, margin: '0 auto', padding: '28px 24px 80px' }}>
                {/* Title */}
                <div style={{ marginBottom: 28 }}>
                    <h1 style={{ fontSize: 20, fontWeight: 500, margin: '0 0 5px', color: 'var(--text)' }}>{data.property_name}</h1>
                    <p style={{ fontSize: 12, color: 'var(--text2)', margin: 0 }}>
                        WhatsApp Performance · {periodLabel}
                    </p>
                </div>

                {/* KPI Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginBottom: 28 }}>
                    {kpis.map((k, i) => (
                        <div key={i} style={cardStyle}>
                            <div style={{ fontSize: 22, fontWeight: 600, color: k.accent || 'var(--text)', marginBottom: 4, letterSpacing: '-0.01em' }}>{k.value}</div>
                            <div style={{ fontSize: 12, fontWeight: 500, color: 'var(--text)', marginBottom: 2 }}>{k.label}</div>
                            <div style={{ fontSize: 11, color: 'var(--text3)' }}>{k.sub}</div>
                        </div>
                    ))}
                </div>

                {/* Hour Chart */}
                <div style={{ ...cardStyle, padding: '18px 20px 14px', marginBottom: 16 }}>
                    <div style={sectionLabelStyle}>
                        When They Messaged — Inquiries by Hour
                    </div>
                    <HourBarChart data={r.inquiries_by_hour} />
                    <div style={{ display: 'flex', gap: 16, marginTop: 10 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: 'var(--text3)' }}>
                            <div style={{ width: 8, height: 8, background: 'var(--teal)', borderRadius: 2 }} /> Business hours (replied)
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: 'var(--text3)' }}>
                            <div style={{ width: 8, height: 8, background: 'var(--red)', borderRadius: 2 }} /> After hours (unanswered)
                        </div>
                    </div>
                </div>

                {/* Sample Unanswered Conversations */}
                {r.sample_abandoned_conversations.length > 0 && (
                    <div style={{ ...cardStyle, padding: 0, marginBottom: 16, overflow: 'hidden' }}>
                        <div style={{ padding: '12px 20px', borderBottom: '0.5px solid var(--border)', ...sectionLabelStyle, marginBottom: 0 }}>
                            What They Were Asking — That Went Unanswered
                        </div>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ borderBottom: '0.5px solid var(--border)' }}>
                                    {['Time', 'Type', 'Message preview', 'Est. value', 'Response'].map(h => (
                                        <th key={h} style={{ padding: '9px 16px', fontSize: 10, color: 'var(--text3)', fontWeight: 600, textAlign: 'left', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {r.sample_abandoned_conversations.map((c, i) => (
                                    <tr key={i} style={{ borderBottom: '0.5px solid var(--border)' }}>
                                        <td style={{ padding: '9px 16px', fontSize: 12, color: 'var(--text2)' }}>{c.time_received}</td>
                                        <td style={{ padding: '9px 16px', fontSize: 12, color: 'var(--text)' }}>{c.intent.replace(/_/g, ' ')}</td>
                                        <td style={{ padding: '9px 16px', fontSize: 12, color: 'var(--text2)', maxWidth: 200 }}>&ldquo;{c.preview.substring(0, 60)}...&rdquo;</td>
                                        <td style={{ padding: '9px 16px', fontSize: 12, fontWeight: 500, color: 'var(--teal)' }}>{fmtRM(c.estimated_value_rm)}</td>
                                        <td style={{ padding: '9px 16px', fontSize: 12, color: 'var(--red)' }}>{c.response}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {/* What If comparison */}
                <div style={{ ...cardStyle, marginBottom: 20 }}>
                    <div style={sectionLabelStyle}>
                        What If Nocturn AI Had Been Active This Week
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                        <div style={{ background: 'var(--bg3)', borderRadius: 8, padding: '12px 14px' }}>
                            <div style={{ fontSize: 10, color: 'var(--text3)', marginBottom: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>This week (actual)</div>
                            {[
                                `${r.after_hours_unanswered} unanswered inquiries`,
                                r.avg_response_time_after_hours ? `Avg ${fmtHrs(r.avg_response_time_after_hours)} response time` : 'No after-hours replies',
                                fmtRM(r.weekly_revenue_leakage) + ' revenue leaked',
                            ].map((txt, i) => (
                                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 7, fontSize: 12 }}>
                                    <span style={{ color: 'var(--red)', fontWeight: 600, fontSize: 13 }}>✗</span>
                                    <span style={{ color: 'var(--text2)' }}>{txt}</span>
                                </div>
                            ))}
                        </div>
                        <div style={{ background: 'var(--teal-bg)', border: '0.5px solid rgba(29,158,117,0.25)', borderRadius: 8, padding: '12px 14px' }}>
                            <div style={{ fontSize: 10, color: 'var(--teal)', marginBottom: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>With Nocturn AI</div>
                            {[
                                `All ${r.after_hours_inquiries} inquiries answered in <30 seconds`,
                                'Response time: under 30 seconds',
                                `Est. ${fmtRM(r.weekly_revenue_leakage * 0.6)} in captured bookings`,
                                `${r.unanswered_count} warm leads in your morning queue`,
                            ].map((txt, i) => (
                                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 7, fontSize: 12 }}>
                                    <span style={{ color: 'var(--teal)', fontWeight: 600, fontSize: 13 }}>✓</span>
                                    <span style={{ color: 'var(--text)' }}>{txt}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* CTA */}
                <div style={{
                    border: '1px solid rgba(29,158,117,0.25)',
                    borderRadius: 'var(--radius)',
                    padding: '28px 24px',
                    background: 'var(--teal-bg)',
                    textAlign: 'center',
                }}>
                    <div style={{ fontSize: 18, fontWeight: 600, color: 'var(--text)', marginBottom: 6, letterSpacing: '-0.01em' }}>
                        Start 48-Hour Implementation
                    </div>
                    <div style={{ fontSize: 13, color: 'var(--text2)', marginBottom: 22, lineHeight: 1.65 }}>
                        RM 999 one-time setup. RM 199/month. 3% only on confirmed bookings.<br />
                        30-day revenue recovery guarantee — if we don't prove it, next month is free.
                    </div>
                    <a
                        href="/apply"
                        style={{
                            display: 'inline-block',
                            background: 'var(--teal)',
                            color: 'white',
                            padding: '14px 40px',
                            borderRadius: 'var(--radius-sm)',
                            textDecoration: 'none',
                            fontWeight: 600,
                            fontSize: 14,
                            letterSpacing: '0.02em',
                            minWidth: 280,
                            boxShadow: '0 4px 20px var(--teal-glow)',
                            transition: 'background 0.15s, box-shadow 0.15s',
                        }}
                    >
                        Start 48-Hour Implementation — RM 999
                    </a>
                    <div style={{ marginTop: 12, fontSize: 11, color: 'var(--text3)' }}>No contract. No lock-in. Cancellable anytime.</div>
                </div>
            </div>
        </div>
    );
}
