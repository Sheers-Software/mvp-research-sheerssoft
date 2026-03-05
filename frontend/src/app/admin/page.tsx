'use client';

import { useEffect, useState } from 'react';
import { apiGet } from '@/lib/api';

interface Metrics {
    total_tenants: number;
    active_tenants: number;
    total_properties: number;
    total_conversations_alltime: number;
    total_conversations_mtd: number;
    total_leads_mtd: number;
    open_support_tickets: number;
    pending_applications: number;
}

const statCards = [
    { key: 'active_tenants', label: 'Active Tenants', icon: '🏨', color: 'var(--success)' },
    { key: 'total_properties', label: 'Properties', icon: '🏢', color: 'var(--info)' },
    { key: 'total_conversations_mtd', label: 'Conversations (MTD)', icon: '💬', color: 'var(--accent)' },
    { key: 'total_leads_mtd', label: 'Leads (MTD)', icon: '🎯', color: 'var(--warning)' },
    { key: 'open_support_tickets', label: 'Open Tickets', icon: '🎫', color: 'var(--danger)' },
    { key: 'pending_applications', label: 'Pending Apps', icon: '📥', color: 'var(--info)' },
    { key: 'total_conversations_alltime', label: 'All-Time Convos', icon: '📈', color: 'var(--success)' },
    { key: 'total_tenants', label: 'Total Tenants', icon: '👥', color: 'var(--text-accent)' },
];

export default function AdminOverviewPage() {
    const [metrics, setMetrics] = useState<Metrics | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        apiGet<Metrics>('/superadmin/metrics')
            .then(setMetrics)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false));
    }, []);

    return (
        <div>
            <div className="flex items-center justify-between" style={{ marginBottom: 32 }}>
                <div>
                    <h1>Platform Overview</h1>
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                        Real-time metrics across all Nocturn AI tenants
                    </p>
                </div>
                <span className="badge badge-success">● Live</span>
            </div>

            {loading ? (
                <div className="flex justify-center" style={{ padding: 60 }}>
                    <div className="loader" />
                </div>
            ) : error ? (
                <div className="card" style={{ textAlign: 'center', padding: 40 }}>
                    <p style={{ color: 'var(--danger)' }}>⚠️ {error}</p>
                    <p className="text-sm text-muted" style={{ marginTop: 8 }}>
                        Make sure you&apos;re logged in as a SuperAdmin and the backend is running.
                    </p>
                </div>
            ) : metrics ? (
                <div className="grid grid-4 animate-in">
                    {statCards.map((card, i) => (
                        <div
                            key={card.key}
                            className="stat-card animate-slide-up"
                            style={{ animationDelay: `${i * 60}ms`, animationFillMode: 'backwards' }}
                        >
                            <div className="stat-icon">{card.icon}</div>
                            <div className="stat-label">{card.label}</div>
                            <div className="stat-value" style={{ color: card.color }}>
                                {(metrics as any)[card.key]?.toLocaleString() ?? 0}
                            </div>
                        </div>
                    ))}
                </div>
            ) : null}
        </div>
    );
}
