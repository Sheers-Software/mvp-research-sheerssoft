import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from '@/lib/auth';

export const metadata: Metadata = {
  title: "Nocturn AI — Hotel Concierge Intelligence",
  description: "AI-powered hotel inquiry capture and conversion engine by SheersSoft",
  icons: { icon: '/favicon.ico' },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
