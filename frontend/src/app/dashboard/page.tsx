'use client';

import { useEffect, useState } from 'react';
import { apiGet } from '@/lib/api';

export interface Property {
    id: string;
    name: string;
    adr: number;
    ota_commission_pct: number;
}
export interface AnalyticsSummary {
    total_inquiries: number;
    after_hours_inquiries: number;
    after_hours_responded: number;
    leads_captured: number;
    handoffs: number;
    inquiries_handled_by_ai: number;
    estimated_revenue_recovered: number;
    cost_savings: number;
    avg_response_time_sec: number;
    channel_breakdown: Record<string, number>;
}
export interface Conversation {
    id: string;
    channel: string;
    guest_name: string;
    guest_identifier: string;
    started_at: string;
    message_count: number;
    status: string;
}

import { VolumeChart, ChannelChart } from '@/components/DashboardCharts';
import html2pdf from 'html2pdf.js';

export default function DashboardPage() {
    const [stats, setStats] = useState<AnalyticsSummary | null>(null);
    const [daily, setDaily] = useState<any[]>([]);
    const [recentConvos, setRecentConvos] = useState<Conversation[]>([]);
    const [property, setProperty] = useState<Property | null>(null);
    const [loading, setLoading] = useState(true);

    const [dateFilter, setDateFilter] = useState<'today' | '7d' | '30d' | '90d' | 'year' | 'custom'>('30d');
    const [customRange, setCustomRange] = useState({ from: '', to: '' });

    useEffect(() => {
        loadDashboard();
    }, [dateFilter, customRange]);

    async function loadDashboard() {
        setLoading(true);
        try {
            const props = await apiGet<Property[]>('/properties');
            if (props.length > 0) {
                setProperty(props[0]);

                let from = '';
                let to = new Date().toISOString().split('T')[0];
                const d = new Date();

                if (dateFilter === 'today') {
                    from = to;
                } else if (dateFilter === '7d') {
                    d.setDate(d.getDate() - 7);
                    from = d.toISOString().split('T')[0];
                } else if (dateFilter === '30d') {
                    d.setDate(d.getDate() - 30);
                    from = d.toISOString().split('T')[0];
                } else if (dateFilter === '90d') {
                    d.setDate(d.getDate() - 90);
                    from = d.toISOString().split('T')[0];
                } else if (dateFilter === 'year') {
                    d.setDate(d.getDate() - 365);
                    from = d.toISOString().split('T')[0];
                } else if (dateFilter === 'custom') {
                    from = customRange.from;
                    to = customRange.to;
                    if (!from || !to) return; // Don't fetch until range is valid
                }

                const summary = await apiGet<AnalyticsSummary>(`/properties/${props[0].id}/analytics/summary?from_date=${from}&to_date=${to}`);
                setStats(summary);

                const range = await apiGet<any>(`/properties/${props[0].id}/analytics?from_date=${from}&to_date=${to}`);
                setDaily(range?.daily || []);

                // Fetch recent conversations for live feed
                const convos = await apiGet<Conversation[]>(`/properties/${props[0].id}/conversations`);
                setRecentConvos(convos.slice(0, 5));
            }
        } catch (err) {
            console.error('Failed to load dashboard:', err);
        } finally {
            setLoading(false);
        }
    }

    const today = new Date().toLocaleDateString('en-MY', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric',
    });

    if (loading) {
        return (
            <div>
                <div className="page-header">
                    <div className="skeleton" style={{ width: 300, height: 32, marginBottom: 8 }} />
                    <div className="skeleton" style={{ width: 200, height: 20 }} />
                </div>
                <div className="stat-grid">
                    {[1, 2, 3, 4].map(i => (
                        <div key={i} className="skeleton" style={{ height: 140, borderRadius: 'var(--radius-lg)' }} />
                    ))}
                </div>
            </div>
        );
    }

    const afterHoursRate = stats && stats.after_hours_inquiries > 0
        ? Math.round((stats.after_hours_responded / stats.after_hours_inquiries) * 100)
        : 0;

    const leadCaptureRate = stats && stats.total_inquiries > 0
        ? Math.round((stats.leads_captured / stats.total_inquiries) * 100)
        : 0;

    const aiHandledRate = stats && stats.total_inquiries > 0
        ? Math.round((stats.inquiries_handled_by_ai / stats.total_inquiries) * 100)
        : 0;

    // Prepare chart data
    const chartData = {
        labels: daily.map(d => new Date(d.date).toLocaleDateString('en-MY', { month: 'short', day: 'numeric' })),
        inquiries: daily.map(d => d.total_inquiries),
        leads: daily.map(d => d.leads_captured)
    };

    function formatTime(iso: string) {
        return new Date(iso).toLocaleTimeString('en-MY', { hour: '2-digit', minute: '2-digit' });
    }

    // ─── Export Features ───

    const handleExportCSV = () => {
        if (!daily || daily.length === 0) return;

        const headers = ['Date', 'Inquiries', 'Leads Captured', 'AI Handled', 'Handoffs', 'After Hours', 'Estimated Rev', 'Ops Savings'];
        const csvContent = [
            headers.join(','),
            ...daily.map(d => [
                d.date,
                d.total_inquiries,
                d.leads_captured,
                d.inquiries_handled_by_ai,
                d.handoffs,
                d.after_hours_inquiries,
                d.estimated_revenue_recovered,
                d.cost_savings
            ].join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `nocturn-analytics_${dateFilter}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleExportPDF = () => {
        const element = document.getElementById('dashboard-content');
        if (!element) return;

        const opt: any = {
            margin: 0.5,
            filename: `nocturn-dashboard_${dateFilter}.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, useCORS: true },
            jsPDF: { unit: 'in', format: 'a4', orientation: 'landscape' }
        };
        html2pdf().from(element).set(opt).save();
    };

    return (
        <div className="animate-in" id="dashboard-content">
            <div className="page-header flex justify-between items-end flex-wrap gap-4">
                <div>
                    <h1 className="page-title">{property?.name || 'Dashboard'}</h1>
                    <p className="page-subtitle">{today} &middot; Analytics Overview</p>
                </div>

                {/* Date Filter & Export Controls */}
                <div className="flex flex-col items-end gap-2" data-html2canvas-ignore="true">
                    <div className="flex gap-2">
                        <button onClick={handleExportCSV} className="btn btn-secondary btn-sm flex items-center gap-1" title="Export tabular data to CSV" disabled={daily.length === 0}>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                            CSV
                        </button>
                        <button onClick={handleExportPDF} className="btn btn-secondary btn-sm flex items-center gap-1" title="Export graphical report to PDF">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                            PDF
                        </button>
                    </div>

                    <div className="flex gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200">
                        <button className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${dateFilter === 'today' ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500 hover:text-slate-700'}`} onClick={() => setDateFilter('today')}>Today</button>
                        <button className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${dateFilter === '7d' ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500 hover:text-slate-700'}`} onClick={() => setDateFilter('7d')}>7 Days</button>
                        <button className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${dateFilter === '30d' ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500 hover:text-slate-700'}`} onClick={() => setDateFilter('30d')}>30 Days</button>
                        <button className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${dateFilter === '90d' ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500 hover:text-slate-700'}`} onClick={() => setDateFilter('90d')}>Quarter</button>
                        <button className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${dateFilter === 'year' ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500 hover:text-slate-700'}`} onClick={() => setDateFilter('year')}>Year</button>
                        <button className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${dateFilter === 'custom' ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500 hover:text-slate-700'}`} onClick={() => setDateFilter('custom')}>Custom</button>
                    </div>

                    {dateFilter === 'custom' && (
                        <div className="flex gap-2 items-center text-sm animate-in fade-in slide-in-from-top-1">
                            <input type="date" className="input py-1 px-2 h-8 text-xs" value={customRange.from} onChange={e => setCustomRange({ ...customRange, from: e.target.value })} />
                            <span className="text-slate-400">to</span>
                            <input type="date" className="input py-1 px-2 h-8 text-xs" value={customRange.to} onChange={e => setCustomRange({ ...customRange, to: e.target.value })} />
                        </div>
                    )}
                </div>
            </div>

            {/* ─── The Money Slide ─── */}
            <div className="stat-grid" style={{ marginBottom: 32 }}>
                <div className="stat-card">
                    <div className="stat-value">{stats?.total_inquiries ?? 0}</div>
                    <div className="stat-label">Inquiries Handled</div>
                </div>

                <div className="stat-card">
                    <div className="stat-value">{stats?.after_hours_responded ?? 0}</div>
                    <div className="stat-label">After-Hours Recovered</div>
                </div>

                <div className="stat-card">
                    <div className="stat-value">{stats?.leads_captured ?? 0}</div>
                    <div className="stat-label">Leads Captured</div>
                </div>

                <div className="stat-card">
                    <div className="stat-value gold">
                        RM {(stats?.estimated_revenue_recovered ?? 0).toLocaleString()}
                    </div>
                    <div className="stat-label">Revenue Recovered</div>
                </div>

                <div className="stat-card">
                    <div className="stat-value gold" style={{ color: 'var(--success)' }}>
                        RM {(stats?.cost_savings ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </div>
                    <div className="stat-label">Ops Cost Savings</div>
                </div>
            </div>

            {/* ─── Secondary Stats ─── */}
            <div className="card" style={{ marginBottom: 24 }}>
                <div className="flex justify-between items-center" style={{ flexWrap: 'wrap', gap: 24 }}>
                    <div>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Avg Response Time</span>
                        <div style={{ fontSize: '1.3rem', fontWeight: 600 }}>
                            {(stats?.avg_response_time_sec ?? 0).toFixed(0)}s
                        </div>
                    </div>

                    <div>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Handoff Rate</span>
                        <div style={{ fontSize: '1.3rem', fontWeight: 600 }}>
                            {stats && stats.total_inquiries > 0
                                ? Math.round((stats.handoffs / stats.total_inquiries) * 100)
                                : 0}%
                        </div>
                    </div>

                    <div>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>AI Handled</span>
                        <div style={{ fontSize: '1.3rem', fontWeight: 600 }}>
                            {aiHandledRate}%
                            <div style={{
                                marginTop: 6, height: 6, borderRadius: 3, background: 'var(--bg-input)',
                                width: 120, overflow: 'hidden'
                            }}>
                                <div style={{
                                    height: '100%', borderRadius: 3, width: `${aiHandledRate}%`,
                                    background: 'linear-gradient(90deg, var(--accent), var(--accent-hover))'
                                }} />
                            </div>
                        </div>
                    </div>

                    <div>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>After-Hours Recovery</span>
                        <div style={{ fontSize: '1.3rem', fontWeight: 600 }}>{afterHoursRate}%</div>
                    </div>

                    <div>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Lead Capture Rate</span>
                        <div style={{ fontSize: '1.3rem', fontWeight: 600 }}>{leadCaptureRate}%</div>
                    </div>
                </div>
            </div>

            {/* ─── Charts & Live Feed Row ─── */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6" style={{ marginBottom: 24 }}>
                <div className="xl:col-span-2 flex flex-col gap-6">
                    <div className="card">
                        <h3 style={{ fontFamily: 'var(--font-display)', marginBottom: 16, fontSize: '1.1rem' }}>
                            Conversation Trend (30 Days)
                        </h3>
                        <div style={{ height: 300 }}>
                            {daily.length > 0 ? (
                                <VolumeChart data={chartData} />
                            ) : (
                                <div className="flex h-full items-center justify-center text-sm" style={{ color: 'var(--text-muted)' }}>
                                    No trend data available
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="card">
                        <h3 style={{ fontFamily: 'var(--font-display)', marginBottom: 16, fontSize: '1.1rem' }}>
                            Channel Breakdown
                        </h3>
                        <div style={{ height: 300 }}>
                            {stats?.channel_breakdown && Object.keys(stats.channel_breakdown).length > 0 ? (
                                <ChannelChart data={stats.channel_breakdown} />
                            ) : (
                                <div className="flex h-full items-center justify-center text-sm" style={{ color: 'var(--text-muted)' }}>
                                    No channel data available
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Live Conversation Feed */}
                <div className="card flex flex-col h-full bg-slate-50 border-slate-200 shadow-inner">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                            Live Conversation Feed
                        </h3>
                        <a href="/dashboard/conversations" className="text-sm text-blue-600 hover:underline">View All</a>
                    </div>

                    <div className="flex flex-col gap-3">
                        {recentConvos.map(conv => (
                            <a
                                key={conv.id}
                                href={`/dashboard/conversations/${conv.id}`}
                                className="bg-white border text-sm border-slate-200 rounded-lg p-3 hover:border-blue-300 transition-colors shadow-sm flex flex-col gap-2"
                            >
                                <div className="flex justify-between items-start">
                                    <div className="flex items-center gap-2">
                                        <span className={`badge badge-channel-${conv.channel} text-xs py-0.5 px-1.5 min-w-0`}>
                                            {conv.channel === 'whatsapp' ? '💬 WA' : conv.channel === 'web' ? '🌐 Web' : '📧 Email'}
                                        </span>
                                        <span className="font-semibold text-slate-700 truncate max-w-[120px]">
                                            {conv.guest_name || conv.guest_identifier || 'Guest'}
                                        </span>
                                    </div>
                                    <span className="text-xs text-slate-400 whitespace-nowrap">{formatTime(conv.started_at)}</span>
                                </div>
                                <div className="flex justify-between items-center mt-1">
                                    <span className="text-xs text-slate-500">{conv.message_count} msgs</span>
                                    <span className={`badge badge-${conv.status === 'handed_off' ? 'handoff' : conv.status} text-xs bg-opacity-70 py-0 px-1.5`}>
                                        {conv.status.replace('_', ' ')}
                                    </span>
                                </div>
                            </a>
                        ))}
                        {recentConvos.length === 0 && (
                            <div className="text-center py-8 text-sm text-slate-400">
                                No active conversations
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* ROI Explanation Footer */}
            <div className="card bg-slate-50 border border-slate-100 p-4">
                <h4 className="font-semibold text-sm mb-2 text-slate-700">How is ROI calculated?</h4>
                <p className="text-sm text-slate-500">
                    Revenue recovered is estimated dynamically based on captured booking leads using an ADR of RM {(property?.adr || 230).toLocaleString()} and an average length of stay contextually extracted by the AI. Savings also factor in OTA commission reduction at {property?.ota_commission_pct || 20}%.
                </p>
            </div>
        </div>
    );
}
