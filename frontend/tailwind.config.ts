import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        // Apple-like system font stack for a clean native feel
        display: [
          "-apple-system",
          "BlinkMacSystemFont",
          "system-ui",
          "Segoe UI",
          "sans-serif"
        ],
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "system-ui",
          "Segoe UI",
          "sans-serif"
        ]
      },
      colors: {
        background: "rgb(var(--bg-root) / <alpha-value>)",
        surface: "rgb(var(--bg-elevated) / <alpha-value>)",
        accent: "rgb(var(--accent) / <alpha-value>)",
        "accent-soft": "rgb(var(--accent-soft) / <alpha-value>)",
        border: "rgb(var(--border-subtle) / <alpha-value>)",
        text: {
          main: "rgb(var(--text-main) / <alpha-value>)",
          muted: "rgb(var(--text-muted) / <alpha-value>)"
        },
        status: {
          success: "#36e9b0",
          pending: "#facc15",
          error: "#fb7185",
          running: "#38bdf8"
        }
      },
      borderRadius: {
        xl: "1.25rem"
      },
      boxShadow: {
        elevated: "0 24px 80px rgba(0,0,0,0.65)"
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" }
        }
      },
      animation: {
        "fade-up": "fade-up 0.6s ease-out forwards"
      }
    }
  },
  plugins: []
};

export default config;


