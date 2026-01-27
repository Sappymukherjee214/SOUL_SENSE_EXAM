import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const data = [
  { name: 'Code', value: 400, color: '#3B82F6' },
  { name: 'Docs', value: 300, color: '#10B981' },
  { name: 'Issues', value: 300, color: '#F59E0B' },
  { name: 'Reviews', value: 200, color: '#8B5CF6' },
];

export function ContributionMixChart() {
  return (
    <Card className="col-span-full md:col-span-1 lg:col-span-3 backdrop-blur-md bg-opacity-50 dark:bg-black/40 border-white/10">
      <CardHeader>
        <CardTitle>Contribution Mix</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[200px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151' }}
                itemStyle={{ color: '#e5e7eb' }}
              />
              <Legend verticalAlign="middle" align="right" layout="vertical" />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
