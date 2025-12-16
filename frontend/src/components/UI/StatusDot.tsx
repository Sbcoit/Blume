import clsx from "clsx";

interface StatusDotProps {
  status: "running" | "pending" | "success" | "error";
}

export default function StatusDot({ status }: StatusDotProps) {
  const colorMap: Record<StatusDotProps["status"], string> = {
    running: "bg-status-running",
    pending: "bg-status-pending",
    success: "bg-status-success",
    error: "bg-status-error"
  };

  return (
    <span
      className={clsx(
        "inline-block h-2 w-2 rounded-full",
        colorMap[status],
        status === "running" && "animate-pulse"
      )}
    />
  );
}


