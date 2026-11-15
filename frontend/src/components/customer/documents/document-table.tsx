"use client";

import React from "react";
import { DocumentItem } from "@/types/document";
import { DocumentAPI } from "@/services/document.service";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  FileText,
  Download,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileCheck,
  ShieldCheck,
  RefreshCw,
} from "lucide-react";

interface DocumentTableProps {
  documents: DocumentItem[];
  onReuploadClick?: (doc: DocumentItem) => void;
}

export function DocumentTable({ documents, onReuploadClick }: DocumentTableProps) {
  if (documents.length === 0) {
    return (
      <div className="p-8 text-center border border-dashed border-slate-200 rounded-lg bg-slate-50/50">
        <FileText className="w-8 h-8 text-slate-300 mx-auto mb-2" />
        <p className="text-xs text-slate-500 font-medium">No documents uploaded yet.</p>
        <p className="text-[11px] text-slate-400 mt-0.5">
          Documents uploaded during proposal onboarding or KYC requests will be safely stored here.
        </p>
      </div>
    );
  }

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden bg-white shadow-2xs">
      <Table>
        <TableHeader className="bg-slate-50">
          <TableRow>
            <TableHead className="text-[11px] font-semibold text-slate-700">Document Type & Name</TableHead>
            <TableHead className="text-[11px] font-semibold text-slate-700">Size & Format</TableHead>
            <TableHead className="text-[11px] font-semibold text-slate-700">Integrity Hash (SHA-256)</TableHead>
            <TableHead className="text-[11px] font-semibold text-slate-700">Verification Status</TableHead>
            <TableHead className="text-[11px] font-semibold text-slate-700">Uploaded On</TableHead>
            <TableHead className="text-[11px] font-semibold text-slate-700 text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {documents.map((doc) => {
            const formattedSize =
              doc.file_size_bytes > 1024 * 1024
                ? `${(doc.file_size_bytes / (1024 * 1024)).toFixed(1)} MB`
                : `${(doc.file_size_bytes / 1024).toFixed(0)} KB`;

            const dateStr = new Date(doc.created_at).toLocaleDateString("en-IN", {
              day: "2-digit",
              month: "short",
              year: "numeric",
            });

            return (
              <TableRow key={doc.id} className="hover:bg-slate-50/60">
                <TableCell>
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-md bg-blue-50 flex items-center justify-center shrink-0">
                      <FileText className="w-4 h-4 text-blue-600" />
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-slate-900 capitalize">
                        {doc.document_type.replace("_", " ")}
                      </div>
                      <div className="text-[11px] text-slate-500 truncate max-w-[200px]">
                        {doc.file_name} (v{doc.version})
                      </div>
                    </div>
                  </div>
                </TableCell>

                <TableCell className="text-xs text-slate-600">
                  <span>{formattedSize}</span>
                  <span className="text-[10px] text-slate-400 block uppercase">
                    {doc.mime_type.split("/")[1] || "PDF"}
                  </span>
                </TableCell>

                <TableCell>
                  <span className="text-[11px] font-mono text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                    {doc.file_hash.substring(0, 12)}...
                  </span>
                </TableCell>

                <TableCell>
                  {doc.verification_status === "verified" ? (
                    <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200 text-[10px] gap-1">
                      <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Verified
                    </Badge>
                  ) : doc.verification_status === "rejected" ? (
                    <div className="space-y-0.5">
                      <Badge variant="outline" className="bg-rose-50 text-rose-700 border-rose-200 text-[10px] gap-1">
                        <AlertCircle className="w-3 h-3 text-rose-600" /> Rejected
                      </Badge>
                      {doc.rejection_reason && (
                        <p className="text-[10px] text-rose-600 max-w-[180px] leading-tight">
                          {doc.rejection_reason}
                        </p>
                      )}
                    </div>
                  ) : doc.verification_status === "extracted" ? (
                    <Badge variant="outline" className="bg-indigo-50 text-indigo-700 border-indigo-200 text-[10px] gap-1">
                      <ShieldCheck className="w-3 h-3 text-indigo-600" /> OCR Extracted
                    </Badge>
                  ) : (
                    <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 text-[10px] gap-1">
                      <Clock className="w-3 h-3 text-blue-600" /> Pending Review
                    </Badge>
                  )}
                </TableCell>

                <TableCell className="text-xs text-slate-500">
                  {dateStr}
                </TableCell>

                <TableCell className="text-right">
                  <div className="flex items-center justify-end gap-1.5">
                    <Button
                      variant="ghost"
                      size="sm"
                      asChild
                      className="text-xs text-slate-600 hover:text-blue-600 h-7"
                    >
                      <a href={DocumentAPI.getDownloadUrl(doc.id)} target="_blank" rel="noopener noreferrer">
                        <Download className="w-3 h-3 mr-1" /> View
                      </a>
                    </Button>
                    {doc.verification_status === "rejected" && onReuploadClick && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onReuploadClick(doc)}
                        className="text-xs border-amber-300 text-amber-700 hover:bg-amber-50 h-7"
                      >
                        <RefreshCw className="w-3 h-3 mr-1" /> Re-upload
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}

