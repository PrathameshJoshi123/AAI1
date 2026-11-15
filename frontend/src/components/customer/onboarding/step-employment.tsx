"use client";

import React from "react";
import { EmploymentFinancialData } from "@/types/application";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ArrowLeft, ArrowRight, Briefcase } from "lucide-react";

interface StepEmploymentProps {
  initialData?: Partial<EmploymentFinancialData>;
  onNext: (data: EmploymentFinancialData) => void;
  onPrev: () => void;
}

export function StepEmployment({ initialData, onNext, onPrev }: StepEmploymentProps) {
  const [formData, setFormData] = React.useState<EmploymentFinancialData>({
    occupation_type: initialData?.occupation_type || "salaried",
    employer_or_business_name: initialData?.employer_or_business_name || "",
    designation: initialData?.designation || "",
    nature_of_duties: initialData?.nature_of_duties || "desk_office",
    gross_annual_income: initialData?.gross_annual_income || 1200000,
    tax_resident_india_only: initialData?.tax_resident_india_only ?? true,
    politically_exposed_person: initialData?.politically_exposed_person ?? false,
  });
  const [error, setError] = React.useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.employer_or_business_name.trim()) {
      setError("Please provide your employer or business entity name.");
      return;
    }
    if (!formData.designation.trim()) {
      setError("Please provide your functional designation.");
      return;
    }
    if (formData.gross_annual_income <= 0) {
      setError("Gross annual income must be greater than zero.");
      return;
    }

    onNext(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="border-b border-slate-200 pb-3">
        <h3 className="text-base font-semibold text-slate-900 flex items-center gap-2">
          <Briefcase className="w-5 h-5 text-blue-600" />
          Step 3: Occupational & Financial Declarations
        </h3>
        <p className="text-xs text-slate-500 mt-1">
          Financial underwriting evaluates insurance eligibility and sum assured adequacy against declared income.
        </p>
      </div>

      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-md">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <Label className="text-xs font-medium text-slate-700">Employment Category *</Label>
          <Select
            value={formData.occupation_type}
            onValueChange={(val: any) => setFormData({ ...formData, occupation_type: val })}
          >
            <SelectTrigger className="text-xs h-9 bg-white">
              <SelectValue placeholder="Select occupation" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="salaried">Salaried Employee (Pvt / Govt)</SelectItem>
              <SelectItem value="self_employed_professional">Self-Employed Professional (Doctor, CA, Lawyer)</SelectItem>
              <SelectItem value="business_owner">Business Owner / Proprietor</SelectItem>
              <SelectItem value="retired">Retired</SelectItem>
              <SelectItem value="homemaker">Homemaker</SelectItem>
              <SelectItem value="student">Student</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label className="text-xs font-medium text-slate-700">Nature of Daily Duties *</Label>
          <Select
            value={formData.nature_of_duties}
            onValueChange={(val: any) => setFormData({ ...formData, nature_of_duties: val })}
          >
            <SelectTrigger className="text-xs h-9 bg-white">
              <SelectValue placeholder="Select duty nature" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="desk_office">Desk / Office Based Work (Standard)</SelectItem>
              <SelectItem value="light_manual">Light Manual / Supervision</SelectItem>
              <SelectItem value="heavy_manual">Heavy Industrial / Machinery Operation</SelectItem>
              <SelectItem value="hazardous_substances">Chemicals / Hazardous Substances</SelectItem>
              <SelectItem value="aviation_offshore">Aviation Crew / Offshore Drilling</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="employer" className="text-xs font-medium text-slate-700">
            Employer / Business Organization Name *
          </Label>
          <Input
            id="employer"
            value={formData.employer_or_business_name}
            onChange={(e) => setFormData({ ...formData, employer_or_business_name: e.target.value })}
            placeholder="e.g. Infosys Ltd / Global Tech Solutions"
            required
            className="text-xs h-9 bg-white"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="designation" className="text-xs font-medium text-slate-700">
            Designation / Role *
          </Label>
          <Input
            id="designation"
            value={formData.designation}
            onChange={(e) => setFormData({ ...formData, designation: e.target.value })}
            placeholder="e.g. Senior Software Engineer"
            required
            className="text-xs h-9 bg-white"
          />
        </div>

        <div className="space-y-1.5 sm:col-span-2">
          <Label htmlFor="income" className="text-xs font-medium text-slate-700">
            Gross Annual Income (₹) *
          </Label>
          <Input
            id="income"
            type="number"
            value={formData.gross_annual_income}
            onChange={(e) => setFormData({ ...formData, gross_annual_income: Number(e.target.value) })}
            placeholder="1200000"
            required
            min={100000}
            step={50000}
            className="text-xs h-9 font-mono bg-white"
          />
          <p className="text-[11px] text-slate-400">
            Income Proof (ITR / Form 16 / Salary Slips) will be required if Sum Assured exceeds ₹50 Lakhs.
          </p>
        </div>

        <div className="sm:col-span-2 pt-2 space-y-2">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="tax_res"
              checked={formData.tax_resident_india_only}
              onCheckedChange={(checked) => setFormData({ ...formData, tax_resident_india_only: !!checked })}
            />
            <Label htmlFor="tax_res" className="text-xs text-slate-700 font-normal cursor-pointer">
              I am a tax resident solely of India and do not hold tax obligations in the USA or other countries (FATCA / CRS).
            </Label>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="pep"
              checked={formData.politically_exposed_person}
              onCheckedChange={(checked) => setFormData({ ...formData, politically_exposed_person: !!checked })}
            />
            <Label htmlFor="pep" className="text-xs text-slate-700 font-normal cursor-pointer">
              I am a Politically Exposed Person (PEP) or closely related to a public office holder.
            </Label>
          </div>
        </div>
      </div>

      <div className="flex justify-between pt-4">
        <Button type="button" variant="outline" size="sm" onClick={onPrev} className="text-xs">
          <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Previous Step
        </Button>
        <Button type="submit" size="sm" className="bg-blue-600 hover:bg-blue-700 text-white text-xs">
          Save & Next Step <ArrowRight className="w-3.5 h-3.5 ml-1" />
        </Button>
      </div>
    </form>
  );
}
