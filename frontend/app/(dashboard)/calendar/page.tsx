import { getConnectedCalendars } from "@/services/calendarService";

export default async function CalendarPage() {
  const calendars = await getConnectedCalendars();

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">
          Calendar Connections
        </h1>
        <p className="mt-1 text-sm text-text-muted">
          Decide exactly which calendars your agents can see, edit, and orchestrate.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {calendars.map((cal) => (
          <div
            key={cal.id}
            className="relative overflow-hidden rounded-xl border border-border/60 bg-surface/80 p-4 shadow-md backdrop-blur"
          >
            <div className="mb-1 text-xs uppercase tracking-[0.2em] text-text-muted">
              {cal.provider.toUpperCase()}
            </div>
            <h2 className="text-sm font-semibold">{cal.accountEmail}</h2>
            <p className="mt-1 text-xs text-text-muted">
              Scope: {cal.scopeDescription}
            </p>
            <p className="mt-2 text-[11px] text-text-muted/80">
              Last sync: {cal.lastSync.toLocaleString()}
            </p>

            <div className="mt-4 flex flex-wrap gap-2 text-xs">
              <button
                className="rounded-full bg-accent/90 px-3 py-1 text-[11px] text-black hover:bg-accent transition"
                onClick={() => console.log("Connect or re-auth calendar", cal.id)}
              >
                {cal.connected ? "Reconnect" : "Connect"}
              </button>
              <button
                className="rounded-full border border-border px-3 py-1 text-[11px] text-text-muted hover:border-status-error hover:text-status-error transition"
                onClick={() => console.log("Disconnect calendar", cal.id)}
              >
                Disconnect
              </button>
              <button
                className="ml-auto rounded-full border border-border px-3 py-1 text-[11px] text-text-muted hover:border-accent hover:text-accent transition"
                onClick={() => console.log("Resync calendar", cal.id)}
              >
                Resync
              </button>
            </div>

            <div className="pointer-events-none absolute -right-10 -top-10 h-32 w-32 rounded-full bg-accent-soft/25 blur-3xl" />
          </div>
        ))}
      </div>
    </div>
  );
}


