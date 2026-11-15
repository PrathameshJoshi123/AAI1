"use client";

import React from "react";
import Link from "next/link";
import { ClipboardList, PlusCircle, RefreshCw, Loader2, AlertCircle } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { ApplicationAPI } from "@/services/application.service";
import { ApplicationItem } from "@/types/application";
import { ApplicationCard } from "@/components/customer/applications/application-card";

export default function CustomerApplicationsPage() {
  const [applications, setApplications] = React.useState<ApplicationItem[]>([]);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);

  const loadApplications = React.useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const apps = await ApplicationAPI.listApplications();
      setApplications(apps);
    } catch (err: any) {
      setError(err.message || "Failed to load applications.");
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadApplications();
  }, [loadApplications]);

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <PageHeader
          title="Insurance Applications"
          description="Track proposal submissions, document verification, and underwriting approval progress in real time."
          breadcrumbs={[
            { label: "Customer Portal", href: "/customer" },
            { label: "Applications" },
          ]}
          actions={
            <Button size="sm" asChild className="bg-blue-600 hover:bg-blue-700 text-white text-xs">
              <Link href="/customer/quotes">
                <PlusCircle className="h-3.5 w-3.5 mr-1.5" />
                Start From Quote
              </Link>
            </Button>
          }
        />
        <Button
          variant="outline"
          size="sm"
          onClick={loadApplications}
          disabled={loading}
          className="text-xs self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} /> Refresh
        </Button>
      </div>

      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-md flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="flex flex-col items-center justify-center min-h-[300px] space-y-2">
          <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
          <p className="text-xs text-slate-500">Loading your applications...</p>
        </div>
      ) : applications.length === 0 ? (
        <EmptyState
          icon={ClipboardList}
          title="No Applications In Progress"
          description="When you choose a quote and complete the proposal questions, your application tracker will display live underwriting milestones here."
          actionLabel="Explore Plans"
          onAction={() => window.location.assign("/customer/explore")}
        />
      ) : (
        <div className="space-y-3">
          {applications.map((app) => (
            <ApplicationCard key={app.id} application={app} />
          ))}
        </div>
      )}
    </div>
  );
}
