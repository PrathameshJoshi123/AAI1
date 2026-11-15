"use client";

import * as React from "react";
import Link from "next/link";
import {
  Scale,
  ShieldAlert,
  CheckCircle2,
  Clock,
  ArrowRight,
  AlertTriangle,
  FileCheck,
  CalendarClock,
  UserCheck,
  Briefcase,
  ExternalLink,
  RefreshCw,
  Plus,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { advisorService } from "@/services/advisor-service";
import { WorkspaceDashboardData } from "@/types/advisor";

export default function AdvisorWorkbenchPage() {
  const [data, setData] = React.useState<WorkspaceDashboardData | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  const loadDashboard = React.useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await advisorService.getWorkspaceDashboard();
      setData(res);
    } catch (err: any) {
      console.error("Failed to load workspace dashboard:", err);
      setError(err?.message || "Failed to load workspace data.");
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const kpis = data?.kpis;
  const tasks = data?.urgent_tasks || [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <PageHeader
          title="Advisor & Underwriter Workstation"
          description="Real-time case triage, urgent SLA alerts, KYC document audits, and customer engagement queue."
          breadcrumbs={[
            { label: "Advisor Workbench", href: "/advisor" },
            { label: "My Workspace" },
          ]}
        />
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <Button
            variant="outline"
            size="sm"
            onClick={loadDashboard}
            disabled={loading}
            className="h-9 gap-1.5 text-xs bg-white border-slate-200"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button size="sm" asChild className="h-9 gap-1.5 text-xs bg-blue-600 hover:bg-blue-700 text-white">
            <Link href="/advisor/underwriting">
              <Scale className="h-3.5 w-3.5" />
              Underwriting Cockpit
            </Link>
          </Button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-sm flex items-center justify-between">
          <span>{error}</span>
          <Button variant="outline" size="sm" onClick={loadDashboard} className="h-7 text-xs">
            Retry
          </Button>
        </div>
      )}

      {/* KPI Stat Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <StatCard
          title="Active Cases"
          value={kpis?.active_cases_count ?? 0}
          description="In review or assigned"
          icon={Briefcase}
        />
        <StatCard
          title="Pending Documents"
          value={kpis?.pending_document_verifications ?? 0}
          description="Require human audit"
          icon={FileCheck}
        />
        <StatCard
          title="SLA at Risk (<4h)"
          value={kpis?.sla_at_risk_count ?? 0}
          description="Immediate review required"
          icon={AlertTriangle}
        />
        <StatCard
          title="Overdue Follow-ups"
          value={kpis?.overdue_follow_ups_count ?? 0}
          description="Customer calls / emails"
          icon={CalendarClock}
        />
        <StatCard
          title="Awaiting Customer"
          value={kpis?.cases_awaiting_info_count ?? 0}
          description="Additional info requested"
          icon={Clock}
        />
        <StatCard
          title="Assigned Leads"
          value={kpis?.total_assigned_leads ?? 0}
          description="Active prospects pipeline"
          icon={UserCheck}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Urgent Action Items Queue */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h2 className="text-base font-semibold text-slate-900">Urgent Casework & Action Items</h2>
              {tasks.length > 0 && (
                <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200 font-semibold text-xs">
                  {tasks.length} Priority
                </Badge>
              )}
            </div>
            <Button variant="ghost" size="sm" asChild className="text-xs text-blue-600 hover:text-blue-700">
              <Link href="/advisor/underwriting">
                View All Cases <ArrowRight className="h-3.5 w-3.5 ml-1" />
              </Link>
            </Button>
          </div>

          {tasks.length === 0 ? (
            <Card className="bg-white border-slate-200">
              <CardContent className="flex flex-col items-center justify-center p-8 text-center">
                <div className="h-12 w-12 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mb-3">
                  <CheckCircle2 className="h-6 w-6" />
                </div>
                <h3 className="text-sm font-semibold text-slate-900">Priority Queue Is Clear</h3>
                <p className="text-xs text-slate-500 max-warn-w mt-1 max-w-sm">
                  There are no immediate SLA breach warnings or overdue follow-ups assigned to your queue.
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {tasks.map((task) => (
                <Card key={task.id} className="bg-white border-slate-200 hover:border-slate-300 transition-colors">
                  <CardContent className="p-4 flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge
                          variant="outline"
                          className={
                            task.priority === "urgent"
                              ? "bg-red-50 text-red-700 border-red-200"
                              : task.priority === "high"
                              ? "bg-amber-50 text-amber-700 border-amber-200"
                              : "bg-blue-50 text-blue-700 border-blue-200"
                          }
                        >
                          {task.priority.toUpperCase()}
                        </Badge>
                        <span className="text-xs font-semibold text-slate-900">{task.title}</span>
                      </div>
                      <p className="text-xs text-slate-600">{task.description}</p>
                      {task.due_date && (
                        <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
                          <Clock className="h-3 w-3" />
                          <span>Deadline: {new Date(task.due_date).toLocaleString()}</span>
                        </div>
                      )}
                    </div>
                    <Button size="sm" variant="outline" asChild className="text-xs shrink-0 border-slate-200">
                      <Link href={task.link_url}>
                        Action <ArrowRight className="h-3 w-3 ml-1" />
                      </Link>
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Quick Operations & Tools */}
        <div className="space-y-4">
          <h2 className="text-base font-semibold text-slate-900">Quick Navigation</h2>
          <div className="space-y-3">
            <Card className="bg-white border-slate-200 hover:border-blue-200 transition-colors">
              <CardHeader className="p-4 pb-2">
                <CardTitle className="text-sm font-semibold flex items-center justify-between">
                  <span>Document Verification Station</span>
                  <Badge variant="outline" className="text-xs font-normal bg-slate-50 border-slate-200">
                    KYC Vault
                  </Badge>
                </CardTitle>
                <CardDescription className="text-xs text-slate-500">
                  Audit uploaded Aadhaar, PAN, and salary slips with side-by-side OCR discrepancy reconciliation.
                </CardDescription>
              </CardHeader>
              <CardContent className="p-4 pt-2">
                <Button variant="outline" size="sm" className="w-full text-xs justify-between" asChild>
                  <Link href="/advisor/documents">
                    <span>Open Document Station</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </Button>
              </CardContent>
            </Card>

            <Card className="bg-white border-slate-200 hover:border-blue-200 transition-colors">
              <CardHeader className="p-4 pb-2">
                <CardTitle className="text-sm font-semibold flex items-center justify-between">
                  <span>Scheduled Follow-ups</span>
                  <Badge variant="outline" className="text-xs font-normal bg-slate-50 border-slate-200">
                    Agenda
                  </Badge>
                </CardTitle>
                <CardDescription className="text-xs text-slate-500">
                  Organize customer outreach calls, video consultations, and missing document collection.
                </CardDescription>
              </CardHeader>
              <CardContent className="p-4 pt-2">
                <Button variant="outline" size="sm" className="w-full text-xs justify-between" asChild>
                  <Link href="/advisor/follow-ups">
                    <span>Manage Follow-ups</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </Button>
              </CardContent>
            </Card>

            <Card className="bg-white border-slate-200 hover:border-blue-200 transition-colors">
              <CardHeader className="p-4 pb-2">
                <CardTitle className="text-sm font-semibold flex items-center justify-between">
                  <span>Customer AI Conversations</span>
                  <Badge variant="outline" className="text-xs font-normal bg-slate-50 border-slate-200">
                    Audit Log
                  </Badge>
                </CardTitle>
                <CardDescription className="text-xs text-slate-500">
                  Review customer multi-turn dialogue with the Mistral AI bot, intent tags, and qualification flags.
                </CardDescription>
              </CardHeader>
              <CardContent className="p-4 pt-2">
                <Button variant="outline" size="sm" className="w-full text-xs justify-between" asChild>
                  <Link href="/advisor/conversations">
                    <span>Inspect Conversations</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
