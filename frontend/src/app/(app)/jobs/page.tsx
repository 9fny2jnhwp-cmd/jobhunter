import { getServerSession } from "next-auth";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";
import { JobFeed } from "@/components/jobs/job-feed";
import { MatchJobsButton } from "@/components/jobs/match-jobs-button";
import { apiFetch, type Job } from "@/lib/api";

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
          <p className="text-muted-foreground">
            Generate cover letters and tailored resumes per role.
          </p>
        </div>
        <MatchJobsButton />
      </div>
      <JobFeed jobs={jobs} />
    </div>
  );
}
