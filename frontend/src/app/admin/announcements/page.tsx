'use client';

import { useEffect, useState } from 'react';
import { apiGet, apiPost, apiPatch } from '@/lib/api';

interface Announcement {
    id: string;
    type: 'maintenance' | 'incident' | 'feature' | 'billing';
    status: 'draft' | 'scheduled' | 'active' | 'resolved' | 'archived';
    title: string;
    body: string;
    target_type: 'all' | 'tier' | 'tenant';
    target_tier?: string | null;
    target_tenant_id?: string | null;
    scheduled_at?: string | null;
    resolved_at?: string | null;
    send_email: boolean;
    created_at: string;
    updated_at: string;
}

const TYPE_STYLES: Record<string, { badge: string; color: string; icon: string }> = {
    maintenance: { badge: 'badge-warning', color: 'var(--warning)', icon: '🔧' },
    incident:    { badge: 'badge-danger',  color: 'var(--danger)',  icon: '🚨' },
    feature:     { badge: 'badge-info',    color: 'var(--info)',    icon: '✨' },
    billing:     { badge: 'badge-warning', color: 'var(--warning)', icon: '💳' },
};

const STATUS_BADGE: Record<string, string> = {
    draft:     'badge-neutral',
    scheduled: 'badge-info',
    active:    'badge-success',
    resolved:  'badge-neutral',
    archived:  'badge-neutral',
};

const blank = (): Partial<Announcement> => ({
    type: 'maintenance',
    status: 'active',
    title: '',
    body: '',
    target_type: 'all',
    send_email: false,
});

