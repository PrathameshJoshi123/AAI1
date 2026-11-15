"use client";

import React from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ApplicationAPI } from "@/services/application.service";
import { ApplicationItem, DynamicRequirements } from "@/types/application";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { StepIndicator } from "@/components/customer/onboarding/step-indicator";
import { StepPersonal } from "@/components/customer/onboarding/step-personal";
import { StepAddress } from "@/components/customer/onboarding/step-address";
import { StepEmployment } from "@/components/customer/onboarding/step-employment";
import { StepFamily } from "@/components/customer/onboarding/step-family";
import { StepMedical } from "@/components/customer/onboarding/step-medical";
import { StepNominee } from "@/components/customer/onboarding/step-nominee";
import { StepStatutory } from "@/components/customer/onboarding/step-statutory";
import { StepDocuments } from "@/components/customer/onboarding/step-documents";
import { OnboardingAIDrawer } from "@/components/customer/onboarding/onboarding-ai-drawer";
import { Button } from "@/components/ui/button";
import {
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  FileCheck2,
  Clock,
  Loader2,
  AlertCircle,
} from "lucide-react";

const STEP_LABELS = [
  "Personal Demographics",
  "Contact & Address",
  "Occupational & Financial",
  "Family & Coverage",
  "Medical & Health",
  "Nominee Designations",
  "Statutory Declarations",
  "Document Upload",
];

