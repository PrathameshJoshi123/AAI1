import * as React from "react";
import { type LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface StatCardProps {
  title: string;
  value: string | number | null;
  description?: string;
  icon?: LucideIcon;
  trend?: {
    value: string;
    isPositive: boolean;
  };
}

export function StatCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
}: StatCardProps) {
  return (
    <Card className="hover:border-slate-300 transition-colors">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            {title}
          </p>
          {Icon && (
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-50 text-slate-500 border border-slate-100">
              <Icon className="h-4 w-4" />
            </div>
          )}
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-2xl font-bold tracking-tight text-slate-900">
            {value !== null && value !== undefined ? value : "—"}
          </span>
          {trend && (
            <span
              className={`text-xs font-medium ${
                trend.isPositive ? "text-emerald-600" : "text-red-600"
              }`}
            >
              {trend.value}
            </span>
          )}
        </div>
        {description && (
          <p className="mt-1 text-xs text-slate-500 leading-normal">
            {description}
          </p>
        )}
      </CardContent>
    </Card>
  );
}

