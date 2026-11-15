"use client";

import * as React from "react";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  useReactTable,
} from "@tanstack/react-table";
import {
  Users,
  Search,
  Download,
  RotateCw,
  ShieldCheck,
  ShieldAlert,
  Clock,
  Sparkles,
  Bot,
  UserCheck,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Activity,
  AlertTriangle,
} from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/shared/page-header";
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
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
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
import {
  AdvisorSummary,
  LeadRecord,
  LeadTimelineEvent,
  ProspectDetail,
  ProspectFilterParams,
} from "@/types/lead";

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

// Helper to render score pill
function getScoreColor(score: number): {
  badge: "success" | "warning" | "secondary" | "default";
  bg: string;
  text: string;
} {
  if (score >= 70) {
    return { badge: "success", bg: "bg-emerald-50 text-emerald-700 border-emerald-200", text: "text-emerald-700" };
  }
  if (score >= 40) {
    return { badge: "warning", bg: "bg-amber-50 text-amber-700 border-amber-200", text: "text-amber-700" };
  }
  return { badge: "secondary", bg: "bg-slate-100 text-slate-700 border-slate-200", text: "text-slate-600" };
}

// Helper to render segment pill
function renderSegmentBadge(segment: string) {
  switch (segment.toLowerCase()) {
    case "high_intent":
      return <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100">High Intent</Badge>;
    case "warm_consideration":
      return <Badge className="bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100">Warm Consideration</Badge>;
    case "top_of_funnel":
      return <Badge variant="secondary">Top of Funnel</Badge>;
    case "price_sensitive":
      return <Badge className="bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100">Price Sensitive</Badge>;
    case "dormant":
      return <Badge variant="outline" className="text-slate-400 border-slate-200">Dormant</Badge>;
    default:
      return <Badge variant="outline">{segment.replace(/_/g, " ")}</Badge>;
  }
}

