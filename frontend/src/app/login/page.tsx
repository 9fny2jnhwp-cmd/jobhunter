"use client";

import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { createClient, isSupabaseConfigured } from "@/lib/supabase/client";

const supabaseEnabled = isSupabaseConfigured();
const devAuth = process.env.NEXT_PUBLIC_DEV_AUTH === "true";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSupabaseAuth() {
    setLoading(true);
    setError(null);
    const supabase = createClient();
    if (!supabase) {
      setError("Supabase is not configured");
      setLoading(false);
      return;
    }

    const fn =
      mode === "signup"
        ? supabase.auth.signUp({ email, password })
        : supabase.auth.signInWithPassword({ email, password });

    const { data, error: authError } = await fn;
    if (authError) {
      setError(authError.message);
      setLoading(false);
      return;
    }

    const session = data.session;
    if (!session?.access_token) {
      setError("Check your email to confirm your account, then sign in.");
      setLoading(false);
      return;
    }

    const res = await signIn("supabase", {
      accessToken: session.access_token,
      email: session.user.email ?? email,
      sub: session.user.id,
      name: session.user.user_metadata?.full_name ?? "",
      redirect: false,
    });

    setLoading(false);
    if (res?.ok) router.push("/dashboard");
    else setError("Failed to establish session");
  }

  async function handleDevLogin() {
    setLoading(true);
    const devEmail = email || process.env.NEXT_PUBLIC_DEV_EMAIL || "dev@jobhunter.local";
    const res = await signIn("dev", { email: devEmail, redirect: false });
    setLoading(false);
    if (res?.ok) router.push("/dashboard");
    else setError("Dev sign-in failed");
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <Card className="border-border/60 bg-card/80 backdrop-blur-xl">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/20">
              <Sparkles className="h-7 w-7 text-primary" />
            </div>
            <CardTitle className="text-2xl">Welcome to JobHunter AI</CardTitle>
            <CardDescription>
              {supabaseEnabled
                ? "Sign in with Supabase or use dev mode locally."
                : "Configure Supabase env vars for production auth."}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {supabaseEnabled && (
              <>
                <div className="flex gap-2">
                  <Button
                    variant={mode === "signin" ? "default" : "outline"}
                    size="sm"
                    className="flex-1"
                    onClick={() => setMode("signin")}
                  >
                    Sign in
                  </Button>
                  <Button
                    variant={mode === "signup" ? "default" : "outline"}
                    size="sm"
                    className="flex-1"
                    onClick={() => setMode("signup")}
                  >
                    Sign up
                  </Button>
                </div>
                <div>
                  <label className="text-sm text-muted-foreground">Email</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
                <div>
                  <label className="text-sm text-muted-foreground">Password</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
                <Button className="w-full" onClick={handleSupabaseAuth} disabled={loading}>
                  {loading ? "Please wait…" : mode === "signup" ? "Create account" : "Sign in with Supabase"}
                </Button>
                {(supabaseEnabled && devAuth) && (
                  <div className="relative py-2">
                    <div className="absolute inset-0 flex items-center">
                      <span className="w-full border-t border-border" />
                    </div>
                    <div className="relative flex justify-center text-xs uppercase">
                      <span className="bg-card px-2 text-muted-foreground">or</span>
                    </div>
                  </div>
                )}
              </>
            )}

            {devAuth && (
              <>
                {!supabaseEnabled && (
                  <div>
                    <label className="text-sm text-muted-foreground">Email (dev)</label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="dev@jobhunter.local"
                      className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                  </div>
                )}
                <Button
                  variant={supabaseEnabled ? "outline" : "default"}
                  className="w-full"
                  onClick={handleDevLogin}
                  disabled={loading}
                >
                  Continue in dev mode
                </Button>
              </>
            )}

            {error && <p className="text-center text-sm text-red-400">{error}</p>}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
