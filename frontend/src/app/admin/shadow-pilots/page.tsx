'use client';

import { useEffect, useState } from 'react';
import { apiGet, apiPatch } from '@/lib/api';

interface ShadowProperty {
    id: string;
    name: string;
    tenant_name: string | null;
    tenant_id: string | null;
    audit_only_mode: boolean;
    shadow_pilot_phone: string | null;
    shadow_pilot_start_date: string | null;
    notification_email: string | null;
    is_active: boolean;
    created_at: string | null;
}

function daysRunning(startDate: string | null): number | null {
    if (!startDate) return null;
    const start = new Date(startDate);
    const now = new Date();
    return Math.floor((now.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
}

export default function ShadowPilotsPage() {
    const [properties, setProperties] = useState<ShadowProperty[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState<string | null>(null);
    const [editPhone, setEditPhone] = useState<Record<string, string>>({});
    const [phoneEdit, setPhoneEdit] = useState<string | null>(null);

    useEffect(() => {
        apiGet<ShadowProperty[]>('/superadmin/shadow-pilots')
            .then(setProperties)
            .catch(() => { })
            .finally(() => setLoading(false));
    }, []);

    const toggleAuditMode = async (prop: ShadowProperty) => {
        setSaving(prop.id);
        try {
            const updated = await apiPatch<ShadowProperty>(
                `/superadmin/shadow-pilots/${prop.id}`,
                { audit_only_mode: !prop.audit_only_mode }
            );
            setProperties(prev =>
                prev.map(p => p.id === prop.id ? { ...p, ...updated } : p)
            );
        } catch {
            alert('Failed to update shadow pilot mode');
        } finally {
            setSaving(null);
        }
    };

    const savePhone = async (prop: ShadowProperty) => {
        const phone = editPhone[prop.id] ?? prop.shadow_pilot_phone ?? '';
        setSaving(prop.id);
        try {
            const updated = await apiPatch<ShadowProperty>(
                `/superadmin/shadow-pilots/${prop.id}`,
                { shadow_pilot_phone: phone || null }
            );
            setProperties(prev =>
                prev.map(p => p.id === prop.id ? { ...p, ...updated } : p)
            );
            setPhoneEdit(null);
        } catch {
            alert('Failed to save phone number');
        } finally {
            setSaving(null);
        }
    };

    const activePilots = properties.filter(p => p.audit_only_mode);
    const allProperties = properties.filter(p => !p.audit_only_mode);

    if (loading) {
        return (
            <div className="login-page">
                <div className="loader" />
            </div>
        );
    }

    return (
        <div>
            <div style={{ marginBottom: 32 }}>
                <h1>Shadow Pilots</h1>
                <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                    Stage 2 of the sales funnel. Properties in audit-only mode log inquiries silently — no AI reply is sent. Weekly reports email the GM their missed-revenue estimate.
                </p>
            </div>

            {/* Active shadow pilots */}
            <div className="card" style={{ marginBottom: 32 }}>
                <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <h3 style={{ margin: 0 }}>Active Shadow Pilots</h3>
                        <p className="text-muted text-sm" style={{ margin: '4px 0 0' }}>
                            {activePilots.length} {activePilots.length === 1 ? 'property' : 'properties'} currently in audit-only mode
                        </p>
                    </div>
                </div>

                {activePilots.length === 0 ? (
                    <div style={{ padding: '32px 24px', textAlign: 'center', color: 'var(--text-muted)' }}>
                        No active shadow pilots. Enable audit-only mode on a property below to start a shadow pilot.
                    </div>
                ) : (
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Property</th>
                                <th>Tenant</th>
                                <th>Shadow Number</th>
                                <th>Days Running</th>
                                <th>Weekly Email To</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {activePilots.map(prop => {
                                const days = daysRunning(prop.shadow_pilot_start_date);
                                const isEditing = phoneEdit === prop.id;
                                return (
                                    <tr key={prop.id}>
                                        <td>
                                            <span className="font-medium">{prop.name}</span>
                                        </td>
                                        <td className="text-sm text-muted">
                                            {prop.tenant_name ?? '—'}
                                        </td>
                                        <td>
                                            {isEditing ? (
                                                <div style={{ display: 'flex', gap: 4 }}>
                                                    <input
                                                        className="input input-sm"
                                                        style={{ width: 140 }}
                                                        value={editPhone[prop.id] ?? prop.shadow_pilot_phone ?? ''}
                                                        onChange={e => setEditPhone(prev => ({ ...prev, [prop.id]: e.target.value }))}
                                                        onKeyDown={e => e.key === 'Enter' && savePhone(prop)}
                                                        placeholder="+601X-XXXXXXX"
                                                        autoFocus
                                                    />
                                                    <button
                                                        className="btn btn-primary btn-sm"
                                                        onClick={() => savePhone(prop)}
                                                        disabled={saving === prop.id}
                                                    >Save</button>
                                                    <button
                                                        className="btn btn-ghost btn-sm"
                                                        onClick={() => setPhoneEdit(null)}
                                                    >✕</button>
                                                </div>
                                            ) : (
                                                <span
                                                    className="text-sm"
                                                    style={{ cursor: 'pointer', borderBottom: '1px dashed var(--border-subtle)' }}
                                                    onClick={() => { setPhoneEdit(prop.id); setEditPhone(prev => ({ ...prev, [prop.id]: prop.shadow_pilot_phone ?? '' })); }}
                                                >
                                                    {prop.shadow_pilot_phone || <span className="text-muted">Click to set number</span>}
                                                </span>
                                            )}
                                        </td>
                                        <td>
                                            {days !== null ? (
                                                <span className={`badge ${days >= 7 ? 'badge-warning' : 'badge-success'}`}>
                                                    Day {days + 1}
                                                </span>
                                            ) : '—'}
                                        </td>
                                        <td className="text-sm text-muted">
                                            {prop.notification_email ?? 'Not configured'}
                                        </td>
                                        <td>
                                            <button
                                                className="btn btn-danger btn-sm"
                                                onClick={() => toggleAuditMode(prop)}
                                                disabled={saving === prop.id}
                                            >
                                                {saving === prop.id ? '...' : 'Deactivate'}
                                            </button>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </div>

            {/* All other properties */}
            <div className="card">
                <div className="card-header">
                    <h3 style={{ margin: 0 }}>All Properties</h3>
                    <p className="text-muted text-sm" style={{ margin: '4px 0 0' }}>
                        Click "Start Shadow Pilot" to activate audit-only mode on a property
                    </p>
                </div>
                <table className="table">
                    <thead>
                        <tr>
                            <th>Property</th>
                            <th>Tenant</th>
                            <th>Status</th>
                            <th>Shadow Pilot</th>
                        </tr>
                    </thead>
                    <tbody>
                        {allProperties.length === 0 ? (
                            <tr>
                                <td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 24 }}>
                                    All properties are currently in shadow pilot mode.
                                </td>
                            </tr>
                        ) : (
                            allProperties.map(prop => (
                                <tr key={prop.id}>
                                    <td className="font-medium">{prop.name}</td>
                                    <td className="text-sm text-muted">{prop.tenant_name ?? '—'}</td>
                                    <td>
                                        <span className={`badge ${prop.is_active ? 'badge-success' : 'badge-neutral'}`}>
                                            {prop.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td>
                                        <button
                                            className="btn btn-primary btn-sm"
                                            onClick={() => toggleAuditMode(prop)}
                                            disabled={saving === prop.id}
                                        >
                                            {saving === prop.id ? '...' : 'Start Shadow Pilot'}
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
