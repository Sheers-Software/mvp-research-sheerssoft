'use client';

import { useAuth } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { useEffect, useState, useRef } from 'react';
import { apiGet } from '@/lib/api';

interface MilestoneItem {
    id: string;
    title: string;
    description: string;
    icon: string;
    points: number;
    completed: boolean;
    status: string;
    cta?: string | null;
    details?: Record<string, string>;
}

interface ChecklistData {
    completion_score: number;
    next_milestone: string | null;
    milestones: MilestoneItem[];
    channel_errors: Record<string, string> | null;
}

function ProgressRing({ score }: { score: number }) {
    const radius = 80;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (score / 100) * circumference;

    return (
        <div className="progress-ring">
            <svg width="200" height="200">
                <circle className="progress-ring__track" cx="100" cy="100" r={radius} />
                <circle
                    className="progress-ring__fill"
                    cx="100"
                    cy="100"
                    r={radius}
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                />
            </svg>
            <div className="progress-ring__text">
                <span className="progress-ring__score">{score}%</span>
                <span className="progress-ring__label">Ready Score</span>
            </div>
        </div>
    );
}

function Confetti() {
    const colors = ['#6366f1', '#a78bfa', '#34d399', '#fbbf24', '#f87171', '#60a5fa'];
    const pieces = Array.from({ length: 30 }, (_, i) => ({
        id: i,
        left: Math.random() * 100,
        color: colors[i % colors.length],
        delay: Math.random() * 2,
        size: 6 + Math.random() * 6,
    }));

    return (
        <>
            {pieces.map((p) => (
                <div
                    key={p.id}
                    className="confetti-piece"
                    style={{
                        left: `${p.left}%`,
                        backgroundColor: p.color,
                        animationDelay: `${p.delay}s`,
                        width: p.size,
                        height: p.size,
                    }}
                />
            ))}
        </>
    );
}

