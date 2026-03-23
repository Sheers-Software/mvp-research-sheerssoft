'use client';

import { useAuth } from '@/lib/auth';
import { useTenant } from '@/lib/tenant-context';
import Link from 'next/link';

function ChannelDot({ status }: { status: string }) {
    const colors: Record<string, string> = {
        active: 'var(--success)',
        configuring: 'var(--warning)',
        failed: 'var(--danger)',
        pending: 'var(--text-muted)',
        skipped: 'var(--text-muted)',
    };
    return (
        <span
            title={status}
            style={{
                display: 'inline-block',
                width: 10,
                height: 10,
                borderRadius: '50%',
                background: colors[status] ?? 'var(--text-muted)',
                marginRight: 4,
            }}
        />
    );
}

export default function PortalHomePage() {
    const { user } = useAuth();
    const { tenantName, tenantTier, properties, loading } = useTenant();

    if (loading) {
        return (
            <div className="flex justify-center" style={{ padding: 80 }}>
                <div className="loader" />
            </div>
        );
    }

    const incompleteProperties = properties.filter((p) => p.onboarding_score < 100);

    return (
        <div>
            {/* Header */}
            <div className="flex items-center justify-between" style={{ marginBottom: 32 }}>
                <div>
                    <h1>Welcome back, {user?.full_name || 'there'}</h1>
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                        {tenantName}
                        {tenantTier && (
                            <span className="badge badge-warning" style={{ marginLeft: 8, fontSize: 11 }}>
                                {tenantTier}
                            </span>
                        )}
                    </p>
                </div>
                {(user?.role === 'owner' || user?.role === 'admin') && (
                    <Link href="/portal/properties" className="btn btn-primary btn-sm">
                        + Add Property
                    </Link>
                )}
            </div>

            {/* Onboarding checklist if any property is incomplete */}
            {incompleteProperties.length > 0 && (
                <div className="card animate-in" style={{ marginBottom: 28, borderColor: 'rgba(99,102,241,0.25)' }}>
                    <div className="flex items-center justify-between" style={{ marginBottom: 12 }}>
                        <h3 style={{ fontSize: 14 }}>Onboarding in progress</h3>
                        <Link href="/welcome" className="text-sm" style={{ color: 'var(--accent)', textDecoration: 'none' }}>
                            Resume wizard →
                        </Link>
                    </div>
                    {incompleteProperties.map((p) => (
                        <div key={p.id} style={{ marginBottom: 10 }}>
                            <div className="flex items-center justify-between" style={{ marginBottom: 4 }}>
                                <span className="text-sm">{p.name}</span>
                                <span className="text-xs text-muted">{p.onboarding_score}/100</span>
                            </div>
                            <div style={{ height: 6, background: 'var(--border-subtle)', borderRadius: 4, overflow: 'hidden' }}>
                                <div
                                    style={{
                                        height: '100%',
                                        width: `${p.onboarding_score}%`,
                                        background: p.onboarding_score >= 75 ? 'var(--success)' : p.onboarding_score >= 40 ? 'var(--warning)' : 'var(--accent)',
                                        borderRadius: 4,
                                        transition: 'width 0.4s ease',
                                    }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Properties grid */}
            {properties.length === 0 ? (
                <div className="empty-state" style={{ marginTop: 60 }}>
                    <div className="empty-icon">🏨</div>
                    <p>No properties yet</p>
                    <p className="text-sm text-muted" style={{ marginTop: 8, marginBottom: 16 }}>
                        Your account manager will set up your property, or you can add one.
                    </p>
                    {(user?.role === 'owner' || user?.role === 'admin') && (
                        <Link href="/portal/properties" className="btn btn-primary btn-sm">
                            Add your first property
                        </Link>
                    )}
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 20 }}>
                    {properties.map((prop) => (
                        <div key={prop.id} className="card animate-in" style={{ padding: 24 }}>
                            {/* Property header */}
                            <div className="flex items-center justify-between" style={{ marginBottom: 12 }}>
                                <h3 style={{ fontSize: 15, fontWeight: 600 }}>{prop.name}</h3>
                                <span className={`badge ${prop.is_active ? 'badge-success' : 'badge-warning'}`}>
                                    {prop.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </div>

                            {/* Onboarding progress */}
                            <div style={{ marginBottom: 14 }}>
                                <div className="flex items-center justify-between" style={{ marginBottom: 4 }}>
                                    <span className="text-xs text-muted">Setup progress</span>
                                    <span className="text-xs text-muted">{prop.onboarding_score}%</span>
                                </div>
                                <div style={{ height: 5, background: 'var(--border-subtle)', borderRadius: 4, overflow: 'hidden' }}>
                                    <div
                                        style={{
                                            height: '100%',
                                            width: `${prop.onboarding_score}%`,
                                            background: prop.onboarding_score >= 75 ? 'var(--success)' : prop.onboarding_score >= 40 ? 'var(--warning)' : 'var(--accent)',
                                            borderRadius: 4,
                                        }}
                                    />
                                </div>
                            </div>

                            {/* Mini stats */}
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 14 }}>
                                <div>
                                    <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--accent)' }}>{prop.weekly_inquiries}</div>
                                    <div className="text-xs text-muted">inquiries</div>
                                </div>
                                <div>
                                    <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--warning)' }}>{prop.weekly_leads}</div>
                                    <div className="text-xs text-muted">leads</div>
                                </div>
                                <div>
                                    <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--success)' }}>
                                        RM {(prop.weekly_revenue_rm ?? 0).toLocaleString('en-MY', { maximumFractionDigits: 0 })}
                                    </div>
                                    <div className="text-xs text-muted">revenue</div>
                                </div>
                            </div>

                            {/* Channel status dots */}
                            <div className="flex items-center" style={{ marginBottom: 16, gap: 12 }}>
                                <span className="text-xs text-muted">Channels:</span>
                                <span className="text-xs flex items-center">
                                    <ChannelDot status={prop.channel_statuses?.whatsapp ?? 'pending'} />
                                    WhatsApp
                                </span>
                                <span className="text-xs flex items-center">
                                    <ChannelDot status={prop.channel_statuses?.email ?? 'pending'} />
                                    Email
                                </span>
                                <span className="text-xs flex items-center">
                                    <ChannelDot status={prop.channel_statuses?.website ?? 'pending'} />
                                    Web
                                </span>
                            </div>

                            {/* Action links */}
                            <div className="flex items-center gap-sm">
                                <Link href="/dashboard" className="btn btn-primary btn-sm">
                                    View Dashboard
                                </Link>
                                <Link href={`/portal/kb/${prop.id}`} className="btn btn-ghost btn-sm">
                                    Manage KB
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
