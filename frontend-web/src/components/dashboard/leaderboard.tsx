import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'; // Assuming avatar exists
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function Leaderboard({ contributors }: { contributors: any[] }) {
  return (
    <Card className="col-span-3 backdrop-blur-md bg-opacity-50 dark:bg-black/40 border-white/10">
      <CardHeader>
        <CardTitle>Top Contributors</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-8">
          {contributors.map((contributor, index) => (
            <div key={contributor.login} className="flex items-center">
              <Avatar className="h-9 w-9">
                <AvatarImage src={contributor.avatar_url} alt={contributor.login} />
                <AvatarFallback>{contributor.login[0]}</AvatarFallback>
              </Avatar>
              <div className="ml-4 space-y-1">
                <p className="text-sm font-medium leading-none">{contributor.login}</p>
                <a
                  href={contributor.html_url}
                  target="_blank"
                  className="text-xs text-muted-foreground hover:text-blue-400"
                >
                  @{contributor.login}
                </a>
              </div>
              <div className="ml-auto font-medium text-sm text-muted-foreground">
                {contributor.contributions} commits
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
