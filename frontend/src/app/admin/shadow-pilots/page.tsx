'use client';

import { useEffect, useState, useRef } from 'react';
import { apiGet, apiPost, apiDelete } from '@/lib/api';

interface ShadowPilot {
    id: string;
    name: string;
    slug: string | null;
    tenant_name: string | null;
    shadow_pilot_mode: boolean;
    shadow_pilot_session_active: boolean;
    shadow_pilot_session_last_seen: string | null;
    shadow_pilot_start_date: string | null;
    shadow_pilot_phone: string | null;
    notification_email: string | null;
    is_active: boolean;
}

interface QRState {
    qr_base64: string | null;
    status: string;
}

function daysRunning(startDate: string | null): number | null {
    if (!startDate) return null;
    const start = new Date(startDate);
    const now = new Date();
    return Math.floor((now.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
}

function SessionBadge({ active, lastSeen }: { active: boolean; lastSeen: string | null }) {
    if (active) return <span className="badge badge-success">● Connected</span>;
    if (lastSeen) {
        const mins = Math.floor((Date.now() - new Date(lastSeen).getTime()) / 60000);
        if (mins < 5) return <span className="badge badge-success">● Connected</span>;
    }
    return <span className="badge badge-neutral">○ Disconnected</span>;
}

export default function ShadowPilotsPage() {
    const [properties, setProperties] = useState<ShadowPilot[]>([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [modalStep, setModalStep] = useState<'form' | 'qr'>('form');
    const [form, setForm] = useState({
        property_id: '',
        hotel_phone: '',
        gm_email: '',
        adr: '230',
        avg_stay_nights: '1',
        operating_hours_open: '09:00',
        operating_hours_close: '18:00',
    });
    const [provisionedId, setProvisionedId] = useState<string | null>(null);
    const [qrState, setQrState] = useState<QRState>({ qr_base64: null, status: 'waiting' });
    const [submitting, setSubmitting] = useState(false);
    const [disconnecting, setDisconnecting] = useState<string | null>(null);
    const qrPollRef = useRef<NodeJS.Timeout | null>(null);

    const load = () => {
        apiGet<ShadowPilot[]>('/superadmin/shadow-pilots')
            .then(setProperties)
            .catch(() => { })
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        load();
        const interval = setInterval(load, 30000);
        return () => clearInterval(interval);
    }, []);

    // Poll QR when modal is in QR step
    useEffect(() => {
        if (modalStep === 'qr' && provisionedId) {
            const poll = async () => {
                try {
                    const data = await apiGet<QRState>(`/superadmin/shadow-pilots/${provisionedId}/qr`);
                    setQrState(data);
                    if (data.status === 'connected') {
                        if (qrPollRef.current) clearInterval(qrPollRef.current);
                        load();
                    }
                } catch { }
            };
            poll();
            qrPollRef.current = setInterval(poll, 3000);
            return () => { if (qrPollRef.current) clearInterval(qrPollRef.current); };
        }
    }, [modalStep, provisionedId]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            const days: Record<string, { open: string; close: string }> = {};
            const weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
            weekdays.forEach(d => {
                days[d] = { open: form.operating_hours_open, close: form.operating_hours_close };
            });
            const result = await apiPost<{ property_id: string }>('/superadmin/shadow-pilots', {
                property_id: form.property_id,
                hotel_phone: form.hotel_phone,
                gm_email: form.gm_email,
                adr: parseFloat(form.adr),
                avg_stay_nights: parseFloat(form.avg_stay_nights),
                operating_hours: days,
            });
            setProvisionedId(result.property_id);
            setModalStep('qr');
        } catch (err: any) {
            alert(err?.message || 'Failed to provision shadow pilot');
        } finally {
            setSubmitting(false);
        }
    };

    const handleDisconnect = async (prop: ShadowPilot) => {
        if (!confirm(`Disconnect shadow pilot for ${prop.name}? The hotel's WhatsApp continues working normally.`)) return;
        setDisconnecting(prop.id);
        try {
            await apiDelete(`/superadmin/shadow-pilots/${prop.id}`);
            load();
        } catch {
            alert('Failed to disconnect');
        } finally {
            setDisconnecting(null);
        }
    };

    const closeModal = () => {
        if (qrPollRef.current) clearInterval(qrPollRef.current);
        setShowModal(false);
        setModalStep('form');
        setProvisionedId(null);
        setQrState({ qr_base64: null, status: 'waiting' });
        setForm({ property_id: '', hotel_phone: '', gm_email: '', adr: '230', avg_stay_nights: '1', operating_hours_open: '09:00', operating_hours_close: '18:00' });
    };

    const activePilots = properties.filter(p => p.shadow_pilot_mode);
    const availableProperties = properties.filter(p => !p.shadow_pilot_mode);

    if (loading) {
        return <div className="login-page"><div className="loader" /></div>;
    }

    return (
        <div>
            <div style={{ marginBottom: 32, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <h1>Shadow Pilots</h1>
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                        Baileys linked device — observes hotel's real WhatsApp for 7 days. No disruption. Day 7 report proves ROI.
                    </p>
                </div>
                <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                    + New Shadow Pilot
                </button>
            </div>

            {/* Active pilots */}
            <div className="card" style={{ marginBottom: 32 }}>
                <div className="card-header">
                    <h3 style={{ margin: 0 }}>Active Shadow Pilots ({activePilots.length})</h3>
                </div>
                {activePilots.length === 0 ? (
                    <div style={{ padding: '32px 24px', textAlign: 'center', color: 'var(--text-muted)' }}>
                        No active shadow pilots. Click "+ New Shadow Pilot" to start one.
                    </div>
                ) : (
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Property</th>
                                <th>Session</th>
                                <th>Day</th>
                                <th>Phone</th>
                                <th>GM Email</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {activePilots.map(prop => {
                                const days = daysRunning(prop.shadow_pilot_start_date);
                                return (
                                    <tr key={prop.id}>
                                        <td>
                                            <span className="font-medium">{prop.name}</span>
                                            <div className="text-xs text-muted">{prop.tenant_name ?? '—'}</div>
                                        </td>
                                        <td>
                                            <SessionBadge active={prop.shadow_pilot_session_active} lastSeen={prop.shadow_pilot_session_last_seen} />
                                        </td>
                                        <td>
                                            {days !== null ? (
                                                <span className={`badge ${days >= 7 ? 'badge-warning' : 'badge-success'}`}>
                                                    Day {days + 1}
                                                </span>
                                            ) : '—'}
                                        </td>
                                        <td className="text-sm">{prop.shadow_pilot_phone || '—'}</td>
                                        <td className="text-sm text-muted">{prop.notification_email || '—'}</td>
                                        <td>
                                            <button
                                                className="btn btn-danger btn-sm"
                                                onClick={() => handleDisconnect(prop)}
                                                disabled={disconnecting === prop.id}
                                            >
                                                {disconnecting === prop.id ? '...' : 'Disconnect'}
                                            </button>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Provision Modal */}
            {showModal && (
                <div style={{
                    position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
                }}>
                    <div style={{
                        background: 'var(--bg)', border: '1px solid var(--border)',
                        borderRadius: 12, padding: 32, width: 480, maxWidth: '95vw'
                    }}>
                        {modalStep === 'form' ? (
                            <>
                                <h3 style={{ margin: '0 0 20px' }}>New Shadow Pilot</h3>
                                <form onSubmit={handleSubmit}>
                                    <div style={{ marginBottom: 16 }}>
                                        <label className="form-label">Property</label>
                                        <select
                                            className="input"
                                            value={form.property_id}
                                            onChange={e => setForm(f => ({ ...f, property_id: e.target.value }))}
                                            required
                                        >
                                            <option value="">Select a property...</option>
                                            {availableProperties.map(p => (
                                                <option key={p.id} value={p.id}>{p.name} {p.tenant_name ? `(${p.tenant_name})` : ''}</option>
                                            ))}
                                        </select>
                                    </div>
                                    <div style={{ marginBottom: 16 }}>
                                        <label className="form-label">Hotel WhatsApp Number</label>
                                        <input
                                            className="input"
                                            placeholder="+60123456789"
                                            value={form.hotel_phone}
                                            onChange={e => setForm(f => ({ ...f, hotel_phone: e.target.value }))}
                                            required
                                        />
                                    </div>
                                    <div style={{ marginBottom: 16 }}>
                                        <label className="form-label">GM Email (for weekly report)</label>
                                        <input
                                            className="input"
                                            type="email"
                                            placeholder="gm@hotel.com"
                                            value={form.gm_email}
                                            onChange={e => setForm(f => ({ ...f, gm_email: e.target.value }))}
                                            required
                                        />
                                    </div>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                                        <div>
                                            <label className="form-label">ADR (RM)</label>
                                            <input
                                                className="input"
                                                type="number"
                                                value={form.adr}
                                                onChange={e => setForm(f => ({ ...f, adr: e.target.value }))}
                                                required
                                            />
                                        </div>
                                        <div>
                                            <label className="form-label">Avg Stay Nights</label>
                                            <input
                                                className="input"
                                                type="number"
                                                step="0.5"
                                                value={form.avg_stay_nights}
                                                onChange={e => setForm(f => ({ ...f, avg_stay_nights: e.target.value }))}
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 24 }}>
                                        <div>
                                            <label className="form-label">Operating Hours Open</label>
                                            <input
                                                className="input"
                                                type="time"
                                                value={form.operating_hours_open}
                                                onChange={e => setForm(f => ({ ...f, operating_hours_open: e.target.value }))}
                                            />
                                        </div>
                                        <div>
                                            <label className="form-label">Operating Hours Close</label>
                                            <input
                                                className="input"
                                                type="time"
                                                value={form.operating_hours_close}
                                                onChange={e => setForm(f => ({ ...f, operating_hours_close: e.target.value }))}
                                            />
                                        </div>
                                    </div>
                                    <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                                        <button type="button" className="btn btn-ghost" onClick={closeModal}>Cancel</button>
                                        <button type="submit" className="btn btn-primary" disabled={submitting}>
                                            {submitting ? 'Provisioning...' : 'Provision + Get QR'}
                                        </button>
                                    </div>
                                </form>
                            </>
                        ) : (
                            <>
                                <h3 style={{ margin: '0 0 8px' }}>Scan WhatsApp QR Code</h3>
                                <p className="text-sm text-muted" style={{ marginBottom: 24 }}>
                                    Have the hotel GM open WhatsApp → Linked Devices → Link a Device, then scan this QR.
                                </p>
                                <div style={{ textAlign: 'center', minHeight: 240, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    {qrState.status === 'connected' ? (
                                        <div style={{ color: 'var(--success)', fontSize: 16, fontWeight: 500 }}>
                                            <div style={{ fontSize: 40, marginBottom: 12 }}>✓</div>
                                            Connected to hotel's WhatsApp
                                        </div>
                                    ) : qrState.qr_base64 ? (
                                        <img src={qrState.qr_base64} alt="WhatsApp QR Code" style={{ width: 200, height: 200 }} />
                                    ) : (
                                        <div style={{ color: 'var(--text-muted)' }}>
                                            <div className="loader" style={{ marginBottom: 12 }} />
                                            Generating QR code...
                                        </div>
                                    )}
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 24 }}>
                                    <button className="btn btn-ghost" onClick={closeModal}>
                                        {qrState.status === 'connected' ? 'Done' : 'Close (pilot still activating)'}
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
