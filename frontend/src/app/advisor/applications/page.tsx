"use client";

import * as React from "react";
import Link from "next/link";
import {
  ClipboardList,
  Search,
  Filter,
  ArrowRight,
  Clock,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Eye,
  FileText,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { advisorService } from "@/services/advisor-service";

interface AppItem {
  id: string;
  application_number: string;
  customer_id: string;
  quote_id: string;
  product_id: string;
  status: string;
  current_step: number;
  submitted_at?: string | null;
  created_at: string;
}

export default function AdvisorApplicationsPage() {
  const [apps, setApps] = React.useState<AppItem[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [search, setSearch] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState("all");

  const loadApps = React.useCallback(async () => {
    try {
      setLoading(true);
      const res = await advisorService.getApplications();
      setApps(res);
    } catch (err) {
      console.error("Failed to load applications:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadApps();
  }, [loadApps]);

  const filtered = apps.filter((a) => {
    const matchesSearch =
      a.application_number?.toLowerCase().includes(search.toLowerCase()) ||
      a.id?.toLowerCase().includes(search.toLowerCase());
    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "in_review" && (a.status === "under_review" || a.status === "submitted")) ||
      a.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <PageHeader
          title="Application Pipeline Management"
          description="Track customer proposals across onboarding stages, submission checksums, and underwriting readiness."
          breadcrumbs={[
            { label: "Advisor Workbench", href: "/advisor" },
            { label: "Applications" },
          ]}
        />
        <Button
          variant="outline"
          size="sm"
          onClick={loadApps}
          disabled={loading}
          className="h-9 gap-1.5 text-xs bg-white border-slate-200 self-start sm:self-auto"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <Tabs value={statusFilter} onValueChange={setStatusFilter} className="w-full sm:w-auto">
          <TabsList className="bg-slate-100 p-1 border border-slate-200 text-xs">
            <TabsTrigger value="all" className="text-xs">All Proposals</TabsTrigger>
            <TabsTrigger value="in_review" className="text-xs">Under Review</TabsTrigger>
            <TabsTrigger value="additional_info_required" className="text-xs">Info Required</TabsTrigger>
            <TabsTrigger value="approved" className="text-xs">Approved</TabsTrigger>
            <TabsTrigger value="draft" className="text-xs">Drafts</TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="relative w-full sm:w-64">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search by application #..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 h-9 text-xs bg-white border-slate-200"
          />
        </div>
      </div>

      {/* Table */}
      <Card className="bg-white border-slate-200">
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="bg-slate-50/50">
                <TableHead className="text-xs font-semibold">Application Number</TableHead>
                <TableHead className="text-xs font-semibold">Current Step</TableHead>
                <TableHead className="text-xs font-semibold">Status</TableHead>
                <TableHead className="text-xs font-semibold">Submitted Date</TableHead>
                <TableHead className="text-xs font-semibold text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-12 text-xs text-slate-400">
                    Loading proposal pipeline...
                  </TableCell>
                </TableRow>
              ) : filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-12 text-xs text-slate-400">
                    No applications matching current filters.
                  </TableCell>
                </TableRow>
              ) : (
                filtered.map((app) => (
                  <TableRow key={app.id} className="hover:bg-slate-50/70 transition-colors">
                    <TableCell className="font-semibold text-xs text-slate-900">
                      {app.application_number}
                    </TableCell>
                    <TableCell className="text-xs text-slate-600">
                      Step {app.current_step} of 8
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className={
                          app.status === "approved"
                            ? "bg-emerald-50 text-emerald-700 border-emerald-200 text-[11px]"
                            : app.status === "rejected"
                            ? "bg-red-50 text-red-700 border-red-200 text-[11px]"
                            : app.status === "additional_info_required"
                            ? "bg-amber-50 text-amber-700 border-amber-200 text-[11px]"
                            : app.status === "submitted" || app.status === "under_review"
                            ? "bg-blue-50 text-blue-700 border-blue-200 text-[11px]"
                            : "bg-slate-50 text-slate-700 border-slate-200 text-[11px]"
                        }
                      >
                        {app.status.replace(/_/g, " ").toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-xs text-slate-500">
                      {app.submitted_at
                        ? new Date(app.submitted_at).toLocaleDateString("en-IN", {
                            month: "short",
                            day: "numeric",
                            year: "numeric",
                          })
                        : "Draft in progress"}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button size="sm" variant="ghost" asChild className="h-8 text-xs text-blue-600 hover:text-blue-700">
                        <Link href={`/customer/applications/${app.id}`}>
                          <Eye className="h-3.5 w-3.5 mr-1" /> View Form
                        </Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

