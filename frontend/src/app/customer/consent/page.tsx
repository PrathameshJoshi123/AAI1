"use client";

import * as React from "react";
import { ShieldCheck, CheckCircle2, XCircle, AlertTriangle, RefreshCw } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CustomerAPI } from "@/services/customer-api";
import { ConsentRecordItem } from "@/types/customer";

export default function CustomerConsentPage() {
  const [consents, setConsents] = React.useState<ConsentRecordItem[]>([]);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [actionLoading, setActionLoading] = React.useState<string | null>(null);

  const fetchConsents = React.useCallback(async () => {
    try {
      const data = await CustomerAPI.listConsents();
      if (Array.isArray(data)) {
        setConsents(data);
      }
    } catch (err) {
      console.error("Failed to fetch consents:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchConsents();
  }, [fetchConsents]);

  const handleToggle = async (consentType: string, isCurrentlyActive: boolean) => {
    setActionLoading(consentType);
    try {
      if (isCurrentlyActive) {
        await CustomerAPI.revokeConsent(consentType);
      } else {
        await CustomerAPI.grantConsent(consentType);
      }
      await fetchConsents();
    } catch (err) {
      console.error("Consent action failed:", err);
    } finally {
      setActionLoading(null);
    }
  };

  const statutoryConsents = [
    {
      type: "terms_of_service",
      title: "Terms of Service & Advisory Scope",
      description: "Authorizes PS-21 to provide automated digital insurance recommendations and indicative quotes.",
      isMandatory: true,
    },
    {
      type: "privacy_policy",
      title: "Data Processing & Privacy Policy",
      description: "Consent for collection, storage, and processing of personal identifiers under the DPDP Act 2023.",
      isMandatory: true,
    },
    {
      type: "marketing_contact",
      title: "Advisor Communication & Outreach",
      description: "Permission for assigned licensed insurance advisors to contact you via Phone, WhatsApp, or Email regarding proposal questions.",
      isMandatory: false,
    },
    {
      type: "medical_record_access",
      title: "Medical & Health Records Access",
      description: "Permission for underwriter review of declared medical reports during proposal evaluation.",
      isMandatory: false,
    },
  ];

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <PageHeader
        title="Consent & Privacy Management Center"
        description="Transparent consent controls complying with Indian DPDP Act 2023 and IRDAI regulations."
        breadcrumbs={[
          { label: "Customer Portal", href: "/customer" },
          { label: "Privacy & Consents" },
        ]}
      />

      <Card className="border-blue-100 bg-blue-50/40">
        <CardContent className="p-4 flex items-center gap-3 text-xs text-blue-900">
          <ShieldCheck className="h-5 w-5 text-blue-600 shrink-0" />
          <div>
            <span className="font-semibold">Privacy First Guarantee:</span> Anonymous behavioral footprints are never treated as consent to contact. You maintain complete control to grant or revoke specific processing permissions at any time.
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {statutoryConsents.map((item) => {
          const record = consents.find((c) => c.consent_type === item.type);
          const isActive = record ? record.is_active : false;
          const isActing = actionLoading === item.type;

          return (
            <Card key={item.type} className="border-slate-200 bg-white shadow-2xs">
              <CardContent className="p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="space-y-1 max-w-xl">
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-semibold text-slate-900">{item.title}</h4>
                    {item.isMandatory ? (
                      <Badge variant="outline" className="text-[10px] text-slate-500 bg-slate-50">
                        Mandatory
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-[10px] text-blue-600 border-blue-200 bg-blue-50/50">
                        Optional
                      </Badge>
                    )}
                    {isActive ? (
                      <Badge variant="default" className="text-[10px] bg-emerald-600 text-white">
                        Active
                      </Badge>
                    ) : (
                      <Badge variant="secondary" className="text-[10px] text-slate-500">
                        Inactive / Revoked
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">{item.description}</p>
                  {record && (
                    <div className="text-[11px] text-slate-400 pt-0.5">
                      {record.is_active
                        ? `Granted on ${new Date(record.granted_at).toLocaleDateString()} (v${record.consent_version})`
                        : record.revoked_at
                        ? `Revoked on ${new Date(record.revoked_at).toLocaleDateString()}`
                        : "Not granted"}
                    </div>
                  )}
                </div>

                <div className="shrink-0 flex items-center">
                  {item.isMandatory ? (
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={isActive || isActing}
                      onClick={() => handleToggle(item.type, false)}
                      className="text-xs"
                    >
                      {isActive ? "Mandatory Active" : "Grant Consent"}
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      variant={isActive ? "outline" : "default"}
                      disabled={isActing}
                      onClick={() => handleToggle(item.type, isActive)}
                      className={`text-xs ${
                        isActive
                          ? "border-red-200 text-red-600 hover:bg-red-50"
                          : "bg-blue-600 hover:bg-blue-700 text-white"
                      }`}
                    >
                      {isActing ? (
                        <RefreshCw className="h-3.5 w-3.5 animate-spin mr-1" />
                      ) : isActive ? (
                        "Revoke Permission"
                      ) : (
                        "Grant Permission"
                      )}
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

