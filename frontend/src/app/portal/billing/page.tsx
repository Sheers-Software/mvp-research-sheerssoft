'use client';

import { useState } from 'react';
import { apiPost } from '@/lib/api';
import { useTenant } from '@/lib/tenant-context';
import Link from 'next/link';

interface PlanFeature {
    label: string;
    included: boolean;
}

interface Plan {
    tier: string;
    name: string;
    features: PlanFeature[];
    highlight?: boolean;
}

const PLANS: Plan[] = [
    {
        tier: 'pilot',
        name: 'Pilot',
        features: [
            { label: '1 property', included: true },
            { label: '500 conversations/month', included: true },
            { label: 'WhatsApp + Web Chat', included: true },
            { label: 'Email channel', included: false },
            { label: 'Priority support', included: false },
            { label: 'Dedicated account manager', included: false },
        ],
    },
    {
        tier: 'boutique',
        name: 'Boutique',
        highlight: true,
        features: [
            { label: '2 properties', included: true },
            { label: '2,000 conversations/month', included: true },
            { label: 'All channels (WhatsApp, Email, Web)', included: true },
            { label: 'Monthly AI insights', included: true },
            { label: 'Priority support', included: false },
            { label: 'Dedicated account manager', included: false },
        ],
    },
    {
        tier: 'independent',
        name: 'Independent',
        features: [
            { label: '5 properties', included: true },
            { label: '10,000 conversations/month', included: true },
            { label: 'All channels', included: true },
            { label: 'Monthly AI insights', included: true },
            { label: 'Priority support', included: true },
            { label: 'Dedicated account manager', included: false },
        ],
    },
    {
        tier: 'premium',
        name: 'Premium',
        features: [
            { label: 'Unlimited properties', included: true },
            { label: 'Unlimited conversations', included: true },
            { label: 'All channels', included: true },
            { label: 'Monthly AI insights', included: true },
            { label: 'Priority support', included: true },
            { label: 'Dedicated account manager', included: true },
        ],
    },
];

const STATUS_BADGE: Record<string, string> = {
    trialing: 'badge-warning',
    active: 'badge-success',
    cancelled: 'badge-danger',
    past_due: 'badge-danger',
};

