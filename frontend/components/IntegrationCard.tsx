"use client";

import React from "react";
import { Settings, Calendar, StickyNote } from "lucide-react";


interface Integration {
  id: string;
  provider: string;
  name: string;
  status: "connected" | "disconnected" | "error";
  icon?: string;
}

interface IntegrationCardProps {
  integration: Integration;
  onConnect: () => void;
  onDisconnect: () => void;
}

const integrationIcons: Record<string, React.ElementType> = {
  google: Calendar,  // Using Calendar icon for unified Google Account
  notion: StickyNote,
};

const integrationDescriptions: Record<string, string> = {
  google: "Connect your Google account to access Calendar, Docs, and Drive for scheduling and document management.",
  notion: "Link your Notion workspace to create and manage notes, pages, and databases.",
};

const integrationColors: Record<string, { bg: string; bgSolid: string; border: string; icon: string }> = {
  google: {
    bg: "rgba(16, 185, 129, 0.12)",  // Subtle teal tint
    bgSolid: "rgba(16, 185, 129, 0.08)",  // Clean matte background
    border: "rgba(255, 255, 255, 0.1)",
    icon: "#10B981"  // Emerald/teal icon
  },
  notion: {
    bg: "rgba(139, 92, 246, 0.12)",  // Subtle purple tint
    bgSolid: "rgba(139, 92, 246, 0.08)",  // Clean matte background
    border: "rgba(255, 255, 255, 0.1)",
    icon: "#8B5CF6"  // Violet/purple icon
  },
};

const statusColors: Record<string, string> = {
  connected: "#66BB6A",
  disconnected: "#666",
  error: "#EF5350",
};

export const IntegrationCard: React.FC<IntegrationCardProps> = ({
  integration,
  onConnect,
  onDisconnect,
}) => {
  const IconComponent = integrationIcons[integration.provider] || Settings;
  const statusColor = statusColors[integration.status];
  const isConnected = integration.status === "connected";
  const colors = integrationColors[integration.provider] || {
    bg: "rgba(255, 255, 255, 0.05)",
    bgSolid: "rgba(20, 20, 20, 0.6)",
    border: "rgba(255, 255, 255, 0.1)",
    icon: "#FFFFFF"
  };

  return (
    <div 
      className="glass-card"
      style={{
        background: colors.bgSolid,
        border: `1px solid ${colors.border}`,
        backdropFilter: "none",
        WebkitBackdropFilter: "none",
        position: "relative",
        overflow: "hidden",
        boxShadow: "0 4px 16px rgba(0, 0, 0, 0.3)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%", position: "relative" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1.5rem", flex: 1 }}>
          {/* Icon */}
          <div style={{
            width: "4.5rem",
            height: "4.5rem",
            borderRadius: "0.75rem",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            backgroundColor: colors.bg,
            border: `1px solid ${colors.border}`,
            flexShrink: 0
          }}>
            <IconComponent size={32} style={{ color: colors.icon }} />
          </div>

          {/* Content */}
          <div style={{ flex: 1, minWidth: 0 }}>
            <h3 className="heading-3" style={{ color: "var(--text-primary)", marginBottom: "0.5rem" }}>{integration.name}</h3>
            
            {/* Description */}
            <p className="body-small" style={{ color: "var(--text-secondary)", marginBottom: "0.75rem", lineHeight: "1.5" }}>
              {integrationDescriptions[integration.provider] || "Connect this integration to enable additional features."}
            </p>
            
            {/* Status */}
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <div
                style={{
                  width: "0.5rem",
                  height: "0.5rem",
                  borderRadius: "50%",
                  backgroundColor: statusColor
                }}
              />
              <span className="body-small" style={{ color: "var(--text-secondary)", textTransform: "capitalize", fontWeight: 500 }}>{integration.status}</span>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div style={{ flexShrink: 0 }}>
          {isConnected ? (
            <button
              onClick={onDisconnect}
              className="glass-button"
            >
              Disconnect
            </button>
          ) : (
            <button
              onClick={onConnect}
              className="glass-button-primary"
            >
              Connect
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
