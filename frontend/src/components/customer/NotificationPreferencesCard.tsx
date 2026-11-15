"use client";

import * as React from "react";
import { Bell, CheckCircle2, Shield, AlertCircle, Loader2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { CustomerAPI } from "@/services/customer-api";

export function NotificationPreferencesCard() {
  const [loading, setLoading] = React.useState(true);
  const [saving, setSaving] = React.useState(false);
  const [successMsg, setSuccessMsg] = React.useState<string | null>(null);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);

  const [quoteAlerts, setQuoteAlerts] = React.useState(true);
  const [appUpdates, setAppUpdates] = React.useState(true);
  const [docRequests, setDocRequests] = React.useState(true);
  const [marketingConsent, setMarketingConsent] = React.useState(false);

  React.useEffect(() => {
    async function fetchPrefs() {
      try {
        const data = await CustomerAPI.getEmailPreferences();
        if (data) {
          setQuoteAlerts(data.quote_alerts !== false);
          setAppUpdates(data.application_updates !== false);
          setDocRequests(data.document_requests !== false);
          setMarketingConsent(data.marketing_consent === true);
        }
      } catch (err) {
        console.error("Failed to load email preferences:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchPrefs();
  }, []);

  const handleToggle = async (key: string, value: boolean) => {
    setSaving(true);
    setSuccessMsg(null);
    setErrorMsg(null);

    const payload = {
      quote_alerts: key === "quote_alerts" ? value : quoteAlerts,
      application_updates: key === "application_updates" ? value : appUpdates,
      document_requests: key === "document_requests" ? value : docRequests,
      marketing_consent: key === "marketing_consent" ? value : marketingConsent,
    };

    if (key === "quote_alerts") setQuoteAlerts(value);
    if (key === "application_updates") setAppUpdates(value);
    if (key === "document_requests") setDocRequests(value);
    if (key === "marketing_consent") setMarketingConsent(value);

    try {
      await CustomerAPI.updateEmailPreferences(payload);
      setSuccessMsg("Notification preferences synchronized successfully.");
    } catch (err: any) {
      setErrorMsg(err?.message || "Failed to update notification settings.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Card className="border-slate-200 bg-white p-6 shadow-2xs">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
          Loading notification settings...
        </div>
      </Card>
    );
  }

  return (
    <Card className="border-slate-200 bg-white shadow-2xs">
      <CardHeader className="p-5 pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold text-slate-900 flex items-center gap-2">
            <Bell className="h-4 w-4 text-blue-600" />
            Email Notification Channels & Consent
          </CardTitle>
          {saving && (
            <span className="text-[11px] text-blue-600 flex items-center gap-1">
              <Loader2 className="h-3 w-3 animate-spin" />
              Saving...
            </span>
          )}
        </div>
        <CardDescription className="text-xs text-slate-500">
          Customize which regulated transactional alerts and communication updates you receive via email.
        </CardDescription>
      </CardHeader>
      <CardContent className="p-5 pt-0 space-y-4">
        {successMsg && (
          <div className="p-2.5 bg-emerald-50 border border-emerald-200 rounded-md text-xs text-emerald-800 flex items-center gap-2">
            <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-emerald-600" />
            <span>{successMsg}</span>
          </div>
        )}

        {errorMsg && (
          <div className="p-2.5 bg-red-50 border border-red-200 rounded-md text-xs text-red-700 flex items-center gap-2">
            <AlertCircle className="h-3.5 w-3.5 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        <div className="divide-y divide-slate-100">
          {/* Quote Alerts */}
          <div className="flex items-center justify-between py-3">
            <div className="space-y-0.5 pr-4">
              <Label className="text-xs font-semibold text-slate-800">Quotes & Actuarial Pricing Summaries</Label>
              <p className="text-[11px] text-slate-500">
                Receive instant emails with premium calculations, product comparisons, and benefit schedules.
              </p>
            </div>
            <Switch
              checked={quoteAlerts}
              onCheckedChange={(val) => handleToggle("quote_alerts", val)}
              className="data-[state=checked]:bg-blue-600"
            />
          </div>

          {/* Application Updates */}
          <div className="flex items-center justify-between py-3">
            <div className="space-y-0.5 pr-4">
              <Label className="text-xs font-semibold text-slate-800">Application & Underwriting Milestones</Label>
              <p className="text-[11px] text-slate-500">
                Receive notifications when your proposal progresses to underwriter review or formal approval.
              </p>
            </div>
            <Switch
              checked={appUpdates}
              onCheckedChange={(val) => handleToggle("application_updates", val)}
              className="data-[state=checked]:bg-blue-600"
            />
          </div>

          {/* Document Verification */}
          <div className="flex items-center justify-between py-3">
            <div className="space-y-0.5 pr-4">
              <Label className="text-xs font-semibold text-slate-800">KYC & Document Verification Alerts</Label>
              <p className="text-[11px] text-slate-500">
                Immediate alerts if additional proof of identity or medical reports are requested by the underwriter.
              </p>
            </div>
            <Switch
              checked={docRequests}
              onCheckedChange={(val) => handleToggle("document_requests", val)}
              className="data-[state=checked]:bg-blue-600"
            />
          </div>

          {/* Marketing / Advisory Consent */}
          <div className="flex items-center justify-between py-3">
            <div className="space-y-0.5 pr-4">
              <div className="flex items-center gap-1.5">
                <Label className="text-xs font-semibold text-slate-800">Advisory Outreach & Follow-up Communications</Label>
                <span className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded border border-slate-200">
                  DPDP Act 2023
                </span>
              </div>
              <p className="text-[11px] text-slate-500">
                Consent to receive tailored insurance advice, policy renewal reminders, and advisor check-ins.
              </p>
            </div>
            <Switch
              checked={marketingConsent}
              onCheckedChange={(val) => handleToggle("marketing_consent", val)}
              className="data-[state=checked]:bg-blue-600"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

