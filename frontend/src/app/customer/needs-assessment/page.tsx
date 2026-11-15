"use client";

import * as React from "react";
import Link from "next/link";
import {
  ListChecks,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  ShieldCheck,
  Heart,
  Activity,
  Car,
  Loader2,
  Edit3,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { CustomerAPI } from "@/services/customer-api";
import { NeedsAssessmentPayload, NeedsAssessmentResult } from "@/types/customer";

export default function NeedsAssessmentPage() {
  const [step, setStep] = React.useState<number>(1);
  const [initialLoading, setInitialLoading] = React.useState<boolean>(true);
  const [hasExistingAssessment, setHasExistingAssessment] = React.useState<boolean>(false);
  const [formData, setFormData] = React.useState<NeedsAssessmentPayload>({
    category: "term_life",
    age: 32,
    annual_income: 1200000,
    dependents_count: 2,
    marital_status: "married",
    occupation: "Salaried Professional",
    tobacco_user: false,
    has_pre_existing_conditions: false,
    pre_existing_conditions_details: "",
    existing_life_cover: 2500000,
    existing_health_cover: 500000,
    desired_coverage_amount: 15000000,
  });

  const [loading, setLoading] = React.useState<boolean>(false);
  const [result, setResult] = React.useState<NeedsAssessmentResult | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    async function initPage() {
      try {
        const urlParams = typeof window !== "undefined" ? new URLSearchParams(window.location.search) : null;
        const wantEdit = urlParams?.get("edit") === "true" || urlParams?.get("retake") === "true";
        const catParam = urlParams?.get("category");

        const summary = await CustomerAPI.getNeedsSummary();
        if (summary && summary.has_assessment) {
          setHasExistingAssessment(true);
          const f = summary.factors || {};
          const loadedData: NeedsAssessmentPayload = {
            category: (catParam as any) || summary.target_category || summary.category || "term_life",
            age: f.age || 32,
            annual_income: f.declared_annual_income || summary.financial_capacity || 1200000,
            dependents_count: f.dependents !== undefined ? f.dependents : 2,
            marital_status: f.marital_status || "married",
            occupation: f.occupation || "Salaried Professional",
            tobacco_user: Boolean(f.tobacco_user),
            has_pre_existing_conditions: Boolean(f.has_pre_existing_conditions),
            pre_existing_conditions_details: f.pre_existing_details || "",
            existing_life_cover: f.existing_life_cover || 0,
            existing_health_cover: f.existing_health_cover || 0,
            desired_coverage_amount: f.desired_coverage_amount || summary.recommended_sum_assured || 15000000,
          };
          setFormData(loadedData);

          const resObj: NeedsAssessmentResult = {
            qualification_id: summary.qualification_id || "saved-qual",
            customer_id: summary.customer_id || "",
            category: summary.target_category || summary.category || "term_life",
            eligibility_status: summary.eligibility_status || "eligible",
            calculated_coverage_gap: summary.calculated_coverage_gap ?? (f.calculated_gap || 0),
            recommended_sum_assured: summary.recommended_sum_assured || 0,
            health_risk_tier: summary.health_risk_tier || summary.health_tier || "standard",
            key_observations: summary.key_observations && summary.key_observations.length > 0
              ? summary.key_observations
              : [
                  `Protection category: ${(summary.target_category || summary.category || "term_life").replace(/_/g, " ")}`,
                  `Coverage gap calculated at ₹${(summary.calculated_coverage_gap || f.calculated_gap || 0).toLocaleString("en-IN")}`,
                  `Health risk tier: ${(summary.health_risk_tier || summary.health_tier || "standard").replace(/_/g, " ")}`,
                ],
            qualifying_products_count: summary.qualifying_products_count || 1,
            factors: f,
            created_at: summary.created_at || new Date().toISOString(),
          };
          setResult(resObj);

          if (!wantEdit) {
            setStep(5);
          }
        } else {
          // Check draft in localStorage if no backend assessment exists
          const draft = localStorage.getItem("needs_assessment_draft");
          if (draft) {
            try {
              const parsed = JSON.parse(draft);
              setFormData((prev) => ({ ...prev, ...parsed }));
            } catch (e) {}
          }
          if (catParam) {
            setFormData((prev) => ({ ...prev, category: catParam as any }));
          }
        }
      } catch (err) {
        console.warn("Could not load existing assessment summary:", err);
      } finally {
        setInitialLoading(false);
      }
    }

    initPage();
  }, []);

  const updateFormData = (patch: Partial<NeedsAssessmentPayload>) => {
    setFormData((prev) => {
      const next = { ...prev, ...patch };
      try {
        localStorage.setItem("needs_assessment_draft", JSON.stringify(next));
      } catch (e) {}
      return next;
    });
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e && e.preventDefault) e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await CustomerAPI.submitNeedsAssessment(formData);
      setResult(res);
      setHasExistingAssessment(true);
      try {
        localStorage.removeItem("needs_assessment_draft");
      } catch (e) {}
      setStep(5); // Show results screen
    } catch (err: any) {
      setError(err?.message || "Failed to process needs assessment. Please check inputs.");
    } finally {
      setLoading(false);
    }
  };

  if (initialLoading) {
    return (
      <div className="space-y-6 max-w-4xl mx-auto">
        <PageHeader
          title="Insurance Needs Assessment"
          description="Structured questionnaire to accurately determine your coverage requirements and risk tier."
          breadcrumbs={[
            { label: "Customer Portal", href: "/customer" },
            { label: "Needs Assessment" },
          ]}
        />
        <Card className="border-slate-200 bg-white p-12 shadow-2xs">
          <div className="flex flex-col items-center justify-center space-y-3">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
            <p className="text-xs text-slate-500 font-medium">Loading your assessment profile...</p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <PageHeader
        title="Insurance Needs Assessment"
        description="Structured questionnaire to accurately determine your coverage requirements and risk tier."
        breadcrumbs={[
          { label: "Customer Portal", href: "/customer" },
          { label: "Needs Assessment" },
        ]}
      />

      {hasExistingAssessment && step < 5 && (
        <div className="p-3 bg-blue-50/70 border border-blue-200 rounded-lg text-xs text-blue-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-blue-600 shrink-0" />
            <span>You have an existing assessment saved. Modifying answers will recalculate your qualification gap.</span>
          </div>
          <Button
            size="sm"
            variant="ghost"
            className="h-7 text-xs text-blue-700 hover:text-blue-900"
            onClick={() => setStep(5)}
          >
            Cancel & View Saved Results
          </Button>
        </div>
      )}

      {/* Step Indicator */}
      <div className="grid grid-cols-4 gap-2 text-xs font-medium">
        {[
          { num: 1, title: "Category & Demographics" },
          { num: 2, title: "Financial Capacity" },
          { num: 3, title: "Family & Dependents" },
          { num: 4, title: "Health & Lifestyle" },
        ].map((s) => (
          <div
            key={s.num}
            className={`p-3 rounded-lg border flex items-center gap-2 ${
              step === s.num
                ? "border-blue-500 bg-white text-blue-900 shadow-2xs"
                : step > s.num
                ? "border-emerald-200 bg-emerald-50/50 text-emerald-800"
                : "border-slate-100 bg-slate-50/50 text-slate-400"
            }`}
          >
            {step > s.num ? (
              <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
            ) : (
              <span
                className={`h-5 w-5 rounded-full flex items-center justify-center text-[11px] font-bold ${
                  step === s.num ? "bg-blue-600 text-white" : "bg-slate-200 text-slate-600"
                }`}
              >
                {s.num}
              </span>
            )}
            <span className="truncate">{s.title}</span>
          </div>
        ))}
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Wizard Form Cards */}
      {step < 5 && (
        <Card className="border-slate-200 bg-white shadow-2xs">
          <CardHeader className="p-6 pb-4">
            <CardTitle className="text-base font-semibold text-slate-900">
              {step === 1 && "Step 1: Target Coverage & Personal Demographics"}
              {step === 2 && "Step 2: Financial Capacity & Income Protection"}
              {step === 3 && "Step 3: Family Support & Dependency Profile"}
              {step === 4 && "Step 4: Health Declarations & Existing Coverage"}
            </CardTitle>
            <CardDescription className="text-xs text-slate-500">
              All declared information is strictly confidential and protected under DPDP standards.
            </CardDescription>
          </CardHeader>

          <CardContent className="p-6 pt-0 space-y-5">
            {step === 1 && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label className="text-xs font-semibold text-slate-700">Insurance Category</Label>
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { id: "term_life", label: "Term Life Protection", icon: Heart },
                      { id: "health", label: "Comprehensive Health", icon: Activity },
                      { id: "motor", label: "Motor Vehicle Plan", icon: Car },
                    ].map((c) => {
                      const Icon = c.icon;
                      const isSel = formData.category === c.id;
                      return (
                        <button
                          key={c.id}
                          type="button"
                          onClick={() => updateFormData({ category: c.id as any })}
                          className={`p-3.5 rounded-lg border text-left flex flex-col justify-between gap-2 transition-all ${
                            isSel
                              ? "border-blue-600 bg-blue-50/50 text-blue-900 ring-1 ring-blue-500"
                              : "border-slate-200 hover:border-slate-300 bg-white text-slate-700"
                          }`}
                        >
                          <Icon className={`h-5 w-5 ${isSel ? "text-blue-600" : "text-slate-400"}`} />
                          <span className="text-xs font-medium">{c.label}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <Label htmlFor="age" className="text-xs font-semibold text-slate-700">Primary Insured Age (Years)</Label>
                    <Input
                      id="age"
                      type="number"
                      min={18}
                      max={75}
                      value={formData.age}
                      onChange={(e) => updateFormData({ age: parseInt(e.target.value) || 18 })}
                      className="text-xs bg-white"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="marital" className="text-xs font-semibold text-slate-700">Marital Status</Label>
                    <Select
                      value={formData.marital_status}
                      onValueChange={(val) => updateFormData({ marital_status: val })}
                    >
                      <SelectTrigger className="text-xs bg-white">
                        <SelectValue placeholder="Select marital status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="single">Single</SelectItem>
                        <SelectItem value="married">Married</SelectItem>
                        <SelectItem value="divorced">Divorced</SelectItem>
                        <SelectItem value="widowed">Widowed</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="occ" className="text-xs font-semibold text-slate-700">Current Occupation / Profession</Label>
                  <Input
                    id="occ"
                    placeholder="e.g. Software Engineer, Business Owner, Consultant"
                    value={formData.occupation}
                    onChange={(e) => updateFormData({ occupation: e.target.value })}
                    className="text-xs bg-white"
                  />
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <Label htmlFor="income" className="text-xs font-semibold text-slate-700">Gross Annual Income (₹ INR)</Label>
                  <Input
                    id="income"
                    type="number"
                    step="50000"
                    min={100000}
                    value={formData.annual_income}
                    onChange={(e) => updateFormData({ annual_income: parseFloat(e.target.value) || 0 })}
                    className="text-xs bg-white"
                  />
                  <p className="text-[11px] text-slate-500">
                    Used to calculate the standard Human Life Value (HLV) multiplier (typically 10x - 15x annual income).
                  </p>
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="desired" className="text-xs font-semibold text-slate-700">Target Protection Cover Desired (₹ INR)</Label>
                  <Input
                    id="desired"
                    type="number"
                    step="500000"
                    min={1000000}
                    value={formData.desired_coverage_amount}
                    onChange={(e) => updateFormData({ desired_coverage_amount: parseFloat(e.target.value) || 0 })}
                    className="text-xs bg-white"
                  />
                  <p className="text-[11px] text-slate-500">
                    Baseline benchmark: ₹1.00 Crore to ₹2.00 Crore for income replacement.
                  </p>
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <Label htmlFor="deps" className="text-xs font-semibold text-slate-700">Number of Financial Dependents</Label>
                  <Select
                    value={formData.dependents_count.toString()}
                    onValueChange={(val) => updateFormData({ dependents_count: parseInt(val) })}
                  >
                    <SelectTrigger className="text-xs bg-white">
                      <SelectValue placeholder="Select dependents" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0">0 (Self Only)</SelectItem>
                      <SelectItem value="1">1 Dependent (Spouse / Parent)</SelectItem>
                      <SelectItem value="2">2 Dependents (Family of 3)</SelectItem>
                      <SelectItem value="3">3 Dependents (Family of 4)</SelectItem>
                      <SelectItem value="4">4+ Dependents</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}

            {step === 4 && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label className="text-xs font-semibold text-slate-700">Tobacco or Nicotine Consumption</Label>
                  <div className="flex gap-4">
                    <label className="flex items-center gap-2 text-xs text-slate-700 cursor-pointer">
                      <input
                        type="radio"
                        name="tobacco"
                        checked={formData.tobacco_user === false}
                        onChange={() => updateFormData({ tobacco_user: false })}
                      />
                      <span>Non-Tobacco User (Eligible for Preferred Rates)</span>
                    </label>
                    <label className="flex items-center gap-2 text-xs text-slate-700 cursor-pointer">
                      <input
                        type="radio"
                        name="tobacco"
                        checked={formData.tobacco_user === true}
                        onChange={() => updateFormData({ tobacco_user: true })}
                      />
                      <span>Tobacco / Nicotine User</span>
                    </label>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="text-xs font-semibold text-slate-700">Existing Pre-Existing Conditions</Label>
                  <div className="flex gap-4">
                    <label className="flex items-center gap-2 text-xs text-slate-700 cursor-pointer">
                      <input
                        type="radio"
                        name="pre_existing"
                        checked={formData.has_pre_existing_conditions === false}
                        onChange={() => updateFormData({ has_pre_existing_conditions: false, pre_existing_conditions_details: "" })}
                      />
                      <span>No Known Medical Conditions</span>
                    </label>
                    <label className="flex items-center gap-2 text-xs text-slate-700 cursor-pointer">
                      <input
                        type="radio"
                        name="pre_existing"
                        checked={formData.has_pre_existing_conditions === true}
                        onChange={() => updateFormData({ has_pre_existing_conditions: true })}
                      />
                      <span>Declared Pre-Existing Medical History</span>
                    </label>
                  </div>
                </div>

                {formData.has_pre_existing_conditions && (
                  <div className="space-y-1.5 pt-2">
                    <Label htmlFor="cond_details" className="text-xs font-semibold text-slate-700">Condition Details</Label>
                    <Input
                      id="cond_details"
                      placeholder="e.g. Hypertension, Type 2 Diabetes, Asthma"
                      value={formData.pre_existing_conditions_details || ""}
                      onChange={(e) => updateFormData({ pre_existing_conditions_details: e.target.value })}
                      className="text-xs bg-white"
                    />
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                  <div className="space-y-1.5">
                    <Label htmlFor="ex_life" className="text-xs font-semibold text-slate-700">Existing Life Cover (₹ INR)</Label>
                    <Input
                      id="ex_life"
                      type="number"
                      step="100000"
                      min={0}
                      value={formData.existing_life_cover}
                      onChange={(e) => updateFormData({ existing_life_cover: parseFloat(e.target.value) || 0 })}
                      className="text-xs bg-white"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="ex_health" className="text-xs font-semibold text-slate-700">Existing Health Cover (₹ INR)</Label>
                    <Input
                      id="ex_health"
                      type="number"
                      step="50000"
                      min={0}
                      value={formData.existing_health_cover}
                      onChange={(e) => updateFormData({ existing_health_cover: parseFloat(e.target.value) || 0 })}
                      className="text-xs bg-white"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Step Action Buttons */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-100">
              {step > 1 ? (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setStep(step - 1)}
                  className="text-xs"
                >
                  <ArrowLeft className="h-3.5 w-3.5 mr-1" />
                  Previous
                </Button>
              ) : <div />}

              {step < 4 ? (
                <Button
                  type="button"
                  size="sm"
                  onClick={() => setStep(step + 1)}
                  className="text-xs bg-blue-600 hover:bg-blue-700 text-white"
                >
                  Next Step
                  <ArrowRight className="h-3.5 w-3.5 ml-1" />
                </Button>
              ) : (
                <Button
                  type="button"
                  size="sm"
                  onClick={() => handleSubmit()}
                  disabled={loading}
                  className="text-xs bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {loading ? "Evaluating & Saving..." : "Generate & Save Qualification"}
                  <Sparkles className="h-3.5 w-3.5 ml-1" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results View */}
      {step === 5 && result && (
        <Card className="border-emerald-200 bg-white shadow-2xs">
          <CardHeader className="p-6 bg-emerald-50/50 border-b border-emerald-100">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <CheckCircle2 className="h-6 w-6 text-emerald-600 shrink-0" />
                <div>
                  <CardTitle className="text-base font-semibold text-emerald-950">
                    Needs Assessment Completed & Saved
                  </CardTitle>
                  <CardDescription className="text-xs text-emerald-700">
                    Qualification stored securely in your profile with zero black-box metrics.
                  </CardDescription>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 uppercase tracking-wide">
                  Tier: {result.health_risk_tier.replace(/_/g, " ")}
                </span>
              </div>
            </div>
          </CardHeader>

          <CardContent className="p-6 space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-4 rounded-lg border border-slate-200 bg-slate-50/60">
                <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider block">
                  Recommended Protection
                </span>
                <span className="text-xl font-bold text-slate-900 mt-1 block">
                  ₹{Number(result.recommended_sum_assured).toLocaleString("en-IN")}
                </span>
                <span className="text-[11px] text-slate-500">Based on income replacement</span>
              </div>

              <div className="p-4 rounded-lg border border-slate-200 bg-slate-50/60">
                <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider block">
                  Net Protection Gap
                </span>
                <span className="text-xl font-bold text-blue-600 mt-1 block">
                  ₹{Number(result.calculated_coverage_gap).toLocaleString("en-IN")}
                </span>
                <span className="text-[11px] text-slate-500">Uncovered family liability</span>
              </div>

              <div className="p-4 rounded-lg border border-slate-200 bg-slate-50/60">
                <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider block">
                  Qualifying Plans
                </span>
                <span className="text-xl font-bold text-slate-900 mt-1 block">
                  {result.qualifying_products_count} Approved Plans
                </span>
                <span className="text-[11px] text-emerald-600">Meets eligibility rules</span>
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Actuarial Observations:
              </h4>
              <ul className="space-y-1.5 text-xs text-slate-700">
                {(result.key_observations || []).map((obs, idx) => (
                  <li key={idx} className="flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-600 shrink-0" />
                    <span>{obs}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="pt-4 border-t border-slate-100 flex flex-wrap items-center gap-3">
              <Button size="sm" asChild className="bg-blue-600 hover:bg-blue-700 text-white">
                <Link href="/customer/recommendations">
                  View Recommended Plans <ArrowRight className="h-4 w-4 ml-1.5" />
                </Link>
              </Button>
              <Button size="sm" variant="outline" asChild>
                <Link href="/customer/chat">
                  Discuss with AI Advisor
                </Link>
              </Button>
              <Button size="sm" variant="outline" onClick={() => setStep(1)}>
                <Edit3 className="h-3.5 w-3.5 mr-1" />
                Edit Assessment Answers
              </Button>
              <Button size="sm" variant="ghost" asChild>
                <Link href="/customer">
                  Customer Dashboard
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

