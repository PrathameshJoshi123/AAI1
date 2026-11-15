"use client";

import React from "react";
import { NomineeData } from "@/types/application";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { ArrowLeft, ArrowRight, ShieldCheck, Plus, Trash2, AlertCircle } from "lucide-react";

interface StepNomineeProps {
  initialNominees?: NomineeData[];
  onNext: (nominees: NomineeData[]) => void;
  onPrev: () => void;
}

export function StepNominee({ initialNominees, onNext, onPrev }: StepNomineeProps) {
  const [nominees, setNominees] = React.useState<NomineeData[]>(
    initialNominees && initialNominees.length > 0
      ? initialNominees
      : [
          {
            nominee_name: "Sunita Sharma",
            relation: "spouse",
            date_of_birth: "1996-08-20",
            share_percentage: 100,
          },
        ]
  );
  const [error, setError] = React.useState<string | null>(null);

  const totalShare = React.useMemo(() => {
    return nominees.reduce((acc, n) => acc + (Number(n.share_percentage) || 0), 0);
  }, [nominees]);

  const isMinor = (dobStr: string) => {
    if (!dobStr) return false;
    const birth = new Date(dobStr);
    const ageDiffMs = Date.now() - birth.getTime();
    const ageDate = new Date(ageDiffMs);
    const age = Math.abs(ageDate.getUTCFullYear() - 1970);
    return age < 18;
  };

  const addNominee = () => {
    if (nominees.length >= 3) {
      setError("A maximum of 3 nominees can be designated.");
      return;
    }
    setNominees([
      ...nominees,
      {
        nominee_name: "",
        relation: "child",
        date_of_birth: "2020-01-01",
        share_percentage: 50,
      },
    ]);
  };

  const removeNominee = (idx: number) => {
    if (nominees.length <= 1) {
      setError("At least one nominee is mandatory.");
      return;
    }
    setNominees(nominees.filter((_, i) => i !== idx));
  };

  const updateNominee = (idx: number, patch: Partial<NomineeData>) => {
    const updated = [...nominees];
    updated[idx] = { ...updated[idx], ...patch };
    setNominees(updated);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate 100% share sum
    if (Math.abs(totalShare - 100) > 0.01) {
      setError(`Nominee share percentages must total exactly 100%. Current total is ${totalShare}%.`);
      return;
    }

    // Validate names and minor appointees
    for (let i = 0; i < nominees.length; i++) {
      const n = nominees[i];
      if (!n.nominee_name.trim()) {
        setError(`Please enter the full legal name for Nominee #${i + 1}.`);
        return;
      }
      if (isMinor(n.date_of_birth)) {
        if (!n.appointee_name?.trim() || !n.appointee_contact?.trim()) {
          setError(
            `Nominee #${i + 1} (${n.nominee_name}) is a minor under 18 years of age. An adult Appointee name and contact number are mandatory under Section 39 of the Insurance Act.`
          );
          return;
        }
      }
    }

    onNext(nominees);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="border-b border-slate-200 pb-3 flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-slate-900 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-blue-600" />
            Step 6: Nominee & Appointee Designations
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Section 39 Insurance Act 1938 requires explicit nominee registration. Total allocation must equal 100%.
          </p>
        </div>
        {nominees.length < 3 && (
          <Button type="button" variant="outline" size="sm" onClick={addNominee} className="text-xs">
            <Plus className="w-3.5 h-3.5 mr-1" /> Add Nominee
          </Button>
        )}
      </div>

      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-md flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Share Progress Bar */}
      <div className="p-3 bg-slate-50 border border-slate-200 rounded-md space-y-1.5">
        <div className="flex justify-between text-xs font-medium">
          <span className="text-slate-700">Total Share Allocation</span>
          <span
            className={
              totalShare === 100
                ? "text-emerald-700 font-bold"
                : "text-amber-700 font-bold"
            }
          >
            {totalShare}% / 100%
          </span>
        </div>
        <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all ${
              totalShare === 100
                ? "bg-emerald-500"
                : totalShare > 100
                ? "bg-rose-500"
                : "bg-blue-600"
            }`}
            style={{ width: `${Math.min(totalShare, 100)}%` }}
          />
        </div>
      </div>

      {/* Nominees list */}
      <div className="space-y-4">
        {nominees.map((nom, idx) => {
          const minor = isMinor(nom.date_of_birth);

          return (
            <div key={idx} className="p-4 border border-slate-200 rounded-lg bg-white space-y-3 relative shadow-2xs">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                <span className="text-xs font-semibold text-slate-900">
                  Nominee #{idx + 1}
                </span>
                {nominees.length > 1 && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => removeNominee(idx)}
                    className="text-rose-500 hover:text-rose-700 text-xs h-7"
                  >
                    <Trash2 className="w-3 h-3 mr-1" /> Remove
                  </Button>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1 sm:col-span-2">
                  <Label className="text-xs font-medium text-slate-700">Nominee Full Legal Name *</Label>
                  <Input
                    placeholder="As shown on identity proof"
                    value={nom.nominee_name}
                    onChange={(e) => updateNominee(idx, { nominee_name: e.target.value })}
                    required
                    className="text-xs h-9 bg-white"
                  />
                </div>

                <div className="space-y-1">
                  <Label className="text-xs font-medium text-slate-700">Relationship with Life Assured *</Label>
                  <Select
                    value={nom.relation}
                    onValueChange={(val: any) => updateNominee(idx, { relation: val })}
                  >
                    <SelectTrigger className="text-xs h-9 bg-white">
                      <SelectValue placeholder="Select relation" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="spouse">Spouse</SelectItem>
                      <SelectItem value="child">Child (Son / Daughter)</SelectItem>
                      <SelectItem value="parent">Parent (Mother / Father)</SelectItem>
                      <SelectItem value="sibling">Sibling (Brother / Sister)</SelectItem>
                      <SelectItem value="other">Other Legal Dependent</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-1">
                  <Label className="text-xs font-medium text-slate-700">Date of Birth *</Label>
                  <Input
                    type="date"
                    value={nom.date_of_birth}
                    onChange={(e) => updateNominee(idx, { date_of_birth: e.target.value })}
                    required
                    className="text-xs h-9 bg-white"
                  />
                </div>

                <div className="space-y-1 sm:col-span-2">
                  <Label className="text-xs font-medium text-slate-700">Claim Share Percentage (%) *</Label>
                  <Input
                    type="number"
                    value={nom.share_percentage}
                    onChange={(e) => updateNominee(idx, { share_percentage: Number(e.target.value) })}
                    min={1}
                    max={100}
                    required
                    className="text-xs h-9 font-mono bg-white"
                  />
                </div>
              </div>

              {/* Appointee Section if minor */}
              {minor && (
                <div className="mt-3 p-3 bg-amber-50/60 border border-amber-200 rounded-md space-y-2">
                  <div className="text-[11px] font-semibold text-amber-900">
                    Minor Nominee Appointee (Mandatory since nominee is under 18)
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    <div>
                      <Input
                        placeholder="Appointee Legal Name"
                        value={nom.appointee_name || ""}
                        onChange={(e) => updateNominee(idx, { appointee_name: e.target.value })}
                        required
                        className="text-xs h-8 bg-white"
                      />
                    </div>
                    <div>
                      <Input
                        placeholder="Appointee Relationship"
                        value={nom.appointee_relation || ""}
                        onChange={(e) => updateNominee(idx, { appointee_relation: e.target.value })}
                        required
                        className="text-xs h-8 bg-white"
                      />
                    </div>
                    <div>
                      <Input
                        placeholder="10-digit Mobile"
                        value={nom.appointee_contact || ""}
                        onChange={(e) => updateNominee(idx, { appointee_contact: e.target.value.replace(/\D/g, "") })}
                        required
                        maxLength={10}
                        className="text-xs h-8 bg-white font-mono"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
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
