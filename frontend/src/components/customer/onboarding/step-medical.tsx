"use client";

import React from "react";
import { MedicalLifestyleData, DynamicDeclaration } from "@/types/application";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ArrowLeft, ArrowRight, HeartPulse } from "lucide-react";

interface StepMedicalProps {
  initialData?: Partial<MedicalLifestyleData>;
  declarations?: DynamicDeclaration[];
  onNext: (data: MedicalLifestyleData) => void;
  onPrev: () => void;
}

export function StepMedical({ initialData, declarations = [], onNext, onPrev }: StepMedicalProps) {
  const [formData, setFormData] = React.useState<MedicalLifestyleData>({
    height_cm: initialData?.height_cm || 175,
    weight_kg: initialData?.weight_kg || 72,
    tobacco_use: initialData?.tobacco_use ?? false,
    alcohol_consumption: initialData?.alcohol_consumption || "none",
    pre_existing_conditions: initialData?.pre_existing_conditions || {},
    hospitalization_past_5_years: initialData?.hospitalization_past_5_years ?? false,
    hospitalization_details: initialData?.hospitalization_details || "",
    family_history_critical: initialData?.family_history_critical ?? false,
    family_history_details: initialData?.family_history_details || "",
  });

  const bmi = React.useMemo(() => {
    if (formData.height_cm > 0 && formData.weight_kg > 0) {
      const hM = formData.height_cm / 100;
      return (formData.weight_kg / (hM * hM)).toFixed(1);
    }
    return "23.5";
  }, [formData.height_cm, formData.weight_kg]);

  const handleConditionToggle = (id: string, checked: boolean) => {
    setFormData({
      ...formData,
      pre_existing_conditions: {
        ...formData.pre_existing_conditions,
        [id]: checked,
      },
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNext(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="border-b border-slate-200 pb-3">
        <h3 className="text-base font-semibold text-slate-900 flex items-center gap-2">
          <HeartPulse className="w-5 h-5 text-blue-600" />
          Step 5: Medical & Lifestyle Disclosures
        </h3>
        <p className="text-xs text-slate-500 mt-1">
          Complete and transparent disclosures guarantee incontestable claim settlements under Section 45 of the Insurance Act 1938.
        </p>
      </div>

      {/* Biometrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 p-4 border border-slate-200 rounded-md bg-slate-50/50">
        <div className="space-y-1.5">
          <Label htmlFor="height" className="text-xs font-medium text-slate-700">
            Height (in cm) *
          </Label>
          <Input
            id="height"
            type="number"
            value={formData.height_cm}
            onChange={(e) => setFormData({ ...formData, height_cm: Number(e.target.value) })}
            min={100}
            max={250}
            required
            className="text-xs h-9 font-mono bg-white"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="weight" className="text-xs font-medium text-slate-700">
            Weight (in kg) *
          </Label>
          <Input
            id="weight"
            type="number"
            value={formData.weight_kg}
            onChange={(e) => setFormData({ ...formData, weight_kg: Number(e.target.value) })}
            min={30}
            max={200}
            required
            className="text-xs h-9 font-mono bg-white"
          />
        </div>

        <div className="space-y-1.5">
          <Label className="text-xs font-medium text-slate-700">Calculated Body Mass Index (BMI)</Label>
          <div className="h-9 rounded-md bg-white border border-slate-200 flex items-center px-3 text-xs font-mono font-semibold text-blue-700">
            {bmi} kg/m²
            <span className="text-[11px] font-normal text-slate-500 ml-2">
              {Number(bmi) < 18.5
                ? "(Underweight)"
                : Number(bmi) <= 24.9
                ? "(Standard/Healthy)"
                : Number(bmi) <= 29.9
                ? "(Overweight)"
                : "(Obese)"}
            </span>
          </div>
        </div>
      </div>

      {/* Habits */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-2 p-3 border border-slate-200 rounded-md bg-white">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="tobacco"
              checked={formData.tobacco_use}
              onCheckedChange={(checked) => setFormData({ ...formData, tobacco_use: !!checked })}
            />
            <Label htmlFor="tobacco" className="text-xs font-medium text-slate-800 cursor-pointer">
              I have used tobacco / cigarettes in the past 36 months.
            </Label>
          </div>
          <p className="text-[11px] text-slate-400 pl-6">
            Non-smoker preferred rates require strict abstinence from all nicotine/tobacco products for at least 3 years.
          </p>
        </div>

        <div className="space-y-1.5 p-3 border border-slate-200 rounded-md bg-white">
          <Label className="text-xs font-medium text-slate-700">Alcohol Consumption</Label>
          <Select
            value={formData.alcohol_consumption}
            onValueChange={(val: any) => setFormData({ ...formData, alcohol_consumption: val })}
          >
            <SelectTrigger className="text-xs h-9 bg-white">
              <SelectValue placeholder="Select alcohol frequency" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">Teetotaler / Never</SelectItem>
              <SelectItem value="occasional">Occasional / Social (1-2 drinks/month)</SelectItem>
              <SelectItem value="regular">Regular Consumption</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Dynamic Health Question Declarations */}
      <div className="space-y-3 border-t border-slate-200 pt-4">
        <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider">
          Medical History & Pre-Existing Health Conditions
        </h4>

        {declarations.length > 0 ? (
          declarations.map((dec) => (
            <div key={dec.id} className="p-3 border border-slate-200 rounded-md bg-slate-50/50 space-y-2">
              <div className="flex items-start space-x-2">
                <Checkbox
                  id={dec.id}
                  checked={!!formData.pre_existing_conditions[dec.id]}
                  onCheckedChange={(checked) => handleConditionToggle(dec.id, !!checked)}
                  className="mt-0.5"
                />
                <Label htmlFor={dec.id} className="text-xs text-slate-800 font-normal cursor-pointer leading-relaxed">
                  {dec.question}
                </Label>
              </div>
            </div>
          ))
        ) : (
          <div className="space-y-2">
            {[
              { id: "dec_diabetes", label: "Have you ever been treated for Diabetes, Elevated Blood Sugar, or Glycosuria?" },
              { id: "dec_cardiac", label: "Have you experienced Chest Pain, Heart Attack, Hypertension, or High Cholesterol?" },
              { id: "dec_respiratory", label: "Have you been diagnosed with Asthma, Tuberculosis, or Chronic Respiratory conditions?" },
            ].map((item) => (
              <div key={item.id} className="p-3 border border-slate-200 rounded-md bg-slate-50/50 flex items-start space-x-2">
                <Checkbox
                  id={item.id}
                  checked={!!formData.pre_existing_conditions[item.id]}
                  onCheckedChange={(checked) => handleConditionToggle(item.id, !!checked)}
                  className="mt-0.5"
                />
                <Label htmlFor={item.id} className="text-xs text-slate-800 font-normal cursor-pointer">
                  {item.label}
                </Label>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Hospitalization past 5 years */}
      <div className="space-y-2 border-t border-slate-200 pt-4">
        <div className="flex items-center space-x-2">
          <Checkbox
            id="hosp"
            checked={formData.hospitalization_past_5_years}
            onCheckedChange={(checked) => setFormData({ ...formData, hospitalization_past_5_years: !!checked })}
          />
          <Label htmlFor="hosp" className="text-xs text-slate-800 font-medium cursor-pointer">
            Have you been hospitalized or undergone any surgical procedure within the last 5 years?
          </Label>
        </div>

        {formData.hospitalization_past_5_years && (
          <div className="pl-6 pt-2">
            <Input
              placeholder="State reason, hospital name, and year (e.g. Appendectomy, Apollo Hospital, 2023)"
              value={formData.hospitalization_details}
              onChange={(e) => setFormData({ ...formData, hospitalization_details: e.target.value })}
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
