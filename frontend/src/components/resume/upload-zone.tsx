"use client";

import { useCallback, useState } from "react";
import { motion } from "framer-motion";
import { FileUp, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiFetch, type Resume } from "@/lib/api";

export function ResumeUploadZone({
  token,
  onUploaded,
}: {
  token: string;
  onUploaded: (resume: Resume) => void;
}) {
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const upload = useCallback(
    async (file: File) => {
      setLoading(true);
      setError(null);
      const form = new FormData();
      form.append("file", file);
      try {
        const resume = await apiFetch<Resume>("/api/v1/resume/upload", {
          method: "POST",
          body: form,
          token,
        });
        onUploaded(resume);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Upload failed");
      } finally {
        setLoading(false);
      }
    },
    [token, onUploaded]
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) upload(file);
    },
    [upload]
  );

  return (
    <div className="space-y-4">
      <motion.div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        animate={{ scale: dragging ? 1.02 : 1 }}
        className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-12 transition-colors ${
          dragging ? "border-primary bg-primary/5" : "border-border/80 bg-card/40"
        }`}
      >
        {loading ? (
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
        ) : (
          <FileUp className="h-10 w-10 text-muted-foreground" />
        )}
        <p className="mt-4 text-center font-medium">Drop your resume here</p>
        <p className="mt-1 text-sm text-muted-foreground">PDF, DOCX, or TXT — max 10 MB</p>
        <label className="mt-6">
          <input
            type="file"
            className="hidden"
            accept=".pdf,.doc,.docx,.txt,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) upload(file);
            }}
          />
          <Button variant="secondary" disabled={loading} asChild>
            <span>Browse files</span>
          </Button>
        </label>
      </motion.div>
      {error && <p className="text-sm text-red-400">{error}</p>}
    </div>
  );
}
