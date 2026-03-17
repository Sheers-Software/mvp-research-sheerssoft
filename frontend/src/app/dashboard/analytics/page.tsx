'use client';

import { useEffect, useState } from 'react';
import { apiGet } from '@/lib/api';

interface DailyData {
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

interface AnalyticsData {
    property_id: string;
    period: { from: string; to: string };
    totals: {
        total_inquiries: number;
        after_hours_inquiries: number;
        after_hours_responded: number;
        leads_captured: number;
        handoffs: number;
        inquiries_handled_by_ai: number;
        inquiries_handled_manually: number;
        avg_response_time_sec: number;
        estimated_revenue_recovered: number;
        cost_savings: number;
    };
    daily: DailyData[];
}

const ranges = [
    { label: '7 Days', days: 7 },
    { label: '30 Days', days: 30 },
    { label: '90 Days', days: 90 },
];

function BarChart({ data, dataKey, color, label }: { data: DailyData[]; dataKey: keyof DailyData; color: string; label: string }) {
    const values = data.map((d) => Number(d[dataKey]) || 0);
    const max = Math.max(...values, 1);

    return (
        <div className="card" style={{ padding: '16px 20px' }}>
            <h4 style={{ fontSize: 13, marginBottom: 12, color: 'var(--text-muted)' }}>{label}</h4>
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 2, height: 120 }}>
                {data.map((d, i) => {
                    const val = Number(d[dataKey]) || 0;
                    const height = max > 0 ? (val / max) * 100 : 0;
                    return (
                        <div
                            key={i}
                            title={`${d.date}: ${val}`}
                            style={{
                                flex: 1,
                                height: `${Math.max(height, 2)}%`,
                                background: `linear-gradient(to top, ${color}, ${color}88)`,
                                borderRadius: '4px 4px 0 0',
                                minWidth: 4,
                                transition: 'height 0.5s ease',
                                cursor: 'pointer',
                            }}
                        />
                    );
                })}
            </div>
            <div className="flex items-center justify-between" style={{ marginTop: 8 }}>
                <span className="text-sm text-muted">{data[0]?.date?.slice(5) || ''}</span>
                <span className="text-sm text-muted">{data[data.length - 1]?.date?.slice(5) || ''}</span>
            </div>
        </div>
    );
}

export default function AnalyticsPage() {
    const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [rangeDays, setRangeDays] = useState(30);
    const [propertyId, setPropertyId] = useState<string | null>(null);

    useEffect(() => {
        apiGet<any>('/analytics/dashboard')
            .then((data) => {
                if (data?.property_id) setPropertyId(data.property_id);
            })
            .catch(() => { });
    }, []);

    useEffect(() => {
        if (!propertyId) return;
        setLoading(true);
        const to = new Date().toISOString().split('T')[0];
        const from = new Date(Date.now() - rangeDays * 86400000).toISOString().split('T')[0];
        apiGet<AnalyticsData>(`/properties/${propertyId}/analytics?from_date=${from}&to_date=${to}`)
            .then(setAnalytics)
            .catch(() => { })
            .finally(() => setLoading(false));
    }, [propertyId, rangeDays]);

    const t = analytics?.totals;

    const kpiCards = [
        { label: 'Revenue Recovered', value: t ? `RM ${t.estimated_revenue_recovered.toLocaleString()}` : '—', icon: '💰', color: 'var(--success)' },
        { label: 'Cost Savings', value: t ? `RM ${t.cost_savings.toLocaleString()}` : '—', icon: '📉', color: 'var(--info)' },
        { label: 'Total Inquiries', value: t ? t.total_inquiries.toLocaleString() : '—', icon: '💬', color: 'var(--accent)' },
        { label: 'Leads Captured', value: t ? t.leads_captured.toLocaleString() : '—', icon: '🎯', color: 'var(--warning)' },
        { label: 'AI Handled', value: t ? t.inquiries_handled_by_ai.toLocaleString() : '—', icon: '🤖', color: 'var(--success)' },
        { label: 'Handoffs', value: t ? t.handoffs.toLocaleString() : '—', icon: '🔄', color: 'var(--danger)' },
        { label: 'After Hours', value: t ? t.after_hours_inquiries.toLocaleString() : '—', icon: '🌙', color: 'var(--warning)' },
        { label: 'Avg Response', value: t ? `${t.avg_response_time_sec.toFixed(1)}s` : '—', icon: '⚡', color: 'var(--info)' },
    ];

    return (
        <div>
            <div className="flex items-center justify-between" style={{ marginBottom: 32 }}>
                <div>
                    <h1>Analytics</h1>
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                        Performance metrics and revenue intelligence
                    </p>
                </div>
                <div className="flex gap-sm">
                    {ranges.map((r) => (
                        <button
                            key={r.days}
                            className={`btn btn-sm ${rangeDays === r.days ? 'btn-primary' : 'btn-ghost'}`}
                            onClick={() => setRangeDays(r.days)}
                        >
                            {r.label}
                        </button>
                    ))}
                </div>
            </div>

            {loading ? (
                <div className="flex justify-center" style={{ padding: 60 }}><div className="loader" /></div>
            ) : !analytics ? (
                <div className="empty-state">
                    <div className="empty-icon">📊</div>
                    <p>No analytics data available</p>
                    <p className="text-sm text-muted" style={{ marginTop: 8 }}>
                        Analytics are generated daily as conversations flow through the system.
                    </p>
                </div>
            ) : (
                <>
                    {/* KPI Grid */}
                    <div className="grid grid-4 animate-in" style={{ marginBottom: 24 }}>
                        {kpiCards.map((card, i) => (
                            <div
                                key={card.label}
                                className="stat-card animate-slide-up"
                                style={{ animationDelay: `${i * 50}ms`, animationFillMode: 'backwards' }}
                            >
                                <div className="stat-icon">{card.icon}</div>
                                <div className="stat-label">{card.label}</div>
                                <div className="stat-value" style={{ color: card.color }}>{card.value}</div>
                            </div>
                        ))}
                    </div>

                    {/* Charts */}
                    {analytics.daily.length > 0 && (
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                            <BarChart data={analytics.daily} dataKey="total_inquiries" color="hsl(245, 60%, 60%)" label="Daily Inquiries" />
                            <BarChart data={analytics.daily} dataKey="leads_captured" color="hsl(40, 90%, 50%)" label="Leads Captured" />
                            <BarChart data={analytics.daily} dataKey="estimated_revenue_recovered" color="hsl(145, 60%, 45%)" label="Revenue Recovered (RM)" />
                            <BarChart data={analytics.daily} dataKey="cost_savings" color="hsl(200, 70%, 50%)" label="Cost Savings (RM)" />
                        </div>
                    )}

                    {/* Period Info */}
                    <div className="text-sm text-muted" style={{ marginTop: 16, textAlign: 'center' }}>
                        Showing data from {analytics.period.from} to {analytics.period.to}
                    </div>
                </>
            )}
        </div>
    );
}
