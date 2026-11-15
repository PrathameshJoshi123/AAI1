"use client";

import * as React from "react";
import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ClipboardList, Loader2 } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { ApplicationAPI } from "@/services/application.service";
import { ApplicationItem } from "@/types/application";

function CustomerOnboardingContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [loading, setLoading] = React.useState<boolean>(true);
  const [applications, setApplications] = React.useState<ApplicationItem[]>([]);

  React.useEffect(() => {
    async function load() {
      const quoteIdParam = searchParams.get("quote_id") || searchParams.get("quoteId");
      if (quoteIdParam) {
        router.replace(`/customer/onboarding/${quoteIdParam}`);
        return;
      }

      try {
        const apps = await ApplicationAPI.listApplications();
        setApplications(apps);
        // Find latest draft if any
        const draft = apps.find((a) => a.status === "draft" || a.status === "documents_pending");
        if (draft) {
          router.replace(`/customer/onboarding/${draft.quote_id}`);
          return;
        }
      } catch (err) {
        console.error("Failed to load applications:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [router, searchParams]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-3">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        <p className="text-xs text-slate-500 font-medium">Checking application status...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <PageHeader
        title="Insurance Proposal Onboarding"
        description="Select an active indicative quote to initiate step-by-step proposal onboarding and KYC verification."
        breadcrumbs={[
          { label: "Customer Portal", href: "/customer" },
          { label: "Onboarding" },
        ]}
      />

      <EmptyState
        icon={ClipboardList}
        title="No Active Proposal Draft in Progress"
        description="To begin your formal insurance proposal, select one of your calculated quotes or explore plans suited to your coverage needs."
        actionLabel="View Active Quotes"
        onAction={() => router.push("/customer/quotes")}
      />
    </div>
  );
}

export default function CustomerOnboardingRedirectPage() {
  return (
    <Suspense
      fallback={
        <div className="flex flex-col items-center justify-center min-h-[400px] space-y-3">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
          <p className="text-xs text-slate-500 font-medium">Checking application status...</p>
        </div>
      }
    >
      <CustomerOnboardingContent />
    </Suspense>
  );
}
