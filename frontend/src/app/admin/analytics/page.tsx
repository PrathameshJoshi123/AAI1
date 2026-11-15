"use client";

import React, { useEffect, useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { AdminAPI } from "@/services/admin.service";
import { ChannelPerformance, ProductPerformance, AdvisorPerformance, TurnaroundAnalytics } from "@/types/admin";
import { RefreshCw, TrendingUp, BarChart3, Clock, DollarSign, AlertCircle } from "lucide-react";

export default function AdminAnalyticsPage() {
  const [channels, setChannels] = useState<ChannelPerformance[]>([]);
  const [products, setProducts] = useState<ProductPerformance[]>([]);
  const [advisors, setAdvisors] = useState<AdvisorPerformance[]>([]);
  const [turnaround, setTurnaround] = useState<TurnaroundAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadAnalytics = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const [chData, prData, adData, tuData] = await Promise.all([
        AdminAPI.getChannelAnalytics(),
        AdminAPI.getProductAnalytics(),
        AdminAPI.getAdvisorAnalytics(),
        AdminAPI.getTurnaroundTimes(),
      ]);
      setChannels(chData);
      setProducts(prData);
      setAdvisors(adData);
      setTurnaround(tuData);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load business analytics.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Business Analytics & Financial Metrics"
        description="Deep-dive performance telemetry computed strictly from database records."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Business Analytics" },
        ]}
        actions={
          <Button variant="outline" size="sm" onClick={loadAnalytics} disabled={isLoading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isLoading ? "animate-spin" : ""}`} />
            Refresh Data
          </Button>
        }
      />

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg text-sm text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {/* Turnaround Summary Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-white border-slate-200">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase font-semibold">Avg Time to Quote</p>
              <p className="text-xl font-bold text-slate-900 mt-1">
                {turnaround?.avg_hours_to_quote || 0} hrs
              </p>
            </div>
            <Clock className="w-6 h-6 text-blue-600" />
          </CardContent>
        </Card>
        <Card className="bg-white border-slate-200">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase font-semibold">Avg Submission Time</p>
              <p className="text-xl font-bold text-slate-900 mt-1">
                {turnaround?.avg_hours_to_submission || 0} hrs
              </p>
            </div>
            <TrendingUp className="w-6 h-6 text-emerald-600" />
          </CardContent>
        </Card>
        <Card className="bg-white border-slate-200">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase font-semibold">Underwriting SLA</p>
              <p className="text-xl font-bold text-slate-900 mt-1">
                {turnaround?.avg_hours_to_underwriting_decision || 0} hrs
              </p>
            </div>
            <BarChart3 className="w-6 h-6 text-indigo-600" />
          </CardContent>
        </Card>
        <Card className="bg-white border-slate-200">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase font-semibold">SLA Compliance</p>
              <p className="text-xl font-bold text-emerald-600 mt-1">
                {turnaround?.sla_compliance_percentage || 0}%
              </p>
            </div>
            <DollarSign className="w-6 h-6 text-emerald-600" />
          </CardContent>
        </Card>
      </div>

      {/* Product Revenue & Conversion Performance */}
      <Card className="bg-white border-slate-200 shadow-sm">
        <CardHeader className="pb-3 border-b border-slate-100">
          <CardTitle className="text-sm font-bold text-slate-900">
            Product Portfolio & Annualized Premium Revenue
          </CardTitle>
          <CardDescription className="text-xs text-slate-500">
            Real quote and proposal volume aggregated by configured insurance product
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-2">
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full" />
            </div>
          ) : products.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-xs">
              No product quotes recorded yet in SQLite.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50/50">
                  <TableHead className="text-xs font-semibold">Insurance Product</TableHead>
                  <TableHead className="text-xs font-semibold">Category</TableHead>
                  <TableHead className="text-xs font-semibold text-right">Quotes Formulated</TableHead>
                  <TableHead className="text-xs font-semibold text-right">Proposals Submitted</TableHead>
                  <TableHead className="text-xs font-semibold text-right">Approved Policies</TableHead>
                  <TableHead className="text-xs font-semibold text-right">Quote-to-App %</TableHead>
                  <TableHead className="text-xs font-semibold text-right">Est. Annualized Premium</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {products.map((p) => (
                  <TableRow key={p.product_id} className="hover:bg-slate-50/50">
                    <TableCell className="font-semibold text-sm text-slate-900">{p.product_name}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-[11px] capitalize">
                        {p.category.replace("_", " ")}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right text-xs font-mono">{p.quotes_count}</TableCell>
                    <TableCell className="text-right text-xs font-mono">{p.applications_count}</TableCell>
                    <TableCell className="text-right text-xs font-mono font-semibold text-emerald-600">
                      {p.approved_count}
                    </TableCell>
                    <TableCell className="text-right text-xs font-semibold text-slate-700">
                      {p.conversion_rate}%
                    </TableCell>
                    <TableCell className="text-right text-xs font-mono font-bold text-slate-900">
                      ₹{p.total_estimated_premium.toLocaleString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Acquisition Channel Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-white border-slate-200 shadow-sm">
          <CardHeader className="pb-3 border-b border-slate-100">
            <CardTitle className="text-sm font-bold text-slate-900">
              Acquisition Channel Performance
            </CardTitle>
            <CardDescription className="text-xs text-slate-500">
              Lead volume, qualification scores, and conversion by lead source
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="p-6 space-y-2">
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
              </div>
            ) : channels.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-xs">
                No lead acquisition records detected.
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-50/50">
                    <TableHead className="text-xs font-semibold">Channel</TableHead>
                    <TableHead className="text-xs font-semibold text-right">Leads</TableHead>
                    <TableHead className="text-xs font-semibold text-right">Qualified</TableHead>
                    <TableHead className="text-xs font-semibold text-right">Conversion</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {channels.map((ch) => (
                    <TableRow key={ch.channel}>
                      <TableCell className="font-semibold text-xs text-slate-800">{ch.channel}</TableCell>
                      <TableCell className="text-right text-xs font-mono">{ch.total_leads}</TableCell>
                      <TableCell className="text-right text-xs font-mono">{ch.qualified_leads}</TableCell>
                      <TableCell className="text-right text-xs font-bold text-blue-600">
                        {ch.conversion_rate}%
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Advisor Productivity Benchmarks */}
        <Card className="bg-white border-slate-200 shadow-sm">
          <CardHeader className="pb-3 border-b border-slate-100">
            <CardTitle className="text-sm font-bold text-slate-900">
              Advisor Productivity Benchmarks
            </CardTitle>
            <CardDescription className="text-xs text-slate-500">
              Caseloads, reviews, and completion rates by assigned staff member
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="p-6 space-y-2">
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
              </div>
            ) : advisors.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-xs">
                No advisor benchmark data available.
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-50/50">
                    <TableHead className="text-xs font-semibold">Advisor</TableHead>
                    <TableHead className="text-xs font-semibold text-right">Active Cases</TableHead>
                    <TableHead className="text-xs font-semibold text-right">Reviews</TableHead>
                    <TableHead className="text-xs font-semibold text-right">Pending Tasks</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {advisors.map((adv) => (
                    <TableRow key={adv.advisor_id}>
                      <TableCell>
                        <p className="font-semibold text-xs text-slate-800">{adv.advisor_name}</p>
                        <p className="text-[10px] text-slate-400">{adv.email}</p>
                      </TableCell>
                      <TableCell className="text-right text-xs font-mono">{adv.active_cases}</TableCell>
                      <TableCell className="text-right text-xs font-mono">{adv.completed_reviews}</TableCell>
                      <TableCell className="text-right text-xs font-mono text-amber-600">
                        {adv.pending_follow_ups}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

