'use client';

import { useState } from 'react';
import Link from 'next/link';
import PublicNav from '@/components/PublicNav';

const CHANNELS = [
  { id: 'whatsapp', label: 'WhatsApp' },
  { id: 'email', label: 'Email' },
  { id: 'phone', label: 'Phone' },
  { id: 'web', label: 'Website chat' },
];

export default function ApplyPage() {
  const [form, setForm] = useState({
    hotel_name: '',
    contact_name: '',
    email: '',
    phone: '',
    room_count: '',
    current_channels: [] as string[],
    message: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const toggleChannel = (id: string) => {
    setForm(f => ({
      ...f,
      current_channels: f.current_channels.includes(id)
        ? f.current_channels.filter(c => c !== id)
        : [...f.current_channels, id],
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      const res = await fetch('/api/v1/applications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          hotel_name: form.hotel_name,
          contact_name: form.contact_name,
          email: form.email,
          phone: form.phone || undefined,
          room_count: form.room_count ? parseInt(form.room_count) : undefined,
          current_channels: form.current_channels.length ? form.current_channels : undefined,
          message: form.message || undefined,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Submission failed. Please try again.');
      }
      setSubmitted(true);
    } catch (err: any) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <PublicNav />

      <div className="apply-page">
        <div className="apply-container">

          {submitted ? (
            /* ── Success state ─────────────────────────────── */
            <div className="apply-success animate-in">
              <div className="apply-success-icon">✅</div>
              <h2>You&apos;re on the list</h2>
              <p>
                Thanks, <strong>{form.contact_name.split(' ')[0]}</strong>. Our team will review your application
                and reach out to <strong>{form.email}</strong> within 1 business day.
              </p>
              <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 8 }}>
                While you wait, browse the{' '}
                <a href="https://ai.sheerssoft.com" target="_blank" rel="noopener">
                  Nocturn AI features
                </a>{' '}
                or{' '}
                <Link href="/login">sign in</Link> if you already have an account.
              </p>
            </div>

          ) : (
            <>
              {/* ── Left col — value prop ─────────────────── */}
              <div className="apply-left">
                <div className="apply-badge">Now accepting hotels — pilot pricing</div>
                <h1 className="apply-headline">
                  Never miss a booking<br />inquiry again.
                </h1>
                <p className="apply-sub">
                  Nocturn AI handles guest inquiries 24/7 across WhatsApp, email,
                  and web chat — capturing leads while your team sleeps.
                </p>

                <ul className="apply-benefits">
                  <li>
                    <span className="apply-check">✓</span>
                    <span>Daily GM Report at 9 AM — revenue recovered, OTA fees saved</span>
                  </li>
                  <li>
                    <span className="apply-check">✓</span>
                    <span>Bilingual AI (EN + BM) trained on your hotel&apos;s knowledge base</span>
                  </li>
                  <li>
                    <span className="apply-check">✓</span>
                    <span>Zero missed inquiries — AI responds in seconds, 24/7</span>
                  </li>
                  <li>
                    <span className="apply-check">✓</span>
                    <span>Direct booking engine — bypasses OTA commissions</span>
                  </li>
                  <li>
                    <span className="apply-check">✓</span>
                    <span>Live in 48 hours — no engineering required</span>
                  </li>
                </ul>

                <div className="apply-social-proof">
                  <div className="apply-stat">
                    <span className="apply-stat-num">94%</span>
                    <span className="apply-stat-label">avg guest sentiment</span>
                  </div>
                  <div className="apply-stat-divider" />
                  <div className="apply-stat">
                    <span className="apply-stat-num">0</span>
                    <span className="apply-stat-label">missed inquiries</span>
                  </div>
                  <div className="apply-stat-divider" />
                  <div className="apply-stat">
                    <span className="apply-stat-num">20%</span>
                    <span className="apply-stat-label">OTA fees saved</span>
                  </div>
                </div>
              </div>

              {/* ── Right col — form ─────────────────────── */}
              <div className="apply-right">
                <div className="apply-card">
                  <div className="apply-card-header">
                    <h2>Get started</h2>
                    <p>Tell us about your property — we&apos;ll set everything up for you.</p>
                  </div>

                  <form onSubmit={handleSubmit} className="apply-form">
                    <div className="apply-row">
                      <div className="input-group">
                        <label htmlFor="hotel_name">Hotel / property name <span className="apply-req">*</span></label>
                        <input
                          id="hotel_name"
                          type="text"
                          className="input"
                          placeholder="Grand Hyatt Kuala Lumpur"
                          value={form.hotel_name}
                          onChange={e => setForm(f => ({ ...f, hotel_name: e.target.value }))}
                          required
                        />
                      </div>
                    </div>

                    <div className="apply-row apply-row-2">
                      <div className="input-group">
                        <label htmlFor="contact_name">Your name <span className="apply-req">*</span></label>
                        <input
                          id="contact_name"
                          type="text"
                          className="input"
                          placeholder="Ahmad Razif"
                          value={form.contact_name}
                          onChange={e => setForm(f => ({ ...f, contact_name: e.target.value }))}
                          required
                        />
                      </div>
                      <div className="input-group">
                        <label htmlFor="phone">Phone (optional)</label>
                        <input
                          id="phone"
                          type="tel"
                          className="input"
                          placeholder="+60 12-345 6789"
                          value={form.phone}
                          onChange={e => setForm(f => ({ ...f, phone: e.target.value }))}
                        />
                      </div>
                    </div>

                    <div className="apply-row apply-row-2">
                      <div className="input-group">
                        <label htmlFor="email">Work email <span className="apply-req">*</span></label>
                        <input
                          id="email"
                          type="email"
                          className="input"
                          placeholder="gm@yourhotel.com"
                          value={form.email}
                          onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                          required
                        />
                      </div>
                      <div className="input-group">
                        <label htmlFor="room_count">Number of rooms</label>
                        <input
                          id="room_count"
                          type="number"
                          className="input"
                          placeholder="120"
                          min="1"
                          max="10000"
                          value={form.room_count}
                          onChange={e => setForm(f => ({ ...f, room_count: e.target.value }))}
                        />
                      </div>
                    </div>

                    <div className="input-group">
                      <label>Current inquiry channels</label>
                      <div className="apply-channels">
                        {CHANNELS.map(ch => (
                          <button
                            key={ch.id}
                            type="button"
                            className={`apply-channel-btn${form.current_channels.includes(ch.id) ? ' active' : ''}`}
                            onClick={() => toggleChannel(ch.id)}
                          >
                            {ch.label}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="input-group">
                      <label htmlFor="message">Anything else you&apos;d like us to know?</label>
                      <textarea
                        id="message"
                        className="input"
                        rows={3}
                        placeholder="e.g. We're a boutique resort with high WhatsApp volume after hours..."
                        value={form.message}
                        onChange={e => setForm(f => ({ ...f, message: e.target.value }))}
                        style={{ resize: 'vertical' }}
                      />
                    </div>

                    {error && (
                      <p style={{ color: 'var(--danger)', fontSize: 13 }}>{error}</p>
                    )}

                    <button
                      type="submit"
                      className="btn btn-primary btn-lg w-full"
                      disabled={submitting}
                    >
                      {submitting ? (
                        <><span className="loader" style={{ width: 18, height: 18 }} /> Submitting...</>
                      ) : (
                        'Request access →'
                      )}
                    </button>

                    <p className="apply-terms">
                      By submitting, you agree to be contacted by SheersSoft.
                      Already have an account?{' '}
                      <Link href="/login">Sign in</Link>
                    </p>
                  </form>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}
