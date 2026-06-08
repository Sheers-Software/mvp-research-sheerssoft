'use client';

import { useAuth } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { DEMO_MODE } from '@/lib/api';
import { setPersona, type DemoPersona } from '@/lib/demo/data';
import PublicNav from '@/components/PublicNav';
import DemoChat from '@/components/DemoChat';
import Logo from '@/components/Logo';

/**
 * Root page.
 * - Demo mode: full marketing landing page for investors/buyers.
 * - Otherwise: redirect based on auth state (original behavior).
 */
export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (DEMO_MODE) return; // landing renders below
    if (loading) return;
    if (!user) {
      router.replace('/login');
    } else if (user.is_superadmin) {
      router.replace('/admin');
    } else {
      router.replace('/dashboard');
    }
  }, [user, loading, router]);

  if (!DEMO_MODE) {
    return (
      <div className="login-page">
        <div className="loader" />
      </div>
    );
  }

  return <Landing />;
}

function enter(persona: DemoPersona, href: string) {
  setPersona(persona);
  window.location.href = href;
}

const METRICS = [
  { value: 'RM 1.03M', label: 'Annual revenue recovered', color: 'var(--teal, #1d9e75)' },
  { value: '91%', label: 'Inquiries handled by AI', color: 'var(--amber, #d99a2b)' },
  { value: '6.4s', label: 'Avg. response time', color: 'var(--purple, #7c5cff)' },
  { value: '24/7', label: 'After-hours coverage', color: 'var(--text, #1a1a1a)' },
];

const STEPS = [
  { icon: '💬', title: 'Guest messages', body: 'A guest reaches out on WhatsApp, web chat, or email — at 2am, after the front desk has gone home.' },
  { icon: '🤖', title: 'AI concierge replies', body: 'In seconds, the AI answers from your knowledge base in English or Bahasa Malaysia, and captures booking intent.' },
  { icon: '🎯', title: 'Lead captured', body: 'Guest name, contact, and intent are logged as a qualified lead — then handed to staff if needed.' },
  { icon: '📈', title: 'Revenue recovered', body: 'Every recovered booking is tracked with ROI analytics owners can see at a glance.' },
];

