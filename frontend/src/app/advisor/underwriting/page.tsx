"use client";

import * as React from "react";
import Link from "next/link";
import {
  Scale,
  ShieldAlert,
  Search,
  Filter,
  ArrowRight,
  Clock,
  AlertTriangle,
  RefreshCw,
  Eye,
  CheckCircle2,
  XCircle,
  Briefcase,
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
import { underwritingService } from "@/services/underwriting-service";
import { UnderwritingCaseSummary } from "@/types/underwriting";

export default function UnderwritingTriagePage() {
  const [cases, setCases] = React.useState<UnderwritingCaseSummary[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [riskFilter, setRiskFilter] = React.useState("all");
  const [priorityFilter, setPriorityFilter] = React.useState("all");
  const [search, setSearch] = React.useState("");

  const loadCases = React.useCallback(async () => {
    try {
      setLoading(true);
      const res = await underwritingService.getTriageQueue({
        risk_rating: riskFilter === "all" ? undefined : riskFilter,
        priority: priorityFilter === "all" ? undefined : priorityFilter,
      });
      setCases(res);
    } catch (err) {
      console.error("Failed to load underwriting triage queue:", err);
    } finally {
      setLoading(false);
    }
  }, [riskFilter, priorityFilter]);

  React.useEffect(() => {
    loadCases();
  }, [loadCases]);

  const filtered = cases.filter(
    (c) =>
      c.customer_name?.toLowerCase().includes(search.toLowerCase()) ||
      c.case_number?.toLowerCase().includes(search.toLowerCase()) ||
      c.product_name?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <PageHeader
          title="Underwriting Risk Triage Matrix"
          description="Examine cases prioritized by actuarial risk rating, statutory disclosures, and SLA countdowns."
          breadcrumbs={[
            { label: "Advisor Workbench", href: "/advisor" },
            { label: "Underwriting Triage" },
          ]}
        />
        <Button
          variant="outline"
          size="sm"
          onClick={loadCases}
          disabled={loading}
          className="h-9 gap-1.5 text-xs bg-white border-slate-200 self-start sm:self-auto"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <Tabs value={riskFilter} onValueChange={setRiskFilter} className="w-full sm:w-auto">
          <TabsList className="bg-slate-100 p-1 border border-slate-200 text-xs">
            <TabsTrigger value="all" className="text-xs">All Risk Ratings</TabsTrigger>
            <TabsTrigger value="standard" className="text-xs">Standard</TabsTrigger>
            <TabsTrigger value="substandard" className="text-xs">Substandard</TabsTrigger>
            <TabsTrigger value="preferred" className="text-xs">Preferred</TabsTrigger>
            <TabsTrigger value="decline" className="text-xs">Decline Flags</TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="relative w-full sm:w-64">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search by case # or applicant..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 h-9 text-xs bg-white border-slate-200"
          />
        </div>
      </div>

      {/* Cases Table */}
      <Card className="bg-white border-slate-200">
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="bg-slate-50/50">
                <TableHead className="text-xs font-semibold">Case #</TableHead>
                <TableHead className="text-xs font-semibold">Applicant</TableHead>
                <TableHead className="text-xs font-semibold">Product & Sum Assured</TableHead>
                <TableHead className="text-xs font-semibold">Priority & SLA</TableHead>
                <TableHead className="text-xs font-semibold">Risk Rating</TableHead>
                <TableHead className="text-xs font-semibold">Status</TableHead>
                <TableHead className="text-xs font-semibold text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-12 text-xs text-slate-400">
                    Loading triage matrix...
                  </TableCell>
                </TableRow>
              ) : filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-12 text-xs text-slate-400">
                    No underwriting cases matching current triage filters.
                  </TableCell>
                </TableRow>
              ) : (
                filtered.map((c) => (
                  <TableRow key={c.id} className="hover:bg-slate-50/70 transition-colors">
                    <TableCell className="font-semibold text-xs text-slate-900 font-mono">
                      {c.case_number}
                    </TableCell>
                    <TableCell className="text-xs text-slate-800 font-medium">
                      {c.customer_name}
                    </TableCell>
                    <TableCell className="text-xs text-slate-600">
                      <div>{c.product_name}</div>
                      <span className="text-[11px] text-slate-400">₹{c.sum_assured.toLocaleString("en-IN")}</span>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-col gap-1 text-xs">
                        <Badge
                          variant="outline"
                          className={
                            c.priority === "urgent"
                              ? "bg-red-50 text-red-700 border-red-200 text-[10px] w-fit"
                              : c.priority === "high"
                              ? "bg-amber-50 text-amber-700 border-amber-200 text-[10px] w-fit"
                              : "bg-blue-50 text-blue-700 border-blue-200 text-[10px] w-fit"
                          }
                        >
                          {c.priority.toUpperCase()}
                        </Badge>
                        {typeof c.sla_hours_remaining === "number" && (
                          <span
                            className={`text-[10px] flex items-center gap-1 ${
                              c.sla_hours_remaining <= 4 ? "text-red-600 font-bold" : "text-slate-400"
                            }`}
                          >
                            <Clock className="h-3 w-3" />
                            {c.sla_hours_remaining > 0 ? `${c.sla_hours_remaining}h SLA left` : "SLA Breached"}
                          </span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1.5">
                        <Badge
                          variant="outline"
                          className={
                            c.risk_rating === "preferred"
                              ? "bg-emerald-50 text-emerald-700 border-emerald-200 text-[11px]"
                              : c.risk_rating === "substandard"
                              ? "bg-amber-50 text-amber-700 border-amber-200 text-[11px]"
                              : c.risk_rating === "decline"
                              ? "bg-red-50 text-red-700 border-red-200 text-[11px]"
                              : "bg-slate-50 text-slate-700 border-slate-200 text-[11px]"
                          }
                        >
                          {c.risk_rating.toUpperCase()}
                        </Badge>
                        {c.risk_flags_count > 0 && (
                          <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200 text-[10px] px-1">
                            {c.risk_flags_count} flags
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="bg-slate-100 text-slate-700 border-slate-300 text-[11px]">
                        {c.status.replace("_", " ").toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button size="sm" variant="outline" asChild className="h-8 text-xs gap-1 border-slate-200">
                        <Link href={`/advisor/cases/${c.case_number}`}>
                          <span>Open Dossier</span>
                          <ArrowRight className="h-3.5 w-3.5 ml-1" />
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
