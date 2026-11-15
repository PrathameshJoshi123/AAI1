"use client";

import React, { useEffect, useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { FunnelVisualizer } from "@/components/admin/funnel-visualizer";
import { AdminAPI } from "@/services/admin.service";
import { ConversionFunnelResponse } from "@/types/admin";
import { RefreshCw, Sparkles, AlertCircle } from "lucide-react";

export default function AdminFunnelPage() {
  const [funnel, setFunnel] = useState<ConversionFunnelResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadFunnel = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await AdminAPI.getConversionFunnel();
      setFunnel(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load conversion funnel.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadFunnel();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Acquisition & Onboarding Conversion Funnel"
        description="Quantitative stage-by-stage drop-off analysis and leakage detection across the 8 journey checkpoints."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Conversion Funnel" },
        ]}
        actions={
          <Button variant="outline" size="sm" onClick={loadFunnel} disabled={isLoading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isLoading ? "animate-spin" : ""}`} />
            Recalculate Funnel
          </Button>
        }
      />

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg text-sm text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {/* Visual Funnel Card */}
      <Card className="bg-white border-slate-200 shadow-sm">
        <CardContent className="p-6">
          {isLoading ? (
            <div className="space-y-3">
              <Skeleton className="h-6 w-1/3" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : (
            <FunnelVisualizer
              stages={funnel?.stages || []}
              overallConversion={funnel?.overall_conversion || 0}
            />
          )}
        </CardContent>
      </Card>

      {/* Detailed Funnel Stage Breakdown Table */}
      <Card className="bg-white border-slate-200 shadow-sm">
        <CardHeader className="pb-3 border-b border-slate-100">
          <CardTitle className="text-sm font-bold text-slate-900">
            Conversion Leakage & Drop-Off Analytics
          </CardTitle>
          <CardDescription className="text-xs text-slate-500">
            Volume of prospects progressing versus abandoning at each critical workflow milestone
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-2">
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full" />
            </div>
          ) : !funnel || funnel.stages.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-xs">
              No conversion stage data available yet.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50/50">
                  <TableHead className="text-xs font-semibold">Stage</TableHead>
                  <TableHead className="text-xs font-semibold text-right">Entrants (Count)</TableHead>
                  <TableHead className="text-xs font-semibold text-right">Drop-off Count</TableHead>
                  <TableHead className="text-xs font-semibold text-right">Step Conversion %</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {funnel.stages.map((stage, idx) => (
                  <TableRow key={stage.stage_key} className="hover:bg-slate-50/50">
                    <TableCell className="font-semibold text-xs text-slate-900">
                      {stage.label}
                    </TableCell>
                    <TableCell className="text-right text-xs font-mono font-semibold">
                      {stage.count.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right text-xs font-mono text-rose-600">
                      {idx === 0 ? "—" : stage.drop_off_count.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right text-xs font-bold text-blue-600">
                      {stage.conversion_from_prev}%
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

