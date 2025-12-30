"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { PhoneModal } from "@/components/PhoneModal";
import { api } from "@/lib/api";
import DashboardLayout from "./(dashboard)/layout";

export default function Home() {
  const router = useRouter();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState<string | null>(null);
  const [agentName, setAgentName] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    // Check authentication first
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    
    if (!token) {
      router.push("/login");
      return;
    }
    
    setIsAuthenticated(true);
    
    const fetchUserData = async () => {
      try {
        // Always show modal
        setIsModalOpen(true);
      } catch (error) {
        console.error("Error fetching user data:", error);
        setIsModalOpen(true);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserData();
  }, [router]);
  
  // Don't render if not authenticated
  if (isAuthenticated === null || !isAuthenticated) {
    return (
      <div style={{ 
        minHeight: "100vh", 
        display: "flex", 
        alignItems: "center", 
        justifyContent: "center" 
      }}>
        <div className="body-base" style={{ color: "var(--text-secondary)" }}>
          Loading...
        </div>
      </div>
    );
  }

  const handleSetNumber = async (phone: string, name?: string) => {
    try {
      setPhoneNumber(phone);
      if (name) {
        setAgentName(name);
      }
      // Don't close the modal after setting - keep it open
      // setIsModalOpen(false);
    } catch (error) {
      console.error("Error setting phone number:", error);
      throw error;
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "60vh" }}>
          <div className="body-base" style={{ color: "var(--text-secondary)" }}>Loading...</div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="animate-fade-in">
        <PhoneModal
          isOpen={isModalOpen}
          onClose={() => {}} // No-op since modal always stays open
          onSetNumber={handleSetNumber}
          currentPhoneNumber={phoneNumber || ""}
          currentAgentName={agentName || ""}
        />
      </div>
    </DashboardLayout>
  );
}
