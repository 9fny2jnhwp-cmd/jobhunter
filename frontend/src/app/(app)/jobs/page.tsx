import { getServerSession } from "next-auth";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";
import { MatchJobsButton } from "@/components/jobs/match-jobs-button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiFetch, type Job } from "@/lib/api";
import { ExternalLink } from "lucide-react";

export default async function JobsPage() {
  const session = await getServerSession(authOptions);
  const token = session?.accessToken ?? "";

  let jobs: Job[] = [];
  try {
    jobs = await apiFetch<Job[]>("/api/v1/jobs/?limit=50", { token });
  } catch {
    // empty
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Job Feed</h1>
          <p className="text-muted-foreground">Remote opportunities matched to your profile.</p>
        </div>
        <MatchJobsButton />
      </div>

      <div className="grid gap-4">
        {jobs.map((job) => (
          <Card key={job.id} className="border-border/60 bg-card/60 transition-colors hover:border-primary/30">
            <CardHeader className="flex flex-row items-start justify-between gap-4">
              <div>
                <CardTitle className="text-lg">{job.title}</CardTitle>
                <p className="text-sm text-muted-foreground">
                  {job.company} · {job.location ?? "Remote"}
                </p>
              </div>
              <div className="flex items-center gap-2">
                {job.remote && <Badge variant="secondary">Remote</Badge>}
                {job.match_score != null && (
                  <Badge variant="success">{job.match_score}%</Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className="flex justify-between">
              <span className="text-xs text-muted-foreground">Source: {job.source ?? "—"}</span>
              {job.url && (
                <a
                  href={job.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
                >
                  View <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </CardContent>
          </Card>
        ))}
        {jobs.length === 0 && (
          <p className="text-muted-foreground">No jobs in feed. Seed the database to preview data.</p>
        )}
      </div>
    </div>
  );
}
