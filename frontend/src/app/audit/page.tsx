'use client';

import { useState, useEffect, useCallback } from 'react';

// ─── Types ────────────────────────────────────────────────────────────────────

interface AuditInputs {
    room_count: number;
    adr: number;
    daily_msgs: number | null;
    front_desk_close: string;
    ota_commission_rate: number;
}

interface AuditResults {
    room_count: number;
    adr: number;
    daily_msgs_used: number;
    after_hours_msgs_per_day: number;
    monthly_after_hours_msgs: number;
    lost_bookings_per_month: number;
    avg_stay_nights: number;
    revenue_lost_monthly: number;
    ota_commission_monthly: number;
    total_monthly_leakage: number;
    annual_leakage: number;
    conservative_annual: number;
    annual_net_recovery: number;
    roi_multiple: number;
}

// ─── Constants ────────────────────────────────────────────────────────────────

const DAILY_MSG_OPTIONS = [
    { label: 'I don\'t know', value: null },
    { label: '~5–10 messages/day', value: 7.5 },
    { label: '~10–20 messages/day', value: 15 },
    { label: '~20–40 messages/day', value: 30 },
    { label: '40+ messages/day', value: 50 },
];

const CLOSURE_OPTIONS = [
    { label: '8pm (20:00)', value: '20:00' },
    { label: '9pm (21:00)', value: '21:00' },
    { label: '10pm (22:00)', value: '22:00' },
    { label: '11pm (23:00)', value: '23:00' },
    { label: 'Midnight (00:00)', value: '00:00' },
    { label: '24-hour front desk', value: '24h' },
];

const OTA_OPTIONS = [
    { label: '15%', value: 15 },
    { label: '18% (Agoda standard)', value: 18 },
    { label: '20%', value: 20 },
    { label: '22%', value: 22 },
    { label: '25%', value: 25 },
];

