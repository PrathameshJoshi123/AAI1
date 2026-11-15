"use client";

import React, { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { EmployeeCreatePayload } from "@/types/admin";

interface EmployeeFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: EmployeeCreatePayload) => Promise<void>;
}

export const EmployeeFormModal: React.FC<EmployeeFormModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phone, setPhone] = useState("");
  const [roles, setRoles] = useState<string[]>(["Advisor"]);
  const [licenseNumber, setLicenseNumber] = useState("");
  const [specializations, setSpecializations] = useState("Term Life, Health");
  const [maxCases, setMaxCases] = useState(50);
  const [authorityLevel, setAuthorityLevel] = useState("Level 1");
  const [maxCoverage, setMaxCoverage] = useState(500000);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggleRole = (role: string) => {
    if (roles.includes(role)) {
      setRoles(roles.filter((r) => r !== role));
    } else {
      setRoles([...roles, role]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password || !firstName || !lastName) {
      setError("Please fill in all mandatory user fields.");
      return;
    }
    if (roles.length === 0) {
      setError("Please select at least one staff role.");
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmit({
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        phone: phone || undefined,
        role_names: roles,
        license_number: licenseNumber || undefined,
        specializations: roles.includes("Advisor") ? specializations : undefined,
        max_active_cases: roles.includes("Advisor") ? maxCases : undefined,
        authority_level: roles.includes("Underwriter") ? authorityLevel : undefined,
        max_coverage_limit: roles.includes("Underwriter") ? maxCoverage : undefined,
      });
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to create employee.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-xl max-h-[90vh] overflow-y-auto bg-white border-slate-200">
        <DialogHeader>
          <DialogTitle className="text-lg font-bold text-slate-900">
            Provision New Staff Member
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 pt-2">
          {error && (
            <div className="p-3 text-xs bg-rose-50 text-rose-700 border border-rose-200 rounded-md">
              {error}
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="firstName" className="text-xs">First Name *</Label>
              <Input
                id="firstName"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                placeholder="Ramesh"
                required
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="lastName" className="text-xs">Last Name *</Label>
              <Input
                id="lastName"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                placeholder="Verma"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="email" className="text-xs">Email Address *</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="ramesh.verma@ps21.insure"
                required
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="phone" className="text-xs">Phone Number</Label>
              <Input
                id="phone"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+91 9876543210"
              />
            </div>
          </div>

          <div className="space-y-1">
            <Label htmlFor="password" className="text-xs">Temporary Password *</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Min 8 characters"
              required
            />
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-100">
            <Label className="text-xs font-semibold text-slate-900">Assign Staff Roles *</Label>
            <div className="flex items-center gap-6">
              {["Advisor", "Underwriter", "Admin"].map((r) => (
                <div key={r} className="flex items-center space-x-2">
                  <Checkbox
                    id={`role-${r}`}
                    checked={roles.includes(r)}
                    onCheckedChange={() => toggleRole(r)}
                  />
                  <Label htmlFor={`role-${r}`} className="text-xs font-normal cursor-pointer">
                    {r}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          {roles.includes("Advisor") && (
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-md space-y-3">
              <p className="text-xs font-semibold text-slate-800">Insurance Advisor Credentials</p>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label className="text-xs">IRDAI License / Code</Label>
                  <Input
                    value={licenseNumber}
                    onChange={(e) => setLicenseNumber(e.target.value)}
                    placeholder="ADV-IN-00921"
                  />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Max Active Caseload</Label>
                  <Input
                    type="number"
                    value={maxCases}
                    onChange={(e) => setMaxCases(Number(e.target.value))}
                  />
                </div>
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Specializations</Label>
                <Input
                  value={specializations}
                  onChange={(e) => setSpecializations(e.target.value)}
                  placeholder="Term Life, Critical Illness, Group Health"
                />
              </div>
            </div>
          )}

          {roles.includes("Underwriter") && (
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-md space-y-3">
              <p className="text-xs font-semibold text-slate-800">Underwriting Authority</p>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label className="text-xs">Authority Level</Label>
                  <Input
                    value={authorityLevel}
                    onChange={(e) => setAuthorityLevel(e.target.value)}
                    placeholder="Level 1, Level 2, Chief"
                  />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Max Coverage Limit (₹)</Label>
                  <Input
                    type="number"
                    value={maxCoverage}
                    onChange={(e) => setMaxCoverage(Number(e.target.value))}
                  />
                </div>
              </div>
            </div>
          )}

          <DialogFooter className="pt-3">
            <Button type="button" variant="outline" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white" disabled={isSubmitting}>
              {isSubmitting ? "Provisioning..." : "Provision Staff Member"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

