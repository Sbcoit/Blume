/* Console page
 * After login, user lands here to:
 * - Set the phone number the agent should message.
 * - Configure tools / API keys (starting with Google Calendar).
 * Backend calls are stubbed; you can wire them to real endpoints later.
 */
"use client";

import { FormEvent, useState } from "react";
import Button from "@/components/UI/Button";
import { useRouter } from "next/navigation";
import { registerPhoneNumber } from "@/services/agentService";

type TabId = "phone" | "tools";

type ToolId = "google-calendar" | "placeholder";

type CountryCode = "US" | "GB";

interface ToolConfig {
  id: ToolId;
  name: string;
  description: string;
  accentClass: string;
  fieldsComponent?: React.ComponentType;
}

// Simple console with two tabs: Phone and Tools, inside a single card.
export default function ConsolePage() {
  const [activeTab, setActiveTab] = useState<TabId>("phone");
  const router = useRouter();

  return (
    <div className="space-y-6">
      <header className="flex items-end justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">
            Blume Console
          </h1>
          <p className="text-sm text-text-muted">
            Set the phone number your agent talks to and wire up its tools.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push("/executions")}
            className="text-xs"
          >
            Executions
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push("/")}
            className="text-xs"
          >
            Log out
          </Button>
        </div>
      </header>

      <ConsoleCard>
        <div className="mb-4 inline-flex rounded-full border border-border/60 bg-background/60 p-1 text-xs">
          <button
            type="button"
            onClick={() => setActiveTab("phone")}
            className={`rounded-full px-4 py-1 transition ${
              activeTab === "phone"
                ? "bg-accent text-black"
                : "text-text-muted hover:text-text-main"
            }`}
          >
            Phone number
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("tools")}
            className={`rounded-full px-4 py-1 transition ${
              activeTab === "tools"
                ? "bg-accent text-black"
                : "text-text-muted hover:text-text-main"
            }`}
          >
            Tools
          </button>
        </div>

        {activeTab === "phone" ? <PhoneSection /> : <ToolsSection />}
      </ConsoleCard>
    </div>
  );
}

