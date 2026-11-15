import React from "react";
import { IntegrationHealth } from "@/types/admin";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CheckCircle2, AlertTriangle, XCircle, RefreshCw } from "lucide-react";

interface IntegrationStatusCardProps {
  integration: IntegrationHealth;
  onTest: (key: string) => void;
  isTesting?: boolean;
}

export const IntegrationStatusCard: React.FC<IntegrationStatusCardProps> = ({
  integration,
  onTest,
  isTesting,
}) => {
  const renderStatus = () => {
    switch (integration.status) {
      case "active":
        return (
          <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200">
            <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" />
            Operational
          </Badge>
        );
      case "warning":
        return (
          <Badge className="bg-amber-50 text-amber-700 border-amber-200">
            <AlertTriangle className="w-3 h-3 mr-1 text-amber-600" />
            Warning
          </Badge>
        );
      case "error":
        return (
          <Badge className="bg-rose-50 text-rose-700 border-rose-200">
            <XCircle className="w-3 h-3 mr-1 text-rose-600" />
            Error
          </Badge>
        );
      case "not_configured":
      default:
        return (
          <Badge className="bg-slate-100 text-slate-600 border-slate-200">
            Not Configured
          </Badge>
        );
    }
  };

  return (
    <Card className="bg-white border-slate-200 shadow-sm">
      <CardContent className="p-5 flex flex-col justify-between h-full space-y-4">
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              {integration.category}
            </span>
            {renderStatus()}
          </div>
          <h4 className="text-sm font-bold text-slate-900">{integration.name}</h4>
          <p className="mt-1 text-xs text-slate-500 leading-relaxed">
            {integration.details}
          </p>
          {integration.endpoint_or_host && (
            <p className="mt-2 text-[11px] font-mono text-slate-400 truncate">
              Host: {integration.endpoint_or_host}
            </p>
          )}
        </div>

        <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
          <span>Checked: {new Date(integration.last_checked_at).toLocaleTimeString()}</span>
          <Button
            size="sm"
            variant="outline"
            className="h-7 text-xs"
            onClick={() => onTest(integration.service_key)}
            disabled={isTesting}
          >
            <RefreshCw className={`w-3 h-3 mr-1.5 ${isTesting ? "animate-spin" : ""}`} />
            Test Ping
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

