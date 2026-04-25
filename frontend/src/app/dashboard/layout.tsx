'use client';

import { useAuth } from '@/lib/auth';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { apiGet } from '@/lib/api';
import Link from 'next/link';

const navItems = [
    { href: '/dashboard', label: 'Home' },
    { href: '/dashboard/conversations', label: 'Conversations' },
    { href: '/dashboard/leads', label: 'Leads' },
    { href: '/dashboard/analytics', label: 'Analytics' },
    { href: '/dashboard/insights', label: 'Insights' },
    { href: '/dashboard/settings', label: 'Settings' },
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
    const [sidebarOpen, setSidebarOpen] = useState(false);

    useEffect(() => {
        if (!loading && !user) {
            router.replace('/login');
        }
    }, [user, loading, router]);

    useEffect(() => {
        setSidebarOpen(false);
    }, [pathname]);

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
                <span className="mobile-header-brand">Nocturn AI</span>
                {property && <span className="text-sm" style={{ flexShrink: 0, color: 'var(--text3)' }}>{property.name}</span>}
            </header>

            {/* Sidebar overlay — closes sidebar when tapping outside on mobile */}
            <div
                className={`sidebar-overlay${sidebarOpen ? ' sidebar-open' : ''}`}
                onClick={() => setSidebarOpen(false)}
            />

            <aside className={`sidebar${sidebarOpen ? ' sidebar-open' : ''}`}>
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
                            onClick={() => setSidebarOpen(false)}
                        >
                            {item.label}
                        </Link>
                    ))}

                    {(user.role === 'owner' || user.role === 'admin') && (
                        <>
                            <span className="nav-section" style={{ marginTop: 8 }}>Management</span>
                            <Link href="/portal" className="nav-link" onClick={() => setSidebarOpen(false)}>
                                Property Portal
                            </Link>
                        </>
                    )}

                    {user.is_superadmin && (
                        <>
                            <span className="nav-section" style={{ marginTop: 8 }}>Admin</span>
                            <Link href="/admin" className="nav-link" onClick={() => setSidebarOpen(false)}>
                                Platform Admin
                            </Link>
                        </>
                    )}
                </nav>

                <div style={{ padding: '14px 20px', borderTop: '1px solid var(--border)' }}>
                    <div className="flex items-center justify-between" style={{ marginBottom: 8 }}>
                        <span className="text-sm" style={{ color: 'var(--text2)' }}>{user.full_name}</span>
                        <span className="badge badge-success">Staff</span>
                    </div>
                    <button className="btn btn-ghost btn-sm w-full" onClick={logout}>
                        Sign out
                    </button>
                </div>
            </aside>

            <main className="main-content">
                {/* Active announcements from SheersSoft */}
                {announcements
                    .filter((a) => !dismissedAnnIds.has(a.id))
                    .map((ann) => {
                        const isUrgent = ann.type === 'incident' || ann.type === 'maintenance';
                        const color = ann.type === 'incident' ? 'var(--red)' : ann.type === 'feature' ? 'var(--purple)' : 'var(--amber)';
                        return (
                            <div key={ann.id} style={{
                                background: `${color === 'var(--red)' ? 'rgba(226,75,74,0.08)' : color === 'var(--purple)' ? 'rgba(127,119,221,0.08)' : 'rgba(239,159,39,0.08)'}`,
                                border: `1px solid ${color === 'var(--red)' ? 'rgba(226,75,74,0.2)' : color === 'var(--purple)' ? 'rgba(127,119,221,0.2)' : 'rgba(239,159,39,0.2)'}`,
                                borderRadius: 8,
                                padding: '10px 14px',
                                marginBottom: 10,
                                display: 'flex',
                                alignItems: 'flex-start',
                                justifyContent: 'space-between',
                                gap: 12,
                            }}>
                                <div className="flex items-start gap-sm">
                                    <div>
                                        <strong style={{ fontSize: 12, color }}>{ann.title}</strong>
                                        <p style={{ fontSize: 11, color: 'var(--text2)', marginTop: 2 }}>{ann.body}</p>
                                    </div>
                                </div>
                                {!isUrgent && (
                                    <button
                                        onClick={() => setDismissedAnnIds((s) => new Set([...s, ann.id]))}
                                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text3)', fontSize: 16, padding: 0, flexShrink: 0, lineHeight: 1 }}
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
                        background: 'rgba(239, 159, 39, 0.08)',
                        border: '1px solid rgba(239, 159, 39, 0.22)',
                        borderRadius: 8,
                        padding: '10px 14px',
                        marginBottom: 18,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: 12,
                    }}>
                        <div className="flex items-center gap-sm">
                            <span style={{ fontSize: 13, color: 'var(--amber)' }}>
                                <strong>Scheduled maintenance:</strong>{' '}
                                {maintenance.message || 'Platform maintenance in progress.'}
                                {maintenance.eta && ` Expected completion: ${maintenance.eta}`}
                            </span>
                        </div>
                        <button
                            onClick={() => setBannerDismissed(true)}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text3)', fontSize: 16, padding: 0, lineHeight: 1 }}
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
