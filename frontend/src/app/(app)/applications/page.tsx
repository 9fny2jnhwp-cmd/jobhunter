import { getServerSession } from "next-auth";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiFetch, type ApplicationDetail } from "@/lib/api";

export default async function ApplicationsPage() {
  const session = await getServerSession(authOptions);
  const token = session?.accessToken ?? "";

  let apps: ApplicationDetail[] = [];
  try {
    apps = await apiFetch<ApplicationDetail[]>("/api/v1/applications/", { token });
  } catch {
    // empty
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Applications</h1>
        <p className="text-muted-foreground">
          Drafts with AI-generated cover letters and tailored resume content.
        </p>
      </div>

      <div className="grid gap-4">
        {apps.map((app) => (
          <Card key={app.id} className="border-border/60 bg-card/60">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg">{app.job_title}</CardTitle>
                <p className="text-sm text-muted-foreground">{app.company}</p>
              </div>
              <Badge variant={app.status === "applied" ? "success" : "secondary"}>
                {app.status}
              </Badge>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              {app.cover_letter && (
                <div>
                  <p className="font-medium text-primary">Cover letter</p>
                  <p className="mt-1 line-clamp-4 whitespace-pre-wrap text-muted-foreground">
                    {app.cover_letter}
                  </p>
                </div>
              )}
              {app.tailored_resume?.tailored_summary && (
                <div>
                  <p className="font-medium text-primary">Tailored summary</p>
                  <p className="mt-1 text-muted-foreground">
                    {String(app.tailored_resume.tailored_summary)}
                  </p>
                </div>
              )}
              {!app.cover_letter && !app.tailored_resume && (
                <p className="text-muted-foreground">No generated content yet.</p>
              )}
            </CardContent>
          </Card>
        ))}
        {apps.length === 0 && (
          <p className="text-muted-foreground">
            No applications yet. Use Job Feed to generate a cover letter or full package.
          </p>
        )}
      </div>
    </div>
  );
}
