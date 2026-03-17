'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AuthCallbackPage() {
    const router = useRouter();
    const [error, setError] = useState('');

    useEffect(() => {
        const hash = window.location.hash;
        if (!hash) {
            router.replace('/login');
            return;
        }

        const params = new URLSearchParams(hash.substring(1));
        const accessToken = params.get('access_token');
        const errorDesc = params.get('error_description');

        if (errorDesc) {
            setError(decodeURIComponent(errorDesc.replace(/\+/g, ' ')));
            return;
        }

        if (!accessToken) {
            router.replace('/login');
            return;
        }

        // Exchange the Supabase token for a backend JWT
        fetch('/api/v1/auth/supabase-callback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ access_token: accessToken }),
        })
            .then((r) => {
                if (!r.ok) return r.json().then((d) => Promise.reject(d.detail || 'Auth failed'));
                return r.json();
            })
            .then((data) => {
                localStorage.setItem('nocturn_token', data.access_token);
                // Determine redirect target from the backend JWT's profile
                return fetch('/api/v1/auth/me', {
                    headers: { Authorization: `Bearer ${data.access_token}` },
                }).then((r) => r.json());
            })
            .then((user) => {
                router.replace(user.is_superadmin ? '/admin' : '/dashboard');
            })
            .catch((msg) => {
                setError(typeof msg === 'string' ? msg : 'Sign-in failed. Please request a new magic link.');
            });
    }, [router]);

    if (error) {
        return (
            <div className="login-page">
                <div className="login-card">
                    <div className="login-logo">
                        <h1>Nocturn AI</h1>
                    </div>
                    <div style={{ color: 'var(--danger)', marginBottom: 16 }}>{error}</div>
                    <a href="/login" className="btn btn-primary w-full" style={{ textAlign: 'center' }}>
                        Back to Login
                    </a>
                </div>
            </div>
        );
    }

    return (
        <div className="login-page">
            <div className="loader" />
        </div>
    );
}
