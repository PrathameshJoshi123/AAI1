"use client";

import React from "react";
import { Check, Clock, AlertCircle, FileCheck2, UserCheck, Shield } from "lucide-react";
import { cn } from "@/lib/utils";

interface ApplicationTimelineProps {
  status: string;
  submittedAt?: string;
}

const MILESTONES = [
  { key: "draft", label: "Proposal Drafted", desc: "Questionnaire completed" },
  { key: "submitted", label: "Proposal Submitted", desc: "E-signature & checksum logged" },
  { key: "documents", label: "KYC & Documents", desc: "Identity & address verified" },
  { key: "underwriting", label: "Underwriting Assessment", desc: "Medical & financial review" },
  { key: "decision", label: "Policy Issuance", desc: "Final underwriting decision" },
];

export function ApplicationTimeline({ status, submittedAt }: ApplicationTimelineProps) {
  const getActiveIndex = () => {
    switch (status) {
      case "draft":
        return 0;
      case "submitted":
        return 1;
      case "documents_pending":
        return 1;
      case "under_review":
        return 3;
      case "approved":
        return 4;
      case "rejected":
        return 4;
      default:
        return 1;
    }
  };

  const activeIdx = getActiveIndex();

  return (
    <div className="w-full bg-slate-50/70 border border-slate-200 rounded-lg p-5">
      <h4 className="text-xs font-semibold text-slate-900 mb-4 flex items-center gap-1.5">
        <Clock className="w-4 h-4 text-blue-600" />
        Application Lifecycle Milestones
      </h4>

      <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
        {MILESTONES.map((m, idx) => {
          const isDone = idx < activeIdx || (idx === 4 && status === "approved");
          const isCurrent = idx === activeIdx && status !== "approved";

          return (
            <div key={m.key} className="space-y-1.5 relative">
              <div className="flex items-center gap-2">
                <div
                  className={cn(
                    "w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0",
                    isDone && "bg-emerald-600 text-white",
                    isCurrent && "bg-blue-600 text-white ring-4 ring-blue-100",
                    !isDone && !isCurrent && "bg-slate-200 text-slate-500"
                  )}
                >
                  {isDone ? <Check className="w-3.5 h-3.5" /> : idx + 1}
                </div>
                <span
                  className={cn(
                    "text-xs font-semibold",
                    isCurrent ? "text-blue-700" : isDone ? "text-slate-900" : "text-slate-400"
                  )}
                >
                  {m.label}
                </span>
              </div>
              <p className="text-[11px] text-slate-500 pl-8 leading-tight">{m.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

