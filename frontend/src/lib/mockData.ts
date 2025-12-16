import { WorkflowExecution, WorkflowStep } from "@/types/workflow";
import { CalendarAccount } from "@/types/calendar";
import { formatDurationMs } from "@/lib/formatters";

const now = new Date();

function buildSteps(): WorkflowStep[] {
  return [
    {
      id: "step-1",
      label: "Collect constraints",
      description:
        "Pull working hours and focus blocks from connected calendars.",
      status: "succeeded",
      timestamp: new Date(now.getTime() - 1000 * 60 * 5),
      kind: "system"
    },
    {
      id: "step-2",
      label: "Draft schedule",
      description:
        "Propose meeting slots that avoid collisions and deep-work blocks.",
      status: "succeeded",
      timestamp: new Date(now.getTime() - 1000 * 60 * 3),
      kind: "task"
    },
    {
      id: "step-3",
      label: "Await human approval",
      description: "Hold invites until confirmation for chosen slot.",
      status: "waiting_approval",
      timestamp: undefined,
      kind: "approval"
    }
  ];
}

export const mockExecutions: WorkflowExecution[] = [
  {
    id: "exec-1",
    name: "Weekly leadership sync scheduling",
    agentName: "Calendar Orchestrator",
    status: "waiting_approval",
    steps: buildSteps(),
    stepCount: 3,
    startedAt: new Date(now.getTime() - 1000 * 60 * 6),
    completedAt: undefined,
    durationHuman: formatDurationMs(1000 * 60 * 6),
    triggerDescription: "Slack slash command: /agent schedule leadership-sync",
    targetCalendar: "amy@company.com"
  },
  {
    id: "exec-2",
    name: "Backlog grooming time-blocks",
    agentName: "Focus Architect",
    status: "succeeded",
    steps: buildSteps().map((s) => ({ ...s, status: "succeeded" })),
    stepCount: 3,
    startedAt: new Date(now.getTime() - 1000 * 60 * 50),
    completedAt: new Date(now.getTime() - 1000 * 60 * 45),
    durationHuman: formatDurationMs(1000 * 60 * 5),
    triggerDescription: "CRON: Monday 9:00",
    targetCalendar: "product@company.com"
  }
];

export const mockCalendars: CalendarAccount[] = [
  {
    id: "cal-1",
    provider: "google",
    accountEmail: "amy@company.com",
    connected: true,
    lastSync: new Date(now.getTime() - 1000 * 60 * 2),
    scopeDescription: "Read/write on primary + project calendars"
  },
  {
    id: "cal-2",
    provider: "google",
    accountEmail: "team@company.com",
    connected: true,
    lastSync: new Date(now.getTime() - 1000 * 60 * 20),
    scopeDescription: "Read-only access to planning calendars"
  },
  {
    id: "cal-3",
    provider: "google",
    accountEmail: "sandbox@company.com",
    connected: false,
    lastSync: new Date(now.getTime() - 1000 * 60 * 60 * 24),
    scopeDescription: "No active connection"
  }
];


