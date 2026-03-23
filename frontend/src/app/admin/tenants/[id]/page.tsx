'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiGet } from '@/lib/api';

interface Property {
    id: string;
    name: string;
    slug: string;
    is_active: boolean;
}

interface User {
    id: string;
    email: string;
    full_name: string;
    role: string;
}

interface OnboardingProgress {
    property_id: string;
    whatsapp_status: string;
    email_status: string;
    website_status: string;
    kb_populated: boolean;
    first_inquiry_received: boolean;
    channel_errors: Record<string, string> | null;
}

interface KbDoc {
    category: string;
}

interface KbStatus {
    property_id: string;
    total: number;
    by_category: Record<string, number>;
}

interface TenantDetails {
    id: string;
    name: string;
    slug: string;
    subscription_tier: string;
    subscription_status: string;
    pilot_start_date: string | null;
    pilot_end_date: string | null;
    assigned_account_manager: string | null;
    is_active: boolean;
    created_at: string | null;
    properties: Property[];
    users: User[];
    onboarding: OnboardingProgress[];
    stats: {
        total_conversations: number;
        total_leads: number;
        property_count: number;
        user_count: number;
    };
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

const channelBadge: Record<string, string> = {
    active: 'badge-success',
    pending: 'badge-warning',
    configuring: 'badge-info',
    skipped: 'badge-neutral',
    failed: 'badge-danger',
};

export default function TenantDetailsPage() {
    const params = useParams();
    const router = useRouter();
    const [tenant, setTenant] = useState<TenantDetails | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [kbStatuses, setKbStatuses] = useState<KbStatus[]>([]);

    useEffect(() => {
        if (!params.id) return;

        apiGet<TenantDetails>(`/superadmin/tenants/${params.id}`)
            .then((data) => {
                setTenant(data);
                // Load KB status for each property
                (data.properties || []).forEach((prop) => {
                    apiGet<{ documents: KbDoc[] }>(`/properties/${prop.id}/kb`)
                        .then((kb) => {
                            const docs = kb.documents || [];
                            const by_category: Record<string, number> = {};
                            docs.forEach((d) => {
                                by_category[d.category] = (by_category[d.category] || 0) + 1;
                            });
                            setKbStatuses((prev) => [
                                ...prev.filter((s) => s.property_id !== prop.id),
                                { property_id: prop.id, total: docs.length, by_category },
                            ]);
                        })
                        .catch(() => {});
                });
            })
            .catch((err) => setError(err.message || 'Failed to load tenant details'))
            .finally(() => setLoading(false));
    }, [params.id]);

    if (loading) {
        return <div className="flex justify-center" style={{ padding: 60 }}><div className="loader" /></div>;
    }

    if (error || !tenant) {
        return (
            <div className="empty-state">
                <div className="empty-icon">⚠️</div>
                <p>{error || 'Tenant not found.'}</p>
                <button className="btn btn-ghost" onClick={() => router.back()} style={{ marginTop: 16 }}>
                    ← Back to Tenants
                </button>
            </div>
        );
    }

    return (
        <div className="animate-in">
            {/* Header section with back button */}
            <div style={{ marginBottom: 24 }}>
                <button 
                    className="btn btn-ghost text-sm" 
                    onClick={() => router.back()}
                    style={{ padding: '4px 0', marginBottom: 16 }}
                >
                    ← Back to Tenants
                </button>
                <div className="flex items-center justify-between">
                    <div>
                        <h1 style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                            {tenant.name}
                            {!tenant.is_active && <span className="badge badge-danger">Inactive</span>}
                        </h1>
                        <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                            {tenant.slug} · Created {tenant.created_at ? new Date(tenant.created_at).toLocaleDateString() : 'Unknown'}
                        </p>
                    </div>
                    <div className="flex items-center gap-sm" style={{ flexWrap: 'wrap' }}>
                        <span className={`badge ${tierBadge[tenant.subscription_tier] || 'badge-neutral'}`}>
                            {tenant.subscription_tier.toUpperCase()}
                        </span>
                        <span className={`badge ${statusBadge[tenant.subscription_status] || 'badge-neutral'}`}>
                            {tenant.subscription_status.toUpperCase()}
                        </span>
                        <Link
                            href={`/admin/kb-ingestion?tenantId=${tenant.id}`}
                            className="btn btn-primary btn-sm"
                            style={{ marginLeft: 8 }}
                        >
                            Open KB Ingestion →
                        </Link>
                        {tenant.properties.length > 0 && tenant.users.length === 0 && (
                            <Link
                                href={`/admin/tenants/${tenant.id}/invite`}
                                className="btn btn-ghost btn-sm"
                            >
                                Provision User
                            </Link>
                        )}
                    </div>
                </div>
            </div>

            {/* Quick Stats Banner */}
            <div className="metrics-grid" style={{ marginBottom: 32 }}>
                <div className="metric-card">
                    <p className="metric-label">Total Conversations</p>
                    <p className="metric-value">{tenant.stats.total_conversations.toLocaleString()}</p>
                </div>
                <div className="metric-card">
                    <p className="metric-label">Total Leads</p>
                    <p className="metric-value text-success">{tenant.stats.total_leads.toLocaleString()}</p>
                </div>
                <div className="metric-card">
                    <p className="metric-label">Properties</p>
                    <p className="metric-value">{tenant.stats.property_count}</p>
                </div>
                <div className="metric-card">
                    <p className="metric-label">Team Members</p>
                    <p className="metric-value">{tenant.stats.user_count}</p>
                </div>
            </div>

            <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: 32 }}>
                {/* Left Column */}
                <div className="flex flex-col gap-lg">
                    
