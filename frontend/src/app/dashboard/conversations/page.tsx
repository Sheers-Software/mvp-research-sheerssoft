'use client';

import { useEffect, useState } from 'react';
import { apiGet, apiPost } from '@/lib/api';

interface ConversationItem {
    id: string;
    channel: string;
    guest_name: string | null;
    guest_identifier: string;
    status: string;
    ai_mode: string;
    is_after_hours: boolean;
    message_count: number;
    started_at: string;
    last_message_at: string | null;
    has_lead: boolean;
    lead_intent: string | null;
}

interface Message {
    id: string;
    role: string;
    content: string;
    sent_at: string;
}

interface ConversationDetail {
    id: string;
    channel: string;
    guest_name: string | null;
    guest_identifier: string;
    status: string;
    ai_mode: string;
    is_after_hours: boolean;
    message_count: number;
    started_at: string;
    messages: Message[];
    lead: {
        id: string;
        guest_name: string | null;
        guest_email: string | null;
        guest_phone: string | null;
        intent: string | null;
        status: string;
        estimated_value: number | null;
    } | null;
}

const channelBadge: Record<string, { class: string; icon: string }> = {
    whatsapp: { class: 'badge-success', icon: '💬' },
    web: { class: 'badge-info', icon: '🌐' },
    email: { class: 'badge-warning', icon: '📧' },
};

const statusBadge: Record<string, string> = {
    active: 'badge-success',
    resolved: 'badge-neutral',
    handed_off: 'badge-warning',
    needs_attention: 'badge-danger',
};

function TimeAgo({ date }: { date: string | null }) {
    if (!date) return <span className="text-muted">—</span>;
    const diff = Date.now() - new Date(date).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return <span className="text-muted">Just now</span>;
    if (mins < 60) return <span className="text-muted">{mins}m ago</span>;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return <span className="text-muted">{hrs}h ago</span>;
    const days = Math.floor(hrs / 24);
    return <span className="text-muted">{days}d ago</span>;
}

