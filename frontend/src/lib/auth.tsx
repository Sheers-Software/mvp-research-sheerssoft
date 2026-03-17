'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { apiGet, apiPost } from '@/lib/api';

interface Membership {
    id: string;
    tenant_id: string;
    tenant_name: string | null;
    role: string;
    accessible_property_ids: string[] | null;
}

export interface User {
    id: string;
    email: string;
    full_name: string;
    phone: string | null;
    is_superadmin: boolean;
    last_login_at: string | null;
    memberships: Membership[];
}

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (email: string, password: string) => Promise<void>;
    requestMagicLink: (email: string) => Promise<void>;
    logout: () => void;
    isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchUser = useCallback(async () => {
        try {
            const profile = await apiGet<User>('/auth/me');
            setUser(profile);
        } catch {
            setUser(null);
            localStorage.removeItem('nocturn_token');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        const token = localStorage.getItem('nocturn_token');
        if (token) {
            fetchUser();
        } else {
            setLoading(false);
        }
    }, [fetchUser]);

    const login = async (email: string, password: string) => {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const res = await fetch('/api/v1/auth/token', {
            method: 'POST',
            body: formData,
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
        if (!res.ok) throw new Error('Invalid credentials');
        const data = await res.json();
        localStorage.setItem('nocturn_token', data.access_token);
        await fetchUser();
    };

    const requestMagicLink = async (email: string) => {
        await apiPost('/auth/magic-link', { email });
    };

    const logout = () => {
        localStorage.removeItem('nocturn_token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, requestMagicLink, logout, isAdmin: user?.is_superadmin ?? false }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within AuthProvider');
    return ctx;
}
