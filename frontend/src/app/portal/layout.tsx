'use client';

import { useAuth } from '@/lib/auth';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { apiGet } from '@/lib/api';
import Link from 'next/link';
import { TenantProvider, useTenant } from '@/lib/tenant-context';

const navItems = [
    { href: '/portal', label: 'Overview', icon: '🏠' },
    { href: '/portal/properties', label: 'Properties', icon: '🏨' },
    { href: '/portal/kb', label: 'Knowledge Base', icon: '📚' },
    { href: '/portal/team', label: 'Team', icon: '👥' },
    { href: '/portal/channels', label: 'Channels', icon: '📡' },
    { href: '/portal/billing', label: 'Billing', icon: '💳' },
    { href: '/portal/support', label: 'Support', icon: '🎧' },
];

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

function PortalLayoutInner({ children }: { children: React.ReactNode }) {
    const { user, loading, logout } = useAuth();
    const router = useRouter();
    const pathname = usePathname();
    const { tenantName } = useTenant();
    const [maintenance, setMaintenance] = useState<MaintenanceInfo | null>(null);
    const [bannerDismissed, setBannerDismissed] = useState(false);
    const [announcements, setAnnouncements] = useState<ActiveAnnouncement[]>([]);
    const [dismissedAnnIds, setDismissedAnnIds] = useState<Set<string>>(new Set());
    const [sidebarOpen, setSidebarOpen] = useState(false);

    useEffect(() => {
        if (!loading && !user) {
            router.replace('/login');
        }
        if (!loading && user && user.role === 'staff' && !user.is_superadmin) {
            router.replace('/dashboard');
        }
    }, [user, loading, router]);

    useEffect(() => {
        setSidebarOpen(false);
    }, [pathname]);

    useEffect(() => {
        const checkMaintenance = () => {
            apiGet<{ maintenance?: MaintenanceInfo }>('/system/info')
                .then((info) => {
                    if (info?.maintenance) {
                        setMaintenance(info.maintenance);
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

    const roleMap: Record<string, string> = { owner: 'Owner', admin: 'Admin', staff: 'Staff' };
    const tierLabel = user?.role ? (roleMap[user.role] ?? user.role) : null;

    return (
        <div className="layout">
            {/* Mobile top bar */}
            <header className="mobile-header">
                <button
                    className="hamburger"
                    onClick={() => setSidebarOpen((o) => !o)}
                    aria-label="Toggle navigation"
                >
                    <span />
                    <span />
                    <span />
                </button>
                <span className="mobile-header-brand">AI Concierge</span>
                {tenantName && <span className="text-sm text-muted" style={{ flexShrink: 0 }}>{tenantName}</span>}
            </header>

            {/* Sidebar overlay */}
            <div
                className={`sidebar-overlay${sidebarOpen ? ' sidebar-open' : ''}`}
                onClick={() => setSidebarOpen(false)}
            />

            <aside className={`sidebar${sidebarOpen ? ' sidebar-open' : ''}`}>
                <div className="sidebar-brand">
                    <h2>AI Concierge</h2>
                    <p>{tenantName || 'Property Portal'}</p>
                </div>

                <nav className="sidebar-nav">
                    <span className="nav-section">Portal</span>
                    {navItems.map((item) => (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`nav-link ${pathname === item.href ? 'active' : ''}`}
                            onClick={() => setSidebarOpen(false)}
                        >
                            <span className="nav-icon">{item.icon}</span>
                            {item.label}
                        </Link>
                    ))}

                    <span className="nav-section" style={{ marginTop: 16 }}>Operations</span>
                    <Link href="/dashboard" className="nav-link" onClick={() => setSidebarOpen(false)}>
                        <span className="nav-icon">📊</span>
                        Staff Dashboard
                    </Link>

                    {user.is_superadmin && (
                        <>
                            <span className="nav-section" style={{ marginTop: 16 }}>Admin</span>
                            <Link href="/admin" className="nav-link" onClick={() => setSidebarOpen(false)}>
                                <span className="nav-icon">⚙️</span>
                                Platform Admin
                            </Link>
                        </>
                    )}
                </nav>

                <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border-subtle)' }}>
                    <div className="flex items-center justify-between" style={{ marginBottom: 8 }}>
                        <span className="text-sm">{user.full_name}</span>
                        {tierLabel && <span className="badge badge-warning">{tierLabel}</span>}
                    </div>
                    <button className="btn btn-ghost btn-sm w-full" onClick={logout}>
                        Logout
                    </button>
                </div>
            </aside>

            <main className="main-content">
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

export default function PortalLayout({ children }: { children: React.ReactNode }) {
    return (
        <TenantProvider>
            <PortalLayoutInner>{children}</PortalLayoutInner>
        </TenantProvider>
    );
}
