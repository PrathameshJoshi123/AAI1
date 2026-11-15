"use client";

import React from "react";
import { Check, Circle } from "lucide-react";
import { cn } from "@/lib/utils";

interface StepIndicatorProps {
  currentStep: number;
  totalSteps: number;
  stepLabels: string[];
  completedSteps: Record<string, boolean>;
  onStepClick?: (step: number) => void;
}

export function StepIndicator({
  currentStep,
  totalSteps,
  stepLabels,
  completedSteps,
  onStepClick,
}: StepIndicatorProps) {
  return (
    <div className="w-full bg-white border border-slate-200 rounded-lg p-4 shadow-2xs mb-6">
      <div className="flex items-center justify-between overflow-x-auto pb-2 sm:pb-0 gap-2">
        {stepLabels.map((label, idx) => {
          const stepNum = idx + 1;
          const isCurrent = stepNum === currentStep;
          const isPassed = stepNum < currentStep;

          return (
            <div key={label} className="flex items-center min-w-fit">
              <button
                type="button"
                onClick={() => isPassed && onStepClick?.(stepNum)}
                disabled={!isPassed && !isCurrent}
                className={cn(
                  "flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors",
                  isCurrent && "bg-blue-50 text-blue-700 border border-blue-200 font-semibold",
                  isPassed && "text-slate-700 hover:bg-slate-50 cursor-pointer",
                  !isCurrent && !isPassed && "text-slate-400 cursor-not-allowed opacity-60"
                )}
              >
                <div
                  className={cn(
                    "w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold",
                    isCurrent && "bg-blue-600 text-white",
                    isPassed && "bg-emerald-100 text-emerald-700",
                    !isCurrent && !isPassed && "bg-slate-100 text-slate-400"
                  )}
                >
                  {isPassed ? <Check className="w-3 h-3" /> : stepNum}
                </div>
                <span>{label}</span>
              </button>
              {idx < totalSteps - 1 && (
                <div className="w-4 sm:w-6 h-[1px] bg-slate-200 mx-1 hidden sm:block" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
