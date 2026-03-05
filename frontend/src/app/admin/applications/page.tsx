'use client';

import { useEffect, useState } from 'react';
import { apiGet, apiPatch } from '@/lib/api';

interface Application {
    id: string;
    hotel_name: string;
    contact_name: string;
    email: string;
    phone: string | null;
    room_count: number | null;
    status: string;
    notes: string | null;
    converted_to_tenant_id: string | null;
    created_at: string;
}

const statusBadge: Record<string, string> = {
    new: 'badge-info',
    contacted: 'badge-warning',
    qualified: 'badge-success',
    converted: 'badge-success',
    declined: 'badge-danger',
};

export default function ApplicationsPage() {
    const [apps, setApps] = useState<Application[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        apiGet<Application[]>('/superadmin/applications')
            .then(setApps)
            .catch(() => { })
            .finally(() => setLoading(false));
    }, []);

    const updateStatus = async (id: string, status: string) => {
        await apiPatch(`/superadmin/applications/${id}`, { status });
        setApps((prev) => prev.map((a) => a.id === id ? { ...a, status } : a));
    };

    return (
        <div>
            <div className="flex items-center justify-between" style={{ marginBottom: 32 }}>
                <div>
                    <h1>Applications</h1>
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                        Incoming applications from <a href="https://ai.sheerssoft.com/apply" target="_blank" rel="noopener">ai.sheerssoft.com/apply</a>
                    </p>
                </div>
                <span className="badge badge-info">{apps.filter(a => a.status === 'new').length} new</span>
            </div>

            {loading ? (
                <div className="flex justify-center" style={{ padding: 60 }}><div className="loader" /></div>
            ) : apps.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">📥</div>
                    <p>No applications yet</p>
                </div>
            ) : (
                <div className="table-container animate-in">
                    <table>
                        <thead>
                            <tr>
                                <th>Hotel</th>
                                <th>Contact</th>
                                <th>Rooms</th>
                                <th>Status</th>
                                <th>Received</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {apps.map((a) => (
                                <tr key={a.id}>
                                    <td>
                                        <strong>{a.hotel_name}</strong>
                                    </td>
                                    <td>
                                        <div>{a.contact_name}</div>
                                        <div className="text-sm text-muted">{a.email}</div>
                                        {a.phone && <div className="text-sm text-muted">{a.phone}</div>}
                                    </td>
                                    <td>{a.room_count || '—'}</td>
                                    <td>
                                        <span className={`badge ${statusBadge[a.status] || 'badge-neutral'}`}>{a.status}</span>
                                    </td>
                                    <td className="text-sm text-muted">{new Date(a.created_at).toLocaleDateString()}</td>
                                    <td>
                                        <div className="flex gap-sm">
                                            {a.status === 'new' && (
                                                <button className="btn btn-sm btn-secondary" onClick={() => updateStatus(a.id, 'contacted')}>
                                                    Mark Contacted
                                                </button>
                                            )}
                                            {a.status === 'contacted' && (
                                                <button className="btn btn-sm btn-primary" onClick={() => updateStatus(a.id, 'qualified')}>
                                                    Qualified
                                                </button>
                                            )}
                                            {a.status === 'qualified' && (
                                                <a href="/admin/onboarding" className="btn btn-sm btn-primary">
                                                    Convert →
                                                </a>
                                            )}
                                        </div>
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
