'use client';

import { useEffect, useState } from 'react';
import { DEMO_MODE } from '@/lib/api';
import { getPersona, setPersona, type DemoPersona } from '@/lib/demo/data';

/**
 * Slim top banner shown only in demo mode. Lets the pitcher jump between the
 * three user planes live (staff dashboard / tenant portal / superadmin ops).
 * Switching persona stores the choice and hard-navigates so AuthProvider
 * re-reads the seeded user for that plane.
 */
const PLANES: { persona: DemoPersona; label: string; href: string }[] = [
    { persona: 'staff', label: 'Property Staff', href: '/dashboard' },
    { persona: 'owner', label: 'Hotel Owner', href: '/portal' },
    { persona: 'superadmin', label: 'SheersSoft Admin', href: '/admin' },
];

export default function DemoPersonaBar() {
    const [persona, setP] = useState<DemoPersona>('owner');

    useEffect(() => {
        setP(getPersona());
    }, []);

    if (!DEMO_MODE) return null;

    const go = (p: DemoPersona, href: string) => {
        setPersona(p);
        window.location.href = href;
    };

    return (
        <div
            style={{
                position: 'sticky', top: 0, zIndex: 200,
                background: '#0F172A', color: '#fff',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                gap: 12, padding: '7px 14px', fontSize: 12.5, flexWrap: 'wrap',
            }}
        >
            <span style={{ fontWeight: 600, letterSpacing: '0.04em', opacity: 0.85 }}>
                ✦ INVESTOR DEMO
            </span>
            <span style={{ opacity: 0.6 }}>View as:</span>
            {PLANES.map((pl) => {
                const active = pl.persona === persona;
                return (
                    <button
                        key={pl.persona}
                        onClick={() => go(pl.persona, pl.href)}
                        style={{
                            background: active ? 'var(--teal, #22C55E)' : 'rgba(255,255,255,0.1)',
                            color: '#fff', border: 'none', borderRadius: 6,
                            padding: '4px 11px', fontSize: 12, cursor: 'pointer',
                            fontWeight: active ? 600 : 400,
                        }}
                    >
                        {pl.label}
                    </button>
                );
            })}
            <a href="/" style={{ color: 'rgba(255,255,255,0.7)', textDecoration: 'none', marginLeft: 4 }}>
                ← Home
            </a>
        </div>
    );
}
