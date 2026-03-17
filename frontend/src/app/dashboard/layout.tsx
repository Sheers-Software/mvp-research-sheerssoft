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

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const { user, loading, logout } = useAuth();
    const router = useRouter();
    const pathname = usePathname();
    const [property, setProperty] = useState<PropertyInfo | null>(null);

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
            .catch(() => {
                // Try to get from the first property in the user's scope
            });
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
                {children}
            </main>
        </div>
    );
}
