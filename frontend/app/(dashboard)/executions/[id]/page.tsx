/* ExecutionDetailPage
 * Shows step-by-step progress for a single workflow execution.
 * Users can approve steps that require confirmation.
 */
"use client";

import { notFound, useRouter } from "next/navigation";
import ExecutionDetail from "@/components/ExecutionDetail";
import { mockExecutions } from "@/lib/mockData";
import { confirmWorkflowStep } from "@/services/workflowService";
import Button from "@/components/UI/Button";

interface Props {
  params: { id: string };
}

export default function ExecutionDetailPage({ params }: Props) {
  const router = useRouter();
  const execution = mockExecutions.find((e) => e.id === params.id);

  if (!execution) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <header className="flex items-end justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">
            {execution.name}
          </h1>
          <p className="text-sm text-text-muted">
            Agent: {execution.agentName} · Run ID: {execution.id}
          </p>
        </div>
        <div className="text-right text-xs text-text-muted">
          <div>Started: {execution.startedAt.toLocaleString()}</div>
          {execution.completedAt && (
            <div>Completed: {execution.completedAt.toLocaleString()}</div>
          )}
        </div>
      </header>

      <ExecutionDetail
        execution={execution}
        onConfirmStep={async (stepId) => {
          await confirmWorkflowStep(execution.id, stepId);
        }}
      />

      <div className="pt-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/executions")}
          className="text-xs"
        >
          ← Back to executions
        </Button>
      </div>
    </div>
  );
}


