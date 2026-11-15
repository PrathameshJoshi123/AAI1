"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Bot, HelpCircle, ShieldAlert, Sparkles, CheckCircle2 } from "lucide-react";

interface OnboardingAIDrawerProps {
  currentStepName: string;
}

const STEP_KNOWLEDGE: Record<string, { title: string; explanation: string; statutory: string; tips: string[] }> = {
  "Personal Demographics": {
    title: "Why Exact Demographics Matter",
    explanation:
      "Your full legal name and date of birth must match your official PAN card. Inconsistencies between proposal records and government KYC databases can cause delays during underwriting or future claim settlements.",
    statutory:
      "IRDAI guidelines mandate Central KYC (CKYC) verification prior to policy issuance.",
    tips: [
      "Enter your name exactly as printed on your PAN card.",
      "Check your date of birth carefully; age directly determines actuarial rate bands.",
    ],
  },
  "Contact & Address": {
    title: "Communication & Regulatory Address",
    explanation:
      "Statutory notices, policy documents, and renewal schedules will be dispatched to your residential address. A valid PIN code ensures postal delivery.",
    statutory:
      "Section 45 of Insurance Act 1938 requires maintainable official contact addresses on file.",
    tips: [
      "Ensure your primary mobile number is active to receive verification OTPs.",
      "Provide complete landmark details.",
    ],
  },
  "Occupational & Financial": {
    title: "Financial Underwriting Guidelines",
    explanation:
      "Life insurance coverage is designed to replace future economic earnings for your dependents. Underwriters evaluate Human Life Value (HLV) against declared annual income.",
    statutory:
      "Underwriting guidelines typically permit sum assured up to 20x annual income for ages under 35, and 10–15x for ages 36–50.",
    tips: [
      "Declare your gross annual income (before income tax deductions).",
      "Have your latest ITR-V or Form 16 ready if Sum Assured exceeds ₹50 Lakhs.",
    ],
  },
  "Family & Coverage": {
    title: "Aggregated Insurance Capacity",
    explanation:
      "Insurers share underwriting data across the industry. Disclosing existing active policies prevents accidental over-insurance and confirms eligibility.",
    statutory:
      "Non-disclosure of existing coverage may be treated as material suppression under insurance regulations.",
    tips: [
      "Include employer group policies or personal term plans.",
      "If you had a previous application declined, disclose the reason transparently.",
    ],
  },
  "Medical & Health": {
    title: "Medical Transparency & Section 45",
    explanation:
      "Disclosing pre-existing health conditions or past hospitalizations does NOT mean your application will be rejected. Most standard conditions are accepted normally or with a modest health loading.",
    statutory:
      "Section 45: A policy cannot be called in question after 3 continuous years. Truthful declarations protect your family's financial security forever.",
    tips: [
      "Declare any prescription medicines you take on a regular basis.",
      "State accurate height and weight so BMI is calculated properly.",
    ],
  },
  "Nominee Designations": {
    title: "Securing Policy Claim Proceeds",
    explanation:
      "A nominee is legally authorized to receive claim proceeds. You can designate up to 3 nominees. Their percentage share must total exactly 100%.",
    statutory:
      "Section 39 Insurance Act 1938: If any nominee is a minor (<18 years), you must appoint an adult Appointee.",
    tips: [
      "Ensure nominee name matches their Aadhaar card.",
      "Verify that the total allocation equals 100%.",
    ],
  },
  "Statutory Declarations": {
    title: "Legal Consent & DPDP Compliance",
    explanation:
      "Your declarations confirm that the provided information is true. Your consent allows secure data processing under the Digital Personal Data Protection Act 2023.",
    statutory:
      "Digital verification creates an immutable SHA-256 proposal checksum logged in audit records.",
    tips: [
      "Review each statement carefully before checking the boxes.",
    ],
  },
  "Document Upload": {
    title: "Document Verification Standards",
    explanation:
      "Upload clean, un-cropped scans or photos of your PAN card, Address Proof, and Income documents. Clear documents ensure faster underwriting approval.",
    statutory:
      "All documents are securely stored and verified with SHA-256 cryptographic digests.",
    tips: [
      "Ensure all 4 corners of identity cards are clearly visible.",
      "Maximum file size is 10 MB per document in PDF, JPEG, or PNG format.",
    ],
  },
};

export function OnboardingAIDrawer({ currentStepName }: OnboardingAIDrawerProps) {
  const info = STEP_KNOWLEDGE[currentStepName] || {
    title: "Proposal Completion Support",
    explanation: "Please ensure all details match your official documents.",
    statutory: "Governed under IRDAI regulations.",
    tips: ["Fill out all required fields before proceeding."],
  };

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="bg-blue-50/70 border-blue-200 text-blue-700 hover:bg-blue-100 text-xs flex items-center gap-1.5"
        >
          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
          <span>AI Guidance for this Step</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-full sm:max-w-md bg-white border-l border-slate-200 p-6 space-y-5">
        <SheetHeader>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center">
              <Bot className="w-4 h-4 text-blue-700" />
            </div>
            <div>
              <SheetTitle className="text-sm font-semibold text-slate-900">
                AI Onboarding Assistant
              </SheetTitle>
              <p className="text-[11px] text-slate-500">{currentStepName}</p>
            </div>
          </div>
        </SheetHeader>

        <Card className="border-slate-200 bg-slate-50/50 shadow-2xs">
          <CardHeader className="p-3 pb-1">
            <CardTitle className="text-xs font-semibold text-slate-900 flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-blue-600" />
              {info.title}
            </CardTitle>
          </CardHeader>
          <CardContent className="p-3 text-xs text-slate-600 leading-relaxed space-y-2">
            <p>{info.explanation}</p>
          </CardContent>
        </Card>

        <Card className="border-blue-200 bg-blue-50/50 shadow-2xs">
          <CardHeader className="p-3 pb-1">
            <CardTitle className="text-xs font-semibold text-blue-900 flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5 text-blue-700" />
              Regulatory & Statutory Context
            </CardTitle>
          </CardHeader>
          <CardContent className="p-3 text-xs text-blue-800 leading-relaxed">
            <p>{info.statutory}</p>
          </CardContent>
        </Card>

        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-slate-800">Best Practices & Tips</h4>
          <ul className="space-y-1.5">
            {info.tips.map((tip, i) => (
              <li key={i} className="text-xs text-slate-600 flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                <span>{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      </SheetContent>
    </Sheet>
  );
}
