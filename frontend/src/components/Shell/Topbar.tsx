/* Topbar
 * Light-weight top navigation for live status + quick actions.
 */
"use client";

import Button from "@/components/UI/Button";

export default function Topbar() {
  return (
    <header className="flex items-center justify-between border-b border-border/70 bg-surface/60 px-8 py-3 backdrop-blur-xl">
      <div className="flex items-center gap-3 text-xs text-text-muted">
        <span className="rounded-full border border-border px-2 py-0.5 uppercase tracking-[0.16em]">
          Live
        </span>
        <span className="hidden md:inline">
          Agents are currently syncing with Google Calendar and internal tools.
        </span>
      </div>

      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm">
          Activity Log
        </Button>
        <Button variant="outline" size="sm">
          New Workflow
        </Button>
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-accent to-accent-soft text-[11px] font-semibold text-black">
          AM
        </div>
      </div>
    </header>
  );
}


