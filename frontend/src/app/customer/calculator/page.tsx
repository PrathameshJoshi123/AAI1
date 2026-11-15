"use client";

import * as React from "react";
import Link from "next/link";
import {
  Calculator,
  ArrowRight,
  ShieldCheck,
  TrendingUp,
  AlertCircle,
  HelpCircle,
  CheckCircle2,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CustomerAPI } from "@/services/customer-api";
import { HLVCalculationPayload, HLVCalculationResult } from "@/types/customer";

export default function CoverageCalculatorPage() {
  const [params, setParams] = React.useState<HLVCalculationPayload>({
    annual_income: 1500000,
    current_age: 32,
    retirement_age: 60,
    annual_household_expenses: 600000,
    outstanding_liabilities: 3500000,
    current_liquid_investments: 1000000,
    inflation_rate_percent: 6.0,
  });

  const [result, setResult] = React.useState<HLVCalculationResult | null>(null);
  const [loading, setLoading] = React.useState<boolean>(false);

  const calculate = React.useCallback(async (payload: HLVCalculationPayload) => {
    setLoading(true);
    try {
      const data = await CustomerAPI.calculateHLV(payload);
      setResult(data);
    } catch (err) {
      console.error("HLV Calculation failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    calculate(params);
  }, []);

  const handleRecalculate = (e: React.FormEvent) => {
    e.preventDefault();
    calculate(params);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <PageHeader
        title="Human Life Value (HLV) Calculator"
        description="Deterministic actuarial income replacement and expense capitalization model."
        breadcrumbs={[
          { label: "Customer Portal", href: "/customer" },
          { label: "Coverage Calculator" },
        ]}
      />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Input Parameters Form */}
        <Card className="lg:col-span-7 border-slate-200 bg-white shadow-2xs">
          <CardHeader className="p-5 pb-3">
            <CardTitle className="text-base font-semibold text-slate-900 flex items-center justify-between">
              <span>Financial Protection Inputs</span>
              <span className="text-xs font-normal text-slate-500">Actuarially Verified</span>
            </CardTitle>
            <CardDescription className="text-xs text-slate-500">
              Adjust your earning profile and family liabilities to estimate ideal life insurance coverage.
            </CardDescription>
          </CardHeader>

          <CardContent className="p-5 pt-0">
            <form onSubmit={handleRecalculate} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label className="text-xs font-semibold text-slate-700">Current Age</Label>
                  <Input
                    type="number"
                    min={18}
                    max={65}
                    value={params.current_age}
                    onChange={(e) => setParams({ ...params, current_age: parseInt(e.target.value) || 18 })}
                    className="text-xs bg-white"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-xs font-semibold text-slate-700">Retirement Age</Label>
                  <Input
                    type="number"
                    min={45}
                    max={75}
                    value={params.retirement_age}
                    onChange={(e) => setParams({ ...params, retirement_age: parseInt(e.target.value) || 60 })}
                    className="text-xs bg-white"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between items-center">
                  <Label className="text-xs font-semibold text-slate-700">Gross Annual Income (₹ INR)</Label>
                  <span className="text-xs font-bold text-slate-900">₹{params.annual_income.toLocaleString("en-IN")}</span>
                </div>
                <Input
                  type="number"
                  step="50000"
                  min={100000}
                  value={params.annual_income}
                  onChange={(e) => setParams({ ...params, annual_income: parseFloat(e.target.value) || 0 })}
                  className="text-xs bg-white"
                />
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between items-center">
                  <Label className="text-xs font-semibold text-slate-700">Annual Household Expenses (₹ INR)</Label>
                  <span className="text-xs font-bold text-slate-900">₹{params.annual_household_expenses.toLocaleString("en-IN")}</span>
                </div>
                <Input
                  type="number"
                  step="25000"
                  min={50000}
                  value={params.annual_household_expenses}
                  onChange={(e) => setParams({ ...params, annual_household_expenses: parseFloat(e.target.value) || 0 })}
                  className="text-xs bg-white"
                />
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between items-center">
                  <Label className="text-xs font-semibold text-slate-700">Outstanding Loans / Liabilities (₹ INR)</Label>
                  <span className="text-xs font-bold text-slate-900">₹{params.outstanding_liabilities.toLocaleString("en-IN")}</span>
                </div>
                <Input
                  type="number"
                  step="100000"
                  min={0}
                  value={params.outstanding_liabilities}
                  onChange={(e) => setParams({ ...params, outstanding_liabilities: parseFloat(e.target.value) || 0 })}
                  className="text-xs bg-white"
                />
                <p className="text-[11px] text-slate-400">Home mortgages, car loans, and business liabilities.</p>
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between items-center">
                  <Label className="text-xs font-semibold text-slate-700">Existing Liquid Savings / Cover (₹ INR)</Label>
                  <span className="text-xs font-bold text-slate-900">₹{params.current_liquid_investments.toLocaleString("en-IN")}</span>
                </div>
                <Input
                  type="number"
                  step="100000"
                  min={0}
                  value={params.current_liquid_investments}
                  onChange={(e) => setParams({ ...params, current_liquid_investments: parseFloat(e.target.value) || 0 })}
                  className="text-xs bg-white"
                />
              </div>

              <Button type="submit" size="sm" disabled={loading} className="w-full text-xs bg-blue-600 hover:bg-blue-700 text-white">
                {loading ? "Calculating..." : "Update HLV Calculation"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Real-Time Calculation Output */}
        <div className="lg:col-span-5 space-y-4">
          {result && (
            <Card className="border-blue-200 bg-white shadow-2xs overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-5 text-white">
                <span className="text-[11px] uppercase tracking-wider font-semibold text-blue-100 block">
                  Recommended Term Cover
                </span>
                <span className="text-2xl font-bold mt-1 block">
                  ₹{result.recommended_term_cover.toLocaleString("en-IN")}
                </span>
                <span className="text-xs text-blue-200 mt-1 block">
                  Multiplier: {result.rule_of_thumb_multiplier}
                </span>
              </div>

              <CardContent className="p-5 space-y-4 text-xs">
                <div className="space-y-2">
                  <div className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-600">Working Years Remaining:</span>
                    <span className="font-semibold text-slate-900">{result.calculation_breakdown.working_years_remaining} years</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-600">Capitalized Family Income:</span>
                    <span className="font-semibold text-slate-900">₹{result.calculation_breakdown.capitalized_future_income.toLocaleString("en-IN")}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-600">Liabilities Added:</span>
                    <span className="font-semibold text-amber-700">+₹{result.outstanding_liabilities_component.toLocaleString("en-IN")}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-600">Existing Assets Offset:</span>
                    <span className="font-semibold text-emerald-700">-₹{result.existing_cover_offset.toLocaleString("en-IN")}</span>
                  </div>
                  <div className="flex justify-between py-1.5 font-bold text-slate-900">
                    <span>Net Protection Gap:</span>
                    <span className="text-blue-600">₹{result.net_protection_gap.toLocaleString("en-IN")}</span>
                  </div>
                </div>

                <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-[11px] text-slate-600 leading-relaxed">
                  <div className="font-semibold text-slate-800 mb-1 flex items-center gap-1">
                    <ShieldCheck className="h-3.5 w-3.5 text-blue-600" />
                    Transparent Mathematical Basis
                  </div>
                  {result.formula_explanation}
                </div>

                <div className="pt-2 flex flex-col gap-2">
                  <Button size="sm" asChild className="w-full text-xs bg-blue-600 hover:bg-blue-700 text-white">
                    <Link href={`/customer/recommendations?amount=${result.recommended_term_cover}`}>
                      Find Plans for this Cover <ArrowRight className="h-3.5 w-3.5 ml-1" />
                    </Link>
                  </Button>
                  <Button size="sm" variant="outline" asChild className="w-full text-xs">
                    <Link href={`/customer/chat?topic=hlv&amount=${result.recommended_term_cover}&gap=${result.net_protection_gap}`}>
                      Ask AI Advisor About HLV
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

