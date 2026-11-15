"use client";

import * as React from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  React.useEffect(() => {
    console.error("Application runtime error:", error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-white px-4 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-50 text-red-600 mb-4 border border-red-100">
        <AlertTriangle className="h-8 w-8" />
      </div>
      <h1 className="text-2xl font-bold tracking-tight text-slate-900">
        System Processing Error
      </h1>
      <p className="mt-2 max-w-md text-sm text-slate-500">
        An unexpected error occurred while rendering this interface. Details have been logged to the compliance audit record.
      </p>
      <div className="mt-6 flex items-center gap-3">
        <Button onClick={() => reset()} size="sm">
          <RotateCcw className="mr-2 h-4 w-4" /> Try Again
        </Button>
      </div>
    </div>
  );
}

