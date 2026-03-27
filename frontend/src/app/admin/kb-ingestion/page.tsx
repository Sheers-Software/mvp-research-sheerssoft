'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiGet, apiPost } from '@/lib/api';

interface Tenant {
    id: string;
    name: string;
    slug: string;
}

interface Property {
    id: string;
    name: string;
    slug: string;
}

interface Room {
    name: string;
    description: string;
    rate_myr: string;
}

interface Faq {
    question: string;
    answer: string;
}

interface KbForm {
    property_name: string;
    rooms: Room[];
    facilities: string;
    faqs: Faq[];
    policies: {
        checkin: string;
        checkout: string;
        cancellation: string;
    };
    contact: {
        phone: string;
        email: string;
        address: string;
        website: string;
    };
}

interface IngestResult {
    docs_created: number;
    property_id: string;
    message?: string;
}

const defaultForm = (): KbForm => ({
    property_name: '',
    rooms: [
        { name: '', description: '', rate_myr: '' },
        { name: '', description: '', rate_myr: '' },
    ],
    facilities: '',
    faqs: [
        { question: '', answer: '' },
        { question: '', answer: '' },
        { question: '', answer: '' },
    ],
    policies: {
        checkin: '',
        checkout: '',
        cancellation: '',
    },
    contact: {
        phone: '',
        email: '',
        address: '',
        website: '',
    },
});

