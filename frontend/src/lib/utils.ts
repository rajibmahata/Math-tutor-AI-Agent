import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Merge Tailwind CSS classes with proper conflict resolution. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Format a duration in seconds to a human-readable string. */
export function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  if (mins === 0) return `${secs}s`;
  return `${mins} min ${secs}s`;
}

/** Format a date to a relative time string (e.g., "2 days ago"). */
export function timeAgo(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  return date.toLocaleDateString();
}

/** Get the grade display name. */
export function gradeDisplay(grade: string): string {
  const map: Record<string, string> = {
    N: "Nursery",
    KG: "Kindergarten",
    "1": "Class 1",
    "2": "Class 2",
    "3": "Class 3",
    "4": "Class 4",
    "5": "Class 5",
    "6": "Class 6",
    "7": "Class 7",
    "8": "Class 8",
    "9": "Class 9",
    "10": "Class 10",
  };
  return map[grade] || `Grade ${grade}`;
}

/** Truncate a string to a max length with ellipsis. */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength) + "...";
}

/** API base URL from environment. */
export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

/** API request helper with auth token. */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem("access_token");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}/api/v1${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}
