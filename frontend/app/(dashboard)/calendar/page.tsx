/* CalendarPage
 * Shows all connected Google Calendar accounts that your agent can access.
 * Manage connections, sync status, and permissions here.
 */
"use client";

import { getConnectedCalendars } from "@/services/calendarService";
import { useEffect, useState } from "react";
import { CalendarAccount } from "@/types/calendar";
import Button from "@/components/UI/Button";
import { useRouter } from "next/navigation";

export default function CalendarPage() {
  const router = useRouter();
  const [calendars, setCalendars] = useState<CalendarAccount[]>([]);

  useEffect(() => {
    getConnectedCalendars().then(setCalendars);
  }, []);

  return (
    <div className="space-y-6">
      <header className="flex items-end justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">
            Calendar Connections
          </h1>
          <p className="text-sm text-text-muted">
            Decide exactly which calendars your agents can see, edit, and orchestrate.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push("/console")}
            className="text-xs"
          >
            Console
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push("/")}
            className="text-xs"
          >
            Log out
          </Button>
        </div>
      </header>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {calendars.map((cal) => (
          <div
            key={cal.id}
            className="relative overflow-hidden rounded-2xl border border-border/40 bg-background/25 p-4 shadow-elevated backdrop-blur-xl"
          >
            <div className="mb-1 text-xs uppercase tracking-[0.2em] text-text-muted">
              {cal.provider.toUpperCase()}
            </div>
            <h2 className="text-sm font-semibold text-text-main">{cal.accountEmail}</h2>
            <p className="mt-1 text-xs text-text-muted">
              Scope: {cal.scopeDescription}
            </p>
            <p className="mt-2 text-[11px] text-text-muted/80">
              Last sync: {cal.lastSync.toLocaleString()}
            </p>

            <div className="mt-4 flex flex-wrap gap-2 text-xs">
              <Button
                variant="primary"
                size="sm"
                onClick={() => console.log("Connect or re-auth calendar", cal.id)}
                className="text-[11px]"
              >
                {cal.connected ? "Reconnect" : "Connect"}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => console.log("Disconnect calendar", cal.id)}
                className="text-[11px] border-status-error/50 text-status-error hover:border-status-error"
              >
                Disconnect
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => console.log("Resync calendar", cal.id)}
                className="ml-auto text-[11px]"
              >
                Resync
              </Button>
            </div>

            {/* Subtle accent glow */}
            <div className="pointer-events-none absolute -right-10 -top-10 h-32 w-32 rounded-full bg-accent-soft/20 blur-3xl" />
          </div>
        ))}
      </div>
    </div>
  );
}


