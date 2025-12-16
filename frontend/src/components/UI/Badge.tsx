import { ReactNode } from "react";
import clsx from "clsx";

interface BadgeProps {
  intent?: "default" | "success" | "warning" | "error";
  children: ReactNode;
  className?: string;
}

export default function Badge({
  intent = "default",
  children,
  className
}: BadgeProps) {
  const intents: Record<NonNullable<BadgeProps["intent"]>, string> = {
    default: "bg-surface/80 text-text-muted border-border/70",
    success: "bg-status-success/10 text-status-success border-status-success/40",
    warning: "bg-status-pending/10 text-status-pending border-status-pending/40",
    error: "bg-status-error/10 text-status-error border-status-error/40"
  };

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px]",
        intents[intent],
        className
      )}
    >
      {children}
    </span>
  );
}


