import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { format, parseISO } from 'date-fns';

export function ActivityAreaChart({ data }: { data: any[] }) {
  // Transform GitHub commit activity (weeks) to chart format
  // Data expected: [{ total: int, week: timestamp, days: [] }]
  const chartData = data
    .map((week) => ({
      date: new Date(week.week * 1000).toISOString().split('T')[0],
      commits: week.total,
    }))
    .filter((d) => d.commits > 0); // Optional filter

  return (
    <Card className="col-span-full lg:col-span-4 backdrop-blur-md bg-opacity-50 dark:bg-black/40 border-white/10">
      <CardHeader>
        <CardTitle>Commit Velocity</CardTitle>
        <CardDescription>Commits per week over the last year</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[200px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorCommits" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.1} />
              <XAxis
                dataKey="date"
                tickFormatter={(str) => format(parseISO(str), 'MMM d')}
                stroke="#888888"
                fontSize={12}
              />
              <YAxis stroke="#888888" fontSize={12} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151' }}
                itemStyle={{ color: '#e5e7eb' }}
                labelStyle={{ color: '#9ca3af' }}
              />
              <Area
                type="monotone"
                dataKey="commits"
                stroke="#8B5CF6"
                fillOpacity={1}
                fill="url(#colorCommits)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
