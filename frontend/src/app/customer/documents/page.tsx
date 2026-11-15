"use client";

import * as React from "react";
import { FolderOpen, ShieldCheck, Loader2, UploadCloud, RefreshCw, AlertCircle } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { DocumentTable } from "@/components/customer/documents/document-table";
import { DocumentAPI } from "@/services/document.service";
import { DocumentItem } from "@/types/document";

export default function CustomerDocumentsPage() {
  const [documents, setDocuments] = React.useState<DocumentItem[]>([]);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);

  const loadDocuments = React.useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const docs = await DocumentAPI.listCustomerDocuments();
      setDocuments(docs);
    } catch (err: any) {
      setError(err.message || "Failed to load documents.");
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const verifiedCount = documents.filter((d) => d.verification_status === "verified").length;
  const pendingCount = documents.filter((d) => d.verification_status === "pending" || d.verification_status === "extracted").length;
  const rejectedCount = documents.filter((d) => d.verification_status === "rejected").length;

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <PageHeader
          title="Customer KYC & Document Vault"
          description="Centralized repository of identity, address, income, and medical records secured with SHA-256 cryptographic verification."
          breadcrumbs={[
            { label: "Customer Portal", href: "/customer" },
            { label: "Document Vault" },
          ]}
        />
        <Button
          variant="outline"
          size="sm"
          onClick={loadDocuments}
          disabled={loading}
          className="text-xs self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} /> Refresh Vault
        </Button>
      </div>

      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-md flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Metrics Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="border-slate-200 bg-white shadow-2xs">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-medium text-slate-500 uppercase">Verified Documents</p>
              <p className="text-xl font-bold text-emerald-600 mt-1">{verifiedCount}</p>
            </div>
            <div className="w-9 h-9 rounded-full bg-emerald-50 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-emerald-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200 bg-white shadow-2xs">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-medium text-slate-500 uppercase">Underwriting Review</p>
              <p className="text-xl font-bold text-blue-600 mt-1">{pendingCount}</p>
            </div>
            <div className="w-9 h-9 rounded-full bg-blue-50 flex items-center justify-center">
              <FolderOpen className="w-5 h-5 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200 bg-white shadow-2xs">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-medium text-slate-500 uppercase">Action Required</p>
              <p className="text-xl font-bold text-rose-600 mt-1">{rejectedCount}</p>
            </div>
            <div className="w-9 h-9 rounded-full bg-rose-50 flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-rose-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Document List */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-slate-900">Stored Verification Records</h3>
        {loading ? (
          <div className="flex flex-col items-center justify-center min-h-[200px] space-y-2">
            <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
            <p className="text-xs text-slate-500">Loading document vault...</p>
          </div>
        ) : (
          <DocumentTable documents={documents} />
        )}
      </div>
    </div>
  );
}
