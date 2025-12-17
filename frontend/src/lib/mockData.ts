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
    name: "Scheduled meeting: Q4 Planning",
    agentName: "Blume",
    status: "waiting_approval",
    steps: [
      {
        id: "step-1",
        label: "Analyzed calendar availability",
        description: "Checked all participants' calendars for next 2 weeks",
        status: "succeeded",
        timestamp: new Date(now.getTime() - 1000 * 60 * 8),
        kind: "system"
      },
      {
        id: "step-2",
        label: "Found optimal time slot",
        description: "Proposed Dec 18, 2:00 PM - 3:30 PM (all participants free)",
        status: "succeeded",
        timestamp: new Date(now.getTime() - 1000 * 60 * 7),
        kind: "task"
      },
      {
        id: "step-3",
        label: "Awaiting approval",
        description: "Waiting for confirmation before sending calendar invites",
        status: "waiting_approval",
        timestamp: undefined,
        kind: "approval"
      }
    ],
    stepCount: 3,
    startedAt: new Date(now.getTime() - 1000 * 60 * 8),
    completedAt: undefined,
    durationHuman: formatDurationMs(1000 * 60 * 8),
    triggerDescription: "SMS: 'Schedule Q4 planning meeting'",
    targetCalendar: "amy@company.com"
  },
  {
    id: "exec-2",
    name: "Blocked focus time: Deep work session",
    agentName: "Blume",
    status: "succeeded",
    steps: [
      {
        id: "step-1",
        label: "Identified free blocks",
        description: "Found 3-hour window tomorrow 9 AM - 12 PM",
        status: "succeeded",
        timestamp: new Date(now.getTime() - 1000 * 60 * 45),
        kind: "system"
      },
      {
        id: "step-2",
        label: "Created calendar event",
        description: "Added 'Deep Work: Project Alpha' to calendar",
        status: "succeeded",
        timestamp: new Date(now.getTime() - 1000 * 60 * 44),
        kind: "task"
      }
    ],
    stepCount: 2,
    startedAt: new Date(now.getTime() - 1000 * 60 * 45),
    completedAt: new Date(now.getTime() - 1000 * 60 * 44),
    durationHuman: formatDurationMs(1000 * 60 * 1),
    triggerDescription: "SMS: 'Block 3 hours for deep work tomorrow'",
    targetCalendar: "amy@company.com"
  },
  {
    id: "exec-3",
    name: "Rescheduled: Team standup",
    agentName: "Blume",
    status: "running",
    steps: [
      {
        id: "step-1",
        label: "Detected conflict",
        description: "Found overlap with 'Client Call' at 10 AM",
        status: "succeeded",
        timestamp: new Date(now.getTime() - 1000 * 60 * 2),
        kind: "system"
      },
      {
        id: "step-2",
        label: "Finding alternative time",
        description: "Searching for next available slot...",
        status: "running",
        timestamp: new Date(now.getTime() - 1000 * 60 * 1),
        kind: "task"
      }
    ],
    stepCount: 2,
    startedAt: new Date(now.getTime() - 1000 * 60 * 2),
    completedAt: undefined,
    durationHuman: formatDurationMs(1000 * 60 * 2),
    triggerDescription: "Auto-detected calendar conflict",
    targetCalendar: "team@company.com"
  },
  {
    id: "exec-4",
    name: "Failed: Schedule all-hands meeting",
    agentName: "Blume",
    status: "failed",
    steps: [
      {
        id: "step-1",
        label: "Attempted to find time",
        description: "Searched for 1-hour slot for 50+ participants",
        status: "succeeded",
        timestamp: new Date(now.getTime() - 1000 * 60 * 120),
        kind: "system"
      },
      {
        id: "step-2",
        label: "No suitable time found",
        description: "Could not find a slot where all participants are available",
        status: "failed",
        timestamp: new Date(now.getTime() - 1000 * 60 * 119),
        kind: "task"
      }
    ],
    stepCount: 2,
    startedAt: new Date(now.getTime() - 1000 * 60 * 120),
    completedAt: new Date(now.getTime() - 1000 * 60 * 119),
    durationHuman: formatDurationMs(1000 * 60 * 1),
    triggerDescription: "SMS: 'Schedule all-hands for next week'",
    targetCalendar: "team@company.com"
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
    lastSync: new Date(now.getTime() - 1000 * 60 * 15),
    scopeDescription: "Read-only access to planning calendars"
  },
  {
    id: "cal-3",
    provider: "google",
    accountEmail: "personal@gmail.com",
    connected: true,
    lastSync: new Date(now.getTime() - 1000 * 60 * 5),
    scopeDescription: "Read/write on personal calendar"
  },
  {
    id: "cal-4",
    provider: "google",
    accountEmail: "sandbox@company.com",
    connected: false,
    lastSync: new Date(now.getTime() - 1000 * 60 * 60 * 24),
    scopeDescription: "No active connection"
  }
];


