'use client';

import { useEffect, useState } from 'react';
import { apiGet } from '@/lib/api';

interface Tenant {
    id: string;
    name: string;
    slug: string;
    subscription_tier: string;
    subscription_status: string;
    is_active: boolean;
    property_count: number;
    assigned_account_manager: string | null;
    created_at: string | null;
}

const tierBadge: Record<string, string> = {
    pilot: 'badge-info',
    boutique: 'badge-neutral',
    independent: 'badge-warning',
    premium: 'badge-success',
};

const statusBadge: Record<string, string> = {
    trialing: 'badge-info',
    active: 'badge-success',
    cancelled: 'badge-danger',
    expired: 'badge-neutral',
};

export default function TenantsPage() {
    const [tenants, setTenants] = useState<Tenant[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        apiGet<Tenant[]>('/superadmin/tenants')
            .then(setTenants)
            .catch(() => { })
            .finally(() => setLoading(false));
    }, []);

    return (
        <div>
            <div className="flex items-center justify-between" style={{ marginBottom: 32 }}>
                <div>
                    <h1>Tenants</h1>
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>All registered hotel clients</p>
                </div>
                <a href="/admin/onboarding" className="btn btn-primary">➕ New Client</a>
            </div>

            {loading ? (
                <div className="flex justify-center" style={{ padding: 60 }}><div className="loader" /></div>
            ) : tenants.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">🏨</div>
                    <p>No tenants yet. <a href="/admin/onboarding">Onboard your first client →</a></p>
                </div>
            ) : (
                <div className="table-container animate-in">
                    <table>
                        <thead>
                            <tr>
                                <th>Hotel</th>
                                <th>Tier</th>
                                <th>Status</th>
                                <th>Properties</th>
                                <th>Manager</th>
                                <th>Created</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tenants.map((t) => (
                                <tr key={t.id} style={{ cursor: 'pointer' }} onClick={() => window.location.href = `/admin/tenants/${t.id}`}>
                                    <td>
                                        <strong>{t.name}</strong>
                                        <br />
                                        <span className="text-sm text-muted">{t.slug}</span>
                                    </td>
                                    <td><span className={`badge ${tierBadge[t.subscription_tier] || 'badge-neutral'}`}>{t.subscription_tier}</span></td>
                                    <td><span className={`badge ${statusBadge[t.subscription_status] || 'badge-neutral'}`}>{t.subscription_status}</span></td>
                                    <td>{t.property_count}</td>
                                    <td className="text-muted">{t.assigned_account_manager || '—'}</td>
                                    <td className="text-sm text-muted">{t.created_at ? new Date(t.created_at).toLocaleDateString() : '—'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
