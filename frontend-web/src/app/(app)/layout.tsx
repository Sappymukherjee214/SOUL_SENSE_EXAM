'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
// Requirement: Use the existing auth context/hook
import { useAuth } from '@/hooks/useAuth';
import { Sidebar } from '@/components/app';

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Requirement: Check authentication status
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Requirement: Redirect to /login if user is not authenticated
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  // Requirement: Include a loading state while auth check is in progress
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50 dark:bg-gray-900">
        <div className="w-12 h-12 border-4 border-blue-200 rounded-full animate-spin border-t-blue-600"></div>
      </div>
    );
  }

  // Double check: If not authenticated, return null (the redirect above handles the move)
  if (!isAuthenticated) {
    return null;
  }

  // Requirement: Wrap children with sidebar and header components
  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* Sidebar Component */}
      <Sidebar />

      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        
        {/* Header */}
        <header className="flex items-center justify-between border-b bg-background px-6 py-4 h-16">
          <h1 className="text-xl font-semibold">Dashboard</h1>
          <div className="h-8 w-8 rounded-full bg-muted"></div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-4 md:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}