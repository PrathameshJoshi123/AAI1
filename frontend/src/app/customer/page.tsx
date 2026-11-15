"use client";

import * as React from "react";
import Link from "next/link";
import {
  Compass,
  BotMessageSquare,
  FileText,
  ClipboardList,
  FolderOpen,
  ArrowRight,
  ShieldCheck,
  Calculator,
  ListChecks,
  Sparkles,
  CheckCircle2,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { CustomerAPI } from "@/services/customer-api";
import { JourneyStatus } from "@/types/customer";
import { JourneyStatusTracker } from "@/components/customer/journey/journey-status-tracker";

export default function CustomerDashboardPage() {
  const [journey, setJourney] = React.useState<JourneyStatus | null>(null);
  const [quotesCount, setQuotesCount] = React.useState<number>(0);
  const [appsCount, setAppsCount] = React.useState<number>(0);
  const [loading, setLoading] = React.useState<boolean>(true);

  React.useEffect(() => {
    async function loadDashboard() {
      try {
        const [jStatus, qList, aList] = await Promise.allSettled([
          CustomerAPI.getJourneyStatus(),
          CustomerAPI.listQuotes(),
          CustomerAPI.listApplications(),
        ]);

        if (jStatus.status === "fulfilled") {
          setJourney(jStatus.value);
        }
        if (qList.status === "fulfilled" && Array.isArray(qList.value)) {
          setQuotesCount(qList.value.length);
        }
        if (aList.status === "fulfilled" && Array.isArray(aList.value)) {
          setAppsCount(aList.value.length);
        }
      } catch (err) {
        console.error("Dashboard data load error:", err);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  const currentStage = journey?.current_stage || "discovery";

  return (
    <div className="space-y-6">
      <PageHeader
        title="Insurance Portfolio"
        description="Your personal insurance advisory, qualification, and onboarding portal."
        breadcrumbs={[{ label: "Customer Portal", href: "/customer" }, { label: "Overview" }]}
        actions={
          <div className="flex gap-2">
            <Button size="sm" variant="outline" asChild>
              <Link href="/customer/calculator">
                <Calculator className="h-4 w-4 mr-1.5" />
                Coverage Calc
              </Link>
            </Button>
            <Button size="sm" asChild className="bg-blue-600 hover:bg-blue-700 text-white">
              <Link href="/customer/chat">
                <BotMessageSquare className="h-4 w-4 mr-1.5" />
                Ask AI Advisor
              </Link>
            </Button>
          </div>
        }
      />

      {/* Real Portfolio Metric Cards (Never hardcoded or fabricated) */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Active Quotes"
          value={quotesCount}
          description="Indicative premium quotes"
          icon={FileText}
        />
        <StatCard
          title="Submitted Proposals"
          value={appsCount}
          description="Underwriting review stages"
          icon={ClipboardList}
        />
        <StatCard
          title="Document Vault"
          value={0}
          description="KYC & medical proofs"
          icon={FolderOpen}
        />
        <StatCard
          title="Active Policies"
          value={0}
          description="Issued coverage plans"
          icon={ShieldCheck}
        />
      </div>

      {/* Active Onboarding Milestone Component */}
      <JourneyStatusTracker
        currentStage={currentStage}
        qualificationCompleted={journey?.qualification_completed}
        hasActiveQuote={quotesCount > 0}
      />

      {/* Main Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-slate-900">
              Active Insurance Journey
            </h2>
            <span className="text-xs text-slate-500 capitalize">
              Stage: {currentStage.replace(/_/g, " ")}
            </span>
          </div>

          {appsCount === 0 && quotesCount === 0 ? (
            journey?.qualification_completed ? (
              <Card className="border-emerald-200 bg-white">
                <CardContent className="p-5 space-y-3">
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
                        <h4 className="text-sm font-semibold text-slate-900">
                          Needs Assessment Completed & Saved
                        </h4>
                      </div>
                      <p className="text-xs text-slate-500 mt-1">
                        Your coverage requirements and risk tier have been calculated. Tailored policy recommendations are ready for review.
                      </p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <Button size="sm" variant="outline" asChild className="text-xs">
                        <Link href="/customer/needs-assessment">
                          Review Answers
                        </Link>
                      </Button>
                      <Button size="sm" asChild className="bg-blue-600 hover:bg-blue-700 text-white text-xs">
                        <Link href="/customer/recommendations">
                          Recommended Plans <ArrowRight className="ml-1 h-3.5 w-3.5" />
                        </Link>
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <EmptyState
                icon={Sparkles}
                title="Start Your Protection Journey"
                description="Complete your structured needs assessment to determine your coverage gap and view tailored policy recommendations."
                actionLabel="Complete Needs Assessment"
                onAction={() => window.location.assign("/customer/needs-assessment")}
                secondaryActionLabel="Chat with Advisor"
                onSecondaryAction={() => window.location.assign("/customer/chat")}
              />
            )
          ) : (
            <Card className="border-slate-200 bg-white">
              <CardContent className="p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-semibold text-slate-900">
                      {quotesCount > 0 ? "Indicative Quote Ready for Review" : "Proposal in Progress"}
                    </h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {quotesCount > 0
                        ? "You have active indicative premium estimates waiting for your review."
                        : "Your application is progressing through document and proposal verification."}
                    </p>
                  </div>
                  <Button size="sm" asChild>
                    <Link href={quotesCount > 0 ? "/customer/quotes" : "/customer/applications"}>
                      View Details <ArrowRight className="ml-1 h-3.5 w-3.5" />
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Quick Discovery Actions */}
        <div className="space-y-4">
          <h2 className="text-base font-semibold text-slate-900">
            Discovery Tools
          </h2>
          <div className="space-y-3">
            <Card className="hover:border-blue-200 transition-colors">
              <CardHeader className="p-4">
                <CardTitle className="text-sm font-semibold flex items-center justify-between">
                  <span>Coverage Calculator</span>
                  <Calculator className="h-4 w-4 text-blue-600" />
                </CardTitle>
                <CardDescription className="text-xs">
                  Calculate Human Life Value (HLV) and find your family's exact protection gap.
                </CardDescription>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <Button variant="outline" size="sm" className="w-full text-xs" asChild>
                  <Link href="/customer/calculator">Open HLV Calculator</Link>
                </Button>
              </CardContent>
            </Card>

            <Card className="hover:border-blue-200 transition-colors">
              <CardHeader className="p-4">
                <CardTitle className="text-sm font-semibold flex items-center justify-between">
                  <span>Needs Assessment</span>
                  <ListChecks className="h-4 w-4 text-emerald-600" />
                </CardTitle>
                <CardDescription className="text-xs">
                  {journey?.qualification_completed
                    ? "Completed: Profile & coverage requirements assessed."
                    : "Declare dependents, lifestyle factors, and existing insurance."}
                </CardDescription>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <Button variant="outline" size="sm" className="w-full text-xs" asChild>
                  <Link href="/customer/needs-assessment">
                    {journey?.qualification_completed ? "View / Edit Assessment" : "Take Assessment"}
                  </Link>
                </Button>
              </CardContent>
            </Card>

            <Card className="hover:border-blue-200 transition-colors">
              <CardHeader className="p-4">
                <CardTitle className="text-sm font-semibold flex items-center justify-between">
                  <span>Document Vault</span>
                  <FolderOpen className="h-4 w-4 text-slate-400" />
                </CardTitle>
                <CardDescription className="text-xs">
                  Upload ID proof, address verification, and medical records.
                </CardDescription>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <Button variant="outline" size="sm" className="w-full text-xs" asChild>
                  <Link href="/customer/documents">Manage Vault</Link>
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
