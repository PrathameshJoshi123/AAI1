"use client";

import React from "react";
import { StatutoryDeclarationsData } from "@/types/application";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ArrowLeft, ArrowRight, Scale, ShieldAlert } from "lucide-react";

interface StepStatutoryProps {
  initialData?: Partial<StatutoryDeclarationsData>;
  onNext: (data: StatutoryDeclarationsData) => void;
  onPrev: () => void;
}

export function StepStatutory({ initialData, onNext, onPrev }: StepStatutoryProps) {
  const [formData, setFormData] = React.useState<StatutoryDeclarationsData>({
    declaration_truthfulness: initialData?.declaration_truthfulness ?? true,
    section_45_insurance_act: initialData?.section_45_insurance_act ?? true,
    dpdp_consent: initialData?.dpdp_consent ?? true,
    consent_ckyc_verification: initialData?.consent_ckyc_verification ?? true,
    consent_timestamp: new Date().toISOString(),
  });
  const [error, setError] = React.useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (
      !formData.declaration_truthfulness ||
      !formData.section_45_insurance_act ||
      !formData.dpdp_consent ||
      !formData.consent_ckyc_verification
    ) {
      setError("All statutory and regulatory consent declarations are mandatory under IRDAI guidelines.");
      return;
    }

    onNext({ ...formData, consent_timestamp: new Date().toISOString() });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="border-b border-slate-200 pb-3">
        <h3 className="text-base font-semibold text-slate-900 flex items-center gap-2">
          <Scale className="w-5 h-5 text-blue-600" />
          Step 7: Statutory Declarations & Legal Consent
        </h3>
        <p className="text-xs text-slate-500 mt-1">
          Mandatory legal authorizations required before proposal submission and underwriting evaluation.
        </p>
      </div>

      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-md">
          {error}
        </div>
      )}

      {/* Section 45 Box */}
      <div className="p-4 bg-blue-50/60 border border-blue-200 rounded-lg space-y-2">
        <div className="flex items-center gap-2 text-xs font-semibold text-blue-900">
          <ShieldAlert className="w-4 h-4 text-blue-700" />
          Section 45 of Insurance Act, 1938 (3-Year Incontestability Clause)
        </div>
        <p className="text-[11px] text-blue-800 leading-relaxed">
          No policy of life insurance shall be called in question on any ground whatsoever after the expiry of three continuous years from the date of issuance or revival of the policy. Full and candid disclosure of all material facts (including medical history and existing coverage) ensures your policy remains fully incontestable and binding upon the insurer.
        </p>
      </div>

      <div className="space-y-4 pt-2">
        <div className="p-3 border border-slate-200 rounded-md bg-white flex items-start space-x-3">
          <Checkbox
            id="dec_truth"
            checked={formData.declaration_truthfulness}
            onCheckedChange={(checked) => setFormData({ ...formData, declaration_truthfulness: !!checked })}
            className="mt-0.5"
          />
          <Label htmlFor="dec_truth" className="text-xs text-slate-800 font-normal cursor-pointer leading-relaxed">
            <strong>Declaration of Truthfulness:</strong> I hereby declare that all statements, answers, and disclosures made in this proposal are true, complete, and accurate in all respects. I have not suppressed or misrepresented any material information that could influence the insurer’s risk assessment.
          </Label>
        </div>

        <div className="p-3 border border-slate-200 rounded-md bg-white flex items-start space-x-3">
          <Checkbox
            id="dec_sec45"
            checked={formData.section_45_insurance_act}
            onCheckedChange={(checked) => setFormData({ ...formData, section_45_insurance_act: !!checked })}
            className="mt-0.5"
          />
          <Label htmlFor="dec_sec45" className="text-xs text-slate-800 font-normal cursor-pointer leading-relaxed">
            <strong>Section 45 Acknowledgment:</strong> I acknowledge and understand the provisions of Section 45 of the Insurance Act 1938 regarding policy incontestability and full disclosure.
          </Label>
        </div>

        <div className="p-3 border border-slate-200 rounded-md bg-white flex items-start space-x-3">
          <Checkbox
            id="dec_dpdp"
            checked={formData.dpdp_consent}
            onCheckedChange={(checked) => setFormData({ ...formData, dpdp_consent: !!checked })}
            className="mt-0.5"
          />
          <Label htmlFor="dec_dpdp" className="text-xs text-slate-800 font-normal cursor-pointer leading-relaxed">
            <strong>DPDP Act 2023 Consent:</strong> In accordance with the Digital Personal Data Protection Act 2023, I grant explicit consent to the platform and insurer to securely process, transmit, and store my personal, financial, and health records solely for the purposes of underwriting, policy servicing, and fraud prevention.
          </Label>
        </div>

        <div className="p-3 border border-slate-200 rounded-md bg-white flex items-start space-x-3">
          <Checkbox
            id="dec_ckyc"
            checked={formData.consent_ckyc_verification}
            onCheckedChange={(checked) => setFormData({ ...formData, consent_ckyc_verification: !!checked })}
            className="mt-0.5"
          />
          <Label htmlFor="dec_ckyc" className="text-xs text-slate-800 font-normal cursor-pointer leading-relaxed">
            <strong>Central KYC (CKYC) & Bureau Consent:</strong> I authorize the insurer to verify my identity credentials through CERSAI / CKYC registry and obtain risk underwriting information from authorized verification agencies.
          </Label>
        </div>
      </div>

      <div className="flex justify-between pt-4">
        <Button type="button" variant="outline" size="sm" onClick={onPrev} className="text-xs">
          <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Previous Step
        </Button>
        <Button type="submit" size="sm" className="bg-blue-600 hover:bg-blue-700 text-white text-xs">
          Save & Proceed to Document Upload <ArrowRight className="w-3.5 h-3.5 ml-1" />
        </Button>
      </div>
    </form>
  );
}
