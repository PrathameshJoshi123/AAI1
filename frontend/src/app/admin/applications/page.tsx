"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ApplicationAPI } from "@/services/application.service";
import { ApplicationItem } from "@/types/application";
import { RefreshCw, ClipboardList, AlertCircle, ExternalLink } from "lucide-react";

export default function AdminApplicationsPage() {
  const [applications, setApplications] = useState<ApplicationItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadApplications = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await ApplicationAPI.listApplications();
      setApplications(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load applications.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadApplications();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "approved":
        return <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200">Approved</Badge>;
      case "under_review":
        return <Badge className="bg-blue-50 text-blue-700 border-blue-200">Under Review</Badge>;
      case "submitted":
        return <Badge className="bg-indigo-50 text-indigo-700 border-indigo-200">Submitted</Badge>;
      case "declined":
        return <Badge className="bg-rose-50 text-rose-700 border-rose-200">Declined</Badge>;
      case "more_info_required":
        return <Badge className="bg-amber-50 text-amber-700 border-amber-200">Info Requested</Badge>;
      case "draft":
      default:
        return <Badge variant="outline" className="text-slate-500">Draft</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Global Application & Proposal Pipeline"
        description="Comprehensive monitoring of customer proposals across all underwriting and issuance stages."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Application Pipeline" },
        ]}
        actions={
          <Button variant="outline" size="sm" onClick={loadApplications} disabled={isLoading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        }
      />

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg text-sm text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      <Card className="bg-white border-slate-200 shadow-sm">
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-3">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : applications.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-sm">
              No insurance applications or proposals found in the database.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50/50">
                  <TableHead className="font-semibold text-xs text-slate-700">Application #</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700">Customer ID</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700">Product</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700">Step Progress</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700">Status</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700">Submitted At</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700 text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {applications.map((app) => (
                  <TableRow key={app.id} className="hover:bg-slate-50/50">
                    <TableCell className="font-mono text-xs font-bold text-slate-900">
                      {app.application_number || app.id.slice(0, 8)}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-slate-500">
                      {app.customer_id.slice(0, 8)}...
                    </TableCell>
                    <TableCell className="text-xs font-semibold text-slate-700">
                      {app.product_id ? app.product_id.slice(0, 12) : "Standard Plan"}
                    </TableCell>
                    <TableCell className="text-xs text-slate-600">
                      Step {app.current_step} of 6
                    </TableCell>
                    <TableCell>{getStatusBadge(app.status)}</TableCell>
                    <TableCell className="text-xs text-slate-500 whitespace-nowrap">
                      {app.submitted_at ? new Date(app.submitted_at).toLocaleDateString() : "Draft"}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button size="sm" variant="ghost" asChild className="h-7 text-xs text-blue-600">
                        <Link href={`/advisor/cases/${app.id}`}>
                          Inspect <ExternalLink className="w-3 h-3 ml-1" />
                        </Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
