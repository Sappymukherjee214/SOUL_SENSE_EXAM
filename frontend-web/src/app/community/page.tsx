'use client';

import { useEffect, useState } from 'react';
import { BentoGrid, BentoGridItem } from '@/components/dashboard/bento-grid';
import { StatsCard } from '@/components/dashboard/stats-card';
import { ActivityAreaChart } from '@/components/dashboard/charts/activity-area-chart';
import { ContributionMixChart } from '@/components/dashboard/charts/contribution-mix';
import { DashboardSkeleton } from '@/components/dashboard/skeleton-loader';
import { Leaderboard } from '@/components/dashboard/leaderboard';
import { ContributionHeatmap } from '@/components/dashboard/heatmap';
import { Users, GitMerge, Star, GitCommit } from 'lucide-react';

export default function CommunityDashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsRes, contributorsRes, activityRes] = await Promise.all([
          fetch('/api/community/stats'),
          fetch('/api/community/contributors?limit=5'),
          fetch('/api/community/activity'),
        ]);

        if (!statsRes.ok || !contributorsRes.ok || !activityRes.ok) {
          throw new Error('Failed to fetch community data');
        }

        const stats = await statsRes.json();
        const contributors = await contributorsRes.json();
        const activity = await activityRes.json();

        setData({ stats, contributors, activity });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-8">
        <div className="max-w-7xl mx-auto space-y-8">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
            Community Pulse
          </h1>
          <DashboardSkeleton />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-500">Something went wrong</h2>
          <p className="text-slate-600 dark:text-slate-400 mt-2">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-6 md:p-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">
              Community Pulse
            </h1>
            <p className="text-slate-600 dark:text-slate-400 mt-2 text-lg">
              Real-time insights into the SoulSense open source ecosystem.
            </p>
          </div>
          <a
            href="https://github.com/Rohanrathod7/SOUL_SENSE_EXAM/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22"
            target="_blank"
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold rounded-full shadow-lg hover:shadow-cyan-500/50 transition-all transform hover:-translate-y-1"
          >
            Contribute Now ✨
          </a>
        </div>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Primary Stats */}
          <StatsCard
            title="Contributors"
            value={data.stats.repository.watchers}
            icon={Users}
            description="Active developers"
          />
          <StatsCard
            title="Stars"
            value={data.stats.repository.stars}
            icon={Star}
            description="Project gazers"
          />
          <StatsCard
            title="Total PRs"
            value={data.stats.pull_requests.total}
            icon={GitMerge}
            description={`${data.stats.pull_requests.open} open`}
          />
          <StatsCard
            title="Total Commits"
            value={data.activity.reduce((acc: number, w: any) => acc + w.total, 0)}
            icon={GitCommit}
            description="Last 52 weeks"
          />

          {/* Charts */}
          <ActivityAreaChart data={data.activity} />
          <ContributionHeatmap />
          <ContributionMixChart />
          <Leaderboard contributors={data.contributors} />
        </div>
      </div>
    </div>
  );
}