                    {/* Properties Section */}
                    <section>
                        <h3 style={{ marginBottom: 16, fontSize: 16, fontWeight: 600 }}>Properties</h3>
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Slug</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {tenant.properties.map((p) => (
                                        <tr key={p.id}>
                                            <td><strong>{p.name}</strong></td>
                                            <td className="text-muted text-sm">{p.slug}</td>
                                            <td>
                                                <span className={`badge ${p.is_active ? 'badge-success' : 'badge-neutral'}`}>
                                                    {p.is_active ? 'Active' : 'Inactive'}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                    {tenant.properties.length === 0 && (
                                        <tr><td colSpan={3} className="text-center text-muted" style={{ padding: 24 }}>No properties</td></tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </section>

                    {/* KB Status Section */}
                    <section>
                        <h3 style={{ marginBottom: 16, fontSize: 16, fontWeight: 600 }}>KB Status</h3>
                        <div className="flex flex-col gap-sm">
                            {tenant.properties.map((prop) => {
                                const kb = kbStatuses.find((s) => s.property_id === prop.id);
                                const cats = ['faqs', 'rooms', 'facilities', 'policies'];
                                return (
                                    <div key={prop.id} className="card" style={{ padding: 16 }}>
                                        <div className="flex items-center justify-between" style={{ marginBottom: kb ? 12 : 0 }}>
                                            <strong className="text-sm">{prop.name}</strong>
                                            <div className="flex gap-sm">
                                                <Link
                                                    href={`/admin/kb-ingestion?tenantId=${tenant.id}&propertyId=${prop.id}`}
                                                    className="btn btn-ghost btn-sm"
                                                >
                                                    Ingest KB
                                                </Link>
                                            </div>
                                        </div>
                                        {kb ? (
                                            <div>
                                                <div className="flex gap-sm" style={{ flexWrap: 'wrap', marginBottom: 8 }}>
                                                    {cats.map((cat) => (
                                                        <span key={cat} className="badge badge-neutral" style={{ fontSize: 11 }}>
                                                            {cat}: {kb.by_category[cat] || 0}
                                                        </span>
                                                    ))}
                                                </div>
                                                <p className="text-muted text-sm">
                                                    {kb.total} total embedding{kb.total !== 1 ? 's' : ''}
                                                </p>
                                            </div>
                                        ) : (
                                            <p className="text-muted text-sm">Loading KB data…</p>
                                        )}
                                    </div>
                                );
                            })}
                            {tenant.properties.length === 0 && (
                                <p className="text-muted text-sm">No properties to show KB status for.</p>
                            )}
                        </div>
                    </section>

                    {/* Team Members Section */}
                    <section>
                        <h3 style={{ marginBottom: 16, fontSize: 16, fontWeight: 600 }}>Team Members</h3>
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>User</th>
                                        <th>Role</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {tenant.users.map((u) => (
                                        <tr key={u.id}>
                                            <td>
                                                <strong>{u.full_name}</strong>
                                                <br />
                                                <span className="text-muted text-sm">{u.email}</span>
                                            </td>
                                            <td><span className="badge badge-neutral">{u.role}</span></td>
                                        </tr>
                                    ))}
                                    {tenant.users.length === 0 && (
                                        <tr><td colSpan={2} className="text-center text-muted" style={{ padding: 24 }}>No members</td></tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </section>
                </div>

                {/* Right Column */}
                <div className="flex flex-col gap-lg">
                    
                    {/* Configuration / Details */}
                    <section>
                        <h3 style={{ marginBottom: 16, fontSize: 16, fontWeight: 600 }}>Account Details</h3>
                        <div className="card text-sm" style={{ padding: 20 }}>
                            <div className="flex justify-between" style={{ paddingBottom: 12, borderBottom: '1px solid var(--border)' }}>
                                <span className="text-muted">Account Manager</span>
                                <strong>{tenant.assigned_account_manager || 'None'}</strong>
                            </div>
                            <div className="flex justify-between" style={{ padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
                                <span className="text-muted">Pilot Start</span>
                                <span>{tenant.pilot_start_date ? new Date(tenant.pilot_start_date).toLocaleDateString() : '—'}</span>
                            </div>
                            <div className="flex justify-between" style={{ paddingTop: 12 }}>
                                <span className="text-muted">Pilot End</span>
                                <span>{tenant.pilot_end_date ? new Date(tenant.pilot_end_date).toLocaleDateString() : '—'}</span>
                            </div>
                        </div>
                    </section>

                    {/* Onboarding Overview */}
                    <section>
                        <h3 style={{ marginBottom: 16, fontSize: 16, fontWeight: 600 }}>Onboarding Status</h3>
                        {tenant.onboarding.map((obs, idx) => {
                            const propName = tenant.properties.find(p => p.id === obs.property_id)?.name || 'Unknown Property';

                            // Compute progress score from channel statuses + milestone flags
                            const channelPoints: Record<string, number> = { active: 20, skipped: 10, configuring: 5, pending: 0, failed: 0 };
                            const waPoints = channelPoints[obs.whatsapp_status] ?? 0;
                            const emailPoints = channelPoints[obs.email_status] ?? 0;
                            const webPoints = channelPoints[obs.website_status] ?? 0;
                            const kbPoints = obs.kb_populated ? 20 : 0;
                            const inquiryPoints = obs.first_inquiry_received ? 20 : 0;
                            const score = Math.min(100, waPoints + emailPoints + webPoints + kbPoints + inquiryPoints);
                            const filledBlocks = Math.round(score / 10);
                            const progressBar = '█'.repeat(filledBlocks) + '░'.repeat(10 - filledBlocks);

                            const failedChannels: Record<string, string> = {};
                            if (obs.whatsapp_status === 'failed') failedChannels['whatsapp'] = obs.channel_errors?.whatsapp || 'Setup failed';
                            if (obs.email_status === 'failed') failedChannels['email'] = obs.channel_errors?.email || 'Setup failed';
                            if (obs.website_status === 'failed') failedChannels['website'] = obs.channel_errors?.website || 'Setup failed';

                            return (
                                <div key={idx} className="card" style={{ padding: 20, marginBottom: 16 }}>
                                    <h4 style={{ fontSize: 14, marginBottom: 12, paddingBottom: 12, borderBottom: '1px solid var(--border)' }}>
                                        {propName}
                                    </h4>

                                    {/* Enhancement A: Progress Bar */}
                                    <div style={{ marginBottom: 16 }}>
                                        <div className="flex items-center justify-between" style={{ marginBottom: 6 }}>
                                            <span className="text-sm text-muted">Setup Progress</span>
                                            <span className="text-sm" style={{ fontWeight: 600 }}>{score}%</span>
                                        </div>
                                        <div style={{
                                            fontFamily: 'monospace',
                                            fontSize: 13,
                                            letterSpacing: 1,
                                            color: score === 100 ? 'var(--success)' : score >= 60 ? 'var(--warning)' : 'var(--danger)',
                                            background: 'var(--surface-raised)',
                                            padding: '6px 10px',
                                            borderRadius: 4,
                                        }}>
                                            [{progressBar}] {score}%
                                        </div>
                                    </div>

                                    <div className="flex flex-col gap-sm text-sm">
                                        <div className="flex justify-between items-center">
                                            <span className="text-muted">WhatsApp Channel</span>
                                            <span className={`badge ${channelBadge[obs.whatsapp_status] || 'badge-neutral'}`}>
                                                {obs.whatsapp_status}
                                            </span>
                                        </div>
                                        {/* Enhancement C: failed channel error + contact support note */}
                                        {obs.whatsapp_status === 'failed' && (
                                            <div style={{ padding: '8px 12px', background: 'var(--danger-light)', borderRadius: 4, fontSize: 12 }}>
                                                <span className="text-danger">{failedChannels['whatsapp']}</span>
                                                <span className="text-muted" style={{ marginLeft: 8 }}>— Contact SheersSoft support to retry.</span>
                                            </div>
                                        )}

                                        <div className="flex justify-between items-center">
                                            <span className="text-muted">Email Channel</span>
                                            <span className={`badge ${channelBadge[obs.email_status] || 'badge-neutral'}`}>
                                                {obs.email_status}
                                            </span>
                                        </div>
                                        {obs.email_status === 'failed' && (
                                            <div style={{ padding: '8px 12px', background: 'var(--danger-light)', borderRadius: 4, fontSize: 12 }}>
                                                <span className="text-danger">{failedChannels['email']}</span>
                                                <span className="text-muted" style={{ marginLeft: 8 }}>— Contact SheersSoft support to retry.</span>
                                            </div>
                                        )}

                                        <div className="flex justify-between items-center">
                                            <span className="text-muted">Website Widget</span>
                                            <span className={`badge ${channelBadge[obs.website_status] || 'badge-neutral'}`}>
                                                {obs.website_status}
                                            </span>
                                        </div>
                                        {obs.website_status === 'failed' && (
                                            <div style={{ padding: '8px 12px', background: 'var(--danger-light)', borderRadius: 4, fontSize: 12 }}>
                                                <span className="text-danger">{failedChannels['website']}</span>
                                                <span className="text-muted" style={{ marginLeft: 8 }}>— Contact SheersSoft support to retry.</span>
                                            </div>
                                        )}

                                        <div className="flex justify-between items-center" style={{ marginTop: 8 }}>
                                            <span className="text-muted">Knowledge Base</span>
                                            <span>{obs.kb_populated ? '✅ Ready' : '⏳ Pending'}</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-muted">First Inquiry</span>
                                            <span>{obs.first_inquiry_received ? '✅ Yes' : '⏳ No'}</span>
                                        </div>
                                    </div>

                                    {/* Existing channel_errors block (non-failed extra errors) */}
                                    {obs.channel_errors && Object.keys(obs.channel_errors).filter(k => !['whatsapp','email','website'].includes(k)).length > 0 && (
                                        <div style={{ marginTop: 16, padding: 12, backgroundColor: 'var(--danger-light)', borderRadius: 6 }}>
                                            <p className="text-danger text-sm" style={{ fontWeight: 600, marginBottom: 4 }}>Additional Setup Errors:</p>
                                            <ul className="text-danger text-sm" style={{ paddingLeft: 16, margin: 0 }}>
                                                {Object.entries(obs.channel_errors)
                                                    .filter(([k]) => !['whatsapp','email','website'].includes(k))
                                                    .map(([chan, err]) => (
                                                        <li key={chan}><strong>{chan}:</strong> {err as string}</li>
                                                    ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                        {tenant.onboarding.length === 0 && (
                            <p className="text-muted text-sm">No onboarding data available.</p>
                        )}
                    </section>
                </div>
            </div>
        </div>
    );
}
