"use client";

import React, { useState, useEffect } from "react";
import { IntegrationCard, Integration } from "@/components/IntegrationCard";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const fetchIntegrations = async () => {
    try {
      setIsLoading(true);
      // Fetch available integrations and connected status
      const [available, connected] = await Promise.all([
        api.get<Array<{ provider: string; name: string }>>("/api/v1/integrations"),
        api.get<Array<{ id: string; provider: string }>>("/api/v1/integrations/connected"),
      ]);

      const connectedProviders = new Set(connected.map((i) => i.provider));

      const integrationsList: Integration[] = available.map((int) => ({
        id: int.provider,
        provider: int.provider,
        name: int.name,
        status: connectedProviders.has(int.provider)
          ? "connected"
          : "disconnected",
      }));

      setIntegrations(integrationsList);
    } catch (error) {
      console.error("Error fetching integrations:", error);
      // Fallback to default integrations if API fails
      setIntegrations([
        {
          id: "google",
          provider: "google",
          name: "Google Account",
          status: "disconnected",
        },
        {
          id: "notion",
          provider: "notion",
          name: "Notion",
          status: "disconnected",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnect = async (provider: string) => {
    try {
      // Initiate OAuth flow
      const response = await api.post<{ auth_url: string }>(
        `/api/v1/integrations/${provider}/authorize`
      );
      
      if (response.auth_url) {
        // For Google integrations, redirect to Google OAuth
        // After authorization, Google will redirect back to our callback
        window.location.href = response.auth_url;
      }
    } catch (error) {
      console.error(`Error connecting ${provider}:`, error);
    }
  };

  const handleDisconnect = async (integrationId: string) => {
    try {
      await api.delete(`/api/v1/integrations/${integrationId}`);
      // Refresh integrations list
      fetchIntegrations();
    } catch (error) {
      console.error(`Error disconnecting ${integrationId}:`, error);
    }
  };

  if (isLoading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "60vh" }}>
        <div className="body-base" style={{ color: "var(--text-secondary)" }}>Loading integrations...</div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: "3rem" }}>
        <h1 className="heading-2" style={{ color: "var(--text-primary)", marginBottom: "0.75rem" }}>Settings</h1>
        <p className="body-base" style={{ color: "var(--text-secondary)", lineHeight: "1.7" }}>
          Connect and manage your integrations
        </p>
      </div>

      {/* Integrations List - Each in its own card */}
      <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        {integrations.map((integration, index) => (
          <div
            key={integration.id}
            className="stagger-animate"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <IntegrationCard
              integration={integration}
              onConnect={() => handleConnect(integration.provider)}
              onDisconnect={() => handleDisconnect(integration.id)}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