export default function ConversationsPage() {
    const [conversations, setConversations] = useState<ConversationItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('');
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [detail, setDetail] = useState<ConversationDetail | null>(null);
    const [detailLoading, setDetailLoading] = useState(false);
    const [propertyId, setPropertyId] = useState<string | null>(null);
    const [actionLoading, setActionLoading] = useState('');
    const [replyText, setReplyText] = useState('');
    const [replySending, setReplySending] = useState(false);
    const [draftEn, setDraftEn] = useState('');
    const [draftBm, setDraftBm] = useState('');
    const [draftLang, setDraftLang] = useState<'en' | 'bm'>('en');
    const [draftLoading, setDraftLoading] = useState(false);
    const [draftCopied, setDraftCopied] = useState(false);
    const [paymentLinkAmount, setPaymentLinkAmount] = useState('');
    const [paymentLinkDesc, setPaymentLinkDesc] = useState('');
    const [generatingLink, setGeneratingLink] = useState(false);
    const [paymentLinkUrl, setPaymentLinkUrl] = useState('');
    const [error, setError] = useState('');

    // Resolve property ID from dashboard stats
    useEffect(() => {
        apiGet<any>('/analytics/dashboard')
            .then((data) => {
                if (data?.property_id) {
                    setPropertyId(data.property_id);
                }
            })
            .catch(() => { });
    }, []);

    useEffect(() => {
        if (!propertyId) return;
        setLoading(true);
        const url = filter
            ? `/properties/${propertyId}/conversations?status=${filter}`
            : `/properties/${propertyId}/conversations`;
        apiGet<ConversationItem[]>(url)
            .then(setConversations)
            .catch(() => { })
            .finally(() => setLoading(false));
    }, [propertyId, filter]);

    const handleGeneratePaymentLink = async () => {
        if (!detail?.lead?.id || !paymentLinkAmount) return;
        setGeneratingLink(true);
        try {
            const result = await apiPost<{ payment_link_url: string }>(
                `/leads/${detail.lead.id}/payment-link`,
                {
                    amount_rm: parseFloat(paymentLinkAmount),
                    description: paymentLinkDesc || 'Direct booking',
                }
            );
            setPaymentLinkUrl(result.payment_link_url);
        } catch (e: unknown) {
            setError((e instanceof Error ? e.message : String(e)) || 'Failed to generate payment link');
        } finally {
            setGeneratingLink(false);
        }
    };

    const generateDraft = async (id: string) => {
        setDraftLoading(true);
        setDraftEn('');
        setDraftBm('');
        setDraftCopied(false);
        try {
            const data = await apiPost<{ draft_en: string; draft_bm: string }>(
                `/conversations/${id}/draft-reply`,
                { language: 'both' }
            );
            setDraftEn(data.draft_en || '');
            setDraftBm(data.draft_bm || '');
        } catch { } finally {
            setDraftLoading(false);
        }
    };

    const copyDraft = () => {
        const text = draftLang === 'en' ? draftEn : draftBm;
        setReplyText(text);
        setDraftCopied(true);
        setTimeout(() => setDraftCopied(false), 2000);
    };

    const openDetail = async (id: string) => {
        setSelectedId(id);
        setDetailLoading(true);
        setDraftEn('');
        setDraftBm('');
        setPaymentLinkUrl('');
        setPaymentLinkAmount('');
        setPaymentLinkDesc('');
        try {
            const data = await apiGet<ConversationDetail>(`/conversations/${id}`);
            setDetail(data);
        } catch {
            setDetail(null);
        } finally {
            setDetailLoading(false);
        }
    };

    const sendStaffReply = async (id: string) => {
        const content = replyText.trim();
        if (!content) return;
        setReplySending(true);
        try {
            await apiPost(`/conversations/${id}/reply`, { content });
            setReplyText('');
            const updatedDetail = await apiGet<ConversationDetail>(`/conversations/${id}`);
            setDetail(updatedDetail);
        } catch { } finally {
            setReplySending(false);
        }
    };

    const doAction = async (id: string, action: 'resolve' | 'handoff' | 'takeover') => {
        setActionLoading(action);
        try {
            await apiPost(`/conversations/${id}/${action}`);
            // Refresh the conversation detail and list
            if (propertyId) {
                const url = filter
                    ? `/properties/${propertyId}/conversations?status=${filter}`
                    : `/properties/${propertyId}/conversations`;
                const updated = await apiGet<ConversationItem[]>(url);
                setConversations(updated);
            }
            if (selectedId === id) {
                const updatedDetail = await apiGet<ConversationDetail>(`/conversations/${id}`);
                setDetail(updatedDetail);
            }
        } catch { } finally {
            setActionLoading('');
        }
    };

    return (
        <div>
            <div className="flex items-center justify-between" style={{ marginBottom: 32 }}>
                <div>
                    <h1>Conversations</h1>
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                        AI-handled guest inquiries across all channels
                    </p>
                </div>
                <div className="flex gap-sm">
                    {['', 'active', 'handed_off', 'resolved'].map((f) => (
                        <button
                            key={f}
                            className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-ghost'}`}
                            onClick={() => { setFilter(f); }}
                        >
                            {f === '' ? 'All' : f === 'handed_off' ? 'Handoff' : f.charAt(0).toUpperCase() + f.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: selectedId ? '1fr 1fr' : '1fr', gap: 24 }}>
                {/* Conversation List */}
                <div>
                    {loading ? (
                        <div className="flex justify-center" style={{ padding: 60 }}><div className="loader" /></div>
                    ) : conversations.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-icon">💬</div>
                            <p>No {filter || ''} conversations yet</p>
                            <p className="text-sm text-muted" style={{ marginTop: 8 }}>
                                Conversations will appear here when guests message via WhatsApp, Web, or Email.
                            </p>
                        </div>
                    ) : (
                        <div className="flex flex-col gap-sm animate-in">
                            {conversations.map((c, i) => (
                                <div
                                    key={c.id}
                                    className="card animate-slide-up"
                                    style={{
                                        padding: '14px 18px',
                                        cursor: 'pointer',
                                        animationDelay: `${i * 40}ms`,
                                        animationFillMode: 'backwards',
                                        border: selectedId === c.id ? '2px solid var(--accent)' : undefined,
                                    }}
                                    onClick={() => openDetail(c.id)}
                                >
                                    <div className="flex items-center justify-between" style={{ marginBottom: 6 }}>
                                        <div className="flex items-center gap-sm">
                                            <span>{channelBadge[c.channel]?.icon || '💬'}</span>
                                            <strong style={{ fontSize: 14 }}>
                                                {c.guest_name || c.guest_identifier}
                                            </strong>
                                        </div>
                                        <TimeAgo date={c.last_message_at || c.started_at} />
                                    </div>
                                    <div className="flex items-center gap-sm">
                                        <span className={`badge ${channelBadge[c.channel]?.class || 'badge-neutral'}`}>
                                            {c.channel}
                                        </span>
                                        <span className={`badge ${statusBadge[c.status] || 'badge-neutral'}`}>
                                            {c.status}
                                        </span>
                                        {c.is_after_hours && <span className="badge badge-warning">🌙 After Hours</span>}
                                        {c.has_lead && <span className="badge badge-success">🎯 Lead</span>}
                                        <span className="text-sm text-muted" style={{ marginLeft: 'auto' }}>
                                            {c.message_count} msgs
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Conversation Detail Panel */}
                {selectedId && (
                    <div className="card animate-in" style={{ padding: 0, position: 'sticky', top: 20, maxHeight: 'calc(100vh - 120px)', overflow: 'auto' }}>
                        {detailLoading ? (
                            <div className="flex justify-center" style={{ padding: 60 }}><div className="loader" /></div>
                        ) : detail ? (
                            <>
                                {/* Header */}
                                <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
                                    <div className="flex items-center justify-between" style={{ marginBottom: 8 }}>
                                        <h3 style={{ fontSize: 16, margin: 0 }}>
                                            {detail.guest_name || detail.guest_identifier}
                                        </h3>
                                        <button className="btn btn-ghost btn-sm" onClick={() => { setSelectedId(null); setDetail(null); }}>✕</button>
                                    </div>
                                    <div className="flex items-center gap-sm">
                                        <span className={`badge ${channelBadge[detail.channel]?.class || 'badge-neutral'}`}>{detail.channel}</span>
                                        <span className={`badge ${statusBadge[detail.status] || 'badge-neutral'}`}>{detail.status}</span>
                                        <span className="text-sm text-muted">{detail.message_count} messages</span>
                                    </div>
                                </div>

                                {/* Lead Info */}
                                {detail.lead && (
                                    <div style={{ padding: '12px 20px', background: 'rgba(var(--success-rgb, 34,197,94), 0.08)', borderBottom: '1px solid var(--border-subtle)' }}>
                                        <div className="flex items-center gap-sm" style={{ marginBottom: 4 }}>
                                            <span>🎯</span>
                                            <strong className="text-sm">Lead Captured</strong>
                                        </div>
                                        <div className="text-sm text-muted">
                                            {detail.lead.guest_name && <div>Name: {detail.lead.guest_name}</div>}
                                            {detail.lead.guest_email && <div>Email: {detail.lead.guest_email}</div>}
                                            {detail.lead.guest_phone && <div>Phone: {detail.lead.guest_phone}</div>}
                                            {detail.lead.intent && <div>Intent: <span className="badge badge-info">{detail.lead.intent}</span></div>}
                                            {detail.lead.estimated_value && <div>Est. Value: RM {detail.lead.estimated_value.toLocaleString()}</div>}
                                        </div>
                                    </div>
                                )}

                                {/* Messages */}
                                <div style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 12 }}>
                                    {detail.messages.map((m) => (
                                        <div
                                            key={m.id}
                                            style={{
                                                padding: '10px 14px',
                                                borderRadius: 12,
                                                maxWidth: '85%',
                                                alignSelf: m.role === 'guest' ? 'flex-start' : 'flex-end',
                                                background: m.role === 'guest'
                                                    ? 'var(--surface-elevated)'
                                                    : m.role === 'staff'
                                                    ? 'linear-gradient(135deg, hsl(145, 55%, 40%), hsl(145, 55%, 32%))'
                                                    : 'linear-gradient(135deg, var(--accent), hsl(260, 60%, 55%))',
                                                color: m.role === 'guest' ? 'var(--text-primary)' : '#fff',
                                            }}
                                        >
                                            <div style={{ fontSize: 13, lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>{m.content}</div>
                                            <div style={{ fontSize: 10, opacity: 0.6, marginTop: 4, textAlign: 'right' }}>
                                                {m.role === 'guest' ? '👤 Guest' : m.role === 'staff' ? '🙋 Staff' : '🤖 AI'} · {new Date(m.sent_at).toLocaleTimeString()}
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {/* AI Draft Sidebar */}
                                {detail.status !== 'resolved' && (
                                    <div style={{ padding: '12px 20px', borderTop: '1px solid var(--border-subtle)', background: 'rgba(99,102,241,0.04)' }}>
                                        <div className="flex items-center justify-between" style={{ marginBottom: 8 }}>
                                            <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                                🤖 AI Draft
                                            </span>
                                            <div className="flex gap-sm">
                                                <button
                                                    className={`btn btn-sm ${draftLang === 'en' ? 'btn-primary' : 'btn-ghost'}`}
                                                    style={{ fontSize: 11, padding: '2px 8px' }}
                                                    onClick={() => setDraftLang('en')}
                                                >EN</button>
                                                <button
                                                    className={`btn btn-sm ${draftLang === 'bm' ? 'btn-primary' : 'btn-ghost'}`}
                                                    style={{ fontSize: 11, padding: '2px 8px' }}
                                                    onClick={() => setDraftLang('bm')}
                                                >BM</button>
                                            </div>
                                        </div>
                                        {(draftEn || draftBm) ? (
                                            <>
                                                <div style={{
                                                    background: 'var(--surface-elevated)',
                                                    border: '1px solid var(--border-subtle)',
                                                    borderRadius: 8,
                                                    padding: '8px 12px',
                                                    fontSize: 13,
                                                    lineHeight: 1.5,
                                                    color: 'var(--text-primary)',
                                                    marginBottom: 8,
                                                    whiteSpace: 'pre-wrap',
                                                    minHeight: 48,
                                                }}>
                                                    {draftLang === 'en' ? draftEn : draftBm}
                                                </div>
                                                <div className="flex gap-sm">
                                                    <button
                                                        className="btn btn-primary btn-sm"
                                                        onClick={copyDraft}
                                                        style={{ fontSize: 12 }}
                                                    >
                                                        {draftCopied ? '✓ Copied to reply' : '📋 Use this draft'}
                                                    </button>
                                                    <button
                                                        className="btn btn-ghost btn-sm"
                                                        onClick={() => generateDraft(detail.id)}
                                                        disabled={draftLoading}
                                                        style={{ fontSize: 12 }}
                                                    >
                                                        {draftLoading ? '...' : '↺ Regenerate'}
                                                    </button>
                                                </div>
                                            </>
                                        ) : (
                                            <button
                                                className="btn btn-ghost btn-sm"
                                                onClick={() => generateDraft(detail.id)}
                                                disabled={draftLoading}
                                                style={{ fontSize: 12, width: '100%' }}
                                            >
                                                {draftLoading ? '⟳ Generating draft…' : '✦ Generate AI Draft'}
                                            </button>
                                        )}
                                    </div>
                                )}

                                {/* Payment link section */}
                                {detail.status !== 'resolved' && detail.lead?.intent === 'room_booking' && (
                                    <div style={{ padding: '12px 20px', borderTop: '1px solid var(--border-subtle)' }}>
                                        <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: 14, marginTop: 2 }}>
                                            <p style={{ fontSize: 12, fontWeight: 600, marginBottom: 8, color: 'var(--text-muted)' }}>
                                                DIRECT BOOKING PAYMENT
                                            </p>
                                            {paymentLinkUrl ? (
                                                <div>
                                                    <p style={{ fontSize: 12, color: 'var(--success)', marginBottom: 6 }}>✓ Payment link ready</p>
                                                    <div style={{ display: 'flex', gap: 6 }}>
                                                        <input
                                                            readOnly
                                                            value={paymentLinkUrl}
                                                            style={{ flex: 1, fontSize: 11, padding: '6px 8px', borderRadius: 4, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)' }}
                                                        />
                                                        <button
                                                            className="btn btn-ghost btn-sm"
                                                            onClick={() => navigator.clipboard.writeText(paymentLinkUrl)}
                                                            style={{ fontSize: 11 }}
                                                        >
                                                            Copy
                                                        </button>
                                                    </div>
                                                    <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
                                                        Paste this into your reply. Guest pays via FPX or card.
                                                    </p>
                                                </div>
                                            ) : (
                                                <div style={{ display: 'grid', gap: 6 }}>
                                                    <input
                                                        type="number"
                                                        value={paymentLinkAmount}
                                                        onChange={(e) => setPaymentLinkAmount(e.target.value)}
                                                        placeholder="Amount in RM (e.g. 560)"
                                                        style={{ padding: '7px 10px', borderRadius: 4, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13 }}
                                                    />
                                                    <input
                                                        type="text"
                                                        value={paymentLinkDesc}
                                                        onChange={(e) => setPaymentLinkDesc(e.target.value)}
                                                        placeholder="e.g. Deluxe King × 2 nights, 3–5 May"
                                                        style={{ padding: '7px 10px', borderRadius: 4, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13 }}
                                                    />
                                                    <button
                                                        className="btn btn-primary btn-sm"
                                                        onClick={handleGeneratePaymentLink}
                                                        disabled={generatingLink || !paymentLinkAmount}
                                                    >
                                                        {generatingLink ? 'Generating…' : 'Generate FPX Payment Link'}
                                                    </button>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}

                                {/* Staff reply input */}
                                {detail.status !== 'resolved' && (
                                    <div style={{ padding: '12px 20px', borderTop: '1px solid var(--border-subtle)' }}>
                                        <div className="flex gap-sm" style={{ alignItems: 'flex-end' }}>
                                            <textarea
                                                value={replyText}
                                                onChange={(e) => setReplyText(e.target.value)}
                                                onKeyDown={(e) => {
                                                    if (e.key === 'Enter' && !e.shiftKey) {
                                                        e.preventDefault();
                                                        sendStaffReply(detail.id);
                                                    }
                                                }}
                                                placeholder="Reply to guest… (Enter to send, Shift+Enter for new line)"
                                                rows={2}
                                                disabled={replySending}
                                                style={{
                                                    flex: 1,
                                                    resize: 'none',
                                                    padding: '8px 12px',
                                                    borderRadius: 8,
                                                    border: '1px solid var(--border-subtle)',
                                                    background: 'var(--surface-elevated)',
                                                    color: 'var(--text-primary)',
                                                    fontSize: 13,
                                                    lineHeight: 1.5,
                                                }}
                                            />
                                            <button
                                                className="btn btn-primary btn-sm"
                                                disabled={replySending || !replyText.trim()}
                                                onClick={() => sendStaffReply(detail.id)}
                                                style={{ flexShrink: 0 }}
                                            >
                                                {replySending ? '...' : 'Send →'}
                                            </button>
                                        </div>
                                    </div>
                                )}

                                {/* Actions */}
                                {detail.status !== 'resolved' && (
                                    <div style={{ padding: '4px 20px 12px' }} className="flex gap-sm">
                                        {detail.status !== 'resolved' && (
                                            <button
                                                className="btn btn-sm btn-primary"
                                                disabled={!!actionLoading}
                                                onClick={() => doAction(detail.id, 'resolve')}
                                            >
                                                {actionLoading === 'resolve' ? '...' : '✅ Resolve'}
                                            </button>
                                        )}
                                        {detail.ai_mode !== 'handoff' && (
                                            <button
                                                className="btn btn-sm btn-secondary"
                                                disabled={!!actionLoading}
                                                onClick={() => doAction(detail.id, 'handoff')}
                                            >
                                                {actionLoading === 'handoff' ? '...' : '🔄 Handoff'}
                                            </button>
                                        )}
                                        {detail.ai_mode !== 'staff' && (
                                            <button
                                                className="btn btn-sm btn-ghost"
                                                disabled={!!actionLoading}
                                                onClick={() => doAction(detail.id, 'takeover')}
                                            >
                                                {actionLoading === 'takeover' ? '...' : '🙋 Take Over'}
                                            </button>
                                        )}
                                    </div>
                                )}
                            </>
                        ) : (
                            <div className="empty-state" style={{ padding: 40 }}>
                                <p>Could not load conversation</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
