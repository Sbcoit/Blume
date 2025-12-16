/* Sidebar
 * Branded navigation shell for dashboard routes.
 */
"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import clsx from "clsx";

const navItems = [{ href: "/console", label: "Console" }];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="relative flex w-60 flex-col border-r border-border/70 bg-surface/70 px-4 py-5 backdrop-blur-xl">
      <div className="mb-8 flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-accent/90 text-black shadow-elevated">
          <span className="text-sm font-semibold">AO</span>
        </div>
        <div className="text-xs">
          <div className="font-semibold tracking-tight">Agent Orchestrator</div>
          <div className="text-[10px] uppercase tracking-[0.18em] text-text-muted">
            control deck
          </div>
        </div>
      </div>

      <nav className="space-y-1 text-sm">
        {navItems.map((item) => {
          const active =
            item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "group flex items-center justify-between rounded-lg px-3 py-2 text-xs transition",
                "border border-transparent",
                active
                  ? "bg-accent-soft/20 border-accent/70 text-text-main"
                  : "text-text-muted hover:text-text-main hover:bg-surface/70 hover:border-border/70"
              )}
            >
              <span>{item.label}</span>
              <span
                className={clsx(
                  "h-1 w-1 rounded-full transition",
                  active ? "bg-accent" : "bg-border group-hover:bg-accent-soft"
                )}
              />
            </Link>
          );
        })}
      </nav>

      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-accent-soft/20 to-transparent" />
    </aside>
  );
}


