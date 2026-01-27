import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

export function ContributionHeatmap() {
  // Simulated data for demo (fetching real full year heatmap is heavy without GraphQL)
  const generateData = () => {
    return Array.from({ length: 52 * 7 }, (_, i) => ({
      date: new Date(Date.now() - (365 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      count: Math.random() > 0.7 ? Math.floor(Math.random() * 5) : 0,
    }));
  };

  const data = generateData();

  const getColor = (count: number) => {
    if (count === 0) return 'bg-neutral-100 dark:bg-neutral-900';
    if (count <= 1) return 'bg-blue-200 dark:bg-blue-900';
    if (count <= 3) return 'bg-blue-400 dark:bg-blue-700';
    return 'bg-blue-600 dark:bg-blue-500';
  };

  return (
    <Card className="col-span-full lg:col-span-4 backdrop-blur-md bg-opacity-50 dark:bg-black/40 border-white/10">
      <CardHeader>
        <CardTitle>Contribution Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-1 justify-center">
          {data.map((day, i) => (
            <TooltipProvider key={i}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <div
                    className={`w-3 h-3 rounded-sm ${getColor(day.count)} cursor-pointer transition-colors duration-200 hover:ring-2 ring-white/20`}
                  />
                </TooltipTrigger>
                <TooltipContent>
                  <p className="text-xs">
                    {day.count} contributions on {day.date}
                  </p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
