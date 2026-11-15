import React from "react";
import { Badge } from "@/components/ui/badge";

interface AgentStatusBadgeProps {
  status: "active" | "paused" | "disabled" | string;
}

export const AgentStatusBadge: React.FC<AgentStatusBadgeProps> = ({ status }) => {
  switch (status.toLowerCase()) {
    case "active":
      return (
        <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-50">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5" />
          Active
        </Badge>
      );
    case "paused":
      return (
        <Badge className="bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-50">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mr-1.5" />
          Paused
        </Badge>
      );
    case "disabled":
    default:
      return (
        <Badge className="bg-rose-50 text-rose-700 border-rose-200 hover:bg-rose-50">
          <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mr-1.5" />
          Disabled
        </Badge>
      );
  }
};

