"use client";

import React from "react";
import { PersonalInfoData } from "@/types/application";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { ArrowRight, UserCheck } from "lucide-react";

interface StepPersonalProps {
  initialData?: Partial<PersonalInfoData>;
  onNext: (data: PersonalInfoData) => void;
}

export function StepPersonal({ initialData, onNext }: StepPersonalProps) {
  const [formData, setFormData] = React.useState<PersonalInfoData>({
    full_name: initialData?.full_name || "",
    date_of_birth: initialData?.date_of_birth || "1994-06-15",
    gender: initialData?.gender || "male",
    marital_status: initialData?.marital_status || "married",
    pan_number: initialData?.pan_number || "",
    aadhaar_last_four: initialData?.aadhaar_last_four || "",
    nationality: initialData?.nationality || "IN",
  });
  const [error, setError] = React.useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.full_name.trim() || formData.full_name.length < 2) {
      setError("Please provide your full legal name as it appears on official records.");
      return;
    }
    const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
    if (!panRegex.test(formData.pan_number.toUpperCase())) {
      setError("Please enter a valid 10-character PAN number (e.g. ABCDE1234F).");
      return;
    }
    if (!/^\d{4}$/.test(formData.aadhaar_last_four)) {
      setError("Please enter the last 4 digits of your Aadhaar number.");
      return;
    }

    onNext({ ...formData, pan_number: formData.pan_number.toUpperCase() });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="border-b border-slate-200 pb-3">
        <h3 className="text-base font-semibold text-slate-900 flex items-center gap-2">
          <UserCheck className="w-5 h-5 text-blue-600" />
          Step 1: Personal Demographics & Government Identity
        </h3>
        <p className="text-xs text-slate-500 mt-1">
          Identity details must match official government records for KYC and claim verification.
        </p>
      </div>

      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-md">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-1.5 sm:col-span-2">
          <Label htmlFor="full_name" className="text-xs font-medium text-slate-700">
            Full Legal Name (as per PAN Card) *
          </Label>
          <Input
            id="full_name"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            placeholder="e.g. Rajesh Kumar Sharma"
            required
            className="text-xs h-9 bg-white"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="date_of_birth" className="text-xs font-medium text-slate-700">
            Date of Birth *
          </Label>
          <Input
            id="date_of_birth"
            type="date"
            value={formData.date_of_birth}
            onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
            required
            className="text-xs h-9 bg-white"
          />
        </div>

        <div className="space-y-1.5">
          <Label className="text-xs font-medium text-slate-700">Gender *</Label>
          <Select
            value={formData.gender}
            onValueChange={(val: any) => setFormData({ ...formData, gender: val })}
          >
            <SelectTrigger className="text-xs h-9 bg-white">
              <SelectValue placeholder="Select gender" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="male">Male</SelectItem>
              <SelectItem value="female">Female</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label className="text-xs font-medium text-slate-700">Marital Status *</Label>
          <Select
            value={formData.marital_status}
            onValueChange={(val: any) => setFormData({ ...formData, marital_status: val })}
          >
            <SelectTrigger className="text-xs h-9 bg-white">
              <SelectValue placeholder="Select marital status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="married">Married</SelectItem>
              <SelectItem value="single">Single / Unmarried</SelectItem>
              <SelectItem value="divorced">Divorced</SelectItem>
              <SelectItem value="widowed">Widowed</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="pan_number" className="text-xs font-medium text-slate-700">
            PAN Number (Permanent Account Number) *
          </Label>
          <Input
            id="pan_number"
            value={formData.pan_number}
            onChange={(e) => setFormData({ ...formData, pan_number: e.target.value.toUpperCase() })}
            placeholder="ABCDE1234F"
            maxLength={10}
            required
            className="text-xs h-9 uppercase font-mono bg-white"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="aadhaar_last_four" className="text-xs font-medium text-slate-700">
            Aadhaar Last 4 Digits *
          </Label>
          <Input
            id="aadhaar_last_four"
            value={formData.aadhaar_last_four}
            onChange={(e) => setFormData({ ...formData, aadhaar_last_four: e.target.value.replace(/\D/g, "") })}
            placeholder="XXXX-XXXX-1234"
            maxLength={4}
            required
            className="text-xs h-9 font-mono bg-white"
          />
          <p className="text-[11px] text-slate-400">
            Only the last 4 digits are stored in accordance with UIDAI privacy standards.
          </p>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="nationality" className="text-xs font-medium text-slate-700">
            Nationality
          </Label>
          <Input
            id="nationality"
            value="Indian (IN)"
            disabled
            className="text-xs h-9 bg-slate-50 text-slate-600"
          />
        </div>
      </div>

      <div className="flex justify-end pt-4">
        <Button type="submit" size="sm" className="bg-blue-600 hover:bg-blue-700 text-white text-xs">
          Save & Next Step <ArrowRight className="w-3.5 h-3.5 ml-1" />
        </Button>
      </div>
    </form>
  );
}
