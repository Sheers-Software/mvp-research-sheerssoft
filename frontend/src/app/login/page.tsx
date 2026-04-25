'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import PublicNav from '@/components/PublicNav';

export default function LoginPage() {
    const { login, requestMagicLink, user, loading } = useAuth();
    const router = useRouter();
    const [mode, setMode] = useState<'magic' | 'legacy'>('magic');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [sent, setSent] = useState(false);
    const [error, setError] = useState(() => {
        if (typeof window !== 'undefined') {
            const params = new URLSearchParams(window.location.search);
            if (params.get('error') === 'no_org') {
                return "Your account was created but you haven't been added to any organization yet. Contact your admin.";
            }
        }
        return '';
    });
    const [submitting, setSubmitting] = useState(false);

    // Redirect if already logged in
    if (!loading && user) {
        router.replace(user.is_superadmin ? '/admin' : '/dashboard');
        return null;
    }

    const handleMagicLink = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSubmitting(true);
        try {
            await requestMagicLink(email);
            setSent(true);
        } catch (err: any) {
            setError(err.message || 'Failed to send magic link');
        } finally {
            setSubmitting(false);
        }
    };

    const handleLegacyLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSubmitting(true);
        try {
            await login(email, password);
            router.push('/admin');
        } catch (err: any) {
            setError(err.message || 'Login failed');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <>
        <PublicNav />
        <div className="login-page">
            <div className="login-card">
                <div className="login-logo">
                    <h1>Nocturn AI</h1>
                    <p>Hotel Concierge Intelligence</p>
                </div>

                {sent ? (
                    <div className="login-sent animate-in">
                        <div className="email-icon">✉️</div>
                        <h3>Check your inbox</h3>
                        <p>We sent a magic link to <strong>{email}</strong></p>
                        <p style={{ marginTop: 8 }}>Click the link in the email to sign in — no password needed.</p>
                        <button
                            className="btn btn-ghost"
                            onClick={() => { setSent(false); setEmail(''); }}
                            style={{ marginTop: 20 }}
                        >
                            ← Try a different email
                        </button>
                    </div>
                ) : (
                    <>
                        {mode === 'magic' ? (
                            <form onSubmit={handleMagicLink} className="flex flex-col gap-md">
                                <div className="input-group">
                                    <label htmlFor="email">Email address</label>
                                    <input
                                        id="email"
                                        type="email"
                                        className="input"
                                        placeholder="you@yourhotel.com"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        autoFocus
                                    />
                                </div>

                                {error && <p style={{ color: 'var(--danger)', fontSize: 13 }}>{error}</p>}

                                <button
                                    type="submit"
                                    className="btn btn-primary btn-lg w-full"
                                    disabled={submitting || !email}
                                >
                                    {submitting ? (
                                        <><span className="loader" style={{ width: 18, height: 18 }} /> Sending...</>
                                    ) : (
                                        '✨ Send Magic Link'
                                    )}
                                </button>

                                <div style={{ textAlign: 'center', marginTop: 8 }}>
                                    <button
                                        type="button"
                                        className="btn btn-ghost text-sm"
                                        onClick={() => setMode('legacy')}
                                    >
                                        SheersSoft Admin Login →
                                    </button>
                                </div>
                            </form>
                        ) : (
                            <form onSubmit={handleLegacyLogin} className="flex flex-col gap-md">
                                <div className="input-group">
                                    <label htmlFor="legacy-user">Username</label>
                                    <input
                                        id="legacy-user"
                                        type="text"
                                        className="input"
                                        placeholder="admin"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        autoFocus
                                    />
                                </div>

                                <div className="input-group">
                                    <label htmlFor="legacy-pass">Password</label>
                                    <input
                                        id="legacy-pass"
                                        type="password"
                                        className="input"
                                        placeholder="••••••••"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                    />
                                </div>

                                {error && <p style={{ color: 'var(--danger)', fontSize: 13 }}>{error}</p>}

                                <button
                                    type="submit"
                                    className="btn btn-primary btn-lg w-full"
                                    disabled={submitting}
                                >
                                    {submitting ? (
                                        <><span className="loader" style={{ width: 18, height: 18 }} /> Signing in...</>
                                    ) : (
                                        '🔐 Sign In'
                                    )}
                                </button>

                                <div style={{ textAlign: 'center', marginTop: 8 }}>
                                    <button
                                        type="button"
                                        className="btn btn-ghost text-sm"
                                        onClick={() => setMode('magic')}
                                    >
                                        ← Back to Magic Link
                                    </button>
                                </div>
                            </form>
                        )}
                    </>
                )}

                <p style={{ textAlign: 'center', fontSize: 12, color: 'var(--text-muted)', marginTop: 24 }}>
                    Powered by SheersSoft · <a href="https://ai.sheerssoft.com" target="_blank" rel="noopener" style={{ color: 'var(--text-muted)' }}>ai.sheerssoft.com</a>
                </p>
            </div>
        </div>
        </>
    );
}
