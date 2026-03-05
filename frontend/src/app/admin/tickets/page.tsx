'use client';

import { useEffect, useState } from 'react';
import { apiGet, apiPatch } from '@/lib/api';

interface Ticket {
    id: string;
    tenant_id: string;
    tenant_name: string | null;
    subject: string;
    description: string;
    status: string;
    priority: string;
    created_by_name: string | null;
    created_at: string | null;
}

const priorityBadge: Record<string, string> = {
    low: 'badge-neutral',
    medium: 'badge-info',
    high: 'badge-warning',
    urgent: 'badge-danger',
};

const statusBadge: Record<string, string> = {
    open: 'badge-warning',
    in_progress: 'badge-info',
    resolved: 'badge-success',
    closed: 'badge-neutral',
};

export default function TicketsPage() {
    const [tickets, setTickets] = useState<Ticket[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('');

    useEffect(() => {
        const url = filter ? `/superadmin/tickets?status=${filter}` : '/superadmin/tickets';
        apiGet<Ticket[]>(url)
            .then(setTickets)
            .catch(() => { })
            .finally(() => setLoading(false));
    }, [filter]);

    const updateTicket = async (id: string, status: string) => {
        await apiPatch(`/superadmin/tickets/${id}`, { status });
        setTickets((prev) => prev.map((t) => t.id === id ? { ...t, status } : t));
    };

    return (
        <div>
            <div className="flex items-center justify-between" style={{ marginBottom: 32 }}>
                <div>
                    <h1>Support Tickets</h1>
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>Manage client support requests</p>
                </div>
                <div className="flex gap-sm">
                    {['', 'open', 'in_progress', 'resolved'].map((f) => (
                        <button key={f} className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-ghost'}`} onClick={() => { setFilter(f); setLoading(true); }}>
                            {f || 'Active'}
                        </button>
                    ))}
                </div>
            </div>

            {loading ? (
                <div className="flex justify-center" style={{ padding: 60 }}><div className="loader" /></div>
            ) : tickets.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">🎫</div>
                    <p>No {filter || 'active'} tickets</p>
                </div>
            ) : (
                <div className="flex flex-col gap-md animate-in">
                    {tickets.map((t) => (
                        <div key={t.id} className="card" style={{ padding: '16px 20px' }}>
                            <div className="flex items-center justify-between" style={{ marginBottom: 8 }}>
                                <div className="flex items-center gap-sm">
                                    <span className={`badge ${priorityBadge[t.priority]}`}>{t.priority}</span>
                                    <span className={`badge ${statusBadge[t.status]}`}>{t.status}</span>
                                    {t.tenant_name && <span className="text-sm text-muted">· {t.tenant_name}</span>}
                                </div>
                                <span className="text-sm text-muted">
                                    {t.created_at ? new Date(t.created_at).toLocaleString() : ''}
                                </span>
                            </div>
                            <h4 style={{ marginBottom: 4 }}>{t.subject}</h4>
                            <p className="text-sm text-muted" style={{ marginBottom: 12 }}>{t.description.slice(0, 200)}{t.description.length > 200 ? '...' : ''}</p>
                            <div className="flex gap-sm">
                                {t.status === 'open' && (
                                    <button className="btn btn-sm btn-secondary" onClick={() => updateTicket(t.id, 'in_progress')}>Mark In Progress</button>
                                )}
                                {t.status === 'in_progress' && (
                                    <button className="btn btn-sm btn-primary" onClick={() => updateTicket(t.id, 'resolved')}>Resolve</button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