// Helper to render qualification status badge
function renderStatusBadge(status: string) {
  switch (status.toLowerCase()) {
    case "qualified":
      return <Badge variant="success">Qualified</Badge>;
    case "engaged":
      return <Badge className="bg-blue-50 text-blue-700 border-blue-200">Engaged</Badge>;
    case "new":
      return <Badge variant="secondary">New Inbound</Badge>;
    case "converted":
      return <Badge className="bg-purple-50 text-purple-700 border-purple-200">Converted</Badge>;
    case "dropped":
      return <Badge variant="destructive">Dropped</Badge>;
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
}

export default function AdminLeadsPage() {
  const [leads, setLeads] = React.useState<LeadRecord[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  // Filters state
  const [searchQuery, setSearchQuery] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState<string>("ALL");
  const [segmentFilter, setSegmentFilter] = React.useState<string>("ALL");
  const [sourceFilter, setSourceFilter] = React.useState<string>("ALL");
  const [advisorFilter, setAdvisorFilter] = React.useState<string>("ALL");

  // Lead inspector state
  const [selectedLeadId, setSelectedLeadId] = React.useState<string | null>(null);
  const [leadDetail, setLeadDetail] = React.useState<ProspectDetail | null>(null);
  const [timelineEvents, setTimelineEvents] = React.useState<LeadTimelineEvent[]>([]);
  const [loadingDetail, setLoadingDetail] = React.useState(false);
  const [isSheetOpen, setIsSheetOpen] = React.useState(false);
  const [recalculatingScore, setRecalculatingScore] = React.useState(false);

  // Advisor reassignment state
  const [isAssignDialogOpen, setIsAssignDialogOpen] = React.useState(false);
  const [advisors, setAdvisors] = React.useState<AdvisorSummary[]>([]);
  const [selectedAdvisorId, setSelectedAdvisorId] = React.useState<string>("");
  const [reassignmentReason, setReassignmentReason] = React.useState("");
  const [assigningLoading, setAssigningLoading] = React.useState(false);

  // Load leads
  const fetchLeads = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: ProspectFilterParams = {
        query: searchQuery.trim() || undefined,
        status: statusFilter !== "ALL" ? statusFilter : undefined,
        segment: segmentFilter !== "ALL" ? segmentFilter : undefined,
        source_name: sourceFilter !== "ALL" ? sourceFilter : undefined,
        assigned_advisor_id: advisorFilter !== "ALL" ? advisorFilter : undefined,
        page_size: 100,
      };

      const res = await leadService.getProspects(params);
      setLeads(res.items || []);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load lead pipeline. Please try again.";
      console.error("Failed to fetch leads:", err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, statusFilter, segmentFilter, sourceFilter, advisorFilter]);

  React.useEffect(() => {
    fetchLeads();
  }, [fetchLeads]);

  // Load advisors for filter & reassignment
  React.useEffect(() => {
    leadService
      .getAvailableAdvisors()
      .then((data) => setAdvisors(data))
      .catch((err) => console.error("Could not load advisors:", err));
  }, []);

  // Open Lead Inspector Sheet
  const handleOpenInspector = async (leadId: string) => {
    setSelectedLeadId(leadId);
    setIsSheetOpen(true);
    setLoadingDetail(true);
    try {
      const [detail, timeline] = await Promise.all([
        leadService.getProspectById(leadId),
        leadService.getProspectTimeline(leadId).catch(() => []),
      ]);
      setLeadDetail(detail);
      setTimelineEvents(timeline);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load lead details.";
      toast.error(msg);
    } finally {
      setLoadingDetail(false);
    }
  };

  // Recalculate score on demand
  const handleRecalculateScore = async () => {
    if (!selectedLeadId) return;
    setRecalculatingScore(true);
    try {
      const updatedScore = await leadService.recalculateScore(selectedLeadId);
      toast.success(`Score recalculated: ${updatedScore.score}/100`);

      // Refresh inspector details and list
      const [refreshedDetail, refreshedTimeline] = await Promise.all([
        leadService.getProspectById(selectedLeadId),
        leadService.getProspectTimeline(selectedLeadId).catch(() => []),
      ]);
      setLeadDetail(refreshedDetail);
      setTimelineEvents(refreshedTimeline);
      fetchLeads();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to recalculate lead score.";
      toast.error(msg);
    } finally {
      setRecalculatingScore(false);
    }
  };

  // Open Reassign Dialog
  const handleOpenAssignDialog = () => {
    setSelectedAdvisorId(leadDetail?.assigned_advisor_id || "");
    setReassignmentReason("");
    setIsAssignDialogOpen(true);
  };

  // Confirm Reassign Advisor
  const handleConfirmAssignment = async () => {
    if (!selectedLeadId || !selectedAdvisorId) {
      toast.error("Please select an advisor for assignment.");
      return;
    }
    setAssigningLoading(true);
    try {
      await leadService.assignAdvisor(
        selectedLeadId,
        selectedAdvisorId,
        reassignmentReason
      );
      toast.success("Advisor assigned successfully.");
      setIsAssignDialogOpen(false);

      // Refresh inspector and list
      const [refreshedDetail, refreshedTimeline] = await Promise.all([
        leadService.getProspectById(selectedLeadId),
        leadService.getProspectTimeline(selectedLeadId).catch(() => []),
      ]);
      setLeadDetail(refreshedDetail);
      setTimelineEvents(refreshedTimeline);
      fetchLeads();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to reassign advisor.";
      toast.error(msg);
    } finally {
      setAssigningLoading(false);
    }
  };

  // Export CSV
  const handleExportCSV = () => {
    if (leads.length === 0) {
      toast.error("No lead records available to export.");
      return;
    }
    const headers = [
      "ID",
      "Name",
      "Email",
      "Phone",
      "Status",
      "Segment",
      "Lead Score",
      "Can Contact (DPDP)",
      "Source",
      "Assigned Advisor",
      "Target Insurance Type",
      "Created At",
      "Last Activity",
    ];

    const rows = leads.map((lead) => [
      `"${lead.id}"`,
      `"${lead.name || "Anonymous"}"`,
      `"${lead.email || ""}"`,
      `"${lead.phone || ""}"`,
      `"${lead.status}"`,
      `"${lead.segment}"`,
      `"${lead.score ?? (typeof lead.latest_score === "object" ? lead.latest_score?.score : lead.latest_score) ?? lead.leadScore ?? 0}"`,
      `"${lead.can_contact ? "Yes" : "No"}"`,
      `"${lead.source_name || lead.source || ""}"`,
      `"${lead.assigned_advisor_name || "Unassigned"}"`,
      `"${lead.target_insurance_type || ""}"`,
      `"${lead.created_at || lead.createdAt || ""}"`,
      `"${lead.last_activity_at || ""}"`,
    ]);

    const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `leads_export_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success(`Exported ${leads.length} leads to CSV.`);
  };

  // TanStack columns definition
  const columns = React.useMemo<ColumnDef<LeadRecord>[]>(
    () => [
      {
        accessorKey: "name",
        header: "Lead Name & Contact",
        cell: ({ row }) => {
          const lead = row.original;
          const name = lead.name || "Anonymous Visitor";
          const canContact = lead.can_contact;
          return (
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-slate-900">{name}</span>
                {canContact ? (
                  <span
                    title="DPDP Consented: Customer explicitly granted marketing contact"
                    className="inline-flex items-center text-emerald-600"
                  >
                    <ShieldCheck className="h-4 w-4" />
                  </span>
                ) : (
                  <span
                    title="Outreach Blocked: No marketing contact consent under DPDP"
                    className="inline-flex items-center text-amber-500"
                  >
                    <ShieldAlert className="h-4 w-4" />
                  </span>
                )}
              </div>
              <div className="text-xs text-slate-500">
                {lead.email ? (
                  <span className="block truncate max-w-[200px]">{lead.email}</span>
                ) : (
                  <span className="italic text-slate-400">No email registered</span>
                )}
                {lead.phone && <span className="block font-mono text-[11px]">{lead.phone}</span>}
              </div>
            </div>
          );
        },
      },
      {
        accessorKey: "source_name",
        header: "Acquisition Source",
        cell: ({ row }) => {
          const lead = row.original;
          const source = lead.source_name || lead.source || "web_direct";
          return (
            <div className="space-y-0.5">
              <div className="text-xs font-medium text-slate-800 capitalize">
                {source.replace(/_/g, " ")}
              </div>
              {lead.target_insurance_type && (
                <Badge variant="outline" className="text-[10px] text-slate-500 font-normal">
                  {lead.target_insurance_type.replace(/_/g, " ")}
                </Badge>
              )}
            </div>
          );
        },
      },
      {
        accessorKey: "segment",
        header: "Segment",
        cell: ({ row }) => renderSegmentBadge(row.original.segment || "top_of_funnel"),
      },
      {
        accessorKey: "score",
        header: "Lead Score",
        cell: ({ row }) => {
          const lead = row.original;
          const score =
            lead.score ??
            (typeof lead.latest_score === "object" ? lead.latest_score?.score : lead.latest_score) ??
            lead.leadScore ??
            0;
          const style = getScoreColor(Number(score));
          return (
            <div className="flex items-center gap-2">
              <span
                className={`inline-flex items-center justify-center font-bold text-xs px-2.5 py-1 rounded-md border ${style.bg}`}
              >
                {Math.round(Number(score))}/100
              </span>
            </div>
          );
        },
      },
      {
        accessorKey: "assigned_advisor_name",
        header: "Assigned Advisor",
        cell: ({ row }) => {
          const advisorName = row.original.assigned_advisor_name;
          if (advisorName) {
            return (
              <div className="flex items-center gap-1.5 text-xs text-slate-800 font-medium">
                <UserCheck className="h-3.5 w-3.5 text-blue-600" />
                <span>{advisorName}</span>
              </div>
            );
          }
          return (
            <Badge variant="outline" className="text-slate-400 border-dashed border-slate-300">
              Unassigned
            </Badge>
          );
        },
      },
      {
        accessorKey: "status",
        header: "Status",
        cell: ({ row }) => renderStatusBadge(row.original.status || "new"),
      },
      {
        accessorKey: "last_activity_at",
        header: "Last Activity",
        cell: ({ row }) => (
          <span className="text-xs text-slate-500 font-mono">
            {formatDate(row.original.last_activity_at || row.original.created_at)}
          </span>
        ),
      },
      {
        id: "actions",
        header: () => <span className="sr-only">Actions</span>,
        cell: ({ row }) => (
          <Button
            variant="outline"
            size="sm"
            className="h-8 text-xs text-blue-600 border-blue-200 hover:bg-blue-50"
            onClick={(e) => {
              e.stopPropagation();
              handleOpenInspector(row.original.id);
            }}
          >
            Inspect
            <ExternalLink className="h-3 w-3 ml-1" />
          </Button>
        ),
      },
    ],
    []
  );

  const table = useReactTable({
    data: leads,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
        pageSize: 15,
      },
    },
  });

  // Calculate segment breakdown counts
  const segmentCounts = React.useMemo(() => {
    const counts: Record<string, number> = {
      ALL: leads.length,
      high_intent: 0,
      warm_consideration: 0,
      top_of_funnel: 0,
      price_sensitive: 0,
      dormant: 0,
    };
    leads.forEach((l) => {
      const seg = l.segment?.toLowerCase() || "top_of_funnel";
      if (counts[seg] !== undefined) {
        counts[seg]++;
      }
    });
    return counts;
  }, [leads]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Prospect & Lead Pipeline"
        description="Monitor multi-channel acquisition funnels, deterministic scoring factors, DPDP consent guardrails, and advisor allocation."
        breadcrumbs={[
          { label: "Admin Dashboard", href: "/admin" },
          { label: "Prospect & Lead Pipeline" },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={fetchLeads}
              disabled={loading}
              className="text-xs bg-white border-slate-200"
            >
              <RotateCw className={`h-3.5 w-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleExportCSV}
              className="text-xs bg-white border-slate-200 text-slate-700"
            >
              <Download className="h-3.5 w-3.5 mr-1.5" />
              Export CSV
            </Button>
          </div>
        }
      />

      {/* Segment Shortcut Pills */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 pb-3">
        {[
          { key: "ALL", label: "All Leads" },
          { key: "high_intent", label: "High Intent" },
          { key: "warm_consideration", label: "Warm Consideration" },
          { key: "top_of_funnel", label: "Top of Funnel" },
          { key: "price_sensitive", label: "Price Sensitive" },
          { key: "dormant", label: "Dormant" },
        ].map((seg) => {
          const isActive = segmentFilter === seg.key;
          const count = segmentCounts[seg.key] ?? 0;
          return (
            <button
              key={seg.key}
              onClick={() => setSegmentFilter(seg.key)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors flex items-center gap-1.5 border ${
                isActive
                  ? "bg-blue-600 text-white border-blue-600 shadow-xs"
                  : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50"
              }`}
            >
              <span>{seg.label}</span>
              <span
                className={`text-[11px] px-1.5 py-0.2 rounded-full ${
                  isActive ? "bg-blue-700 text-white" : "bg-slate-100 text-slate-600"
                }`}
              >
                {count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Filters Toolbar */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3 bg-white p-4 rounded-lg border border-slate-200 shadow-2xs">
        <div className="md:col-span-2 relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search by name, email, phone..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 h-9 text-xs bg-white border-slate-200"
          />
        </div>

        <div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="h-9 text-xs bg-white border-slate-200">
              <SelectValue placeholder="Status: All" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Status: All</SelectItem>
              <SelectItem value="new">New Inbound</SelectItem>
              <SelectItem value="engaged">Engaged</SelectItem>
              <SelectItem value="qualified">Qualified</SelectItem>
              <SelectItem value="converted">Converted</SelectItem>
              <SelectItem value="dropped">Dropped</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Select value={sourceFilter} onValueChange={setSourceFilter}>
            <SelectTrigger className="h-9 text-xs bg-white border-slate-200">
              <SelectValue placeholder="Source: All" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Source: All</SelectItem>
              <SelectItem value="web_direct">Web Direct</SelectItem>
              <SelectItem value="google_cpc">Google Ads</SelectItem>
              <SelectItem value="google_organic">Google Organic</SelectItem>
              <SelectItem value="partner_aggregator">Partner Aggregator</SelectItem>
              <SelectItem value="mobile_referral">Mobile Referral</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Select value={advisorFilter} onValueChange={setAdvisorFilter}>
            <SelectTrigger className="h-9 text-xs bg-white border-slate-200">
              <SelectValue placeholder="Advisor: All" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Advisor: All</SelectItem>
              <SelectItem value="unassigned">Unassigned Only</SelectItem>
              {advisors.map((adv) => (
                <SelectItem key={adv.id} value={adv.id}>
                  {adv.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between text-red-700 text-sm">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" />
            <span>{error}</span>
          </div>
          <Button variant="outline" size="sm" onClick={fetchLeads} className="h-8 text-xs border-red-300">
            Retry
          </Button>
        </div>
      )}

      {/* Leads Table */}
      <div className="rounded-lg border border-slate-200 bg-white overflow-hidden shadow-2xs">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id} className="bg-slate-50/75 border-slate-200 hover:bg-slate-50/75">
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id} className="text-xs font-semibold text-slate-700 h-10">
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {loading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <TableRow key={i} className="border-slate-100">
                  <TableCell><Skeleton className="h-4 w-36" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-28" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-7 w-16" /></TableCell>
                </TableRow>
              ))
            ) : table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  onClick={() => handleOpenInspector(row.original.id)}
                  className="cursor-pointer hover:bg-slate-50/80 transition-colors border-slate-100"
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id} className="py-3">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-48 text-center">
                  <div className="flex flex-col items-center justify-center text-slate-400 space-y-2">
                    <Users className="h-8 w-8 text-slate-300 stroke-[1.5]" />
                    <p className="text-sm font-medium text-slate-600">No matching prospects found</p>
                    <p className="text-xs text-slate-400 max-w-sm">
                      Try clearing filters or search queries. New inbound prospects will appear automatically.
                    </p>
                  </div>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination controls */}
      {table.getPageCount() > 1 && (
        <div className="flex items-center justify-between px-2 text-xs text-slate-500">
          <div>
            Showing Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()} (Total {leads.length} records)
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="h-8 text-xs bg-white border-slate-200"
            >
              <ChevronLeft className="h-3.5 w-3.5 mr-1" />
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="h-8 text-xs bg-white border-slate-200"
            >
              Next
              <ChevronRight className="h-3.5 w-3.5 ml-1" />
            </Button>
          </div>
        </div>
      )}

      {/* LEAD INSPECTOR SHEET */}
      <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
        <SheetContent className="w-full sm:max-w-xl md:max-w-2xl bg-white border-l border-slate-200 p-0 overflow-y-auto">
          <SheetHeader className="sr-only">
            <SheetTitle>Prospect Inspector</SheetTitle>
            <SheetDescription>Detailed lead signals, score factor breakdown, and assignment controls</SheetDescription>
          </SheetHeader>

          {loadingDetail || !leadDetail ? (
            <div className="p-6 space-y-4">
              <Skeleton className="h-8 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
              <Skeleton className="h-48 w-full" />
            </div>
          ) : (
            <div className="flex flex-col h-full">
              {/* Sheet Top Info */}
              <div className="p-6 border-b border-slate-200 bg-white space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-lg font-bold text-slate-900">
                      {leadDetail.name || "Anonymous Prospect"}
                    </h2>
                    <p className="text-xs text-slate-500 font-mono">ID: {leadDetail.id}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {leadDetail.can_contact ? (
                      <Badge variant="success" className="text-xs py-1">
                        <ShieldCheck className="h-3 w-3 mr-1" />
                        DPDP Consented
                      </Badge>
                    ) : (
                      <Badge variant="warning" className="text-xs py-1">
                        <ShieldAlert className="h-3 w-3 mr-1" />
                        Contact Blocked
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs bg-slate-50 p-3 rounded-lg border border-slate-100">
                  <div>
                    <span className="text-slate-400 block text-[11px]">Email</span>
                    <span className="font-medium text-slate-800 truncate block">
                      {leadDetail.email || "—"}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Phone</span>
                    <span className="font-mono text-slate-800 block">
                      {leadDetail.phone || "—"}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Segment</span>
                    <span className="font-medium text-slate-800 block capitalize">
                      {leadDetail.segment.replace(/_/g, " ")}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Target Insurance</span>
                    <span className="font-medium text-slate-800 block capitalize">
                      {leadDetail.target_insurance_type?.replace(/_/g, " ") || "Not Specified"}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Source Attribution</span>
                    <span className="font-medium text-slate-800 block">
                      {leadDetail.source_name || "web_direct"}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Signals Ingested</span>
                    <span className="font-semibold text-slate-800 block">
                      {leadDetail.signals_count} events
                    </span>
                  </div>
                </div>

                {/* Score Banner & Recalculate */}
                <div className="flex items-center justify-between bg-blue-50/60 border border-blue-200/80 p-3 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-white font-bold text-sm shadow-xs">
                      {Math.round(leadDetail.latest_score?.score ?? 0)}
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-slate-900">Deterministic Lead Score</p>
                      <p className="text-[11px] text-slate-500">
                        Calculated {formatDate(leadDetail.latest_score?.calculated_at)}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRecalculateScore}
                    disabled={recalculatingScore}
                    className="h-8 text-xs bg-white text-blue-700 border-blue-200 hover:bg-blue-50"
                  >
                    <RotateCw className={`h-3 w-3 mr-1 ${recalculatingScore ? "animate-spin" : ""}`} />
                    Recalculate
                  </Button>
                </div>
              </div>

              {/* Sheet Tabs */}
              <div className="p-6 flex-1">
                <Tabs defaultValue="timeline" className="w-full">
                  <TabsList className="grid w-full grid-cols-4 bg-slate-100 p-1 mb-4">
                    <TabsTrigger value="timeline" className="text-xs">Timeline</TabsTrigger>
                    <TabsTrigger value="scoring" className="text-xs">Score Factors</TabsTrigger>
                    <TabsTrigger value="signals" className="text-xs">Signals</TabsTrigger>
                    <TabsTrigger value="advisor" className="text-xs">Advisor</TabsTrigger>
                  </TabsList>

                  {/* Tab a: Activity Timeline */}
                  <TabsContent value="timeline" className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
                        <Clock className="h-3.5 w-3.5 text-slate-400" />
                        Chronological Event Log
                      </h3>
                      <span className="text-[11px] text-slate-400">
                        {timelineEvents.length} events recorded
                      </span>
                    </div>

                    {timelineEvents.length === 0 ? (
                      <div className="p-8 text-center border border-dashed border-slate-200 rounded-lg text-slate-400 text-xs">
                        No timeline events logged yet for this prospect.
                      </div>
                    ) : (
                      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                        {timelineEvents.map((evt, idx) => (
                          <div key={idx} className="relative group">
                            {/* Dot icon */}
                            <div className="absolute -left-6 top-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-white border border-slate-300 shadow-2xs group-hover:border-blue-500 transition-colors">
                              {evt.event_type.includes("CONSENT") ? (
                                <ShieldCheck className="h-3 w-3 text-emerald-600" />
                              ) : evt.event_type.includes("SCORE") ? (
                                <Sparkles className="h-3 w-3 text-amber-500" />
                              ) : evt.event_type.includes("ADVISOR") ? (
                                <UserCheck className="h-3 w-3 text-blue-600" />
                              ) : evt.event_type.includes("AI") ? (
                                <Bot className="h-3 w-3 text-purple-600" />
                              ) : (
                                <Activity className="h-3 w-3 text-slate-400" />
                              )}
                            </div>
                            <div className="bg-white border border-slate-200 p-3 rounded-lg shadow-2xs space-y-1">
                              <div className="flex items-center justify-between">
                                <span className="text-xs font-semibold text-slate-900">{evt.title}</span>
                                <span className="text-[10px] text-slate-400 font-mono">
                                  {formatDate(evt.timestamp)}
                                </span>
                              </div>
                              <p className="text-xs text-slate-600">{evt.description}</p>
                              {evt.actor && (
                                <span className="text-[10px] text-slate-400 block">
                                  Actor: {evt.actor}
                                </span>
                              )}
                              {evt.metadata && Object.keys(evt.metadata).length > 0 && (
                                <pre className="text-[10px] bg-slate-50 p-1.5 rounded border border-slate-100 text-slate-600 font-mono mt-1 overflow-x-auto">
                                  {JSON.stringify(evt.metadata, null, 2)}
                                </pre>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </TabsContent>

                  {/* Tab b: Score Factor Breakdown */}
                  <TabsContent value="scoring" className="space-y-4">
                    <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2">
                      <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
                        <span>Overall Score Integrity</span>
                        <span className="font-mono text-sm text-blue-700">
                          {Math.round(leadDetail.latest_score?.score ?? 0)} / 100
                        </span>
                      </div>
                      <Progress
                        value={leadDetail.latest_score?.score ?? 0}
                        className="h-2 bg-slate-200"
                      />
                      <p className="text-[11px] text-slate-500">
                        Deterministic point evaluation calculated from database rules. Clamped between 0 and 100.
                      </p>
                    </div>

                    <div className="space-y-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600">
                        Contributing Factor Breakdown
                      </h4>

                      {leadDetail.latest_score?.factors && leadDetail.latest_score.factors.length > 0 ? (
                        <div className="space-y-2">
                          {leadDetail.latest_score.factors.map((factor, idx) => (
                            <div
                              key={idx}
                              className="bg-white border border-slate-200 p-3 rounded-lg flex items-start justify-between gap-3 shadow-2xs"
                            >
                              <div className="space-y-1">
                                <div className="flex items-center gap-2">
                                  <span className="text-xs font-semibold text-slate-900">
                                    {factor.rule_name}
                                  </span>
                                  <Badge variant="outline" className="text-[10px] text-slate-500 uppercase">
                                    {factor.category}
                                  </Badge>
                                </div>
                                <p className="text-xs text-slate-600">{factor.rationale}</p>
                                <span className="text-[10px] font-mono text-slate-400 block">
                                  Rule: {factor.rule_code}
                                </span>
                              </div>
                              <span
                                className={`text-xs font-bold px-2 py-0.5 rounded ${
                                  factor.points_awarded > 0
                                    ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                                    : factor.points_awarded < 0
                                    ? "bg-red-50 text-red-700 border border-red-200"
                                    : "bg-slate-100 text-slate-600"
                                }`}
                              >
                                {factor.points_awarded > 0 ? `+${factor.points_awarded}` : factor.points_awarded} pts
                              </span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="p-6 text-center border border-dashed border-slate-200 rounded-lg text-slate-400 text-xs">
                          No factor breakdown recorded for current score evaluation.
                        </div>
                      )}
                    </div>
                  </TabsContent>

                  {/* Tab c: Behavioral Signals */}
                  <TabsContent value="signals" className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600">
                        Client-Side Engagement Footprint
                      </h4>
                      <span className="text-[11px] text-slate-400 font-mono">
                        Total {leadDetail.signals?.length || leadDetail.signals_count || 0} signals
                      </span>
                    </div>

                    {leadDetail.signals && leadDetail.signals.length > 0 ? (
                      <div className="space-y-2">
                        {leadDetail.signals.map((sig, idx) => (
                          <div
                            key={idx}
                            className="bg-white border border-slate-200 p-3 rounded-lg space-y-1.5 shadow-2xs text-xs"
                          >
                            <div className="flex items-center justify-between">
                              <Badge className="bg-slate-100 text-slate-800 border-slate-200 font-mono text-[11px]">
                                {sig.signal_type}
                              </Badge>
                              <span className="text-[10px] text-slate-400 font-mono">
                                {formatDate(sig.created_at)}
                              </span>
                            </div>
                            <div className="text-[11px] text-slate-500 font-mono">
                              Session: {sig.session_id}
                            </div>
                            {(sig.payload_json || sig.payload) && (
                              <pre className="text-[10px] bg-slate-50 p-2 rounded border border-slate-100 font-mono text-slate-700 overflow-x-auto max-h-32">
                                {JSON.stringify(sig.payload_json || sig.payload, null, 2)}
                              </pre>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-6 text-center border border-dashed border-slate-200 rounded-lg text-slate-400 text-xs">
                        No raw behavioral signals ingested yet. Signals ingest during visitor web engagement.
                      </div>
                    )}
                  </TabsContent>

                  {/* Tab d: Advisor Assignment */}
                  <TabsContent value="advisor" className="space-y-4">
                    <div className="bg-white border border-slate-200 rounded-lg p-4 space-y-3 shadow-2xs">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                          Current Assignment
                        </span>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={handleOpenAssignDialog}
                          className="h-8 text-xs text-blue-600 border-blue-200 hover:bg-blue-50"
                        >
                          <UserCheck className="h-3.5 w-3.5 mr-1" />
                          {leadDetail.assigned_advisor_id ? "Reassign Advisor" : "Assign Advisor"}
                        </Button>
                      </div>

                      {leadDetail.assigned_advisor_id ? (
                        <div className="p-3 bg-slate-50 rounded-md border border-slate-200 space-y-2">
                          <div className="flex items-center gap-2">
                            <UserCheck className="h-4 w-4 text-emerald-600" />
                            <span className="text-sm font-bold text-slate-900">
                              {leadDetail.assigned_advisor_name || "Assigned Advisor"}
                            </span>
                          </div>
                          <p className="text-xs text-slate-500">
                            Assigned on: {formatDate(leadDetail.assigned_at)}
                          </p>
                        </div>
                      ) : (
                        <div className="p-4 text-center border border-dashed border-slate-200 rounded-lg text-slate-500 text-xs">
                          This prospect is currently unassigned. Click &quot;Assign Advisor&quot; to allocate based on workload.
                        </div>
                      )}
                    </div>

                    {/* Advisor Capacity Overview */}
                    <div className="space-y-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600">
                        Active Advisor Workload & Capacity
                      </h4>
                      <div className="space-y-2 max-h-60 overflow-y-auto">
                        {advisors.map((adv) => {
                          const loadRatio =
                            adv.max_active_cases > 0
                              ? Math.min(100, Math.round((adv.current_active_cases / adv.max_active_cases) * 100))
                              : 0;
                          const isFull = adv.current_active_cases >= adv.max_active_cases;
                          return (
                            <div
                              key={adv.id}
                              className="bg-white border border-slate-200 p-3 rounded-lg text-xs space-y-1.5 shadow-2xs"
                            >
                              <div className="flex items-center justify-between">
                                <span className="font-semibold text-slate-900">{adv.name}</span>
                                <Badge
                                  variant={isFull ? "destructive" : "outline"}
                                  className="text-[10px]"
                                >
                                  {adv.current_active_cases} / {adv.max_active_cases} cases ({loadRatio}%)
                                </Badge>
                              </div>
                              <Progress value={loadRatio} className="h-1.5 bg-slate-100" />
                              <div className="flex items-center justify-between text-[11px] text-slate-400">
                                <span>Lic: {adv.license_number}</span>
                                <span>{Array.isArray(adv.specializations) ? adv.specializations.join(", ") : adv.specializations || "General"}</span>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>

      {/* ADVISOR REASSIGNMENT DIALOG */}
      <Dialog open={isAssignDialogOpen} onOpenChange={setIsAssignDialogOpen}>
        <DialogContent className="sm:max-w-md bg-white border border-slate-200">
          <DialogHeader>
            <DialogTitle className="text-base font-bold text-slate-900">
              Reassign Insurance Advisor
            </DialogTitle>
            <DialogDescription className="text-xs text-slate-500">
              Select an active advisor respecting capacity constraints. Every assignment is logged in the audit trail.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-2">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-700">Select Available Advisor</label>
              <Select value={selectedAdvisorId} onValueChange={setSelectedAdvisorId}>
                <SelectTrigger className="h-9 text-xs bg-white border-slate-200">
                  <SelectValue placeholder="Choose an advisor..." />
                </SelectTrigger>
                <SelectContent>
                  {advisors.map((adv) => {
                    const isFull = adv.current_active_cases >= adv.max_active_cases;
                    return (
                      <SelectItem
                        key={adv.id}
                        value={adv.id}
                        disabled={isFull}
                        className="text-xs"
                      >
                        {adv.name} — {adv.current_active_cases}/{adv.max_active_cases} cases {isFull ? "(Full)" : ""}
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-700">
                Reassignment Reason (Mandatory Audit Trail)
              </label>
              <Input
                placeholder="e.g. Workload rebalancing or specialized product match"
                value={reassignmentReason}
                onChange={(e) => setReassignmentReason(e.target.value)}
                className="h-9 text-xs bg-white border-slate-200"
              />
            </div>
          </div>

          <DialogFooter className="gap-2 sm:gap-0">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsAssignDialogOpen(false)}
              className="text-xs border-slate-200"
            >
              Cancel
            </Button>
            <Button
              size="sm"
              onClick={handleConfirmAssignment}
              disabled={assigningLoading || !selectedAdvisorId}
              className="text-xs bg-blue-600 hover:bg-blue-700 text-white"
            >
              {assigningLoading ? "Assigning..." : "Confirm Assignment"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
