import { getServerSession } from "next-auth";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";

interface Application {
  id: string;
  job_id: string;
  status: string;
  applied_at: string | null;
  created_at: string;
}

export default async function ApplicationsPage() {
  const session = await getServerSession(authOptions);
  const token = session?.accessToken ?? "";

  let apps: Application[] = [];
  try {
    apps = await apiFetch<Application[]>("/api/v1/applications/", { token });
  } catch {
    // empty
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Applications</h1>
        <p className="text-muted-foreground">Track draft, applied, and interview stages.</p>
      </div>

      <div className="grid gap-3">
        {apps.map((app) => (
          <Card key={app.id} className="border-border/60 bg-card/60">
            <CardHeader className="flex flex-row items-center justify-between py-4">
              <CardTitle className="text-base font-medium">Application {app.id.slice(0, 8)}…</CardTitle>
              <Badge variant={app.status === "applied" ? "success" : "secondary"}>
                {app.status}
              </Badge>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              {app.applied_at
                ? `Applied ${new Date(app.applied_at).toLocaleDateString()}`
                : `Created ${new Date(app.created_at).toLocaleDateString()}`}
            </CardContent>
          </Card>
        ))}
        {apps.length === 0 && (
          <p className="text-muted-foreground">No applications yet.</p>
        )}
      </div>
    </div>
  );
}
