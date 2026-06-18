'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useTenant } from '@/lib/tenant-context';

export default function PortalKBIndexPage() {
    const { businesses, loading } = useTenant();
    const router = useRouter();

    useEffect(() => {
        if (!loading) {
            if (businesses.length > 0) {
                router.replace(`/portal/kb/${businesses[0].id}`);
            }
        }
    }, [businesses, loading, router]);

    return (
        <div className="flex justify-center" style={{ padding: 80 }}>
            <div className="loader" />
        </div>
    );
}
