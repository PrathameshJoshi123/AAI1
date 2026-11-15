import * as React from "react";
import { type LucideIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  secondaryActionLabel?: string;
  onSecondaryAction?: () => void;
  className?: string;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
  secondaryActionLabel,
  onSecondaryAction,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={`flex min-h-[320px] flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 bg-white p-8 text-center animate-in fade-in-50 ${
        className || ""
      }`}
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-50 border border-slate-100 text-slate-500 shadow-2xs">
        <Icon className="h-6 w-6 stroke-[1.5]" />
      </div>
      <h3 className="mt-4 text-base font-semibold text-slate-900">{title}</h3>
      <p className="mt-1.5 max-w-sm text-sm text-slate-500 leading-relaxed">
        {description}
      </p>

      {(actionLabel || secondaryActionLabel) && (
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          {actionLabel && (
            <Button onClick={onAction} size="sm">
              {actionLabel}
            </Button>
          )}
          {secondaryActionLabel && (
            <Button
              onClick={onSecondaryAction}
              variant="outline"
              size="sm"
            >
              {secondaryActionLabel}
            </Button>
          )}
        </div>
      )}
    </div>
  );
}

