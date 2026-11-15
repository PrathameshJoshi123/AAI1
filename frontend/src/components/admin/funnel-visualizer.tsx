import React from "react";
import { FunnelStage } from "@/types/admin";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowDown, AlertCircle } from "lucide-react";

interface FunnelVisualizerProps {
  stages: FunnelStage[];
  overallConversion: number;
}

export const FunnelVisualizer: React.FC<FunnelVisualizerProps> = ({
  stages,
  overallConversion,
}) => {
  if (!stages || stages.length === 0) {
    return (
      <Card className="bg-white border-slate-200">
        <CardContent className="p-8 text-center text-slate-500">
          No funnel data recorded yet.
        </CardContent>
      </Card>
    );
  }

  const maxCount = Math.max(...stages.map((s) => s.count), 1);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
        <div>
          <h4 className="text-sm font-semibold text-slate-900">
            Stage-by-Stage Acquisition Funnel
          </h4>
          <p className="text-xs text-slate-500">
            Real-time throughput and step-by-step conversion rates
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs font-medium text-slate-500">Overall Conversion</p>
          <p className="text-lg font-bold text-blue-600">{overallConversion}%</p>
        </div>
      </div>

      <div className="space-y-2 pt-2">
        {stages.map((stage, idx) => {
          const widthPct = Math.max(12, Math.round((stage.count / maxCount) * 100));

          return (
            <div key={stage.stage_key} className="space-y-1">
              <div className="flex items-center justify-between text-xs font-medium text-slate-700">
                <span className="flex items-center gap-1.5">
                  <span className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center text-[10px] font-bold text-slate-600">
                    {idx + 1}
                  </span>
                  {stage.label}
                </span>
                <div className="flex items-center gap-4 text-xs">
                  <span className="font-semibold text-slate-900">
                    {stage.count.toLocaleString()}
                  </span>
                  <span
                    className={`px-1.5 py-0.5 rounded text-[11px] font-medium ${
                      stage.conversion_from_prev >= 80
                        ? "bg-emerald-50 text-emerald-700"
                        : stage.conversion_from_prev >= 50
                        ? "bg-blue-50 text-blue-700"
                        : "bg-amber-50 text-amber-700"
                    }`}
                  >
                    {stage.conversion_from_prev}%
                  </span>
                </div>
              </div>

              {/* Bar */}
              <div className="h-6 w-full bg-slate-100 rounded-md overflow-hidden flex items-center p-1">
                <div
                  className="h-full rounded bg-blue-600 transition-all duration-500 flex items-center justify-end pr-2"
                  style={{ width: `${widthPct}%` }}
                >
                  {widthPct > 20 && (
                    <span className="text-[10px] font-medium text-white truncate">
                      {stage.count}
                    </span>
                  )}
                </div>
              </div>

              {/* Drop-off notice if drop-off > 0 */}
              {stage.drop_off_count > 0 && idx > 0 && (
                <div className="flex items-center gap-1 text-[11px] text-slate-400 pl-6">
                  <ArrowDown className="w-3 h-3 text-slate-400" />
                  <span>
                    Drop-off: <strong>{stage.drop_off_count.toLocaleString()}</strong> prospects
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

