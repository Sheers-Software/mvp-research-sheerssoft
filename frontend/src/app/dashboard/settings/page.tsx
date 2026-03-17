'use client';

import { useEffect, useState } from 'react';
import { apiGet, apiPut } from '@/lib/api';

interface PropertySettings {
    id: string;
    name: string;
    notification_email: string | null;
    operating_hours: { start: string; end: string; timezone: string } | null;
    timezone: string;
    adr: number;
    hourly_rate: number;
    brand_vocabulary: string | null;
    whatsapp_number: string | null;
    website_url: string | null;
    plan_tier: string;
    is_active: boolean;
}

export default function SettingsPage() {
    const [settings, setSettings] = useState<PropertySettings | null>(null);
    const [propertyId, setPropertyId] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);
    const [error, setError] = useState('');

    // Form state
    const [notificationEmail, setNotificationEmail] = useState('');
    const [hoursStart, setHoursStart] = useState('07:00');
    const [hoursEnd, setHoursEnd] = useState('23:00');
    const [timezone, setTimezone] = useState('Asia/Kuala_Lumpur');
    const [adr, setAdr] = useState('');
    const [hourlyRate, setHourlyRate] = useState('');
    const [brandVocabulary, setBrandVocabulary] = useState('');

    useEffect(() => {
        apiGet<any>('/analytics/dashboard')
            .then((data) => {
                if (data?.property_id) {
                    setPropertyId(data.property_id);
                    return apiGet<PropertySettings>(`/properties/${data.property_id}/settings`);
                }
            })
            .then((s) => {
                if (!s) return;
                setSettings(s);
                setNotificationEmail(s.notification_email || '');
                setHoursStart(s.operating_hours?.start || '07:00');
                setHoursEnd(s.operating_hours?.end || '23:00');
                setTimezone(s.timezone || 'Asia/Kuala_Lumpur');
                setAdr(s.adr?.toString() || '230');
                setHourlyRate(s.hourly_rate?.toString() || '25');
                setBrandVocabulary(s.brand_vocabulary || '');
            })
            .catch(() => setError('Failed to load settings'))
            .finally(() => setLoading(false));
    }, []);

    const save = async () => {
        if (!propertyId) return;
        setSaving(true);
        setError('');
        try {
            await apiPut(`/properties/${propertyId}/settings`, {
                notification_email: notificationEmail || null,
                operating_hours: {
                    start: hoursStart,
                    end: hoursEnd,
                    timezone,
                },
                timezone,
                adr: parseFloat(adr) || 230,
                hourly_rate: parseFloat(hourlyRate) || 25,
                brand_vocabulary: brandVocabulary || null,
            });
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
        } catch {
            setError('Failed to save settings');
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return <div className="flex justify-center" style={{ padding: 80 }}><div className="loader" /></div>;
    }

    return (
        <div>
            <div style={{ marginBottom: 32 }}>
                <h1>Property Settings</h1>
                <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                    Configure your property for the AI concierge
                </p>
            </div>

            {error && (
                <div className="card" style={{ padding: '12px 16px', marginBottom: 24, borderColor: 'var(--danger)', color: 'var(--danger)' }}>
                    {error}
                </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>

                {/* Notifications */}
                <div className="card" style={{ padding: 24 }}>
                    <h3 style={{ fontSize: 15, marginBottom: 16 }}>📧 Daily Report Email</h3>
                    <p className="text-sm text-muted" style={{ marginBottom: 16 }}>
                        Receives the 7:30am daily intelligence report.
                    </p>
                    <label className="text-sm" style={{ display: 'block', marginBottom: 6 }}>
                        Notification Email
                    </label>
                    <input
                        type="email"
                        className="input"
                        value={notificationEmail}
                        onChange={(e) => setNotificationEmail(e.target.value)}
                        placeholder="reservations@vivatel.com.my"
                        style={{ width: '100%' }}
                    />
                </div>

                {/* Operating Hours */}
                <div className="card" style={{ padding: 24 }}>
                    <h3 style={{ fontSize: 15, marginBottom: 16 }}>🕐 Operating Hours</h3>
                    <p className="text-sm text-muted" style={{ marginBottom: 16 }}>
                        Outside these hours, the AI activates after-hours mode.
                    </p>
                    <div className="flex gap-sm" style={{ marginBottom: 12 }}>
                        <div style={{ flex: 1 }}>
                            <label className="text-sm" style={{ display: 'block', marginBottom: 6 }}>Opens</label>
                            <input
                                type="time"
                                className="input"
                                value={hoursStart}
                                onChange={(e) => setHoursStart(e.target.value)}
                                style={{ width: '100%' }}
                            />
                        </div>
                        <div style={{ flex: 1 }}>
                            <label className="text-sm" style={{ display: 'block', marginBottom: 6 }}>Closes</label>
                            <input
                                type="time"
                                className="input"
                                value={hoursEnd}
                                onChange={(e) => setHoursEnd(e.target.value)}
                                style={{ width: '100%' }}
                            />
                        </div>
                    </div>
                    <label className="text-sm" style={{ display: 'block', marginBottom: 6 }}>Timezone</label>
                    <select
                        className="input"
                        value={timezone}
                        onChange={(e) => setTimezone(e.target.value)}
                        style={{ width: '100%' }}
                    >
                        <option value="Asia/Kuala_Lumpur">Asia/Kuala_Lumpur (MYT +8)</option>
                        <option value="Asia/Singapore">Asia/Singapore (SGT +8)</option>
                        <option value="Asia/Jakarta">Asia/Jakarta (WIB +7)</option>
                        <option value="Asia/Bangkok">Asia/Bangkok (ICT +7)</option>
                        <option value="UTC">UTC</option>
                    </select>
                </div>

                {/* Revenue Calculations */}
                <div className="card" style={{ padding: 24 }}>
                    <h3 style={{ fontSize: 15, marginBottom: 16 }}>💰 Revenue Calculations</h3>
                    <p className="text-sm text-muted" style={{ marginBottom: 16 }}>
                        Used to estimate revenue recovered from AI-captured leads.
                    </p>
                    <div className="flex gap-sm">
                        <div style={{ flex: 1 }}>
                            <label className="text-sm" style={{ display: 'block', marginBottom: 6 }}>
                                ADR (Average Daily Rate, RM)
                            </label>
                            <input
                                type="number"
                                className="input"
                                value={adr}
                                onChange={(e) => setAdr(e.target.value)}
                                min="0"
                                step="10"
                                style={{ width: '100%' }}
                            />
                            <p className="text-xs text-muted" style={{ marginTop: 4 }}>
                                Revenue formula: leads × ADR × 20%
                            </p>
                        </div>
                        <div style={{ flex: 1 }}>
                            <label className="text-sm" style={{ display: 'block', marginBottom: 6 }}>
                                Staff Hourly Rate (RM)
                            </label>
                            <input
                                type="number"
                                className="input"
                                value={hourlyRate}
                                onChange={(e) => setHourlyRate(e.target.value)}
                                min="0"
                                step="5"
                                style={{ width: '100%' }}
                            />
                            <p className="text-xs text-muted" style={{ marginTop: 4 }}>
                                Cost savings: AI-handled × 15 min × this rate
                            </p>
                        </div>
                    </div>
                </div>

                {/* Brand Voice */}
                <div className="card" style={{ padding: 24 }}>
                    <h3 style={{ fontSize: 15, marginBottom: 16 }}>🗣️ Brand Voice</h3>
                    <p className="text-sm text-muted" style={{ marginBottom: 16 }}>
                        Guides how the AI speaks to your guests. Optional.
                    </p>
                    <label className="text-sm" style={{ display: 'block', marginBottom: 6 }}>
                        Brand Vocabulary / Tone Instructions
                    </label>
                    <textarea
                        className="input"
                        value={brandVocabulary}
                        onChange={(e) => setBrandVocabulary(e.target.value)}
                        placeholder={`Example:\n- Use "Welcome Home" instead of "Hello"\n- Always address guests as "Guest" not "Sir/Madam"\n- Formal but warm tone`}
                        rows={5}
                        style={{ width: '100%', resize: 'vertical', fontFamily: 'inherit', fontSize: 13 }}
                    />
                </div>

            </div>

            {/* Property Info (read-only) */}
            {settings && (
                <div className="card" style={{ padding: 24, marginTop: 24 }}>
                    <h3 style={{ fontSize: 15, marginBottom: 16 }}>🏨 Property Information</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
                        <div>
                            <div className="text-sm text-muted">Property Name</div>
                            <div className="text-sm" style={{ marginTop: 2, fontWeight: 500 }}>{settings.name}</div>
                        </div>
                        <div>
                            <div className="text-sm text-muted">WhatsApp Number</div>
                            <div className="text-sm" style={{ marginTop: 2, fontWeight: 500 }}>{settings.whatsapp_number || '—'}</div>
                        </div>
                        <div>
                            <div className="text-sm text-muted">Website</div>
                            <div className="text-sm" style={{ marginTop: 2, fontWeight: 500 }}>{settings.website_url || '—'}</div>
                        </div>
                        <div>
                            <div className="text-sm text-muted">Plan</div>
                            <div className="text-sm" style={{ marginTop: 2 }}>
                                <span className="badge badge-info">{settings.plan_tier}</span>
                            </div>
                        </div>
                        <div>
                            <div className="text-sm text-muted">Status</div>
                            <div className="text-sm" style={{ marginTop: 2 }}>
                                <span className={`badge ${settings.is_active ? 'badge-success' : 'badge-danger'}`}>
                                    {settings.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Save button */}
            <div className="flex items-center gap-sm" style={{ marginTop: 24 }}>
                <button
                    className="btn btn-primary"
                    onClick={save}
                    disabled={saving}
                >
                    {saving ? 'Saving...' : 'Save Settings'}
                </button>
                {saved && (
                    <span className="text-sm" style={{ color: 'var(--success)' }}>
                        ✓ Settings saved
                    </span>
                )}
            </div>
        </div>
    );
}
