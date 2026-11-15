"use client";

import { ColumnDef } from "@tanstack/react-table";
import { ShieldAlert, Filter } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { DataTable } from "@/components/shared/data-table";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";

interface EscalationCase {
  id: string;
  applicant: string;
  product: string;
  escalationReason: string;
  severity: "HIGH" | "MEDIUM" | "LOW";
  status: string;
  escalatedAt: string;
}

export default function AdvisorQueuePage() {
  const columns: ColumnDef<EscalationCase>[] = [
    {
      accessorKey: "id",
      header: "Case ID",
    },
    {
      accessorKey: "applicant",
      header: "Applicant",
    },
    {
      accessorKey: "product",
      header: "Policy Product",
    },
    {
      accessorKey: "escalationReason",
      header: "Escalation Reason",
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => <StatusBadge status={row.getValue("status")} />,
    },
    {
      accessorKey: "escalatedAt",
      header: "Escalated At",
    },
  ];

  // In Phase 1: Pure empty array - zero fake metrics
  const data: EscalationCase[] = [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Human-in-the-Loop Escalation Queue"
        description="Review applications escalated by AI agents due to pre-existing conditions, financial variance, or policy exceptions."
        breadcrumbs={[
          { label: "Advisor Workbench", href: "/advisor" },
          { label: "Escalated Cases" },
        ]}
        actions={
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Filter Priority
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data}
        emptyMessage="No escalated cases in the queue. All customer risk evaluations are currently within normal processing limits."
      />
    </div>
  );
}