function PhoneSection() {
  const [agentName, setAgentName] = useState("");
  const [phone, setPhone] = useState("");
  const [country, setCountry] = useState<CountryCode>("US");
  const [status, setStatus] = useState<"idle" | "sending" | "sent">("idle");
   const [error, setError] = useState<string | null>(null);
  const [countryMenuOpen, setCountryMenuOpen] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!phone) {
      setError("Please enter a phone number.");
      return;
    }

    const normalized = normalizePhone(phone, country);
    if (!normalized) {
      setError(
        "That doesn’t look like a valid number for the selected country. Check the digits and try again."
      );
      return;
    }

    setStatus("sending");

    try {
      await registerPhoneNumber({
        agentName: agentName || "Unnamed agent",
        phone: normalized,
      });
      setStatus("sent");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to send confirmation message. Please try again."
      );
      setStatus("idle");
    }
  }

  return (
    <section className="space-y-3">
      <h2 className="text-sm font-semibold text-text-main">
        Phone number to connect
      </h2>
      <p className="mt-1 text-xs text-text-muted">
        The agent will send a one-time message to confirm it&apos;s connected
        to this number.
      </p>

      <form onSubmit={handleSubmit} className="mt-4 space-y-3 text-sm">
        <div className="space-y-1">
          <label className="text-xs text-text-muted">Agent name</label>
          <input
            type="text"
            value={agentName}
            onChange={(e) => setAgentName(e.target.value)}
            className="w-full rounded-lg border border-border/70 bg-background px-3 py-2 text-sm text-text-main outline-none ring-0 focus:border-accent"
            placeholder="e.g. Blume, Calendar Copilot"
          />
        </div>
        <div className="space-y-1">
          <label className="text-xs text-text-muted">Phone number</label>
          <div className="relative flex items-stretch rounded-lg border border-border/70 bg-background">
            <div className="relative flex items-center">
              <button
                type="button"
                onClick={() => setCountryMenuOpen((o) => !o)}
                className="flex h-full items-center gap-1 border-r border-border/60 bg-surface/80 px-2.5 text-[11px] text-text-main outline-none ring-0 focus:outline-none focus:ring-0 active:scale-[0.97] transition-transform"
              >
                <span>
                  {country === "US" ? "+1 US" : "+44 UK"}
                </span>
                <span className="text-[9px]">▾</span>
              </button>
              {countryMenuOpen && (
                <div className="absolute left-0 top-full z-20 mt-1 w-28 rounded-lg border border-border/70 bg-surface/95 py-1 text-[11px] shadow-elevated">
                  <button
                    type="button"
                    className="flex w-full items-center justify-between px-2 py-1 text-left hover:bg-background/80"
                    onClick={() => {
                      setCountry("US");
                      setError(null);
                      setCountryMenuOpen(false);
                    }}
                  >
                    <span>+1</span>
                    <span className="text-text-muted">US</span>
                  </button>
                  <button
                    type="button"
                    className="flex w-full items-center justify-between px-2 py-1 text-left hover:bg-background/80"
                    onClick={() => {
                      setCountry("GB");
                      setError(null);
                      setCountryMenuOpen(false);
                    }}
                  >
                    <span>+44</span>
                    <span className="text-text-muted">UK</span>
                  </button>
                </div>
              )}
            </div>
            <input
              type="tel"
              required
              value={formatPhoneForDisplay(phone, country)}
              onChange={(e) => {
                const digitsOnly = e.target.value.replace(/[^\d]/g, "");
                setPhone(digitsOnly);
              }}
              className="flex-1 bg-transparent px-3 py-2 text-sm text-text-main outline-none ring-0 focus:border-accent"
              placeholder={
                country === "US" ? "555-123-4567" : "7123-456-789" // simple examples
              }
            />
          </div>
        </div>
        {error && (
          <p className="text-xs text-status-error">
            {error}
          </p>
        )}
        <Button
          type="submit"
          variant="primary"
          size="md"
          className="mt-1"
          disabled={status === "sending"}
        >
          {status === "sending" ? "Sending…" : "Set number"}
        </Button>
      </form>

      {status === "sent" && (
        <p className="mt-3 text-xs text-status-success">
          Confirmation message sent to{" "}
          {country === "US" ? `+1-${formatPhoneForDisplay(phone, country)}` : `+44-${formatPhoneForDisplay(phone, country)}`}
          . Once you wire the backend, this
          will reflect the real delivery status.
        </p>
      )}
    </section>
  );
}

function ToolsSection() {
  // Tool registry: map tool IDs to their field components
  const toolFieldsRegistry: Record<string, React.ComponentType> = {
    "google-calendar": GoogleCalendarFields
    
    // Add more tools here as you create them:
    // "slack": SlackFields,
    // "email": EmailFields,
  };

  const tools: ToolConfig[] = [
    {
      id: "google-calendar",
      name: "Google Calendar",
      description: "Let the agent read/create events on specific calendars.",
      accentClass: "from-blue-500/20 to-blue-500/5",
      fieldsComponent: GoogleCalendarFields
    },
    {
      id: "placeholder",
      name: "Add another tool",
      description:
        "When you're ready, mirror this for Slack, email, internal APIs, and more.",
      accentClass: "from-emerald-500/20 to-emerald-500/5"
    }
  ];

  return (
    <section className="space-y-4">
      <header className="space-y-1">
        <h2 className="text-sm font-semibold text-text-main">Tools</h2>
        <p className="text-xs text-text-muted">
          Configure what your agent is allowed to access. Start with Google
          Calendar; add more later.
        </p>
      </header>

      <div className="max-h-[calc(100vh-350px)] min-h-0 overflow-y-auto rounded-xl bg-background/25 backdrop-blur-xl pr-2">
        <div className="space-y-3 p-3">
          {tools.map((tool) => {
            const FieldsComponent = tool.fieldsComponent || toolFieldsRegistry[tool.id];
            
            return (
              <ToolCard key={tool.id} tool={tool}>
                {FieldsComponent ? (
                  <FieldsComponent />
                ) : (
                  <p className="text-xs text-text-muted">
                    This is just a placeholder. To add a real tool, create a fields component
                    and add it to the tools array with a fieldsComponent property.
                  </p>
                )}
              </ToolCard>
            );
          })}
        </div>
      </div>
    </section>
  );
}

