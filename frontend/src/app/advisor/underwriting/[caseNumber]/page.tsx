"use client";

import * as React from "react";
import { useParams, useRouter } from "next/navigation";
import { Clock } from "lucide-react";

export default function UnderwritingCaseRedirectPage() {
  const params = useParams();
  const router = useRouter();
  const caseNumber = params?.caseNumber as string;

  React.useEffect(() => {
    if (caseNumber) {
      router.replace(`/advisor/cases/${encodeURIComponent(caseNumber)}`);
    }
  }, [caseNumber, router]);

  return (
    <div className="flex flex-col items-center justify-center p-24 text-slate-400 text-sm">
      <Clock className="h-6 w-6 animate-spin mb-2 text-blue-600" />
      Loading Underwriting Cockpit for Case {caseNumber}...
    </div>
  );
}

