'use client';

/**
 * API client for Nocturn AI backend.
 *
 * Uses relative URLs (/api/v1/...) so all requests go through the Next.js
 * server-side rewrite proxy (next.config.ts → NEXT_PUBLIC_API_URL).
 * This avoids CORS entirely — requests are same-origin from the browser's perspective.
 *
 * NEXT_PUBLIC_API_URL is still used for direct window.open links (e.g. CSV export).
 */
export const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function api<T = any>(
    path: string,
    options: RequestInit = {},
): Promise<T> {
    const token = typeof window !== 'undefined' ? localStorage.getItem('nocturn_token') : null;

    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string> || {}),
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const res = await fetch(`/api/v1${path}`, {
        ...options,
        headers,
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || 'API request failed');
    }

    return res.json();
}

export const apiGet = <T = any>(path: string) => api<T>(path, { method: 'GET' });
export const apiPost = <T = any>(path: string, body?: any) =>
    api<T>(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined });
export const apiPatch = <T = any>(path: string, body?: any) =>
    api<T>(path, { method: 'PATCH', body: body ? JSON.stringify(body) : undefined });
export const apiPut = <T = any>(path: string, body?: any) =>
    api<T>(path, { method: 'PUT', body: body ? JSON.stringify(body) : undefined });
