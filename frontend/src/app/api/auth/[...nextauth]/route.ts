import NextAuth, { type NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { apiFetch, type User } from "@/lib/api";

const devEmail = process.env.NEXT_PUBLIC_DEV_EMAIL ?? "dev@jobhunter.local";

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      id: "dev",
      name: "Development",
      credentials: {
        email: { label: "Email", type: "email" },
      },
      async authorize(credentials) {
        const email = credentials?.email ?? devEmail;
        const token = `dev:${email}`;

        try {
          await apiFetch<User>("/api/v1/auth/register", {
            method: "POST",
            body: JSON.stringify({
              email,
              full_name: "Dev User",
              supabase_id: `dev-${email}`,
            }),
          });
        } catch {
          // User may already exist
        }

        await apiFetch<User>("/api/v1/auth/sync", { method: "POST", token });
        const user = await apiFetch<User>("/api/v1/auth/me", { token });
        return {
          id: user.id,
          email: user.email,
          name: user.full_name,
          accessToken: token,
        };
      },
    }),
    CredentialsProvider({
      id: "supabase",
      name: "Supabase",
      credentials: {
        accessToken: { label: "Access Token", type: "text" },
        email: { label: "Email", type: "email" },
        sub: { label: "Sub", type: "text" },
        name: { label: "Name", type: "text" },
      },
      async authorize(credentials) {
        const accessToken = credentials?.accessToken;
        if (!accessToken) return null;

        await apiFetch<User>("/api/v1/auth/sync", {
          method: "POST",
          token: accessToken,
        });
        const user = await apiFetch<User>("/api/v1/auth/me", { token: accessToken });

        return {
          id: user.id,
          email: user.email,
          name: user.full_name ?? credentials?.name,
          accessToken,
        };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = (user as { accessToken?: string }).accessToken;
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string;
      return session;
    },
  },
  pages: { signIn: "/login" },
  session: { strategy: "jwt" },
  secret: process.env.NEXTAUTH_SECRET,
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
