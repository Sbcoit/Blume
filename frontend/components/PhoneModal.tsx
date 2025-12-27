"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface PhoneModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSetNumber: (phoneNumber: string, agentName?: string) => void;
  currentPhoneNumber?: string;
  currentAgentName?: string;
}

export const PhoneModal: React.FC<PhoneModalProps> = ({
  isOpen,
  onClose,
  onSetNumber,
  currentPhoneNumber = "",
  currentAgentName = "",
}) => {
  const [phoneNumber, setPhoneNumber] = useState(currentPhoneNumber);
  const [agentName, setAgentName] = useState(currentAgentName);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      await onSetNumber(phoneNumber, agentName || undefined);
      // Modal stays open - don't close it
    } catch (error) {
      console.error("Error setting phone number:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop - non-interactive since modal always stays open */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
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
            <div className="glass-modal" style={{ maxWidth: "56rem", width: "896px", minWidth: "32rem" }}>
              <h2 className="heading-3" style={{ color: "var(--text-primary)", marginBottom: "0.5rem" }}>
                Set Up Your Blume Agent
              </h2>
              <p className="body-small" style={{ color: "var(--text-secondary)", marginBottom: "2rem" }}>
                Configure your phone number and customize your agent
              </p>
              
              <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
                {/* Form Fields - Horizontal Layout */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
                  {/* Phone Number Input */}
                  <div>
                    <label
                      htmlFor="phone"
                      className="body-small"
                      style={{ 
                        color: "var(--text-secondary)", 
                        marginBottom: "0.75rem",
                        display: "block",
                        fontWeight: 500
                      }}
                    >
                      Phone Number *
                    </label>
                    <input
                      id="phone"
                      type="tel"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      placeholder="+1 (555) 123-4567"
                      required
                      style={{ width: "100%", marginBottom: "0.5rem" }}
                      disabled={isSubmitting}
                    />
                    <p className="body-small" style={{ color: "var(--text-tertiary)", fontSize: "0.8125rem" }}>
                      This number will be used for iMessage communication
                    </p>
                  </div>

                  {/* Agent Name Input (Optional) */}
                  <div>
                    <label
                      htmlFor="agentName"
                      className="body-small"
                      style={{ 
                        color: "var(--text-secondary)", 
                        marginBottom: "0.75rem",
                        display: "block",
                        fontWeight: 500
                      }}
                    >
                      Agent Name (Optional)
                    </label>
                    <input
                      id="agentName"
                      type="text"
                      value={agentName}
                      onChange={(e) => setAgentName(e.target.value)}
                      placeholder="My Assistant"
                      style={{ width: "100%", marginBottom: "0.5rem" }}
                      disabled={isSubmitting}
                    />
                    <p className="body-small" style={{ color: "var(--text-tertiary)", fontSize: "0.8125rem" }}>
                      Give your Blume agent a custom name
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div style={{ display: "flex", gap: "1rem", paddingTop: "0.5rem", justifyContent: "flex-start" }}>
                  <button
                    type="submit"
                    className="glass-button-primary"
                    style={{ minWidth: "120px" }}
                    disabled={isSubmitting || !phoneNumber}
                  >
                    {isSubmitting ? "Setting..." : "Set Number"}
                  </button>
                </div>
              </form>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
