'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';

export default function AuthCallbackPage() {
    const router = useRouter();
    const [error, setError] = useState('');

    useEffect(() => {
        async function handleCallback() {
            let supabaseAccessToken: string | null = null;

            // PKCE flow: Supabase sends ?code= as a query param
            const searchParams = new URLSearchParams(window.location.search);
            const code = searchParams.get('code');
            const queryError = searchParams.get('error_description');

            if (queryError) {
                setError(decodeURIComponent(queryError.replace(/\+/g, ' ')));
                return;
            }

            if (code) {
                // Exchange PKCE code for a Supabase session
                const { data, error: exchError } = await supabase.auth.exchangeCodeForSession(code);
                if (exchError || !data.session) {
                    setError(exchError?.message || 'Failed to exchange auth code. Please request a new magic link.');
                    return;
                }
                supabaseAccessToken = data.session.access_token;
            } else {
                // Implicit flow: Supabase sends #access_token= in hash
                const hash = window.location.hash;
                if (!hash) {
                    router.replace('/login');
                    return;
                }
                const hashParams = new URLSearchParams(hash.substring(1));
                const hashError = hashParams.get('error_description');
                if (hashError) {
                    setError(decodeURIComponent(hashError.replace(/\+/g, ' ')));
                    return;
                }
                supabaseAccessToken = hashParams.get('access_token');
                if (!supabaseAccessToken) {
                    router.replace('/login');
                    return;
                }
            }

            // Exchange Supabase token for our backend JWT
            try {
                const res = await fetch('/api/v1/auth/supabase-callback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ access_token: supabaseAccessToken }),
                });
                if (!res.ok) {
                    const d = await res.json();
                    throw new Error(d.detail || 'Auth failed');
                }
                const { access_token } = await res.json();
                localStorage.setItem('nocturn_token', access_token);

                const profileRes = await fetch('/api/v1/auth/me', {
                    headers: { Authorization: `Bearer ${access_token}` },
                });
                const user = await profileRes.json();
                router.replace(user.is_superadmin ? '/admin' : '/dashboard');
            } catch (err: any) {
                setError(err.message || 'Sign-in failed. Please request a new magic link.');
            }
        }

        handleCallback();
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
