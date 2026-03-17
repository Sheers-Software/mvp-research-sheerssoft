'use client';

import { useEffect, useState, useCallback } from 'react';
import { apiGet } from '@/lib/api';

interface ServiceResult {
    name: string;
    status: 'ok' | 'error' | 'timeout';
    latency_ms: number;
    detail?: string;
}

interface HealthPayload {
    overall: 'ok' | 'degraded';
    checked_at: string;
    services: ServiceResult[];
}

const STATUS_COLOR: Record<string, string> = {
    ok: 'var(--success)',
    error: 'var(--danger)',
    timeout: 'var(--warning)',
};

const STATUS_LABEL: Record<string, string> = {
    ok: 'OK',
    error: 'Error',
    timeout: 'Timeout',
};

const STATUS_ICON: Record<string, string> = {
    ok: '✓',
    error: '✗',
    timeout: '⏱',
};

function ServiceCard({ svc }: { svc: ServiceResult }) {
    const color = STATUS_COLOR[svc.status] ?? 'var(--text-muted)';
    return (
        <div
            style={{
                padding: '14px 16px',
                borderRadius: 8,
                border: `1px solid ${svc.status === 'ok' ? 'var(--border-subtle)' : color}`,
                background: svc.status === 'ok' ? 'var(--bg-card)' : `${color}10`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: 12,
            }}
        >
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span
                    style={{
                        width: 28,
                        height: 28,
                        borderRadius: '50%',
                        background: color,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#fff',
                        fontSize: 13,
                        fontWeight: 700,
                        flexShrink: 0,
                    }}
                >
                    {STATUS_ICON[svc.status]}
                </span>
                <div>
                    <strong style={{ fontSize: 14 }}>{svc.name}</strong>
                    {svc.detail && (
                        <p className="text-xs text-muted" style={{ marginTop: 2 }}>
                            {svc.detail}
                        </p>
                    )}
                </div>
            </div>
            <div style={{ textAlign: 'right', flexShrink: 0 }}>
                <span
                    className="badge"
                    style={{
                        background: `${color}20`,
                        color,
                        border: `1px solid ${color}40`,
                        fontSize: 11,
                        fontWeight: 700,
                    }}
                >
                    {STATUS_LABEL[svc.status]}
                </span>
                <p className="text-xs text-muted" style={{ marginTop: 4 }}>
                    {svc.latency_ms} ms
                </p>
            </div>
        </div>
    );
}

export default function ServiceHealthPage() {
    const [data, setData] = useState<HealthPayload | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [countdown, setCountdown] = useState(30);

    const refresh = useCallback(() => {
        setLoading(true);
        setError('');
        apiGet<HealthPayload>('/superadmin/service-health')
            .then((d) => {
                setData(d);
                setCountdown(30);
            })
            .catch((e) => setError(e.message || 'Failed to fetch health status'))
            .finally(() => setLoading(false));
    }, []);

    // Initial load
    useEffect(() => {
        refresh();
    }, [refresh]);

    // 30-second auto-refresh
    useEffect(() => {
        const interval = setInterval(() => {
            setCountdown((c) => {
                if (c <= 1) {
                    refresh();
                    return 30;
                }
                return c - 1;
            });
        }, 1000);
        return () => clearInterval(interval);
    }, [refresh]);

    const healthyCount = data?.services.filter((s) => s.status === 'ok').length ?? 0;
    const totalCount = data?.services.length ?? 0;
    const overallColor = data?.overall === 'ok' ? 'var(--success)' : 'var(--danger)';

    return (
        <div>
            <div className="flex items-center justify-between" style={{ marginBottom: 24 }}>
                <div>
                    <h1>Service Health</h1>
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                        Live status of all external integrations — refreshes every 30s
                    </p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span className="text-xs text-muted">Next refresh in {countdown}s</span>
                    <button
                        className="btn btn-sm btn-ghost"
                        onClick={refresh}
                        disabled={loading}
                    >
                        {loading ? 'Checking...' : 'Refresh now'}
                    </button>
                </div>
            </div>

            {error && (
                <div
                    className="card"
                    style={{ padding: '12px 16px', marginBottom: 24, borderColor: 'var(--danger)', color: 'var(--danger)' }}
                >
                    {error}
                </div>
            )}

            {data && (
                <>
                    {/* Overall status banner */}
                    <div
                        className="card"
                        style={{
                            padding: '16px 20px',
                            marginBottom: 24,
                            borderColor: overallColor,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                        }}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                            <span
                                style={{
                                    width: 40,
                                    height: 40,
                                    borderRadius: '50%',
                                    background: overallColor,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontSize: 18,
                                    color: '#fff',
                                }}
                            >
                                {data.overall === 'ok' ? '✓' : '!'}
                            </span>
                            <div>
                                <strong style={{ fontSize: 16, color: overallColor }}>
                                    {data.overall === 'ok' ? 'All systems operational' : 'Service degradation detected'}
                                </strong>
                                <p className="text-xs text-muted" style={{ marginTop: 2 }}>
                                    {healthyCount}/{totalCount} services healthy
                                </p>
                            </div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                            <p className="text-xs text-muted">Last checked</p>
                            <p className="text-sm">
                                {new Date(data.checked_at).toLocaleTimeString('en-MY', {
                                    hour: '2-digit',
                                    minute: '2-digit',
                                    second: '2-digit',
                                })}
                            </p>
                        </div>
                    </div>

                    {/* Service grid */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: 12 }}>
                        {data.services.map((svc) => (
                            <ServiceCard key={svc.name} svc={svc} />
                        ))}
                    </div>
                </>
            )}

            {loading && !data && (
                <div className="flex justify-center" style={{ padding: 60 }}>
                    <div className="loader" />
                </div>
            )}
        </div>
    );
}
