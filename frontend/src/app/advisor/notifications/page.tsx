"use client";

import * as React from "react";
import Link from "next/link";
import {
  Bell,
  CheckCheck,
  Clock,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  Info,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { advisorService } from "@/services/advisor-service";
import { AppNotification } from "@/types/advisor";

export default function AdvisorNotificationsPage() {
  const [notifications, setNotifications] = React.useState<AppNotification[]>([]);
  const [unreadCount, setUnreadCount] = React.useState(0);
  const [loading, setLoading] = React.useState(true);
  const [filter, setFilter] = React.useState("all");

  const loadNotifications = React.useCallback(async () => {
    try {
      setLoading(true);
      const res = await advisorService.getNotifications();
      setNotifications(res.items);
      setUnreadCount(res.unread_count);
    } catch (err) {
      console.error("Failed to load notifications:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadNotifications();
    const intervalId = setInterval(loadNotifications, 5000);
    return () => clearInterval(intervalId);
  }, [loadNotifications]);

  const handleMarkRead = async (id: number) => {
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

  const filtered = notifications.filter((n) => {
    if (filter === "unread") return !n.is_read;
    if (filter === "case_update") return n.notification_type === "case_update";
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <PageHeader
          title="Notification Center"
          description="Real-time alerts for case escalations, customer responses, SLA deadline countdowns, and document uploads."
          breadcrumbs={[
            { label: "Advisor Workbench", href: "/advisor" },
            { label: "Notifications" },
          ]}
        />
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <Button
            variant="outline"
            size="sm"
            onClick={loadNotifications}
            disabled={loading}
            className="h-9 gap-1.5 text-xs bg-white border-slate-200"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          {unreadCount > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleMarkAllRead}
              className="h-9 gap-1.5 text-xs bg-white border-slate-200 text-slate-700"
            >
              <CheckCheck className="h-3.5 w-3.5" />
              Mark All Read
            </Button>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between">
        <Tabs value={filter} onValueChange={setFilter}>
          <TabsList className="bg-slate-100 p-1 border border-slate-200 text-xs">
            <TabsTrigger value="all" className="text-xs">
              All Alerts ({notifications.length})
            </TabsTrigger>
            <TabsTrigger value="unread" className="text-xs">
              Unread ({unreadCount})
            </TabsTrigger>
            <TabsTrigger value="case_update" className="text-xs">
              Case Updates
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading notifications...</div>
      ) : filtered.length === 0 ? (
        <Card className="bg-white border-slate-200">
          <CardContent className="flex flex-col items-center justify-center p-12 text-center">
            <Bell className="h-10 w-10 text-slate-300 mb-2" />
            <p className="text-sm font-semibold text-slate-800">No Notifications</p>
            <p className="text-xs text-slate-400 max-w-sm mt-1">
              You are all caught up. New SLA alerts or case assignments will appear here.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2.5">
          {filtered.map((item) => (
            <Card
              key={item.id}
              className={`border transition-colors ${
                item.is_read
                  ? "bg-white border-slate-200"
                  : "bg-blue-50/40 border-blue-200 shadow-2xs"
              }`}
            >
              <CardContent className="p-4 flex items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div
                    className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${
                      item.is_read
                        ? "bg-slate-100 text-slate-500"
                        : "bg-blue-600 text-white shadow-xs"
                    }`}
                  >
                    <Bell className="h-4 w-4" />
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-xs text-slate-900">{item.title}</span>
                      {!item.is_read && (
                        <Badge variant="outline" className="bg-blue-600 text-white text-[10px] py-0 px-1 border-0">
                          NEW
                        </Badge>
                      )}
                      <Badge variant="outline" className="text-[10px] bg-white border-slate-200 text-slate-500">
                        {item.notification_type.replace(/_/g, " ").toUpperCase()}
                      </Badge>
                    </div>
                    <p className="text-xs text-slate-600">{item.message}</p>
                    <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
                      <Clock className="h-3 w-3" />
                      <span>{new Date(item.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0 self-center">
                  {!item.is_read && (
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleMarkRead(item.id)}
                      className="h-8 text-xs text-slate-500 hover:text-slate-900"
                    >
                      Mark Read
                    </Button>
                  )}
                  {item.link_url && (
                    <Button size="sm" variant="outline" asChild className="h-8 text-xs border-slate-200">
                      <Link href={item.link_url}>
                        Open <ExternalLink className="h-3 w-3 ml-1" />
                      </Link>
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