function Landing() {
  useEffect(() => { window.scrollTo(0, 0); }, []);

  return (
    <>
      <PublicNav />

      {/* Hero — padding-top clears demo bar (36px) + public nav (58px) + breathing room */}
      <section style={{ maxWidth: 1140, margin: '0 auto', padding: '116px 24px 40px' }}>
        <div style={{ display: 'flex', gap: 48, flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ flex: '1 1 420px', minWidth: 300 }}>
            <div style={{ marginBottom: 20 }}>
              <Logo size={36} variant="green" showText />
            </div>
            <h1 style={{ fontSize: 44, lineHeight: 1.1, letterSpacing: '-0.02em', marginBottom: 18 }}>
              Stop losing bookings<br />after the front desk closes.
            </h1>
            <p style={{ fontSize: 17, color: 'var(--text2, #555)', lineHeight: 1.55, marginBottom: 28, maxWidth: 520 }}>
              Nocturn AI answers every guest message instantly across WhatsApp, web, and email —
              capturing leads and recovering revenue that would otherwise slip away overnight.
            </p>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <button className="btn btn-primary btn-lg" onClick={() => enter('owner', '/portal')}>
                Explore the live dashboard →
              </button>
              <a href="#demo" className="btn btn-ghost btn-lg">Try the AI concierge</a>
            </div>
            <p className="text-sm" style={{ color: 'var(--text3, #999)', marginTop: 16 }}>
              Self-contained interactive demo · no signup required
            </p>
          </div>

          <div style={{ flex: '1 1 380px', display: 'flex', justifyContent: 'center' }}>
            <span id="demo" style={{ position: 'absolute', marginTop: -80 }} />
            <DemoChat />
          </div>
        </div>
      </section>

      {/* Metrics band */}
      <section style={{ background: 'var(--bg-subtle, #f7f8fa)', borderTop: '1px solid var(--border-subtle,#eee)', borderBottom: '1px solid var(--border-subtle,#eee)' }}>
        <div style={{ maxWidth: 1140, margin: '0 auto', padding: '32px 24px' }}>
          <div className="grid grid-4" style={{ gap: 20 }}>
            {METRICS.map((m) => (
              <div key={m.label} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 30, fontWeight: 700, color: m.color, letterSpacing: '-0.02em' }}>{m.value}</div>
                <div className="text-sm" style={{ color: 'var(--text3,#999)', marginTop: 4 }}>{m.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section style={{ maxWidth: 1140, margin: '0 auto', padding: '56px 24px' }}>
        <div style={{ textAlign: 'center', marginBottom: 36 }}>
          <h2 style={{ fontSize: 30, letterSpacing: '-0.02em', marginBottom: 10 }}>How it works</h2>
          <p style={{ color: 'var(--text2,#555)', fontSize: 16 }}>From missed message to recovered revenue — automatically.</p>
        </div>
        <div className="grid grid-4" style={{ gap: 18 }}>
          {STEPS.map((s, i) => (
            <div key={s.title} className="card" style={{ padding: '24px 20px' }}>
              <div style={{ fontSize: 28, marginBottom: 12 }}>{s.icon}</div>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--teal,#1d9e75)', marginBottom: 6 }}>STEP {i + 1}</div>
              <h4 style={{ marginBottom: 8 }}>{s.title}</h4>
              <p className="text-sm" style={{ color: 'var(--text2,#555)', lineHeight: 1.5 }}>{s.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Plane explorer */}
      <section style={{ background: '#0F172A', color: '#fff' }}>
        <div style={{ maxWidth: 1140, margin: '0 auto', padding: '56px 24px' }}>
          <div style={{ textAlign: 'center', marginBottom: 36 }}>
            <h2 style={{ fontSize: 30, letterSpacing: '-0.02em', marginBottom: 10, color: '#fff' }}>Explore the full product</h2>
            <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: 16 }}>One platform, three tailored experiences. Jump into any of them — fully populated with demo data.</p>
          </div>
          <div className="grid grid-3" style={{ gap: 18 }}>
            {[
              { p: 'staff' as DemoPersona, href: '/dashboard', icon: '📊', t: 'Property Staff', d: 'Live conversations, lead triage, and daily ROI — the operational cockpit for front-office teams.' },
              { p: 'owner' as DemoPersona, href: '/portal', icon: '🏨', t: 'Hotel Owner', d: 'Configure the business: knowledge base, team, channels, billing, and multi-property analytics.' },
              { p: 'superadmin' as DemoPersona, href: '/admin', icon: '🛠️', t: 'SheersSoft Admin', d: 'Platform operations: tenants, onboarding pipeline, support tickets, and system health.' },
            ].map((c) => (
              <div
                key={c.p}
                onClick={() => enter(c.p, c.href)}
                style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 12, padding: 24, cursor: 'pointer' }}
              >
                <div style={{ fontSize: 30, marginBottom: 12 }}>{c.icon}</div>
                <h4 style={{ color: '#fff', marginBottom: 8 }}>{c.t}</h4>
                <p style={{ fontSize: 13.5, color: 'rgba(255,255,255,0.7)', lineHeight: 1.5, marginBottom: 14 }}>{c.d}</p>
                <span style={{ color: 'var(--teal,#22C55E)', fontSize: 13, fontWeight: 600 }}>Enter as {c.t} →</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ maxWidth: 1140, margin: '0 auto', padding: '32px 24px', textAlign: 'center', color: 'var(--text3,#999)', fontSize: 13 }}>
        Nocturn AI · Powered by SheersSoft · This is an interactive demo with seeded data.
      </footer>
    </>
  );
}
