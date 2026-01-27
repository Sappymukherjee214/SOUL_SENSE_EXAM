import { Skeleton } from '@/components/ui/skeleton'; // Assuming standard shadcn skeleton exists, if not I'll just use divs

export function DashboardSkeleton() {
  return (
    <div className="flex flex-col space-y-6 animate-pulse">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-32 rounded-xl bg-muted/50" />
        ))}
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <div className="col-span-4 h-[300px] rounded-xl bg-muted/50" />
        <div className="col-span-3 h-[300px] rounded-xl bg-muted/50" />
      </div>
    </div>
  );
}
