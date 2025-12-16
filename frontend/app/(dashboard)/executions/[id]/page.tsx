import { notFound } from "next/navigation";
import ExecutionDetail from "@/components/ExecutionDetail";
import { mockExecutions } from "@/lib/mockData";
import { confirmWorkflowStep } from "@/services/workflowService";

interface Props {
  params: { id: string };
}

export default function ExecutionDetailPage({ params }: Props) {
  const execution = mockExecutions.find((e) => e.id === params.id);

  if (!execution) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-text-muted">
            Execution
          </p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight">
            {execution?.name}
          </h1>
          <p className="mt-1 text-sm text-text-muted">
            Agent: {execution?.agentName} · Run ID: {execution?.id}
          </p>
        </div>
        {execution && (
          <div className="text-right text-xs text-text-muted">
            <div>Started: {execution.startedAt.toLocaleString()}</div>
            {execution.completedAt && (
              <div>Completed: {execution.completedAt.toLocaleString()}</div>
            )}
          </div>
        )}
      </header>

      {execution && (
        <ExecutionDetail
          execution={execution}
          onConfirmStep={async (stepId) => {
            await confirmWorkflowStep(execution.id, stepId);
          }}
        />
      )}
    </div>
  );
}


