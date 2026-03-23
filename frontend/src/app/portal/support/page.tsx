'use client';

import { useEffect, useState } from 'react';
import { apiGet, apiPost } from '@/lib/api';

interface Ticket {
    id: string;
    subject: string;
    description: string;
    priority: string;
    status: string;
    created_at: string;
}

const PRIORITY_BADGE: Record<string, string> = {
    low: 'badge-success',
    medium: 'badge-warning',
    high: 'badge-danger',
    urgent: 'badge-danger',
};

const STATUS_BADGE: Record<string, string> = {
    open: 'badge-warning',
    in_progress: 'badge-warning',
    resolved: 'badge-success',
    closed: '',
};

export default function PortalSupportPage() {
    const [tickets, setTickets] = useState<Ticket[]>([]);
    const [loading, setLoading] = useState(true);
    const [ticketsAvailable, setTicketsAvailable] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [form, setForm] = useState({ subject: '', description: '', priority: 'medium' });
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const loadTickets = () => {
        setLoading(true);
        apiGet<Ticket[]>('/support/tickets')
            .then((data) => { setTickets(data || []); setTicketsAvailable(true); })
            .catch(() => { setTicketsAvailable(false); setTickets([]); })
            .finally(() => setLoading(false));
    };

    useEffect(() => { loadTickets(); }, []);

    const handleSubmit = async () => {
        if (!form.subject.trim() || !form.description.trim()) return;
        setSubmitting(true);
        setError('');
        setSuccess('');
        try {
            await apiPost('/support/tickets', form);
            setSuccess('Ticket submitted successfully. We\'ll get back to you shortly.');
            setForm({ subject: '', description: '', priority: 'medium' });
            setShowForm(false);
            loadTickets();
        } catch (e: unknown) {
            setError((e instanceof Error ? e.message : String(e)) || 'Failed to submit ticket');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div>
            <div className="flex items-center justify-between" style={{ marginBottom: 28 }}>
                <div>
                    <h1>Support</h1>
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                        Get help from the SheersSoft team
                    </p>
                </div>
                <button
                    className="btn btn-primary btn-sm"
                    onClick={() => { setShowForm(!showForm); setError(''); setSuccess(''); }}
                >
                    + New Ticket
                </button>
            </div>

            {error && <div style={{ color: 'var(--danger)', marginBottom: 12, fontSize: 13 }}>{error}</div>}
            {success && <div style={{ color: 'var(--success)', marginBottom: 12, fontSize: 13 }}>{success}</div>}

            {/* New ticket form */}
            {showForm && (
                <div className="card animate-in" style={{ marginBottom: 20, borderColor: 'rgba(99,102,241,0.3)', padding: 24 }}>
                    <h3 style={{ marginBottom: 16, fontSize: 14 }}>New Support Ticket</h3>
                    <div style={{ display: 'grid', gap: 12 }}>
                        <div>
                            <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Subject</label>
                            <input
                                type="text"
                                value={form.subject}
                                onChange={(e) => setForm((f) => ({ ...f, subject: e.target.value }))}
                                placeholder="Brief description of your issue"
                                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-subtle)', background: 'var(--surface)', color: 'var(--text-primary)', fontSize: 13, boxSizing: 'border-box' }}
                            />
                        </div>
                        <div>
                            <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Description</label>
                            <textarea
                                value={form.description}
                                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                                placeholder="Please describe the issue in detail..."
                                rows={5}
                                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-subtle)', background: 'var(--surface)', color: 'var(--text-primary)', fontSize: 13, resize: 'vertical', boxSizing: 'border-box', fontFamily: 'inherit' }}
                            />
                        </div>
                        <div>
                            <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Priority</label>
                            <select
                                value={form.priority}
                                onChange={(e) => setForm((f) => ({ ...f, priority: e.target.value }))}
                                style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-subtle)', background: 'var(--surface)', color: 'var(--text-primary)', fontSize: 13 }}
                            >
                                <option value="low">Low</option>
                                <option value="medium">Medium</option>
                                <option value="high">High</option>
                                <option value="urgent">Urgent</option>
                            </select>
                        </div>
                    </div>
                    <div className="flex items-center gap-sm" style={{ marginTop: 16 }}>
                        <button
                            className="btn btn-primary btn-sm"
                            onClick={handleSubmit}
                            disabled={submitting}
                        >
                            {submitting ? 'Submitting…' : 'Submit Ticket'}
                        </button>
                        <button
                            className="btn btn-ghost btn-sm"
                            onClick={() => { setShowForm(false); setForm({ subject: '', description: '', priority: 'medium' }); }}
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}

            {/* Tickets list or fallback */}
            {loading ? (
                <div className="flex justify-center" style={{ padding: 60 }}>
                    <div className="loader" />
                </div>
            ) : !ticketsAvailable ? (
                <div className="card" style={{ padding: 32, textAlign: 'center' }}>
                    <div style={{ fontSize: 40, marginBottom: 16 }}>🎧</div>
                    <h3 style={{ marginBottom: 8 }}>Need help?</h3>
                    <p className="text-muted text-sm" style={{ marginBottom: 16 }}>
                        Reach out to us directly and we&apos;ll respond within 1 business day.
                    </p>
                    <a
                        href="mailto:support@sheerssoft.com"
                        className="btn btn-primary btn-sm"
                        style={{ display: 'inline-block' }}
                    >
                        ✉ support@sheerssoft.com
                    </a>
                </div>
            ) : tickets.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">🎫</div>
                    <p>No support tickets</p>
                    <p className="text-sm text-muted" style={{ marginTop: 4 }}>
                        Open a ticket if you need help with anything
                    </p>
                </div>
            ) : (
                <div style={{ display: 'grid', gap: 12 }}>
                    {tickets.map((ticket) => (
                        <div key={ticket.id} className="card animate-in" style={{ padding: 20 }}>
                            <div className="flex items-center justify-between" style={{ marginBottom: 8 }}>
                                <span style={{ fontWeight: 600, fontSize: 14 }}>{ticket.subject}</span>
                                <div className="flex items-center gap-sm">
                                    <span className={`badge ${PRIORITY_BADGE[ticket.priority] ?? 'badge-warning'}`} style={{ fontSize: 11 }}>
                                        {ticket.priority}
                                    </span>
                                    <span className={`badge ${STATUS_BADGE[ticket.status] ?? 'badge-warning'}`} style={{ fontSize: 11 }}>
                                        {ticket.status.replace('_', ' ')}
                                    </span>
                                </div>
                            </div>
                            <p className="text-sm text-muted" style={{ marginBottom: 8, lineHeight: 1.5 }}>
                                {ticket.description.length > 150
                                    ? ticket.description.slice(0, 150) + '…'
                                    : ticket.description}
                            </p>
                            <span className="text-xs text-muted">
                                Opened {new Date(ticket.created_at).toLocaleDateString()}
                            </span>
                        </div>
                    ))}
                </div>
            )}

            <div style={{ marginTop: 32, padding: '16px 20px', background: 'var(--surface)', borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
                <p className="text-sm" style={{ marginBottom: 4 }}>
                    <strong>Other ways to reach us:</strong>
                </p>
                <p className="text-sm text-muted">
                    Email: <a href="mailto:support@sheerssoft.com" style={{ color: 'var(--accent)' }}>support@sheerssoft.com</a>
                    {' · '}
                    Response time: within 1 business day (priority support: 4 hours)
                </p>
            </div>
        </div>
    );
}
