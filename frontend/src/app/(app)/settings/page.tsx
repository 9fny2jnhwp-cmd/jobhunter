export default function SettingsPage() {
  const supabase = Boolean(
    process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  );

  return (
    <div className="max-w-2xl space-y-6 animate-fade-in">
      <h1 className="text-3xl font-bold tracking-tight">Settings</h1>

      <section className="rounded-lg border border-border/60 bg-card/60 p-6 space-y-3">
        <h2 className="font-semibold">Authentication</h2>
        <p className="text-sm text-muted-foreground">
          Supabase: {supabase ? "configured" : "not configured — set NEXT_PUBLIC_SUPABASE_URL and anon key"}
        </p>
        <ul className="list-disc pl-5 text-sm text-muted-foreground space-y-1">
          <li>Backend validates JWT via SUPABASE_JWT_SECRET in root .env</li>
          <li>OAuth redirect: /auth/callback</li>
          <li>Dev mode: NEXT_PUBLIC_DEV_AUTH=true</li>
        </ul>
      </section>

      <section className="rounded-lg border border-border/60 bg-card/60 p-6 space-y-3">
        <h2 className="font-semibold">AI matching</h2>
        <p className="text-sm text-muted-foreground">
          Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env for LLM-powered LangGraph scoring.
          Without keys, heuristic matching is used.
        </p>
      </section>
    </div>
  );
}
