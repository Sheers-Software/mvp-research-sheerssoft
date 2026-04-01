'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Logo from '@/components/Logo';

export default function PublicNav() {
  const pathname = usePathname();
  const isApply = pathname === '/apply';

  return (
    <nav className="public-nav">
      <div className="public-nav-inner">
        {/* Logo — left */}
        <Link href="/" className="public-nav-logo">
          <Logo size={28} variant="navy" showText />
          <span className="public-nav-byline">by SheersSoft</span>
        </Link>

        {/* Sign Up — right */}
        {!isApply && (
          <Link href="/apply" className="public-nav-signup">
            Sign up
          </Link>
        )}
        {isApply && (
          <Link href="/login" className="public-nav-signin">
            Sign in
          </Link>
        )}
      </div>
    </nav>
  );
}
