'use client';

import { useEffect, useState } from 'react';
import { apiGet, apiPut } from '@/lib/api';

interface SchedulerJobs {
    daily_report: boolean;
    followups: boolean;
    insights: boolean;
    cleanup: boolean;
}

const JOB_LABELS: Record<keyof SchedulerJobs, { label: string; description: string; icon: string }> = {
    daily_report: {
        label: 'Daily Report Email',
        description: 'Sends the 7:30am intelligence report to each property\'s notification email.',
        icon: '📧',
    },
    followups: {
        label: 'Automated Follow-ups',
        description: 'Sends 24h / 72h / 7d follow-up messages to active conversations.',
        icon: '🔁',
    },
    insights: {
        label: 'Monthly Insights',
        description: 'Generates and emails the 30-day guest sentiment report on the 1st of each month.',
        icon: '💡',
    },
    cleanup: {
        label: 'Data Retention Cleanup',
        description: 'Deletes leads and conversations older than 90 days (weekly). Keeps DB under free-tier limits.',
        icon: '🗑️',
    },
};

export default function SystemConfigPage() {
    const [jobs, setJobs] = useState<SchedulerJobs | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        apiGet<{ jobs: SchedulerJobs }>('/superadmin/scheduler-config')
            .then((data) => setJobs(data.jobs))
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false));
    }, []);

    const toggleJob = (key: keyof SchedulerJobs) => {
        if (!jobs) return;
        setJobs({ ...jobs, [key]: !jobs[key] });
    };

    const save = async () => {
        if (!jobs) return;
        setSaving(true);
        setError('');
        try {
            const data = await apiPut<{ jobs: SchedulerJobs }>('/superadmin/scheduler-config', { jobs });
            setJobs(data.jobs);
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
        } catch (e: any) {
            setError(e.message || 'Save failed');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div>
            <div style={{ marginBottom: 32 }}>
                <h1>System Configuration</h1>
                <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                    Control scheduler jobs and platform-wide settings
                </p>
            </div>

            {error && (
                <div className="card" style={{ padding: '12px 16px', marginBottom: 24, borderColor: 'var(--danger)', color: 'var(--danger)' }}>
                    {error}
                </div>
            )}

            <div className="card" style={{ padding: 24, marginBottom: 24 }}>
                <h3 style={{ fontSize: 15, marginBottom: 4 }}>⏱️ Scheduler Jobs</h3>
                <p className="text-sm text-muted" style={{ marginBottom: 20 }}>
                    Toggle which automated jobs run. Notification jobs are disabled by default in demo mode.
                </p>

                {loading ? (
                    <div className="flex justify-center" style={{ padding: 40 }}><div className="loader" /></div>
                ) : jobs ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                        {(Object.keys(JOB_LABELS) as Array<keyof SchedulerJobs>).map((key) => {
                            const meta = JOB_LABELS[key];
                            const enabled = jobs[key];
                            return (
                                <div
                                    key={key}
                                    className="flex items-center justify-between"
                                    style={{
                                        padding: '14px 16px',
                                        borderRadius: 8,
                                        border: '1px solid var(--border-subtle)',
                                        background: enabled ? 'var(--bg-card)' : 'var(--bg-base)',
                                        transition: 'background 0.2s',
                                    }}
                                >
                                    <div style={{ flex: 1 }}>
                                        <div className="flex items-center gap-sm" style={{ marginBottom: 2 }}>
                                            <span>{meta.icon}</span>
                                            <strong style={{ fontSize: 14 }}>{meta.label}</strong>
                                            <span className={`badge ${enabled ? 'badge-success' : 'badge-neutral'}`}>
                                                {enabled ? 'Enabled' : 'Disabled'}
                                            </span>
                                        </div>
                                        <p className="text-xs text-muted" style={{ marginLeft: 22 }}>{meta.description}</p>
                                    </div>
                                    <button
                                        className={`btn btn-sm ${enabled ? 'btn-danger' : 'btn-primary'}`}
                                        style={{ marginLeft: 16, minWidth: 80 }}
                                        onClick={() => toggleJob(key)}
                                    >
                                        {enabled ? 'Disable' : 'Enable'}
                                    </button>
                                </div>
                            );
                        })}
                    </div>
                ) : null}
            </div>

            <div className="flex items-center gap-sm">
                <button
                    className="btn btn-primary"
                    onClick={save}
                    disabled={saving || loading || !jobs}
                >
                    {saving ? 'Saving...' : 'Save Changes'}
                </button>
                {saved && (
                    <span className="text-sm" style={{ color: 'var(--success)' }}>
                        ✓ Saved
                    </span>
                )}
            </div>
        </div>
    );
}
