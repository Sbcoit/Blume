"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";

interface AgentInfoModalProps {
  isOpen: boolean;
  phoneNumber: string | null;
  agentName: string | null;
  onEdit: () => void;
}

export const AgentInfoModal: React.FC<AgentInfoModalProps> = ({
  isOpen,
  phoneNumber,
  agentName,
  onEdit,
}) => {
  const displayName = agentName || "Blume";

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, scale: 0.92, y: 30 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.92, y: 30 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          style={{
            position: "relative",
            width: "100%",
            height: "100%"
          }}
        >
          <div 
            className="glass-modal" 
            style={{ 
              width: "100%",
              height: "100%",
              display: "flex",
              flexDirection: "column"
            }}
          >
              <h2 className="heading-3" style={{ color: "var(--text-primary)", marginBottom: "0.25rem" }}>
                Your Blume Agent
              </h2>
              <p className="body-small" style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>
                Current configuration
              </p>
              
              <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", flex: 1 }}>
                {/* Info Display - Horizontal Layout */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
                  {/* Phone Number Display */}
                  <div>
                    <label
                      className="body-small"
                      style={{ 
                        color: "var(--text-secondary)", 
                        marginBottom: "0.75rem",
                        display: "block",
                        fontWeight: 500
                      }}
                    >
                      Phone Number
                    </label>
                    <div
                      style={{
                        padding: "0.75rem 1rem",
                        borderRadius: "var(--radius-md)",
                        backgroundColor: "rgba(255, 255, 255, 0.05)",
                        border: "1px solid var(--border-primary)",
                        color: "var(--text-primary)",
                        fontSize: "1rem",
                        marginBottom: "0.5rem"
                      }}
                    >
                      {phoneNumber || "Not set"}
                    </div>
                    <p className="body-small" style={{ color: "var(--text-tertiary)", fontSize: "0.8125rem" }}>
                      Connected for iMessage communication
                    </p>
                  </div>

                  {/* Agent Name Display */}
                  <div>
                    <label
                      className="body-small"
                      style={{ 
                        color: "var(--text-secondary)", 
                        marginBottom: "0.75rem",
                        display: "block",
                        fontWeight: 500
                      }}
                    >
                      Agent Name
                    </label>
                    <div
                      style={{
                        padding: "0.75rem 1rem",
                        borderRadius: "var(--radius-md)",
                        backgroundColor: "rgba(255, 255, 255, 0.05)",
                        border: "1px solid var(--border-primary)",
                        color: "var(--text-primary)",
                        fontSize: "1rem",
                        marginBottom: "0.5rem"
                      }}
                    >
                      {displayName}
                    </div>
                    <p className="body-small" style={{ color: "var(--text-tertiary)", fontSize: "0.8125rem" }}>
                      {agentName ? "Custom agent name" : "Default agent name"}
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div style={{ display: "flex", gap: "1rem", paddingTop: "0.5rem", justifyContent: "flex-start", marginTop: "auto" }}>
                  <button
                    type="button"
                    onClick={onEdit}
                    className="glass-button-primary"
                    style={{ minWidth: "120px" }}
                  >
                    Edit Configuration
                  </button>
                </div>
              </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

