"use client";

import { motion } from "framer-motion";
import { FileText, Send, Target, Users } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DashboardStats } from "@/lib/api";

const cards = [
  {
    key: "total_applications" as const,
    label: "Total Applications",
    icon: Send,
    format: (v: number) => String(v),
  },
  {
    key: "applied_this_week" as const,
    label: "Applied This Week",
    icon: Target,
    format: (v: number) => String(v),
  },
  {
    key: "interviews" as const,
    label: "Interviews",
    icon: Users,
    format: (v: number) => String(v),
  },
  {
    key: "avg_match_score" as const,
    label: "Avg Match Score",
    icon: FileText,
    format: (v: number | null) => (v != null ? `${Math.round(v)}%` : "—"),
  },
];

export function StatsCards({ stats }: { stats: DashboardStats }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map(({ key, label, icon: Icon, format }, i) => (
        <motion.div
          key={key}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.08 }}
        >
          <Card className="border-border/60 bg-card/60 backdrop-blur">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{label}</CardTitle>
              <Icon className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold tracking-tight">
                {key === "avg_match_score"
                  ? format(stats.avg_match_score)
                  : format(stats[key] as number)}
              </p>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
