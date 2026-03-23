'use client';

import { useEffect, useState } from 'react';
import { apiGet, apiPost, apiDelete } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { useTenant } from '@/lib/tenant-context';

interface Member {
    id: string;
    user_id: string;
    full_name: string;
    email: string;
    role: string;
    last_login: string | null;
}

const ROLE_BADGE: Record<string, string> = {
    owner: 'badge-warning',
    admin: 'badge-success',
    staff: 'badge-success',
};

const ROLE_LABELS: Record<string, string> = {
    owner: 'Owner',
    admin: 'Admin',
    staff: 'Staff',
};

export default function PortalTeamPage() {
    const { user } = useAuth();
    const { tenantId } = useTenant();
    const [members, setMembers] = useState<Member[]>([]);
    const [loading, setLoading] = useState(true);
    const [showInviteForm, setShowInviteForm] = useState(false);
    const [inviteForm, setInviteForm] = useState({ email: '', full_name: '', role: 'staff' });
    const [inviting, setInviting] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const loadMembers = () => {
        setLoading(true);
        apiGet<Member[]>('/portal/team')
            .then((data) => setMembers(data || []))
            .catch(() => setMembers([]))
            .finally(() => setLoading(false));
    };

    useEffect(() => { loadMembers(); }, []);

    const handleInvite = async () => {
        if (!inviteForm.email.trim() || !tenantId) return;
        setInviting(true);
        setError('');
        setSuccess('');
        try {
            await apiPost(`/onboarding/invite-user/${tenantId}`, inviteForm);
            setSuccess(`Invitation sent to ${inviteForm.email}`);
            setInviteForm({ email: '', full_name: '', role: 'staff' });
            setShowInviteForm(false);
            loadMembers();
        } catch (e: unknown) {
            setError((e instanceof Error ? e.message : String(e)) || 'Failed to send invitation');
        } finally {
            setInviting(false);
        }
    };

    const handleRemove = async (membershipId: string, memberName: string) => {
        if (!window.confirm(`Remove ${memberName} from this team?`)) return;
        try {
            await apiDelete(`/portal/team/${membershipId}`);
            loadMembers();
        } catch (e: unknown) {
            setError((e instanceof Error ? e.message : String(e)) || 'Failed to remove member');
        }
    };

    return (
        <div>
            <div className="flex items-center justify-between" style={{ marginBottom: 28 }}>
                <div>
                    <h1>Team Members</h1>
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                        Manage who has access to your AI concierge portal
                    </p>
                </div>
                <button
                    className="btn btn-primary btn-sm"
                    onClick={() => { setShowInviteForm(!showInviteForm); setError(''); setSuccess(''); }}
                >
                    + Invite Member
                </button>
            </div>

            {error && <div style={{ color: 'var(--danger)', marginBottom: 12, fontSize: 13 }}>{error}</div>}
            {success && <div style={{ color: 'var(--success)', marginBottom: 12, fontSize: 13 }}>{success}</div>}

            {/* Invite form */}
            {showInviteForm && (
                <div className="card animate-in" style={{ marginBottom: 20, borderColor: 'rgba(99,102,241,0.3)', padding: 24 }}>
                    <h3 style={{ marginBottom: 16, fontSize: 14 }}>Invite Team Member</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
                        <div>
                            <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Email</label>
                            <input
                                type="email"
                                value={inviteForm.email}
                                onChange={(e) => setInviteForm((f) => ({ ...f, email: e.target.value }))}
                                placeholder="staff@yourhotel.com"
                                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-subtle)', background: 'var(--surface)', color: 'var(--text-primary)', fontSize: 13, boxSizing: 'border-box' }}
                            />
                        </div>
                        <div>
                            <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Full Name</label>
                            <input
                                type="text"
                                value={inviteForm.full_name}
                                onChange={(e) => setInviteForm((f) => ({ ...f, full_name: e.target.value }))}
                                placeholder="Jane Smith"
                                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-subtle)', background: 'var(--surface)', color: 'var(--text-primary)', fontSize: 13, boxSizing: 'border-box' }}
                            />
                        </div>
                    </div>
                    <div style={{ marginBottom: 16 }}>
                        <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Role</label>
                        <select
                            value={inviteForm.role}
                            onChange={(e) => setInviteForm((f) => ({ ...f, role: e.target.value }))}
                            style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-subtle)', background: 'var(--surface)', color: 'var(--text-primary)', fontSize: 13 }}
                        >
                            <option value="staff">Staff</option>
                            <option value="admin">Admin</option>
                            <option value="owner">Owner</option>
                        </select>
                    </div>
                    <div className="flex items-center gap-sm">
                        <button
                            className="btn btn-primary btn-sm"
                            onClick={handleInvite}
                            disabled={inviting}
                        >
                            {inviting ? 'Sending…' : 'Send Invitation'}
                        </button>
                        <button
                            className="btn btn-ghost btn-sm"
                            onClick={() => { setShowInviteForm(false); setInviteForm({ email: '', full_name: '', role: 'staff' }); }}
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}

            {/* Members table */}
            {loading ? (
                <div className="flex justify-center" style={{ padding: 60 }}>
                    <div className="loader" />
                </div>
            ) : members.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">👥</div>
                    <p>No team members yet</p>
                    <p className="text-sm text-muted" style={{ marginTop: 4 }}>
                        Invite your hotel staff to access the dashboard
                    </p>
                </div>
            ) : (
                <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                                <th style={{ padding: '12px 20px', textAlign: 'left', fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Name</th>
                                <th style={{ padding: '12px 20px', textAlign: 'left', fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Email</th>
                                <th style={{ padding: '12px 20px', textAlign: 'left', fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Role</th>
                                <th style={{ padding: '12px 20px', textAlign: 'left', fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Last Login</th>
                                <th style={{ padding: '12px 20px', textAlign: 'right', fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {members.map((member, idx) => {
                                const isOwnAccount = member.user_id === user?.id || member.email === user?.email;
                                return (
                                    <tr
                                        key={member.id}
                                        style={{ borderBottom: idx < members.length - 1 ? '1px solid var(--border-subtle)' : 'none' }}
                                    >
                                        <td style={{ padding: '14px 20px', fontSize: 14 }}>{member.full_name || '—'}</td>
                                        <td style={{ padding: '14px 20px', fontSize: 13, color: 'var(--text-secondary)' }}>{member.email}</td>
                                        <td style={{ padding: '14px 20px' }}>
                                            <span className={`badge ${ROLE_BADGE[member.role] ?? 'badge-warning'}`}>
                                                {ROLE_LABELS[member.role] ?? member.role}
                                            </span>
                                        </td>
                                        <td style={{ padding: '14px 20px', fontSize: 13, color: 'var(--text-muted)' }}>
                                            {member.last_login
                                                ? new Date(member.last_login).toLocaleDateString()
                                                : 'Never'}
                                        </td>
                                        <td style={{ padding: '14px 20px', textAlign: 'right' }}>
                                            {!isOwnAccount && (
                                                <button
                                                    className="btn btn-sm"
                                                    style={{ background: 'none', color: 'var(--danger)', border: '1px solid var(--danger)', borderRadius: 6, padding: '4px 10px', cursor: 'pointer', fontSize: 12 }}
                                                    onClick={() => handleRemove(member.id, member.full_name || member.email)}
                                                >
                                                    Remove
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
