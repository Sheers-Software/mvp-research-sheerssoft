'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function PublicNav() {
  const pathname = usePathname();
  const isApply = pathname === '/apply';

  return (
    <nav className="public-nav">
      <div className="public-nav-inner">
        {/* Logo — left */}
        <Link href="/" className="public-nav-logo">
          <svg
            viewBox="0 0 120 28"
            height="22"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-label="Nocturn AI"
          >
            {/* Wordmark: NOCTURN in dark, AI in accent blue */}
            <text
              x="0" y="21"
              fontFamily="'Inter', -apple-system, sans-serif"
              fontWeight="800"
              fontSize="20"
              letterSpacing="-0.5"
              fill="#0f172a"
            >NOCTURN</text>
            <text
              x="84" y="21"
              fontFamily="'Inter', -apple-system, sans-serif"
              fontWeight="800"
              fontSize="20"
              letterSpacing="-0.5"
              fill="#2563eb"
            > AI</text>
          </svg>
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
