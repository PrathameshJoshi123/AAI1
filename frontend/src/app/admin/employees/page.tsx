"use client";

import React, { useEffect, useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { EmployeeFormModal } from "@/components/admin/employee-form-modal";
import { AdminAPI } from "@/services/admin.service";
import { Employee, EmployeeCreatePayload } from "@/types/admin";
import { UserPlus, RefreshCw, Shield, AlertCircle } from "lucide-react";

export default function AdminEmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadEmployees = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await AdminAPI.listEmployees();
      setEmployees(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load staff directory.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadEmployees();
  }, []);

  const handleCreateEmployee = async (payload: EmployeeCreatePayload) => {
    await AdminAPI.createEmployee(payload);
    await loadEmployees();
  };

  const handleToggleStatus = async (employee: Employee, currentActive: boolean) => {
    try {
      await AdminAPI.updateEmployeeStatus(employee.id, !currentActive, employee.is_available ?? undefined);
      setEmployees((prev) =>
        prev.map((e) => (e.id === employee.id ? { ...e, is_active: !currentActive } : e))
      );
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to toggle status.");
    }
  };

  const handleToggleAvailability = async (employee: Employee, currentAvailable: boolean) => {
    try {
      await AdminAPI.updateEmployeeStatus(employee.id, employee.is_active, !currentAvailable);
      setEmployees((prev) =>
        prev.map((e) => (e.id === employee.id ? { ...e, is_available: !currentAvailable } : e))
      );
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to toggle availability.");
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Employee & Credential Administration"
        description="Provision staff accounts, assign administrative roles, manage licenses, and monitor workloads."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Employees" },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={loadEmployees} disabled={isLoading}>
              <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => setIsModalOpen(true)}>
              <UserPlus className="w-3.5 h-3.5 mr-1.5" />
              Provision Staff Member
            </Button>
          </div>
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
          ) : employees.length === 0 ? (
            <div className="p-12 text-center text-slate-500">
              No staff members found in the database. Use &quot;Provision Staff Member&quot; to add advisors or underwriters.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50/50">
                  <TableHead className="font-semibold text-xs text-slate-700">Staff Member</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700">Roles</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700">License / Code</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700">Caseload / Capacity</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700">Availability</TableHead>
                  <TableHead className="font-semibold text-xs text-slate-700">Account Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {employees.map((emp) => (
                  <TableRow key={emp.id} className="hover:bg-slate-50/50">
                    <TableCell>
                      <div>
                        <p className="font-semibold text-sm text-slate-900">
                          {emp.first_name} {emp.last_name}
                        </p>
                        <p className="text-xs text-slate-400">{emp.email}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {emp.roles.map((r) => (
                          <Badge
                            key={r}
                            variant="outline"
                            className={`text-[11px] ${
                              r === "Admin" || r === "Owner"
                                ? "bg-purple-50 text-purple-700 border-purple-200"
                                : r === "Underwriter"
                                ? "bg-blue-50 text-blue-700 border-blue-200"
                                : "bg-emerald-50 text-emerald-700 border-emerald-200"
                            }`}
                          >
                            <Shield className="w-2.5 h-2.5 mr-1" />
                            {r}
                          </Badge>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell className="text-xs font-mono text-slate-600">
                      {emp.license_number || "—"}
                    </TableCell>
                    <TableCell>
                      {emp.advisor_id ? (
                        <div className="space-y-1">
                          <div className="flex items-center justify-between text-xs text-slate-600">
                            <span>{emp.active_cases_count || 0} active</span>
                            <span className="text-slate-400">/ {emp.max_active_cases || 50} max</span>
                          </div>
                          <div className="h-1.5 w-24 bg-slate-100 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-blue-600 rounded-full"
                              style={{
                                width: `${Math.min(
                                  100,
                                  ((emp.active_cases_count || 0) / (emp.max_active_cases || 50)) * 100
                                )}%`,
                              }}
                            />
                          </div>
                        </div>
                      ) : emp.underwriter_id ? (
                        <div className="text-xs text-slate-600">
                          <span className="font-semibold">{emp.authority_level}</span>
                          <p className="text-[11px] text-slate-400">
                            Max ₹{(emp.max_coverage_limit || 0).toLocaleString()}
                          </p>
                        </div>
                      ) : (
                        <span className="text-xs text-slate-400">—</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {emp.advisor_id ? (
                        <div className="flex items-center space-x-2">
                          <Switch
                            checked={emp.is_available ?? false}
                            onCheckedChange={() => handleToggleAvailability(emp, emp.is_available ?? false)}
                          />
                          <span className="text-xs text-slate-600">
                            {emp.is_available ? "Available" : "Away"}
                          </span>
                        </div>
                      ) : (
                        <span className="text-xs text-slate-400">—</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Switch
                          checked={emp.is_active}
                          onCheckedChange={() => handleToggleStatus(emp, emp.is_active)}
                        />
                        <span className={`text-xs font-medium ${emp.is_active ? "text-emerald-700" : "text-slate-400"}`}>
                          {emp.is_active ? "Active" : "Disabled"}
                        </span>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <EmployeeFormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateEmployee}
      />
    </div>
  );
}

