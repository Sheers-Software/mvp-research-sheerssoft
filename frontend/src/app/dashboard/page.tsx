'use client';

import { useEffect, useState } from 'react';
import { apiGet } from '@/lib/api';
import Link from 'next/link';

interface LiveStats {
    property_id: string;
    property_name: string;
    report_date: string;
    total_inquiries: number;
    after_hours_inquiries: number;
    after_hours_responded: number;
    leads_captured: number;
    avg_response_time_sec: number;
    estimated_revenue_recovered: number;
    actual_revenue_recovered: number;
    active_conversations: number;
    handed_off_conversations: number;
    inquiries_handled_by_ai: number;
    inquiries_handled_manually: number;
    cost_savings: number;
}

interface PeriodTotals {
    total_inquiries: number;
    after_hours_inquiries: number;
    leads_captured: number;
    handoffs: number;
    inquiries_handled_by_ai: number;
    avg_response_time_sec: number;
    estimated_revenue_recovered: number;
    cost_savings: number;
}

interface AnalyticsData {
    property_id: string;
    period: { from: string; to: string };
    totals: PeriodTotals;
}

function KpiCard({
    label,
    value,
    sub,
    color,
}: {
    label: string;
    value: string;
    sub?: string;
    color?: string;
}) {
    return (
        <div className="stat-card">
            <div className="stat-label">{label}</div>
            <div className="stat-value" style={{ color: color || 'var(--text)' }}>{value}</div>
            {sub && <div className="stat-sub">{sub}</div>}
        </div>
    );
}

