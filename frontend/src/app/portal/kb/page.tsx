'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useTenant } from '@/lib/tenant-context';

export default function PortalKBIndexPage() {
    const { properties, loading } = useTenant();
    const router = useRouter();

    useEffect(() => {
        if (!loading) {
            if (properties.length > 0) {
                router.replace(`/portal/kb/${properties[0].id}`);
            }
        }
    }, [properties, loading, router]);

    return (
        <div className="flex justify-center" style={{ padding: 80 }}>
            <div className="loader" />
        </div>
    );
}
