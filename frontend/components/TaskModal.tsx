"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, X } from "lucide-react";
import { MessageBubble } from "./MessageBubble";
import { Task } from "./TaskCard";

interface TaskModalProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onNext?: () => void;
  onPrevious?: () => void;
  hasNext?: boolean;
  hasPrevious?: boolean;
}

export const TaskModal: React.FC<TaskModalProps> = ({
  task,
  isOpen,
  onClose,
  onNext,
  onPrevious,
  hasNext = false,
  hasPrevious = false,
}) => {
  if (!task) return null;

  const date = new Date(task.created_at);
  const formattedDate = date.toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-40"
            style={{
              background: "rgba(0, 0, 0, 0.7)",
              backdropFilter: "blur(20px)",
              WebkitBackdropFilter: "blur(20px)",
            }}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.92, y: 30 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.92, y: 30 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="glass-modal max-w-3xl w-full max-h-[90vh] overflow-y-auto mx-auto">
              {/* Header with Navigation */}
              <div style={{ 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "space-between",
                marginBottom: "2.5rem"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                  {(hasPrevious || hasNext) && (
                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      <button
                        onClick={onPrevious}
                        disabled={!hasPrevious}
                        className="glass-button"
                        style={{ 
                          padding: "0.5rem",
                          opacity: !hasPrevious ? 0.5 : 1,
                          cursor: !hasPrevious ? "not-allowed" : "pointer"
                        }}
                      >
                        <ChevronLeft size={20} />
                      </button>
                      <button
                        onClick={onNext}
                        disabled={!hasNext}
                        className="glass-button"
                        style={{ 
                          padding: "0.5rem",
                          opacity: !hasNext ? 0.5 : 1,
                          cursor: !hasNext ? "not-allowed" : "pointer"
                        }}
                      >
                        <ChevronRight size={20} />
                      </button>
                    </div>
                  )}
                </div>
                <button
                  onClick={onClose}
                  className="glass-button"
                  style={{ padding: "0.5rem" }}
                >
                  <X size={20} />
                </button>
              </div>

              {/* Task Details Section */}
              <section style={{ marginBottom: "3rem" }}>
                <h2 className="heading-3" style={{ color: "var(--text-primary)", marginBottom: "1.5rem" }}>Task Details</h2>
                <div className="glass" style={{ borderRadius: "1rem", padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1.25rem" }}>
                  <div>
                    <p className="body-small" style={{ color: "var(--text-secondary)", marginBottom: "0.5rem", fontWeight: 500 }}>Type</p>
                    <p className="body-base" style={{ color: "var(--text-primary)", textTransform: "capitalize" }}>{task.type}</p>
                  </div>
                  <div>
                    <p className="body-small" style={{ color: "var(--text-secondary)", marginBottom: "0.5rem", fontWeight: 500 }}>Status</p>
                    <p className="body-base" style={{ color: "var(--text-primary)", textTransform: "capitalize" }}>{task.status}</p>
                  </div>
                  <div>
                    <p className="body-small" style={{ color: "var(--text-secondary)", marginBottom: "0.5rem", fontWeight: 500 }}>Created</p>
                    <p className="body-base" style={{ color: "var(--text-primary)" }}>{formattedDate}</p>
                  </div>
                </div>
              </section>

              {/* User Input Section */}
              <section style={{ marginBottom: "3rem" }}>
                <h2 className="heading-3" style={{ color: "var(--text-primary)", marginBottom: "1.5rem" }}>User Input</h2>
                <div style={{ paddingLeft: "1rem", paddingRight: "1rem" }}>
                  <MessageBubble message={task.input} isAgent={false} />
                </div>
              </section>

              {/* Agent Output Section */}
              {task.output && (
                <section style={{ marginBottom: "3rem" }}>
                  <h2 className="heading-3" style={{ color: "var(--text-primary)", marginBottom: "1.5rem" }}>Agent Output</h2>
                  <div style={{ paddingLeft: "1rem", paddingRight: "1rem" }}>
                    <MessageBubble message={task.output} isAgent={true} />
                  </div>
                </section>
              )}

              {/* Execution Details Section */}
              {task.metadata && Object.keys(task.metadata).length > 0 && (
                <section style={{ marginBottom: "2rem" }}>
                  <h2 className="heading-3" style={{ color: "var(--text-primary)", marginBottom: "1.5rem" }}>Execution Details</h2>
                  <div className="glass" style={{ borderRadius: "1rem", padding: "1.5rem" }}>
                    <pre className="body-small" style={{ 
                      color: "var(--text-primary)",
                      whiteSpace: "pre-wrap",
                      wordWrap: "break-word",
                      fontFamily: "inherit"
                    }}>
                      {JSON.stringify(task.metadata, null, 2)}
                    </pre>
                  </div>
                </section>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
