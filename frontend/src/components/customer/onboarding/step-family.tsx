"use client";

import React from "react";
import { FamilyCoverageData, DependentData, ExistingPolicyData } from "@/types/application";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ArrowLeft, ArrowRight, Users, Plus, Trash2 } from "lucide-react";

interface StepFamilyProps {
  initialData?: Partial<FamilyCoverageData>;
  onNext: (data: FamilyCoverageData) => void;
  onPrev: () => void;
}

export function StepFamily({ initialData, onNext, onPrev }: StepFamilyProps) {
  const [dependents, setDependents] = React.useState<DependentData[]>(
    initialData?.dependents || [
      { name: "Sunita Sharma", relation: "Spouse", age: 30, financially_dependent: true },
      { name: "Aarav Sharma", relation: "Child", age: 3, financially_dependent: true },
    ]
  );
  const [hasExistingInsurance, setHasExistingInsurance] = React.useState<boolean>(
    initialData?.has_existing_insurance ?? false
  );
  const [existingPolicies, setExistingPolicies] = React.useState<ExistingPolicyData[]>(
    initialData?.existing_policies || []
  );
  const [hasRejections, setHasRejections] = React.useState<boolean>(
    initialData?.has_previous_rejections ?? false
  );
  const [rejectionDetails, setRejectionDetails] = React.useState<string>(
    initialData?.rejection_details || ""
  );

  const addDependent = () => {
    setDependents([...dependents, { name: "", relation: "Spouse", age: 25, financially_dependent: true }]);
  };

  const removeDependent = (idx: number) => {
    setDependents(dependents.filter((_, i) => i !== idx));
  };

  const addPolicy = () => {
    setExistingPolicies([...existingPolicies, { insurer_name: "", sum_assured: 2500000, year_issued: 2022 }]);
  };

  const removePolicy = (idx: number) => {
    setExistingPolicies(existingPolicies.filter((_, i) => i !== idx));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNext({
      dependents,
      has_existing_insurance: hasExistingInsurance,
      existing_policies: hasExistingInsurance ? existingPolicies : [],
      has_previous_rejections: hasRejections,
      rejection_details: hasRejections ? rejectionDetails : undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="border-b border-slate-200 pb-3">
        <h3 className="text-base font-semibold text-slate-900 flex items-center gap-2">
          <Users className="w-5 h-5 text-blue-600" />
          Step 4: Family Dependents & Existing Coverage
        </h3>
        <p className="text-xs text-slate-500 mt-1">
          Helps underwriters verify total financial liability and aggregated active sum assured.
        </p>
      </div>

      {/* Dependents list */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label className="text-xs font-semibold text-slate-800">Financial Dependents</Label>
          <Button type="button" variant="outline" size="sm" onClick={addDependent} className="text-xs">
            <Plus className="w-3.5 h-3.5 mr-1" /> Add Dependent
          </Button>
        </div>

        {dependents.map((dep, idx) => (
          <div key={idx} className="p-3 border border-slate-200 rounded-md bg-slate-50/50 grid grid-cols-1 sm:grid-cols-4 gap-2 items-center">
            <div className="sm:col-span-2">
              <Input
                placeholder="Dependent Full Name"
                value={dep.name}
                onChange={(e) => {
                  const updated = [...dependents];
                  updated[idx].name = e.target.value;
                  setDependents(updated);
                }}
                className="text-xs h-8 bg-white"
                required
              />
            </div>
            <div>
              <Input
                placeholder="Relation (e.g. Spouse)"
                value={dep.relation}
                onChange={(e) => {
                  const updated = [...dependents];
                  updated[idx].relation = e.target.value;
                  setDependents(updated);
                }}
                className="text-xs h-8 bg-white"
                required
              />
            </div>
            <div className="flex items-center gap-2">
              <Input
                type="number"
                placeholder="Age"
                value={dep.age}
                onChange={(e) => {
                  const updated = [...dependents];
                  updated[idx].age = Number(e.target.value);
                  setDependents(updated);
                }}
                className="text-xs h-8 bg-white w-20 font-mono"
                min={0}
                max={100}
                required
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={() => removeDependent(idx)}
                className="h-8 w-8 text-rose-500 hover:text-rose-700"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </Button>
            </div>
          </div>
        ))}
      </div>

      {/* Existing Insurance */}
      <div className="border-t border-slate-200 pt-4 space-y-3">
        <div className="flex items-center space-x-2">
          <Checkbox
            id="has_existing"
            checked={hasExistingInsurance}
            onCheckedChange={(checked) => setHasExistingInsurance(!!checked)}
          />
          <Label htmlFor="has_existing" className="text-xs text-slate-800 font-medium cursor-pointer">
            I currently hold active life or health insurance policies with other insurers.
          </Label>
        </div>

        {hasExistingInsurance && (
          <div className="space-y-3 pl-6 pt-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-600">List existing active policies:</span>
              <Button type="button" variant="outline" size="sm" onClick={addPolicy} className="text-xs">
                <Plus className="w-3.5 h-3.5 mr-1" /> Add Policy
              </Button>
            </div>

            {existingPolicies.map((pol, idx) => (
              <div key={idx} className="p-2 border border-slate-200 rounded-md bg-white grid grid-cols-1 sm:grid-cols-3 gap-2 items-center">
                <Input
                  placeholder="Insurer Name (e.g. LIC / HDFC Life)"
                  value={pol.insurer_name}
                  onChange={(e) => {
                    const u = [...existingPolicies];
                    u[idx].insurer_name = e.target.value;
                    setExistingPolicies(u);
                  }}
                  className="text-xs h-8 bg-white"
                  required
                />
                <Input
                  type="number"
                  placeholder="Sum Assured (₹)"
                  value={pol.sum_assured}
                  onChange={(e) => {
                    const u = [...existingPolicies];
                    u[idx].sum_assured = Number(e.target.value);
                    setExistingPolicies(u);
                  }}
                  className="text-xs h-8 font-mono bg-white"
                  required
                />
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    placeholder="Year Issued"
                    value={pol.year_issued || ""}
                    onChange={(e) => {
                      const u = [...existingPolicies];
                      u[idx].year_issued = Number(e.target.value);
                      setExistingPolicies(u);
                    }}
                    className="text-xs h-8 font-mono bg-white w-28"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => removePolicy(idx)}
                    className="h-8 w-8 text-rose-500 hover:text-rose-700"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Previous rejections */}
      <div className="border-t border-slate-200 pt-4 space-y-2">
        <div className="flex items-center space-x-2">
          <Checkbox
            id="has_rejections"
            checked={hasRejections}
            onCheckedChange={(checked) => setHasRejections(!!checked)}
          />
          <Label htmlFor="has_rejections" className="text-xs text-slate-800 font-medium cursor-pointer">
            Has any insurance proposal submitted by you ever been declined, postponed, or issued with special loading?
          </Label>
        </div>

        {hasRejections && (
          <div className="pl-6 pt-2">
            <Input
              placeholder="State insurer name, reason given, and year of decision"
              value={rejectionDetails}
              onChange={(e) => setRejectionDetails(e.target.value)}
              className="text-xs h-9 bg-white"
              required
            />
          </div>
        )}
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
