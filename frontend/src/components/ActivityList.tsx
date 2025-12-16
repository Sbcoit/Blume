/* ActivityList
 * Reusable list component to display workflow executions with statuses and quick metadata.
 * Consumed by the main dashboard and executions index pages.
 */
"use client";

import { WorkflowExecution } from "@/types/workflow";
import Card from "@/components/UI/Card";
import Badge from "@/components/UI/Badge";
import StatusDot from "@/components/UI/StatusDot";
import Skeleton from "@/components/UI/Skeleton";

interface ActivityListProps {
  executions: WorkflowExecution[];
  isLoading?: boolean;
  emptyState?: string;
  onSelectExecution?: (id: string) => void;
}

export default function ActivityList({
  executions,
  isLoading,
  emptyState = "No workflow runs yet. Trigger your first agent to see live activity.",
  onSelectExecution
}: ActivityListProps) {
  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-20 w-full rounded-xl" />
        ))}
      </div>
    );
  }

  if (!executions.length) {
    return (
      <Card className="flex items-center justify-between">
        <p className="text-sm text-text-muted">{emptyState}</p>
      </Card>
    );
  }

  return (
    <div className="space-y-2">
      {executions.map((exec, idx) => (
        <Card
          key={exec.id}
          className="flex cursor-pointer items-center justify-between gap-4 border-border/60 bg-surface/80 transition hover:bg-surface"
          style={{ animationDelay: `${idx * 40}ms` }}
          onClick={() => onSelectExecution?.(exec.id)}
        >
          <div className="flex flex-1 items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-surface/80 text-xs text-text-muted border border-border/80">
              <StatusDot status={executionStatusToDot(exec.status)} />
            </div>
            <div>
              <div className="text-sm font-medium">{exec.name}</div>
              <div className="mt-0.5 text-xs text-text-muted">
                {exec.agentName} · {exec.stepCount} steps ·{" "}
                {exec.startedAt.toLocaleTimeString()}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 text-xs text-text-muted">
            <Badge intent={executionStatusToIntent(exec.status)}>
              <span className="capitalize">{exec.status}</span>
            </Badge>
            <span className="hidden text-[11px] md:inline">
              Duration: {exec.durationHuman}
            </span>
          </div>
        </Card>
      ))}
    </div>
  );
}

function executionStatusToDot(
  status: WorkflowExecution["status"]
): "running" | "pending" | "success" | "error" {
  switch (status) {
    case "running":
      return "running";
    case "succeeded":
      return "success";
    case "failed":
      return "error";
    case "waiting_approval":
    default:
      return "pending";
  }
}

function executionStatusToIntent(
  status: WorkflowExecution["status"]
): "default" | "success" | "warning" | "error" {
  switch (status) {
    case "succeeded":
      return "success";
    case "failed":
      return "error";
    case "waiting_approval":
      return "warning";
    case "running":
    default:
      return "default";
  }
}