export default function DashboardPage() {
    const { user, loading, logout } = useAuth();
    const router = useRouter();
    const [checklist, setChecklist] = useState<ChecklistData | null>(null);
    const [loadingData, setLoadingData] = useState(true);
    const [showConfetti, setShowConfetti] = useState(false);
    const prevScoreRef = useRef(0);

    useEffect(() => {
        if (loading) return;
        if (!user) { router.replace('/login'); return; }

        const tenantId = user.memberships?.[0]?.tenant_id;
        if (!tenantId) { setLoadingData(false); return; }

        apiGet<ChecklistData>(`/onboarding/checklist/${tenantId}`)
            .then((data) => {
                if (data.completion_score > prevScoreRef.current && prevScoreRef.current > 0) {
                    setShowConfetti(true);
                    setTimeout(() => setShowConfetti(false), 3000);
                }
                prevScoreRef.current = data.completion_score;
                setChecklist(data);
            })
            .catch(() => { })
            .finally(() => setLoadingData(false));
    }, [user, loading, router]);

    if (loading || loadingData) {
        return (
            <div className="login-page">
                <div className="loader" />
            </div>
        );
    }

    if (!user) return null;

    const tenantName = user.memberships?.[0]?.tenant_name || 'Your Hotel';

    return (
        <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
            {showConfetti && <Confetti />}

            {/* Top bar */}
            <header style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '16px 32px', borderBottom: '1px solid var(--border-subtle)',
            }}>
                <div>
                    <h2 style={{ fontSize: 18, background: 'linear-gradient(135deg, var(--accent), #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                        Nocturn AI
                    </h2>
                    <span className="text-sm text-muted">{tenantName}</span>
                </div>
                <div className="flex items-center gap-md">
                    <span className="text-sm text-muted">{user.email}</span>
                    <button className="btn btn-ghost btn-sm" onClick={logout}>Logout</button>
                </div>
            </header>

            {/* Welcome Banner */}
            <div className="container" style={{ paddingTop: 40 }}>
                <div className="card animate-in" style={{ textAlign: 'center', padding: '40px 32px', marginBottom: 32, border: '1px solid rgba(99,102,241,0.15)', background: 'linear-gradient(135deg, rgba(99,102,241,0.05), rgba(168,85,247,0.03))' }}>
                    <h1 style={{ marginBottom: 8 }}>Welcome, {user.full_name} 👋</h1>
                    <p className="text-muted" style={{ maxWidth: 600, margin: '0 auto' }}>
                        Your AI concierge is being set up. Complete the milestones below to get the most out of Nocturn AI — your first quick win is just minutes away.
                    </p>
                </div>

                {checklist ? (
                    <div style={{ display: 'grid', gridTemplateColumns: '240px 1fr', gap: 32 }}>
                        {/* Progress Ring */}
                        <div className="card animate-slide-up" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: 32 }}>
                            <ProgressRing score={checklist.completion_score} />
                            <div style={{ marginTop: 16, textAlign: 'center' }}>
                                {checklist.next_milestone && (
                                    <p className="text-sm" style={{ marginTop: 8 }}>
                                        <span className="text-muted">Next: </span>
                                        <span className="text-accent">{checklist.next_milestone.replace(/_/g, ' ')}</span>
                                    </p>
                                )}
                            </div>
                        </div>

                        {/* Milestone Cards */}
                        <div className="flex flex-col gap-md">
                            {checklist.milestones.map((m, i) => (
                                <div
                                    key={m.id}
                                    className="card animate-slide-up"
                                    style={{
                                        animationDelay: `${i * 80}ms`,
                                        animationFillMode: 'backwards',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: 16,
                                        padding: '16px 20px',
                                        borderLeft: `3px solid ${m.completed ? 'var(--success)' : m.status === 'in_progress' ? 'var(--warning)' : 'var(--border-subtle)'}`,
                                        opacity: m.status === 'locked' ? 0.5 : 1,
                                    }}
                                >
                                    <span style={{ fontSize: 28, flexShrink: 0 }}>{m.icon}</span>
                                    <div style={{ flex: 1 }}>
                                        <div className="flex items-center gap-sm">
                                            <h4>{m.title}</h4>
                                            <span className={`badge ${m.completed ? 'badge-success' : m.status === 'in_progress' ? 'badge-warning' : 'badge-neutral'}`}>
                                                {m.completed ? '✓ Done' : m.status === 'in_progress' ? 'In Progress' : m.status === 'locked' ? 'Locked' : `+${m.points}%`}
                                            </span>
                                        </div>
                                        <p className="text-sm text-muted" style={{ marginTop: 2 }}>{m.description}</p>
                                        {m.details && (
                                            <div className="flex gap-sm" style={{ marginTop: 6 }}>
                                                {Object.entries(m.details).map(([k, v]) => (
                                                    <span key={k} className={`badge ${v === 'active' ? 'badge-success' : v === 'failed' ? 'badge-danger' : v === 'skipped' ? 'badge-neutral' : 'badge-warning'}`}>
                                                        {k}: {v}
                                                    </span>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                    {m.cta && !m.completed && (
                                        <button className="btn btn-primary btn-sm">{m.cta}</button>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="empty-state">
                        <div className="empty-icon">🏨</div>
                        <p>No onboarding data yet. Your account manager is setting things up.</p>
                    </div>
                )}

                {checklist?.channel_errors && Object.keys(checklist.channel_errors).length > 0 && (
                    <div className="card" style={{ marginTop: 24, borderColor: 'rgba(248,113,113,0.2)', background: 'var(--danger-bg)' }}>
                        <h4 style={{ color: 'var(--danger)', marginBottom: 8 }}>⚠️ Channel Setup Issues</h4>
                        {Object.entries(checklist.channel_errors).map(([channel, err]) => (
                            <p key={channel} className="text-sm" style={{ color: 'var(--danger)' }}>
                                <strong>{channel}:</strong> {err}
                            </p>
                        ))}
                        <p className="text-sm text-muted" style={{ marginTop: 8 }}>
                            Your account manager has been notified and will resolve this shortly.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
