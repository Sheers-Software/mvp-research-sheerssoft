'use client';

import { useState } from 'react';
import { apiPost } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { useTenant } from '@/lib/tenant-context';
import Link from 'next/link';

const TIMEZONES = [
    'Asia/Kuala_Lumpur',
    'Asia/Singapore',
    'Asia/Bangkok',
    'Asia/Jakarta',
    'Asia/Manila',
    'Asia/Tokyo',
    'Asia/Seoul',
    'Asia/Hong_Kong',
    'Asia/Colombo',
    'Asia/Kolkata',
    'Asia/Dubai',
    'Europe/London',
    'America/New_York',
    'America/Los_Angeles',
    'Australia/Sydney',
];

export default function PortalPropertiesPage() {
    const { user } = useAuth();
    const { tenantId, properties, loading, refresh } = useTenant();
    const [showAddForm, setShowAddForm] = useState(false);
    const [addForm, setAddForm] = useState({ property_name: '', timezone: 'Asia/Kuala_Lumpur' });
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const isOwnerOrAdmin = user?.role === 'owner' || user?.role === 'admin' || user?.is_superadmin;

    const handleAdd = async () => {
        if (!addForm.property_name.trim() || !tenantId) return;
        setSaving(true);
        setError('');
        setSuccess('');
        try {
            await apiPost(`/onboarding/add-property/${tenantId}`, addForm);
            setSuccess(`Property "${addForm.property_name}" created successfully`);
            setAddForm({ property_name: '', timezone: 'Asia/Kuala_Lumpur' });
            setShowAddForm(false);
            refresh();
        } catch (e: unknown) {
            setError((e instanceof Error ? e.message : String(e)) || 'Failed to add property');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div>
            <div className="flex items-center justify-between" style={{ marginBottom: 28 }}>
                <div>
                    <h1>Properties</h1>
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                        Manage your hotel properties
                    </p>
                </div>
                {isOwnerOrAdmin && (
                    <button
                        className="btn btn-primary btn-sm"
                        onClick={() => { setShowAddForm(!showAddForm); setError(''); setSuccess(''); }}
                    >
                        + Add Property
                    </button>
                )}
            </div>

            {error && <div style={{ color: 'var(--danger)', marginBottom: 12, fontSize: 13 }}>{error}</div>}
            {success && <div style={{ color: 'var(--success)', marginBottom: 12, fontSize: 13 }}>{success}</div>}

            {/* Add Property form */}
            {showAddForm && (
                <div className="card animate-in" style={{ marginBottom: 20, borderColor: 'rgba(99,102,241,0.3)', padding: 24 }}>
                    <h3 style={{ marginBottom: 16, fontSize: 14 }}>Add New Property</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                        <div>
                            <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Property Name</label>
                            <input
                                type="text"
                                value={addForm.property_name}
                                onChange={(e) => setAddForm((f) => ({ ...f, property_name: e.target.value }))}
                                placeholder="e.g. Grand Palace Hotel KL"
                                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13, boxSizing: 'border-box' }}
                            />
                        </div>
                        <div>
                            <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Timezone</label>
                            <select
                                value={addForm.timezone}
                                onChange={(e) => setAddForm((f) => ({ ...f, timezone: e.target.value }))}
                                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13 }}
                            >
                                {TIMEZONES.map((tz) => (
                                    <option key={tz} value={tz}>{tz}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                    <div className="flex items-center gap-sm">
                        <button
                            className="btn btn-primary btn-sm"
                            onClick={handleAdd}
                            disabled={saving}
                        >
                            {saving ? 'Creating…' : 'Create Property'}
                        </button>
                        <button
                            className="btn btn-ghost btn-sm"
                            onClick={() => { setShowAddForm(false); setAddForm({ property_name: '', timezone: 'Asia/Kuala_Lumpur' }); }}
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}

            {/* Properties list */}
            {loading ? (
                <div className="flex justify-center" style={{ padding: 60 }}>
                    <div className="loader" />
                </div>
            ) : properties.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">🏨</div>
                    <p>No properties yet</p>
                    <p className="text-sm text-muted" style={{ marginTop: 4 }}>
                        Add your first property to get started
                    </p>
                </div>
            ) : (
                <div style={{ display: 'grid', gap: 16 }}>
                    {properties.map((prop) => (
                        <div key={prop.id} className="card animate-in" style={{ padding: 20 }}>
                            <div className="flex items-center justify-between">
                                <div style={{ flex: 1 }}>
                                    <div className="flex items-center gap-sm" style={{ marginBottom: 8 }}>
                                        <span style={{ fontWeight: 600, fontSize: 15 }}>{prop.name}</span>
                                        <span className={`badge ${prop.is_active ? 'badge-success' : 'badge-warning'}`}>
                                            {prop.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </div>

                                    {/* Onboarding score */}
                                    <div style={{ marginBottom: 10, maxWidth: 280 }}>
                                        <div className="flex items-center justify-between" style={{ marginBottom: 4 }}>
                                            <span className="text-xs text-muted">Setup progress</span>
                                            <span className="text-xs text-muted">{prop.onboarding_score}%</span>
                                        </div>
                                        <div style={{ height: 5, background: 'var(--border-subtle)', borderRadius: 4, overflow: 'hidden' }}>
                                            <div
                                                style={{
                                                    height: '100%',
                                                    width: `${prop.onboarding_score}%`,
                                                    background: prop.onboarding_score >= 75 ? 'var(--success)' : prop.onboarding_score >= 40 ? 'var(--warning)' : 'var(--accent)',
                                                    borderRadius: 4,
                                                }}
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-sm">
                                    <Link href={`/portal/kb/${prop.id}`} className="btn btn-ghost btn-sm">
                                        📚 Manage KB
                                    </Link>
                                    <Link href="/portal/channels" className="btn btn-ghost btn-sm">
                                        📡 Channels
                                    </Link>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
