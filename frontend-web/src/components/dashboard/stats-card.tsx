import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon: LucideIcon;
  className?: string;
  trend?: 'up' | 'down' | 'neutral';
}

export function StatsCard({
  title,
  value,
  description,
  icon: Icon,
  className,
  trend,
}: StatsCardProps) {
  return (
    <Card
      className={cn(
        'backdrop-blur-md bg-opacity-50 dark:bg-black/40 border-white/10 hover:border-blue-500/50 transition-colors',
        className
      )}
    >
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground group-hover:text-blue-500 transition-colors" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-foreground">{value}</div>
        {description && <p className="text-xs text-muted-foreground mt-1">{description}</p>}
      </CardContent>
    </Card>
  );
}
