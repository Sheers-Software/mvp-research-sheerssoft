'use client';

import { useEffect, useState } from 'react';
import { apiGet, apiPost } from '@/lib/api';

interface Lead {
    id: string;
    conversation_id: string;
    guest_name: string | null;
    guest_phone: string | null;
    guest_email: string | null;
    intent: string | null;
    status: string;
    estimated_value: number | null;
    actual_revenue: number | null;
    priority: string | null;
    flag_reason: string | null;
    captured_at: string;
}

const statusBadge: Record<string, string> = {
    new: 'badge-info',
    contacted: 'badge-warning',
    qualified: 'badge-success',
    converted: 'badge-success',
    lost: 'badge-danger',
};

const intentBadge: Record<string, string> = {
    booking: 'badge-success',
    inquiry: 'badge-info',
    complaint: 'badge-danger',
    group_booking: 'badge-warning',
    event: 'badge-warning',
};

export default function LeadsPage() {
    const [leads, setLeads] = useState<Lead[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('');
    const [propertyId, setPropertyId] = useState<string | null>(null);
    const [convertingId, setConvertingId] = useState<string | null>(null);
    const [revenue, setRevenue] = useState('');

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
        const params = filter ? `?status=${filter}` : '';
        apiGet<Lead[]>(`/properties/${propertyId}/leads${params}`)
            .then(setLeads)
            .catch(() => { })
            .finally(() => setLoading(false));
    }, [propertyId, filter]);

    const exportCSV = () => {
        if (!propertyId) return;
        const token = localStorage.getItem('nocturn_token');
        const params = filter ? `?status=${filter}` : '';
        window.open(
            `/api/v1/properties/${propertyId}/leads/export${params}${params ? '&' : '?'}token=${token}`,
            '_blank'
        );
    };

    const convertLead = async (id: string) => {
        if (!revenue) return;
        try {
            await apiPost(`/leads/${id}/convert`, { actual_revenue: parseFloat(revenue) });
            setLeads((prev) => prev.map((l) => l.id === id ? { ...l, status: 'converted', actual_revenue: parseFloat(revenue) } : l));
            setConvertingId(null);
            setRevenue('');
        } catch { }
    };

    // Summary stats
    const totalLeads = leads.length;
    const totalValue = leads.reduce((sum, l) => sum + (l.estimated_value || 0), 0);
    const convertedCount = leads.filter((l) => l.status === 'converted').length;
    const actualRevenue = leads.reduce((sum, l) => sum + (l.actual_revenue || 0), 0);

    return (
        <div>
            <div className="flex items-center justify-between" style={{ marginBottom: 32 }}>
                <div>
                    <h1>Leads</h1>
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                        Guest contacts captured by AI — ready for follow-up
                    </p>
                </div>
                <div className="flex gap-sm">
                    <button className="btn btn-sm btn-secondary" onClick={exportCSV}>
                        📥 Export CSV
                    </button>
                </div>
            </div>

            {/* KPI Mini Cards */}
            <div className="grid grid-4 animate-in" style={{ marginBottom: 24 }}>
                <div className="stat-card">
                    <div className="stat-icon">🎯</div>
                    <div className="stat-label">Total Leads</div>
                    <div className="stat-value" style={{ color: 'var(--accent)' }}>{totalLeads}</div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">💰</div>
                    <div className="stat-label">Est. Pipeline</div>
                    <div className="stat-value" style={{ color: 'var(--warning)' }}>RM {totalValue.toLocaleString()}</div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">✅</div>
                    <div className="stat-label">Converted</div>
                    <div className="stat-value" style={{ color: 'var(--success)' }}>{convertedCount}</div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">📈</div>
                    <div className="stat-label">Actual Revenue</div>
                    <div className="stat-value" style={{ color: 'var(--success)' }}>RM {actualRevenue.toLocaleString()}</div>
                </div>
            </div>

            {/* Filters */}
            <div className="flex gap-sm" style={{ marginBottom: 16 }}>
                {['', 'new', 'contacted', 'qualified', 'converted', 'lost'].map((f) => (
                    <button
                        key={f}
                        className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-ghost'}`}
                        onClick={() => { setFilter(f); }}
                    >
                        {f === '' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}
                    </button>
                ))}
            </div>

            {loading ? (
                <div className="flex justify-center" style={{ padding: 60 }}><div className="loader" /></div>
            ) : leads.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">🎯</div>
                    <p>No {filter || ''} leads yet</p>
                    <p className="text-sm text-muted" style={{ marginTop: 8 }}>
                        Leads are captured automatically when guests share contact details during conversations.
                    </p>
                </div>
            ) : (
                <div className="grid grid-3 animate-in">
                    {leads.map((l, i) => {
                        // Highlight leads captured $>24h$ ago that aren't converted/lost
                        const isStale = ['new', 'contacted', 'qualified'].includes(l.status) && (Date.now() - new Date(l.captured_at).getTime() > 24 * 60 * 60 * 1000);
                        return (
                            <div
                                key={l.id}
                                className="card animate-slide-up"
                                style={{ animationDelay: `${i * 30}ms`, animationFillMode: 'backwards', position: 'relative', overflow: 'hidden' }}
                            >
                                {isStale && (
                                    <div style={{ position: 'absolute', top: 0, left: 0, right: 0, background: 'var(--warning-bg)', color: 'var(--warning)', padding: '4px 12px', fontSize: 11, fontWeight: 600, textAlign: 'center', borderBottom: '1px solid rgba(251, 191, 36, 0.2)' }}>
                                        ⚠️ Needs Follow-up
                                    </div>
                                )}
                                <div style={{ paddingTop: isStale ? 24 : 0 }}>
                                    <div className="flex items-center justify-between" style={{ marginBottom: 12 }}>
                                        <h3 style={{ fontSize: 16, margin: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                            {l.guest_name || 'Anonymous Guest'}
                                        </h3>
                                        <span className={`badge ${statusBadge[l.status] || 'badge-neutral'}`} style={{ flexShrink: 0 }}>
                                            {l.status}
                                        </span>
                                    </div>
                                    
                                    <div className="text-sm text-muted" style={{ marginBottom: 16, minHeight: 40 }}>
                                        {l.guest_email && <div>📧 {l.guest_email}</div>}
                                        {l.guest_phone && <div>📱 {l.guest_phone}</div>}
                                        {!l.guest_email && !l.guest_phone && <div>No contact info</div>}
                                    </div>

                                    <div className="flex items-center gap-sm" style={{ marginBottom: 16 }}>
                                        {l.intent && <span className={`badge ${intentBadge[l.intent] || 'badge-neutral'}`}>{l.intent}</span>}
                                        {l.priority && <span className={`badge ${l.priority === 'high' ? 'badge-danger' : l.priority === 'medium' ? 'badge-warning' : 'badge-neutral'}`}>{l.priority}</span>}
                                    </div>

                                    <div style={{ padding: '12px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', marginBottom: 16 }}>
                                        <div className="text-sm text-muted">Estimated Pipeline Value</div>
                                        <div style={{ fontSize: 18, fontWeight: 600, color: 'var(--text-primary)' }}>
                                            {l.estimated_value ? `RM ${l.estimated_value.toLocaleString()}` : '—'}
                                        </div>
                                    </div>

                                    <div className="flex flex-col gap-sm">
                                        {l.status !== 'converted' && l.status !== 'lost' && (
                                            <>
                                                {convertingId === l.id ? (
                                                    <div className="flex gap-sm items-center">
                                                        <input
                                                            type="number"
                                                            className="input"
                                                            placeholder="Revenue (RM)"
                                                            value={revenue}
                                                            onChange={(e) => setRevenue(e.target.value)}
                                                            style={{ flex: 1, fontSize: 13 }}
                                                        />
                                                        <button className="btn btn-sm btn-primary" onClick={() => convertLead(l.id)}>✓</button>
                                                        <button className="btn btn-sm btn-ghost" onClick={() => setConvertingId(null)}>✕</button>
                                                    </div>
                                                ) : (
                                                    <div className="flex gap-sm w-full">
                                                        <button className="btn btn-sm btn-primary w-full" onClick={() => setConvertingId(l.id)}>
                                                            Convert to Booking
                                                        </button>
                                                        <button className="btn btn-sm btn-secondary w-full" onClick={() => window.location.href=`/dashboard/conversations`}>
                                                            Message
                                                        </button>
                                                    </div>
                                                )}
                                            </>
                                        )}
                                        {l.status === 'converted' && l.actual_revenue && (
                                            <div className="text-center" style={{ color: 'var(--success)', fontWeight: 500, padding: '8px 0', background: 'var(--success-bg)', borderRadius: 'var(--radius-sm)' }}>
                                                🎉 Won: RM {l.actual_revenue.toLocaleString()}
                                            </div>
                                        )}
                                        {l.status === 'lost' && (
                                            <div className="text-center" style={{ color: 'var(--danger)', fontWeight: 500, padding: '8px 0', background: 'var(--danger-bg)', borderRadius: 'var(--radius-sm)' }}>
                                                ❌ Lost Request
                                            </div>
                                        )}
                                    </div>
                                    <div className="text-muted text-center" style={{ fontSize: 11, marginTop: 12 }}>
                                        Captured {new Date(l.captured_at).toLocaleDateString()}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
