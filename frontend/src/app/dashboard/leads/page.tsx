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
                <div className="table-container animate-in">
                    <table>
                        <thead>
                            <tr>
                                <th>Guest</th>
                                <th>Contact</th>
                                <th>Intent</th>
                                <th>Est. Value</th>
                                <th>Status</th>
                                <th>Priority</th>
                                <th>Captured</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {leads.map((l, i) => (
                                <tr
                                    key={l.id}
                                    className="animate-slide-up"
                                    style={{ animationDelay: `${i * 30}ms`, animationFillMode: 'backwards' }}
                                >
                                    <td><strong>{l.guest_name || '—'}</strong></td>
                                    <td>
                                        {l.guest_email && <div className="text-sm">{l.guest_email}</div>}
                                        {l.guest_phone && <div className="text-sm text-muted">{l.guest_phone}</div>}
                                        {!l.guest_email && !l.guest_phone && <span className="text-muted">—</span>}
                                    </td>
                                    <td>
                                        {l.intent ? (
                                            <span className={`badge ${intentBadge[l.intent] || 'badge-neutral'}`}>{l.intent}</span>
                                        ) : '—'}
                                    </td>
                                    <td>
                                        {l.estimated_value ? (
                                            <span style={{ fontWeight: 600 }}>RM {l.estimated_value.toLocaleString()}</span>
                                        ) : '—'}
                                    </td>
                                    <td>
                                        <span className={`badge ${statusBadge[l.status] || 'badge-neutral'}`}>{l.status}</span>
                                    </td>
                                    <td>
                                        {l.priority ? (
                                            <span className={`badge ${l.priority === 'high' ? 'badge-danger' : l.priority === 'medium' ? 'badge-warning' : 'badge-neutral'}`}>
                                                {l.priority}
                                            </span>
                                        ) : '—'}
                                    </td>
                                    <td className="text-sm text-muted">
                                        {new Date(l.captured_at).toLocaleDateString()}
                                    </td>
                                    <td>
                                        {l.status !== 'converted' && (
                                            <>
                                                {convertingId === l.id ? (
                                                    <div className="flex gap-sm items-center">
                                                        <input
                                                            type="number"
                                                            className="input"
                                                            placeholder="Revenue (RM)"
                                                            value={revenue}
                                                            onChange={(e) => setRevenue(e.target.value)}
                                                            style={{ width: 120, fontSize: 12 }}
                                                        />
                                                        <button className="btn btn-sm btn-primary" onClick={() => convertLead(l.id)}>✓</button>
                                                        <button className="btn btn-sm btn-ghost" onClick={() => setConvertingId(null)}>✕</button>
                                                    </div>
                                                ) : (
                                                    <button className="btn btn-sm btn-secondary" onClick={() => setConvertingId(l.id)}>
                                                        Convert
                                                    </button>
                                                )}
                                            </>
                                        )}
                                        {l.status === 'converted' && l.actual_revenue && (
                                            <span className="text-sm" style={{ color: 'var(--success)' }}>
                                                RM {l.actual_revenue.toLocaleString()}
                                            </span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
