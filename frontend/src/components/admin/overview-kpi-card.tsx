import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface OverviewKPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  badge?: string;
  badgeVariant?: "default" | "secondary" | "outline" | "destructive";
}

export const OverviewKPICard: React.FC<OverviewKPICardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  badge,
}) => {
  return (
    <Card className="bg-white border-slate-200 shadow-sm hover:shadow transition-shadow">
      <CardContent className="p-5">
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
            {title}
          </p>
          <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
            <Icon className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline justify-between">
          <p className="text-2xl font-bold tracking-tight text-slate-900">{value}</p>
          {badge && (
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
              {badge}
            </span>
          )}
        </div>
        {subtitle && (
          <p className="mt-1 text-xs text-slate-500 truncate">{subtitle}</p>
        )}
      </CardContent>
    </Card>
  );
};

