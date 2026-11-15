"use client";

import * as React from "react";
import {
  Users,
  PhoneCall,
  Mail,
  FileText,
  ShieldCheck,
  ShieldAlert,
  Calendar,
  RotateCw,
  Search,
  AlertTriangle,
} from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { leadService } from "@/services/lead-service";
import { AssignedLeadItem, OutreachLogRequest } from "@/types/lead";

// Helper to format timestamps
function formatDate(dateStr?: string | null): string {
  if (!dateStr) return "—";
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-IN", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return dateStr;
  }
}

export default function AdvisorLeadsPage() {
  const [leads, setLeads] = React.useState<AssignedLeadItem[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  // Search & Filter
  const [searchQuery, setSearchQuery] = React.useState("");
  const [priorityFilter, setPriorityFilter] = React.useState("ALL");
  const [typeFilter, setTypeFilter] = React.useState("ALL");

  // Outreach Dialog State
  const [selectedLead, setSelectedLead] = React.useState<AssignedLeadItem | null>(null);
  const [isLogDialogOpen, setIsLogDialogOpen] = React.useState(false);
  const [outreachChannel, setOutreachChannel] = React.useState<"phone" | "email" | "whatsapp" | "meeting">("phone");
  const [outreachOutcome, setOutreachOutcome] = React.useState<
    "connected_interested" | "busy_callback_requested" | "unreachable" | "not_interested"
  >("connected_interested");
  const [targetStatus, setTargetStatus] = React.useState<"contacted" | "qualified" | "disqualified">("contacted");
  const [followUpDate, setFollowUpDate] = React.useState("");
  const [outreachNotes, setOutreachNotes] = React.useState("");
  const [submittingLog, setSubmittingLog] = React.useState(false);

  // Load advisor's assigned leads
  const fetchAdvisorLeads = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await leadService.getAdvisorLeads({
        search: searchQuery.trim() || undefined,
        priority: priorityFilter !== "ALL" ? priorityFilter : undefined,
        type: typeFilter !== "ALL" ? typeFilter : undefined,
      });
      setLeads(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load assigned leads. Please verify network or session.";
      console.error("Failed to fetch advisor leads:", err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, priorityFilter, typeFilter]);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      fetchAdvisorLeads();
    }, 0);
    return () => clearTimeout(timer);
  }, [fetchAdvisorLeads]);

  // Open Log Dialog
  const handleOpenLogDialog = (lead: AssignedLeadItem) => {
    setSelectedLead(lead);
    setOutreachChannel(lead.can_contact ? "phone" : "email");
    setOutreachOutcome("connected_interested");
    setTargetStatus("contacted");
    setFollowUpDate("");
    setOutreachNotes("");
    setIsLogDialogOpen(true);
  };

  // Submit Outreach Log
  const handleSubmitLog = async () => {
    if (!selectedLead) return;
    if (!outreachNotes.trim()) {
      toast.error("Please provide brief notes summarizing the outreach outcome.");
      return;
    }

    setSubmittingLog(true);
    try {
      const payload: OutreachLogRequest = {
        channel: outreachChannel,
        outcome: outreachOutcome,
        notes: outreachNotes.trim(),
        target_status: targetStatus,
        follow_up_date: followUpDate || undefined,
      };

      await leadService.logAdvisorOutreach(selectedLead.id || selectedLead.prospect_id, payload);
      toast.success("Outreach activity logged and follow-up scheduled.");
      setIsLogDialogOpen(false);
      fetchAdvisorLeads();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to save outreach notes.";
      toast.error(msg);
    } finally {
      setSubmittingLog(false);
    }
  };

  // KPI calculations
  const stats = React.useMemo(() => {
    const total = leads.length;
    const readyToCall = leads.filter((l) => l.can_contact && l.status !== "dropped" && l.status !== "converted").length;
    const followUpToday = leads.filter((l) => l.status === "contacted" || l.last_note).length;
    const contactBlocked = leads.filter((l) => !l.can_contact).length;
    return { total, readyToCall, followUpToday, contactBlocked };
  }, [leads]);

  return (
    <TooltipProvider>
      <div className="space-y-6">
        <PageHeader
          title="My Assigned Leads"
          description="Prioritized prospective customers assigned to your advisory queue for direct consultation and onboarding."
          breadcrumbs={[
            { label: "Advisor Workbench", href: "/advisor" },
            { label: "Assigned Leads" },
          ]}
          actions={
            <div className="flex items-center gap-2">
              <Badge variant="success" className="h-7 text-xs px-2.5">
                <span className="h-2 w-2 rounded-full bg-emerald-500 mr-1.5 animate-pulse" />
                Advisor Status: Active
              </Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={fetchAdvisorLeads}
                disabled={loading}
                className="text-xs bg-white border-slate-200"
              >
                <RotateCw className={`h-3.5 w-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />
                Refresh
              </Button>
            </div>
          }
        />

        {/* Top KPI Stat Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Assigned"
            value={loading ? null : stats.total}
            description="Active caseload in your queue"
            icon={Users}
          />
          <StatCard
            title="Ready to Call"
            value={loading ? null : stats.readyToCall}
            description="DPDP consented prospects"
            icon={PhoneCall}
          />
          <StatCard
            title="Follow-up Today"
            value={loading ? null : stats.followUpToday}
            description="Pending touchpoints & reviews"
            icon={Calendar}
          />
          <StatCard
            title="Needs Digital Review"
            value={loading ? null : stats.contactBlocked}
            description="In-app chat only (No outreach consent)"
            icon={ShieldAlert}
          />
        </div>

        {/* Toolbar & Filters */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 bg-white p-4 rounded-lg border border-slate-200 shadow-2xs">
          <div className="md:col-span-2 relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Search my leads by name, email, or coverage..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 h-9 text-xs bg-white border-slate-200"
            />
          </div>

          <div>
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className="h-9 text-xs bg-white border-slate-200">
                <SelectValue placeholder="Priority: All" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Priority: All</SelectItem>
                <SelectItem value="high_intent">High Intent First</SelectItem>
                <SelectItem value="warm_consideration">Warm Consideration</SelectItem>
                <SelectItem value="top_of_funnel">Top of Funnel</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="h-9 text-xs bg-white border-slate-200">
                <SelectValue placeholder="Insurance Type: All" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Insurance Type: All</SelectItem>
                <SelectItem value="term_life">Term Life</SelectItem>
                <SelectItem value="health">Comprehensive Health</SelectItem>
                <SelectItem value="motor">Motor Insurance</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between text-red-700 text-sm">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              <span>{error}</span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchAdvisorLeads}
              className="h-8 text-xs border-red-300"
            >
              Retry
            </Button>
          </div>
        )}

        {/* Assigned Leads Table */}
        <div className="rounded-lg border border-slate-200 bg-white overflow-hidden shadow-2xs">
          <Table>
            <TableHeader>
              <TableRow className="bg-slate-50/75 border-slate-200 hover:bg-slate-50/75">
                <TableHead className="text-xs font-semibold text-slate-700 h-10">Customer Details</TableHead>
                <TableHead className="text-xs font-semibold text-slate-700 h-10">Intended Coverage</TableHead>
                <TableHead className="text-xs font-semibold text-slate-700 h-10">Lead Score</TableHead>
                <TableHead className="text-xs font-semibold text-slate-700 h-10">DPDP Contactability</TableHead>
                <TableHead className="text-xs font-semibold text-slate-700 h-10">Assigned / Last Touch</TableHead>
                <TableHead className="text-xs font-semibold text-slate-700 h-10 text-right">Advisor Quick Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <TableRow key={i} className="border-slate-100">
                    <TableCell><Skeleton className="h-4 w-36" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-28" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                    <TableCell className="text-right"><Skeleton className="h-8 w-32 ml-auto" /></TableCell>
                  </TableRow>
                ))
              ) : leads.length > 0 ? (
                leads.map((lead) => {
                  const score = Number(lead.score || 0);
                  const scoreBadgeVariant =
                    score >= 70 ? "bg-emerald-50 text-emerald-700 border-emerald-200" :
                    score >= 40 ? "bg-amber-50 text-amber-700 border-amber-200" :
                    "bg-slate-100 text-slate-700 border-slate-200";

                  return (
                    <TableRow key={lead.id || lead.prospect_id} className="border-slate-100 hover:bg-slate-50/80">
                      {/* Customer Details */}
                      <TableCell className="py-3">
                        <div className="space-y-0.5">
                          <p className="font-semibold text-slate-900">{lead.customer_name || "Prospective Client"}</p>
                          <div className="text-xs text-slate-500 space-y-0.5">
                            {lead.customer_email && (
                              <p className="truncate max-w-[200px]">{lead.customer_email}</p>
                            )}
                            {lead.customer_phone && (
                              <p className="font-mono text-[11px]">{lead.customer_phone}</p>
                            )}
                          </div>
                        </div>
                      </TableCell>

                      {/* Intended Coverage */}
                      <TableCell className="py-3">
                        <div className="space-y-1">
                          <p className="text-xs font-semibold text-slate-800 capitalize">
                            {lead.intended_coverage || "Insurance Portfolio"}
                          </p>
                          <Badge variant="outline" className="text-[10px] text-slate-500 capitalize">
                            {lead.segment.replace(/_/g, " ")}
                          </Badge>
                        </div>
                      </TableCell>

                      {/* Lead Score */}
                      <TableCell className="py-3">
                        <span
                          className={`inline-flex items-center justify-center font-bold text-xs px-2.5 py-1 rounded-md border ${scoreBadgeVariant}`}
                        >
                          {Math.round(score)}/100
                        </span>
                      </TableCell>

                      {/* Contactability Pill */}
                      <TableCell className="py-3">
                        {lead.can_contact ? (
                          <div className="space-y-1">
                            <Badge variant="success" className="text-[11px] font-medium">
                              <ShieldCheck className="h-3 w-3 mr-1" />
                              Consented
                            </Badge>
                            <p className="text-[10px] text-slate-500">
                              {lead.contact_channels?.length
                                ? lead.contact_channels.join(" / ")
                                : "Call / Email / WhatsApp"}
                            </p>
                          </div>
                        ) : (
                          <div className="space-y-1">
                            <Badge variant="warning" className="text-[11px] font-medium">
                              <ShieldAlert className="h-3 w-3 mr-1" />
                              No Contact
                            </Badge>
                            <p className="text-[10px] text-amber-700 font-medium">
                              In-App Chat Only
                            </p>
                          </div>
                        )}
                      </TableCell>

                      {/* Timeline / Touchpoint */}
                      <TableCell className="py-3 text-xs text-slate-500">
                        <p className="font-mono text-[11px] text-slate-700">
                          {formatDate(lead.assigned_at || lead.last_activity_at)}
                        </p>
                        {lead.last_note && (
                          <p className="text-[11px] text-slate-500 truncate max-w-[180px] italic">
                            &ldquo;{lead.last_note}&rdquo;
                          </p>
                        )}
                      </TableCell>

                      {/* Strict UI Constraint: Quick Action Controls */}
                      <TableCell className="py-3 text-right">
                        <div className="inline-flex items-center gap-1.5 justify-end">
                          {/* Call Button */}
                          {lead.can_contact && lead.customer_phone ? (
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <a
                                  href={`tel:${lead.customer_phone}`}
                                  className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-emerald-200 text-emerald-700 hover:bg-emerald-50 hover:text-emerald-800 transition-colors"
                                >
                                  <PhoneCall className="h-3.5 w-3.5" />
                                </a>
                              </TooltipTrigger>
                              <TooltipContent>
                                Call {lead.customer_name || "customer"} ({lead.customer_phone})
                              </TooltipContent>
                            </Tooltip>
                          ) : (
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <span tabIndex={0} className="inline-block cursor-not-allowed">
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    disabled
                                    className="h-8 w-8 p-0 border-slate-200 text-slate-300 opacity-50 pointer-events-none"
                                  >
                                    <PhoneCall className="h-3.5 w-3.5" />
                                  </Button>
                                </span>
                              </TooltipTrigger>
                              <TooltipContent className="max-w-xs text-xs text-amber-800 border-amber-200 bg-amber-50">
                                Outreach blocked: Customer has not provided marketing contact consent under DPDP guidelines.
                              </TooltipContent>
                            </Tooltip>
                          )}

                          {/* Email Button */}
                          {lead.can_contact && lead.customer_email ? (
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <a
                                  href={`mailto:${lead.customer_email}`}
                                  className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-blue-200 text-blue-700 hover:bg-blue-50 hover:text-blue-800 transition-colors"
                                >
                                  <Mail className="h-3.5 w-3.5" />
                                </a>
                              </TooltipTrigger>
                              <TooltipContent>
                                Send Email to {lead.customer_email}
                              </TooltipContent>
                            </Tooltip>
                          ) : (
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <span tabIndex={0} className="inline-block cursor-not-allowed">
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    disabled
                                    className="h-8 w-8 p-0 border-slate-200 text-slate-300 opacity-50 pointer-events-none"
                                  >
                                    <Mail className="h-3.5 w-3.5" />
                                  </Button>
                                </span>
                              </TooltipTrigger>
                              <TooltipContent className="max-w-xs text-xs text-amber-800 border-amber-200 bg-amber-50">
                                Outreach blocked: Customer has not provided marketing contact consent under DPDP guidelines.
                              </TooltipContent>
                            </Tooltip>
                          )}

                          {/* Log Outreach Button */}
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleOpenLogDialog(lead)}
                            className="h-8 text-xs text-slate-700 border-slate-200 hover:bg-slate-50"
                          >
                            <FileText className="h-3.5 w-3.5 mr-1 text-slate-500" />
                            Log Outreach
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })
              ) : (
                <TableRow>
                  <TableCell colSpan={6} className="h-44 text-center">
                    <div className="flex flex-col items-center justify-center text-slate-400 space-y-2">
                      <Users className="h-8 w-8 text-slate-300 stroke-[1.5]" />
                      <p className="text-sm font-medium text-slate-600">No leads assigned to your queue</p>
                      <p className="text-xs text-slate-400 max-w-sm">
                        Qualified prospects allocated by the workload-aware assignment engine will appear here.
                      </p>
                    </div>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>

        {/* OUTREACH LOGGING DIALOG */}
        <Dialog open={isLogDialogOpen} onOpenChange={setIsLogDialogOpen}>
          <DialogContent className="sm:max-w-lg bg-white border border-slate-200">
            <DialogHeader>
              <DialogTitle className="text-base font-bold text-slate-900">
                Log Customer Outreach Note
              </DialogTitle>
              <DialogDescription className="text-xs text-slate-500">
                Record outreach results, customer sentiment, and schedule follow-up actions in the audit log.
              </DialogDescription>
            </DialogHeader>

            {selectedLead && (
              <div className="space-y-4 py-2">
                {/* Customer Summary banner */}
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-semibold text-slate-900 block">
                      {selectedLead.customer_name}
                    </span>
                    <span className="text-slate-500 font-mono text-[11px]">
                      {selectedLead.intended_coverage}
                    </span>
                  </div>
                  <div>
                    {selectedLead.can_contact ? (
                      <Badge variant="success" className="text-[10px]">
                        DPDP Consented
                      </Badge>
                    ) : (
                      <Badge variant="warning" className="text-[10px]">
                        In-App Chat Only
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-700">Outreach Channel</label>
                    <Select
                      value={outreachChannel}
                      onValueChange={(val: "phone" | "email" | "whatsapp" | "meeting") =>
                        setOutreachChannel(val)
                      }
                    >
                      <SelectTrigger className="h-9 text-xs bg-white border-slate-200">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="phone">Phone Call</SelectItem>
                        <SelectItem value="email">Direct Email</SelectItem>
                        <SelectItem value="whatsapp">WhatsApp Business</SelectItem>
                        <SelectItem value="meeting">Video / In-Person</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-700">Outreach Outcome</label>
                    <Select
                      value={outreachOutcome}
                      onValueChange={(
                        val: "connected_interested" | "busy_callback_requested" | "unreachable" | "not_interested"
                      ) => setOutreachOutcome(val)}
                    >
                      <SelectTrigger className="h-9 text-xs bg-white border-slate-200">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="connected_interested">Connected & Interested</SelectItem>
                        <SelectItem value="busy_callback_requested">Busy / Callback Requested</SelectItem>
                        <SelectItem value="unreachable">Unreachable / No Answer</SelectItem>
                        <SelectItem value="not_interested">Not Interested</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-700">Lead Stage Transition</label>
                    <Select
                      value={targetStatus}
                      onValueChange={(val: "contacted" | "qualified" | "disqualified") =>
                        setTargetStatus(val)
                      }
                    >
                      <SelectTrigger className="h-9 text-xs bg-white border-slate-200">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="contacted">Mark as Contacted</SelectItem>
                        <SelectItem value="qualified">Advance to Qualified</SelectItem>
                        <SelectItem value="disqualified">Disqualify Lead</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-700">Next Follow-Up Date</label>
                    <Input
                      type="date"
                      value={followUpDate}
                      onChange={(e) => setFollowUpDate(e.target.value)}
                      className="h-9 text-xs bg-white border-slate-200"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700">
                    Outreach Notes & Next Actions
                  </label>
                  <textarea
                    rows={3}
                    placeholder="Summarize customer discussion, stated insurance requirements, and promised next steps..."
                    value={outreachNotes}
                    onChange={(e) => setOutreachNotes(e.target.value)}
                    className="w-full text-xs rounded-md border border-slate-200 bg-white p-2.5 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-primary text-slate-900"
                  />
                </div>
              </div>
            )}

            <DialogFooter className="gap-2 sm:gap-0">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsLogDialogOpen(false)}
                className="text-xs border-slate-200"
              >
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={handleSubmitLog}
                disabled={submittingLog || !outreachNotes.trim()}
                className="text-xs bg-blue-600 hover:bg-blue-700 text-white"
              >
                {submittingLog ? "Saving..." : "Save Outreach Log"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </TooltipProvider>
  );
}
