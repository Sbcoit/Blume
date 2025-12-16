/* Login page
 * Simple, clean entry point. Assumes backend auth exists; here we just fake success
 * and route to the console.
 */
"use client";

import { FormEvent } from "react";
import { useRouter } from "next/navigation";
import Button from "@/components/UI/Button";

export default function HomePage() {
  const router = useRouter();

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    // TODO: wire real authentication here later.
    // For now, pressing "Continue" just routes straight to the console.
    router.push("/console");
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-sm rounded-2xl border border-border/40 bg-background/30 p-6 shadow-elevated backdrop-blur-2xl page-enter">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-2xl bg-accent text-black shadow-elevated">
            <span className="text-sm font-semibold">AO</span>
          </div>
          <h1 className="text-lg font-semibold tracking-tight">
            Sign in to your agent
          </h1>
          <p className="mt-1 text-xs text-text-muted">
            Minimal console to wire your phone number and tools.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-sm">
          <div className="space-y-1">
            <label className="text-xs text-text-muted">Email</label>
            <input
              type="email"
              // Left as uncontrolled for now; hook into real auth later.
              className="w-full rounded-lg border border-border/70 bg-background px-3 py-2 text-sm text-text-main outline-none ring-0 focus:border-accent"
              placeholder="you@company.com"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-text-muted">Password</label>
            <input
              type="password"
              // Left as uncontrolled for now; hook into real auth later.
              className="w-full rounded-lg border border-border/70 bg-background px-3 py-2 text-sm text-text-main outline-none ring-0 focus:border-accent"
              placeholder="••••••••"
            />
          </div>
          <Button
            type="submit"
            variant="primary"
            size="md"
            className="w-full mt-2"
          >
            Continue
          </Button>
        </form>
      </div>
    </div>
  );
}




