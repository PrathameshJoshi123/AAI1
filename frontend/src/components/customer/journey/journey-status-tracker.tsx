"use client";

import * as React from "react";
import Link from "next/link";
import { CheckCircle2, Circle, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface JourneyTrackerProps {
  currentStage: "discovery" | "needs_assessment" | "product_matching" | "quote_review" | "proposal_draft" | "submitted";
  qualificationCompleted?: boolean;
  hasActiveQuote?: boolean;
}

const STAGES = [
  { id: "discovery", label: "1. Discovery", href: "/customer/explore" },
  { id: "needs_assessment", label: "2. Needs Assessment", href: "/customer/needs-assessment" },
  { id: "product_matching", label: "3. Product Match", href: "/customer/recommendations" },
  { id: "quote_review", label: "4. Indicative Quote", href: "/customer/quotes" },
  { id: "proposal_draft", label: "5. Proposal Draft", href: "/customer/onboarding" },
];

export function JourneyStatusTracker({
  currentStage,
  qualificationCompleted = false,
  hasActiveQuote = false,
}: JourneyTrackerProps) {
  const currentIdx = STAGES.findIndex((s) => s.id === currentStage);
  const activeIdx = currentIdx === -1 ? 0 : currentIdx;

  const nextAction = React.useMemo(() => {
    switch (currentStage) {
      case "discovery":
        return { label: "Complete Needs Assessment", href: "/customer/needs-assessment" };
      case "needs_assessment":
        return { label: "View Recommended Plans", href: "/customer/recommendations" };
      case "product_matching":
        return { label: "Generate Indicative Quote", href: "/customer/quotes" };
      case "quote_review":
        return { label: "Proceed to Proposal Onboarding", href: "/customer/onboarding" };
      default:
        return { label: "Chat with AI Advisor", href: "/customer/chat" };
    }
  }, [currentStage]);

  return (
    <Card className="border-blue-100 bg-gradient-to-r from-blue-50/60 via-white to-blue-50/30">
      <CardContent className="p-5 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-blue-700 bg-blue-100/80 px-2.5 py-0.5 rounded-full">
              Active Onboarding Milestone
            </span>
            <h3 className="text-base font-semibold text-slate-900 mt-1">
              Your Insurance Acquisition Roadmap
            </h3>
          </div>
          <Button size="sm" asChild className="shrink-0 bg-blue-600 hover:bg-blue-700 text-white text-xs">
            <Link href={nextAction.href}>
              {nextAction.label} <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
            </Link>
          </Button>
        </div>

        {/* Step Progress Dots */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 pt-2 border-t border-slate-100">
          {STAGES.map((stage, idx) => {
            const isCompleted = idx < activeIdx || (idx === 1 && qualificationCompleted) || (idx === 3 && hasActiveQuote);
            const isCurrent = idx === activeIdx;

            return (
              <Link
                key={stage.id}
                href={stage.href}
                className={`p-2.5 rounded-lg border text-xs font-medium flex items-center gap-2 transition-colors ${
                  isCurrent
                    ? "border-blue-500 bg-white shadow-2xs text-blue-900"
                    : isCompleted
                    ? "border-slate-200 bg-slate-50/60 text-slate-700 hover:bg-white"
                    : "border-slate-100 bg-transparent text-slate-400 hover:text-slate-600"
                }`}
              >
                {isCompleted ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                ) : isCurrent ? (
                  <Circle className="h-4 w-4 text-blue-600 fill-blue-600 shrink-0" />
                ) : (
                  <Circle className="h-4 w-4 text-slate-300 shrink-0" />
                )}
                <span className="truncate">{stage.label}</span>
              </Link>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