// Very small helper to normalize a phone number toward E.164 for US-style inputs.
// In a production app, prefer a library like libphonenumber-js.
function normalizePhone(raw: string, country: CountryCode): string | null {
  const digits = raw.replace(/[^\d]/g, "");
  if (country === "US") {
    if (digits.length === 10) return `+1${digits}`;
    if (digits.length === 11 && digits.startsWith("1")) return `+${digits}`;
    return null;
  }

  if (country === "GB") {
    // Very lightweight UK handling: expect 10 or 11 digits and prepend +44.
    if (digits.length === 10 || digits.length === 11) {
      // Remove leading 0 if present (common in local formats).
      const local = digits.startsWith("0") ? digits.slice(1) : digits;
      return `+44${local}`;
    }
    return null;
  }

  return null;
}

// Lightweight formatter to show dashes as the user types, based on country.
function formatPhoneForDisplay(digitsOnly: string, country: CountryCode): string {
  const digits = digitsOnly.replace(/[^\d]/g, "");
  if (country === "US") {
    if (digits.length <= 3) return digits;
    if (digits.length <= 6) {
      return `${digits.slice(0, 3)}-${digits.slice(3)}`;
    }
    return `${digits.slice(0, 3)}-${digits.slice(3, 6)}-${digits.slice(6, 10)}`;
  }

  if (country === "GB") {
    // Very rough grouping for readability, not a full UK formatter.
    if (digits.length <= 4) return digits;
    if (digits.length <= 7) {
      return `${digits.slice(0, 4)}-${digits.slice(4)}`;
    }
    return `${digits.slice(0, 4)}-${digits.slice(4, 7)}-${digits.slice(7, 11)}`;
  }

  return digits;
}

function ToolCard({
  tool,
  children
}: {
  tool: ToolConfig;
  children: React.ReactNode;
}) {
  return (
    <div className="relative overflow-hidden rounded-xl border border-border/35 bg-background/25 p-4 text-xs backdrop-blur-xl shadow-elevated">
      <div
        className={`pointer-events-none absolute inset-0 bg-gradient-to-br ${tool.accentClass} opacity-60`}
      />
      <div className="relative space-y-2">
        <div className="text-[11px] uppercase tracking-[0.16em] text-text-muted">
          {tool.name}
        </div>
        <p className="text-xs text-text-muted">{tool.description}</p>
        {children}
      </div>
    </div>
  );
}

function GoogleCalendarFields() {
  const router = useRouter();
  
  return (
    <div className="mt-2 space-y-2">
      <div className="space-y-1">
        <label className="text-[11px] text-text-muted">
          API key / credentials
        </label>
        <input
          type="password"
          className="w-full rounded-lg border border-border/70 bg-surface px-3 py-2 text-xs text-text-main outline-none ring-0 focus:border-accent"
          placeholder="Paste service account JSON or token"
        />
      </div>
      <div className="space-y-1">
        <label className="text-[11px] text-text-muted">
          Allowed calendars (comma separated)
        </label>
        <input
          type="text"
          className="w-full rounded-lg border border-border/70 bg-surface px-3 py-2 text-xs text-text-main outline-none ring-0 focus:border-accent"
          placeholder="primary, team@company.com, ..."
        />
      </div>
      <div className="flex items-center justify-between gap-2 pt-1">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() =>
            console.log("[agent] save google calendar tool config (stub)")
          }
          className="text-[11px]"
        >
          Save settings
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => router.push("/calendar")}
          className="text-[11px] text-text-muted hover:text-text-main"
        >
          Manage calendars →
        </Button>
      </div>
    </div>
  );
}

function ConsoleCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-border/40 bg-transparent p-5 shadow-elevated backdrop-blur-2xl">
      {children}
    </div>
  );
}

