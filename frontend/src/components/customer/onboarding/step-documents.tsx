"use client";

import React from "react";
import { DocumentItem, DocumentRequirement } from "@/types/document";
import { DocumentAPI } from "@/services/document.service";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  FileText,
  Upload,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileCheck2,
  ArrowLeft,
  Send,
  Loader2,
} from "lucide-react";

interface StepDocumentsProps {
  applicationId: string;
  requirements: DocumentRequirement[];
  existingDocuments: DocumentItem[];
  applicantName: string;
  onPrev: () => void;
  onSubmitProposal: (eSignatureName: string) => Promise<void>;
}

export function StepDocuments({
  applicationId,
  requirements,
  existingDocuments,
  applicantName,
  onPrev,
  onSubmitProposal,
}: StepDocumentsProps) {
  const [documents, setDocuments] = React.useState<DocumentItem[]>(existingDocuments);
  const [uploadingType, setUploadingType] = React.useState<string | null>(null);
  const [eSignature, setESignature] = React.useState<string>(applicantName || "");
  const [submitting, setSubmitting] = React.useState<boolean>(false);
  const [error, setError] = React.useState<string | null>(null);

  const handleFileUpload = async (req: DocumentRequirement, file: File) => {
    setError(null);
    setUploadingType(req.document_type);

    try {
      const doc = await DocumentAPI.uploadDocument(applicationId, req.document_type, file);
      // Update state with new/replaced doc
      setDocuments((prev) => {
        const filtered = prev.filter((d) => d.document_type !== req.document_type);
        return [doc, ...filtered];
      });
    } catch (err: any) {
      setError(err.message || "Failed to upload document.");
    } finally {
      setUploadingType(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate mandatory documents
    for (const req of requirements) {
      if (req.mandatory) {
        const hasDoc = documents.some((d) => d.document_type === req.document_type);
        if (!hasDoc) {
          setError(`Mandatory document '${req.title}' has not been uploaded.`);
          return;
        }
      }
    }

    if (!eSignature.trim() || eSignature.length < 2) {
      setError("Please type your full legal name as your electronic signature.");
      return;
    }

    setSubmitting(true);
    try {
      await onSubmitProposal(eSignature);
    } catch (err: any) {
      setError(err.message || "Submission failed. Please check form details.");
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="border-b border-slate-200 pb-3">
        <h3 className="text-base font-semibold text-slate-900 flex items-center gap-2">
          <FileCheck2 className="w-5 h-5 text-blue-600" />
          Step 8: Document Upload & Final Proposal Submission
        </h3>
        <p className="text-xs text-slate-500 mt-1">
          Upload required KYC and verification documents. Files are secured with SHA-256 integrity verification.
        </p>
      </div>

      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-md flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Required Documents Upload Cards */}
      <div className="space-y-3">
        {requirements.map((req) => {
          const uploaded = documents.find((d) => d.document_type === req.document_type);
          const isUploading = uploadingType === req.document_type;

          return (
            <div
              key={req.document_type}
              className="p-4 border border-slate-200 rounded-lg bg-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-2xs"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-slate-900">{req.title}</span>
                  {req.mandatory ? (
                    <Badge variant="outline" className="text-[10px] bg-rose-50 text-rose-700 border-rose-200">
                      Mandatory
                    </Badge>
                  ) : (
                    <Badge variant="outline" className="text-[10px] bg-slate-50 text-slate-600">
                      Optional
                    </Badge>
                  )}
                </div>
                {req.description && (
                  <p className="text-[11px] text-slate-500">{req.description}</p>
                )}
                {uploaded && (
                  <div className="flex items-center gap-2 pt-1 text-[11px] text-slate-600">
                    <FileText className="w-3.5 h-3.5 text-blue-600" />
                    <span className="font-medium text-slate-800">{uploaded.file_name}</span>
                    <span>({(uploaded.file_size_bytes / 1024).toFixed(0)} KB)</span>
                    <Badge
                      variant="outline"
                      className={`text-[10px] ${
                        uploaded.verification_status === "verified"
                          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                          : uploaded.verification_status === "rejected"
                          ? "bg-rose-50 text-rose-700 border-rose-200"
                          : "bg-blue-50 text-blue-700 border-blue-200"
                      }`}
                    >
                      {uploaded.verification_status.toUpperCase()}
                    </Badge>
                  </div>
                )}
              </div>

              <div>
                <label className="cursor-pointer">
                  <input
                    type="file"
                    className="hidden"
                    accept=".pdf,.jpg,.jpeg,.png"
                    disabled={isUploading}
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleFileUpload(req, file);
                    }}
                  />
                  <Button
                    type="button"
                    variant={uploaded ? "outline" : "default"}
                    size="sm"
                    disabled={isUploading}
                    className="text-xs pointer-events-none"
                  >
                    {isUploading ? (
                      <>
                        <Loader2 className="w-3 h-3 mr-1 animate-spin" /> Uploading...
                      </>
                    ) : uploaded ? (
                      <>
                        <Upload className="w-3 h-3 mr-1" /> Replace File
                      </>
                    ) : (
                      <>
                        <Upload className="w-3 h-3 mr-1" /> Upload Document
                      </>
                    )}
                  </Button>
                </label>
              </div>
            </div>
          );
        })}
      </div>

      {/* E-Signature confirmation */}
      <div className="p-4 border border-slate-200 rounded-lg bg-slate-50/50 space-y-3">
        <div className="text-xs font-semibold text-slate-900">
          Electronic Proposal Signature & Confirmation
        </div>
        <p className="text-[11px] text-slate-600 leading-relaxed">
          By entering your legal name below, you confirm that you have reviewed the proposal and authorized submission to Star Union Life & General Underwriting.
        </p>
        <div className="space-y-1.5 max-w-md">
          <Label htmlFor="esign" className="text-xs font-medium text-slate-700">
            Type Full Legal Name as Electronic Signature *
          </Label>
          <Input
            id="esign"
            value={eSignature}
            onChange={(e) => setESignature(e.target.value)}
            placeholder="e.g. Rajesh Kumar Sharma"
            required
            className="text-xs h-9 bg-white font-serif italic text-base"
          />
        </div>
      </div>

      <div className="flex justify-between pt-4">
        <Button type="button" variant="outline" size="sm" onClick={onPrev} disabled={submitting} className="text-xs">
          <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Previous Step
        </Button>
        <Button
          type="submit"
          size="sm"
          disabled={submitting}
          className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs"
        >
          {submitting ? (
            <>
              <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" /> Submitting to Underwriting...
            </>
          ) : (
            <>
              <Send className="w-3.5 h-3.5 mr-1" /> Submit Proposal
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