export default function PortalBillingPage() {
    const { tenantTier, tenantId } = useTenant();
    const [upgrading, setUpgrading] = useState(false);
    const [subscribing, setSubscribing] = useState(false);
    const [error, setError] = useState('');

    const handleUpgrade = async () => {
        setUpgrading(true);
        setError('');
        try {
            const data = await apiPost<{ checkout_url: string }>('/billing/checkout-session');
            if (data?.checkout_url) {
                window.location.href = data.checkout_url;
            }
        } catch (e: unknown) {
            setError((e instanceof Error ? e.message : String(e)) || 'Failed to start upgrade. Please contact support.');
        } finally {
            setUpgrading(false);
        }
    };

    const handleSubscribe = async () => {
        if (!tenantId) { setError('Tenant not found. Please reload the page.'); return; }
        setSubscribing(true);
        setError('');
        try {
            const origin = window.location.origin;
            const data = await apiPost<{ checkout_url: string }>('/billing/subscribe', {
                tenant_id: tenantId,
                success_url: `${origin}/portal/billing?subscribed=1`,
                cancel_url: `${origin}/portal/billing`,
            });
            if (data?.checkout_url) {
                window.location.href = data.checkout_url;
            }
        } catch (e: unknown) {
            setError((e instanceof Error ? e.message : String(e)) || 'Failed to start subscription. Please contact support.');
        } finally {
            setSubscribing(false);
        }
    };

    const currentPlan = PLANS.find((p) => p.tier === tenantTier) ?? PLANS[0];

    return (
        <div>
            <div style={{ marginBottom: 28 }}>
                <h1>Billing</h1>
                <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                    Manage your subscription and plan
                </p>
            </div>

            {error && <div style={{ color: 'var(--danger)', marginBottom: 12, fontSize: 13 }}>{error}</div>}

            {/* Current plan card */}
            <div className="card animate-in" style={{ marginBottom: 28, padding: 24 }}>
                <div className="flex items-center justify-between" style={{ marginBottom: 16 }}>
                    <div>
                        <p className="text-xs text-muted" style={{ marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Current Plan</p>
                        <h2 style={{ fontSize: 22, fontWeight: 700 }}>{currentPlan.name}</h2>
                    </div>
                    <span className={`badge ${STATUS_BADGE['active']}`} style={{ fontSize: 13 }}>
                        Active
                    </span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 8, marginBottom: 20 }}>
                    {currentPlan.features.map((f) => (
                        <div key={f.label} className="flex items-center gap-sm">
                            <span style={{ color: f.included ? 'var(--success)' : 'var(--text-muted)', fontSize: 14 }}>
                                {f.included ? '✓' : '✗'}
                            </span>
                            <span className="text-sm" style={{ color: f.included ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                                {f.label}
                            </span>
                        </div>
                    ))}
                </div>

                <div className="flex items-center gap-sm" style={{ flexWrap: 'wrap' }}>
                    <button
                        className="btn btn-primary btn-sm"
                        onClick={handleSubscribe}
                        disabled={subscribing || upgrading}
                    >
                        {subscribing ? 'Redirecting…' : '✦ Activate RM 199/month'}
                    </button>
                    <button
                        className="btn btn-ghost btn-sm"
                        onClick={handleUpgrade}
                        disabled={upgrading || subscribing}
                    >
                        {upgrading ? 'Redirecting…' : '⬆ Upgrade Plan'}
                    </button>
                    <Link href="/portal/support" className="btn btn-ghost btn-sm">
                        Contact Support
                    </Link>
                </div>
                <p className="text-xs text-muted" style={{ marginTop: 8 }}>
                    RM 199/month · No contract · Cancel anytime · 3% performance fee on confirmed direct bookings only
                </p>
            </div>

            {/* All plan tiers for comparison */}
            <h3 style={{ marginBottom: 16, fontSize: 14, color: 'var(--text-muted)' }}>All Plans</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 16 }}>
                {PLANS.map((plan) => {
                    const isCurrent = plan.tier === (tenantTier ?? 'pilot');
                    return (
                        <div
                            key={plan.tier}
                            className="card"
                            style={{
                                padding: 20,
                                borderColor: isCurrent ? 'var(--accent)' : plan.highlight ? 'rgba(99,102,241,0.2)' : undefined,
                                position: 'relative',
                            }}
                        >
                            {isCurrent && (
                                <div style={{ position: 'absolute', top: -1, right: 12, background: 'var(--accent)', color: 'white', fontSize: 10, fontWeight: 700, padding: '2px 8px', borderRadius: '0 0 6px 6px', letterSpacing: '0.05em' }}>
                                    CURRENT
                                </div>
                            )}
                            <h4 style={{ marginBottom: 12 }}>{plan.name}</h4>
                            <div style={{ display: 'grid', gap: 6 }}>
                                {plan.features.map((f) => (
                                    <div key={f.label} className="flex items-center gap-sm">
                                        <span style={{ color: f.included ? 'var(--success)' : 'var(--text-muted)', fontSize: 12, flexShrink: 0 }}>
                                            {f.included ? '✓' : '—'}
                                        </span>
                                        <span className="text-xs" style={{ color: f.included ? 'var(--text-secondary)' : 'var(--text-muted)' }}>
                                            {f.label}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    );
                })}
            </div>

            <p className="text-xs text-muted" style={{ marginTop: 24, textAlign: 'center' }}>
                Need a custom plan?{' '}
                <a href="mailto:sales@sheerssoft.com" style={{ color: 'var(--accent)' }}>
                    Contact our sales team
                </a>
            </p>
        </div>
    );
}
