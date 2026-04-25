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

// ─── Shared input styles ──────────────────────────────────────────────────────

const selectStyle: React.CSSProperties = {
    width: '100%',
    background: 'var(--bg3)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-sm)',
    color: 'var(--text)',
    padding: '10px 14px',
    fontSize: 14,
    fontFamily: 'inherit',
    outline: 'none',
    appearance: 'none',
};

const labelStyle: React.CSSProperties = {
    display: 'block',
    fontSize: 12,
    fontWeight: 500,
    marginBottom: 10,
    color: 'var(--text2)',
};

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
            background: 'var(--bg)',
            color: 'var(--text)',
            fontFamily: 'Inter, -apple-system, system-ui, sans-serif',
        }}>
            {/* Header */}
            <div style={{
                background: 'var(--bg2)',
                borderBottom: '1px solid var(--border)',
                padding: '44px 24px 36px',
                textAlign: 'center',
            }}>
                <div style={{ maxWidth: 680, margin: '0 auto' }}>
                    <div style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 8,
                        background: 'var(--teal-bg)',
                        border: '0.5px solid rgba(29,158,117,0.3)',
                        borderRadius: 'var(--radius-full)',
                        padding: '5px 14px',
                        fontSize: 12,
                        color: 'var(--teal)',
                        marginBottom: 20,
                        fontWeight: 500,
                        letterSpacing: '0.02em',
                    }}>
                        Free · No account required · Instant results
                    </div>
                    <h1 style={{ fontSize: 34, fontWeight: 700, lineHeight: 1.2, marginBottom: 14, color: 'var(--text)', letterSpacing: '-0.02em' }}>
                        After-Hours Revenue Audit
                    </h1>
                    <p style={{ fontSize: 16, color: 'var(--text2)', lineHeight: 1.65 }}>
                        How much is your hotel losing every night because nobody answers WhatsApp?
                        Enter your numbers and find out in 30 seconds.
                    </p>
                </div>
            </div>

            {/* Main layout */}
            <div style={{
                maxWidth: 1060,
                margin: '0 auto',
                padding: '36px 24px 80px',
                display: 'grid',
                gridTemplateColumns: 'minmax(0,1fr) minmax(0,1fr)',
                gap: 28,
                alignItems: 'start',
            }}>

                {/* LEFT — Inputs */}
                <div style={{
                    background: 'var(--bg2)',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius-lg)',
                    padding: 28,
                }}>
                    <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 24, color: 'var(--text)' }}>Your Hotel Details</h2>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>

                        {/* Room count */}
                        <div>
                            <label style={labelStyle}>Number of rooms</label>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                                <input
                                    type="range"
                                    min={20} max={200} step={5}
                                    value={inputs.room_count}
                                    onChange={e => setInputs(p => ({ ...p, room_count: +e.target.value }))}
                                    style={{ flex: 1, accentColor: 'var(--teal)' }}
                                />
                                <span style={{
                                    minWidth: 48,
                                    textAlign: 'right',
                                    fontWeight: 600,
                                    fontSize: 18,
                                    color: 'var(--teal)',
                                }}>{inputs.room_count}</span>
                            </div>
                        </div>

                        {/* ADR */}
                        <div>
                            <label style={labelStyle}>Average room rate (RM / night)</label>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                                <input
                                    type="range"
                                    min={80} max={800} step={10}
                                    value={inputs.adr}
                                    onChange={e => setInputs(p => ({ ...p, adr: +e.target.value }))}
                                    style={{ flex: 1, accentColor: 'var(--teal)' }}
                                />
                                <span style={{
                                    minWidth: 72,
                                    textAlign: 'right',
                                    fontWeight: 600,
                                    fontSize: 18,
                                    color: 'var(--teal)',
                                }}>RM {inputs.adr}</span>
                            </div>
                        </div>

                        {/* Daily messages */}
                        <div>
                            <label style={labelStyle}>Daily WhatsApp messages</label>
                            <select
                                value={inputs.daily_msgs === null ? '' : String(inputs.daily_msgs)}
                                onChange={e => setInputs(p => ({
                                    ...p,
                                    daily_msgs: e.target.value === '' ? null : +e.target.value,
                                }))}
                                style={selectStyle}
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
                            <label style={labelStyle}>Front desk goes to skeleton crew / closes</label>
                            <select
                                value={inputs.front_desk_close}
                                onChange={e => setInputs(p => ({ ...p, front_desk_close: e.target.value }))}
                                style={selectStyle}
                            >
                                {CLOSURE_OPTIONS.map(o => (
                                    <option key={o.value} value={o.value}>{o.label}</option>
                                ))}
                            </select>
                        </div>

                        {/* OTA commission */}
                        <div>
                            <label style={labelStyle}>OTA commission rate (Agoda / Booking.com)</label>
                            <select
                                value={inputs.ota_commission_rate}
                                onChange={e => setInputs(p => ({ ...p, ota_commission_rate: +e.target.value }))}
                                style={selectStyle}
                            >
                                {OTA_OPTIONS.map(o => (
                                    <option key={o.value} value={o.value}>{o.label}</option>
                                ))}
                            </select>
                        </div>

                    </div>
                </div>

                {/* RIGHT — Results */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

                    {results ? (
                        <>
                            {/* Primary metric */}
                            <div style={{
                                background: 'linear-gradient(135deg, rgba(29,158,117,0.15) 0%, rgba(29,158,117,0.04) 100%)',
                                border: '1px solid rgba(29,158,117,0.3)',
                                borderRadius: 'var(--radius-lg)',
                                padding: '28px 24px',
                                textAlign: 'center',
                                position: 'relative',
                                overflow: 'hidden',
                            }}>
                                <div style={{ fontSize: 11, color: 'var(--text3)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600 }}>
                                    Conservative annual leakage
                                </div>
                                <div style={{
                                    fontSize: 46,
                                    fontWeight: 700,
                                    color: 'var(--red)',
                                    lineHeight: 1,
                                    marginBottom: 8,
                                    opacity: calculating ? 0.45 : 1,
                                    transition: 'opacity 0.2s',
                                    letterSpacing: '-0.02em',
                                }}>
                                    {fmtK(results.conservative_annual)}
                                </div>
                                <div style={{ fontSize: 13, color: 'var(--text2)' }}>
                                    per year in recoverable revenue
                                </div>
                            </div>

                            {/* Breakdown */}
                            <div style={{
                                background: 'var(--bg2)',
                                border: '1px solid var(--border)',
                                borderRadius: 'var(--radius-lg)',
                                padding: '20px 24px',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: 14,
                            }}>
                                <h3 style={{ fontSize: 11, fontWeight: 600, color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
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
                                        borderBottom: '1px solid var(--border)',
                                    }}>
                                        <span style={{ fontSize: 13, color: 'var(--text2)' }}>{row.label}</span>
                                        <span style={{
                                            fontSize: 14,
                                            fontWeight: (row as any).bold ? 600 : 500,
                                            color: (row as any).bold ? 'var(--text)' : 'var(--teal)',
                                        }}>
                                            {row.value}{row.unit ? ` ${row.unit}` : ''}
                                        </span>
                                    </div>
                                ))}
                            </div>

                            {/* ROI */}
                            <div style={{
                                background: 'var(--teal-bg)',
                                border: '1px solid rgba(29,158,117,0.25)',
                                borderRadius: 'var(--radius-lg)',
                                padding: '18px 24px',
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                            }}>
                                <div>
                                    <div style={{ fontSize: 12, color: 'var(--teal)', marginBottom: 4 }}>
                                        Nocturn AI ROI (RM 199/month + RM 999 setup)
                                    </div>
                                    <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--teal)' }}>
                                        {results.roi_multiple}x return
                                    </div>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <div style={{ fontSize: 12, color: 'var(--text2)', marginBottom: 4 }}>
                                        Net Year 1 recovery
                                    </div>
                                    <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--text)' }}>
                                        {fmtK(results.annual_net_recovery)}
                                    </div>
                                </div>
                            </div>

                            {/* CTA */}
                            {submitted ? (
                                <div style={{
                                    background: 'var(--teal-bg)',
                                    border: '1px solid rgba(29,158,117,0.3)',
                                    borderRadius: 'var(--radius-lg)',
                                    padding: '22px 24px',
                                    textAlign: 'center',
                                }}>
                                    <div style={{ fontSize: 18, marginBottom: 8, color: 'var(--teal)', fontWeight: 600 }}>Report sent!</div>
                                    <p style={{ color: 'var(--text2)', fontSize: 13 }}>
                                        Check your inbox. We'll be in touch within 24 hours to walk through your numbers.
                                    </p>
                                </div>
                            ) : !showGate ? (
                                <button
                                    onClick={() => setShowGate(true)}
                                    className="btn btn-primary btn-lg w-full"
                                    style={{ fontSize: 14, letterSpacing: '0.01em' }}
                                >
                                    Get Full Report + Start Free 30-Day Pilot
                                </button>
                            ) : (
                                <div style={{
                                    background: 'var(--bg2)',
                                    border: '1px solid var(--border)',
                                    borderRadius: 'var(--radius-lg)',
                                    padding: '22px 24px',
                                }}>
                                    <h3 style={{ fontWeight: 600, marginBottom: 4, color: 'var(--text)', fontSize: 15 }}>Get your personalised report</h3>
                                    <p style={{ fontSize: 12, color: 'var(--text2)', marginBottom: 18 }}>
                                        We'll email your full audit + a 30-day free pilot proposal. No setup fee. No contract.
                                    </p>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                                        {[
                                            { label: 'Your name', value: contactName, setter: setContactName, placeholder: 'Ahmad Farid', required: true },
                                            { label: 'Hotel name', value: hotelName, setter: setHotelName, placeholder: 'Hotel Selangor', required: true },
                                            { label: 'Email', value: email, setter: setEmail, placeholder: 'gm@hotelselangor.com', required: true },
                                            { label: 'WhatsApp (optional)', value: phone, setter: setPhone, placeholder: '+60 12-345 6789', required: false },
                                        ].map(f => (
                                            <div key={f.label}>
                                                <label style={{ display: 'block', fontSize: 11, color: 'var(--text2)', marginBottom: 5 }}>
                                                    {f.label}{f.required && ' *'}
                                                </label>
                                                <input
                                                    type="text"
                                                    value={f.value}
                                                    onChange={e => f.setter(e.target.value)}
                                                    placeholder={f.placeholder}
                                                    style={{
                                                        width: '100%',
                                                        background: 'var(--bg3)',
                                                        border: '1px solid var(--border)',
                                                        borderRadius: 'var(--radius-sm)',
                                                        color: 'var(--text)',
                                                        padding: '9px 12px',
                                                        fontSize: 13,
                                                        fontFamily: 'inherit',
                                                        outline: 'none',
                                                    }}
                                                />
                                            </div>
                                        ))}
                                        <button
                                            onClick={handleSubmit}
                                            disabled={submitting || !contactName || !hotelName || !email}
                                            className="btn btn-primary w-full"
                                            style={{ marginTop: 6 }}
                                        >
                                            {submitting ? 'Sending...' : 'Send My Audit Report'}
                                        </button>
                                    </div>
                                </div>
                            )}

                        </>
                    ) : (
                        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 280 }}>
                            <div className="loader" />
                        </div>
                    )}
                </div>
            </div>

            {/* Footer note */}
            <div style={{
                textAlign: 'center',
                padding: '0 24px 48px',
                color: 'var(--text3)',
                fontSize: 12,
                maxWidth: 580,
                margin: '0 auto',
                lineHeight: 1.65,
            }}>
                Conservative estimate using a 40% discount on industry benchmarks.
                Actual recovery depends on your property's WhatsApp response rates and guest booking behaviour.
                Powered by <strong style={{ color: 'var(--text2)' }}>Nocturn AI</strong> by SheersSoft.
            </div>

            <style>{`
                @media (max-width: 768px) {
                    div[style*="gridTemplateColumns: minmax"] {
                        grid-template-columns: 1fr !important;
                    }
                }
            `}</style>
        </div>
    );
}
