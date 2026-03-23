'use client';

import { useEffect, useState } from 'react';
import { apiGet } from '@/lib/api';

interface ChannelStatus {
    status: string;
    error?: string;
    embed_slug?: string;
}

interface PropertyChannels {
    property_id: string;
    property_name: string;
    property_slug: string;
    channels: {
        whatsapp: ChannelStatus;
        email: ChannelStatus;
        website: ChannelStatus;
    };
}

function StatusIcon({ status }: { status: string }) {
    if (status === 'active') return <span style={{ color: 'var(--success)' }}>✓</span>;
    if (status === 'configuring' || status === 'pending') return <span style={{ color: 'var(--warning)' }}>⏳</span>;
    if (status === 'failed') return <span style={{ color: 'var(--danger)' }}>✗</span>;
    return <span style={{ color: 'var(--text-muted)' }}>—</span>;
}

function statusBadgeClass(status: string): string {
    if (status === 'active') return 'badge-success';
    if (status === 'configuring' || status === 'pending') return 'badge-warning';
    if (status === 'failed') return 'badge-danger';
    return '';
}

interface ChannelCardProps {
    name: string;
    icon: string;
    channelKey: 'whatsapp' | 'email' | 'website';
    status: ChannelStatus;
    slug: string;
}

function ChannelCard({ name, icon, channelKey, status, slug }: ChannelCardProps) {
    const [copied, setCopied] = useState(false);

    const embedCode = `<script src="https://cdn.sheerssoft.com/widget.js" data-property="${slug}" async></script>`;

    const handleCopy = () => {
        navigator.clipboard.writeText(embedCode).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    };

    const statusLabel = status.status.charAt(0).toUpperCase() + status.status.slice(1);

    return (
        <div className="card" style={{ padding: 20 }}>
            <div className="flex items-center justify-between" style={{ marginBottom: 12 }}>
                <div className="flex items-center gap-sm">
                    <span style={{ fontSize: 24 }}>{icon}</span>
                    <span style={{ fontWeight: 600, fontSize: 14 }}>{name}</span>
                </div>
                <span className={`badge ${statusBadgeClass(status.status)}`} style={!statusBadgeClass(status.status) ? { color: 'var(--text-muted)', fontSize: 11 } : {}}>
                    <StatusIcon status={status.status} />
                    {' '}{statusLabel}
                </span>
            </div>

            {status.status === 'failed' && status.error && (
                <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 6, padding: '8px 12px', fontSize: 12, color: 'var(--danger)', marginBottom: 10 }}>
                    {status.error}
                </div>
            )}

            {channelKey === 'website' && status.status === 'active' && (
                <div style={{ marginTop: 8 }}>
                    <p className="text-xs text-muted" style={{ marginBottom: 6 }}>Embed code — paste before &lt;/body&gt;:</p>
                    <div style={{ position: 'relative', background: 'var(--surface-elevated, rgba(0,0,0,0.2))', borderRadius: 6, padding: '10px 12px', paddingRight: 80, fontFamily: 'monospace', fontSize: 11, color: 'var(--text-secondary)', wordBreak: 'break-all' }}>
                        {embedCode}
                        <button
                            onClick={handleCopy}
                            className="btn btn-ghost btn-sm"
                            style={{ position: 'absolute', top: 6, right: 6, fontSize: 11, padding: '2px 8px' }}
                        >
                            {copied ? '✓ Copied' : 'Copy'}
                        </button>
                    </div>
                </div>
            )}

            {(status.status === 'pending' || status.status === 'configuring') && (
                <p className="text-xs text-muted">
                    Channels are configured by your account manager (SheersSoft). Contact support if this is taking longer than expected.
                </p>
            )}
        </div>
    );
}

export default function PortalChannelsPage() {
    const [channels, setChannels] = useState<PropertyChannels[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        apiGet<PropertyChannels[]>('/portal/channels')
            .then((data) => setChannels(data || []))
            .catch(() => setChannels([]))
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="flex justify-center" style={{ padding: 80 }}>
                <div className="loader" />
            </div>
        );
    }

    return (
        <div>
            <div style={{ marginBottom: 28 }}>
                <h1>Channels</h1>
                <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                    View the status of your AI concierge channels across all properties
                </p>
            </div>

            {channels.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">📡</div>
                    <p>No channel data available</p>
                    <p className="text-sm text-muted" style={{ marginTop: 4 }}>
                        Channel setup is managed by your SheersSoft account manager.
                        Contact{' '}
                        <a href="mailto:support@sheerssoft.com" style={{ color: 'var(--accent)' }}>
                            support@sheerssoft.com
                        </a>{' '}
                        to get started.
                    </p>
                </div>
            ) : (
                <div style={{ display: 'grid', gap: 32 }}>
                    {channels.map((prop) => (
                        <div key={prop.property_id}>
                            <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                {prop.property_name}
                            </h3>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }}>
                                <ChannelCard
                                    name="WhatsApp"
                                    icon="💬"
                                    channelKey="whatsapp"
                                    status={prop.channels?.whatsapp ?? { status: 'pending' }}
                                    slug={prop.property_slug}
                                />
                                <ChannelCard
                                    name="Email"
                                    icon="✉️"
                                    channelKey="email"
                                    status={prop.channels?.email ?? { status: 'pending' }}
                                    slug={prop.property_slug}
                                />
                                <ChannelCard
                                    name="Website Widget"
                                    icon="🌐"
                                    channelKey="website"
                                    status={prop.channels?.website ?? { status: 'pending' }}
                                    slug={prop.property_slug}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