export default function AnnouncementsPage() {
    const [list, setList] = useState<Announcement[]>([]);
    const [loading, setLoading] = useState(true);
    const [form, setForm] = useState<Partial<Announcement>>(blank());
    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);
    const [error, setError] = useState('');

    const load = () => {
        setLoading(true);
        apiGet<Announcement[]>('/superadmin/announcements')
            .then(setList)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false));
    };

    useEffect(() => { load(); }, []);

    const submit = async () => {
        if (!form.title?.trim() || !form.body?.trim()) {
            setError('Title and body are required.');
            return;
        }
        setSaving(true);
        setError('');
        try {
            await apiPost('/superadmin/announcements', form);
            setForm(blank());
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
            load();
        } catch (e: any) {
            setError(e.message || 'Failed to create announcement');
        } finally {
            setSaving(false);
        }
    };

    const changeStatus = async (id: string, status: string) => {
        try {
            await apiPatch(`/superadmin/announcements/${id}`, { status });
            load();
        } catch (e: any) {
            setError(e.message || 'Failed to update');
        }
    };

    return (
        <div>
            <div style={{ marginBottom: 32 }}>
                <h1>Announcements</h1>
                <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                    Broadcast maintenance notices, incidents, and feature updates to hotel clients
                </p>
            </div>

            {error && (
                <div className="card" style={{ padding: '12px 16px', marginBottom: 24, borderColor: 'var(--danger)', color: 'var(--danger)' }}>
                    {error}
                </div>
            )}

            {/* Compose */}
            <div className="card" style={{ padding: 24, marginBottom: 32 }}>
                <h3 style={{ fontSize: 15, marginBottom: 16 }}>Compose Announcement</h3>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
                    <div>
                        <label className="text-xs text-muted" style={{ display: 'block', marginBottom: 4 }}>Type</label>
                        <select
                            value={form.type}
                            onChange={(e) => setForm({ ...form, type: e.target.value as any })}
                            style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-subtle)', background: 'var(--bg-input)', color: 'var(--text-primary)', fontSize: 14 }}
                        >
                            <option value="maintenance">🔧 Maintenance</option>
                            <option value="incident">🚨 Incident</option>
                            <option value="feature">✨ Feature</option>
                            <option value="billing">💳 Billing</option>
                        </select>
                    </div>
                    <div>
                        <label className="text-xs text-muted" style={{ display: 'block', marginBottom: 4 }}>Status</label>
                        <select
                            value={form.status}
                            onChange={(e) => setForm({ ...form, status: e.target.value as any })}
                            style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-subtle)', background: 'var(--bg-input)', color: 'var(--text-primary)', fontSize: 14 }}
                        >
                            <option value="draft">Draft (not visible)</option>
                            <option value="active">Active (visible now)</option>
                            <option value="scheduled">Scheduled</option>
                        </select>
                    </div>
                </div>

                <div style={{ marginBottom: 12 }}>
                    <label className="text-xs text-muted" style={{ display: 'block', marginBottom: 4 }}>Title</label>
                    <input
                        type="text"
                        value={form.title || ''}
                        onChange={(e) => setForm({ ...form, title: e.target.value })}
                        placeholder="e.g. Scheduled maintenance — Saturday 11pm–2am MYT"
                        style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-subtle)', background: 'var(--bg-input)', color: 'var(--text-primary)', fontSize: 14 }}
                    />
                </div>

                <div style={{ marginBottom: 12 }}>
                    <label className="text-xs text-muted" style={{ display: 'block', marginBottom: 4 }}>Body</label>
                    <textarea
                        value={form.body || ''}
                        onChange={(e) => setForm({ ...form, body: e.target.value })}
                        rows={3}
                        placeholder="Describe what will be affected and any action tenants need to take..."
                        style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-subtle)', background: 'var(--bg-input)', color: 'var(--text-primary)', fontSize: 14, resize: 'vertical' }}
                    />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
                    <div>
                        <label className="text-xs text-muted" style={{ display: 'block', marginBottom: 4 }}>Target audience</label>
                        <select
                            value={form.target_type}
                            onChange={(e) => setForm({ ...form, target_type: e.target.value as any })}
                            style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-subtle)', background: 'var(--bg-input)', color: 'var(--text-primary)', fontSize: 14 }}
                        >
                            <option value="all">All tenants</option>
                            <option value="tier">By subscription tier</option>
                            <option value="tenant">Specific tenant</option>
                        </select>
                    </div>
                    {form.target_type === 'tier' && (
                        <div>
                            <label className="text-xs text-muted" style={{ display: 'block', marginBottom: 4 }}>Tier</label>
                            <select
                                value={form.target_tier || ''}
                                onChange={(e) => setForm({ ...form, target_tier: e.target.value })}
                                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-subtle)', background: 'var(--bg-input)', color: 'var(--text-primary)', fontSize: 14 }}
                            >
                                <option value="">Select tier...</option>
                                <option value="pilot">Pilot</option>
                                <option value="boutique">Boutique</option>
                                <option value="independent">Independent</option>
                                <option value="premium">Premium</option>
                            </select>
                        </div>
                    )}
                    {form.target_type === 'tenant' && (
                        <div>
                            <label className="text-xs text-muted" style={{ display: 'block', marginBottom: 4 }}>Tenant ID</label>
                            <input
                                type="text"
                                value={form.target_tenant_id || ''}
                                onChange={(e) => setForm({ ...form, target_tenant_id: e.target.value })}
                                placeholder="UUID"
                                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-subtle)', background: 'var(--bg-input)', color: 'var(--text-primary)', fontSize: 14 }}
                            />
                        </div>
                    )}
                </div>

                <label className="flex items-center gap-sm" style={{ cursor: 'pointer', marginBottom: 16 }}>
                    <input
                        type="checkbox"
                        checked={form.send_email || false}
                        onChange={(e) => setForm({ ...form, send_email: e.target.checked })}
                        style={{ width: 16, height: 16 }}
                    />
                    <span className="text-sm">Also send email to tenant owner(s)</span>
                </label>

                <div className="flex items-center gap-sm">
                    <button className="btn btn-primary btn-sm" onClick={submit} disabled={saving}>
                        {saving ? 'Posting...' : 'Post Announcement'}
                    </button>
                    {saved && <span className="text-sm" style={{ color: 'var(--success)' }}>✓ Posted</span>}
                </div>
            </div>

            {/* List */}
            <h3 style={{ fontSize: 15, marginBottom: 12 }}>All Announcements</h3>

            {loading ? (
                <div className="flex justify-center" style={{ padding: 40 }}><div className="loader" /></div>
            ) : list.length === 0 ? (
                <p className="text-muted text-sm">No announcements yet.</p>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {list.map((ann) => {
                        const ts = TYPE_STYLES[ann.type] ?? TYPE_STYLES.feature;
                        return (
                            <div
                                key={ann.id}
                                className="card"
                                style={{
                                    padding: '16px 20px',
                                    borderColor: ann.status === 'active' ? ts.color : undefined,
                                }}
                            >
                                <div className="flex items-center justify-between" style={{ marginBottom: 6 }}>
                                    <div className="flex items-center gap-sm">
                                        <span>{ts.icon}</span>
                                        <strong style={{ fontSize: 14 }}>{ann.title}</strong>
                                        <span className={`badge ${ts.badge}`}>{ann.type}</span>
                                        <span className={`badge ${STATUS_BADGE[ann.status]}`}>{ann.status}</span>
                                    </div>
                                    <div className="flex items-center gap-sm">
                                        {ann.status === 'active' && (
                                            <button className="btn btn-sm btn-ghost" onClick={() => changeStatus(ann.id, 'resolved')}>
                                                Resolve
                                            </button>
                                        )}
                                        {ann.status === 'draft' && (
                                            <button className="btn btn-sm btn-primary" onClick={() => changeStatus(ann.id, 'active')}>
                                                Activate
                                            </button>
                                        )}
                                        {(ann.status === 'resolved' || ann.status === 'draft') && (
                                            <button className="btn btn-sm btn-ghost" onClick={() => changeStatus(ann.id, 'archived')}>
                                                Archive
                                            </button>
                                        )}
                                    </div>
                                </div>
                                <p className="text-sm" style={{ color: 'var(--text-secondary)', marginBottom: 6 }}>{ann.body}</p>
                                <div className="flex items-center gap-sm">
                                    <span className="text-xs text-muted">Target: {ann.target_type}{ann.target_tier ? ` (${ann.target_tier})` : ''}</span>
                                    <span className="text-xs text-muted">·</span>
                                    <span className="text-xs text-muted">{new Date(ann.created_at).toLocaleString('en-MY')}</span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
