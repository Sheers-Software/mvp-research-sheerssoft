'use client';

import { useAuth } from '@/lib/auth';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';

const navItems = [
    { href: '/admin', label: 'Overview', icon: '📊' },
    { href: '/admin/onboarding', label: 'New Client', icon: '➕' },
    { href: '/admin/pipeline', label: 'Pipeline', icon: '🔄' },
    { href: '/admin/tenants', label: 'Tenants', icon: '🏨' },
    { href: '/admin/tickets', label: 'Support', icon: '🎫' },
    { href: '/admin/applications', label: 'Applications', icon: '📥' },
    { href: '/admin/kb-ingestion', label: 'KB Ingestion', icon: '📚' },
    { href: '/admin/system', label: 'System', icon: '⚙️' },
    { href: '/admin/announcements', label: 'Announcements', icon: '📢' },
    { href: '/admin/health', label: 'Service Health', icon: '🩺' },
    { href: '/admin/tools/revenue-audit', label: 'Revenue Audit', icon: '💰' },
    { href: '/admin/shadow-pilots', label: 'Shadow Pilots', icon: '👥' },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
    const { user, loading, logout } = useAuth();
    const router = useRouter();
    const pathname = usePathname();
    const [sidebarOpen, setSidebarOpen] = useState(false);

    useEffect(() => {
        if (!loading && !user) {
            router.replace('/login');
        }
    }, [user, loading, router]);

    useEffect(() => {
        setSidebarOpen(false);
    }, [pathname]);

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
                <span className="text-sm text-muted" style={{ flexShrink: 0 }}>Admin</span>
            </header>

            {/* Sidebar overlay */}
            <div
                className={`sidebar-overlay${sidebarOpen ? ' sidebar-open' : ''}`}
                onClick={() => setSidebarOpen(false)}
            />

            <aside className={`sidebar${sidebarOpen ? ' sidebar-open' : ''}`}>
                <div className="sidebar-brand">
                    <h2>Nocturn AI</h2>
                    <p>SheersSoft Admin</p>
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
                            <span className="nav-icon">{item.icon}</span>
                            {item.label}
                        </Link>
                    ))}
                </nav>

                <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border-subtle)' }}>
                    <div className="flex items-center justify-between" style={{ marginBottom: 8 }}>
                        <span className="text-sm">{user.full_name}</span>
                        <span className="badge badge-info">{user.is_superadmin ? 'Admin' : 'Staff'}</span>
                    </div>
                    <button className="btn btn-ghost btn-sm w-full" onClick={logout}>
                        Logout
                    </button>
                </div>
            </aside>

            <main className="main-content">
                {children}
            </main>
        </div>
    );
}
