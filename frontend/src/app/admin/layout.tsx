'use client';

import { useAuth } from '@/lib/auth';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect } from 'react';
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
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
    const { user, loading, logout } = useAuth();
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        if (!loading && !user) {
            router.replace('/login');
        }
    }, [user, loading, router]);

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
                    <p>SheersSoft Admin</p>
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
