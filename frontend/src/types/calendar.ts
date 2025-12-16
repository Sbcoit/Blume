export interface CalendarAccount {
  id: string;
  provider: "google";
  accountEmail: string;
  connected: boolean;
  lastSync: Date;
  scopeDescription: string;
}

export interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  calendarId: string;
  sourceExecutionId?: string;
}


