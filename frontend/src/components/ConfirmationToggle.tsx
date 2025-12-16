/* ConfirmationToggle
 * Small toggle used to confirm or approve workflow steps.
 * Shows optimistic UI with a pill + thumb interaction.
 */
"use client";

import { useState } from "react";
import clsx from "clsx";

interface ConfirmationToggleProps {
  label?: string;
  value: boolean;
  disabled?: boolean;
  onChange?: (next: boolean) => Promise<void> | void;
}

export default function ConfirmationToggle({
  label = "Confirm",
  value,
  disabled,
  onChange
}: ConfirmationToggleProps) {
  const [pending, setPending] = useState(false);

  const handleToggle = async () => {
    if (disabled || pending || !onChange) return;
    const next = !value;

    try {
      setPending(true);
      await onChange(next);
    } finally {
      setPending(false);
    }
  };

  return (
    <button
      type="button"
      className={clsx(
        "inline-flex items-center gap-2 rounded-full border px-2 py-1 text-xs transition",
        value
          ? "border-status-success/70 bg-status-success/10 text-status-success"
          : "border-border bg-surface/70 text-text-muted",
        disabled && "cursor-not-allowed opacity-60"
      )}
      disabled={disabled || pending}
      onClick={handleToggle}
    >
      <div
        className={clsx(
          "relative h-4 w-7 rounded-full border transition",
          value
            ? "border-status-success bg-status-success/30"
            : "border-border bg-surface/70"
        )}
      >
        <span
          className={clsx(
            "absolute left-[2px] top-[1px] h-3 w-3 rounded-full bg-white shadow-sm transition-transform",
            value && "translate-x-3 bg-status-success"
          )}
        />
      </div>
      <span>
        {value ? "Confirmed" : label}
        {pending && "…"}
      </span>
    </button>
  );
}


