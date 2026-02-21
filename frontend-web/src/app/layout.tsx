import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/globals.css';
import { ThemeProvider, NavbarController } from '@/components/layout';
import { ToastProvider } from '@/components/ui';
import { NetworkErrorBanner } from '@/components/common';
import { AuthProvider } from '@/hooks/useAuth';
import { OfflineBanner } from '@/components/offline';
import { register } from '@/lib/offline';

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' });

export const metadata: Metadata = {
  title: 'Soul Sense | AI-Powered Emotional Intelligence Test',
  description:
    'Discover your emotional intelligence with Soul Sense. Get deep insights into your EQ, build better relationships, and unlock your full potential using our AI-powered analysis.',
  keywords: [
    'EQ Test',
    'Emotional Intelligence',
    'AI Assessment',
    'Self-Awareness',
    'Professional Growth',
  ],
  manifest: '/manifest.json',
  themeColor: '#8b5cf6',
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'Soul Sense',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <ToastProvider>
            <AuthProvider>
              <OfflineBanner />
              <NetworkErrorBanner />
              <NavbarController />
              {children}
            </AuthProvider>
          </ToastProvider>
        </ThemeProvider>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if (typeof window !== 'undefined') {
                ${register.toString()}
                register();
              }
            `,
          }}
        />
      </body>
    </html>
  );
}
