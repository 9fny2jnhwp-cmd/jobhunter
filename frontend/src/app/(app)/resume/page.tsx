"use client";

import { useSession } from "next-auth/react";
import { useCallback, useEffect, useState } from "react";
import { ResumeUploadZone } from "@/components/resume/upload-zone";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiFetch, type Resume } from "@/lib/api";

export default function ResumePage() {
  const { data: session } = useSession();
  const token = session?.accessToken ?? "";
  const [resumes, setResumes] = useState<Resume[]>([]);

  const load = useCallback(async () => {
    if (!token) return;
    try {
      const data = await apiFetch<Resume[]>("/api/v1/resume/", { token });
      setResumes(data);
    } catch {
      setResumes([]);
    }
  }, [token]);

  useEffect(() => {
    load();
  }, [load]);

  const primary = resumes.find((r) => r.is_primary) ?? resumes[0];

  return (
    <div className="mx-auto max-w-3xl space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Resume Builder</h1>
        <p className="text-muted-foreground">
          Upload and parse your resume. Phase 2 adds AI tailoring per job.
        </p>
      </div>

      <ResumeUploadZone token={token} onUploaded={() => load()} />

      {primary && (
        <Card className="border-border/60 bg-card/60">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">{primary.filename}</CardTitle>
              {primary.is_primary && <Badge>Primary</Badge>}
            </div>
            <CardDescription>Parsed profile extracted from your resume</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {primary.parsed_json?.skills && primary.parsed_json.skills.length > 0 && (
              <div>
                <p className="mb-2 text-sm font-medium text-muted-foreground">Skills</p>
                <div className="flex flex-wrap gap-2">
                  {primary.parsed_json.skills.map((s) => (
                    <Badge key={s} variant="secondary">
                      {s}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            {primary.parsed_json?.experience_years != null && (
              <p className="text-sm">
                <span className="text-muted-foreground">Experience: </span>
                {primary.parsed_json.experience_years}+ years
              </p>
            )}
            {primary.parsed_json?.job_titles && primary.parsed_json.job_titles.length > 0 && (
              <p className="text-sm text-muted-foreground">
                Titles detected: {primary.parsed_json.job_titles.join(", ")}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {resumes.length > 1 && (
        <div className="text-sm text-muted-foreground">{resumes.length} resumes on file</div>
      )}
    </div>
  );
}
