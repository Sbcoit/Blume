/* ExecutionsPage
 * Client component to allow navigation handlers to be passed into ActivityList.
 */
"use client";

import { useRouter } from "next/navigation";
import ActivityList from "@/components/ActivityList";
import { mockExecutions } from "@/lib/mockData";

export default function ExecutionsPage() {
  const router = useRouter();
  const executions = mockExecutions;

  return (
    <div className="space-y-6">
      <header className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Workflow Executions
          </h1>
          <p className="mt-1 text-sm text-text-muted">
            Every run of your agent workflows, from first decision to final calendar invite.
          </p>
        </div>
        <div className="flex gap-2 text-xs text-text-muted">
          <span className="rounded-full border border-border px-3 py-1">
            Status: Any
          </span>
          <span className="rounded-full border border-border px-3 py-1">
            Agent: All
          </span>
        </div>
      </header>

      <ActivityList
        executions={executions}
        isLoading={false}
        onSelectExecution={(id) => {
          router.push(`/executions/${id}`);
        }}
      />
    </div>
  );
}



