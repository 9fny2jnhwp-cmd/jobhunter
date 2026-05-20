import { getServerSession } from "next-auth";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";
import { StatsCards } from "@/components/dashboard/stats-cards";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiFetch, type DashboardStats, type Job } from "@/lib/api";

export default async function DashboardPage() {
  const session = await getServerSession(authOptions);
  const token = session?.accessToken ?? "";

  let stats: DashboardStats = {
    total_applications: 0,
    applied_this_week: 0,
    interviews: 0,
    avg_match_score: null,
    resumes_uploaded: 0,
  };
  let jobs: Job[] = [];

  try {
    [stats, jobs] = await Promise.all([
      apiFetch<DashboardStats>("/api/v1/dashboard/stats", { token }),
      apiFetch<Job[]>("/api/v1/jobs/?limit=5", { token }),
    ]);
  } catch {
    // API may be offline during first setup
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Track applications, match scores, and resume status at a glance.
        </p>
      </div>

      <StatsCards stats={stats} />

      <Card className="border-border/60 bg-card/60">
        <CardHeader>
          <CardTitle>Top Matches</CardTitle>
          <CardDescription>Remote roles ranked by AI match score</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {jobs.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No jobs yet. Run <code className="text-primary">python -m scripts.seed</code> on the
              backend.
            </p>
          ) : (
            jobs.map((job) => (
              <div
                key={job.id}
                className="flex items-center justify-between rounded-lg border border-border/50 bg-background/50 px-4 py-3"
              >
                <div>
                  <p className="font-medium">{job.title}</p>
                  <p className="text-sm text-muted-foreground">
                    {job.company} · {job.location ?? "Remote"}
                  </p>
                </div>
                {job.match_score != null && (
                  <Badge variant="success">{job.match_score}% match</Badge>
                )}
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
