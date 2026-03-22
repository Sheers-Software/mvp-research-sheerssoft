import { createClient, SupabaseClient } from '@supabase/supabase-js';

let _supabase: SupabaseClient | null = null;

/**
 * Lazily creates the Supabase client.
 * This avoids crashing during Next.js static prerendering when
 * NEXT_PUBLIC_SUPABASE_URL is not set at build time.
 */
export function getSupabase(): SupabaseClient {
    if (!_supabase) {
        const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
        const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
        
        if (!supabaseUrl) {
            throw new Error('NEXT_PUBLIC_SUPABASE_URL is not configured');
        }
        
        _supabase = createClient(supabaseUrl, supabaseAnonKey, {
            auth: {
                persistSession: false,
                autoRefreshToken: false,
                detectSessionInUrl: false,
            },
        });
    }
    return _supabase;
}

/** @deprecated Use getSupabase() instead — kept for backward compatibility */
export const supabase = typeof window !== 'undefined'
    ? getSupabase()
    : (null as unknown as SupabaseClient);
