"use client";

import * as React from "react";
import { Mail, RefreshCw, Search, CheckCircle2, AlertCircle, Clock, Ban } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AdminAPI } from "@/services/admin.service";

interface EmailDeliveryLogItem {
  id: number;
  user_id?: string;
  recipient_email: string;
  subject: string;
  template_name: string;
  status: string;
  error_message?: string;
  sent_at?: string;
  created_at: string;
}

export function EmailDeliveryLogTable() {
  const [logs, setLogs] = React.useState<EmailDeliveryLogItem[]>([]);
  const [total, setTotal] = React.useState(0);
  const [loading, setLoading] = React.useState(true);
  const [statusFilter, setStatusFilter] = React.useState<string>("all");
  const [searchTerm, setSearchTerm] = React.useState("");
  const [page, setPage] = React.useState(1);

  const fetchLogs = React.useCallback(async () => {
    try {
      setLoading(true);
      const res = await AdminAPI.getEmailDeliveryLogs({
        page,
        page_size: 15,
        status: statusFilter === "all" ? undefined : statusFilter,
        search: searchTerm.trim() || undefined,
      });
      if (res && res.items) {
        setLogs(res.items);
        setTotal(res.total || 0);
      }
    } catch (err) {
      console.error("Failed to load email delivery audit logs:", err);
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter, searchTerm]);

  React.useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  const getStatusBadge = (status: string) => {
    const s = status.toUpperCase();
    if (s === "SENT") {
      return (
        <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200 font-semibold text-[11px]">
          <CheckCircle2 className="h-3 w-3 mr-1 text-emerald-600" />
          SENT
        </Badge>
      );
    }
    if (s === "NOT_CONFIGURED") {
      return (
        <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-200 font-semibold text-[11px]">
          <Clock className="h-3 w-3 mr-1 text-amber-600" />
          NOT CONFIG
        </Badge>
      );
    }
    if (s === "FAILED") {
      return (
        <Badge variant="outline" className="bg-rose-50 text-rose-700 border-rose-200 font-semibold text-[11px]">
          <AlertCircle className="h-3 w-3 mr-1 text-rose-600" />
          FAILED
        </Badge>
      );
    }
    if (s.includes("SUPPRESSED")) {
      return (
        <Badge variant="outline" className="bg-slate-100 text-slate-700 border-slate-300 font-semibold text-[11px]">
          <Ban className="h-3 w-3 mr-1 text-slate-500" />
          NO CONSENT
        </Badge>
      );
    }
    return <Badge variant="outline">{status}</Badge>;
  };

  return (
    <Card className="border-slate-200 bg-white shadow-2xs">
      <CardHeader className="p-5 pb-3">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Mail className="h-4 w-4 text-blue-600" />
              Email Notification Delivery Audit Log
            </CardTitle>
            <CardDescription className="text-xs text-slate-500 mt-0.5">
              Immutable ledger of transactional and advisory email dispatches with honest transmission status.
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchLogs()}
            disabled={loading}
            className="text-xs bg-white hover:bg-slate-50 border-slate-200 text-slate-700 h-8 self-start sm:self-auto"
          >
            <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />
            Refresh Logs
          </Button>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row items-center gap-3 pt-3">
          <div className="relative w-full sm:w-72">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-400" />
            <Input
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setPage(1);
              }}
              placeholder="Search recipient, subject, template..."
              className="pl-8 text-xs bg-white border-slate-200 h-8"
            />
          </div>
          <Select
            value={statusFilter}
            onValueChange={(val) => {
              setStatusFilter(val);
              setPage(1);
            }}
          >
            <SelectTrigger className="w-full sm:w-44 text-xs bg-white border-slate-200 h-8">
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Delivery Statuses</SelectItem>
              <SelectItem value="SENT">Sent Successfully</SelectItem>
              <SelectItem value="NOT_CONFIGURED">Not Configured (Dev)</SelectItem>
              <SelectItem value="FAILED">Failed Transmissions</SelectItem>
              <SelectItem value="SUPPRESSED_NO_CONSENT">Suppressed (No Consent)</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>

      <CardContent className="p-0 border-t border-slate-100">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader className="bg-slate-50/75">
              <TableRow className="border-b border-slate-200 hover:bg-transparent">
                <TableHead className="text-[11px] font-bold text-slate-700 uppercase tracking-wider py-2.5 pl-5">Timestamp</TableHead>
                <TableHead className="text-[11px] font-bold text-slate-700 uppercase tracking-wider py-2.5">Recipient</TableHead>
                <TableHead className="text-[11px] font-bold text-slate-700 uppercase tracking-wider py-2.5">Subject & Template</TableHead>
                <TableHead className="text-[11px] font-bold text-slate-700 uppercase tracking-wider py-2.5">Status</TableHead>
                <TableHead className="text-[11px] font-bold text-slate-700 uppercase tracking-wider py-2.5 pr-5">Diagnostic Detail</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody className="divide-y divide-slate-100">
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-xs text-slate-400">
                    Loading delivery audit log...
                  </TableCell>
                </TableRow>
              ) : logs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-xs text-slate-400">
                    No email notification delivery records found.
                  </TableCell>
                </TableRow>
              ) : (
                logs.map((log) => (
                  <TableRow key={log.id} className="hover:bg-slate-50/50">
                    <TableCell className="text-xs text-slate-500 py-3 pl-5 whitespace-nowrap">
                      {new Date(log.created_at).toLocaleString("en-IN", {
                        day: "2-digit",
                        month: "short",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </TableCell>
                    <TableCell className="text-xs font-semibold text-slate-900 py-3 whitespace-nowrap">
                      {log.recipient_email}
                    </TableCell>
                    <TableCell className="text-xs py-3 max-w-xs">
                      <p className="font-medium text-slate-800 truncate">{log.subject}</p>
                      <p className="text-[10px] text-blue-600 font-mono mt-0.5 uppercase tracking-wide">
                        {log.template_name}
                      </p>
                    </TableCell>
                    <TableCell className="py-3 whitespace-nowrap">
                      {getStatusBadge(log.status)}
                    </TableCell>
                    <TableCell className="text-xs text-slate-500 py-3 pr-5 max-w-sm truncate">
                      {log.error_message || (log.sent_at ? `Delivered at ${new Date(log.sent_at).toLocaleTimeString()}` : "Ready")}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        {/* Footer pagination info */}
        <div className="p-3.5 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 px-5">
          <span>Showing {logs.length} of {total} delivery events</span>
          <div className="flex gap-1">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="text-xs h-7 px-2.5 bg-white border-slate-200"
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={logs.length < 15}
              onClick={() => setPage((p) => p + 1)}
              className="text-xs h-7 px-2.5 bg-white border-slate-200"
            >
              Next
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

