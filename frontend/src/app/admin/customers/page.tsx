"use client";

import React, { useEffect, useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { AdminAPI } from "@/services/admin.service";
import { AdminCustomer } from "@/types/admin";
import { RefreshCw, UserCheck, AlertCircle, MapPin, Briefcase } from "lucide-react";

export default function AdminCustomersPage() {
  const [customers, setCustomers] = useState<AdminCustomer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadCustomers = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await AdminAPI.listCustomers();
      setCustomers(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load customer directory.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCustomers();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Customer Master Directory"
        description="Comprehensive customer profiles, onboarding journey progression, and assigned advisors."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Customer Directory" },
        ]}
        actions={
          <Button variant="outline" size="sm" onClick={loadCustomers} disabled={isLoading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        }
      />

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg text-sm text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      <Card className="bg-white border-slate-200 shadow-sm">
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-3">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : customers.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-sm">
              No customer master records found in the database.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50/50">
                  <TableHead className="font-semibold text-xs text-slate-700">Customer</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700">Location</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700">Occupation & Income</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700">Onboarding Stage</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700">Risk Tier</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700">Assigned Advisor</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700">Registered</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {customers.map((c) => (
                  <TableRow key={c.id} className="hover:bg-slate-50/50">
                    <TableCell>
                      <div>
                        <p className="font-semibold text-sm text-slate-900">{c.full_name}</p>
                        <p className="text-xs text-slate-400">{c.email}</p>
                        {c.phone && <p className="text-[11px] text-slate-400 font-mono">{c.phone}</p>}
                      </div>
                    </TableCell>
                    <TableCell className="text-xs text-slate-600">
                      {c.city || c.state ? (
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3 h-3 text-slate-400" />
                          {[c.city, c.state].filter(Boolean).join(", ")}
                        </span>
                      ) : (
                        "—"
                      )}
                    </TableCell>
                    <TableCell className="text-xs text-slate-600">
                      <div>
                        <p className="font-medium">{c.occupation || "Not declared"}</p>
                        {c.annual_income && (
                          <p className="text-[11px] text-slate-400 font-mono">
                            ₹{c.annual_income.toLocaleString()}/yr
                          </p>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-[11px] font-medium capitalize border-blue-200 bg-blue-50 text-blue-700">
                        {c.onboarding_stage.replace("_", " ")}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className={`text-[11px] capitalize ${
                          c.risk_tier === "preferred"
                            ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                            : c.risk_tier === "substandard"
                            ? "bg-amber-50 text-amber-700 border-amber-200"
                            : "bg-slate-50 text-slate-700 border-slate-200"
                        }`}
                      >
                        {c.risk_tier}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-xs text-slate-700 font-medium">
                      {c.assigned_advisor_name || <span className="text-slate-400 font-normal">Unassigned</span>}
                    </TableCell>
                    <TableCell className="text-xs text-slate-400 whitespace-nowrap">
                      {new Date(c.created_at).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

