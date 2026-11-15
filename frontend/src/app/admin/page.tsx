"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Users,
  UserCheck,
  MessageSquare,
  Calculator,
  FileText,
  Clock,
  TrendingUp,
  CalendarCheck,
  Plus,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { OverviewKPICard } from "@/components/admin/overview-kpi-card";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { AdminAPI } from "@/services/admin.service";
import { ExecutiveMetrics, RecentActivityItem } from "@/types/admin";

export default function AdminOverviewPage() {
  const [metrics, setMetrics] = useState<ExecutiveMetrics | null>(null);
  const [activities, setActivities] = useState<RecentActivityItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const [metricsData, activityData] = await Promise.all([
        AdminAPI.getMetrics(),
        AdminAPI.getActivityStream(10),
      ]);
      setMetrics(metricsData);
      setActivities(activityData.activities);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load executive overview data.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Executive Business Overview"
        description="Real-time key performance indicators, operational caseloads, and conversion health."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Overview" },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={loadData} disabled={isLoading}>
              <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Button size="sm" asChild className="bg-blue-600 hover:bg-blue-700 text-white">
              <Link href="/admin/products">
                <Plus className="w-3.5 h-3.5 mr-1.5" />
                Configure Product
              </Link>
            </Button>
          </div>
        }
      />

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg text-sm text-rose-700">
          {error}
        </div>
      )}

      {/* 8 Real Database-Backed KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {isLoading ? (
          Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-lg bg-slate-100" />
          ))
        ) : (
          <>
            <OverviewKPICard
              title="Total Prospects"
              value={metrics?.total_prospects.toLocaleString() || 0}
              subtitle="Registered leads in acquisition pipeline"
              icon={Users}
            />
            <OverviewKPICard
              title="Qualified Leads"
              value={metrics?.qualified_leads.toLocaleString() || 0}
              subtitle="Score >= 60 ready for consultation"
              icon={UserCheck}
              badge={`${
                metrics?.total_prospects
                  ? Math.round((metrics.qualified_leads / metrics.total_prospects) * 100)
                  : 0
              }% qualified`}
            />
            <OverviewKPICard
              title="Active Conversations"
              value={metrics?.active_conversations.toLocaleString() || 0}
              subtitle="AI engagement sessions within 24h"
              icon={MessageSquare}
            />
            <OverviewKPICard
              title="Quotes Formulated"
              value={metrics?.quotes_generated.toLocaleString() || 0}
              subtitle="Deterministic actuarial pricing calculations"
              icon={Calculator}
            />
            <OverviewKPICard
              title="Proposals Submitted"
              value={metrics?.applications_submitted.toLocaleString() || 0}
              subtitle="Applications progressed past draft"
              icon={FileText}
            />
            <OverviewKPICard
              title="Awaiting Underwriting"
              value={metrics?.applications_awaiting_review.toLocaleString() || 0}
              subtitle="In triage queue for human underwriter"
              icon={Clock}
              badge="Underwriting Queue"
            />
            <OverviewKPICard
              title="Pipeline Conversion"
              value={`${metrics?.conversion_rate || 0}%`}
              subtitle="Submitted applications vs total prospects"
              icon={TrendingUp}
            />
            <OverviewKPICard
              title="Pending Follow-ups"
              value={metrics?.pending_follow_ups.toLocaleString() || 0}
              subtitle="Scheduled calls and outreach tasks"
              icon={CalendarCheck}
            />
          </>
        )}
      </div>

      {/* Real-time Activity Pulse Stream */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 bg-white border-slate-200">
          <CardHeader className="pb-3 border-b border-slate-100 flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-base font-bold text-slate-900">
                Real-Time Operational Pulse
              </CardTitle>
              <CardDescription className="text-xs text-slate-500">
                Chronological transactional events streamed from immutable audit logs
              </CardDescription>
            </div>
            <Button variant="ghost" size="sm" asChild className="text-xs text-blue-600">
              <Link href="/admin/audit">
                View Full Audit Vault <ExternalLink className="w-3 h-3 ml-1" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="p-6 space-y-3">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : activities.length === 0 ? (
              <div className="p-12 text-center text-slate-400 text-sm">
                No recent transactional events recorded in the audit logs.
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {activities.map((act) => (
                  <div key={act.id} className="p-4 flex items-center justify-between hover:bg-slate-50/50 transition-colors">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-[11px] font-mono border-slate-200">
                          {act.action}
                        </Badge>
                        <span className="text-xs font-semibold text-slate-800">
                          {act.resource_type}
                        </span>
                        <span className="text-xs text-slate-400 font-mono">
                          ({act.resource_id.slice(0, 12)}...)
                        </span>
                      </div>
                      <p className="text-xs text-slate-500">
                        Actor: {act.actor_email || "System"} • {act.description}
                      </p>
                    </div>
                    <span className="text-[11px] text-slate-400 whitespace-nowrap">
                      {new Date(act.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Operations Panel */}
        <Card className="bg-white border-slate-200">
          <CardHeader className="pb-3 border-b border-slate-100">
            <CardTitle className="text-base font-bold text-slate-900">
              Quick Governance Actions
            </CardTitle>
            <CardDescription className="text-xs text-slate-500">
              Administrative shortcuts and governance links
            </CardDescription>
          </CardHeader>
          <CardContent className="p-5 space-y-3">
            <Button variant="outline" asChild className="w-full justify-start text-xs h-9">
              <Link href="/admin/agents">
                <ShieldCheck className="w-4 h-4 mr-2 text-blue-600" />
                Agent Control Centre & Kill-Switches
              </Link>
            </Button>
            <Button variant="outline" asChild className="w-full justify-start text-xs h-9">
              <Link href="/admin/employees">
                <Users className="w-4 h-4 mr-2 text-emerald-600" />
                Staff Directory & Role Provisioning
              </Link>
            </Button>
            <Button variant="outline" asChild className="w-full justify-start text-xs h-9">
              <Link href="/admin/funnel">
                <TrendingUp className="w-4 h-4 mr-2 text-indigo-600" />
                Conversion Funnel & Drop-off Analysis
              </Link>
            </Button>
            <Button variant="outline" asChild className="w-full justify-start text-xs h-9">
              <Link href="/admin/integrations">
                <RefreshCw className="w-4 h-4 mr-2 text-amber-600" />
                Third-Party & Insurer Health Status
              </Link>
            </Button>
            <Button variant="outline" asChild className="w-full justify-start text-xs h-9">
              <Link href="/admin/settings">
                <Calculator className="w-4 h-4 mr-2 text-slate-600" />
                Underwriting SLAs & Auto-Assignment Rules
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
