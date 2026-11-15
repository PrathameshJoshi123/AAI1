import * as React from "react";
import { Badge } from "@/components/ui/badge";
import { InsuranceStatus } from "@/types/common";

interface StatusBadgeProps {
  status: InsuranceStatus | string;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  switch (status.toUpperCase()) {
    case "APPROVED":
    case "ISSUED":
      return (
        <Badge variant="success" className={className}>
          {status.replace("_", " ")}
        </Badge>
      );
    case "QUOTED":
    case "QUALIFIED":
    case "UNDER_REVIEW":
      return (
        <Badge variant="warning" className={className}>
          {status.replace("_", " ")}
        </Badge>
      );
    case "ESCALATED":
      return (
        <Badge
          className={`border-purple-200 bg-purple-50 text-purple-700 hover:bg-purple-100 ${
            className || ""
          }`}
        >
          {status.replace("_", " ")}
        </Badge>
      );
    case "REJECTED":
      return (
        <Badge variant="destructive" className={className}>
          {status.replace("_", " ")}
        </Badge>
      );
    case "DRAFT":
    case "IN_PROGRESS":
    default:
      return (
        <Badge variant="secondary" className={className}>
          {status.replace("_", " ")}
        </Badge>
      );
  }
}

