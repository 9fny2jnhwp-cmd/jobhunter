"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";
import { ExternalLink, FileText, Loader2, Mail, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  apiFetch,
  type ApplicationPackageResult,
  type CoverLetterResult,
  type Job,
  type TailoredResumeResult,
} from "@/lib/api";

export function JobCard({ job }: { job: Job }) {
  const { data: session } = useSession();
  const token = session?.accessToken ?? "";
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [coverLetter, setCoverLetter] = useState<string | null>(null);
  const [tailored, setTailored] = useState<TailoredResumeResult | null>(null);
  const [expanded, setExpanded] = useState(false);

  async function runAction(
    action: "cover-letter" | "tailor-resume" | "package",
    label: string
  ) {
    if (!token) return;
    setLoading(label);
    setError(null);
    try {
      if (action === "cover-letter") {
        const res = await apiFetch<CoverLetterResult>(
          `/api/v1/ai/cover-letter/${job.id}`,
          { method: "POST", token }
        );
        setCoverLetter(res.cover_letter);
      } else if (action === "tailor-resume") {
        const res = await apiFetch<TailoredResumeResult>(
          `/api/v1/ai/tailor-resume/${job.id}`,
          { method: "POST", token }
        );
        setTailored(res);
      } else {
        const res = await apiFetch<ApplicationPackageResult>(
          `/api/v1/ai/application-package/${job.id}`,
          { method: "POST", token }
        );
        setCoverLetter(res.cover_letter);
        const t = res.tailored_resume as TailoredResumeResult;
        setTailored(t);
      }
      setExpanded(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(null);
    }
  }

  return (
    <Card className="border-border/60 bg-card/60 transition-colors hover:border-primary/30">
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          <CardTitle className="text-lg">{job.title}</CardTitle>
          <p className="text-sm text-muted-foreground">
            {job.company} · {job.location ?? "Remote"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {job.remote && <Badge variant="secondary">Remote</Badge>}
          {job.match_score != null && <Badge variant="success">{job.match_score}%</Badge>}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-2">
          <Button
            size="sm"
            variant="outline"
            disabled={!!loading}
            onClick={() => runAction("cover-letter", "letter")}
            className="gap-1"
          >
            {loading === "letter" ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              <Mail className="h-3 w-3" />
            )}
            Cover letter
          </Button>
          <Button
            size="sm"
            variant="outline"
            disabled={!!loading}
            onClick={() => runAction("tailor-resume", "resume")}
            className="gap-1"
          >
            {loading === "resume" ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              <FileText className="h-3 w-3" />
            )}
            Tailor resume
          </Button>
          <Button
            size="sm"
            disabled={!!loading}
            onClick={() => runAction("package", "package")}
            className="gap-1"
          >
            {loading === "package" ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              <Sparkles className="h-3 w-3" />
            )}
            Full package
          </Button>
          {job.url && (
            <a
              href={job.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 rounded-md border border-input px-3 py-1.5 text-sm hover:bg-accent"
            >
              View <ExternalLink className="h-3 w-3" />
            </a>
          )}
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}

        {expanded && (coverLetter || tailored) && (
          <div className="space-y-3 rounded-lg border border-border/50 bg-background/50 p-4 text-sm">
            {coverLetter && (
              <div>
                <p className="mb-2 font-medium text-primary">Cover letter</p>
                <p className="whitespace-pre-wrap text-muted-foreground">{coverLetter}</p>
              </div>
            )}
            {tailored && (
              <div>
                <p className="mb-2 font-medium text-primary">Tailored summary</p>
                <p className="text-muted-foreground">{tailored.tailored_summary}</p>
                {tailored.bullet_highlights?.length > 0 && (
                  <ul className="mt-2 list-disc pl-5 text-muted-foreground">
                    {tailored.bullet_highlights.map((b, i) => (
                      <li key={i}>{b}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