const DEFAULT_INPUTS: AuditInputs = {
    room_count: 60,
    adr: 280,
    daily_msgs: null,
    front_desk_close: '22:00',
    ota_commission_rate: 18,
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

function fmt(n: number) {
    return 'RM ' + Math.round(n).toLocaleString('en-MY');
}

function fmtK(n: number) {
    if (n >= 1_000_000) return `RM ${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `RM ${Math.round(n / 1_000)}K`;
    return fmt(n);
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function AuditPage() {
    const [inputs, setInputs] = useState<AuditInputs>(DEFAULT_INPUTS);
    const [results, setResults] = useState<AuditResults | null>(null);
    const [calculating, setCalculating] = useState(false);
    const [showGate, setShowGate] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    const [contactName, setContactName] = useState('');
    const [hotelName, setHotelName] = useState('');
    const [email, setEmail] = useState('');
    const [phone, setPhone] = useState('');

    const calculate = useCallback(async (inp: AuditInputs) => {
        setCalculating(true);
        try {
            const res = await fetch('/api/v1/audit/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(inp),
            });
            if (res.ok) {
                const data = await res.json();
                setResults(data);
            }
        } catch {
            // silent — results just won't update
        } finally {
            setCalculating(false);
        }
    }, []);

    useEffect(() => {
        const t = setTimeout(() => calculate(inputs), 300);
        return () => clearTimeout(t);
    }, [inputs, calculate]);

    const handleSubmit = async () => {
        if (!contactName || !hotelName || !email) return;
        setSubmitting(true);
        try {
            const res = await fetch('/api/v1/audit/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    inputs,
                    contact_name: contactName,
                    hotel_name: hotelName,
                    email,
                    phone: phone || null,
                }),
            });
            if (res.ok) {
                setSubmitted(true);
                setShowGate(false);
            }
        } catch {
            // silent
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: 'var(--bg-primary)',
            color: 'var(--text-primary)',
            fontFamily: 'Inter, sans-serif',
        }}>
            {/* Header */}
            <div style={{
                background: 'linear-gradient(135deg, rgba(99,102,241,0.15) 0%, transparent 60%)',
                borderBottom: '1px solid var(--border-subtle)',
                padding: '48px 24px 40px',
                textAlign: 'center',
            }}>
                <div style={{ maxWidth: 720, margin: '0 auto' }}>
                    <div style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 8,
                        background: 'var(--accent-subtle)',
                        border: '1px solid rgba(99,102,241,0.3)',
                        borderRadius: 'var(--radius-full)',
                        padding: '6px 16px',
                        fontSize: 13,
                        color: 'var(--text-accent)',
                        marginBottom: 20,
                    }}>
                        Free · No account required · Instant results
                    </div>
                    <h1 style={{ fontSize: 40, fontWeight: 800, lineHeight: 1.15, marginBottom: 16 }}>
                        After-Hours Revenue Audit
                    </h1>
                    <p style={{ fontSize: 18, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                        How much is your hotel losing every night because nobody answers WhatsApp?
                        Enter your numbers and find out in 30 seconds.
                    </p>
                </div>
            </div>

            {/* Main layout */}
            <div style={{
                maxWidth: 1100,
                margin: '0 auto',
                padding: '40px 24px 80px',
                display: 'grid',
                gridTemplateColumns: 'minmax(0,1fr) minmax(0,1fr)',
                gap: 32,
                alignItems: 'start',
            }}>

                {/* LEFT — Inputs */}
                <div style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-default)',
                    borderRadius: 'var(--radius-lg)',
                    padding: 32,
                }}>
                    <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 28 }}>Your Hotel Details</h2>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

                        {/* Room count */}
                        <div>
                            <label style={{ display: 'block', fontSize: 14, fontWeight: 500, marginBottom: 10, color: 'var(--text-secondary)' }}>
                                Number of rooms
                            </label>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                                <input
                                    type="range"
                                    min={20} max={200} step={5}
                                    value={inputs.room_count}
                                    onChange={e => setInputs(p => ({ ...p, room_count: +e.target.value }))}
                                    style={{ flex: 1, accentColor: 'var(--accent)' }}
                                />
                                <span style={{
                                    minWidth: 52,
                                    textAlign: 'right',
                                    fontWeight: 700,
                                    fontSize: 20,
                                    color: 'var(--text-accent)',
                                }}>{inputs.room_count}</span>
                            </div>
                        </div>

                        {/* ADR */}
                        <div>
                            <label style={{ display: 'block', fontSize: 14, fontWeight: 500, marginBottom: 10, color: 'var(--text-secondary)' }}>
                                Average room rate (RM / night)
                            </label>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                                <input
                                    type="range"
                                    min={80} max={800} step={10}
                                    value={inputs.adr}
                                    onChange={e => setInputs(p => ({ ...p, adr: +e.target.value }))}
                                    style={{ flex: 1, accentColor: 'var(--accent)' }}
                                />
                                <span style={{
                                    minWidth: 76,
                                    textAlign: 'right',
                                    fontWeight: 700,
                                    fontSize: 20,
                                    color: 'var(--text-accent)',
                                }}>RM {inputs.adr}</span>
                            </div>
                        </div>

                        {/* Daily messages */}
                        <div>
                            <label style={{ display: 'block', fontSize: 14, fontWeight: 500, marginBottom: 10, color: 'var(--text-secondary)' }}>
                                Daily WhatsApp messages
                            </label>
                            <select
                                value={inputs.daily_msgs === null ? '' : String(inputs.daily_msgs)}
                                onChange={e => setInputs(p => ({
                                    ...p,
                                    daily_msgs: e.target.value === '' ? null : +e.target.value,
                                }))}
                                style={{
                                    width: '100%',
                                    background: 'var(--bg-input)',
                                    border: '1px solid var(--border-default)',
                                    borderRadius: 'var(--radius-sm)',
                                    color: 'var(--text-primary)',
                                    padding: '10px 14px',
                                    fontSize: 14,
                                }}
                            >
                                {DAILY_MSG_OPTIONS.map(o => (
                                    <option key={String(o.value)} value={o.value === null ? '' : String(o.value)}>
                                        {o.label}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Front desk close */}
                        <div>
                            <label style={{ display: 'block', fontSize: 14, fontWeight: 500, marginBottom: 10, color: 'var(--text-secondary)' }}>
                                Front desk goes to skeleton crew / closes
                            </label>
                            <select
                                value={inputs.front_desk_close}
                                onChange={e => setInputs(p => ({ ...p, front_desk_close: e.target.value }))}
                                style={{
                                    width: '100%',
                                    background: 'var(--bg-input)',
                                    border: '1px solid var(--border-default)',
                                    borderRadius: 'var(--radius-sm)',
                                    color: 'var(--text-primary)',
                                    padding: '10px 14px',
                                    fontSize: 14,
                                }}
                            >
                                {CLOSURE_OPTIONS.map(o => (
                                    <option key={o.value} value={o.value}>{o.label}</option>
                                ))}
                            </select>
                        </div>

                        {/* OTA commission */}
                        <div>
                            <label style={{ display: 'block', fontSize: 14, fontWeight: 500, marginBottom: 10, color: 'var(--text-secondary)' }}>
                                OTA commission rate (Agoda / Booking.com)
                            </label>
                            <select
                                value={inputs.ota_commission_rate}
                                onChange={e => setInputs(p => ({ ...p, ota_commission_rate: +e.target.value }))}
                                style={{
                                    width: '100%',
                                    background: 'var(--bg-input)',
                                    border: '1px solid var(--border-default)',
                                    borderRadius: 'var(--radius-sm)',
                                    color: 'var(--text-primary)',
                                    padding: '10px 14px',
                                    fontSize: 14,
                                }}
                            >
                                {OTA_OPTIONS.map(o => (
                                    <option key={o.value} value={o.value}>{o.label}</option>
                                ))}
                            </select>
                        </div>

                    </div>
                </div>

                {/* RIGHT — Results */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

                    {results ? (
                        <>
                            {/* Primary metric */}
                            <div style={{
                                background: 'linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(99,102,241,0.05) 100%)',
                                border: '1px solid rgba(99,102,241,0.4)',
                                borderRadius: 'var(--radius-lg)',
                                padding: '32px 28px',
                                textAlign: 'center',
                                position: 'relative',
                                overflow: 'hidden',
                            }}>
                                <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                                    Conservative annual leakage
                                </div>
                                <div style={{
                                    fontSize: 52,
                                    fontWeight: 800,
                                    color: '#f87171',
                                    lineHeight: 1,
                                    marginBottom: 8,
                                    opacity: calculating ? 0.5 : 1,
                                    transition: 'opacity 0.2s',
                                }}>
                                    {fmtK(results.conservative_annual)}
                                </div>
                                <div style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
                                    per year in recoverable revenue
                                </div>
                            </div>

                            {/* Breakdown */}
                            <div style={{
                                background: 'var(--bg-card)',
                                border: '1px solid var(--border-default)',
                                borderRadius: 'var(--radius-lg)',
                                padding: '24px 28px',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: 16,
                            }}>
                                <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                                    Breakdown
                                </h3>
                                {[
                                    { label: 'After-hours msgs/day', value: `${results.after_hours_msgs_per_day}`, unit: 'msgs' },
                                    { label: 'Lost bookings/month', value: `${results.lost_bookings_per_month}`, unit: 'bookings' },
                                    { label: 'Revenue lost/month', value: fmt(results.revenue_lost_monthly), unit: '' },
                                    { label: 'OTA commission displaced/month', value: fmt(results.ota_commission_monthly), unit: '' },
                                    { label: 'Total monthly leakage', value: fmt(results.total_monthly_leakage), unit: '', bold: true },
                                ].map(row => (
                                    <div key={row.label} style={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center',
                                        paddingBottom: 12,
                                        borderBottom: '1px solid var(--border-subtle)',
                                    }}>
                                        <span style={{ fontSize: 14, color: 'var(--text-secondary)' }}>{row.label}</span>
                                        <span style={{
                                            fontSize: 15,
                                            fontWeight: (row as any).bold ? 700 : 500,
                                            color: (row as any).bold ? 'var(--text-primary)' : 'var(--text-accent)',
                                        }}>
                                            {row.value}{row.unit ? ` ${row.unit}` : ''}
                                        </span>
                                    </div>
                                ))}
                            </div>

                            {/* ROI */}
                            <div style={{
                                background: 'var(--success-bg)',
                                border: '1px solid rgba(52,211,153,0.3)',
                                borderRadius: 'var(--radius-lg)',
                                padding: '20px 28px',
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                            }}>
                                <div>
                                    <div style={{ fontSize: 13, color: 'var(--success)', marginBottom: 4 }}>
                                        Nocturn AI ROI (RM 499/mo)
                                    </div>
                                    <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--success)' }}>
                                        {results.roi_multiple}x return
                                    </div>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 4 }}>
                                        Net Year 1 recovery
                                    </div>
                                    <div style={{ fontSize: 22, fontWeight: 700 }}>
                                        {fmtK(results.annual_net_recovery)}
                                    </div>
                                </div>
                            </div>

                            {/* CTA */}
                            {submitted ? (
                                <div style={{
                                    background: 'var(--success-bg)',
                                    border: '1px solid rgba(52,211,153,0.3)',
                                    borderRadius: 'var(--radius-lg)',
                                    padding: '24px 28px',
                                    textAlign: 'center',
                                }}>
                                    <div style={{ fontSize: 20, marginBottom: 8 }}>Report sent!</div>
                                    <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
                                        Check your inbox. We'll be in touch within 24 hours to walk through your numbers.
                                    </p>
                                </div>
                            ) : !showGate ? (
                                <button
                                    onClick={() => setShowGate(true)}
                                    className="btn btn-primary"
                                    style={{ width: '100%', padding: '14px 24px', fontSize: 15, fontWeight: 600 }}
                                >
                                    Get Full Report + Start Free 30-Day Pilot
                                </button>
                            ) : (
                                <div style={{
                                    background: 'var(--bg-card)',
                                    border: '1px solid var(--border-default)',
                                    borderRadius: 'var(--radius-lg)',
                                    padding: '24px 28px',
                                }}>
                                    <h3 style={{ fontWeight: 700, marginBottom: 4 }}>Get your personalised report</h3>
                                    <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 20 }}>
                                        We'll email your full audit + a 30-day free pilot proposal. No setup fee. No contract.
                                    </p>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                        {[
                                            { label: 'Your name', value: contactName, setter: setContactName, placeholder: 'Ahmad Farid', required: true },
                                            { label: 'Hotel name', value: hotelName, setter: setHotelName, placeholder: 'Hotel Selangor', required: true },
                                            { label: 'Email', value: email, setter: setEmail, placeholder: 'gm@hotelselangor.com', required: true },
                                            { label: 'WhatsApp (optional)', value: phone, setter: setPhone, placeholder: '+60 12-345 6789', required: false },
                                        ].map(f => (
                                            <div key={f.label}>
                                                <label style={{ display: 'block', fontSize: 12, color: 'var(--text-secondary)', marginBottom: 6 }}>
                                                    {f.label}{f.required && ' *'}
                                                </label>
                                                <input
                                                    type="text"
                                                    value={f.value}
                                                    onChange={e => f.setter(e.target.value)}
                                                    placeholder={f.placeholder}
                                                    className="form-input"
                                                    style={{ width: '100%' }}
                                                />
                                            </div>
                                        ))}
                                        <button
                                            onClick={handleSubmit}
                                            disabled={submitting || !contactName || !hotelName || !email}
                                            className="btn btn-primary"
                                            style={{ marginTop: 8 }}
                                        >
                                            {submitting ? 'Sending...' : 'Send My Audit Report'}
                                        </button>
                                    </div>
                                </div>
                            )}

                        </>
                    ) : (
                        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 300 }}>
                            <div className="loader" />
                        </div>
                    )}
                </div>
            </div>

            {/* Footer note */}
            <div style={{
                textAlign: 'center',
                padding: '0 24px 48px',
                color: 'var(--text-muted)',
                fontSize: 13,
                maxWidth: 640,
                margin: '0 auto',
            }}>
                Conservative estimate using a 40% discount on industry benchmarks.
                Actual recovery depends on your property's WhatsApp response rates and guest booking behaviour.
                Powered by <strong style={{ color: 'var(--text-secondary)' }}>Nocturn AI</strong> by SheersSoft.
            </div>

            {/* Mobile responsive */}
            <style>{`
                @media (max-width: 768px) {
                    div[style*="gridTemplateColumns"] {
                        grid-template-columns: 1fr !important;
                    }
                }
            `}</style>
        </div>
    );
}
