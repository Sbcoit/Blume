import { ButtonHTMLAttributes, ReactNode } from "react";
import clsx from "clsx";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost" | "outline";
  size?: "sm" | "md";
  children: ReactNode;
}

export default function Button({
  variant = "primary",
  size = "md",
  className,
  children,
  ...rest
}: ButtonProps) {
  const base =
    "inline-flex items-center justify-center rounded-full font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/80";

  const variants: Record<NonNullable<ButtonProps["variant"]>, string> = {
    primary:
      "bg-accent text-black hover:bg-accent/90 active:bg-accent-soft/80 border border-accent/60",
    ghost:
      "bg-transparent text-text-muted hover:text-text-main hover:bg-surface/80 border border-transparent",
    outline:
      "bg-transparent text-text-main border border-border hover:border-accent/70 hover:text-accent"
  };

  const sizes: Record<NonNullable<ButtonProps["size"]>, string> = {
    sm: "px-3 py-1 text-xs",
    md: "px-4 py-2 text-sm"
  };

  return (
    <button
      className={clsx(base, variants[variant], sizes[size], className)}
      {...rest}
    >
      {children}
    </button>
  );
}


