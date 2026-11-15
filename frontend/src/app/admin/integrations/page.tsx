"use client";

import React, { useEffect, useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { IntegrationStatusCard } from "@/components/admin/integration-status-card";
import { SendTestEmailModal } from "@/components/admin/SendTestEmailModal";
import { EmailDeliveryLogTable } from "@/components/admin/EmailDeliveryLogTable";
import { AdminAPI } from "@/services/admin.service";

import { IntegrationHealth } from "@/types/admin";
import { RefreshCw, ShieldAlert, AlertCircle } from "lucide-react";

export default function AdminIntegrationsPage() {
  const [integrations, setIntegrations] = useState<IntegrationHealth[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [testingKey, setTestingKey] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadIntegrations = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await AdminAPI.checkIntegrations();
      setIntegrations(res.integrations);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to probe external integrations.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadIntegrations();
  }, []);

  const handleTest = async (serviceKey: string) => {
    try {
      setTestingKey(serviceKey);
      await AdminAPI.testIntegration(serviceKey);
      await loadIntegrations();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Connectivity probe failed.");
    } finally {
      setTestingKey(null);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Third-Party & Insurer Integration Console"
        description="Health monitoring, credentials status, and connection diagnostics for external service dependencies."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Integrations" },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <SendTestEmailModal onDispatched={loadIntegrations} />
            <Button variant="outline" size="sm" onClick={loadIntegrations} disabled={isLoading} className="text-xs border-slate-200">
              <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isLoading ? "animate-spin" : ""}`} />
              Re-probe All Services
            </Button>
          </div>
        }
      />


      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg text-sm text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {/* Honest Status Policy Banner */}
      <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-600 flex items-center gap-3">
        <ShieldAlert className="w-5 h-5 text-slate-400 shrink-0" />
        <p>
          <strong>Zero Fallback & Honest Status Policy:</strong> The system conducts active network and configuration checks against live credentials. Unconfigured integrations will never report simulated success.
        </p>
      </div>

      {/* Integrations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading ? (
          Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-44 rounded-lg bg-slate-100" />
          ))
        ) : integrations.length === 0 ? (
          <div className="col-span-3 p-12 text-center text-slate-400 text-sm">
            No integration health definitions found.
          </div>
        ) : (
          integrations.map((item) => (
            <IntegrationStatusCard
              key={item.service_key}
              integration={item}
              onTest={handleTest}
              isTesting={testingKey === item.service_key}
            />
          ))
        )}
      </div>

      {/* Phase 11: Live Email Delivery Audit Log Table */}
      <div className="pt-2">
        <EmailDeliveryLogTable />
      </div>
    </div>
  );
}


