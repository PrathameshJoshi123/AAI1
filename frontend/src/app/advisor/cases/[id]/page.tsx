"use client";

import * as React from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  Scale,
  ShieldAlert,
  CheckCircle2,
  Clock,
  ArrowLeft,
  FileText,
  User,
  Heart,
  FolderOpen,
  History,
  MessageSquare,
  AlertTriangle,
  Sparkles,
  Lock,
  Plus,
  Send,
  Download,
  AlertCircle,
  ExternalLink,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { underwritingService } from "@/services/underwriting-service";
import { UnderwritingCaseDetail, UnderwritingReview } from "@/types/underwriting";

export default function CustomerCaseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.id as string;

  const [detail, setDetail] = React.useState<UnderwritingCaseDetail | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  // Review Dialog State
  const [reviewOpen, setReviewOpen] = React.useState(false);
  const [reviewDecision, setReviewDecision] = React.useState<string>("approved_standard");
  const [reviewType, setReviewType] = React.useState<string>("initial_assessment");
  const [loadingPct, setLoadingPct] = React.useState<number>(0);
  const [reviewNotes, setReviewNotes] = React.useState<string>("");
  const [reviewConditions, setReviewConditions] = React.useState<string>("");
  const [submittingReview, setSubmittingReview] = React.useState(false);

  // Note Dialog State
  const [newNoteContent, setNewNoteContent] = React.useState("");
  const [newNoteType, setNewNoteType] = React.useState("internal_note");
  const [newNoteConfidential, setNewNoteConfidential] = React.useState(false);
  const [submittingNote, setSubmittingNote] = React.useState(false);

  // AI Escalation State
  const [runningAi, setRunningAi] = React.useState(false);

  const loadCase = React.useCallback(async () => {
    if (!caseId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await underwritingService.getCaseDetail(caseId);
      setDetail(data);
    } catch (err: any) {
      console.error("Failed to load case detail:", err);
      setError(err?.message || "Failed to load case detail.");
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  React.useEffect(() => {
    loadCase();
  }, [loadCase]);

  const handleSubmitReview = async () => {
    if (!detail) return;
    try {
      setSubmittingReview(true);
      await underwritingService.submitReview(detail.case_number, {
        review_type: reviewType,
        decision: reviewDecision as any,
        loading_percentage: loadingPct,
        notes: reviewNotes,
        conditions: reviewConditions || undefined,
      });
      setReviewOpen(false);
      setReviewNotes("");
      setReviewConditions("");
      await loadCase();
    } catch (err: any) {
      alert(err?.message || "Failed to record review decision.");
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!detail || !newNoteContent.trim()) return;
    try {
      setSubmittingNote(true);
      await underwritingService.addCaseNote(detail.id, {
        note_type: newNoteType,
        content: newNoteContent,
        is_confidential: newNoteConfidential,
      });
      setNewNoteContent("");
      await loadCase();
    } catch (err: any) {
      alert(err?.message || "Failed to add note.");
    } finally {
      setSubmittingNote(false);
    }
  };

  const handleRunAiRisk = async () => {
    if (!detail) return;
    try {
      setRunningAi(true);
      await underwritingService.triggerAiRiskSynthesis(detail.case_number);
      await loadCase();
    } catch (err: any) {
      alert(err?.message || "Failed to run AI risk escalation.");
    } finally {
      setRunningAi(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-24 text-slate-400 text-sm">
        <Clock className="h-6 w-6 animate-spin mb-2 text-blue-600" />
        Loading customer case dossier...
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div className="space-y-4">
        <Button variant="ghost" size="sm" asChild className="text-xs">
          <Link href="/advisor/underwriting">
            <ArrowLeft className="h-4 w-4 mr-1" /> Back to Triage Queue
          </Link>
        </Button>
        <div className="p-8 bg-red-50 border border-red-200 rounded-lg text-red-800 text-sm">
          {error || "Case file not found."}
        </div>
      </div>
    );
  }

  const pData = detail.proposal_data || {};
  const isMedRestricted = detail.medical_risk_summary?.includes("RESTRICTED");

  return (
    <div className="space-y-6">
      {/* Top Navigation */}
      <div className="flex items-center justify-between">
        <Button variant="ghost" size="sm" asChild className="text-xs text-slate-600">
          <Link href="/advisor/underwriting">
            <ArrowLeft className="h-4 w-4 mr-1" /> Back to Triage Queue
          </Link>
        </Button>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRunAiRisk}
            disabled={runningAi}
            className="h-8 text-xs gap-1.5 border-slate-200 bg-white"
          >
            <Sparkles className={`h-3.5 w-3.5 text-blue-600 ${runningAi ? "animate-spin" : ""}`} />
            Run AI Risk Synthesis
          </Button>

          <Dialog open={reviewOpen} onOpenChange={setReviewOpen}>
            <DialogTrigger asChild>
              <Button size="sm" className="h-8 text-xs gap-1.5 bg-blue-600 hover:bg-blue-700 text-white">
                <Scale className="h-3.5 w-3.5" />
                Submit Underwriting Review
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-lg bg-white border-slate-200">
              <DialogHeader>
                <DialogTitle className="text-base font-bold text-slate-900">
                  Record Underwriting Decision
                </DialogTitle>
                <DialogDescription className="text-xs text-slate-500">
                  Record a formal human underwriting decision for Case {detail.case_number}. Decisions are permanently logged in audit trails.
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4 py-2">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Review Decision *
                  </label>
                  <Select value={reviewDecision} onValueChange={setReviewDecision}>
                    <SelectTrigger className="h-9 text-xs bg-white border-slate-200">
                      <SelectValue placeholder="Select decision" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="approved_standard">Approved (Standard Rates)</SelectItem>
                      <SelectItem value="approved_with_loading">Approved (With Actuarial Loading)</SelectItem>
                      <SelectItem value="more_info_needed">More Information Needed</SelectItem>
                      <SelectItem value="declined">Declined</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Review Assessment Stage
                  </label>
                  <Select value={reviewType} onValueChange={setReviewType}>
                    <SelectTrigger className="h-9 text-xs bg-white border-slate-200">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="initial_assessment">Initial Assessment</SelectItem>
                      <SelectItem value="medical_evaluation">Medical Evaluation</SelectItem>
                      <SelectItem value="financial_scrutiny">Financial Scrutiny</SelectItem>
                      <SelectItem value="supervisor_escalation">Supervisor Escalation</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {reviewDecision === "approved_with_loading" && (
                  <div>
                    <label className="text-xs font-semibold text-slate-700 block mb-1">
                      Loading Percentage (%) *
                    </label>
                    <Input
                      type="number"
                      min="0"
                      max="200"
                      step="0.5"
                      value={loadingPct}
                      onChange={(e) => setLoadingPct(parseFloat(e.target.value) || 0)}
                      className="h-9 text-xs bg-white border-slate-200"
                      placeholder="e.g. 15.0"
                    />
                    <p className="text-[11px] text-slate-500 mt-1">
                      Applied additively to the base actuarial mortality/morbidity rate.
                    </p>
                  </div>
                )}

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Underwriter Clinical / Financial Rationale *
                  </label>
                  <Textarea
                    rows={3}
                    value={reviewNotes}
                    onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setReviewNotes(e.target.value)}
                    placeholder="Enter statutory clinical reasoning, verified disclosures, or missing items..."
                    className="text-xs bg-white border-slate-200"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Policy Conditions & Endorsements (Optional)
                  </label>
                  <Input
                    value={reviewConditions}
                    onChange={(e) => setReviewConditions(e.target.value)}
                    placeholder="e.g. Exclusion of pre-existing hypertension for 2 years"
                    className="h-9 text-xs bg-white border-slate-200"
                  />
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" size="sm" onClick={() => setReviewOpen(false)} className="text-xs">
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={handleSubmitReview}
                  disabled={submittingReview || reviewNotes.trim().length < 5}
                  className="text-xs bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {submittingReview ? "Recording..." : "Record Official Decision"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Case Header Dossier Card */}
      <Card className="bg-white border-slate-200">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2.5">
                <h1 className="text-xl font-bold text-slate-900">{detail.customer_name}</h1>
                <Badge
                  variant="outline"
                  className={
                    detail.priority === "urgent"
                      ? "bg-red-50 text-red-700 border-red-200"
                      : detail.priority === "high"
                      ? "bg-amber-50 text-amber-700 border-amber-200"
                      : "bg-blue-50 text-blue-700 border-blue-200"
                  }
                >
                  {detail.priority.toUpperCase()} PRIORITY
                </Badge>
                <Badge
                  variant="outline"
                  className={
                    detail.risk_rating === "preferred"
                      ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                      : detail.risk_rating === "substandard"
                      ? "bg-amber-50 text-amber-700 border-amber-200"
                      : detail.risk_rating === "decline"
                      ? "bg-red-50 text-red-700 border-red-200"
                      : "bg-slate-50 text-slate-700 border-slate-200"
                  }
                >
                  {detail.risk_rating.toUpperCase()} RISK
                </Badge>
                <Badge variant="outline" className="bg-slate-100 text-slate-700 border-slate-300">
                  {detail.status.replace("_", " ").toUpperCase()}
                </Badge>
              </div>

              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
                <span>Case #{detail.case_number}</span>
                <span>•</span>
                <span>Email: {detail.customer_email || "—"}</span>
                <span>•</span>
                <span>Phone: {detail.customer_phone || "—"}</span>
                <span>•</span>
                <span>City: {detail.customer_city || "—"}</span>
                <span>•</span>
                <span>DOB: {detail.customer_dob || "—"}</span>
              </div>
            </div>

            <div className="flex items-center gap-4 border-t md:border-t-0 md:border-l border-slate-100 pt-3 md:pt-0 md:pl-6 shrink-0">
              <div className="text-right">
                <span className="text-[11px] text-slate-400 block">Sum Assured</span>
                <span className="text-base font-bold text-slate-900">₹{detail.sum_assured.toLocaleString("en-IN")}</span>
              </div>
              <div className="text-right">
                <span className="text-[11px] text-slate-400 block">Total Premium</span>
                <span className="text-base font-bold text-blue-600">₹{detail.total_premium.toLocaleString("en-IN")}/yr</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Risk Flags Alert Banner */}
      {detail.risk_flags && detail.risk_flags.length > 0 && (
        <div className="p-4 bg-amber-50/70 border border-amber-200 rounded-lg space-y-2">
          <div className="flex items-center gap-2 text-amber-900 font-semibold text-xs">
            <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0" />
            <span>AI Risk Synthesizer Discrepancies ({detail.risk_flags.length} Flagged Indicators):</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
            {detail.risk_flags.map((flag, idx) => (
              <div key={idx} className="flex items-start gap-2 bg-white/80 p-2 rounded border border-amber-200/60">
                <Badge
                  variant="outline"
                  className={
                    flag.severity === "critical" || flag.severity === "high"
                      ? "bg-red-50 text-red-700 border-red-200 text-[10px]"
                      : "bg-amber-50 text-amber-700 border-amber-200 text-[10px]"
                  }
                >
                  {flag.severity}
                </Badge>
                <div>
                  <p className="font-medium text-slate-800">{flag.flag}</p>
                  <span className="text-[10px] text-slate-400">Source: {flag.source}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 7-Tab Dossier Workspace */}
      <Tabs defaultValue="proposal" className="space-y-4">
        <TabsList className="bg-slate-100 p-1 border border-slate-200 text-xs">
          <TabsTrigger value="proposal" className="gap-1.5 text-xs">
            <FileText className="h-3.5 w-3.5" /> Proposal Snapshot
          </TabsTrigger>
          <TabsTrigger value="declarations" className="gap-1.5 text-xs">
            <Heart className="h-3.5 w-3.5" /> Declarations & Lifestyle
          </TabsTrigger>
          <TabsTrigger value="documents" className="gap-1.5 text-xs">
            <FolderOpen className="h-3.5 w-3.5" /> Document Vault ({detail.documents.length})
          </TabsTrigger>
          <TabsTrigger value="reviews" className="gap-1.5 text-xs">
            <Scale className="h-3.5 w-3.5" /> Underwriting Reviews ({detail.reviews.length})
          </TabsTrigger>
          <TabsTrigger value="notes" className="gap-1.5 text-xs">
            <MessageSquare className="h-3.5 w-3.5" /> Internal Notes ({detail.notes.length})
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: Proposal Snapshot */}
        <TabsContent value="proposal" className="space-y-4">
          <Card className="bg-white border-slate-200">
            <CardHeader className="p-4 border-b border-slate-100">
              <CardTitle className="text-sm font-semibold">Structured Proposal Intake</CardTitle>
              <CardDescription className="text-xs">
                Verified customer demographics, employment, and income disclosures.
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs">
                <div className="space-y-2">
                  <h4 className="font-semibold text-slate-900 border-b pb-1">Product Details</h4>
                  <div className="space-y-1 text-slate-600">
                    <p><span className="text-slate-400">Plan:</span> {detail.product_name}</p>
                    <p><span className="text-slate-400">Category:</span> {detail.product_category}</p>
                    <p><span className="text-slate-400">Policy Term:</span> {detail.policy_term_years} Years</p>
                    <p><span className="text-slate-400">Coverage:</span> ₹{detail.sum_assured.toLocaleString("en-IN")}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-semibold text-slate-900 border-b pb-1">Applicant Profile</h4>
                  <div className="space-y-1 text-slate-600">
                    <p><span className="text-slate-400">Occupation:</span> {pData.occupation || "Salaried Professional"}</p>
                    <p><span className="text-slate-400">Annual Income:</span> ₹{(pData.annual_income || 0).toLocaleString("en-IN")}</p>
                    <p><span className="text-slate-400">Marital Status:</span> {pData.marital_status || "Single"}</p>
                    <p><span className="text-slate-400">City / State:</span> {detail.customer_city || "—"}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-semibold text-slate-900 border-b pb-1">Integrity Checksum</h4>
                  <div className="space-y-1 text-slate-600">
                    <p><span className="text-slate-400">Status:</span> Immutable Submission</p>
                    <p className="truncate"><span className="text-slate-400">SHA-256:</span> {detail.proposal_checksum || "Verified On Ingest"}</p>
                    <p><span className="text-slate-400">Submitted:</span> {new Date(detail.created_at).toLocaleString()}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 2: Declarations & Lifestyle */}
        <TabsContent value="declarations" className="space-y-4">
          <Card className="bg-white border-slate-200">
            <CardHeader className="p-4 border-b border-slate-100">
              <CardTitle className="text-sm font-semibold flex items-center justify-between">
                <span>Medical & Lifestyle Risk Assessment</span>
                {isMedRestricted && (
                  <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200 text-xs">
                    <Lock className="h-3 w-3 mr-1" />
                    SPDI Redacted
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-4 text-xs">
              {isMedRestricted ? (
                <div className="p-6 bg-slate-50 border border-slate-200 rounded-lg text-center text-slate-500">
                  <Lock className="h-8 w-8 text-slate-400 mx-auto mb-2" />
                  <p className="font-semibold text-slate-800">Medical SPDI Data Restricted</p>
                  <p className="text-xs text-slate-500 max-w-md mx-auto mt-1">
                    Under the Digital Personal Data Protection (DPDP) Act and IRDAI regulations, detailed clinical records are restricted to authorized Underwriters holding the `medical_data:view` permission.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 space-y-2">
                    <h4 className="font-semibold text-slate-900">Clinical Evaluation Summary</h4>
                    <p className="text-slate-700 leading-relaxed">
                      {detail.medical_risk_summary || "No adverse clinical history declared on proposal."}
                    </p>
                  </div>
                  <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 space-y-2">
                    <h4 className="font-semibold text-slate-900">Financial Multiple Assessment</h4>
                    <p className="text-slate-700 leading-relaxed">
                      {detail.financial_risk_summary || "Financial disclosures conform to underwriting multipliers."}
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 3: Document Vault */}
        <TabsContent value="documents" className="space-y-4">
          <Card className="bg-white border-slate-200">
            <CardHeader className="p-4 border-b border-slate-100 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-sm font-semibold">Attached Compliance Documents</CardTitle>
                <CardDescription className="text-xs">
                  Inspect KYC, identity proof, and salary slip attachments.
                </CardDescription>
              </div>
              <Button size="sm" variant="outline" asChild className="text-xs h-8">
                <Link href="/advisor/documents">Go to Document Station</Link>
              </Button>
            </CardHeader>
            <CardContent className="p-4">
              {detail.documents.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-400">
                  No documents uploaded for this case yet.
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {detail.documents.map((doc) => (
                    <div key={doc.id} className="py-3 flex items-center justify-between text-xs">
                      <div>
                        <span className="font-semibold text-slate-900 block">{doc.file_name}</span>
                        <div className="flex items-center gap-2 text-[11px] text-slate-400 mt-0.5">
                          <span>{doc.document_type.replace("_", " ").toUpperCase()}</span>
                          <span>•</span>
                          <span>{(doc.file_size_bytes / 1024).toFixed(1)} KB</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge
                          variant="outline"
                          className={
                            doc.verification_status === "verified"
                              ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                              : doc.verification_status === "rejected"
                              ? "bg-red-50 text-red-700 border-red-200"
                              : "bg-amber-50 text-amber-700 border-amber-200"
                          }
                        >
                          {doc.verification_status.toUpperCase()}
                        </Badge>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-8 text-xs text-blue-600 hover:text-blue-700"
                          onClick={() => window.open(`/api/v1/documents/${doc.id}/download`, "_blank")}
                        >
                          <Download className="h-3.5 w-3.5 mr-1" /> View
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 4: Underwriting Reviews */}
        <TabsContent value="reviews" className="space-y-4">
          <Card className="bg-white border-slate-200">
            <CardHeader className="p-4 border-b border-slate-100">
              <CardTitle className="text-sm font-semibold">Underwriting Review Log</CardTitle>
              <CardDescription className="text-xs">
                Decisions recorded by authorized underwriters under Section 45 compliance.
              </CardDescription>
            </CardHeader>
            <CardContent className="p-4">
              {detail.reviews.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-400">
                  No review decisions recorded yet. Case is pending evaluation.
                </div>
              ) : (
                <div className="space-y-3">
                  {detail.reviews.map((r) => (
                    <div key={r.id} className="p-4 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Badge
                            variant="outline"
                            className={
                              r.decision.includes("approved")
                                ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                                : r.decision === "declined"
                                ? "bg-red-50 text-red-700 border-red-200"
                                : "bg-amber-50 text-amber-700 border-amber-200"
                            }
                          >
                            {r.decision.replace("_", " ").toUpperCase()}
                          </Badge>
                          <span className="font-semibold text-slate-800">
                            Stage: {r.review_type.replace("_", " ")}
                          </span>
                        </div>
                        <span className="text-[11px] text-slate-400">
                          {new Date(r.reviewed_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-slate-700">{r.notes}</p>
                      {r.loading_percentage > 0 && (
                        <p className="text-amber-800 font-semibold">
                          Applied Loading: +{r.loading_percentage}%
                        </p>
                      )}
                      {r.conditions && (
                        <p className="text-slate-500 italic">Conditions: {r.conditions}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 5: Internal Collaboration Notes */}
        <TabsContent value="notes" className="space-y-4">
          <Card className="bg-white border-slate-200">
            <CardHeader className="p-4 border-b border-slate-100">
              <CardTitle className="text-sm font-semibold">Advisor & Underwriter Discussion</CardTitle>
              <CardDescription className="text-xs">
                Internal collaborative notes and inquiries regarding customer disclosures.
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              <form onSubmit={handleAddNote} className="space-y-3">
                <Textarea
                  rows={2}
                  value={newNoteContent}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setNewNoteContent(e.target.value)}
                  placeholder="Post an internal note or query for the underwriter..."
                  className="text-xs bg-white border-slate-200"
                />
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 text-xs text-slate-600">
                    <label className="flex items-center gap-1.5 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={newNoteConfidential}
                        onChange={(e) => setNewNoteConfidential(e.target.checked)}
                        className="rounded border-slate-300"
                      />
                      <span>Confidential (Underwriters & Admins only)</span>
                    </label>
                  </div>
                  <Button
                    type="submit"
                    size="sm"
                    disabled={submittingNote || !newNoteContent.trim()}
                    className="text-xs gap-1.5 bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    <Send className="h-3 w-3" /> Post Note
                  </Button>
                </div>
              </form>

              <div className="divide-y divide-slate-100 pt-4">
                {detail.notes.length === 0 ? (
                  <p className="text-xs text-slate-400 text-center py-4">No internal notes posted yet.</p>
                ) : (
                  detail.notes.map((n) => (
                    <div key={n.id} className="py-3 space-y-1 text-xs">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-slate-900">{n.author_name}</span>
                          <Badge variant="outline" className="text-[10px] py-0 px-1 bg-slate-50 border-slate-200">
                            {n.author_role}
                          </Badge>
                          {n.is_confidential && (
                            <Badge variant="outline" className="text-[10px] py-0 px-1 bg-red-50 text-red-700 border-red-200">
                              Confidential
                            </Badge>
                          )}
                        </div>
                        <span className="text-[10px] text-slate-400">
                          {new Date(n.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-slate-700">{n.content}</p>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
