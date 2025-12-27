"use client";

import React from "react";
import { motion } from "framer-motion";
import { Calendar, Search, FileText, Settings, Phone, MessageSquare } from "lucide-react";

export interface Task {
  id: string;
  type: string;
  input: string;
  output?: string;
  status: "pending" | "completed" | "failed";
  created_at: string;
  metadata?: Record<string, any>;
}

interface TaskCardProps {
  task: Task;
  onClick: () => void;
}

const taskTypeIcons: Record<string, React.ElementType> = {
  scheduling: Calendar,
  research: Search,
  document: FileText,
  workflow: Settings,
  call: Phone,
  text: MessageSquare,
};

const taskTypeColors: Record<string, string> = {
  scheduling: "#FF6B6B",
  research: "#4ECDC4",
  document: "#95E1D3",
  workflow: "#F38181",
  call: "#AA96DA",
  text: "#FCBAD3",
};

const statusColors: Record<string, string> = {
  pending: "#FFA726",
  completed: "#66BB6A",
  failed: "#EF5350",
};

export const TaskCard: React.FC<TaskCardProps> = ({ task, onClick }) => {
  const IconComponent = taskTypeIcons[task.type] || FileText;
  const typeColor = taskTypeColors[task.type] || "#666";
  const statusColor = statusColors[task.status];
  
  const previewText = task.input.length > 60 
    ? task.input.substring(0, 60) + "..." 
    : task.input;
  
  const date = new Date(task.created_at);
  const formattedDate = date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: date.getFullYear() !== new Date().getFullYear() ? "numeric" : undefined,
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      className="glass-card glass-hover"
      onClick={onClick}
      style={{ cursor: "pointer" }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", gap: "1.25rem" }}>
        {/* Type Icon/Color Indicator */}
        <div
          style={{
            width: "3.5rem",
            height: "3.5rem",
            borderRadius: "0.75rem",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
            backgroundColor: `${typeColor}20`
          }}
        >
          <IconComponent size={26} style={{ color: typeColor }} />
        </div>

        {/* Content */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* Title Preview */}
          <h3 className="body-base" style={{ 
            color: "var(--text-primary)", 
            marginBottom: "0.75rem",
            fontWeight: 500,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
            lineHeight: "1.5"
          }}>
            {previewText}
          </h3>

          {/* Status and Date */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
            <span
              style={{
                fontSize: "0.75rem",
                fontWeight: 500,
                padding: "0.375rem 0.75rem",
                borderRadius: "9999px",
                backgroundColor: `${statusColor}20`,
                color: statusColor,
              }}
            >
              {task.status}
            </span>
            <span className="body-small" style={{ color: "var(--text-tertiary)", fontSize: "0.8125rem" }}>
              {formattedDate}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
