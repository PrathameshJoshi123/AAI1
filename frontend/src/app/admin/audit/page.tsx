"use client";

import React, { useEffect, useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { AuditFilterPanel } from "@/components/admin/audit-filter-panel";
import { AdminAPI } from "@/services/admin.service";
import { AuditLogRecord } from "@/types/admin";
import { RefreshCw, Shield, AlertCircle, FileText, ChevronLeft, ChevronRight } from "lucide-react";

export default function AdminAuditPage() {
  const [records, setRecords] = useState<AuditLogRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [size] = useState(20);
  const [filters, setFilters] = useState<{ action?: string; resource_type?: string; resource_id?: string }>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedChanges, setSelectedChanges] = useState<{ id: number; data: Record<string, unknown> } | null>(null);

  const loadAuditLogs = async (currentPage = page, currentFilters = filters) => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await AdminAPI.searchAuditLogs({
        ...currentFilters,
        page: currentPage,
        size,
      });
      setRecords(res.records);
      setTotal(res.total);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load audit records.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAuditLogs(page, filters);
  }, [page]);

  const handleSearch = (newFilters: { action?: string; resource_type?: string; resource_id?: string }) => {
    setFilters(newFilters);
    setPage(1);
    loadAuditLogs(1, newFilters);
  };

  const handleReset = () => {
    setFilters({});
    setPage(1);
    loadAuditLogs(1, {});
  };

  const handleExport = () => {
    const API_BASE = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";
    const token = localStorage.getItem("token") || localStorage.getItem("auth_token") || "";
    const params = new URLSearchParams();
    if (filters.action) params.set("action", filters.action);
    if (filters.resource_type) params.set("resource_type", filters.resource_type);
    window.open(`${API_BASE}/api/v1/admin/audit/export?${params.toString()}`, "_blank");
  };

  const totalPages = Math.ceil(total / size) || 1;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Regulatory Compliance & Audit Vault"
        description="Searchable, immutable audit records for regulatory oversight, data access, and IRDAI compliance."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Compliance & Audit" },
        ]}
        actions={
          <Button variant="outline" size="sm" onClick={() => loadAuditLogs(page, filters)} disabled={isLoading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isLoading ? "animate-spin" : ""}`} />
            Refresh Logs
          </Button>
        }
      />

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg text-sm text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {/* Filter Bar */}
      <AuditFilterPanel onSearch={handleSearch} onReset={handleReset} onExport={handleExport} />

      {/* Audit Table */}
      <Card className="bg-white border-slate-200 shadow-sm">
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-3">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : records.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-sm">
              No audit records matching the search criteria.
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-50/50">
                    <TableHead className="text-xs font-semibold">Timestamp</TableHead>
                    <TableHead className="text-xs font-semibold">User / Actor</TableHead>
                    <TableHead className="text-xs font-semibold">Action Event</TableHead>
                    <TableHead className="text-xs font-semibold">Target Resource</TableHead>
                    <TableHead className="text-xs font-semibold">Resource ID</TableHead>
                    <TableHead className="text-xs font-semibold">IP Address</TableHead>
                    <TableHead className="text-xs font-semibold text-right">State Diff</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {records.map((log) => (
                    <TableRow key={log.id} className="hover:bg-slate-50/50">
                      <TableCell className="text-xs font-mono text-slate-500 whitespace-nowrap">
                        {new Date(log.timestamp).toLocaleString()}
                      </TableCell>
                      <TableCell className="text-xs font-medium text-slate-800">
                        {log.user_email || "System/Anonymous"}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="font-mono text-[10px] border-slate-300 text-slate-700">
                          {log.action}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-xs font-semibold text-slate-700">
                        {log.resource_type}
                      </TableCell>
                      <TableCell className="text-xs font-mono text-slate-500">
                        {log.resource_id}
                      </TableCell>
                      <TableCell className="text-xs font-mono text-slate-400">
                        {log.ip_address || "127.0.0.1"}
                      </TableCell>
                      <TableCell className="text-right">
                        {log.changes_json ? (
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-7 text-xs text-blue-600"
                            onClick={() => setSelectedChanges({ id: log.id, data: log.changes_json || {} })}
                          >
                            <FileText className="w-3 h-3 mr-1" />
                            Diff
                          </Button>
                        ) : (
                          <span className="text-xs text-slate-400">—</span>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination bar */}
              <div className="p-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span>
                  Showing page <strong>{page}</strong> of <strong>{totalPages}</strong> ({total.toLocaleString()} total entries)
                </span>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-8"
                    disabled={page <= 1 || isLoading}
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                  >
                    <ChevronLeft className="w-3.5 h-3.5 mr-1" /> Previous
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-8"
                    disabled={page >= totalPages || isLoading}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    Next <ChevronRight className="w-3.5 h-3.5 ml-1" />
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Changes JSON Diff Modal */}
      {selectedChanges && (
        <Dialog open={true} onOpenChange={() => setSelectedChanges(null)}>
          <DialogContent className="max-w-xl max-h-[80vh] overflow-y-auto bg-white border-slate-200">
            <DialogHeader>
              <DialogTitle className="text-sm font-bold text-slate-900">
                Audit Record Diff #{selectedChanges.id}
              </DialogTitle>
            </DialogHeader>
            <pre className="p-3 bg-slate-50 border border-slate-200 rounded-md text-xs font-mono text-slate-800 overflow-x-auto">
              {JSON.stringify(selectedChanges.data, null, 2)}
            </pre>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
