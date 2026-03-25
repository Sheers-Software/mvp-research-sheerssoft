'use client';

import { useState, useEffect, useCallback } from 'react';
import { apiGet, apiPost, apiPatch } from '@/lib/api';

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
    revenue_lost_monthly: number;
    ota_commission_monthly: number;
    total_monthly_leakage: number;
    annual_leakage: number;
    conservative_annual: number;
    annual_net_recovery: number;
    roi_multiple: number;
}

interface AuditRecord {
    id: string;
    hotel_name: string | null;
    contact_name: string | null;
    email: string | null;
    phone: string | null;
    room_count: number;
    adr: number;
    conservative_annual: number;
    roi_multiple: number;
    status: string;
    notes: string | null;
    source: string;
    created_at: string;
}

const DAILY_MSG_OPTIONS = [
    { label: 'Auto (derive from room count)', value: null },
    { label: '~5–10 msgs/day', value: 7.5 },
    { label: '~10–20 msgs/day', value: 15 },
    { label: '~20–40 msgs/day', value: 30 },
    { label: '40+ msgs/day', value: 50 },
];

const CLOSURE_OPTIONS = [
    { label: '8pm', value: '20:00' },
    { label: '9pm', value: '21:00' },
    { label: '10pm', value: '22:00' },
    { label: '11pm', value: '23:00' },
    { label: 'Midnight', value: '00:00' },
    { label: '24-hour front desk', value: '24h' },
];

const STATUS_OPTIONS = ['submitted', 'contacted', 'qualified', 'converted', 'closed'];

const statusBadge: Record<string, string> = {
    submitted: 'badge-info',
    contacted: 'badge-warning',
    qualified: 'badge-warning',
    converted: 'badge-success',
    closed: 'badge-neutral',
};

