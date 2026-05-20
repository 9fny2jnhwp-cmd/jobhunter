"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiFetch, type MatchAllResponse } from "@/lib/api";

export function MatchJobsButton() {
  const { data: session } = useSession();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function runMatch() {
    const token = session?.accessToken;
    if (!token) return;

    setLoading(true);
    setMessage(null);
    try {
      const result = await apiFetch<MatchAllResponse>(
        "/api/v1/ai/match-all?use_llm=true",
        { method: "POST", token }
      );
      setMessage(`Matched ${result.matched} jobs with AI scoring.`);
      router.refresh();
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Matching failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-end gap-2">
      <Button onClick={runMatch} disabled={loading} className="gap-2">
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Sparkles className="h-4 w-4" />
        )}
        {loading ? "Scoring…" : "AI Match All Jobs"}
      </Button>
      {message && <p className="text-xs text-muted-foreground">{message}</p>}
    </div>
  );
}
