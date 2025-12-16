import { ReactNode } from "react";
import clsx from "clsx";

interface CardProps {
  children: ReactNode;
  className?: string;
}

export default function Card({ children, className }: CardProps) {
  return (
    <div
      className={clsx(
        "relative overflow-hidden rounded-xl border border-border/70 bg-surface/90 p-4 shadow-elevated backdrop-blur-md",
        "transition hover:border-accent/70 hover:-translate-y-[1px]",
        className
      )}
    >
      {children}
    </div>
  );
}


