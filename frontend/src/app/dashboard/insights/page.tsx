'use client';

import { useEffect, useState } from 'react';
import { apiGet } from '@/lib/api';
import Link from 'next/link';

interface TopicCount {
    topic: string;
    count: number;
}

interface SentimentSummary {
    positive: number;
    neutral: number;
    negative: number;
}

interface KBGap {
    topic: string;
    frequency: number;
}

interface InsightsData {
    generated_at: string;
    period_start: string;
    period_end: string;
    top_topics: TopicCount[];
    sentiment: SentimentSummary;
    kb_gaps: KBGap[];
    property_id: string;
}

function CSSBar({ value, max, color }: { value: number; max: number; color: string }) {
    const pct = max > 0 ? Math.round((value / max) * 100) : 0;
    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ flex: 1, height: 8, background: 'var(--border-subtle)', borderRadius: 4, overflow: 'hidden' }}>
                <div
                    style={{
                        height: '100%',
                        width: `${pct}%`,
                        background: color,
                        borderRadius: 4,
                        transition: 'width 0.4s ease',
                    }}
                />
            </div>
            <span className="text-xs text-muted" style={{ minWidth: 24, textAlign: 'right' }}>{value}</span>
        </div>
    );
}

export default function DashboardInsightsPage() {
    const [insights, setInsights] = useState<InsightsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [propertyId, setPropertyId] = useState<string | null>(null);

    useEffect(() => {
        apiGet<{ property_id: string }>('/analytics/dashboard')
            .then((data) => {
                if (data?.property_id) {
                    setPropertyId(data.property_id);
                    return apiGet<InsightsData>(`/properties/${data.property_id}/insights`);
                }
                throw new Error('No property');
            })
            .then((data) => setInsights(data))
            .catch((e: unknown) => {
                const msg = e instanceof Error ? e.message : '';
                if (msg !== 'No property') {
                    // Insights not available yet — not an error, just no data
                    setInsights(null);
                }
            })
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="flex justify-center" style={{ padding: 80 }}>
                <div className="loader" />
            </div>
        );
    }

    const maxTopicCount = insights?.top_topics?.length
        ? Math.max(...insights.top_topics.map((t) => t.count))
        : 1;

    const sentimentTotal = insights
        ? (insights.sentiment.positive + insights.sentiment.neutral + insights.sentiment.negative) || 1
        : 1;

    return (
        <div>
            <div className="flex items-center justify-between" style={{ marginBottom: 28 }}>
                <div>
                    <h1>AI Insights</h1>
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                        Monthly intelligence generated from your guest conversations
                    </p>
                </div>
            </div>

            {!insights ? (
                <div className="empty-state" style={{ marginTop: 60 }}>
                    <div className="empty-icon">💡</div>
                    <p>No insights yet</p>
                    <p className="text-sm text-muted" style={{ marginTop: 8, maxWidth: 380, lineHeight: 1.6 }}>
                        Insights are generated monthly once you have 30 or more conversations.
                        Check back next month — your AI will surface trending topics, sentiment
                        patterns, and knowledge base gaps automatically.
                    </p>
                </div>
            ) : (
                <div style={{ display: 'grid', gap: 24 }}>
                    {/* Generated date */}
                    <p className="text-sm text-muted">
                        Generated on: {new Date(insights.generated_at).toLocaleDateString('en-MY', {
                            day: 'numeric', month: 'long', year: 'numeric',
                        })}
                        {insights.period_start && (
                            <> · Period: {new Date(insights.period_start).toLocaleDateString()} – {new Date(insights.period_end).toLocaleDateString()}</>
                        )}
                    </p>

                    {/* Top Guest Topics */}
                    {insights.top_topics?.length > 0 && (
                        <div className="card animate-in" style={{ padding: 24 }}>
                            <h3 style={{ marginBottom: 4 }}>Top Guest Topics</h3>
                            <p className="text-sm text-muted" style={{ marginBottom: 20 }}>
                                What guests asked about most this month
                            </p>
                            <div style={{ display: 'grid', gap: 12 }}>
                                {insights.top_topics.slice(0, 10).map((topic, idx) => (
                                    <div key={idx}>
                                        <div className="flex items-center justify-between" style={{ marginBottom: 4 }}>
                                            <span className="text-sm" style={{ fontWeight: idx < 3 ? 600 : 400 }}>
                                                {idx < 3 && <span style={{ marginRight: 6 }}>{'🥇🥈🥉'[idx]}</span>}
                                                {topic.topic}
                                            </span>
                                        </div>
                                        <CSSBar
                                            value={topic.count}
                                            max={maxTopicCount}
                                            color={idx === 0 ? 'var(--accent)' : idx === 1 ? 'var(--info)' : 'var(--success)'}
                                        />
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Sentiment Summary */}
                    {insights.sentiment && (
                        <div className="card animate-in" style={{ padding: 24 }}>
                            <h3 style={{ marginBottom: 4 }}>Guest Sentiment</h3>
                            <p className="text-sm text-muted" style={{ marginBottom: 20 }}>
                                Overall tone of conversations this month
                            </p>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 20 }}>
                                {([
                                    { label: 'Positive', value: insights.sentiment.positive, color: 'var(--success)', icon: '😊' },
                                    { label: 'Neutral', value: insights.sentiment.neutral, color: 'var(--warning)', icon: '😐' },
                                    { label: 'Negative', value: insights.sentiment.negative, color: 'var(--danger)', icon: '😟' },
                                ] as const).map((s) => {
                                    const pct = Math.round((s.value / sentimentTotal) * 100);
                                    return (
                                        <div key={s.label} style={{ textAlign: 'center', padding: '16px 12px', background: 'var(--bg-secondary)', borderRadius: 8 }}>
                                            <div style={{ fontSize: 28, marginBottom: 6 }}>{s.icon}</div>
                                            <div style={{ fontSize: 22, fontWeight: 700, color: s.color }}>{pct}%</div>
                                            <div className="text-xs text-muted" style={{ marginTop: 2 }}>{s.label}</div>
                                            <div className="text-xs text-muted">{s.value} conversations</div>
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Stacked bar */}
                            <div style={{ height: 10, borderRadius: 6, overflow: 'hidden', display: 'flex', gap: 2 }}>
                                {insights.sentiment.positive > 0 && (
                                    <div style={{ flex: insights.sentiment.positive, background: 'var(--success)' }} />
                                )}
                                {insights.sentiment.neutral > 0 && (
                                    <div style={{ flex: insights.sentiment.neutral, background: 'var(--warning)' }} />
                                )}
                                {insights.sentiment.negative > 0 && (
                                    <div style={{ flex: insights.sentiment.negative, background: 'var(--danger)' }} />
                                )}
                            </div>
                        </div>
                    )}

                    {/* KB Gaps */}
                    {insights.kb_gaps?.length > 0 && (
                        <div className="card animate-in" style={{ padding: 24 }}>
                            <div className="flex items-center justify-between" style={{ marginBottom: 4 }}>
                                <h3>Knowledge Base Gaps</h3>
                                {propertyId && (
                                    <Link href={`/portal/kb/${propertyId}`} className="btn btn-primary btn-sm">
                                        + Add to KB
                                    </Link>
                                )}
                            </div>
                            <p className="text-sm text-muted" style={{ marginBottom: 20 }}>
                                Topics guests asked about that aren&apos;t covered in your knowledge base
                            </p>
                            <div style={{ display: 'grid', gap: 10 }}>
                                {insights.kb_gaps.map((gap, idx) => (
                                    <div
                                        key={idx}
                                        className="flex items-center justify-between"
                                        style={{ padding: '10px 14px', background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border-default)' }}
                                    >
                                        <div className="flex items-center gap-sm">
                                            <span style={{ color: 'var(--warning)', fontSize: 16 }}>⚠</span>
                                            <span className="text-sm">{gap.topic}</span>
                                        </div>
                                        <div className="flex items-center gap-sm">
                                            <span className="text-xs text-muted">{gap.frequency} guests asked</span>
                                            {propertyId && (
                                                <Link
                                                    href={`/portal/kb/${propertyId}`}
                                                    className="text-xs"
                                                    style={{ color: 'var(--accent)', textDecoration: 'none' }}
                                                >
                                                    Add →
                                                </Link>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
