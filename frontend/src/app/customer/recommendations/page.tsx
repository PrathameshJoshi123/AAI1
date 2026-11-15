"use client";

import * as React from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Heart,
  Activity,
  Car,
  RefreshCw,
  Info,
  Calendar,
  Layers,
  LogIn,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { RecommendationAPI } from "@/services/recommendation-api";
import { MarkdownRenderer } from "@/components/shared/markdown-renderer";
import { RecommendationItem, RecommendationEvaluateResponse, RecommendationExplanation } from "@/types/recommendation";

function RecommendationsContent() {
  const searchParams = useSearchParams();
  const amountParam = searchParams.get("amount");
  const queryAmount = amountParam ? parseFloat(amountParam) : null;

  const [data, setData] = React.useState<RecommendationEvaluateResponse | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [refreshing, setRefreshing] = React.useState<boolean>(false);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);
  const [selectedExplanation, setSelectedExplanation] = React.useState<RecommendationExplanation | null>(null);
  const [explainingProduct, setExplainingProduct] = React.useState<string | null>(null);
  const [isExplainModalOpen, setIsExplainModalOpen] = React.useState<boolean>(false);

  const fetchRecommendations = React.useCallback(async (force = false) => {
    try {
      if (force) setRefreshing(true);
      setErrorMsg(null);
      const res = force || queryAmount
        ? await RecommendationAPI.evaluateRecommendations(undefined, queryAmount || undefined)
        : await RecommendationAPI.getRecommendations(undefined, queryAmount || undefined);
      setData(res);
    } catch (err: any) {
      console.error("Failed to load recommendations:", err);
      setErrorMsg(err?.message || "Failed to load policy recommendations.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [queryAmount]);

  React.useEffect(() => {
    fetchRecommendations(false);
  }, [fetchRecommendations]);

  const handleExplainAI = async (rec: RecommendationItem) => {
    try {
      setExplainingProduct(rec.product_name || "Policy");
      setIsExplainModalOpen(true);
      setSelectedExplanation(null);
      const explanation = await RecommendationAPI.explainRecommendation(rec.id);
      setSelectedExplanation(explanation);
    } catch (err) {
      console.error("Failed to get AI explanation:", err);
    }
  };

  const recList = data?.recommendations || [];
  const primaryRec = data?.primary_recommendation || recList[0];
  const targetCategory = data?.target_category || "term_life";
  const recommendedCover = queryAmount || data?.recommended_sum_assured || 10000000;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <PageHeader
        title="Personalized Policy Recommendations"
        description="Objectively matched through deterministic actuarial scoring with explainable AI insights."
        breadcrumbs={[
          { label: "Customer Portal", href: "/customer" },
          { label: "Recommendations" },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => fetchRecommendations(true)}
              disabled={refreshing || loading}
              className="text-xs border-slate-200 bg-white hover:bg-slate-50"
            >
              <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${refreshing ? "animate-spin" : ""}`} />
              Re-evaluate Fit
            </Button>
            <Button size="sm" asChild className="bg-blue-600 hover:bg-blue-700 text-white text-xs">
              <Link href={queryAmount ? `/customer/chat?topic=hlv&amount=${queryAmount}` : "/customer/chat"}>
                <Sparkles className="h-3.5 w-3.5 mr-1.5" />
                Ask Advisor
              </Link>
            </Button>
          </div>
        }
      />

      {/* Qualification Context Summary Banner */}
      <Card className="border-blue-100 bg-blue-50/40 shadow-none">
        <CardContent className="p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2.5">
            <ShieldCheck className="h-5 w-5 text-blue-600 shrink-0" />
            <div>
              <span className="font-semibold text-slate-900">Assessed Protection Need:</span>{" "}
              <span className="font-bold text-blue-700">₹{recommendedCover.toLocaleString("en-IN")}</span>
              <span className="text-slate-500 ml-2">({targetCategory.replace(/_/g, " ").toUpperCase()})</span>
            </div>
          </div>
          <Button size="sm" variant="outline" asChild className="text-xs h-7 bg-white border-blue-200 hover:bg-blue-50">
            <Link href="/customer/needs-assessment">Update Needs Profile</Link>
          </Button>
        </CardContent>
      </Card>

      {/* Auth / Error Alert if failed */}
      {errorMsg && (
        <Alert variant="destructive" className="bg-amber-50 border-amber-200 text-amber-900">
          <AlertCircle className="h-4 w-4 text-amber-600" />
          <AlertTitle className="text-xs font-semibold text-amber-800">Recommendation Service Notice</AlertTitle>
          <AlertDescription className="text-xs text-amber-700 flex flex-col sm:flex-row sm:items-center justify-between gap-2 mt-1">
            <span>{errorMsg}</span>
            <div className="flex items-center gap-2 shrink-0">
              <Button size="sm" variant="outline" asChild className="text-[11px] h-7 bg-white border-amber-300">
                <Link href="/login">
                  <LogIn className="h-3 w-3 mr-1" /> Sign In to Customer Account
                </Link>
              </Button>
              <Button size="sm" onClick={() => fetchRecommendations(true)} className="text-[11px] h-7 bg-amber-600 hover:bg-amber-700 text-white">
                Retry
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Loading Skeleton */}
      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2].map((i) => (
            <Card key={i} className="animate-pulse p-6 bg-white border-slate-200">
              <div className="h-4 bg-slate-100 rounded w-1/4 mb-4" />
              <div className="h-6 bg-slate-100 rounded w-3/4 mb-2" />
              <div className="h-16 bg-slate-50 rounded mb-4" />
              <div className="h-10 bg-slate-100 rounded" />
            </Card>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && recList.length === 0 && !errorMsg && (
        <Card className="p-8 text-center bg-white border-slate-200">
          <Sparkles className="h-8 w-8 text-blue-500 mx-auto mb-2" />
          <h4 className="text-sm font-semibold text-slate-900">Matching Plans for Your Profile</h4>
          <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
            Click below to calculate and view personalized policy recommendations matching your declared coverage gap of ₹{recommendedCover.toLocaleString("en-IN")}.
          </p>
          <div className="flex justify-center gap-3 mt-4">
            <Button
              size="sm"
              onClick={() => fetchRecommendations(true)}
              disabled={refreshing}
              className="bg-blue-600 hover:bg-blue-700 text-white text-xs"
            >
              <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${refreshing ? "animate-spin" : ""}`} />
              {refreshing ? "Calculating Matches..." : "Evaluate Recommendations"}
            </Button>
            <Button size="sm" variant="outline" asChild className="text-xs">
              <Link href="/customer/needs-assessment">Review Needs Profile</Link>
            </Button>
          </div>
        </Card>
      )}

      {/* Recommendation Match Cards */}
      {!loading && recList.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {recList.map((rec, idx) => {
            const isLife = rec.product_category === "term_life";
            const isHealth = rec.product_category === "health";
            const Icon = isLife ? Heart : isHealth ? Activity : Car;
            const isTopMatch = idx === 0;

            return (
              <Card
                key={rec.id}
                className={`flex flex-col justify-between border bg-white shadow-xs transition-all ${
                  isTopMatch ? "border-blue-300 ring-1 ring-blue-100" : "border-slate-200 hover:border-slate-300"
                }`}
              >
                <CardHeader className="space-y-2 p-5 pb-3">
                  <div className="flex items-center justify-between">
                    <Badge variant={isTopMatch ? "default" : "secondary"} className="text-[11px] capitalize font-medium">
                      {rec.product_category?.replace(/_/g, " ") || "Policy"}
                    </Badge>
                    <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full">
                      {rec.match_score}% Fit Score
                    </span>
                  </div>

                  <CardTitle className="text-base font-semibold text-slate-900 flex items-center justify-between">
                    <span>{rec.product_name}</span>
                  </CardTitle>

                  <CardDescription className="text-xs text-slate-500 leading-relaxed">
                    Underwritten by {rec.insurer_name || "Star Union Life & General"} · IRDAI Solvency {rec.insurer_solvency_ratio || "2.15"}x
                  </CardDescription>
                </CardHeader>

                <CardContent className="p-5 pt-0 space-y-4 text-xs">
                  {/* Coverage Specs */}
                  <div className="grid grid-cols-2 gap-2 p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Recommended Cover</span>
                      <span className="font-bold text-slate-900 text-sm">
                        ₹{Number(rec.recommended_sum_assured).toLocaleString("en-IN")}
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Recommended Tenure</span>
                      <span className="font-bold text-slate-900 text-sm">{rec.recommended_term_years} Years</span>
                    </div>
                  </div>

                  {/* Objective Rationale */}
                  <div className="space-y-1.5">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-600 block">
                      Why this policy fits:
                    </span>
                    <div className="text-slate-700 leading-relaxed bg-blue-50/30 p-2.5 rounded border border-blue-50">
                      <MarkdownRenderer content={rec.rationale} />
                    </div>
                  </div>

                  {/* Factor Accordion */}
                  <Accordion type="single" collapsible className="w-full">
                    <AccordionItem value="factors" className="border-b-0">
                      <AccordionTrigger className="text-[11px] py-1 text-slate-600 hover:text-blue-600">
                        View Underwriting Factors & Assumptions
                      </AccordionTrigger>
                      <AccordionContent className="pt-2 text-[11px] text-slate-600 space-y-2">
                        {rec.assumptions_json && rec.assumptions_json.length > 0 && (
                          <div className="space-y-1">
                            <span className="font-medium text-slate-700">Applied Assumptions:</span>
                            <ul className="list-disc pl-4 space-y-0.5 text-slate-600">
                              {rec.assumptions_json.map((a, i) => (
                                <li key={i}>{a}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {rec.limitations_json && rec.limitations_json.length > 0 && (
                          <div className="space-y-1">
                            <span className="font-medium text-amber-700">Mandatory Limitations:</span>
                            <ul className="list-disc pl-4 space-y-0.5 text-slate-600">
                              {rec.limitations_json.map((l, i) => (
                                <li key={i}>{l}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>
                </CardContent>

                <CardFooter className="p-5 pt-2 border-t border-slate-100 flex flex-col sm:flex-row gap-2">
                  <Button size="sm" asChild className="w-full sm:flex-1 text-xs bg-blue-600 hover:bg-blue-700 text-white">
                    <Link
                      href={`/customer/quotes?product_id=${rec.recommended_product_id}&sum_assured=${rec.recommended_sum_assured}&term=${rec.recommended_term_years}`}
                    >
                      Generate Indicative Quote <ArrowRight className="h-3.5 w-3.5 ml-1" />
                    </Link>
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleExplainAI(rec)}
                    className="w-full sm:w-auto text-xs border-slate-200 hover:bg-slate-50"
                  >
                    <Sparkles className="h-3.5 w-3.5 mr-1 text-blue-600" />
                    Explain Fit
                  </Button>
                </CardFooter>
              </Card>
            );
          })}
        </div>
      )}

      {/* Statutory Regulatory Notice */}
      <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-slate-500 text-[11px] flex items-start gap-2">
        <Info className="h-4 w-4 text-slate-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-slate-700">IRDAI Regulatory Advisory:</span> Policy recommendations are generated
          algorithmically based on your declared financial and demographic parameters. Final premium rates, policy issuance, and
          benefit structures remain subject to formal proposal submission, medical underwriting, and insurer acceptance.
        </div>
      </div>

      {/* Explainable AI Modal */}
      <Dialog open={isExplainModalOpen} onOpenChange={setIsExplainModalOpen}>
        <DialogContent className="max-w-lg bg-white border-slate-200">
          <DialogHeader>
            <DialogTitle className="text-base font-semibold text-slate-900 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-blue-600" />
              Advisory Explanation for {explainingProduct}
            </DialogTitle>
            <DialogDescription className="text-xs text-slate-500">
              Grounded analysis generated by the Recommendation Specialist Agent (Mistral AI).
            </DialogDescription>
          </DialogHeader>

          {!selectedExplanation ? (
            <div className="p-8 text-center space-y-3">
              <RefreshCw className="h-6 w-6 text-blue-600 animate-spin mx-auto" />
              <p className="text-xs text-slate-500">Analyzing policy terms, match score, and underwriting factors...</p>
            </div>
          ) : (
            <div className="space-y-4 text-xs">
              <div className="p-3 bg-blue-50/60 rounded-lg border border-blue-100">
                <span className="font-semibold text-blue-900 block mb-1">{selectedExplanation.headline}</span>
                <div className="text-blue-800 leading-relaxed">
                  <MarkdownRenderer content={selectedExplanation.advisor_advice} />
                </div>
              </div>

              <div>
                <span className="font-semibold text-slate-900 block mb-1.5">Why this fits your profile:</span>
                <ul className="space-y-1.5 text-slate-700">
                  {selectedExplanation.why_it_fits.map((fit, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" />
                      <span>{fit}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <span className="font-semibold text-slate-900 block mb-1.5">Critical exclusions to keep in mind:</span>
                <ul className="space-y-1.5 text-slate-600">
                  {selectedExplanation.critical_exclusions_to_note.map((ex, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <AlertCircle className="h-3.5 w-3.5 text-amber-600 shrink-0 mt-0.5" />
                      <span>{ex}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="pt-2 border-t border-slate-100 flex justify-end">
                <Button size="sm" onClick={() => setIsExplainModalOpen(false)} className="text-xs bg-slate-900 hover:bg-slate-800 text-white">
                  Close Review
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default function RecommendationsPage() {
  return (
    <React.Suspense fallback={<div className="p-8 text-center text-xs text-slate-500">Loading recommendations...</div>}>
      <RecommendationsContent />
    </React.Suspense>
  );
}
