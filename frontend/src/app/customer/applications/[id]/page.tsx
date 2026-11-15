"use client";

import React from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ApplicationAPI } from "@/services/application.service";
import { DocumentAPI } from "@/services/document.service";
import { ApplicationDetail } from "@/types/application";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ApplicationTimeline } from "@/components/customer/applications/application-timeline";
import {
  FileText,
  Download,
  CheckCircle2,
  Clock,
  AlertCircle,
  ShieldCheck,
  User,
  Heart,
  Scale,
  Loader2,
  ArrowLeft,
} from "lucide-react";

export default function ApplicationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const appId = params.id as string;

  const [loading, setLoading] = React.useState<boolean>(true);
  const [app, setApp] = React.useState<ApplicationDetail | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    async function load() {
      if (!appId) return;
      try {
        setLoading(true);
        const data = await ApplicationAPI.getApplication(appId);
        setApp(data);
      } catch (err: any) {
        setError(err.message || "Failed to load application details.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [appId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-3">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        <p className="text-xs text-slate-500">Loading proposal details...</p>
      </div>
    );
  }

  if (error || !app) {
    return (
      <div className="max-w-xl mx-auto py-12">
        <Card className="border-rose-200 bg-white p-6 text-center space-y-4">
          <AlertCircle className="w-10 h-10 text-rose-600 mx-auto" />
          <h2 className="text-base font-bold text-slate-900">Application Not Found</h2>
          <p className="text-xs text-slate-600">{error || "Unable to locate the specified application."}</p>
          <Button size="sm" asChild className="bg-blue-600 hover:bg-blue-700 text-white text-xs">
            <Link href="/customer/applications">Back to Applications</Link>
          </Button>
        </Card>
      </div>
    );
  }

  const proposal = app.proposal_data_json || {};
  const personal = proposal.personal_info || {};
  const contact = proposal.contact_address || {};
  const employment = proposal.employment_financial || {};
  const medical = proposal.medical_lifestyle || {};
  const nominees = proposal.nominee_details?.nominees || [];
  const esign = proposal.e_signature || {};

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <PageHeader
          title={`Application #${app.application_number}`}
          description={`Insurance proposal under review with ${app.insurer_name || "Star Union Life & General"}`}
          breadcrumbs={[
            { label: "Customer Portal", href: "/customer" },
            { label: "Applications", href: "/customer/applications" },
            { label: app.application_number },
          ]}
        />
        <Button variant="outline" size="sm" asChild className="text-xs self-start sm:self-auto">
          <Link href="/customer/applications">
            <ArrowLeft className="w-3.5 h-3.5 mr-1" /> All Applications
          </Link>
        </Button>
      </div>

      {/* Real-time progression milestones */}
      <ApplicationTimeline status={app.status} submittedAt={app.submitted_at} />

      {/* Plan summary */}
      <Card className="border-slate-200 bg-white shadow-2xs">
        <CardHeader className="p-4 pb-2 border-b border-slate-100 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-sm font-semibold text-slate-900">
              {app.product_name || "Term Life Protection Plan"}
            </CardTitle>
            <p className="text-xs text-slate-500">Quote #{app.quote_number || "QTE-2026-ACTIVE"}</p>
          </div>
          <Badge variant="outline" className="text-xs bg-blue-50 text-blue-700 border-blue-200 capitalize">
            {app.status.replace("_", " ")}
          </Badge>
        </CardHeader>
        <CardContent className="p-4 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div>
            <span className="text-slate-500 block">Sum Assured</span>
            <span className="font-mono font-bold text-slate-900 text-sm">
              ₹{(app.sum_assured || 10000000).toLocaleString("en-IN")}
            </span>
          </div>
          <div>
            <span className="text-slate-500 block">Policy Term</span>
            <span className="font-medium text-slate-800">{app.policy_term_years || 30} Years</span>
          </div>
          <div>
            <span className="text-slate-500 block">Annual Premium</span>
            <span className="font-mono font-bold text-blue-700 text-sm">
              ₹{(app.total_premium || 14850).toLocaleString("en-IN")}
            </span>
          </div>
          <div>
            <span className="text-slate-500 block">Proposal Checksum</span>
            <span className="font-mono text-slate-600 text-[11px] block truncate">
              {app.proposal_checksum ? `${app.proposal_checksum.substring(0, 16)}...` : "Pending Signature"}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Submitted Proposal Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Personal & Contact */}
        <Card className="border-slate-200 bg-white shadow-2xs">
          <CardHeader className="p-4 pb-2 border-b border-slate-100">
            <CardTitle className="text-xs font-semibold text-slate-900 flex items-center gap-1.5">
              <User className="w-4 h-4 text-blue-600" />
              Identity & Contact Declarations
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">Full Name:</span>
              <span className="font-medium text-slate-800">{personal.full_name || "—"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Date of Birth:</span>
              <span className="text-slate-800">{personal.date_of_birth || "—"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">PAN Number:</span>
              <span className="font-mono text-slate-800 font-semibold">{personal.pan_number || "—"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Mobile & Email:</span>
              <span className="text-slate-800">
                {contact.mobile_number} • {contact.email}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">City / State:</span>
              <span className="text-slate-800">
                {contact.city}, {contact.state} - {contact.pincode}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Occupation & Financial */}
        <Card className="border-slate-200 bg-white shadow-2xs">
          <CardHeader className="p-4 pb-2 border-b border-slate-100">
            <CardTitle className="text-xs font-semibold text-slate-900 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-blue-600" />
              Occupational & Financial Profile
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">Employer Name:</span>
              <span className="font-medium text-slate-800">{employment.employer_or_business_name || "—"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Designation:</span>
              <span className="text-slate-800">{employment.designation || "—"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Occupation Category:</span>
              <span className="text-slate-800 capitalize">{employment.occupation_type?.replace("_", " ") || "—"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Declared Annual Income:</span>
              <span className="font-mono font-semibold text-slate-900">
                ₹{Number(employment.gross_annual_income || 0).toLocaleString("en-IN")}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Tax Resident of India Only:</span>
              <span className="text-slate-800">{employment.tax_resident_india_only ? "Yes" : "No"}</span>
            </div>
          </CardContent>
        </Card>

        {/* Health Declarations */}
        <Card className="border-slate-200 bg-white shadow-2xs">
          <CardHeader className="p-4 pb-2 border-b border-slate-100">
            <CardTitle className="text-xs font-semibold text-slate-900 flex items-center gap-1.5">
              <Heart className="w-4 h-4 text-blue-600" />
              Medical & Lifestyle Profile
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">Height / Weight:</span>
              <span className="text-slate-800">
                {medical.height_cm} cm / {medical.weight_kg} kg
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Tobacco / Nicotine Usage:</span>
              <span className={medical.tobacco_use ? "text-amber-700 font-semibold" : "text-emerald-700"}>
                {medical.tobacco_use ? "Yes (Tobacco User)" : "No (Non-Smoker)"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Alcohol Consumption:</span>
              <span className="text-slate-800 capitalize">{medical.alcohol_consumption || "None"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Hospitalized in Past 5 Years:</span>
              <span className="text-slate-800">
                {medical.hospitalization_past_5_years ? `Yes (${medical.hospitalization_details})` : "No"}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Nominee Designations */}
        <Card className="border-slate-200 bg-white shadow-2xs">
          <CardHeader className="p-4 pb-2 border-b border-slate-100">
            <CardTitle className="text-xs font-semibold text-slate-900 flex items-center gap-1.5">
              <Scale className="w-4 h-4 text-blue-600" />
              Nominee Allocations (Section 39)
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-2 text-xs">
            {nominees.map((nom: any, idx: number) => (
              <div key={idx} className="flex justify-between pb-1 border-b border-slate-50 last:border-none">
                <div>
                  <span className="font-semibold text-slate-900 block">{nom.nominee_name}</span>
                  <span className="text-[11px] text-slate-500 capitalize">{nom.relation}</span>
                </div>
                <div className="text-right">
                  <span className="font-mono font-bold text-blue-700">{nom.share_percentage}%</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Uploaded Documents List */}
      <Card className="border-slate-200 bg-white shadow-2xs">
        <CardHeader className="p-4 pb-2 border-b border-slate-100">
          <CardTitle className="text-xs font-semibold text-slate-900 flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-blue-600" />
            Uploaded KYC & Supporting Documents
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4">
          {app.documents.length === 0 ? (
            <p className="text-xs text-slate-500">No documents attached.</p>
          ) : (
            <div className="space-y-2">
              {app.documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-2.5 border border-slate-200 rounded-md bg-slate-50/50 text-xs"
                >
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-blue-600 shrink-0" />
                    <div>
                      <span className="font-semibold text-slate-900 capitalize block">
                        {doc.document_type.replace("_", " ")}
                      </span>
                      <span className="text-[11px] text-slate-500">
                        {doc.file_name} • {(doc.file_size_bytes / 1024).toFixed(0)} KB
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge
                      variant="outline"
                      className={`text-[10px] ${
                        doc.verification_status === "verified"
                          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                          : doc.verification_status === "rejected"
                          ? "bg-rose-50 text-rose-700 border-rose-200"
                          : "bg-blue-50 text-blue-700 border-blue-200"
                      }`}
                    >
                      {doc.verification_status.toUpperCase()}
                    </Badge>
                    <Button variant="ghost" size="sm" asChild className="h-7 text-xs">
                      <a href={DocumentAPI.getDownloadUrl(doc.id)} target="_blank" rel="noopener noreferrer">
                        <Download className="w-3 h-3 mr-1" /> View
                      </a>
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