export default function DashboardPage() {
    const [live, setLive] = useState<LiveStats | null>(null);
    const [period, setPeriod] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [noProperty, setNoProperty] = useState(false);

    useEffect(() => {
        apiGet<LiveStats>('/analytics/dashboard')
            .then((data) => {
                setLive(data);
                const to = new Date().toISOString().split('T')[0];
                const from = new Date(Date.now() - 30 * 86400000).toISOString().split('T')[0];
                return apiGet<AnalyticsData>(
                    `/properties/${data.property_id}/analytics?from_date=${from}&to_date=${to}`
                );
            })
            .then(setPeriod)
            .catch((err) => {
                if (err?.status === 404) setNoProperty(true);
            })
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="flex justify-center" style={{ padding: 80 }}>
                <div className="loader" />
            </div>
        );
    }

    if (noProperty || !live) {
        return (
            <div className="empty-state" style={{ marginTop: 80 }}>
                <div className="empty-icon" style={{ fontSize: 32, opacity: 0.4 }}>◎</div>
                <p style={{ color: 'var(--text2)', fontSize: 14, marginTop: 8 }}>No property configured yet.</p>
                <p className="text-sm" style={{ marginTop: 6, color: 'var(--text3)' }}>
                    Your account manager is setting up your property. You&apos;ll see live data here once your AI concierge goes live.
                </p>
            </div>
        );
    }

    const today = new Date().toLocaleDateString('en-MY', {
        weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
    });

    const hasActivity = live.total_inquiries > 0 || live.leads_captured > 0;
    const t = period?.totals;

    const aiPct = live.total_inquiries > 0
        ? Math.round((live.inquiries_handled_by_ai / live.total_inquiries) * 100)
        : 0;

    return (
        <div>
            {/* Header */}
            <div className="page-header">
                <div>
                    <h1>{live.property_name}</h1>
                    <p className="text-sm" style={{ marginTop: 4, color: 'var(--text3)' }}>
                        Today · {today}
                    </p>
                </div>
                {live.handed_off_conversations > 0 && (
                    <Link href="/dashboard/conversations" className="btn btn-primary btn-sm">
                        {live.handed_off_conversations} pending handoff{live.handed_off_conversations !== 1 ? 's' : ''}
                    </Link>
                )}
            </div>

            {/* Today's live KPIs */}
            {hasActivity ? (
                <>
                    <div className="grid grid-4 animate-in" style={{ marginBottom: 8 }}>
                        <KpiCard
                            label="Revenue Recovered"
                            value={`RM ${live.estimated_revenue_recovered.toLocaleString('en-MY', { maximumFractionDigits: 0 })}`}
                            sub={live.actual_revenue_recovered > 0 ? `RM ${live.actual_revenue_recovered.toLocaleString('en-MY', { maximumFractionDigits: 0 })} confirmed` : 'estimated today'}
                            color="var(--teal)"
                        />
                        <KpiCard
                            label="Leads Captured"
                            value={live.leads_captured.toString()}
                            sub="from AI conversations"
                            color="var(--amber)"
                        />
                        <KpiCard
                            label="Inquiries Handled"
                            value={live.total_inquiries.toString()}
                            sub={`${aiPct}% by AI`}
                            color="var(--text)"
                        />
                        <KpiCard
                            label="After-Hours"
                            value={live.after_hours_inquiries.toString()}
                            sub={live.after_hours_inquiries > 0 ? `${live.after_hours_responded} responded` : 'no overnight yet'}
                            color="var(--purple)"
                        />
                    </div>

                    <div className="grid grid-4 animate-in" style={{ marginBottom: 28 }}>
                        <KpiCard
                            label="Cost Savings"
                            value={`RM ${live.cost_savings.toLocaleString('en-MY', { maximumFractionDigits: 0 })}`}
                            sub="vs. manual handling"
                            color="var(--purple)"
                        />
                        <KpiCard
                            label="Avg Response"
                            value={live.avg_response_time_sec > 0 ? `${live.avg_response_time_sec.toFixed(1)}s` : '—'}
                            sub="end-to-end"
                            color="var(--teal)"
                        />
                        <KpiCard
                            label="AI Handled"
                            value={live.inquiries_handled_by_ai.toString()}
                            sub={`${live.inquiries_handled_manually} needed staff`}
                            color="var(--teal)"
                        />
                        <KpiCard
                            label="Active Now"
                            value={live.active_conversations.toString()}
                            sub={live.active_conversations > 0 ? 'conversations in progress' : 'no active conversations'}
                            color="var(--text)"
                        />
                    </div>
                </>
            ) : (
                <div className="card animate-in" style={{ textAlign: 'center', padding: '44px 32px', marginBottom: 28 }}>
                    <div style={{ fontSize: 28, marginBottom: 14, color: 'var(--text3)' }}>◎</div>
                    <h3 style={{ marginBottom: 8, color: 'var(--text2)', fontWeight: 500 }}>AI concierge is live and listening</h3>
                    <p style={{ fontSize: 13, color: 'var(--text3)' }}>
                        No inquiries yet today. When guests message on WhatsApp or your web widget, their conversations and leads will appear here in real time.
                    </p>
                </div>
            )}

            {/* 30-day summary */}
            {t && (t.total_inquiries > 0 || t.leads_captured > 0) && (
                <div className="card animate-in" style={{ marginBottom: 28 }}>
                    <div className="flex items-center justify-between" style={{ marginBottom: 16 }}>
                        <h3 style={{ fontSize: 12, color: 'var(--text3)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Last 30 Days</h3>
                        <Link href="/dashboard/analytics" className="text-sm text-accent" style={{ textDecoration: 'none' }}>
                            Full analytics →
                        </Link>
                    </div>
                    <div className="grid grid-4" style={{ gap: 20 }}>
                        <div>
                            <div style={{ fontSize: 20, fontWeight: 600, color: 'var(--teal)', letterSpacing: '-0.02em' }}>
                                RM {t.estimated_revenue_recovered.toLocaleString('en-MY', { maximumFractionDigits: 0 })}
                            </div>
                            <div style={{ fontSize: 11, color: 'var(--text3)', marginTop: 3 }}>Revenue Recovered</div>
                        </div>
                        <div>
                            <div style={{ fontSize: 20, fontWeight: 600, color: 'var(--amber)', letterSpacing: '-0.02em' }}>
                                {t.leads_captured}
                            </div>
                            <div style={{ fontSize: 11, color: 'var(--text3)', marginTop: 3 }}>Leads Captured</div>
                        </div>
                        <div>
                            <div style={{ fontSize: 20, fontWeight: 600, color: 'var(--text)', letterSpacing: '-0.02em' }}>
                                {t.total_inquiries}
                            </div>
                            <div style={{ fontSize: 11, color: 'var(--text3)', marginTop: 3 }}>Total Inquiries</div>
                        </div>
                        <div>
                            <div style={{ fontSize: 20, fontWeight: 600, color: 'var(--purple)', letterSpacing: '-0.02em' }}>
                                {t.avg_response_time_sec > 0 ? `${t.avg_response_time_sec.toFixed(1)}s` : '—'}
                            </div>
                            <div style={{ fontSize: 11, color: 'var(--text3)', marginTop: 3 }}>Avg Response</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Quick actions */}
            <div className="grid grid-3" style={{ gap: 14 }}>
                <Link href="/dashboard/conversations" style={{ textDecoration: 'none' }}>
                    <div className="card" style={{
                        padding: '18px 22px',
                        cursor: 'pointer',
                        borderColor: live.handed_off_conversations > 0 ? 'rgba(29,158,117,0.4)' : undefined,
                    }}>
                        <h4 style={{ marginBottom: 6 }}>Conversations</h4>
                        <p className="text-sm" style={{ color: 'var(--text3)' }}>
                            {live.active_conversations > 0
                                ? `${live.active_conversations} active · ${live.handed_off_conversations} need attention`
                                : 'View all guest conversations'}
                        </p>
                    </div>
                </Link>

                <Link href="/dashboard/leads" style={{ textDecoration: 'none' }}>
                    <div className="card" style={{ padding: '18px 22px', cursor: 'pointer' }}>
                        <h4 style={{ marginBottom: 6 }}>Leads</h4>
                        <p className="text-sm" style={{ color: 'var(--text3)' }}>
                            {live.leads_captured > 0
                                ? `${live.leads_captured} captured today — follow up now`
                                : 'Track and convert captured leads'}
                        </p>
                    </div>
                </Link>

                <Link href="/dashboard/analytics" style={{ textDecoration: 'none' }}>
                    <div className="card" style={{ padding: '18px 22px', cursor: 'pointer' }}>
                        <h4 style={{ marginBottom: 6 }}>Analytics</h4>
                        <p className="text-sm" style={{ color: 'var(--text3)' }}>
                            Full 7, 30, 90-day charts and revenue breakdown
                        </p>
                    </div>
                </Link>
            </div>

            {/* Revenue formula transparency */}
            <p style={{ fontSize: 11, color: 'var(--text3)', marginTop: 20, textAlign: 'center' }}>
                Revenue estimated as: leads captured × property ADR × 20% conversion rate.{' '}
                <Link href="/dashboard/analytics" style={{ color: 'var(--teal)', textDecoration: 'none' }}>
                    See full breakdown →
                </Link>
            </p>
        </div>
    );
}
