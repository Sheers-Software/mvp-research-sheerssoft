import type { Metadata } from "next";
import { Instrument_Serif } from "next/font/google";
import "./globals.css";
import { AuthProvider } from '@/lib/auth';

const instrumentSerif = Instrument_Serif({
  weight: ["400"],
  subsets: ["latin"],
  variable: "--font-instrument-serif",
  display: "swap",
});

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
    <html lang="en" className={instrumentSerif.variable}>
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
