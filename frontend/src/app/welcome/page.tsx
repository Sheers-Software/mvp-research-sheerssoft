'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiPost } from '@/lib/api';

export default function WelcomePage() {
    const router = useRouter();
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleGenerate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!url.trim()) return;

        setLoading(true);
        setError('');

        try {
            const result = await apiPost<{
                tenant_id: string;
                business_id: string;
                business_name: string;
            }>('/onboarding/scrape-url', { url: url.trim() });

            // On success, redirect to the portal/dashboard
            router.push(`/portal?business_id=${result.business_id}`);
        } catch (err: any) {
            setError(err.message || 'Failed to generate AI. Please check the URL and try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #09090b 0%, #18181b 100%)',
            color: 'white',
            fontFamily: 'Inter, sans-serif'
        }}>
            <div style={{
                width: '100%',
                maxWidth: '600px',
                padding: '40px',
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: '24px',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
                textAlign: 'center'
            }}>
                <div style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '64px',
                    height: '64px',
                    borderRadius: '20px',
                    background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
                    marginBottom: '24px',
                    fontSize: '28px'
                }}>
                    ✨
                </div>
                
                <h1 style={{
                    fontSize: '36px',
                    fontWeight: 800,
                    marginBottom: '16px',
                    background: 'linear-gradient(to right, #fff, #a1a1aa)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent'
                }}>
                    Instantly create your AI Concierge.
                </h1>
                
                <p style={{
                    fontSize: '16px',
                    color: '#a1a1aa',
                    marginBottom: '40px',
                    lineHeight: 1.6
                }}>
                    Just paste your business website URL, and we'll train a custom AI assistant on your services, pricing, and FAQs in seconds. No coding required.
                </p>

                <form onSubmit={handleGenerate} style={{ position: 'relative' }}>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        background: 'rgba(0, 0, 0, 0.5)',
                        border: '1px solid rgba(255, 255, 255, 0.15)',
                        borderRadius: '16px',
                        padding: '8px',
                        transition: 'all 0.3s ease',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
                    }}>
                        <div style={{ padding: '0 16px', color: '#a1a1aa' }}>
                            🌐
                        </div>
                        <input
                            type="text"
                            placeholder="https://yourbusiness.com"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            disabled={loading}
                            style={{
                                flex: 1,
                                background: 'transparent',
                                border: 'none',
                                color: 'white',
                                fontSize: '16px',
                                outline: 'none',
                                padding: '12px 0'
                            }}
                        />
                        <button
                            type="submit"
                            disabled={loading || !url.trim()}
                            style={{
                                background: url.trim() ? 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)' : 'rgba(255, 255, 255, 0.1)',
                                color: url.trim() ? 'white' : '#71717a',
                                border: 'none',
                                padding: '12px 24px',
                                borderRadius: '12px',
                                fontSize: '15px',
                                fontWeight: 600,
                                cursor: url.trim() && !loading ? 'pointer' : 'not-allowed',
                                transition: 'all 0.2s',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px'
                            }}
                        >
                            {loading ? (
                                <>
                                    <div style={{
                                        width: '16px',
                                        height: '16px',
                                        border: '2px solid rgba(255,255,255,0.3)',
                                        borderTopColor: '#fff',
                                        borderRadius: '50%',
                                        animation: 'spin 1s linear infinite'
                                    }} />
                                    Scanning...
                                </>
                            ) : (
                                'Generate AI'
                            )}
                        </button>
                    </div>
                    {error && (
                        <div style={{
                            marginTop: '16px',
                            color: '#ef4444',
                            fontSize: '14px',
                            background: 'rgba(239, 68, 68, 0.1)',
                            padding: '12px',
                            borderRadius: '8px'
                        }}>
                            {error}
                        </div>
                    )}
                </form>

                <div style={{
                    marginTop: '40px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '24px',
                    color: '#71717a',
                    fontSize: '13px'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ color: '#10b981' }}>✓</span> Reads entire site
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ color: '#10b981' }}>✓</span> Extracts FAQs
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ color: '#10b981' }}>✓</span> Ready in 10s
                    </div>
                </div>
            </div>
            <style dangerouslySetInnerHTML={{__html: `
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
                input::placeholder { color: #52525b; }
                input:focus { outline: none; }
            `}} />
        </div>
    );
}
