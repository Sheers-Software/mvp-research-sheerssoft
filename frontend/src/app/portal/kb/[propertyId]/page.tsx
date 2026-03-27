'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { apiGet, apiPost, apiPut, apiDelete } from '@/lib/api';
import Link from 'next/link';

type Tab = 'faqs' | 'rooms' | 'policies' | 'facilities' | 'general';

interface KBDoc {
    id: string;
    doc_type: string;
    title: string;
    content: string;
    updated_at: string;
}

const TABS: { key: Tab; label: string; types: string[] }[] = [
    { key: 'faqs', label: 'FAQs', types: ['faqs'] },
    { key: 'rooms', label: 'Rooms & Rates', types: ['rooms', 'rates'] },
    { key: 'policies', label: 'Policies', types: ['policies'] },
    { key: 'facilities', label: 'Facilities', types: ['facilities'] },
    { key: 'general', label: 'General', types: ['general'] },
];

function tabForType(docType: string): Tab {
    if (docType === 'faqs') return 'faqs';
    if (docType === 'rooms' || docType === 'rates') return 'rooms';
    if (docType === 'policies') return 'policies';
    if (docType === 'facilities') return 'facilities';
    return 'general';
}

export default function PortalKBPage() {
    const params = useParams();
    const propertyId = params?.propertyId as string;

    const [documents, setDocuments] = useState<KBDoc[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<Tab>('faqs');
    const [showAddModal, setShowAddModal] = useState(false);
    const [addForm, setAddForm] = useState({ doc_type: 'faqs', title: '', content: '' });
    const [saving, setSaving] = useState(false);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editContent, setEditContent] = useState('');
    const [editSaving, setEditSaving] = useState(false);
    const [error, setError] = useState('');

    const loadDocs = () => {
        setLoading(true);
        apiGet<KBDoc[]>(`/properties/${propertyId}/kb`)
            .then((data) => setDocuments(data || []))
            .catch(() => setDocuments([]))
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        if (propertyId) loadDocs();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [propertyId]);

    const visibleDocs = documents.filter((d) => tabForType(d.doc_type) === activeTab);

    const handleAdd = async () => {
        if (!addForm.title.trim() || !addForm.content.trim()) return;
        setSaving(true);
        setError('');
        try {
            await apiPost(`/properties/${propertyId}/kb`, addForm);
            setAddForm({ doc_type: 'faqs', title: '', content: '' });
            setShowAddModal(false);
            loadDocs();
        } catch (e: unknown) {
            setError((e instanceof Error ? e.message : String(e)) || 'Failed to save');
        } finally {
            setSaving(false);
        }
    };

    const handleEdit = async (doc: KBDoc) => {
        setEditSaving(true);
        setError('');
        try {
            await apiPut(`/properties/${propertyId}/kb/${doc.id}`, { ...doc, content: editContent });
            setEditingId(null);
            loadDocs();
        } catch (e: unknown) {
            setError((e instanceof Error ? e.message : String(e)) || 'Failed to save');
        } finally {
            setEditSaving(false);
        }
    };

    const handleDelete = async (docId: string) => {
        if (!window.confirm('Delete this document?')) return;
        try {
            await apiDelete(`/properties/${propertyId}/kb/${docId}`);
            loadDocs();
        } catch (e: unknown) {
            setError((e instanceof Error ? e.message : String(e)) || 'Failed to delete');
        }
    };

    return (
        <div>
            {/* Header */}
            <div className="flex items-center justify-between" style={{ marginBottom: 28 }}>
                <div>
                    <h1>Knowledge Base</h1>
                    <p className="text-muted text-sm" style={{ marginTop: 4 }}>
                        Manage what your AI concierge knows about this property
                    </p>
                </div>
                <div className="flex items-center gap-sm">
                    <Link href="/welcome" className="btn btn-ghost btn-sm">
                        📋 Use Wizard
                    </Link>
                    <button
                        className="btn btn-primary btn-sm"
                        onClick={() => setShowAddModal(true)}
                    >
                        + Add Document
                    </button>
                </div>
            </div>

            {error && (
                <div style={{ color: 'var(--danger)', marginBottom: 12, fontSize: 13 }}>{error}</div>
            )}

            {/* Tab bar */}
            <div style={{ display: 'flex', gap: 4, marginBottom: 20, borderBottom: '1px solid var(--border-subtle)', paddingBottom: 0 }}>
                {TABS.map((tab) => {
                    const count = documents.filter((d) => tabForType(d.doc_type) === tab.key).length;
                    return (
                        <button
                            key={tab.key}
                            onClick={() => setActiveTab(tab.key)}
                            style={{
                                padding: '8px 16px',
                                background: 'none',
                                border: 'none',
                                borderBottom: activeTab === tab.key ? '2px solid var(--accent)' : '2px solid transparent',
                                color: activeTab === tab.key ? 'var(--accent)' : 'var(--text-secondary)',
                                fontWeight: activeTab === tab.key ? 600 : 400,
                                cursor: 'pointer',
                                fontSize: 13,
                                marginBottom: -1,
                            }}
                        >
                            {tab.label}
                            {count > 0 && (
                                <span style={{ marginLeft: 6, fontSize: 11, background: 'var(--border-subtle)', borderRadius: 10, padding: '1px 6px' }}>
                                    {count}
                                </span>
                            )}
                        </button>
                    );
                })}
            </div>

            {/* Add document modal */}
            {showAddModal && (
                <div className="card animate-in" style={{ marginBottom: 20, borderColor: 'rgba(99,102,241,0.3)', padding: 24 }}>
                    <h3 style={{ marginBottom: 16, fontSize: 14 }}>Add Document</h3>
                    <div style={{ display: 'grid', gap: 12 }}>
                        <div>
                            <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Type</label>
                            <select
                                value={addForm.doc_type}
                                onChange={(e) => setAddForm((f) => ({ ...f, doc_type: e.target.value }))}
                                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13 }}
                            >
                                <option value="faqs">FAQs</option>
                                <option value="rooms">Rooms</option>
                                <option value="rates">Rates</option>
                                <option value="facilities">Facilities</option>
                                <option value="policies">Policies</option>
                                <option value="general">General</option>
                            </select>
                        </div>
                        <div>
                            <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Title</label>
                            <input
                                type="text"
                                value={addForm.title}
                                onChange={(e) => setAddForm((f) => ({ ...f, title: e.target.value }))}
                                placeholder="e.g. Breakfast FAQ"
                                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13, boxSizing: 'border-box' }}
                            />
                        </div>
                        <div>
                            <label className="text-sm" style={{ display: 'block', marginBottom: 4 }}>Content</label>
                            <textarea
                                value={addForm.content}
                                onChange={(e) => setAddForm((f) => ({ ...f, content: e.target.value }))}
                                placeholder="Enter document content here..."
                                rows={8}
                                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13, resize: 'vertical', boxSizing: 'border-box', fontFamily: 'inherit' }}
                            />
                        </div>
                    </div>
                    <div className="flex items-center gap-sm" style={{ marginTop: 16 }}>
                        <button
                            className="btn btn-primary btn-sm"
                            onClick={handleAdd}
                            disabled={saving}
                        >
                            {saving ? 'Saving…' : 'Save Document'}
                        </button>
                        <button
                            className="btn btn-ghost btn-sm"
                            onClick={() => { setShowAddModal(false); setAddForm({ doc_type: 'faqs', title: '', content: '' }); }}
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}

            {/* Document list */}
            {loading ? (
                <div className="flex justify-center" style={{ padding: 60 }}>
                    <div className="loader" />
                </div>
            ) : visibleDocs.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">📄</div>
                    <p>No documents in this category</p>
                    <p className="text-sm text-muted" style={{ marginTop: 4 }}>
                        Click &ldquo;Add Document&rdquo; to create your first one
                    </p>
                </div>
            ) : (
                <div style={{ display: 'grid', gap: 12 }}>
                    {visibleDocs.map((doc) => (
                        <div key={doc.id} className="card" style={{ padding: 20 }}>
                            <div className="flex items-center justify-between" style={{ marginBottom: editingId === doc.id ? 12 : 0 }}>
                                <div>
                                    <span style={{ fontWeight: 600, fontSize: 14 }}>{doc.title}</span>
                                    <span className="text-xs text-muted" style={{ marginLeft: 12 }}>
                                        {doc.content?.length ?? 0} chars · updated {new Date(doc.updated_at).toLocaleDateString()}
                                    </span>
                                </div>
                                <div className="flex items-center gap-sm">
                                    <button
                                        className="btn btn-ghost btn-sm"
                                        onClick={() => {
                                            if (editingId === doc.id) {
                                                setEditingId(null);
                                            } else {
                                                setEditingId(doc.id);
                                                setEditContent(doc.content);
                                            }
                                        }}
                                    >
                                        {editingId === doc.id ? 'Cancel' : 'Edit'}
                                    </button>
                                    <button
                                        className="btn btn-sm"
                                        style={{ background: 'none', color: 'var(--danger)', border: '1px solid var(--danger)', borderRadius: 6, padding: '4px 10px', cursor: 'pointer', fontSize: 12 }}
                                        onClick={() => handleDelete(doc.id)}
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>

                            {editingId === doc.id && (
                                <div style={{ marginTop: 8 }}>
                                    <textarea
                                        value={editContent}
                                        onChange={(e) => setEditContent(e.target.value)}
                                        rows={8}
                                        style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-default)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: 13, resize: 'vertical', boxSizing: 'border-box', fontFamily: 'inherit', marginBottom: 8 }}
                                    />
                                    <button
                                        className="btn btn-primary btn-sm"
                                        onClick={() => handleEdit(doc)}
                                        disabled={editSaving}
                                    >
                                        {editSaving ? 'Saving…' : 'Save Changes'}
                                    </button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