function fmt(n: number) {
    return 'RM ' + Math.round(n).toLocaleString('en-MY');
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function RevenueAuditPage() {
    const [tab, setTab] = useState<'calculator' | 'records'>('calculator');

    // Calculator state
    const [inputs, setInputs] = useState<AuditInputs>({
        room_count: 60,
        adr: 280,
        daily_msgs: null,
        front_desk_close: '22:00',
        ota_commission_rate: 18,
    });
    const [hotelName, setHotelName] = useState('');
    const [contactName, setContactName] = useState('');
    const [email, setEmail] = useState('');
    const [phone, setPhone] = useState('');
    const [results, setResults] = useState<AuditResults | null>(null);
    const [calculating, setCalculating] = useState(false);
    const [saving, setSaving] = useState(false);
    const [saveMsg, setSaveMsg] = useState('');

    // Records state
    const [records, setRecords] = useState<AuditRecord[]>([]);
    const [recordsLoading, setRecordsLoading] = useState(false);
    const [editingNote, setEditingNote] = useState<string | null>(null);
    const [noteText, setNoteText] = useState('');

    const calculate = useCallback(async (inp: AuditInputs) => {
        setCalculating(true);
        try {
            const data = await apiPost<AuditResults>('/audit/calculate', inp);
            setResults(data);
        } catch {
            // silent
        } finally {
            setCalculating(false);
        }
    }, []);

    useEffect(() => {
        const t = setTimeout(() => calculate(inputs), 300);
        return () => clearTimeout(t);
    }, [inputs, calculate]);

    const loadRecords = async () => {
        setRecordsLoading(true);
        try {
            const data = await apiGet<AuditRecord[]>('/audit/records');
            setRecords(data);
        } catch {
            // silent
        } finally {
            setRecordsLoading(false);
        }
    };

    useEffect(() => {
        if (tab === 'records') loadRecords();
    }, [tab]);

    const saveAudit = async () => {
        setSaving(true);
        setSaveMsg('');
        try {
            await apiPost('/audit/submit', {
                inputs,
                contact_name: contactName || '(not provided)',
                hotel_name: hotelName || '(not provided)',
                email: email || 'admin@sheerssoft.com',
                phone: phone || null,
            });
            setSaveMsg('Saved to pipeline.');
        } catch {
            setSaveMsg('Save failed.');
        } finally {
            setSaving(false);
        }
    };

    const updateStatus = async (id: string, status: string) => {
        await apiPatch(`/audit/records/${id}`, { status });
        setRecords(prev => prev.map(r => r.id === id ? { ...r, status } : r));
    };

    const saveNote = async (id: string) => {
        await apiPatch(`/audit/records/${id}`, { notes: noteText });
        setRecords(prev => prev.map(r => r.id === id ? { ...r, notes: noteText } : r));
        setEditingNote(null);
    };

    return (
        <div>
            <div className="flex items-center justify-between" style={{ marginBottom: 28 }}>
                <div>
                    <h1>Revenue Audit Tool</h1>
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                        Run live audits on sales calls or review inbound submissions
                    </p>
                </div>
                <div className="flex gap-sm">
                    <button
                        className={`btn btn-sm ${tab === 'calculator' ? 'btn-primary' : 'btn-ghost'}`}
                        onClick={() => setTab('calculator')}
                    >
                        Calculator
                    </button>
                    <button
                        className={`btn btn-sm ${tab === 'records' ? 'btn-primary' : 'btn-ghost'}`}
                        onClick={() => setTab('records')}
                    >
                        Submissions ({records.length || '...'})
                    </button>
                </div>
            </div>

            {/* ── Calculator tab ── */}
            {tab === 'calculator' && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, alignItems: 'start' }}>

                    {/* Inputs */}
                    <div className="card animate-in">
                        <h3 style={{ marginBottom: 24 }}>Property Inputs</h3>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                            <div>
                                <label className="label">Hotel name</label>
                                <input className="form-input" value={hotelName} onChange={e => setHotelName(e.target.value)} placeholder="Hotel Selangor" />
                            </div>
                            <div>
                                <label className="label">GM / Contact name</label>
                                <input className="form-input" value={contactName} onChange={e => setContactName(e.target.value)} placeholder="Ahmad Farid" />
                            </div>
                            <div>
                                <label className="label">Email</label>
                                <input className="form-input" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="gm@hotel.com" />
                            </div>
                            <div>
                                <label className="label">Phone / WhatsApp</label>
                                <input className="form-input" value={phone} onChange={e => setPhone(e.target.value)} placeholder="+60 12-345 6789" />
                            </div>

                            <hr style={{ borderColor: 'var(--border-subtle)' }} />

                            <div>
                                <label className="label">Rooms: <strong style={{ color: 'var(--text-accent)' }}>{inputs.room_count}</strong></label>
                                <input type="range" min={20} max={200} step={5} value={inputs.room_count}
                                    onChange={e => setInputs(p => ({ ...p, room_count: +e.target.value }))}
                                    style={{ width: '100%', accentColor: 'var(--accent)' }} />
                            </div>
                            <div>
                                <label className="label">ADR: <strong style={{ color: 'var(--text-accent)' }}>RM {inputs.adr}</strong></label>
                                <input type="range" min={80} max={800} step={10} value={inputs.adr}
                                    onChange={e => setInputs(p => ({ ...p, adr: +e.target.value }))}
                                    style={{ width: '100%', accentColor: 'var(--accent)' }} />
                            </div>
                            <div>
                                <label className="label">Daily WhatsApp messages</label>
                                <select className="form-input"
                                    value={inputs.daily_msgs === null ? '' : String(inputs.daily_msgs)}
                                    onChange={e => setInputs(p => ({ ...p, daily_msgs: e.target.value === '' ? null : +e.target.value }))}>
                                    {DAILY_MSG_OPTIONS.map(o => (
                                        <option key={String(o.value)} value={o.value === null ? '' : String(o.value)}>{o.label}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="label">Front desk closes</label>
                                <select className="form-input" value={inputs.front_desk_close}
                                    onChange={e => setInputs(p => ({ ...p, front_desk_close: e.target.value }))}>
                                    {CLOSURE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="label">OTA commission rate</label>
                                <select className="form-input" value={inputs.ota_commission_rate}
                                    onChange={e => setInputs(p => ({ ...p, ota_commission_rate: +e.target.value }))}>
                                    {[15, 18, 20, 22, 25].map(v => (
                                        <option key={v} value={v}>{v}%</option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* Results */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                        {results ? (
                            <>
                                {/* Hero */}
                                <div style={{
                                    background: 'linear-gradient(135deg, rgba(248,113,113,0.15) 0%, transparent 100%)',
                                    border: '1px solid rgba(248,113,113,0.3)',
                                    borderRadius: 'var(--radius-lg)',
                                    padding: '28px 24px',
                                    textAlign: 'center',
                                    opacity: calculating ? 0.5 : 1,
                                    transition: 'opacity 0.2s',
                                }}>
                                    <div className="text-sm text-muted" style={{ marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.07em' }}>
                                        Conservative annual leakage
                                    </div>
                                    <div style={{ fontSize: 48, fontWeight: 800, color: '#f87171', lineHeight: 1 }}>
                                        {fmt(results.conservative_annual)}
                                    </div>
                                    <div className="text-sm text-muted" style={{ marginTop: 6 }}>per year</div>
                                </div>

                                {/* Table */}
                                <div className="card">
                                    <table style={{ width: '100%', fontSize: 14 }}>
                                        <tbody>
                                            {[
                                                ['Daily msgs used', results.daily_msgs_used],
                                                ['After-hours msgs/day', results.after_hours_msgs_per_day],
                                                ['Monthly after-hours msgs', Math.round(results.monthly_after_hours_msgs)],
                                                ['Lost bookings/month', results.lost_bookings_per_month],
                                                ['Revenue lost/month', fmt(results.revenue_lost_monthly)],
                                                ['OTA commission/month', fmt(results.ota_commission_monthly)],
                                                ['Total monthly leakage', fmt(results.total_monthly_leakage)],
                                                ['Annual leakage (full)', fmt(results.annual_leakage)],
                                                ['Annual leakage (conservative)', fmt(results.conservative_annual)],
                                            ].map(([label, value]) => (
                                                <tr key={String(label)} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                                                    <td style={{ padding: '10px 0', color: 'var(--text-secondary)' }}>{label}</td>
                                                    <td style={{ padding: '10px 0', textAlign: 'right', fontWeight: 600 }}>{value}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>

                                {/* ROI */}
                                <div style={{
                                    background: 'var(--success-bg)',
                                    border: '1px solid rgba(52,211,153,0.3)',
                                    borderRadius: 'var(--radius-lg)',
                                    padding: '20px 24px',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                }}>
                                    <div>
                                        <div className="text-sm text-muted">ROI (RM 499/mo)</div>
                                        <div style={{ fontSize: 24, fontWeight: 700, color: 'var(--success)' }}>{results.roi_multiple}x</div>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <div className="text-sm text-muted">Net Year 1</div>
                                        <div style={{ fontSize: 24, fontWeight: 700 }}>{fmt(results.annual_net_recovery)}</div>
                                    </div>
                                </div>

                                {/* Save button */}
                                <button className="btn btn-primary" onClick={saveAudit} disabled={saving}>
                                    {saving ? 'Saving...' : 'Save to Pipeline'}
                                </button>
                                {saveMsg && <p className="text-sm text-muted" style={{ textAlign: 'center' }}>{saveMsg}</p>}
                            </>
                        ) : (
                            <div className="flex justify-center" style={{ padding: 60 }}><div className="loader" /></div>
                        )}
                    </div>
                </div>
            )}

            {/* ── Records tab ── */}
            {tab === 'records' && (
                <>
                    {recordsLoading ? (
                        <div className="flex justify-center" style={{ padding: 60 }}><div className="loader" /></div>
                    ) : records.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-icon">📊</div>
                            <p>No audit submissions yet</p>
                            <p className="text-sm text-muted">Share the public audit link to start collecting leads</p>
                        </div>
                    ) : (
                        <div className="table-container animate-in">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Hotel</th>
                                        <th>Contact</th>
                                        <th>Rooms / ADR</th>
                                        <th>Conservative Annual</th>
                                        <th>ROI</th>
                                        <th>Status</th>
                                        <th>Notes</th>
                                        <th>Submitted</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {records.map(r => (
                                        <tr key={r.id}>
                                            <td>
                                                <strong>{r.hotel_name || '—'}</strong>
                                                <div className="text-sm text-muted">{r.source}</div>
                                            </td>
                                            <td>
                                                <div>{r.contact_name || '—'}</div>
                                                <div className="text-sm text-muted">{r.email || '—'}</div>
                                                {r.phone && <div className="text-sm text-muted">{r.phone}</div>}
                                            </td>
                                            <td>
                                                <div>{r.room_count} rooms</div>
                                                <div className="text-sm text-muted">RM {r.adr}/night</div>
                                            </td>
                                            <td style={{ color: '#f87171', fontWeight: 700 }}>
                                                {fmt(r.conservative_annual)}/yr
                                            </td>
                                            <td style={{ color: 'var(--success)', fontWeight: 600 }}>
                                                {r.roi_multiple}x
                                            </td>
                                            <td>
                                                <select
                                                    value={r.status}
                                                    onChange={e => updateStatus(r.id, e.target.value)}
                                                    style={{
                                                        background: 'var(--bg-input)',
                                                        border: '1px solid var(--border-default)',
                                                        borderRadius: 'var(--radius-sm)',
                                                        color: 'var(--text-primary)',
                                                        fontSize: 12,
                                                        padding: '4px 8px',
                                                    }}
                                                >
                                                    {STATUS_OPTIONS.map(s => (
                                                        <option key={s} value={s}>{s}</option>
                                                    ))}
                                                </select>
                                            </td>
                                            <td style={{ maxWidth: 180 }}>
                                                {editingNote === r.id ? (
                                                    <div className="flex gap-sm">
                                                        <input
                                                            className="form-input"
                                                            style={{ fontSize: 12 }}
                                                            value={noteText}
                                                            onChange={e => setNoteText(e.target.value)}
                                                            onKeyDown={e => e.key === 'Enter' && saveNote(r.id)}
                                                            autoFocus
                                                        />
                                                        <button className="btn btn-sm btn-primary" onClick={() => saveNote(r.id)}>Save</button>
                                                    </div>
                                                ) : (
                                                    <button
                                                        className="btn btn-ghost btn-sm"
                                                        style={{ fontSize: 12, textAlign: 'left' }}
                                                        onClick={() => { setEditingNote(r.id); setNoteText(r.notes || ''); }}
                                                    >
                                                        {r.notes || <span className="text-muted">+ Add note</span>}
                                                    </button>
                                                )}
                                            </td>
                                            <td className="text-sm text-muted">
                                                {new Date(r.created_at).toLocaleDateString()}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
