"use client";

import { JobCard } from "@/components/jobs/job-card";
import type { Job } from "@/lib/api";

export function JobFeed({ jobs }: { jobs: Job[] }) {
  if (jobs.length === 0) {
    return (
      <p className="text-muted-foreground">No jobs in feed. Seed the database to preview data.</p>
    );
  }
  return (
    <div className="grid gap-4">
      {jobs.map((job) => (
        <JobCard key={job.id} job={job} />
      ))}
    </div>
  );
}