export default function KbIngestionPage() {
    const searchParams = useSearchParams();
    const router = useRouter();

    const [tenants, setTenants] = useState<Tenant[]>([]);
    const [selectedTenantId, setSelectedTenantId] = useState<string | null>(
        searchParams.get('tenantId') || null
    );
    const [properties, setProperties] = useState<Property[]>([]);
    const [selectedPropertyId, setSelectedPropertyId] = useState<string | null>(
        searchParams.get('propertyId') || null
    );
    const [loading, setLoading] = useState(true);
    const [propertiesLoading, setPropertiesLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [result, setResult] = useState<IngestResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [form, setForm] = useState<KbForm>(defaultForm());

    // Load tenants on mount
    useEffect(() => {
        apiGet<{ tenants: Tenant[] }>('/superadmin/tenants')
            .then((data) => setTenants(data.tenants || []))
            .catch(() => {})
            .finally(() => setLoading(false));
    }, []);

    // Load properties when tenant selected
    useEffect(() => {
        if (!selectedTenantId) {
            setProperties([]);
            setSelectedPropertyId(null);
            return;
        }
        setPropertiesLoading(true);
        apiGet<{ properties: Property[] }>(`/superadmin/tenants/${selectedTenantId}`)
            .then((data) => {
                setProperties(data.properties || []);
                // If propertyId is in query params and matches this tenant, keep selection
                const qpPropId = searchParams.get('propertyId');
                if (qpPropId && data.properties?.some((p: Property) => p.id === qpPropId)) {
                    setSelectedPropertyId(qpPropId);
                }
            })
            .catch(() => {})
            .finally(() => setPropertiesLoading(false));
    }, [selectedTenantId]); // eslint-disable-line react-hooks/exhaustive-deps

    // Pre-fill property name when property is selected
    useEffect(() => {
        if (!selectedPropertyId) return;
        const prop = properties.find((p) => p.id === selectedPropertyId);
        if (prop) {
            setForm((f) => ({ ...f, property_name: prop.name }));
        }
    }, [selectedPropertyId, properties]);

    // --- Form helpers ---

    const updateRoom = (idx: number, field: keyof Room, value: string) => {
        setForm((f) => {
            const rooms = [...f.rooms];
            rooms[idx] = { ...rooms[idx], [field]: value };
            return { ...f, rooms };
        });
    };

    const addRoom = () =>
        setForm((f) => ({ ...f, rooms: [...f.rooms, { name: '', description: '', rate_myr: '' }] }));

    const removeRoom = (idx: number) =>
        setForm((f) => ({ ...f, rooms: f.rooms.filter((_, i) => i !== idx) }));

    const updateFaq = (idx: number, field: keyof Faq, value: string) => {
        setForm((f) => {
            const faqs = [...f.faqs];
            faqs[idx] = { ...faqs[idx], [field]: value };
            return { ...f, faqs };
        });
    };

    const addFaq = () =>
        setForm((f) => ({ ...f, faqs: [...f.faqs, { question: '', answer: '' }] }));

    const removeFaq = (idx: number) =>
        setForm((f) => ({ ...f, faqs: f.faqs.filter((_, i) => i !== idx) }));

    // --- Submit ---

    const handleIngest = async () => {
        if (!selectedPropertyId) return;
        setSaving(true);
        setError(null);
        setResult(null);
        try {
            const payload = {
                property_name: form.property_name,
                rooms: form.rooms.filter((r) => r.name.trim()),
                facilities: form.facilities,
                faqs: form.faqs.filter((f) => f.question.trim()),
                policies: form.policies,
                contact: form.contact,
            };
            const res = await apiPost<IngestResult>(
                `/properties/${selectedPropertyId}/kb/ingest-wizard`,
                payload
            );
            setResult(res);
        } catch (err: any) {
            setError(err.message || 'Ingestion failed.');
        } finally {
            setSaving(false);
        }
    };

    // --- Render ---

    const selectedTenant = tenants.find((t) => t.id === selectedTenantId);
    const selectedProperty = properties.find((p) => p.id === selectedPropertyId);

    const inputStyle: React.CSSProperties = {
        width: '100%',
        padding: '8px 12px',
        border: '1px solid var(--border)',
        borderRadius: 6,
        fontSize: 14,
        background: 'var(--bg-secondary)',
        color: 'var(--text)',
        boxSizing: 'border-box',
    };

    const textareaStyle: React.CSSProperties = {
        ...inputStyle,
        minHeight: 80,
        resize: 'vertical',
        fontFamily: 'inherit',
    };

    const selectStyle: React.CSSProperties = {
        ...inputStyle,
        cursor: 'pointer',
    };

    return (
        <div className="animate-in" style={{ maxWidth: 900, margin: '0 auto' }}>
            {/* Header */}
            <div style={{ marginBottom: 32 }}>
                <h1 style={{ marginBottom: 4 }}>KB Ingestion Tool</h1>
                <p className="text-muted text-sm">Set up knowledge base for a client property</p>
            </div>

            {/* Step 1: Tenant + Property selection */}
            <div className="card" style={{ padding: 24, marginBottom: 24 }}>
                <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>
                    Step 1 — Select Client &amp; Property
                </h3>
                <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                    <div>
                        <label className="text-sm" style={{ display: 'block', marginBottom: 6, fontWeight: 500 }}>
                            Tenant / Client
                        </label>
                        {loading ? (
                            <div className="loader" style={{ width: 20, height: 20 }} />
                        ) : (
                            <select
                                style={selectStyle}
                                value={selectedTenantId || ''}
                                onChange={(e) => {
                                    setSelectedTenantId(e.target.value || null);
                                    setSelectedPropertyId(null);
                                    setResult(null);
                                    setForm(defaultForm());
                                }}
                            >
                                <option value="">— Select a tenant —</option>
                                {tenants.map((t) => (
                                    <option key={t.id} value={t.id}>
                                        {t.name}
                                    </option>
                                ))}
                            </select>
                        )}
                    </div>
                    <div>
                        <label className="text-sm" style={{ display: 'block', marginBottom: 6, fontWeight: 500 }}>
                            Property
                        </label>
                        {propertiesLoading ? (
                            <div className="loader" style={{ width: 20, height: 20 }} />
                        ) : (
                            <select
                                style={selectStyle}
                                value={selectedPropertyId || ''}
                                disabled={!selectedTenantId}
                                onChange={(e) => {
                                    setSelectedPropertyId(e.target.value || null);
                                    setResult(null);
                                }}
                            >
                                <option value="">
                                    {!selectedTenantId ? '— Select a tenant first —' : '— Select a property —'}
                                </option>
                                {properties.map((p) => (
                                    <option key={p.id} value={p.id}>
                                        {p.name}
                                    </option>
                                ))}
                            </select>
                        )}
                    </div>
                </div>
            </div>

            {/* Step 2: KB Form — shown only after property selected */}
            {selectedPropertyId && (
                <div className="animate-in">
                    <div className="card" style={{ padding: 24, marginBottom: 24 }}>
                        <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 4 }}>
                            Step 2 — Knowledge Base Content
                        </h3>
                        <p className="text-muted text-sm" style={{ marginBottom: 24 }}>
                            Filling in for: <strong>{selectedProperty?.name}</strong>
                            {selectedTenant && (
                                <span> ({selectedTenant.name})</span>
                            )}
                        </p>

                        {/* Property Info */}
                        <section style={{ marginBottom: 32 }}>
                            <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, paddingBottom: 8, borderBottom: '1px solid var(--border)' }}>
                                Property Info
                            </h4>
                            <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                                <div>
                                    <label className="text-sm" style={{ display: 'block', marginBottom: 6 }}>Display Name</label>
                                    <input
                                        style={inputStyle}
                                        value={form.property_name}
                                        onChange={(e) => setForm((f) => ({ ...f, property_name: e.target.value }))}
                                        placeholder="e.g. The Grand Hotel KL"
                                    />
                                </div>
                                <div>
                                    <label className="text-sm" style={{ display: 'block', marginBottom: 6 }}>Phone</label>
                                    <input
                                        style={inputStyle}
                                        value={form.contact.phone}
                                        onChange={(e) => setForm((f) => ({ ...f, contact: { ...f.contact, phone: e.target.value } }))}
                                        placeholder="+60 3-1234 5678"
                                    />
                                </div>
                                <div>
                                    <label className="text-sm" style={{ display: 'block', marginBottom: 6 }}>Email</label>
                                    <input
                                        style={inputStyle}
                                        type="email"
                                        value={form.contact.email}
                                        onChange={(e) => setForm((f) => ({ ...f, contact: { ...f.contact, email: e.target.value } }))}
                                        placeholder="reservations@hotel.com"
                                    />
                                </div>
                                <div>
                                    <label className="text-sm" style={{ display: 'block', marginBottom: 6 }}>Website</label>
                                    <input
                                        style={inputStyle}
                                        type="url"
                                        value={form.contact.website}
                                        onChange={(e) => setForm((f) => ({ ...f, contact: { ...f.contact, website: e.target.value } }))}
                                        placeholder="https://www.hotel.com"
                                    />
                                </div>
                                <div style={{ gridColumn: '1 / -1' }}>
                                    <label className="text-sm" style={{ display: 'block', marginBottom: 6 }}>Address</label>
                                    <input
                                        style={inputStyle}
                                        value={form.contact.address}
                                        onChange={(e) => setForm((f) => ({ ...f, contact: { ...f.contact, address: e.target.value } }))}
                                        placeholder="123 Jalan Bukit Bintang, 55100 Kuala Lumpur"
                                    />
                                </div>
                            </div>
                        </section>

                        {/* Rooms */}
                        <section style={{ marginBottom: 32 }}>
                            <div className="flex items-center justify-between" style={{ marginBottom: 12, paddingBottom: 8, borderBottom: '1px solid var(--border)' }}>
                                <h4 style={{ fontSize: 14, fontWeight: 600 }}>Rooms</h4>
                                <button className="btn btn-ghost btn-sm" onClick={addRoom}>+ Add Room</button>
                            </div>
                            <div style={{ overflowX: 'auto' }}>
                                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                    <thead>
                                        <tr style={{ textAlign: 'left' }}>
                                            <th className="text-sm text-muted" style={{ padding: '0 8px 8px 0', fontWeight: 500, width: '25%' }}>Room Name</th>
                                            <th className="text-sm text-muted" style={{ padding: '0 8px 8px 0', fontWeight: 500 }}>Description</th>
                                            <th className="text-sm text-muted" style={{ padding: '0 8px 8px 0', fontWeight: 500, width: 140 }}>Rate (RM/night)</th>
                                            <th style={{ width: 36 }} />
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {form.rooms.map((room, idx) => (
                                            <tr key={idx}>
                                                <td style={{ padding: '4px 8px 4px 0', verticalAlign: 'top' }}>
                                                    <input
                                                        style={inputStyle}
                                                        value={room.name}
                                                        onChange={(e) => updateRoom(idx, 'name', e.target.value)}
                                                        placeholder="Deluxe Room"
                                                    />
                                                </td>
                                                <td style={{ padding: '4px 8px 4px 0', verticalAlign: 'top' }}>
                                                    <input
                                                        style={inputStyle}
                                                        value={room.description}
                                                        onChange={(e) => updateRoom(idx, 'description', e.target.value)}
                                                        placeholder="King bed, city view, 35 sqm…"
                                                    />
                                                </td>
                                                <td style={{ padding: '4px 8px 4px 0', verticalAlign: 'top' }}>
                                                    <input
                                                        style={inputStyle}
                                                        value={room.rate_myr}
                                                        onChange={(e) => updateRoom(idx, 'rate_myr', e.target.value)}
                                                        placeholder="350"
                                                        type="number"
                                                        min="0"
                                                    />
                                                </td>
                                                <td style={{ padding: '4px 0', verticalAlign: 'top', textAlign: 'center' }}>
                                                    <button
                                                        className="btn btn-ghost btn-sm"
                                                        onClick={() => removeRoom(idx)}
                                                        style={{ color: 'var(--danger)', padding: '6px 8px' }}
                                                        title="Remove row"
                                                    >
                                                        ×
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </section>

                        {/* Facilities */}
                        <section style={{ marginBottom: 32 }}>
                            <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, paddingBottom: 8, borderBottom: '1px solid var(--border)' }}>
                                Facilities
                            </h4>
                            <label className="text-sm text-muted" style={{ display: 'block', marginBottom: 6 }}>
                                List facilities separated by commas or one per line
                            </label>
                            <textarea
                                style={textareaStyle}
                                value={form.facilities}
                                onChange={(e) => setForm((f) => ({ ...f, facilities: e.target.value }))}
                                placeholder={"Swimming Pool\nFitness Centre\nFree WiFi\nParking\nRestaurant"}
                                rows={5}
                            />
                        </section>

                        {/* FAQs */}
                        <section style={{ marginBottom: 32 }}>
                            <div className="flex items-center justify-between" style={{ marginBottom: 12, paddingBottom: 8, borderBottom: '1px solid var(--border)' }}>
                                <h4 style={{ fontSize: 14, fontWeight: 600 }}>FAQs</h4>
                                <button className="btn btn-ghost btn-sm" onClick={addFaq}>+ Add FAQ</button>
                            </div>
                            <div className="flex flex-col gap-sm">
                                {form.faqs.map((faq, idx) => (
                                    <div key={idx} className="card" style={{ padding: 16, position: 'relative' }}>
                                        <button
                                            className="btn btn-ghost btn-sm"
                                            onClick={() => removeFaq(idx)}
                                            style={{
                                                position: 'absolute',
                                                top: 12,
                                                right: 12,
                                                color: 'var(--danger)',
                                                padding: '2px 8px',
                                            }}
                                            title="Remove FAQ"
                                        >
                                            ×
                                        </button>
                                        <div style={{ paddingRight: 40 }}>
                                            <div style={{ marginBottom: 8 }}>
                                                <label className="text-sm" style={{ display: 'block', marginBottom: 4, fontWeight: 500 }}>
                                                    Q{idx + 1}. Question
                                                </label>
                                                <input
                                                    style={inputStyle}
                                                    value={faq.question}
                                                    onChange={(e) => updateFaq(idx, 'question', e.target.value)}
                                                    placeholder="What time is breakfast served?"
                                                />
                                            </div>
                                            <div>
                                                <label className="text-sm" style={{ display: 'block', marginBottom: 4, fontWeight: 500 }}>
                                                    Answer
                                                </label>
                                                <textarea
                                                    style={{ ...textareaStyle, minHeight: 60 }}
                                                    value={faq.answer}
                                                    onChange={(e) => updateFaq(idx, 'answer', e.target.value)}
                                                    placeholder="Breakfast is served from 7:00 AM to 10:30 AM at The Garden Restaurant…"
                                                    rows={2}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                ))}
                                {form.faqs.length === 0 && (
                                    <p className="text-muted text-sm">No FAQs added. Click "+ Add FAQ" to add one.</p>
                                )}
                            </div>
                        </section>

                        {/* Policies */}
                        <section style={{ marginBottom: 32 }}>
                            <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, paddingBottom: 8, borderBottom: '1px solid var(--border)' }}>
                                Policies
                            </h4>
                            <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                                <div>
                                    <label className="text-sm" style={{ display: 'block', marginBottom: 6 }}>Check-in Time</label>
                                    <input
                                        style={inputStyle}
                                        value={form.policies.checkin}
                                        onChange={(e) => setForm((f) => ({ ...f, policies: { ...f.policies, checkin: e.target.value } }))}
                                        placeholder="3:00 PM"
                                    />
                                </div>
                                <div>
                                    <label className="text-sm" style={{ display: 'block', marginBottom: 6 }}>Check-out Time</label>
                                    <input
                                        style={inputStyle}
                                        value={form.policies.checkout}
                                        onChange={(e) => setForm((f) => ({ ...f, policies: { ...f.policies, checkout: e.target.value } }))}
                                        placeholder="12:00 PM"
                                    />
                                </div>
                                <div style={{ gridColumn: '1 / -1' }}>
                                    <label className="text-sm" style={{ display: 'block', marginBottom: 6 }}>Cancellation Policy</label>
                                    <textarea
                                        style={textareaStyle}
                                        value={form.policies.cancellation}
                                        onChange={(e) => setForm((f) => ({ ...f, policies: { ...f.policies, cancellation: e.target.value } }))}
                                        placeholder="Free cancellation up to 48 hours before check-in. Late cancellations are charged one night's stay."
                                        rows={3}
                                    />
                                </div>
                            </div>
                        </section>

                        {/* Error */}
                        {error && (
                            <div style={{ padding: 16, background: 'var(--danger-light)', borderRadius: 8, marginBottom: 16 }}>
                                <p className="text-danger text-sm">{error}</p>
                            </div>
                        )}

                        {/* Submit */}
                        <div className="flex items-center gap-sm">
                            <button
                                className="btn btn-primary"
                                onClick={handleIngest}
                                disabled={saving || !selectedPropertyId}
                            >
                                {saving ? 'Ingesting…' : 'Ingest KB'}
                            </button>
                            {saving && <div className="loader" style={{ width: 18, height: 18 }} />}
                        </div>
                    </div>

                    {/* Result card */}
                    {result && (
                        <div
                            className="card animate-in"
                            style={{
                                padding: 24,
                                borderLeft: '4px solid var(--success)',
                                marginBottom: 24,
                            }}
                        >
                            <div className="flex items-center gap-sm" style={{ marginBottom: 12 }}>
                                <span style={{ fontSize: 20 }}>✅</span>
                                <h3 style={{ fontSize: 16, fontWeight: 600 }}>KB Ingestion Successful</h3>
                            </div>
                            <p className="text-sm" style={{ marginBottom: 16 }}>
                                <strong>{result.docs_created}</strong> document{result.docs_created !== 1 ? 's' : ''} created and embedded for{' '}
                                <strong>{selectedProperty?.name}</strong>.
                            </p>
                            {result.message && (
                                <p className="text-muted text-sm" style={{ marginBottom: 16 }}>{result.message}</p>
                            )}
                            <div className="flex gap-sm">
                                <Link
                                    href={`/admin/tenants/${selectedTenantId}`}
                                    className="btn btn-primary btn-sm"
                                >
                                    View Tenant Detail →
                                </Link>
                                <button
                                    className="btn btn-ghost btn-sm"
                                    onClick={() => {
                                        setResult(null);
                                        setForm(defaultForm());
                                        setSelectedPropertyId(null);
                                    }}
                                >
                                    Ingest Another Property
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Empty state before selection */}
            {!selectedPropertyId && !loading && (
                <div className="empty-state" style={{ paddingTop: 40 }}>
                    <div className="empty-icon">📚</div>
                    <p className="text-muted">Select a tenant and property above to begin KB setup.</p>
                </div>
            )}
        </div>
    );
}
