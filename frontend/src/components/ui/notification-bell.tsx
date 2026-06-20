"use client";

import { useEffect, useState, useCallback } from "react";

const API = "http://localhost:8000/api/v1";

interface Notification {
  id: string;
  type: string;
  priority: string;
  title: string;
  body: string;
  action_url?: string;
  is_read: boolean;
  created_at: string;
}

interface NotificationBellProps {
  /** Number of pixels for the bell icon size (default 20) */
  size?: number;
}

export function NotificationBell({ size = 20 }: NotificationBellProps) {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchNotifications = useCallback(async () => {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/notifications?limit=20`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setNotifications(data.data || []);
        setUnreadCount(data.unread_count || 0);
      }
    } catch {
      // Silently fail — notifications are non-critical
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
    // Poll every 60 seconds for new notifications
    const timer = setInterval(fetchNotifications, 60_000);
    return () => clearInterval(timer);
  }, [fetchNotifications]);

  const markRead = async (id: string) => {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    try {
      await fetch(`${API}/notifications/${id}/read`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch {}
  };

  const markAllRead = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    try {
      await fetch(`${API}/notifications/read-all`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch {}
  };

  const priorityColor: Record<string, string> = {
    urgent: "bg-red-100 border-red-300",
    high: "bg-orange-50 border-orange-200",
    medium: "bg-blue-50 border-blue-200",
    low: "bg-gray-50 border-gray-200",
  };

  return (
    <div className="relative">
      {/* Bell Button */}
      <button
        onClick={() => {
          setOpen((o) => !o);
          if (!open) fetchNotifications();
        }}
        className="relative p-1 rounded-full hover:bg-white/20 transition"
        aria-label="Notifications"
      >
        <svg
          width={size}
          height={size}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] font-bold rounded-full min-w-[16px] h-4 flex items-center justify-center px-1">
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown Panel */}
      {open && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-80 bg-white rounded-2xl shadow-xl border border-gray-100 z-50 overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
              <h3 className="font-semibold text-gray-800 text-sm">Notifications</h3>
              <div className="flex items-center gap-2">
                {unreadCount > 0 && (
                  <button
                    onClick={markAllRead}
                    className="text-xs text-blue-600 hover:underline"
                  >
                    Mark all read
                  </button>
                )}
                <span className="text-xs text-gray-400">{unreadCount} unread</span>
              </div>
            </div>

            {/* List */}
            <div className="max-h-80 overflow-y-auto divide-y divide-gray-50">
              {loading && (
                <div className="py-6 text-center text-sm text-gray-400">
                  Loading…
                </div>
              )}
              {!loading && notifications.length === 0 && (
                <div className="py-8 text-center">
                  <span className="text-2xl">🔔</span>
                  <p className="text-sm text-gray-400 mt-2">No notifications yet</p>
                </div>
              )}
              {notifications.map((n) => (
                <button
                  key={n.id}
                  onClick={() => {
                    markRead(n.id);
                    if (n.action_url) window.location.href = n.action_url;
                  }}
                  className={`w-full text-left px-4 py-3 hover:bg-gray-50 transition border-l-2 ${
                    n.is_read ? "border-transparent opacity-60" : priorityColor[n.priority] || "border-blue-200"
                  }`}
                >
                  <p className={`text-xs font-semibold ${n.is_read ? "text-gray-500" : "text-gray-800"}`}>
                    {n.title}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{n.body}</p>
                  <p className="text-[10px] text-gray-400 mt-1">
                    {new Date(n.created_at).toLocaleString()}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
