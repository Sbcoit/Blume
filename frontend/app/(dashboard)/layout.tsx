"use client";

import React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Home, ListTodo, Settings, LogOut } from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    // Clear token from localStorage
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
    }
    // Redirect to login page
    router.push("/login");
  };

  const tabs = [
    { name: "Home", href: "/", icon: Home },
    { name: "Tasks", href: "/tasks", icon: ListTodo },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <div style={{ 
      minHeight: "100vh", 
      display: "flex", 
      flexDirection: "column",
      backgroundColor: "transparent",
      width: "100%",
      position: "relative"
    }}>
      {/* Tab Navigation */}
      <nav 
        className="glass" 
        style={{ 
          borderBottom: "1px solid var(--border-primary)",
          position: "sticky",
          top: 0,
          zIndex: 30,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "1rem",
          padding: "0.5rem var(--space-lg)",
          paddingLeft: "var(--space-xl)",
          width: "100%"
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          {/* Blume Logo/Text */}
          <div style={{
            fontSize: "1.25rem",
            fontWeight: 700,
            color: "var(--text-primary)",
            letterSpacing: "-0.02em"
          }}>
            Blume
          </div>
          
          {tabs.map((tab) => {
            const isActive = pathname === tab.href;
            const Icon = tab.icon;
            return (
              <Link
                key={tab.href}
                href={tab.href}
                style={{
                  position: "relative",
                  padding: "1rem 1.5rem",
                  fontWeight: 500,
                  fontSize: "0.875rem",
                  transition: "all 300ms cubic-bezier(0.4, 0, 0.2, 1)",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                  borderRadius: "0.5rem",
                  color: isActive ? "var(--text-primary)" : "var(--text-secondary)",
                  backgroundColor: "transparent",
                  textDecoration: "none"
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.color = "var(--text-primary)";
                    e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.05)";
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = "transparent";
                  if (!isActive) {
                    e.currentTarget.style.color = "var(--text-secondary)";
                  }
                }}
              >
                {isActive && (
                  <span
                    style={{
                      position: "absolute",
                      bottom: 0,
                      left: 0,
                      right: 0,
                      height: "2px",
                      borderRadius: "9999px",
                      background: "var(--accent-blue)",
                    }}
                  />
                )}
                <Icon size={18} />
                <span>{tab.name}</span>
              </Link>
            );
          })}
        </div>

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
            padding: "0.75rem 1.25rem",
            fontWeight: 500,
            fontSize: "0.875rem",
            color: "var(--text-secondary)",
            background: "transparent",
            border: "none",
            borderRadius: "0.5rem",
            cursor: "pointer",
            transition: "all 300ms cubic-bezier(0.4, 0, 0.2, 1)"
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = "var(--text-primary)";
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.05)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = "var(--text-secondary)";
            e.currentTarget.style.backgroundColor = "transparent";
          }}
        >
          <LogOut size={18} />
          <span>Log out</span>
        </button>
      </nav>

      {/* Main Content */}
      <main style={{
        flex: "1 1 auto",
        maxWidth: "1280px",
        margin: "0 auto",
        padding: "2.5rem var(--space-lg)",
        width: "100%",
        overflow: "visible"
      }}>
        <div style={{
          maxWidth: "896px",
          margin: "0 auto",
          width: "100%",
          minHeight: "0"
        }}>
          {children}
        </div>
      </main>
    </div>
  );
}
