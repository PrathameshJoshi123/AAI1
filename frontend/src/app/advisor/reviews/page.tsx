"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Scale, CheckCircle2 } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { DataTable } from "@/components/shared/data-table";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";

interface ReviewItem {
  id: string;
  caseId: string;
  applicant: string;
  decision: string;
  underwriter: string;
  reviewedAt: string;
}

export default function AdvisorReviewsPage() {
  const columns: ColumnDef<ReviewItem>[] = [
    {
      accessorKey: "caseId",
      header: "Case ID",
    },
    {
      accessorKey: "applicant",
      header: "Applicant",
    },
    {
      accessorKey: "decision",
      header: "Decision",
      cell: ({ row }) => <StatusBadge status={row.getValue("decision")} />,
    },
    {
      accessorKey: "underwriter",
      header: "Assigned Underwriter",
    },
    {
      accessorKey: "reviewedAt",
      header: "Decision Date",
    },
  ];

  // In Phase 1: Pure empty array - zero fake metrics
  const data: ReviewItem[] = [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Underwriting Reviews History"
        description="Formal risk evaluation decisions, premium loading adjustments, and policy sanction logs."
        breadcrumbs={[
          { label: "Advisor Workbench", href: "/advisor" },
          { label: "Underwriting Reviews" },
        ]}
      />

      <DataTable
        columns={columns}
        data={data}
        emptyMessage="No historical review records found. Completed underwriting decisions will be archived here."
      />
    </div>
  );
}

