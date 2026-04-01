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
    icon,
}: {
    label: string;
    value: string;
    sub?: string;
    color: string;
    icon: string;
}) {
    return (
        <div className="stat-card">
            <div className="stat-icon">{icon}</div>
            <div className="stat-label">{label}</div>
            <div className="stat-value" style={{ color }}>{value}</div>
            {sub && <div className="text-xs text-muted" style={{ marginTop: 2 }}>{sub}</div>}
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
                <div className="empty-icon">🏨</div>
                <p>No property configured yet.</p>
                <p className="text-sm text-muted" style={{ marginTop: 8 }}>
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
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                        Today · {today}
                    </p>
                </div>
                {live.handed_off_conversations > 0 && (
                    <Link href="/dashboard/conversations" className="btn btn-primary btn-sm">
                        ⚡ {live.handed_off_conversations} pending handoff{live.handed_off_conversations !== 1 ? 's' : ''}
                    </Link>
                )}
            </div>

            {/* Today's live KPIs — the money slide */}
            {hasActivity ? (
                <>
                    <div className="grid grid-4 animate-in" style={{ marginBottom: 8 }}>
                        <KpiCard
                            label="Revenue Recovered"
                            value={`RM ${live.estimated_revenue_recovered.toLocaleString('en-MY', { maximumFractionDigits: 0 })}`}
                            sub={live.actual_revenue_recovered > 0 ? `RM ${live.actual_revenue_recovered.toLocaleString('en-MY', { maximumFractionDigits: 0 })} confirmed` : 'estimated'}
                            color="var(--success)"
                            icon="💰"
                        />
                        <KpiCard
                            label="Leads Captured"
                            value={live.leads_captured.toString()}
                            sub="from AI conversations"
                            color="var(--warning)"
                            icon="🎯"
                        />
                        <KpiCard
                            label="Inquiries Handled"
                            value={live.total_inquiries.toString()}
                            sub={`${aiPct}% by AI`}
                            color="var(--accent)"
                            icon="💬"
                        />
                        <KpiCard
                            label="After-Hours"
                            value={live.after_hours_inquiries.toString()}
                            sub={live.after_hours_inquiries > 0 ? `${live.after_hours_responded} responded` : 'no overnight inquiries yet'}
                            color="var(--info)"
                            icon="🌙"
                        />
                    </div>

                    <div className="grid grid-4 animate-in" style={{ marginBottom: 32 }}>
                        <KpiCard
                            label="Cost Savings"
                            value={`RM ${live.cost_savings.toLocaleString('en-MY', { maximumFractionDigits: 0 })}`}
                            sub="vs. manual handling"
                            color="var(--info)"
                            icon="📉"
                        />
                        <KpiCard
                            label="Avg Response"
                            value={live.avg_response_time_sec > 0 ? `${live.avg_response_time_sec.toFixed(1)}s` : '—'}
                            sub="end-to-end"
                            color="var(--success)"
                            icon="⚡"
                        />
                        <KpiCard
                            label="AI Handled"
                            value={live.inquiries_handled_by_ai.toString()}
                            sub={`${live.inquiries_handled_manually} needed staff`}
                            color="var(--success)"
                            icon="🤖"
                        />
                        <KpiCard
                            label="Active Now"
                            value={live.active_conversations.toString()}
                            sub={live.active_conversations > 0 ? 'conversations in progress' : 'no active conversations'}
                            color="var(--accent)"
                            icon="🔴"
                        />
                    </div>
                </>
            ) : (
                <div className="card animate-in" style={{ textAlign: 'center', padding: '48px 32px', marginBottom: 32, borderColor: 'rgba(99,102,241,0.15)' }}>
                    <div style={{ fontSize: 48, marginBottom: 16 }}>📡</div>
                    <h3 style={{ marginBottom: 8 }}>AI concierge is live and listening</h3>
                    <p className="text-muted text-sm">
                        No inquiries yet today. When guests message on WhatsApp or your web widget, their conversations and leads will appear here in real time.
                    </p>
                </div>
            )}

            {/* 30-day summary */}
            {t && (t.total_inquiries > 0 || t.leads_captured > 0) && (
                <div className="card animate-in" style={{ marginBottom: 32 }}>
                    <div className="flex items-center justify-between" style={{ marginBottom: 16 }}>
                        <h3 style={{ fontSize: 14, color: 'var(--text-muted)' }}>Last 30 Days</h3>
                        <Link href="/dashboard/analytics" className="text-sm text-accent" style={{ textDecoration: 'none' }}>
                            Full Analytics →
                        </Link>
                    </div>
                    <div className="grid grid-4" style={{ gap: 24 }}>
                        <div>
                            <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--success)' }}>
                                RM {t.estimated_revenue_recovered.toLocaleString('en-MY', { maximumFractionDigits: 0 })}
                            </div>
                            <div className="text-xs text-muted" style={{ marginTop: 2 }}>Revenue Recovered</div>
                        </div>
                        <div>
                            <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--warning)' }}>
                                {t.leads_captured}
                            </div>
                            <div className="text-xs text-muted" style={{ marginTop: 2 }}>Leads Captured</div>
                        </div>
                        <div>
                            <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--accent)' }}>
                                {t.total_inquiries}
                            </div>
                            <div className="text-xs text-muted" style={{ marginTop: 2 }}>Total Inquiries</div>
                        </div>
                        <div>
                            <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--info)' }}>
                                {t.avg_response_time_sec > 0 ? `${t.avg_response_time_sec.toFixed(1)}s` : '—'}
                            </div>
                            <div className="text-xs text-muted" style={{ marginTop: 2 }}>Avg Response</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Quick actions */}
            <div className="grid grid-3" style={{ gap: 16 }}>
                <Link href="/dashboard/conversations" style={{ textDecoration: 'none' }}>
                    <div className="card" style={{ padding: '20px 24px', cursor: 'pointer', transition: 'border-color 0.2s', borderColor: live.handed_off_conversations > 0 ? 'var(--accent)' : undefined }}>
                        <div style={{ fontSize: 24, marginBottom: 8 }}>💬</div>
                        <h4>Conversations</h4>
                        <p className="text-sm text-muted" style={{ marginTop: 4 }}>
                            {live.active_conversations > 0
                                ? `${live.active_conversations} active · ${live.handed_off_conversations} need attention`
                                : 'View all guest conversations'}
                        </p>
                    </div>
                </Link>

                <Link href="/dashboard/leads" style={{ textDecoration: 'none' }}>
                    <div className="card" style={{ padding: '20px 24px', cursor: 'pointer' }}>
                        <div style={{ fontSize: 24, marginBottom: 8 }}>🎯</div>
                        <h4>Leads</h4>
                        <p className="text-sm text-muted" style={{ marginTop: 4 }}>
                            {live.leads_captured > 0
                                ? `${live.leads_captured} captured today — follow up now`
                                : 'Track and convert captured leads'}
                        </p>
                    </div>
                </Link>

                <Link href="/dashboard/analytics" style={{ textDecoration: 'none' }}>
                    <div className="card" style={{ padding: '20px 24px', cursor: 'pointer' }}>
                        <div style={{ fontSize: 24, marginBottom: 8 }}>📊</div>
                        <h4>Analytics</h4>
                        <p className="text-sm text-muted" style={{ marginTop: 4 }}>
                            Full 7, 30, 90-day charts and revenue breakdown
                        </p>
                    </div>
                </Link>
            </div>

            {/* Revenue formula transparency */}
            <p className="text-xs text-muted" style={{ marginTop: 24, textAlign: 'center' }}>
                Revenue estimated as: leads captured × property ADR × 20% conversion rate.{' '}
                <Link href="/dashboard/analytics" className="text-accent" style={{ textDecoration: 'none' }}>
                    See full breakdown →
                </Link>
            </p>
        </div>
    );
}
