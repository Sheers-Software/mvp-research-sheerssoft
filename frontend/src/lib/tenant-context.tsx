'use client';
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiGet } from './api';

interface PropertySummary {
  id: string;
  name: string;
  slug: string;
  is_active: boolean;
  weekly_inquiries: number;
  weekly_leads: number;
  weekly_revenue_rm: number;
  onboarding_score: number;
  channel_statuses: { whatsapp: string; email: string; website: string };
}

interface TenantContextValue {
  tenantId: string | null;
  tenantName: string | null;
  tenantTier: string | null;
  properties: PropertySummary[];
  loading: boolean;
  refresh: () => void;
}

const TenantContext = createContext<TenantContextValue>({
  tenantId: null, tenantName: null, tenantTier: null, properties: [], loading: true, refresh: () => {}
});

interface PortalHomeData {
  tenant?: { id: string; name: string; subscription_tier: string };
  properties?: PropertySummary[];
}

export function TenantProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<PortalHomeData | null>(null);
  const [loading, setLoading] = useState(true);

  const load = () => {
    apiGet<PortalHomeData>('/portal/home')
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []); // load is stable — defined at module scope within component, runs once on mount

  return (
    <TenantContext.Provider value={{
      tenantId: data?.tenant?.id ?? null,
      tenantName: data?.tenant?.name ?? null,
      tenantTier: data?.tenant?.subscription_tier ?? null,
      properties: data?.properties ?? [],
      loading,
      refresh: load,
    }}>
      {children}
    </TenantContext.Provider>
  );
}

export const useTenant = () => useContext(TenantContext);
