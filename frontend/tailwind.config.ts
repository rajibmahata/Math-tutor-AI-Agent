import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#EEF2FF",
          100: "#E0E7FF",
          200: "#C7D2FE",
          300: "#A5B4FC",
          400: "#818CF8",
          500: "#6366F1",
          600: "#4F46E5",
          700: "#4338CA",
          800: "#3730A3",
          900: "#312E81",
        },
        success: {
          50: "#ECFDF5",
          500: "#10B981",
          600: "#059669",
        },
        warning: {
          50: "#FFFBEB",
          500: "#F59E0B",
          600: "#D97706",
        },
        error: {
          50: "#FEF2F2",
          500: "#EF4444",
          600: "#DC2626",
        },
      },
      fontFamily: {
        heading: ["Nunito", "Noto Sans Devanagari", "Noto Sans Bengali", "sans-serif"],
        body: ["Inter", "Noto Sans Devanagari", "Noto Sans Bengali", "sans-serif"],
        math: ["KaTeX_Main", "KaTeX_Math", "serif"],
      },
      borderRadius: {
        xl: "0.75rem",
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
      animation: {
        "bounce-in": "bounceIn 0.5s ease-out",
        "confetti": "confetti 1s ease-out forwards",
        "pulse-glow": "pulseGlow 2s ease-in-out infinite",
      },
      keyframes: {
        bounceIn: {
          "0%": { transform: "scale(0.3)", opacity: "0" },
          "50%": { transform: "scale(1.05)" },
          "70%": { transform: "scale(0.9)" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
        pulseGlow: {
          "0%, 100%": { boxShadow: "0 0 0 0 rgba(79, 70, 229, 0.4)" },
          "50%": { boxShadow: "0 0 20px 10px rgba(79, 70, 229, 0)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
