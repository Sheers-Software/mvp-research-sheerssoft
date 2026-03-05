'use client';

import { useEffect, useState } from 'react';
import { apiGet } from '@/lib/api';

interface PipelineItem {
    tenant_id: string;
    tenant_name: string;
    property_id: string;
    created_at: string | null;
}

interface PipelineData {
    provisioned: PipelineItem[];
    channels_setup: PipelineItem[];
    live: PipelineItem[];
    first_week_review: PipelineItem[];
    fully_onboarded: PipelineItem[];
}

const columns = [
    { key: 'provisioned', label: 'Provisioned', color: 'var(--text-muted)', icon: '📋' },
    { key: 'channels_setup', label: 'Channels Setup', color: 'var(--warning)', icon: '⚙️' },
    { key: 'live', label: 'Live', color: 'var(--success)', icon: '🟢' },
    { key: 'first_week_review', label: 'First Week', color: 'var(--info)', icon: '📊' },
    { key: 'fully_onboarded', label: 'Fully Onboarded', color: 'var(--accent)', icon: '🏆' },
];

function TimeAgo({ date }: { date: string | null }) {
    if (!date) return <span className="text-muted">—</span>;
    const d = new Date(date);
    const diff = Date.now() - d.getTime();
    const days = Math.floor(diff / 86400000);
    if (days === 0) return <span className="text-muted">Today</span>;
    if (days === 1) return <span className="text-muted">Yesterday</span>;
    return <span className="text-muted">{days}d ago</span>;
}

export default function PipelinePage() {
    const [pipeline, setPipeline] = useState<PipelineData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        apiGet<PipelineData>('/superadmin/pipeline')
            .then(setPipeline)
            .catch(() => { })
            .finally(() => setLoading(false));
    }, []);

    return (
        <div>
            <div style={{ marginBottom: 32 }}>
                <h1>Onboarding Pipeline</h1>
                <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                    Track every client from provisioning to fully onboarded
                </p>
            </div>

            {loading ? (
                <div className="flex justify-center" style={{ padding: 60 }}>
                    <div className="loader" />
                </div>
            ) : pipeline ? (
                <div className="kanban animate-in">
                    {columns.map((col) => {
                        const items = (pipeline as any)[col.key] as PipelineItem[];
                        return (
                            <div key={col.key} className="kanban-column">
                                <div className="kanban-column-header">
                                    <span>{col.icon} {col.label}</span>
                                    <span className="kanban-column-count" style={{ color: col.color }}>
                                        {items.length}
                                    </span>
                                </div>

                                {items.length === 0 ? (
                                    <p className="text-sm text-muted" style={{ padding: '20px 0', textAlign: 'center' }}>
                                        No tenants
                                    </p>
                                ) : (
                                    items.map((item) => (
                                        <a key={item.tenant_id} href={`/admin/tenants/${item.tenant_id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                                            <div className="kanban-card">
                                                <h4 style={{ fontSize: 14, marginBottom: 4 }}>{item.tenant_name}</h4>
                                                <TimeAgo date={item.created_at} />
                                            </div>
                                        </a>
                                    ))
                                )}
                            </div>
                        );
                    })}
                </div>
            ) : (
                <div className="empty-state">
                    <div className="empty-icon">🔄</div>
                    <p>No pipeline data available</p>
                </div>
            )}
        </div>
    );
}
