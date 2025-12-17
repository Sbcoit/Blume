/* ExecutionsPage
 * Shows all agent workflow executions (when your agent ran tasks, scheduled meetings, etc.)
 * Click any execution to see step-by-step details.
 */
"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import ActivityList from "@/components/ActivityList";
import { mockExecutions } from "@/lib/mockData";
import Button from "@/components/UI/Button";

export default function ExecutionsPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");

  const filteredExecutions = useMemo(() => {
    if (!searchQuery.trim()) return mockExecutions;

    const query = searchQuery.toLowerCase();
    return mockExecutions.filter(
      (exec) =>
        exec.name.toLowerCase().includes(query) ||
        exec.agentName.toLowerCase().includes(query) ||
        exec.status.toLowerCase().includes(query) ||
        exec.id.toLowerCase().includes(query)
    );
  }, [searchQuery]);

  return (
    <div className="space-y-6">
      <header className="flex items-end justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">
            Workflow Executions
          </h1>
          <p className="text-sm text-text-muted">
            Every run of your agent workflows, from first decision to final calendar invite.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push("/console")}
            className="text-xs"
          >
            Console
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push("/")}
            className="text-xs"
          >
            Log out
          </Button>
        </div>
      </header>

      <div className="space-y-4">
        <div className="relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by name, agent, status, or ID..."
            className="w-full rounded-lg border border-border/40 bg-background/25 px-4 py-2.5 pl-10 text-sm text-text-main placeholder:text-text-muted/60 outline-none ring-0 focus:border-accent/70 backdrop-blur-xl"
          />
          <svg
            className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted/60"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted/60 hover:text-text-main transition"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {filteredExecutions.length === 0 ? (
          <div className="rounded-2xl border border-border/40 bg-background/25 p-8 text-center backdrop-blur-xl">
            <p className="text-sm text-text-muted">
              No executions found matching &quot;{searchQuery}&quot;
            </p>
          </div>
        ) : (
          <ActivityList
            executions={filteredExecutions}
            isLoading={false}
            onSelectExecution={(id) => {
              router.push(`/executions/${id}`);
            }}
          />
        )}
      </div>
    </div>
  );
}



