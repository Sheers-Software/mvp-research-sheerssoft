'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiGet, apiPost } from '@/lib/api';
import { useAuth } from '@/lib/auth';

interface RoomRow {
    name: string;
    description: string;
    rate: string;
}

interface FaqRow {
    question: string;
    answer: string;
}

interface WizardData {
    propertyInfo: { address: string; phone: string; email: string; website: string };
    rooms: RoomRow[];
    facilities: string;
    faqs: FaqRow[];
    policies: { checkin: string; checkout: string; cancellation: string };
}

const TOTAL_STEPS = 6;

function StepIndicator({ current }: { current: number }) {
    return (
        <div className="flex items-center justify-center" style={{ gap: 8, marginBottom: 32 }}>
            {Array.from({ length: TOTAL_STEPS }, (_, i) => {
                const step = i + 1;
                const done = step < current;
                const active = step === current;
                return (
                    <div key={step} style={{ display: 'flex', alignItems: 'center' }}>
                        <div
                            style={{
                                width: 32,
                                height: 32,
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: 13,
                                fontWeight: 700,
                                background: done ? 'var(--success)' : active ? 'var(--accent)' : 'var(--border-subtle)',
                                color: done || active ? 'white' : 'var(--text-muted)',
                                transition: 'all 0.2s',
                            }}
                        >
                            {done ? '✓' : step}
                        </div>
                        {step < TOTAL_STEPS && (
                            <div
                                style={{
                                    width: 32,
                                    height: 2,
                                    background: done ? 'var(--success)' : 'var(--border-subtle)',
                                    transition: 'background 0.2s',
                                }}
                            />
                        )}
                    </div>
                );
            })}
        </div>
    );
}