export default function OnboardingWizardPage() {
  const params = useParams();
  const router = useRouter();
  const quoteId = params.quoteId as string;

  const [loading, setLoading] = React.useState<boolean>(true);
  const [application, setApplication] = React.useState<ApplicationItem | null>(null);
  const [requirements, setRequirements] = React.useState<DynamicRequirements | null>(null);
  const [currentStep, setCurrentStep] = React.useState<number>(1);
  const [autoSaveStatus, setAutoSaveStatus] = React.useState<string | null>(null);
  const [submittedApp, setSubmittedApp] = React.useState<ApplicationItem | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  // Load or initialize application draft
  React.useEffect(() => {
    async function init() {
      if (!quoteId) return;
      try {
        setLoading(true);
        const app = await ApplicationAPI.getOrCreateDraft(quoteId);
        setApplication(app);
        if (app.status === "submitted" || app.status === "under_review") {
          setSubmittedApp(app);
          setLoading(false);
          return;
        }
        setCurrentStep(app.current_step || 1);

        const reqs = await ApplicationAPI.getRequirements(app.id);
        setRequirements(reqs);
      } catch (err: any) {
        setError(err.message || "Failed to initialize application draft.");
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [quoteId]);

  const handleStepSave = async (stepKey: string, stepData: Record<string, any>, nextStepNum: number) => {
    if (!application) return;
    setAutoSaveStatus("Saving draft...");

    try {
      const updated = await ApplicationAPI.saveDraftStep(
        application.id,
        nextStepNum,
        stepKey,
        stepData
      );
      setApplication(updated);
      setCurrentStep(nextStepNum);
      const timeStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      setAutoSaveStatus(`Draft saved automatically at ${timeStr}`);
    } catch (err: any) {
      setAutoSaveStatus("Auto-save failed");
      setError(err.message || "Could not save step draft.");
    }
  };

  const handleProposalSubmit = async (eSignatureName: string) => {
    if (!application) return;
    const finalApp = await ApplicationAPI.submitProposal(application.id, eSignatureName);
    setSubmittedApp(finalApp);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-3">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        <p className="text-xs text-slate-500 font-medium">Preparing proposal questionnaire...</p>
      </div>
    );
  }

  if (error && !application) {
    return (
      <div className="max-w-xl mx-auto py-12">
        <Card className="border-rose-200 bg-white p-6 text-center space-y-4">
          <AlertCircle className="w-10 h-10 text-rose-600 mx-auto" />
          <h2 className="text-base font-bold text-slate-900">Application Error</h2>
          <p className="text-xs text-slate-600 leading-relaxed">{error}</p>
          <Button size="sm" asChild className="bg-blue-600 hover:bg-blue-700 text-white text-xs">
            <Link href="/customer/quotes">Return to Quotes</Link>
          </Button>
        </Card>
      </div>
    );
  }

  // Submitted success screen
  if (submittedApp) {
    return (
      <div className="max-w-2xl mx-auto py-10 space-y-6">
        <Card className="border-emerald-200 bg-white p-8 text-center space-y-4 shadow-sm">
          <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-6 h-6 text-emerald-600" />
          </div>
          <h2 className="text-xl font-bold text-slate-900">
            Insurance Proposal Submitted
          </h2>
          <p className="text-xs text-slate-600 max-w-md mx-auto leading-relaxed">
            Your application proposal has been logged and assigned to the underwriting review queue.
          </p>

          <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg max-w-md mx-auto text-left space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-500">Application Number:</span>
              <span className="font-mono font-bold text-slate-900">
                {submittedApp.application_number}
              </span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-500">Current Status:</span>
              <span className="font-semibold text-blue-700 capitalize">
                {submittedApp.status.replace("_", " ")}
              </span>
            </div>
            {submittedApp.proposal_checksum && (
              <div className="flex justify-between text-[11px] pt-1 border-t border-slate-200">
                <span className="text-slate-500">Proposal Checksum:</span>
                <span className="font-mono text-slate-700">
                  {submittedApp.proposal_checksum.substring(0, 16)}...
                </span>
              </div>
            )}
          </div>

          <div className="pt-4 flex justify-center gap-3">
            <Button size="sm" asChild className="bg-blue-600 hover:bg-blue-700 text-white text-xs">
              <Link href="/customer/applications">
                Track Application Status <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </Link>
            </Button>
            <Button size="sm" variant="outline" asChild className="text-xs">
              <Link href="/customer/documents">View Document Vault</Link>
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  const proposalData = application?.proposal_data_json || {};
  const currentStepName = STEP_LABELS[currentStep - 1] || "Proposal Step";

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <PageHeader
          title="Insurance Proposal Onboarding"
          description={`Application #${application?.application_number} — Complete proposal disclosures and document verification`}
          breadcrumbs={[
            { label: "Customer Portal", href: "/customer" },
            { label: "Quotes", href: "/customer/quotes" },
            { label: "Proposal Onboarding" },
          ]}
        />
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <OnboardingAIDrawer currentStepName={currentStepName} />
        </div>
      </div>

      {/* Auto save indicator */}
      {autoSaveStatus && (
        <div className="flex items-center gap-1.5 text-[11px] text-slate-500 px-1">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>{autoSaveStatus}</span>
        </div>
      )}

      {/* 8-Step Stepper */}
      <StepIndicator
        currentStep={currentStep}
        totalSteps={8}
        stepLabels={STEP_LABELS}
        completedSteps={application?.step_progress_json || {}}
        onStepClick={(s) => setCurrentStep(s)}
      />

      {/* Active Step Container */}
      <Card className="border-slate-200 bg-white shadow-2xs">
        <CardContent className="p-6">
          {currentStep === 1 && (
            <StepPersonal
              initialData={proposalData.personal_info}
              onNext={(data) => handleStepSave("personal_info", data, 2)}
            />
          )}

          {currentStep === 2 && (
            <StepAddress
              initialData={proposalData.contact_address}
              onNext={(data) => handleStepSave("contact_address", data, 3)}
              onPrev={() => setCurrentStep(1)}
            />
          )}

          {currentStep === 3 && (
            <StepEmployment
              initialData={proposalData.employment_financial}
              onNext={(data) => handleStepSave("employment_financial", data, 4)}
              onPrev={() => setCurrentStep(2)}
            />
          )}

          {currentStep === 4 && (
            <StepFamily
              initialData={proposalData.family_coverage}
              onNext={(data) => handleStepSave("family_coverage", data, 5)}
              onPrev={() => setCurrentStep(3)}
            />
          )}

          {currentStep === 5 && (
            <StepMedical
              initialData={proposalData.medical_lifestyle}
              declarations={requirements?.declarations || []}
              onNext={(data) => handleStepSave("medical_lifestyle", data, 6)}
              onPrev={() => setCurrentStep(4)}
            />
          )}

          {currentStep === 6 && (
            <StepNominee
              initialNominees={proposalData.nominee_details?.nominees}
              onNext={(nominees) => handleStepSave("nominee_details", { nominees }, 7)}
              onPrev={() => setCurrentStep(5)}
            />
          )}

          {currentStep === 7 && (
            <StepStatutory
              initialData={proposalData.statutory_declarations}
              onNext={(data) => handleStepSave("statutory_declarations", data, 8)}
              onPrev={() => setCurrentStep(6)}
            />
          )}

          {currentStep === 8 && application && (
            <StepDocuments
              applicationId={application.id}
              requirements={requirements?.required_documents || []}
              existingDocuments={application.documents || []}
              applicantName={proposalData.personal_info?.full_name || ""}
              onPrev={() => setCurrentStep(7)}
              onSubmitProposal={handleProposalSubmit}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
