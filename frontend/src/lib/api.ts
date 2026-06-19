"use client";

import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useAuthStore } from "@/store";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// =============================================================================
// API Client
// =============================================================================

interface ApiOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  isFormData?: boolean;
}

export async function apiCall<T = unknown>(
  endpoint: string,
  options: ApiOptions = {}
): Promise<T> {
  const { method = "GET", body, headers = {}, isFormData } = options;

  const token = typeof window !== "undefined"
    ? localStorage.getItem("access_token")
    : null;

  const requestHeaders: Record<string, string> = {
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...headers,
  };

  if (token) {
    requestHeaders["Authorization"] = `Bearer ${token}`;
  }

  const url = `${API_BASE}/api/v1${endpoint}`;

  const response = await fetch(url, {
    method,
    headers: requestHeaders,
    body: isFormData
      ? body as FormData
      : body
        ? JSON.stringify(body)
        : undefined,
  });

  if (!response.ok) {
    const error = await response.text();
    let message = `HTTP ${response.status}`;
    try {
      const parsed = JSON.parse(error);
      message = parsed.detail || parsed.title || message;
      if (parsed.errors) {
        message = parsed.errors.map((e: { message: string }) => e.message).join(", ");
      }
    } catch {}
    throw new Error(message);
  }

  // Handle no-content
  if (response.status === 204) return undefined as T;

  return response.json();
}

// =============================================================================
// Auth API
// =============================================================================

export async function authSignup(email: string, password: string, fullName: string, role: string) {
  return apiCall("/auth/signup", {
    method: "POST",
    body: { email, password, full_name: fullName, role },
  });
}

export async function authLogin(email: string, password: string) {
  return apiCall("/auth/login", {
    method: "POST",
    body: { email, password },
  });
}

// =============================================================================
// Student API
// =============================================================================

export async function createStudent(age: number, grade: string, language: string, board = "ncert") {
  return apiCall("/students", {
    method: "POST",
    body: { age, grade, preferred_language: language, board },
  });
}

export async function getStudent(studentId: string) {
  return apiCall(`/students/${studentId}`);
}

// =============================================================================
// Tutoring API
// =============================================================================

export async function startSession(type = "tutoring", language = "en", topicId?: string) {
  return apiCall("/tutoring/sessions", {
    method: "POST",
    body: { session_type: type, language, topic_id: topicId },
  });
}

export async function getSessionMessages(sessionId: string) {
  return apiCall(`/tutoring/sessions/${sessionId}/messages`);
}

// =============================================================================
// Practice API
// =============================================================================

export async function generatePractice(topicId?: string, difficulty = "adaptive", count = 10, language = "en") {
  return apiCall("/practice/generate", {
    method: "POST",
    body: { topic_id: topicId, difficulty, question_count: count, language },
  });
}

export async function submitPracticeAnswer(setId: string, questionNum: number, answer: string, timeTaken?: number) {
  return apiCall(`/practice/${setId}/questions/${questionNum}/answer`, {
    method: "POST",
    body: { answer, time_taken_seconds: timeTaken, hints_used: 0 },
  });
}

export async function completePractice(setId: string) {
  return apiCall(`/practice/${setId}/complete`, { method: "POST" });
}

// =============================================================================
// Progress API
// =============================================================================

export async function getProgress(studentId: string) {
  return apiCall(`/progress/${studentId}`);
}

export async function getAchievements(studentId: string) {
  return apiCall(`/achievements/${studentId}`);
}

// =============================================================================
// Voice API
// =============================================================================

export async function textToSpeech(text: string, language = "en", voiceStyle = "natural"): Promise<ArrayBuffer> {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api/v1/voice/tts`, {
    method: "POST",
    headers,
    body: JSON.stringify({ text, language, voice_style: voiceStyle }),
  });
  if (!res.ok) throw new Error("TTS failed");
  return res.arrayBuffer();
}

export async function speechToText(audioBlob: Blob, language?: string): Promise<{ text: string; language_detected: string }> {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.webm");
  if (language) formData.append("language", language);

  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api/v1/voice/stt`, {
    method: "POST",
    headers,
    body: formData,
  });
  if (!res.ok) throw new Error("STT failed");
  return res.json();
}
