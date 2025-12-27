"use client";

import React, { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const result = await signIn("credentials", {
        email,
        password,
        redirect: false,
      });

      if (result?.error) {
        setError("Invalid email or password");
      } else {
        router.push("/");
      }
    } catch (err) {
      setError("An error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "var(--space-lg)"
    }}>
      <div className="glass-modal" style={{ maxWidth: "28rem", width: "100%" }}>
        <h1 className="heading-2" style={{ color: "var(--text-primary)", marginBottom: "0.5rem" }}>
          Welcome to Blume
        </h1>
        <p className="body-base" style={{ color: "var(--text-secondary)", marginBottom: "2rem" }}>
          Sign in to your account
        </p>

        {error && (
          <div style={{
            marginBottom: "1.5rem",
            padding: "1rem",
            borderRadius: "var(--radius-md)",
            backgroundColor: "rgba(239, 68, 68, 0.15)",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            color: "#EF4444"
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <div>
            <label
              htmlFor="email"
              className="body-small"
              style={{
                color: "var(--text-secondary)",
                marginBottom: "0.75rem",
                display: "block",
                fontWeight: 500
              }}
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{ width: "100%" }}
              disabled={isLoading}
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="body-small"
              style={{
                color: "var(--text-secondary)",
                marginBottom: "0.75rem",
                display: "block",
                fontWeight: 500
              }}
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{ width: "100%" }}
              disabled={isLoading}
            />
          </div>

          <button
            type="submit"
            className="glass-button-primary"
            style={{ width: "100%" }}
            disabled={isLoading}
          >
            {isLoading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <div style={{ marginTop: "1.5rem", textAlign: "center" }}>
          <p className="body-small" style={{ color: "var(--text-secondary)" }}>
            Don't have an account?{" "}
            <Link
              href="/signup"
              style={{
                color: "var(--accent-blue)",
                textDecoration: "none",
                transition: "opacity var(--transition-fast)"
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.opacity = "0.8";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.opacity = "1";
              }}
            >
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

