import clsx from "clsx";

interface SkeletonProps {
  className?: string;
}

export default function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={clsx(
        "animate-pulse rounded-md bg-surface/70",
        "bg-gradient-to-r from-surface via-surface/40 to-surface",
        className
      )}
    />
  );
}


