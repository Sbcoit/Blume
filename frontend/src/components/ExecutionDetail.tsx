/* ExecutionDetail
 * Detail view for a single workflow execution.
 * Renders a vertical timeline of steps and a sidebar with context.
 */
"use client";

import { WorkflowExecution, WorkflowStep } from "@/types/workflow";
import Badge from "@/components/UI/Badge";
import StatusDot from "@/components/UI/StatusDot";
import ConfirmationToggle from "@/components/ConfirmationToggle";

interface ExecutionDetailProps {
  execution: WorkflowExecution;
  onConfirmStep?: (stepId: string) => Promise<void>;
}

export default function ExecutionDetail({
  execution,
  onConfirmStep
}: ExecutionDetailProps) {
  return (
    <section className="grid gap-8 md:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
      <div className="space-y-5">
        <header className="flex items-center gap-3 text-xs text-text-muted">
          <Badge intent={statusToIntent(execution.status)}>
            <StatusDot status={statusToDot(execution.status)} />
            <span className="ml-1 capitalize">{execution.status}</span>
          </Badge>
          <span>Started {execution.startedAt.toLocaleString()}</span>
          {execution.completedAt && (
            <span>Completed {execution.completedAt.toLocaleString()}</span>
          )}
        </header>

        <ol className="relative space-y-4 border-l border-border/60 pl-5">
          {execution.steps.map((step, index) => (
            <StepRow
              key={step.id}
              step={step}
              index={index}
              canConfirm={step.kind === "approval"}
              onConfirmStep={onConfirmStep}
            />
          ))}
        </ol>
      </div>

      <aside className="space-y-4 rounded-xl border border-border/70 bg-surface/70 p-4 text-xs text-text-muted">
        <h3 className="text-sm font-semibold text-text-main">Run context</h3>
        <div className="space-y-1.5">
          <div>
            <span className="text-[11px] uppercase tracking-[0.16em]">
              Agent
            </span>
            <div className="mt-0.5 text-sm text-text-main">
              {execution.agentName}
            </div>
          </div>
          <div>
            <span className="text-[11px] uppercase tracking-[0.16em]">
              Trigger
            </span>
            <div className="mt-0.5">
              {execution.triggerDescription ?? "Manual trigger (placeholder)"}
            </div>
          </div>
          <div>
            <span className="text-[11px] uppercase tracking-[0.16em]">
              Target calendar
            </span>
            <div className="mt-0.5">
              {execution.targetCalendar ?? "Primary work calendar"}
            </div>
          </div>
        </div>
      </aside>
    </section>
  );
}

interface StepRowProps {
  step: WorkflowStep;
  index: number;
  canConfirm: boolean;
  onConfirmStep?: (stepId: string) => Promise<void>;
}

function StepRow({ step, index, canConfirm, onConfirmStep }: StepRowProps) {
  const approving = step.status === "waiting_approval" && !!onConfirmStep;

  return (
    <li className="relative flex gap-3">
      <div className="absolute -left-[9px] top-1">
        <span className="flex h-4 w-4 items-center justify-center rounded-full border border-border bg-surface">
          <span
            className={`h-2 w-2 rounded-full ${
              {
                running: "bg-status-running",
                pending: "bg-status-pending",
                succeeded: "bg-status-success",
                failed: "bg-status-error",
                waiting_approval: "bg-status-pending"
              }[step.status]
            }`}
          />
        </span>
      </div>

      <div className="flex-1 space-y-1">
        <div className="flex items-center gap-2">
          <span className="text-[11px] uppercase tracking-[0.16em] text-text-muted">
            {String(index + 1).padStart(2, "0")} · {step.label}
          </span>
          <Badge intent={statusToIntent(step.status)}>
            <span className="capitalize">{step.status}</span>
          </Badge>
        </div>
        <p className="text-xs text-text-main/90">{step.description}</p>
        <p className="text-[11px] text-text-muted">
          {step.timestamp?.toLocaleString() ?? "Pending"}
        </p>

        {canConfirm && (
          <div className="mt-2">
            <ConfirmationToggle
              label="Approve this step"
              value={step.status === "succeeded"}
              disabled={!approving}
              onChange={async () => {
                if (!onConfirmStep) return;
                await onConfirmStep(step.id);
              }}
            />
          </div>
        )}
      </div>
    </li>
  );
}

function statusToDot(
  status: WorkflowExecution["status"] | WorkflowStep["status"]
): "running" | "pending" | "success" | "error" {
  if (status === "running") return "running";
  if (status === "succeeded") return "success";
  if (status === "failed") return "error";
  return "pending";
}

function statusToIntent(
  status: WorkflowExecution["status"] | WorkflowStep["status"]
): "default" | "success" | "warning" | "error" {
  switch (status) {
    case "succeeded":
      return "success";
    case "failed":
      return "error";
    case "waiting_approval":
      return "warning";
    default:
      return "default";
  }
}


