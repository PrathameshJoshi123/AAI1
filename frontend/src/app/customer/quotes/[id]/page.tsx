"use client";

import * as React from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  FileText,
  ShieldCheck,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  SlidersHorizontal,
  RefreshCw,
  Calculator,
  Lock,
  Calendar,
  Layers,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { QuoteAPI } from "@/services/quote-api";
import { QuoteItem, QuoteCalculationBreakdown } from "@/types/quote";
import { SendQuoteEmailDialog } from "@/components/customer/SendQuoteEmailDialog";


export default function QuoteDetailPage() {
  const params = useParams();
  const router = useRouter();
  const quoteId = params.id as string;

  const [quote, setQuote] = React.useState<QuoteItem | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [recalculating, setRecalculating] = React.useState<boolean>(false);

  // Interactive Form State
  const [sumAssured, setSumAssured] = React.useState<number>(10000000);
  const [policyTerm, setPolicyTerm] = React.useState<number>(30);
  const [frequency, setFrequency] = React.useState<"monthly" | "quarterly" | "half_yearly" | "annually">("annually");
  const [selectedRiders, setSelectedRiders] = React.useState<string[]>([]);

  const loadQuote = React.useCallback(async () => {
    try {
      const q = await QuoteAPI.getQuote(quoteId);
      setQuote(q);
      setSumAssured(Number(q.sum_assured));
      setPolicyTerm(q.policy_term_years);
      setFrequency(q.payment_frequency as any);
      if (q.selected_riders_json && Array.isArray(q.selected_riders_json)) {
        setSelectedRiders(q.selected_riders_json.map((r) => r.rider_code));
      }
    } catch (err) {
      console.error("Failed to load quote details:", err);
    } finally {
      setLoading(false);
    }
  }, [quoteId]);

  React.useEffect(() => {
    loadQuote();
  }, [loadQuote]);

  const handleRecalculate = async (
    newSa = sumAssured,
    newTerm = policyTerm,
    newFreq = frequency,
    newRiders = selectedRiders
  ) => {
    try {
      setRecalculating(true);
      const updated = await QuoteAPI.recalculateQuote(quoteId, {
        sum_assured: newSa,
        policy_term_years: newTerm,
        payment_frequency: newFreq,
        selected_rider_codes: newRiders,
      });
      setQuote(updated);
    } catch (err) {
      console.error("Recalculation error:", err);
    } finally {
      setRecalculating(false);
    }
  };

  const handleRiderToggle = (code: string) => {
    const updated = selectedRiders.includes(code)
      ? selectedRiders.filter((r) => r !== code)
      : [...selectedRiders, code];
    setSelectedRiders(updated);
    handleRecalculate(sumAssured, policyTerm, frequency, updated);
  };

  const handleFrequencyChange = (newFreq: "monthly" | "quarterly" | "half_yearly" | "annually") => {
    setFrequency(newFreq);
    handleRecalculate(sumAssured, policyTerm, newFreq, selectedRiders);
  };

  if (loading || !quote) {
    return (
      <div className="max-w-5xl mx-auto p-12 text-center space-y-3">
        <RefreshCw className="h-6 w-6 text-blue-600 animate-spin mx-auto" />
        <p className="text-xs text-slate-500">Retrieving actuarial quote breakdown...</p>
      </div>
    );
  }

  const breakdown: QuoteCalculationBreakdown | undefined = quote.calculation_breakdown_json as any;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <PageHeader
        title={`Quote Breakdown: ${quote.quote_number}`}
        description={`Itemized actuarial pricing schedule powered by version ${quote.pricing_matrix_version}.`}
        breadcrumbs={[
          { label: "Customer Portal", href: "/customer" },
          { label: "Quotes", href: "/customer/quotes" },
          { label: quote.quote_number },
        ]}
        actions={
          <Button size="sm" variant="outline" asChild className="text-xs border-slate-200">
            <Link href="/customer/quotes">
              <ArrowLeft className="h-3.5 w-3.5 mr-1.5" />
              Back to Quotes
            </Link>
          </Button>
        }
      />

      {/* Main Grid: Customizer on Left, Invoice Math on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Interactive Customizer (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <Card className="border-slate-200 bg-white shadow-xs">
            <CardHeader className="p-5 pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                  <SlidersHorizontal className="h-4 w-4 text-blue-600" />
                  Interactive Coverage Parameters
                </CardTitle>
                <span className="text-[11px] font-mono text-slate-500">
                  Matrix: {quote.pricing_matrix_version}
                </span>
              </div>
              <CardDescription className="text-xs text-slate-500">
                Adjust sum assured, tenure, and installment frequency for live deterministic recalculation.
              </CardDescription>
            </CardHeader>

            <CardContent className="p-5 pt-0 space-y-5 text-xs">
              {/* Sum Assured Input */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <Label htmlFor="sumAssured" className="text-xs font-medium text-slate-700">
                    Sum Assured Protection (₹)
                  </Label>
                  <span className="font-bold text-blue-600 text-sm">
                    ₹{sumAssured.toLocaleString("en-IN")}
                  </span>
                </div>
                <Input
                  id="sumAssured"
                  type="number"
                  step="500000"
                  min="1000000"
                  max="50000000"
                  value={sumAssured}
                  onChange={(e) => {
                    const val = parseFloat(e.target.value) || 1000000;
                    setSumAssured(val);
                  }}
                  onBlur={() => handleRecalculate(sumAssured, policyTerm, frequency, selectedRiders)}
                  className="text-xs font-mono bg-white border-slate-200"
                />
                <div className="flex justify-between text-[10px] text-slate-400">
                  <span>Min: ₹25 Lakhs</span>
                  <span>Max: ₹5 Crores</span>
                </div>
              </div>

              {/* Policy Term Selection */}
              <div className="space-y-1.5">
                <Label htmlFor="term" className="text-xs font-medium text-slate-700">
                  Policy Tenure (Years)
                </Label>
                <Select
                  value={String(policyTerm)}
                  onValueChange={(val) => {
                    const t = parseInt(val, 10);
                    setPolicyTerm(t);
                    handleRecalculate(sumAssured, t, frequency, selectedRiders);
                  }}
                >
                  <SelectTrigger id="term" className="text-xs bg-white border-slate-200">
                    <SelectValue placeholder="Select tenure" />
                  </SelectTrigger>
                  <SelectContent className="bg-white border-slate-200">
                    {[10, 15, 20, 25, 30, 35, 40].map((yr) => (
                      <SelectItem key={yr} value={String(yr)} className="text-xs">
                        {yr} Years Tenure
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Payment Frequency Toggle Buttons */}
              <div className="space-y-1.5">
                <Label className="text-xs font-medium text-slate-700 block">
                  Payment Installment Frequency
                </Label>
                <div className="grid grid-cols-4 gap-2">
                  {(["monthly", "quarterly", "half_yearly", "annually"] as const).map((freq) => (
                    <button
                      key={freq}
                      type="button"
                      onClick={() => handleFrequencyChange(freq)}
                      className={`py-2 px-2.5 rounded text-xs font-medium border text-center transition-all capitalize ${
                        frequency === freq
                          ? "bg-blue-600 border-blue-600 text-white shadow-2xs"
                          : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"
                      }`}
                    >
                      {freq.replace(/_/g, " ")}
                    </button>
                  ))}
                </div>
              </div>

              {/* Optional Riders Selection */}
              <div className="space-y-2.5 pt-3 border-t border-slate-100">
                <Label className="text-xs font-semibold text-slate-900 block">
                  Optional Policy Add-On Riders
                </Label>

                <div className="space-y-2">
                  {[
                    {
                      code: "ACC_DEATH",
                      name: "Accidental Death Benefit",
                      rate: "₹0.25 / ₹1k SA",
                      desc: "Double sum assured payout in event of accidental demise.",
                    },
                    {
                      code: "CRIT_ILL",
                      name: "Accelerated Critical Illness Cover",
                      rate: "₹0.75 / ₹1k SA",
                      desc: "Immediate lump sum payout upon diagnosis of 36 critical illnesses.",
                    },
                    {
                      code: "PREM_WAIVER",
                      name: "Waiver of Premium on Disability",
                      rate: "₹0.15 / ₹1k SA",
                      desc: "All future premiums waived upon permanent total disability.",
                    },
                  ].map((rider) => {
                    const isChecked = selectedRiders.includes(rider.code);
                    return (
                      <div
                        key={rider.code}
                        onClick={() => handleRiderToggle(rider.code)}
                        className={`p-3 rounded-lg border cursor-pointer transition-all flex items-start gap-2.5 ${
                          isChecked ? "border-blue-300 bg-blue-50/30" : "border-slate-200 bg-white hover:bg-slate-50"
                        }`}
                      >
                        <Checkbox checked={isChecked} onCheckedChange={() => handleRiderToggle(rider.code)} className="mt-0.5" />
                        <div className="space-y-0.5 flex-1">
                          <div className="flex justify-between items-center">
                            <span className="font-semibold text-slate-900">{rider.name}</span>
                            <span className="text-[11px] font-mono text-blue-600 font-medium">{rider.rate}</span>
                          </div>
                          <p className="text-[11px] text-slate-500 leading-relaxed">{rider.desc}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Invoice-Style Actuarial Math Breakdown (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <Card className="border-slate-200 bg-white shadow-xs">
            <CardHeader className="p-5 pb-3 bg-slate-50 border-b border-slate-100 rounded-t-xl">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Actuarial Premium Schedule
                </span>
                <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  AUDITED CALCULATION
                </span>
              </div>
              <CardTitle className="text-2xl font-bold text-slate-900 mt-1">
                ₹{Number(quote.total_premium).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                <span className="text-xs text-slate-500 font-normal ml-1">/{quote.payment_frequency}</span>
              </CardTitle>
            </CardHeader>

            <CardContent className="p-5 space-y-3.5 text-xs">
              <div className="space-y-2">
                <div className="flex justify-between text-slate-600">
                  <span>Base Premium ({quote.payment_frequency}):</span>
                  <span className="font-mono text-slate-900 font-medium">
                    ₹{Number(quote.base_premium).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                  </span>
                </div>

                {Number(quote.health_loading_amount) > 0 && (
                  <div className="flex justify-between text-amber-700">
                    <span>Medical / Mortality Loading:</span>
                    <span className="font-mono font-medium">
                      +₹{Number(quote.health_loading_amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                )}

                {Number(quote.rider_premium) > 0 && (
                  <div className="flex justify-between text-blue-700">
                    <span>Optional Riders ({quote.selected_riders_json?.length || 0}):</span>
                    <span className="font-mono font-medium">
                      +₹{Number(quote.rider_premium).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                )}

                <div className="flex justify-between text-slate-700 font-medium pt-2 border-t border-slate-100">
                  <span>Net Premium (Pre-Tax):</span>
                  <span className="font-mono">
                    ₹{Number(quote.net_premium).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                  </span>
                </div>

                <div className="flex justify-between text-slate-600">
                  <span>GST Applicable (18.00%):</span>
                  <span className="font-mono text-slate-900">
                    ₹{Number(quote.tax_amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                  </span>
                </div>
              </div>

              {/* Total Payable Box */}
              <div className="p-3 bg-blue-50/60 rounded-lg border border-blue-100 space-y-1">
                <div className="flex justify-between items-center text-sm font-bold text-blue-950">
                  <span>Total Premium Payable:</span>
                  <span className="text-base text-blue-700">
                    ₹{Number(quote.total_premium).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                  </span>
                </div>
                <div className="text-[10px] text-blue-700 flex justify-between">
                  <span>Billing Cycle: {quote.payment_frequency.toUpperCase()}</span>
                  <span>Quote Valid for 30 Days</span>
                </div>
              </div>

              {/* Statutory Notice */}
              <div className="p-2.5 bg-slate-50 border border-slate-100 rounded text-[11px] text-slate-500 leading-relaxed flex items-start gap-1.5">
                <AlertCircle className="h-3.5 w-3.5 text-slate-400 shrink-0 mt-0.5" />
                <span>
                  Indicative quote only. Final premium and policy terms are subject to formal underwriting review and insurer acceptance.
                </span>
              </div>
            </CardContent>

            <CardFooter className="p-5 pt-0 border-t border-slate-100 flex flex-col gap-2">
              <Button size="sm" asChild className="w-full text-xs bg-blue-600 hover:bg-blue-700 text-white h-9">
                <Link href={`/customer/onboarding/${quote.id}`}>
                  Apply for this Policy <ArrowRight className="h-3.5 w-3.5 ml-1.5" />
                </Link>
              </Button>
              <SendQuoteEmailDialog quoteId={quote.id} quoteNumber={quote.quote_number} />
              <Button size="sm" variant="outline" asChild className="w-full text-xs border-slate-200">
                <Link href={`/customer/chat?product_id=${quote.product_id}&product_name=${encodeURIComponent(quote.product?.name || "Quote Review")}&action=quote`}>
                  Discuss Quote with AI Advisor
                </Link>
              </Button>
            </CardFooter>

          </Card>
        </div>
      </div>
    </div>
  );
}

