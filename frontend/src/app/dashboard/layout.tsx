'use client';

import { useAuth } from '@/lib/auth';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { apiGet } from '@/lib/api';
import Link from 'next/link';

const navItems = [
    { href: '/dashboard', label: 'Home', icon: '🏠' },
    { href: '/dashboard/conversations', label: 'Conversations', icon: '💬' },
    { href: '/dashboard/leads', label: 'Leads', icon: '🎯' },
    { href: '/dashboard/analytics', label: 'Analytics', icon: '📊' },
    { href: '/dashboard/settings', label: 'Settings', icon: '⚙️' },
];

interface PropertyInfo {
    id: string;
    name: string;
}

interface MaintenanceInfo {
    enabled: boolean;
    message: string;
    eta: string | null;
}

interface ActiveAnnouncement {
    id: string;
    type: 'maintenance' | 'incident' | 'feature' | 'billing';
    title: string;
    body: string;
    created_at: string;
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const { user, loading, logout } = useAuth();
    const router = useRouter();
    const pathname = usePathname();
    const [property, setProperty] = useState<PropertyInfo | null>(null);
    const [maintenance, setMaintenance] = useState<MaintenanceInfo | null>(null);
    const [bannerDismissed, setBannerDismissed] = useState(false);
    const [announcements, setAnnouncements] = useState<ActiveAnnouncement[]>([]);
    const [dismissedAnnIds, setDismissedAnnIds] = useState<Set<string>>(new Set());

    useEffect(() => {
        if (!loading && !user) {
            router.replace('/login');
        }
    }, [user, loading, router]);

    useEffect(() => {
        // Fetch the user's primary property for display and API calls
        apiGet<any>('/analytics/dashboard')
            .then((data) => {
                if (data?.property_id && data?.property_name) {
                    setProperty({ id: data.property_id, name: data.property_name });
                }
            })
            .catch(() => {});
    }, []);

    useEffect(() => {
        // Poll for maintenance mode — check on load and every 60s
        const checkMaintenance = () => {
            apiGet<any>('/system/info')
                .then((info) => {
                    if (info?.maintenance) {
                        setMaintenance(info.maintenance);
                        // Re-show banner if maintenance just became active
                        if (info.maintenance.enabled) setBannerDismissed(false);
                    }
                })
                .catch(() => {});
        };
        checkMaintenance();
        const interval = setInterval(checkMaintenance, 60000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        // Fetch active announcements on load (no polling needed — staff refresh is sufficient)
        apiGet<ActiveAnnouncement[]>('/announcements/active')
            .then((data) => setAnnouncements(data || []))
            .catch(() => {});
    }, []);

    if (loading) {
        return (
            <div className="login-page">
                <div className="loader" />
            </div>
        );
    }

    if (!user) return null;

    return (
        <div className="layout">
            <aside className="sidebar">
                <div className="sidebar-brand">
                    <h2>Nocturn AI</h2>
                    <p>{property?.name || 'Hotel Dashboard'}</p>
                </div>

                <nav className="sidebar-nav">
                    <span className="nav-section">Dashboard</span>
                    {navItems.map((item) => (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`nav-link ${pathname === item.href ? 'active' : ''}`}
                        >
                            <span className="nav-icon">{item.icon}</span>
                            {item.label}
                        </Link>
                    ))}

                    {user.is_superadmin && (
                        <>
                            <span className="nav-section" style={{ marginTop: 16 }}>Admin</span>
                            <Link href="/admin" className="nav-link">
                                <span className="nav-icon">⚙️</span>
                                Platform Admin
                            </Link>
                        </>
                    )}
                </nav>

                <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border-subtle)' }}>
                    <div className="flex items-center justify-between" style={{ marginBottom: 8 }}>
                        <span className="text-sm">{user.full_name}</span>
                        <span className="badge badge-success">Staff</span>
                    </div>
                    <button className="btn btn-ghost btn-sm w-full" onClick={logout}>
                        Logout
                    </button>
                </div>
            </aside>

            <main className="main-content">
                {/* Active announcements from SheersSoft */}
                {announcements
                    .filter((a) => !dismissedAnnIds.has(a.id))
                    .map((ann) => {
                        const isUrgent = ann.type === 'incident' || ann.type === 'maintenance';
                        const color = ann.type === 'incident' ? 'var(--danger)' : ann.type === 'feature' ? 'var(--info)' : 'var(--warning)';
                        const icon = ann.type === 'incident' ? '🚨' : ann.type === 'feature' ? '✨' : ann.type === 'billing' ? '💳' : '🔧';
                        return (
                            <div key={ann.id} style={{
                                background: `${color}12`,
                                border: `1px solid ${color}35`,
                                borderRadius: 8,
                                padding: '10px 16px',
                                marginBottom: 12,
                                display: 'flex',
                                alignItems: 'flex-start',
                                justifyContent: 'space-between',
                                gap: 12,
                            }}>
                                <div className="flex items-start gap-sm">
                                    <span>{icon}</span>
                                    <div>
                                        <strong style={{ fontSize: 13, color }}>{ann.title}</strong>
                                        <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>{ann.body}</p>
                                    </div>
                                </div>
                                {!isUrgent && (
                                    <button
                                        onClick={() => setDismissedAnnIds((s) => new Set([...s, ann.id]))}
                                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', fontSize: 16, padding: 0, flexShrink: 0 }}
                                    >
                                        ×
                                    </button>
                                )}
                            </div>
                        );
                    })}

                {/* Maintenance mode banner */}
                {maintenance?.enabled && !bannerDismissed && (
                    <div style={{
                        background: 'rgba(245, 158, 11, 0.12)',
                        border: '1px solid rgba(245, 158, 11, 0.35)',
                        borderRadius: 8,
                        padding: '10px 16px',
                        marginBottom: 20,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: 12,
                    }}>
                        <div className="flex items-center gap-sm">
                            <span>🔧</span>
                            <span style={{ fontSize: 13, color: 'var(--warning)' }}>
                                <strong>Scheduled maintenance:</strong>{' '}
                                {maintenance.message || 'Platform maintenance in progress.'}
                                {maintenance.eta && ` Expected completion: ${maintenance.eta}`}
                            </span>
                        </div>
                        <button
                            onClick={() => setBannerDismissed(true)}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', fontSize: 16, padding: 0 }}
                        >
                            ×
                        </button>
                    </div>
                )}
                {children}
            </main>
        </div>
    );
}
