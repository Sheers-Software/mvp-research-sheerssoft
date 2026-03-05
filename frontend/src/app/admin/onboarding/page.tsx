'use client';

import { useState } from 'react';
import { apiPost } from '@/lib/api';

const tiers = [
    { value: 'pilot', label: '🆓 Pilot (30-day free trial)' },
    { value: 'boutique', label: '🏠 Boutique (RM 1,500/mo)' },
    { value: 'independent', label: '🏨 Independent (RM 3,500/mo)' },
    { value: 'premium', label: '⭐ Premium (RM 7,500/mo)' },
];

const channels = [
    { value: 'whatsapp', label: '💬 WhatsApp', default: true },
    { value: 'email', label: '📧 Email', default: true },
    { value: 'website', label: '🌐 Website Chat', default: true },
];

export default function OnboardingNewPage() {
    const [submitting, setSubmitting] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState('');

    const [form, setForm] = useState({
        tenant_name: '',
        property_name: '',
        owner_email: '',
        owner_name: '',
        owner_phone: '',
        timezone: 'Asia/Kuala_Lumpur',
        subscription_tier: 'pilot',
        pilot_duration_days: 30,
        preferred_channels: ['whatsapp', 'email', 'website'],
        whatsapp_provider: 'meta',
        whatsapp_number: '',
        twilio_phone_number: '',
        reservation_email: '',
        website_url: '',
        assigned_account_manager: '',
    });

    const updateField = (field: string, value: any) => {
        setForm((prev) => ({ ...prev, [field]: value }));
    };

    const toggleChannel = (ch: string) => {
        setForm((prev) => ({
            ...prev,
            preferred_channels: prev.preferred_channels.includes(ch)
                ? prev.preferred_channels.filter((c) => c !== ch)
                : [...prev.preferred_channels, ch],
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        setError('');
        setResult(null);

        try {
            const res = await apiPost('/onboarding/provision-tenant', form);
            setResult(res);
        } catch (err: any) {
            setError(err.message || 'Provisioning failed');
        } finally {
            setSubmitting(false);
        }
    };

    if (result) {
        return (
            <div>
                <h1 style={{ marginBottom: 24 }}>✅ Client Provisioned</h1>
                <div className="card animate-in" style={{ maxWidth: 600, padding: 32 }}>
                    <div style={{ fontSize: 48, textAlign: 'center', marginBottom: 16 }}>🎉</div>
                    <p style={{ textAlign: 'center', fontSize: 16, marginBottom: 24 }}>{result.message}</p>

                    <div className="flex flex-col gap-sm" style={{ fontSize: 14 }}>
                        <div className="flex justify-between" style={{ padding: '8px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                            <span className="text-muted">Tenant ID</span>
                            <code style={{ fontSize: 12 }}>{result.tenant_id}</code>
                        </div>
                        <div className="flex justify-between" style={{ padding: '8px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                            <span className="text-muted">Property ID</span>
                            <code style={{ fontSize: 12 }}>{result.property_id}</code>
                        </div>
                        <div className="flex justify-between" style={{ padding: '8px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                            <span className="text-muted">Magic Link</span>
                            <span className={`badge ${result.magic_link_sent ? 'badge-success' : 'badge-warning'}`}>
                                {result.magic_link_sent ? '✅ Sent' : '⚠️ Not sent'}
                            </span>
                        </div>
                        <div className="flex justify-between" style={{ padding: '8px 0' }}>
                            <span className="text-muted">Channels</span>
                            <span className={`badge ${result.channels_setup_initiated ? 'badge-success' : 'badge-warning'}`}>
                                {result.channels_setup_initiated ? '🔄 Setup started' : '⚠️ Pending'}
                            </span>
                        </div>
                    </div>

                    <div className="flex gap-md" style={{ marginTop: 24 }}>
                        <button className="btn btn-primary" onClick={() => { setResult(null); setForm({ ...form, tenant_name: '', property_name: '', owner_email: '', owner_name: '', owner_phone: '' }); }}>
                            ➕ Onboard Another
                        </button>
                        <a href="/admin/pipeline" className="btn btn-secondary">View Pipeline →</a>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div>
            <div style={{ marginBottom: 32 }}>
                <h1>Onboard New Client</h1>
                <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                    One-click tenant provisioning — creates account, property, user, and starts channel auto-setup.
                </p>
            </div>

            <form onSubmit={handleSubmit} style={{ maxWidth: 680 }}>
                <div className="card animate-in" style={{ marginBottom: 20 }}>
                    <h3 style={{ marginBottom: 16 }}>🏨 Hotel Details</h3>
                    <div className="grid grid-2 gap-md">
                        <div className="input-group">
                            <label>Hotel / Group Name *</label>
                            <input className="input" required value={form.tenant_name} onChange={(e) => updateField('tenant_name', e.target.value)} placeholder="e.g. Vivatel Kuala Lumpur" />
                        </div>
                        <div className="input-group">
                            <label>Property Name *</label>
                            <input className="input" required value={form.property_name} onChange={(e) => updateField('property_name', e.target.value)} placeholder="e.g. Vivatel KL City Centre" />
                        </div>
                    </div>
                </div>

                <div className="card animate-in" style={{ marginBottom: 20, animationDelay: '100ms' }}>
                    <h3 style={{ marginBottom: 16 }}>👤 Contact Person (GM / Owner)</h3>
                    <div className="grid grid-2 gap-md">
                        <div className="input-group">
                            <label>Full Name *</label>
                            <input className="input" required value={form.owner_name} onChange={(e) => updateField('owner_name', e.target.value)} placeholder="e.g. Ahmad Razali" />
                        </div>
                        <div className="input-group">
                            <label>Email *</label>
                            <input className="input" required type="email" value={form.owner_email} onChange={(e) => updateField('owner_email', e.target.value)} placeholder="gm@hotel.com" />
                        </div>
                        <div className="input-group">
                            <label>Phone (WhatsApp)</label>
                            <input className="input" value={form.owner_phone} onChange={(e) => updateField('owner_phone', e.target.value)} placeholder="+60123456789" />
                        </div>
                        <div className="input-group">
                            <label>Account Manager</label>
                            <input className="input" value={form.assigned_account_manager} onChange={(e) => updateField('assigned_account_manager', e.target.value)} placeholder="e.g. Amir" />
                        </div>
                    </div>
                </div>

                <div className="card animate-in" style={{ marginBottom: 20, animationDelay: '200ms' }}>
                    <h3 style={{ marginBottom: 16 }}>💳 Subscription</h3>
                    <div className="grid grid-2 gap-md">
                        <div className="input-group">
                            <label>Tier *</label>
                            <select className="input" value={form.subscription_tier} onChange={(e) => updateField('subscription_tier', e.target.value)}>
                                {tiers.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                            </select>
                        </div>
                        {form.subscription_tier === 'pilot' && (
                            <div className="input-group">
                                <label>Pilot Duration (days)</label>
                                <input className="input" type="number" value={form.pilot_duration_days} onChange={(e) => updateField('pilot_duration_days', parseInt(e.target.value))} min={7} max={90} />
                            </div>
                        )}
                    </div>
                </div>

                <div className="card animate-in" style={{ marginBottom: 20, animationDelay: '300ms' }}>
                    <h3 style={{ marginBottom: 16 }}>📱 Channels</h3>
                    <div className="flex gap-md" style={{ marginBottom: 16 }}>
                        {channels.map((ch) => (
                            <button
                                key={ch.value}
                                type="button"
                                className={`btn ${form.preferred_channels.includes(ch.value) ? 'btn-primary' : 'btn-secondary'}`}
                                onClick={() => toggleChannel(ch.value)}
                            >
                                {ch.label}
                            </button>
                        ))}
                    </div>

                    {form.preferred_channels.includes('whatsapp') && (
                        <div className="grid grid-2 gap-md" style={{ marginTop: 12 }}>
                            <div className="input-group">
                                <label>WhatsApp Provider</label>
                                <select className="input" value={form.whatsapp_provider} onChange={(e) => updateField('whatsapp_provider', e.target.value)}>
                                    <option value="meta">Meta Cloud API</option>
                                    <option value="twilio">Twilio</option>
                                </select>
                            </div>
                            <div className="input-group">
                                <label>WhatsApp Business Number</label>
                                <input className="input" value={form.whatsapp_number} onChange={(e) => updateField('whatsapp_number', e.target.value)} placeholder="+60123456789" />
                            </div>
                        </div>
                    )}

                    {form.preferred_channels.includes('email') && (
                        <div className="input-group" style={{ marginTop: 12 }}>
                            <label>Reservation Email (to forward)</label>
                            <input className="input" type="email" value={form.reservation_email} onChange={(e) => updateField('reservation_email', e.target.value)} placeholder="reservations@hotel.com" />
                        </div>
                    )}

                    {form.preferred_channels.includes('website') && (
                        <div className="input-group" style={{ marginTop: 12 }}>
                            <label>Hotel Website URL</label>
                            <input className="input" value={form.website_url} onChange={(e) => updateField('website_url', e.target.value)} placeholder="https://www.hotel.com" />
                        </div>
                    )}
                </div>

                {error && (
                    <div className="card" style={{ background: 'var(--danger-bg)', borderColor: 'rgba(248,113,113,0.2)', marginBottom: 20 }}>
                        <p style={{ color: 'var(--danger)', fontSize: 14 }}>❌ {error}</p>
                    </div>
                )}

                <button type="submit" className="btn btn-primary btn-lg" disabled={submitting} style={{ marginBottom: 32 }}>
                    {submitting ? (
                        <><span className="loader" style={{ width: 18, height: 18 }} /> Provisioning...</>
                    ) : (
                        '🚀 Provision Tenant'
                    )}
                </button>
            </form>
        </div>
    );
}
