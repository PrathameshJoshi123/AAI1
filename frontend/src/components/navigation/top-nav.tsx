"use client";

import * as React from "react";
import Link from "next/link";
import { Bell, CheckCheck, Clock, ExternalLink, Shield } from "lucide-react";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { advisorService } from "@/services/advisor-service";
import { AppNotification } from "@/types/advisor";

interface TopNavProps {
  roleTitle?: string;
}

export function TopNav({ roleTitle = "Dashboard" }: TopNavProps) {
  const [unreadCount, setUnreadCount] = React.useState<number>(0);
  const [notifications, setNotifications] = React.useState<AppNotification[]>([]);
  const [isOpen, setIsOpen] = React.useState(false);

  const fetchNotifications = React.useCallback(async () => {
    try {
      const res = await advisorService.getNotifications();
      if (res && typeof res.unread_count === "number") {
        setUnreadCount(res.unread_count);
        setNotifications(res.items || []);
      }
    } catch {
      // Ignored for unauthenticated routes or temporary network drops
    }
  }, []);

  // Event loop: Poll for new notifications every 5 seconds
  React.useEffect(() => {
    fetchNotifications();
    const intervalId = setInterval(fetchNotifications, 5000);
    return () => clearInterval(intervalId);
  }, [fetchNotifications]);

  const handleMarkRead = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await advisorService.markNotificationRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch (err) {
      console.error("Failed to mark read:", err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await advisorService.markAllNotificationsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error("Failed to mark all read:", err);
    }
  };

  return (
    <header className="sticky top-0 z-30 flex h-14 w-full items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur-xs">
      <div className="flex items-center gap-3">
        <SidebarTrigger />
        <div className="hidden h-4 w-px bg-slate-200 sm:block" />
        <span className="text-sm font-semibold text-slate-800">{roleTitle}</span>
      </div>

      <div className="flex items-center gap-2">
        <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="relative h-8 w-8 text-slate-600">
              <Bell className="h-4 w-4" />
              <span className="sr-only">Notifications</span>
              {unreadCount > 0 ? (
                <span className="absolute -top-1 -right-1 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-rose-600 px-1 text-[10px] font-bold text-white shadow-xs animate-pulse">
                  {unreadCount > 9 ? "9+" : unreadCount}
                </span>
              ) : (
                <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-emerald-500" />
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-88 max-h-[460px] overflow-hidden flex flex-col p-0">
            <DropdownMenuLabel className="flex items-center justify-between py-2.5 px-3 bg-slate-50 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-slate-900">Notifications</span>
                <span className="inline-flex items-center gap-1 rounded bg-blue-50 px-1.5 py-0.5 text-[10px] font-medium text-blue-700">
                  <span className="h-1.5 w-1.5 rounded-full bg-blue-600 animate-ping" />
                  Live (5s)
                </span>
              </div>
              {unreadCount > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleMarkAllRead}
                  className="h-6 text-[11px] px-2 text-slate-600 hover:text-slate-900"
                >
                  <CheckCheck className="h-3 w-3 mr-1" />
                  Mark all read
                </Button>
              )}
            </DropdownMenuLabel>
            
            <div className="overflow-y-auto divide-y divide-slate-100 max-h-[380px]">
              {notifications.length === 0 ? (
                <div className="p-6 text-center text-xs text-slate-500">
                  No alerts or notifications yet.
                </div>
              ) : (
                notifications.slice(0, 10).map((n) => (
                  <div
                    key={n.id}
                    className={`p-3 text-xs transition-colors hover:bg-slate-50 ${
                      !n.is_read ? "bg-blue-50/30" : "bg-white"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <span className={`font-semibold ${!n.is_read ? "text-blue-900" : "text-slate-900"}`}>
                        {n.title}
                      </span>
                      {!n.is_read && (
                        <button
                          type="button"
                          onClick={(e) => handleMarkRead(n.id, e)}
                          className="text-[10px] text-blue-600 hover:underline shrink-0"
                        >
                          Mark read
                        </button>
                      )}
                    </div>
                    <p className="text-[11px] text-slate-600 line-clamp-2 mt-0.5">{n.message}</p>
                    <div className="flex items-center justify-between mt-1 text-[10px] text-slate-400">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                      {n.link_url && (
                        <Link
                          href={n.link_url}
                          onClick={() => setIsOpen(false)}
                          className="text-blue-600 hover:underline flex items-center gap-0.5"
                        >
                          Open <ExternalLink className="h-2.5 w-2.5" />
                        </Link>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </DropdownMenuContent>
        </DropdownMenu>

        <div className="hidden md:flex items-center text-xs text-slate-500 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded-md">
          <Shield className="h-3.5 w-3.5 mr-1.5 text-primary" />
          <span>AES-256 Encrypted</span>
        </div>
      </div>
    </header>
  );
}


