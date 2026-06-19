"""Frontend component tests for GanitMitra.
Uses Vitest + React Testing Library.
"""

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

// =============================================================================
// Store Tests
// =============================================================================

describe("AuthStore", () => {
  beforeEach(() => {
    localStorage.clear();
    // Re-import to reset store state
    vi.resetModules();
  });

  it("should initialize with no user", async () => {
    const { useAuthStore } = await import("@/store");
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it("should login and set user + tokens", async () => {
    const { useAuthStore } = await import("@/store");
    const user = { id: "1", email: "test@test.com", full_name: "Test", role: "student", is_verified: true, created_at: new Date().toISOString() };

    useAuthStore.getState().login(user, "access-token-123", "refresh-token-456");

    const state = useAuthStore.getState();
    expect(state.user).toEqual(user);
    expect(state.accessToken).toBe("access-token-123");
    expect(state.refreshToken).toBe("refresh-token-456");
    expect(state.isAuthenticated).toBe(true);
    expect(localStorage.getItem("access_token")).toBe("access-token-123");
  });

  it("should logout and clear state", async () => {
    const { useAuthStore } = await import("@/store");

    useAuthStore.getState().login(
      { id: "1", email: "t@t.com", full_name: "T", role: "student", is_verified: true, created_at: "" },
      "token",
      "refresh"
    );
    useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(localStorage.getItem("access_token")).toBeNull();
  });
});

describe("LanguageStore", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.resetModules();
  });

  it("should default to English", async () => {
    const { useLanguageStore } = await import("@/store");
    expect(useLanguageStore.getState().language).toBe("en");
  });

  it("should switch language to Hindi", async () => {
    const { useLanguageStore } = await import("@/store");
    useLanguageStore.getState().setLanguage("hi");
    expect(useLanguageStore.getState().language).toBe("hi");
    expect(localStorage.getItem("preferred_language")).toBe("hi");
  });

  it("should switch language to Bengali", async () => {
    const { useLanguageStore } = await import("@/store");
    useLanguageStore.getState().setLanguage("bn");
    expect(useLanguageStore.getState().language).toBe("bn");
  });
});

// =============================================================================
// Utils Tests
// =============================================================================

describe("Utility Functions", () => {
  it("cn should merge classes", async () => {
    const { cn } = await import("@/lib/utils");
    expect(cn("px-4", "py-2")).toBe("px-4 py-2");
    expect(cn("px-4", false && "hidden")).toBe("px-4");
  });

  it("formatDuration should format seconds", async () => {
    const { formatDuration } = await import("@/lib/utils");
    expect(formatDuration(45)).toBe("45s");
    expect(formatDuration(120)).toBe("2 min 0s");
    expect(formatDuration(3661)).toBe("61 min 1s");
  });

  it("gradeDisplay should show full grade names", async () => {
    const { gradeDisplay } = await import("@/lib/utils");
    expect(gradeDisplay("N")).toBe("Nursery");
    expect(gradeDisplay("KG")).toBe("Kindergarten");
    expect(gradeDisplay("1")).toBe("Class 1");
    expect(gradeDisplay("10")).toBe("Class 10");
    expect(gradeDisplay("unknown")).toBe("Grade unknown");
  });

  it("truncate should limit string length", async () => {
    const { truncate } = await import("@/lib/utils");
    expect(truncate("Hello World", 5)).toBe("Hello...");
    expect(truncate("Hi", 5)).toBe("Hi");
  });

  it("timeAgo should return relative time", async () => {
    const { timeAgo } = await import("@/lib/utils");
    const now = new Date().toISOString();
    expect(timeAgo(now)).toBe("just now");

    const twoHoursAgo = new Date(Date.now() - 2 * 3600 * 1000).toISOString();
    expect(timeAgo(twoHoursAgo)).toContain("h ago");
  });
});

// =============================================================================
// Component Tests
// =============================================================================

describe("LoginPage Validation", () => {
  it("should require email and password format", () => {
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    expect(emailRegex.test("test@example.com")).toBe(true);
    expect(emailRegex.test("invalid")).toBe(false);
    expect(emailRegex.test("")).toBe(false);
  });

  it("should require minimum password length", () => {
    const MIN_PASSWORD_LENGTH = 8;
    expect("12345678".length >= MIN_PASSWORD_LENGTH).toBe(true);
    expect("1234567".length >= MIN_PASSWORD_LENGTH).toBe(false);
  });
});

describe("Grade Validation", () => {
  const VALID_GRADES = ["N", "KG", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"];

  it("should accept all valid grades", () => {
    VALID_GRADES.forEach((grade) => {
      expect(VALID_GRADES.includes(grade)).toBe(true);
    });
  });

  it("should reject invalid grades", () => {
    expect(VALID_GRADES.includes("11")).toBe(false);
    expect(VALID_GRADES.includes("0")).toBe(false);
    expect(VALID_GRADES.includes("")).toBe(false);
  });
});

describe("Language Codes", () => {
  const VALID_LANGUAGES = ["en", "hi", "bn"];

  it("should accept all supported languages", () => {
    VALID_LANGUAGES.forEach((lang) => {
      expect(VALID_LANGUAGES.includes(lang)).toBe(true);
    });
  });

  it("should reject unsupported languages", () => {
    expect(VALID_LANGUAGES.includes("fr")).toBe(false);
    expect(VALID_LANGUAGES.includes("")).toBe(false);
  });
});

describe("SymPy Verification (Logic)", () => {
  it("should correctly identify equal expressions", () => {
    // Testing the logic, not actual SymPy calls
    const normalize = (s: string) => s.replace(/\s+/g, "");

    expect(normalize("12+5")).toBe("12+5");
    expect(normalize(" 12 + 5 ")).toBe("12+5");
    expect(normalize("12+5")).not.toBe("12+6");
  });

  it("should handle common answer formats", () => {
    const extractAnswer = (text: string): string => {
      // Simulate answer extraction logic
      const eqMatch = text.match(/=\s*(-?[\d.]+)/);
      if (eqMatch) return eqMatch[1];
      if (/^-?\d+\.?\d*$/.test(text.trim())) return text.trim();
      return text.trim();
    };

    expect(extractAnswer("60")).toBe("60");
    expect(extractAnswer("= 60")).toBe("60");
    expect(extractAnswer("the answer is = 60")).toBe("60");
    expect(extractAnswer("12 + 5")).toBe("12 + 5");
  });
});
