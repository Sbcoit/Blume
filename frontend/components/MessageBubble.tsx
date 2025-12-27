"use client";

import React from "react";

interface MessageBubbleProps {
  message: string;
  isAgent?: boolean; // true for agent (blue), false for user (gray)
  className?: string;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isAgent = true,
  className = "",
}) => {
  const bubbleColor = isAgent ? "#007AFF" : "#2C2C2E";
  const textColor = "#FFFFFF";

  return (
    <div
      className={`message-bubble ${isAgent ? "message-bubble-agent" : "message-bubble-user"} ${className}`}
      style={{
        backgroundColor: bubbleColor,
        color: textColor,
        borderRadius: isAgent
          ? "18px 18px 4px 18px" // top-left: 18px, top-right: 18px, bottom-right: 4px, bottom-left: 18px (right-aligned with tail)
          : "18px 18px 18px 4px", // left-aligned with tail
        padding: "10px 16px",
        maxWidth: "75%",
        marginLeft: isAgent ? "auto" : "0",
        marginRight: isAgent ? "0" : "auto",
        marginBottom: "8px",
        position: "relative",
        boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
        wordWrap: "break-word",
        lineHeight: "1.4",
      }}
    >
      {/* Tail pointer */}
      {isAgent && (
        <div
          style={{
            position: "absolute",
            right: "-8px",
            bottom: "8px",
            width: "0",
            height: "0",
            borderLeft: `8px solid ${bubbleColor}`,
            borderTop: "8px solid transparent",
            borderBottom: "8px solid transparent",
          }}
        />
      )}
      {!isAgent && (
        <div
          style={{
            position: "absolute",
            left: "-8px",
            bottom: "8px",
            width: "0",
            height: "0",
            borderRight: `8px solid ${bubbleColor}`,
            borderTop: "8px solid transparent",
            borderBottom: "8px solid transparent",
          }}
        />
      )}

      {/* Message content */}
      <div style={{ position: "relative", zIndex: 1 }}>
        {message}
      </div>

      <style jsx>{`
        .message-bubble {
          font-size: 16px;
          font-weight: 400;
          letter-spacing: -0.01em;
        }

        .message-bubble-agent {
          /* Additional agent-specific styles if needed */
        }

        .message-bubble-user {
          /* Additional user-specific styles if needed */
        }
      `}</style>
    </div>
  );
};

