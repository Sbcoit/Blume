"use client";

import React, { useState, useEffect } from "react";
import { PhoneModal } from "@/components/PhoneModal";
import { AgentInfoModal } from "@/components/AgentInfoModal";
import { api } from "@/lib/api";

export default function HomePage() {
  const [isSetupModalOpen, setIsSetupModalOpen] = useState(false);
  const [isInfoModalOpen, setIsInfoModalOpen] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState<string | null>(null);
  const [agentName, setAgentName] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Fetch current user data
    const fetchUserData = async () => {
      console.log("🔵 Starting to fetch user data...");
      try {
        console.log("🔵 Calling api.get('/api/v1/users/me')...");
        const user = await api.get<{
          phone_number?: string;
          agent_name?: string;
        }>("/api/v1/users/me");
        console.log("🔵 User data received:", user);
        
        if (user.phone_number) {
          setPhoneNumber(user.phone_number);
          // If phone number exists, show both modals
          setIsInfoModalOpen(true);
          setIsSetupModalOpen(false); // Don't show setup modal by default if phone is set
        } else {
          // If no phone number, show setup modal only
          setIsSetupModalOpen(true);
          setIsInfoModalOpen(false);
        }
        
        if (user.agent_name) {
          setAgentName(user.agent_name);
        }
      } catch (error: any) {
        console.error("❌ Error fetching user data:", error);
        console.error("Error details:", {
          message: error.message,
          status: error.status,
          response: error.response,
          name: error.name
        });
        // Show setup modal on error
        setIsSetupModalOpen(true);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserData();
  }, []);

  const handleSetNumber = async (phone: string, name?: string) => {
    console.log("handleSetNumber called with:", { phone, name });
    try {
      // If no name provided, use "Blume" as default
      const agentNameToSave = name?.trim() || "Blume";
      
      console.log("About to call api.patch with:", { 
        endpoint: "/api/v1/users/me", 
        data: { phone_number: phone, agent_name: agentNameToSave } 
      });
      
      const response = await api.patch<{
        phone_number?: string;
        agent_name?: string;
      }>("/api/v1/users/me", {
        phone_number: phone,
        agent_name: agentNameToSave,
      });
      
      console.log("PATCH response received:", response);
      console.log("Response fields:", {
        phone_number: response.phone_number,
        agent_name: response.agent_name,
        has_phone: !!response.phone_number,
        has_agent: !!response.agent_name
      });
      
      // Update state with response data
      const savedPhone = response.phone_number || phone;
      const savedAgent = response.agent_name || agentNameToSave;
      
      console.log("Setting state:", { savedPhone, savedAgent });
      setPhoneNumber(savedPhone);
      setAgentName(savedAgent);
      
      // Keep setup modal open, show info modal below it
      setIsSetupModalOpen(true);
      setIsInfoModalOpen(true);
      
      console.log("State updated, showing both modals");
    } catch (error: any) {
      console.error("ERROR in handleSetNumber:", error);
      console.error("Error details:", {
        message: error.message,
        status: error.status,
        response: error.response,
        stack: error.stack
      });
      throw error;
    }
  };

  const handleEdit = () => {
    // Open setup modal for editing (info modal stays visible below)
    setIsSetupModalOpen(true);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="body-base text-secondary">Loading...</div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in" style={{ position: "relative", width: "100%", height: "100%" }}>
      {/* Compact grid layout - side by side when both visible */}
      <div style={{
        display: "grid",
        gridTemplateColumns: phoneNumber && isInfoModalOpen ? "2fr 1fr" : "1fr",
        gap: "2rem",
        alignItems: "start",
        maxWidth: "1800px",
        width: "100%",
        margin: "0 auto",
        padding: "1.5rem",
        height: "100%"
      }}>
        {/* Setup Modal - shown when editing or no phone number is set */}
        {isSetupModalOpen && (
      <PhoneModal
            isOpen={isSetupModalOpen}
            onClose={() => setIsSetupModalOpen(false)}
        onSetNumber={handleSetNumber}
        currentPhoneNumber={phoneNumber || ""}
        currentAgentName={agentName || ""}
      />
        )}
        
        {/* Info Modal - shown when phone number is set */}
        {phoneNumber && isInfoModalOpen && (
          <AgentInfoModal
            isOpen={isInfoModalOpen}
            phoneNumber={phoneNumber}
            agentName={agentName}
            onEdit={handleEdit}
          />
        )}
      </div>
    </div>
  );
}

