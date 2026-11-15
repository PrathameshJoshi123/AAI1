"use client";

import React from "react";
import Link from "next/link";
import { ApplicationItem } from "@/types/application";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  ClipboardList,
  ArrowRight,
  Clock,
  CheckCircle2,
  AlertCircle,
  FileText,
  ShieldCheck,
} from "lucide-react";

interface ApplicationCardProps {
  application: ApplicationItem;
}

export function ApplicationCard({ application }: ApplicationCardProps) {
  const isDraft = application.status === "draft" || application.status === "documents_pending";
  const dateStr = application.submitted_at
    ? new Date(application.submitted_at).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      })
    : new Date(application.created_at).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      });

  const getStatusBadge = () => {
    switch (application.status) {
      case "approved":
        return (
          <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200 text-xs">
            Approved
          </Badge>
        );
      case "under_review":
      case "submitted":
        return (
          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 text-xs">
            In Underwriting Review
          </Badge>
        );
      case "rejected":
        return (
          <Badge variant="outline" className="bg-rose-50 text-rose-700 border-rose-200 text-xs">
            Declined
          </Badge>
        );
      case "additional_info_required":
        return (
          <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-200 text-xs">
            Information Requested
          </Badge>
        );
      default:
        return (
          <Badge variant="outline" className="bg-slate-100 text-slate-700 text-xs">
            Draft (Step {application.current_step}/8)
          </Badge>
        );
    }
  };

  return (
    <Card className="border-slate-200 bg-white hover:border-slate-300 transition-all shadow-2xs">
      <CardContent className="p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs font-bold text-slate-900">
              {application.application_number}
            </span>
            {getStatusBadge()}
          </div>

          <div className="text-xs text-slate-600 flex items-center gap-3">
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              {isDraft ? "Draft created:" : "Submitted on:"} {dateStr}
            </span>
            {application.documents?.length > 0 && (
              <span className="flex items-center gap-1 text-slate-500">
                <FileText className="w-3.5 h-3.5 text-blue-600" />
                {application.documents.length} document(s) uploaded
              </span>
            )}
          </div>
        </div>

        <div>
          {isDraft ? (
            <Button size="sm" asChild className="bg-blue-600 hover:bg-blue-700 text-white text-xs">
              <Link href={`/customer/onboarding/${application.quote_id}`}>
                Resume Proposal <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </Link>
            </Button>
          ) : (
            <Button variant="outline" size="sm" asChild className="text-xs">
              <Link href={`/customer/applications/${application.id}`}>
                View Application & Milestones <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </Link>
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

