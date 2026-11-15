"use client";

import * as React from "react";
import { History, ArrowRight, X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ResumeJourneyBannerProps {
  lastMessage?: string | null;
  stage: string;
  onResume: () => void;
  onDismiss: () => void;
}

export function ResumeJourneyBanner({
  lastMessage,
  stage,
  onResume,
  onDismiss,
}: ResumeJourneyBannerProps) {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mx-4 mt-2 flex items-center justify-between gap-3 text-xs text-blue-900">
      <div className="flex items-center gap-2.5 flex-1 min-w-0">
        <History className="h-4 w-4 text-blue-600 shrink-0" />
        <div className="truncate">
          <span className="font-semibold">Unfinished Session Found ({stage}):</span>{" "}
          <span className="text-slate-600 truncate">{lastMessage || "Pick up where you left off"}</span>
        </div>
      </div>
      <div className="flex items-center gap-1.5 shrink-0">
        <Button size="sm" variant="default" className="h-7 text-xs px-3 bg-blue-600 hover:bg-blue-700" onClick={onResume}>
          Resume Consultation <ArrowRight className="h-3 w-3 ml-1" />
        </Button>
        <button
          onClick={onDismiss}
          className="text-slate-400 hover:text-slate-600 p-1 rounded-md"
          title="Dismiss"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}

