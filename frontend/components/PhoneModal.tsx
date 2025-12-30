"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface PhoneModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSetNumber: (phoneNumber: string, agentName?: string) => void;
  currentPhoneNumber?: string;
  currentAgentName?: string;
}

// Normalize phone number to E.164 format (e.g., +15551234567)
const normalizePhoneNumber = (phone: string): string => {
  // Remove all non-digit characters except +
  let cleaned = phone.replace(/[^\d+]/g, '');
  
  // If it starts with +, keep it; otherwise add +1 for US numbers
  if (cleaned.startsWith('+')) {
    return cleaned;
  }
  
  // If it's 10 digits, assume US number and add +1
  if (cleaned.length === 10) {
    return `+1${cleaned}`;
  }
  
  // If it's 11 digits and starts with 1, add +
  if (cleaned.length === 11 && cleaned.startsWith('1')) {
    return `+${cleaned}`;
  }
  
  // Otherwise, try to add +1 if it looks like a US number
  if (cleaned.length >= 10) {
    return `+1${cleaned.slice(-10)}`;
  }
  
  // Return as-is if we can't normalize
  return phone;
};

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
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState(false);

  // Update state when props change
  useEffect(() => {
    setPhoneNumber(currentPhoneNumber);
    setAgentName(currentAgentName);
  }, [currentPhoneNumber, currentAgentName]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Form submitted with:", { phoneNumber, agentName });
    setError("");
    setSuccess(false);
    setIsSubmitting(true);
    
    try {
      // Normalize phone number before submitting
      const normalizedPhone = normalizePhoneNumber(phoneNumber.trim());
      console.log("Normalized phone:", normalizedPhone);
      
      // Basic validation
      if (!normalizedPhone || normalizedPhone.length < 10) {
        setError("Please enter a valid phone number");
        setIsSubmitting(false);
        return;
      }
      
      console.log("Calling onSetNumber with:", { phone: normalizedPhone, name: agentName?.trim() || undefined });
      try {
        await onSetNumber(normalizedPhone, agentName?.trim() || undefined);
        console.log("onSetNumber completed successfully");
        setSuccess(true);
        
        // Clear success message after 2 seconds
        setTimeout(() => {
          setSuccess(false);
        }, 2000);
      } catch (onSetNumberError: any) {
        console.error("Error in onSetNumber callback:", onSetNumberError);
        throw onSetNumberError; // Re-throw to be caught by outer catch
      }
    } catch (error: any) {
      console.error("Error setting phone number in PhoneModal:", error);
      console.error("Error stack:", error.stack);
      setError(error.message || "Failed to save phone number. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

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
                Set Up Your Blume Agent
              </h2>
              <p className="body-small" style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>
                Configure your phone number and customize your agent
              </p>
              
              {/* Error Message */}
              {error && (
                <div style={{
                  marginBottom: "1rem",
                  padding: "0.75rem",
                  borderRadius: "var(--radius-md)",
                  backgroundColor: "rgba(239, 68, 68, 0.15)",
                  border: "1px solid rgba(239, 68, 68, 0.3)",
                  color: "#EF4444",
                  fontSize: "0.875rem"
                }}>
                  {error}
                </div>
              )}

              {/* Success Message */}
              {success && (
                <div style={{
                  marginBottom: "1rem",
                  padding: "0.75rem",
                  borderRadius: "var(--radius-md)",
                  backgroundColor: "rgba(34, 197, 94, 0.15)",
                  border: "1px solid rgba(34, 197, 94, 0.3)",
                  color: "#22C55E",
                  fontSize: "0.875rem"
                }}>
                  Phone number saved successfully!
                </div>
              )}
              
              <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.5rem", flex: 1 }}>
                {/* Form Fields - Horizontal Layout */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
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
                <div style={{ display: "flex", gap: "1rem", paddingTop: "0.5rem", justifyContent: "flex-start", marginTop: "auto" }}>
                  <button
                    type="submit"
                    className="glass-button-primary"
                    style={{ minWidth: "120px" }}
                    disabled={isSubmitting || !phoneNumber.trim()}
                    onClick={(e) => {
                      console.log("Button clicked, phoneNumber:", phoneNumber, "isSubmitting:", isSubmitting);
                      if (!phoneNumber.trim()) {
                        e.preventDefault();
                        setError("Please enter a phone number");
                      }
                    }}
                  >
                    {isSubmitting ? "Setting..." : "Set Number"}
                  </button>
                </div>
              </form>
            </div>
          </motion.div>
      )}
    </AnimatePresence>
  );
};
