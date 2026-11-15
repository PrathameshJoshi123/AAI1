"use client";

import * as React from "react";
import {
  FileCheck,
  CheckCircle2,
  XCircle,
  Download,
  Search,
  Filter,
  RefreshCw,
  Eye,
  AlertTriangle,
  FileText,
  Shield,
  Clock,
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { advisorService } from "@/services/advisor-service";

interface DocItem {
  id: string;
  application_id: string;
  customer_id: string;
  document_type: string;
  version: number;
  file_name: string;
  file_path: string;
  file_size_bytes: number;
  mime_type: string;
  file_hash: string;
  verification_status: string;
  extracted_data_json?: Record<string, any> | null;
  ocr_confidence_score?: number | null;
  rejection_reason?: string | null;
  created_at: string;
}

export default function AdvisorDocumentsPage() {
  const [documents, setDocuments] = React.useState<DocItem[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [statusFilter, setStatusFilter] = React.useState("pending");
  const [search, setSearch] = React.useState("");

  // Inspect Modal State
  const [inspectDoc, setInspectDoc] = React.useState<DocItem | null>(null);
  const [actionLoading, setActionLoading] = React.useState(false);
  const [rejectionCode, setRejectionCode] = React.useState("ILLEGIBLE_SCAN");
  const [rejectionNotes, setRejectionNotes] = React.useState("");
  const [showRejectForm, setShowRejectForm] = React.useState(false);

  const loadDocuments = React.useCallback(async () => {
    try {
      setLoading(true);
      const res = await advisorService.getDocumentVerificationQueue(
        statusFilter === "all" ? undefined : statusFilter
      );
      setDocuments(res);
    } catch (err) {
      console.error("Failed to load documents queue:", err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  React.useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const handleVerify = async () => {
    if (!inspectDoc) return;
    try {
      setActionLoading(true);
      await advisorService.verifyDocument(inspectDoc.id);
      setInspectDoc(null);
      await loadDocuments();
    } catch (err: any) {
      alert(err?.message || "Failed to verify document.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!inspectDoc) return;
    try {
      setActionLoading(true);
      const fullReason = `[${rejectionCode}] ${rejectionNotes || "Document does not satisfy underwriting requirements."}`;
      await advisorService.rejectDocument(inspectDoc.id, fullReason);
      setInspectDoc(null);
      setShowRejectForm(false);
      setRejectionNotes("");
      await loadDocuments();
    } catch (err: any) {
      alert(err?.message || "Failed to reject document.");
    } finally {
      setActionLoading(false);
    }
  };

  const filtered = documents.filter(
    (d) =>
      d.file_name?.toLowerCase().includes(search.toLowerCase()) ||
      d.document_type?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <PageHeader
          title="Document Verification Station"
          description="Examine uploaded proof of identity, address, income disclosures, and medical records under IRDAI guidelines."
          breadcrumbs={[
            { label: "Advisor Workbench", href: "/advisor" },
            { label: "Document Verification" },
          ]}
        />
        <Button
          variant="outline"
          size="sm"
          onClick={loadDocuments}
          disabled={loading}
          className="h-9 gap-1.5 text-xs bg-white border-slate-200 self-start sm:self-auto"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <Tabs value={statusFilter} onValueChange={setStatusFilter} className="w-full sm:w-auto">
          <TabsList className="bg-slate-100 p-1 border border-slate-200 text-xs">
            <TabsTrigger value="pending" className="text-xs">Pending Verification</TabsTrigger>
            <TabsTrigger value="verified" className="text-xs">Verified</TabsTrigger>
            <TabsTrigger value="rejected" className="text-xs">Rejected</TabsTrigger>
            <TabsTrigger value="all" className="text-xs">All Documents</TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="relative w-full sm:w-64">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search by file name or type..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 h-9 text-xs bg-white border-slate-200"
          />
        </div>
      </div>

      <Card className="bg-white border-slate-200">
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="bg-slate-50/50">
                <TableHead className="text-xs font-semibold">Document Type</TableHead>
                <TableHead className="text-xs font-semibold">File Name</TableHead>
                <TableHead className="text-xs font-semibold">Size</TableHead>
                <TableHead className="text-xs font-semibold">SHA-256 Checksum</TableHead>
                <TableHead className="text-xs font-semibold">Status</TableHead>
                <TableHead className="text-xs font-semibold text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-12 text-xs text-slate-400">
                    Loading verification queue...
                  </TableCell>
                </TableRow>
              ) : filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-12 text-xs text-slate-400">
                    No documents awaiting review in this category.
                  </TableCell>
                </TableRow>
              ) : (
                filtered.map((doc) => (
                  <TableRow key={doc.id} className="hover:bg-slate-50/70 transition-colors">
                    <TableCell className="font-semibold text-xs text-slate-900">
                      {doc.document_type.replace(/_/g, " ").toUpperCase()}
                    </TableCell>
                    <TableCell className="text-xs text-slate-600 font-mono">
                      {doc.file_name}
                    </TableCell>
                    <TableCell className="text-xs text-slate-500">
                      {(doc.file_size_bytes / 1024).toFixed(1)} KB
                    </TableCell>
                    <TableCell className="text-xs text-slate-400 font-mono truncate max-w-[140px]">
                      {doc.file_hash.slice(0, 16)}...
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className={
                          doc.verification_status === "verified"
                            ? "bg-emerald-50 text-emerald-700 border-emerald-200 text-[11px]"
                            : doc.verification_status === "rejected"
                            ? "bg-red-50 text-red-700 border-red-200 text-[11px]"
                            : "bg-amber-50 text-amber-700 border-amber-200 text-[11px]"
                        }
                      >
                        {doc.verification_status.toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => {
                          setInspectDoc(doc);
                          setShowRejectForm(false);
                        }}
                        className="h-8 text-xs text-blue-600 hover:text-blue-700"
                      >
                        <Eye className="h-3.5 w-3.5 mr-1" /> Audit & Verify
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Inspection Modal */}
      {inspectDoc && (
        <Dialog open={!!inspectDoc} onOpenChange={() => setInspectDoc(null)}>
          <DialogContent className="max-w-2xl bg-white border-slate-200">
            <DialogHeader>
              <DialogTitle className="text-base font-bold text-slate-900 flex items-center justify-between">
                <span>Audit Document: {inspectDoc.document_type.replace(/_/g, " ").toUpperCase()}</span>
                <Badge variant="outline" className="text-xs">
                  Version {inspectDoc.version}
                </Badge>
              </DialogTitle>
              <DialogDescription className="text-xs text-slate-500 font-mono">
                SHA-256: {inspectDoc.file_hash}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-2 text-xs">
              <div className="grid grid-cols-2 gap-4 p-3 bg-slate-50 rounded-lg border border-slate-200">
                <div>
                  <span className="text-slate-400 block">File Name</span>
                  <span className="font-semibold text-slate-800">{inspectDoc.file_name}</span>
                </div>
                <div>
                  <span className="text-slate-400 block">MIME Type</span>
                  <span className="font-semibold text-slate-800">{inspectDoc.mime_type}</span>
                </div>
                <div>
                  <span className="text-slate-400 block">File Size</span>
                  <span className="font-semibold text-slate-800">
                    {(inspectDoc.file_size_bytes / 1024).toFixed(1)} KB
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block">Upload Timestamp</span>
                  <span className="font-semibold text-slate-800">
                    {new Date(inspectDoc.created_at).toLocaleString()}
                  </span>
                </div>
              </div>

              {/* OCR Discrepancy Reconciliation */}
              {inspectDoc.extracted_data_json && (
                <div className="p-3 bg-blue-50/60 rounded-lg border border-blue-200 space-y-1.5">
                  <span className="font-semibold text-blue-900 block">
                    OCR Extracted Attributes:
                  </span>
                  <pre className="text-[11px] text-blue-800 bg-white/70 p-2 rounded border border-blue-200 font-mono overflow-x-auto">
                    {JSON.stringify(inspectDoc.extracted_data_json, null, 2)}
                  </pre>
                </div>
              )}

              {/* Rejection Form toggle */}
              {showRejectForm ? (
                <div className="p-4 bg-red-50/70 border border-red-200 rounded-lg space-y-3">
                  <h4 className="font-semibold text-red-900">Specify Rejection Reason</h4>
                  <div>
                    <label className="text-[11px] font-semibold text-red-800 block mb-1">
                      Reason Code *
                    </label>
                    <Select value={rejectionCode} onValueChange={setRejectionCode}>
                      <SelectTrigger className="h-8 text-xs bg-white border-red-200">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ILLEGIBLE_SCAN">Illegible or Blurry Scan</SelectItem>
                        <SelectItem value="EXPIRED_DOCUMENT">Document Expired</SelectItem>
                        <SelectItem value="NAME_MISMATCH">Name Mismatch with Proposal</SelectItem>
                        <SelectItem value="INCOMPLETE_PAGES">Incomplete Document Pages</SelectItem>
                        <SelectItem value="FRAUD_SUSPICION">Suspicious or Altered Document</SelectItem>
                        <SelectItem value="OTHER">Other Compliance Exception</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-[11px] font-semibold text-red-800 block mb-1">
                      Instructions for Customer *
                    </label>
                    <Textarea
                      rows={2}
                      value={rejectionNotes}
                      onChange={(e) => setRejectionNotes(e.target.value)}
                      placeholder="Explain what the customer needs to re-upload..."
                      className="text-xs bg-white border-red-200"
                    />
                  </div>
                </div>
              ) : null}
            </div>

            <DialogFooter className="flex items-center justify-between sm:justify-between w-full">
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.open(`/api/v1/documents/${inspectDoc.id}/download`, "_blank")}
                className="text-xs gap-1.5 border-slate-200"
              >
                <Download className="h-3.5 w-3.5" /> Open Binary File
              </Button>

              <div className="flex items-center gap-2">
                {!showRejectForm ? (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowRejectForm(true)}
                      className="text-xs text-red-600 border-red-200 hover:bg-red-50"
                    >
                      <XCircle className="h-3.5 w-3.5 mr-1" /> Reject Document
                    </Button>
                    <Button
                      size="sm"
                      onClick={handleVerify}
                      disabled={actionLoading}
                      className="text-xs bg-emerald-600 hover:bg-emerald-700 text-white"
                    >
                      <CheckCircle2 className="h-3.5 w-3.5 mr-1" /> Approve & Mark Verified
                    </Button>
                  </>
                ) : (
                  <>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowRejectForm(false)}
                      className="text-xs"
                    >
                      Cancel
                    </Button>
                    <Button
                      size="sm"
                      onClick={handleReject}
                      disabled={actionLoading}
                      className="text-xs bg-red-600 hover:bg-red-700 text-white"
                    >
                      Confirm Rejection
                    </Button>
                  </>
                )}
              </div>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