export default function WelcomePage() {
    const { user, loading: authLoading } = useAuth();
    const router = useRouter();

    const [currentStep, setCurrentStep] = useState(1);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    // Provisioned state — set after self-provision or portal/home load
    const [propertyId, setPropertyId] = useState<string | null>(null);
    const [tenantId, setTenantId] = useState<string | null>(null);
    const [propertyName, setPropertyName] = useState('');

    // Step 1: hotel name input (used when no account exists yet)
    const [hotelName, setHotelName] = useState('');
    const [provisioning, setProvisioning] = useState(false);
    // 'unknown' while checking, 'needed' if no tenant yet, 'done' if already provisioned
    const [provisionState, setProvisionState] = useState<'unknown' | 'needed' | 'done'>('unknown');

    interface PropertyChannelData {
        property_id: string;
        channels: { whatsapp: string; email: string; website: string };
    }
    const [channels, setChannels] = useState<PropertyChannelData[]>([]);

    const [wizardData, setWizardData] = useState<WizardData>({
        propertyInfo: { address: '', phone: '', email: '', website: '' },
        rooms: [{ name: '', description: '', rate: '' }],
        facilities: '',
        faqs: [{ question: '', answer: '' }],
        policies: { checkin: '14:00', checkout: '12:00', cancellation: '' },
    });

    const [inviteForm, setInviteForm] = useState({ email: '', full_name: '', role: 'staff' });
    const [inviting, setInviting] = useState(false);
    const [inviteSuccess, setInviteSuccess] = useState('');
    const [checkoutLoading, setCheckoutLoading] = useState(false);
    const [checkoutError, setCheckoutError] = useState('');
    const [paymentSkipped, setPaymentSkipped] = useState(false);

    // Redirect to login if not authenticated
    useEffect(() => {
        if (!authLoading && !user) {
            router.replace('/login');
        }
    }, [user, authLoading, router]);

    // On mount: check if user already has a tenant/property
    useEffect(() => {
        if (authLoading || !user) return;

        const params = new URLSearchParams(window.location.search);
        if (params.get('paid') === 'true') {
            setCurrentStep(6);
        }
        if (params.get('step')) {
            const s = parseInt(params.get('step')!);
            if (s >= 1 && s <= 6) setCurrentStep(s);
        }

        apiGet<{
            tenant?: { id: string };
            properties?: Array<{ id: string; name: string; onboarding_score: number }>;
        }>('/portal/home')
            .then((data) => {
                const props = data?.properties ?? [];
                const tid = data?.tenant ? (data.tenant as any).id : null;
                if (props.length > 0) {
                    const firstProp = props[0];
                    setPropertyId(firstProp.id);
                    setPropertyName(firstProp.name);
                    if (tid) setTenantId(tid);
                    setProvisionState('done');
                    // If already fully onboarded, go to portal
                    if (firstProp.onboarding_score >= 100) {
                        router.replace('/portal');
                    }
                } else {
                    setProvisionState('needed');
                }
            })
            .catch(() => {
                // 403 = no tenant membership yet — user needs to self-provision
                setProvisionState('needed');
            });
    }, [user, authLoading, router]);

    // Load channel statuses when entering step 3
    useEffect(() => {
        if (currentStep === 3 && propertyId) {
            apiGet<PropertyChannelData[]>('/portal/channels')
                .then((data) => setChannels(Array.isArray(data) ? data : []))
                .catch(() => {});
        }
    }, [currentStep, propertyId]);

    // Step 1 → 2: provision tenant if needed, then advance
    const handleGetStarted = async () => {
        if (provisionState === 'done') {
            setCurrentStep(2);
            return;
        }
        if (!hotelName.trim()) {
            setError('Please enter your hotel name to continue.');
            return;
        }
        setProvisioning(true);
        setError('');
        try {
            const result = await apiPost<{
                tenant_id: string;
                property_id: string;
                property_name: string;
                is_new: boolean;
            }>('/onboarding/self-provision', { hotel_name: hotelName.trim() });
            setPropertyId(result.property_id);
            setTenantId(result.tenant_id);
            setPropertyName(result.property_name);
            setProvisionState('done');
            setCurrentStep(2);
        } catch (e: unknown) {
            setError((e instanceof Error ? e.message : String(e)) || 'Failed to set up your account. Please try again.');
        } finally {
            setProvisioning(false);
        }
    };

    // Step 2: save knowledge base
    const handleSaveKB = async () => {
        if (!propertyId) {
            setError('Account setup incomplete. Please go back to Step 1.');
            return;
        }
        setSaving(true);
        setError('');
        try {
            const { propertyInfo, rooms, facilities, faqs, policies } = wizardData;
            await apiPost(`/properties/${propertyId}/kb/ingest-wizard`, {
                property_name: propertyName || 'My Hotel',
                rooms: rooms
                    .filter((r) => r.name.trim())
                    .map((r) => ({
                        name: r.name,
                        description: r.description,
                        rate_myr: r.rate ? parseFloat(r.rate) || null : null,
                    })),
                facilities: facilities.split(',').map((s: string) => s.trim()).filter(Boolean),
                faqs: faqs.filter((f) => f.question.trim() && f.answer.trim()),
                policies,
                contact: {
                    address: propertyInfo.address || null,
                    phone: propertyInfo.phone || null,
                    email: propertyInfo.email || null,
                },
            });
            setCurrentStep(3);
        } catch (e: unknown) {
            setError((e instanceof Error ? e.message : String(e)) || 'Failed to save knowledge base');
        } finally {
            setSaving(false);
        }
    };

    // Step 4: invite team member
    const handleInvite = async () => {
        const tid = tenantId || user?.tenant_id;
        if (!inviteForm.email || !tid) {
            setError('Cannot send invitation — account not fully provisioned yet.');
            return;
        }
        setInviting(true);
        setError('');
        try {
            await apiPost(`/onboarding/invite-user/${tid}`, inviteForm);
            setInviteSuccess(`Invitation sent to ${inviteForm.email}`);
            setInviteForm({ email: '', full_name: '', role: 'staff' });
        } catch (e: unknown) {
            setError((e instanceof Error ? e.message : String(e)) || 'Failed to send invitation');
        } finally {
            setInviting(false);
        }
    };

    // Step 5: proceed to payment
    const handleProceedToPayment = async () => {
        if (!tenantId) {
            setCheckoutError('Account not fully set up. Please go back to Step 1.');
            return;
        }
        setCheckoutLoading(true);
        setCheckoutError('');
        try {
            const result = await apiPost<{ checkout_url: string }>('/billing/checkout', {
                hotel_id: tenantId,
                success_url: `${window.location.origin}/welcome?step=6&paid=true`,
                cancel_url: `${window.location.origin}/welcome?step=5`,
            });
            window.location.href = result.checkout_url;
        } catch (e: unknown) {
            setCheckoutError((e instanceof Error ? e.message : String(e)) || 'Failed to start checkout. Please try again.');
        } finally {
            setCheckoutLoading(false);
        }
    };

    // Step 6: activate and go to portal
    const handleActivate = async () => {
        if (!propertyId) {
            router.replace('/portal');
            return;
        }
        setSaving(true);
        setError('');
        try {
            await apiPost(`/onboarding/complete/${propertyId}`);
        } catch {
            // Non-fatal — endpoint may not exist yet, proceed anyway
        }
        router.replace('/portal');
    };

    if (authLoading || provisionState === 'unknown') {
        return (
            <div className="login-page">
                <div className="loader" />
            </div>
        );
    }

    if (!user) return null;

    const channelStatuses = (() => {
        if (!channels.length || !propertyId) return { whatsapp: 'skipped', email: 'skipped', website: 'skipped' };
        const propChannels = channels.find((c) => c.property_id === propertyId);
        return propChannels?.channels ?? { whatsapp: 'skipped', email: 'skipped', website: 'skipped' };
    })();

    const statusIcon = (status: string) => {
        if (status === 'active') return '✅';
        if (status === 'configuring' || status === 'pending') return '⏳';
        if (status === 'failed') return '❌';
        if (status === 'skipped') return '—';
        return '—';
    };

    return (
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'flex-start', justifyContent: 'center', paddingTop: 60, paddingBottom: 60, background: 'var(--bg-primary)' }}>
            <div style={{ width: '100%', maxWidth: 680, padding: '0 20px' }}>
                {/* Brand */}
                <div style={{ textAlign: 'center', marginBottom: 32 }}>
                    <h2 style={{ fontWeight: 700, marginBottom: 4 }}>AI Concierge</h2>
                    <p className="text-muted text-sm">Setup Wizard</p>
                </div>

                <StepIndicator current={currentStep} />

                {error && (
                    <div style={{ color: 'var(--danger)', marginBottom: 16, fontSize: 13, background: 'rgba(239,68,68,0.08)', padding: '10px 14px', borderRadius: 6 }}>
                        {error}
                    </div>
                )}

                {/* ─── STEP 1: Welcome / Property Name ─── */}
                {currentStep === 1 && (
                    <div className="card animate-in" style={{ padding: 32 }}>
                        <div style={{ textAlign: 'center', marginBottom: 28 }}>
                            <div style={{ fontSize: 48, marginBottom: 12 }}>🏨</div>
                            <h2 style={{ marginBottom: 8 }}>Welcome to AI Concierge</h2>
                            {propertyName ? (
                                <p className="text-muted" style={{ fontSize: 15 }}>
                                    Continuing setup for <strong>{propertyName}</strong>
                                </p>
                            ) : (
                                <p className="text-sm text-muted" style={{ marginTop: 8, lineHeight: 1.6 }}>
                                    Let's get your AI concierge up and running in minutes.
                                </p>
                            )}
                        </div>

                        <div style={{ display: 'grid', gap: 16, marginBottom: 24 }}>
                            {[
                                { icon: '📚', title: 'Set up your knowledge base', desc: 'Tell the AI about your rooms, rates, and policies' },
                                { icon: '📡', title: 'Connect channels', desc: 'WhatsApp, Email, and Web Chat — configured by your account manager' },
                                { icon: '👥', title: 'Invite your team', desc: 'Add staff who will monitor the dashboard' },
                            ].map((item) => (
                                <div key={item.title} className="flex items-center gap-sm" style={{ padding: '12px 16px', background: 'var(--bg-primary)', borderRadius: 8, border: '1px solid var(--border-default)' }}>
                                    <span style={{ fontSize: 24, flexShrink: 0 }}>{item.icon}</span>
                                    <div>
                                        <p style={{ fontWeight: 600, fontSize: 13, marginBottom: 2 }}>{item.title}</p>
                                        <p className="text-xs text-muted">{item.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {provisionState === 'needed' && (
                            <div style={{ marginBottom: 20 }}>
                                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6 }}>
                                    Hotel / Property Name
                                </label>
                                <input
                                    type="text"
                                    value={hotelName}
                                    onChange={(e) => setHotelName(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleGetStarted()}
                                    placeholder="e.g. Grand Hyatt Kuala Lumpur"
                                    autoFocus
                                    style={{ width: '100%', padding: '10px 14px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 14, boxSizing: 'border-box' }}
                                />
                                <p className="text-xs text-muted" style={{ marginTop: 6 }}>
                                    This creates your account. You can change the name later in Settings.
                                </p>
                            </div>
                        )}

                        <button
                            className="btn btn-primary w-full"
                            onClick={handleGetStarted}
                            disabled={provisioning || (provisionState === 'needed' && !hotelName.trim())}
                        >
                            {provisioning ? (
                                <span className="flex items-center gap-sm" style={{ justifyContent: 'center' }}>
                                    <span className="loader" style={{ width: 14, height: 14 }} /> Setting up your account…
                                </span>
                            ) : 'Get Started →'}
                        </button>
                    </div>
                )}

                {/* ─── STEP 2: Knowledge Base ─── */}
                {currentStep === 2 && (
                    <div className="card animate-in" style={{ padding: 32 }}>
                        <h2 style={{ marginBottom: 6 }}>Knowledge Base Setup</h2>
                        <p className="text-sm text-muted" style={{ marginBottom: 24 }}>
                            Tell the AI what it needs to know to answer guest questions accurately.
                            {propertyName && <> Setting up <strong>{propertyName}</strong>.</>}
                        </p>

                        {/* Property Info */}
                        <section style={{ marginBottom: 24 }}>
                            <h3 style={{ fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: 12 }}>Property Information</h3>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                                {(['address', 'phone', 'email', 'website'] as const).map((field) => (
                                    <div key={field}>
                                        <label className="text-sm" style={{ display: 'block', marginBottom: 4, textTransform: 'capitalize' }}>{field}</label>
                                        <input
                                            type="text"
                                            value={wizardData.propertyInfo[field]}
                                            onChange={(e) => setWizardData((d) => ({ ...d, propertyInfo: { ...d.propertyInfo, [field]: e.target.value } }))}
                                            placeholder={field === 'address' ? 'e.g. 123 Jalan Hotel, KL' : field === 'email' ? 'hotel@example.com' : field === 'website' ? 'https://...' : '+60 3-xxxx xxxx'}
                                            style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13, boxSizing: 'border-box' }}
                                        />
                                    </div>
                                ))}
                            </div>
                        </section>

                        {/* Rooms */}
                        <section style={{ marginBottom: 24 }}>
                            <div className="flex items-center justify-between" style={{ marginBottom: 12 }}>
                                <h3 style={{ fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>Rooms</h3>
                                <button
                                    className="btn btn-ghost btn-sm"
                                    onClick={() => setWizardData((d) => ({ ...d, rooms: [...d.rooms, { name: '', description: '', rate: '' }] }))}
                                >
                                    + Add Room
                                </button>
                            </div>
                            {wizardData.rooms.map((room, idx) => (
                                <div key={idx} style={{ display: 'grid', gridTemplateColumns: '2fr 3fr 1fr auto', gap: 8, marginBottom: 8, alignItems: 'start' }}>
                                    <input
                                        type="text"
                                        value={room.name}
                                        onChange={(e) => setWizardData((d) => { const r = [...d.rooms]; r[idx] = { ...r[idx], name: e.target.value }; return { ...d, rooms: r }; })}
                                        placeholder="Room type"
                                        style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13 }}
                                    />
                                    <input
                                        type="text"
                                        value={room.description}
                                        onChange={(e) => setWizardData((d) => { const r = [...d.rooms]; r[idx] = { ...r[idx], description: e.target.value }; return { ...d, rooms: r }; })}
                                        placeholder="Description"
                                        style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13 }}
                                    />
                                    <input
                                        type="text"
                                        value={room.rate}
                                        onChange={(e) => setWizardData((d) => { const r = [...d.rooms]; r[idx] = { ...r[idx], rate: e.target.value }; return { ...d, rooms: r }; })}
                                        placeholder="RM/night"
                                        style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13 }}
                                    />
                                    {wizardData.rooms.length > 1 && (
                                        <button
                                            onClick={() => setWizardData((d) => ({ ...d, rooms: d.rooms.filter((_, i) => i !== idx) }))}
                                            style={{ padding: '8px 10px', background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer', fontSize: 16 }}
                                        >
                                            ×
                                        </button>
                                    )}
                                </div>
                            ))}
                        </section>

                        {/* Facilities */}
                        <section style={{ marginBottom: 24 }}>
                            <h3 style={{ fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: 12 }}>Facilities</h3>
                            <input
                                type="text"
                                value={wizardData.facilities}
                                onChange={(e) => setWizardData((d) => ({ ...d, facilities: e.target.value }))}
                                placeholder="Pool, Gym, Spa, Restaurant, Free WiFi (comma-separated)"
                                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13, boxSizing: 'border-box' }}
                            />
                        </section>

                        {/* FAQs */}
                        <section style={{ marginBottom: 24 }}>
                            <div className="flex items-center justify-between" style={{ marginBottom: 12 }}>
                                <h3 style={{ fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>FAQs</h3>
                                <button
                                    className="btn btn-ghost btn-sm"
                                    onClick={() => setWizardData((d) => ({ ...d, faqs: [...d.faqs, { question: '', answer: '' }] }))}
                                >
                                    + Add FAQ
                                </button>
                            </div>
                            {wizardData.faqs.map((faq, idx) => (
                                <div key={idx} style={{ display: 'grid', gap: 6, marginBottom: 12, padding: '12px 14px', background: 'var(--bg-primary)', borderRadius: 8, border: '1px solid var(--border-default)', position: 'relative' }}>
                                    <input
                                        type="text"
                                        value={faq.question}
                                        onChange={(e) => setWizardData((d) => { const f = [...d.faqs]; f[idx] = { ...f[idx], question: e.target.value }; return { ...d, faqs: f }; })}
                                        placeholder="Question"
                                        style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13 }}
                                    />
                                    <textarea
                                        value={faq.answer}
                                        onChange={(e) => setWizardData((d) => { const f = [...d.faqs]; f[idx] = { ...f[idx], answer: e.target.value }; return { ...d, faqs: f }; })}
                                        placeholder="Answer"
                                        rows={2}
                                        style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13, resize: 'vertical', fontFamily: 'inherit' }}
                                    />
                                    {wizardData.faqs.length > 1 && (
                                        <button
                                            onClick={() => setWizardData((d) => ({ ...d, faqs: d.faqs.filter((_, i) => i !== idx) }))}
                                            style={{ position: 'absolute', top: 8, right: 8, background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer', fontSize: 16, padding: 0 }}
                                        >
                                            ×
                                        </button>
                                    )}
                                </div>
                            ))}
                        </section>

                        {/* Policies */}
                        <section style={{ marginBottom: 28 }}>
                            <h3 style={{ fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: 12 }}>Policies</h3>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 10 }}>
                                <div>
                                    <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Check-in time</label>
                                    <input
                                        type="text"
                                        value={wizardData.policies.checkin}
                                        onChange={(e) => setWizardData((d) => ({ ...d, policies: { ...d.policies, checkin: e.target.value } }))}
                                        placeholder="14:00"
                                        style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13, boxSizing: 'border-box' }}
                                    />
                                </div>
                                <div>
                                    <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Check-out time</label>
                                    <input
                                        type="text"
                                        value={wizardData.policies.checkout}
                                        onChange={(e) => setWizardData((d) => ({ ...d, policies: { ...d.policies, checkout: e.target.value } }))}
                                        placeholder="12:00"
                                        style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13, boxSizing: 'border-box' }}
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Cancellation policy</label>
                                <textarea
                                    value={wizardData.policies.cancellation}
                                    onChange={(e) => setWizardData((d) => ({ ...d, policies: { ...d.policies, cancellation: e.target.value } }))}
                                    placeholder="e.g. Free cancellation up to 48 hours before check-in…"
                                    rows={3}
                                    style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13, resize: 'vertical', boxSizing: 'border-box', fontFamily: 'inherit' }}
                                />
                            </div>
                        </section>

                        <div className="flex items-center gap-sm">
                            <button
                                className="btn btn-primary"
                                onClick={handleSaveKB}
                                disabled={saving}
                            >
                                {saving ? (
                                    <span className="flex items-center gap-sm"><span className="loader" style={{ width: 14, height: 14 }} /> Saving…</span>
                                ) : 'Save & Continue →'}
                            </button>
                            <button className="btn btn-ghost btn-sm" onClick={() => setCurrentStep(1)}>
                                Back
                            </button>
                            <button className="btn btn-ghost btn-sm" style={{ marginLeft: 'auto' }} onClick={() => setCurrentStep(3)}>
                                Skip for now →
                            </button>
                        </div>
                    </div>
                )}

                {/* ─── STEP 3: Channel Status ─── */}
                {currentStep === 3 && (
                    <div className="card animate-in" style={{ padding: 32 }}>
                        <h2 style={{ marginBottom: 6 }}>Channel Status</h2>
                        <p className="text-sm text-muted" style={{ marginBottom: 24 }}>
                            Channels are set up by your SheersSoft account manager. Contact{' '}
                            <a href="mailto:support@sheerssoft.com" style={{ color: 'var(--accent)' }}>support@sheerssoft.com</a>{' '}
                            if any channel is missing or failed.
                        </p>

                        <div style={{ display: 'grid', gap: 12, marginBottom: 28 }}>
                            {([
                                { key: 'whatsapp', icon: '💬', name: 'WhatsApp' },
                                { key: 'email', icon: '✉️', name: 'Email' },
                                { key: 'website', icon: '🌐', name: 'Website Widget' },
                            ] as const).map((ch) => {
                                const status = channelStatuses[ch.key] ?? 'skipped';
                                return (
                                    <div key={ch.key} className="flex items-center justify-between" style={{ padding: '14px 18px', background: 'var(--bg-primary)', borderRadius: 8, border: '1px solid var(--border-default)' }}>
                                        <div className="flex items-center gap-sm">
                                            <span style={{ fontSize: 24 }}>{ch.icon}</span>
                                            <span style={{ fontWeight: 600, fontSize: 14 }}>{ch.name}</span>
                                        </div>
                                        <span style={{ fontSize: 18 }}>{statusIcon(status)}</span>
                                    </div>
                                );
                            })}
                        </div>

                        <div className="flex items-center gap-sm">
                            <button className="btn btn-primary" onClick={() => setCurrentStep(4)}>
                                Continue →
                            </button>
                            <button className="btn btn-ghost btn-sm" onClick={() => setCurrentStep(2)}>
                                Back
                            </button>
                        </div>
                    </div>
                )}

                {/* ─── STEP 4: Invite Team ─── */}
                {currentStep === 4 && (
                    <div className="card animate-in" style={{ padding: 32 }}>
                        <h2 style={{ marginBottom: 6 }}>Invite Your Team</h2>
                        <p className="text-sm text-muted" style={{ marginBottom: 24 }}>
                            Add staff members who will use the dashboard to monitor conversations and leads. You can skip this step and invite them later.
                        </p>

                        {inviteSuccess && (
                            <div style={{ color: 'var(--success)', marginBottom: 12, fontSize: 13 }}>{inviteSuccess}</div>
                        )}

                        <div style={{ display: 'grid', gap: 10, marginBottom: 16 }}>
                            <div>
                                <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Email</label>
                                <input
                                    type="email"
                                    value={inviteForm.email}
                                    onChange={(e) => setInviteForm((f) => ({ ...f, email: e.target.value }))}
                                    placeholder="staff@yourhotel.com"
                                    style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13, boxSizing: 'border-box' }}
                                />
                            </div>
                            <div>
                                <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Full Name</label>
                                <input
                                    type="text"
                                    value={inviteForm.full_name}
                                    onChange={(e) => setInviteForm((f) => ({ ...f, full_name: e.target.value }))}
                                    placeholder="Jane Smith"
                                    style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13, boxSizing: 'border-box' }}
                                />
                            </div>
                            <div>
                                <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Role</label>
                                <select
                                    value={inviteForm.role}
                                    onChange={(e) => setInviteForm((f) => ({ ...f, role: e.target.value }))}
                                    style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13 }}
                                >
                                    <option value="staff">Staff</option>
                                    <option value="admin">Admin</option>
                                </select>
                            </div>
                        </div>

                        <div className="flex items-center gap-sm">
                            <button
                                className="btn btn-primary btn-sm"
                                onClick={handleInvite}
                                disabled={inviting || !inviteForm.email}
                            >
                                {inviting ? 'Sending…' : 'Send Invitation'}
                            </button>
                            <button className="btn btn-ghost btn-sm" onClick={() => setCurrentStep(5)}>
                                Skip for now →
                            </button>
                        </div>

                        <div style={{ marginTop: 20, paddingTop: 20, borderTop: '1px solid var(--border-subtle)' }}>
                            <div className="flex items-center gap-sm">
                                <button className="btn btn-ghost btn-sm" onClick={() => setCurrentStep(3)}>← Back</button>
                                {inviteSuccess && (
                                    <button className="btn btn-primary" onClick={() => setCurrentStep(5)}>
                                        Continue →
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {/* ─── STEP 5: Setup Fee Payment ─── */}
                {currentStep === 5 && (
                    <div className="card animate-in" style={{ padding: 32 }}>
                        <div style={{ textAlign: 'center', marginBottom: 28 }}>
                            <div style={{ fontSize: 48, marginBottom: 12 }}>💳</div>
                            <h2 style={{ marginBottom: 8 }}>One-time Setup Fee</h2>
                            <p className="text-sm text-muted">
                                Your AI concierge is ready. Complete the RM 999 setup to activate your account.
                            </p>
                        </div>
                        <div style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-default)', borderRadius: 10, padding: '20px 24px', marginBottom: 24 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                                <span style={{ fontSize: 14, fontWeight: 600 }}>Nocturn AI Setup Fee</span>
                                <span style={{ fontSize: 18, fontWeight: 700 }}>RM 999</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>
                                <span>Monthly subscription (after setup)</span>
                                <span>RM 199 / month</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, color: 'var(--text-muted)' }}>
                                <span>Performance fee (confirmed direct bookings)</span>
                                <span>3% only</span>
                            </div>
                            <div style={{ borderTop: '1px solid var(--border-subtle)', marginTop: 14, paddingTop: 12 }}>
                                <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: 0, lineHeight: 1.5 }}>
                                    30-day money-back guarantee. If Nocturn AI doesn&apos;t recover more than RM 199 in the first month, your next month is free.
                                </p>
                            </div>
                        </div>
                        {checkoutError && (
                            <div style={{ color: 'var(--danger)', marginBottom: 16, fontSize: 13, background: 'rgba(239,68,68,0.08)', padding: '10px 14px', borderRadius: 6 }}>
                                {checkoutError}
                            </div>
                        )}
                        <button
                            className="btn btn-primary w-full"
                            onClick={handleProceedToPayment}
                            disabled={checkoutLoading}
                            style={{ marginBottom: 12 }}
                        >
                            {checkoutLoading
                                ? <span className="flex items-center gap-sm" style={{ justifyContent: 'center' }}><span className="loader" style={{ width: 14, height: 14 }} /> Redirecting to payment…</span>
                                : 'Pay RM 999 and Activate →'}
                        </button>
                        <div className="flex items-center gap-sm" style={{ justifyContent: 'center' }}>
                            <button className="btn btn-ghost btn-sm" onClick={() => setCurrentStep(4)}>← Back</button>
                            <button
                                className="btn btn-ghost btn-sm"
                                style={{ color: 'var(--text-muted)', fontSize: 12 }}
                                onClick={() => { setPaymentSkipped(true); setCurrentStep(6); }}
                            >
                                Skip for now (pay later)
                            </button>
                        </div>
                    </div>
                )}

                {/* ─── STEP 6: Go Live ─── */}
                {currentStep === 6 && (
                    <div className="card animate-in" style={{ padding: 32 }}>
                        <div style={{ textAlign: 'center', marginBottom: 28 }}>
                            <div style={{ fontSize: 56, marginBottom: 12 }}>🚀</div>
                            <h2 style={{ marginBottom: 8 }}>Ready to Go Live</h2>
                            <p className="text-sm text-muted">
                                Your AI concierge is configured. Click below to go to your portal.
                            </p>
                        </div>

                        {paymentSkipped && (
                            <div style={{ background: 'rgba(234,179,8,0.12)', border: '1px solid rgba(234,179,8,0.4)', borderRadius: 8, padding: '12px 16px', marginBottom: 20, fontSize: 13, color: 'var(--text-primary)' }}>
                                Payment pending — your account will be activated once the RM 999 setup fee is received. You can complete this from the portal billing page.
                            </div>
                        )}

                        <div style={{ display: 'grid', gap: 10, marginBottom: 28 }}>
                            <div className="flex items-center gap-sm" style={{ padding: '12px 16px', background: 'var(--bg-primary)', borderRadius: 8 }}>
                                <span>✅</span>
                                <span className="text-sm">Account created for <strong>{propertyName || 'your property'}</strong></span>
                            </div>
                            <div className="flex items-center gap-sm" style={{ padding: '12px 16px', background: 'var(--bg-primary)', borderRadius: 8 }}>
                                <span>{statusIcon(channelStatuses.whatsapp)}</span>
                                <span className="text-sm">WhatsApp — {channelStatuses.whatsapp}</span>
                            </div>
                            <div className="flex items-center gap-sm" style={{ padding: '12px 16px', background: 'var(--bg-primary)', borderRadius: 8 }}>
                                <span>{statusIcon(channelStatuses.email)}</span>
                                <span className="text-sm">Email — {channelStatuses.email}</span>
                            </div>
                            <div className="flex items-center gap-sm" style={{ padding: '12px 16px', background: 'var(--bg-primary)', borderRadius: 8 }}>
                                <span>{statusIcon(channelStatuses.website)}</span>
                                <span className="text-sm">Website Widget — {channelStatuses.website}</span>
                            </div>
                        </div>

                        <div className="flex items-center gap-sm" style={{ justifyContent: 'center' }}>
                            <button
                                className="btn btn-primary"
                                onClick={handleActivate}
                                disabled={saving}
                                style={{ minWidth: 180 }}
                            >
                                {saving ? 'Loading…' : 'Go to My Portal →'}
                            </button>
                        </div>

                        <div style={{ textAlign: 'center', marginTop: 16 }}>
                            <button className="btn btn-ghost btn-sm" onClick={() => setCurrentStep(5)}>← Back</button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
