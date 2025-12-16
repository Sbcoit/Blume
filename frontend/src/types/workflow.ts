export type WorkflowStatus =
  | "running"
  | "succeeded"
  | "failed"
  | "waiting_approval";

export type WorkflowStepStatus =
  | "pending"
  | "running"
  | "succeeded"
  | "failed"
  | "waiting_approval";

export interface WorkflowStep {
  id: string;
  label: string;
  description: string;
  status: WorkflowStepStatus;
  timestamp?: Date;
  kind?: "task" | "approval" | "system";
}

export interface WorkflowExecution {
  id: string;
  name: string;
  agentName: string;
  status: WorkflowStatus;
  steps: WorkflowStep[];
  stepCount: number;
  startedAt: Date;
  completedAt?: Date;
  durationHuman: string;
  triggerDescription?: string;
  targetCalendar?: string;
}


