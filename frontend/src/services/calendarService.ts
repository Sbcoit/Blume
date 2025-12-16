import { CalendarAccount } from "@/types/calendar";
import { mockCalendars } from "@/lib/mockData";

export async function getConnectedCalendars(): Promise<CalendarAccount[]> {
  // Example REST call to replace mock data later:
  // const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/calendars`, {
  //   cache: "no-store"
  // });
  // if (!res.ok) throw new Error("Failed to fetch calendars");
  // return res.json();

  return mockCalendars;
}

export async function connectCalendar(accountId: string): Promise<void> {
  console.log("[calendarService] Connect calendar", { accountId });
}

export async function disconnectCalendar(accountId: string): Promise<void> {
  console.log("[calendarService] Disconnect calendar", { accountId });
}


