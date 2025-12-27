"use client";

import React, { useState, useEffect } from "react";
import { PhoneModal } from "@/components/PhoneModal";
import { api } from "@/lib/api";

export default function HomePage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState<string | null>(null);
  const [agentName, setAgentName] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Fetch current user data
    const fetchUserData = async () => {
      try {
        const user = await api.get<{
          phone_number?: string;
          agent_name?: string;
        }>("/api/v1/users/me");
        
        if (user.phone_number) {
          setPhoneNumber(user.phone_number);
        }
        if (user.agent_name) {
          setAgentName(user.agent_name);
        } else {
          // If no phone number is set, show modal
          setIsModalOpen(true);
        }
      } catch (error) {
        console.error("Error fetching user data:", error);
        // Show modal on error as well
        setIsModalOpen(true);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserData();
  }, []);

  const handleSetNumber = async (phone: string, name?: string) => {
    try {
      await api.patch("/api/v1/users/me", {
        phone_number: phone,
        agent_name: name,
      });
      setPhoneNumber(phone);
      if (name) {
        setAgentName(name);
      }
    } catch (error) {
      console.error("Error setting phone number:", error);
      throw error;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="body-base text-secondary">Loading...</div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="glass-card">
        <h1 className="heading-2 mb-4">
          Welcome to Blume{agentName ? `, ${agentName}` : ""}
        </h1>
        <p className="body-base text-secondary mb-8">
          Your personal secretary agent is ready to help with scheduling,
          workflows, research, and more.
        </p>

        {phoneNumber ? (
          <div className="space-y-4">
            <div>
              <p className="body-small text-secondary mb-2">
                Connected Phone Number
              </p>
              <p className="body-large">{phoneNumber}</p>
            </div>
            <button
              onClick={() => setIsModalOpen(true)}
              className="glass-button"
            >
              Update Phone Number
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="body-base text-secondary">
              Get started by setting up your phone number for iMessage
              communication.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="glass-button-primary"
            >
              Set Up Phone Number
            </button>
          </div>
        )}
      </div>

      <PhoneModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSetNumber={handleSetNumber}
        currentPhoneNumber={phoneNumber || ""}
        currentAgentName={agentName || ""}
      />
    </div>
  );
}

