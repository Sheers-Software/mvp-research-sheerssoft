'use client';

import { useState, useRef, useEffect } from 'react';
import { demoChatScript } from '@/lib/demo/data';

/**
 * Scripted concierge chat for the landing page. Walks through a believable
 * guest → AI conversation (availability → amenity → lead capture) from a local
 * script — zero LLM cost, no API keys, can't fail during a pitch.
 */
interface ChatMsg {
    role: 'user' | 'assistant';
    content: string;
}

export default function DemoChat() {
    const [messages, setMessages] = useState<ChatMsg[]>([
        { role: 'assistant', content: 'Welcome to Lumière Suites 🌙 — try sending a message below to see the AI concierge in action.' },
    ]);
    const [step, setStep] = useState(0);
    const [typing, setTyping] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, typing]);

    const sendNext = () => {
        if (step >= demoChatScript.length || typing) return;
        const turn = demoChatScript[step];
        setMessages((m) => [...m, { role: 'user', content: turn.user }]);
        setTyping(true);
        setTimeout(() => {
            setMessages((m) => [...m, { role: 'assistant', content: turn.ai }]);
            setTyping(false);
            setStep((s) => s + 1);
        }, 1100);
    };

    const reset = () => {
        setMessages([{ role: 'assistant', content: 'Welcome to Lumière Suites 🌙 — try sending a message below to see the AI concierge in action.' }]);
        setStep(0);
    };

    const done = step >= demoChatScript.length;
    const nextLabel = !done ? demoChatScript[step].user : '';

    return (
        <div className="card" style={{ padding: 0, overflow: 'hidden', maxWidth: 440, width: '100%' }}>
            <div style={{ background: 'var(--teal, #1d9e75)', color: '#fff', padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'rgba(255,255,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18 }}>🌙</div>
                <div>
                    <div style={{ fontWeight: 600, fontSize: 14 }}>Lumière AI Concierge</div>
                    <div style={{ fontSize: 11, opacity: 0.85 }}>● Online · replies in seconds</div>
                </div>
            </div>

            <div style={{ padding: 16, height: 340, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 10, background: 'var(--bg-subtle, #f7f8fa)' }}>
                {messages.map((m, i) => (
                    <div
                        key={i}
                        style={{
                            alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                            maxWidth: '82%',
                            background: m.role === 'user' ? 'var(--teal, #1d9e75)' : '#fff',
                            color: m.role === 'user' ? '#fff' : 'var(--text, #1a1a1a)',
                            padding: '9px 13px',
                            borderRadius: 14,
                            borderBottomRightRadius: m.role === 'user' ? 4 : 14,
                            borderBottomLeftRadius: m.role === 'user' ? 14 : 4,
                            fontSize: 13.5,
                            lineHeight: 1.45,
                            boxShadow: '0 1px 2px rgba(0,0,0,0.06)',
                        }}
                    >
                        {m.content}
                    </div>
                ))}
                {typing && (
                    <div style={{ alignSelf: 'flex-start', background: '#fff', padding: '10px 14px', borderRadius: 14, fontSize: 13, color: 'var(--text-muted, #888)', boxShadow: '0 1px 2px rgba(0,0,0,0.06)' }}>
                        <span className="demo-typing">typing…</span>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            <div style={{ padding: 12, borderTop: '1px solid var(--border-subtle, #eee)', background: '#fff' }}>
                {done ? (
                    <button className="btn btn-ghost w-full" onClick={reset} style={{ fontSize: 13 }}>
                        ↺ Replay the conversation
                    </button>
                ) : (
                    <button
                        className="btn btn-primary w-full"
                        onClick={sendNext}
                        disabled={typing}
                        style={{ fontSize: 13, textAlign: 'left', justifyContent: 'flex-start' }}
                    >
                        Send: “{nextLabel}”
                    </button>
                )}
            </div>
        </div>
    );
}
