"use client";

import * as React from "react";
import { User, CheckCircle2, ShieldCheck, Save, AlertCircle } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { CustomerAPI } from "@/services/customer-api";
import { CustomerProfile } from "@/types/customer";
import { EmailProvisionCard } from "@/components/customer/EmailProvisionCard";
import { NotificationPreferencesCard } from "@/components/customer/NotificationPreferencesCard";


export default function CustomerProfilePage() {
  const [profile, setProfile] = React.useState<CustomerProfile | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [saving, setSaving] = React.useState<boolean>(false);
  const [successMsg, setSuccessMsg] = React.useState<string | null>(null);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);

  React.useEffect(() => {
    async function load() {
      try {
        const data = await CustomerAPI.getProfile();
        setProfile(data);
      } catch (err) {
        console.error("Profile load error:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile) return;
    setSaving(true);
    setSuccessMsg(null);
    setErrorMsg(null);

    try {
      const updated = await CustomerAPI.updateProfile({
        first_name: profile.first_name,
        last_name: profile.last_name,
        phone: profile.phone || undefined,
        occupation: profile.occupation || undefined,
        annual_income: profile.annual_income || undefined,
        city: profile.city || undefined,
        pincode: profile.pincode || undefined,
        state: profile.state || undefined,
        gender: profile.gender || undefined,
        tobacco_user: profile.tobacco_user,
        preferred_language: profile.preferred_language,
      });
      setProfile(updated);
      setSuccessMsg("Profile and preferences saved successfully.");
    } catch (err: any) {
      setErrorMsg(err?.message || "Failed to save profile. Please check entries.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <PageHeader
        title="Customer Profile & Preferences"
        description="Manage your personal information, residential details, and communication settings."
        breadcrumbs={[
          { label: "Customer Portal", href: "/customer" },
          { label: "Profile" },
        ]}
      />

      {successMsg && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600" />
          <span>{successMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {profile && (
        <form onSubmit={handleSave} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Identity Card */}
            <Card className="border-slate-200 bg-white shadow-2xs">
              <CardHeader className="p-5 pb-3">
                <CardTitle className="text-base font-semibold text-slate-900 flex items-center gap-2">
                  <User className="h-4 w-4 text-blue-600" />
                  Legal Identity
                </CardTitle>
                <CardDescription className="text-xs text-slate-500">
                  Primary identification details linked to your insurance policies.
                </CardDescription>
              </CardHeader>
              <CardContent className="p-5 pt-0 space-y-3.5">
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <Label className="text-xs font-semibold text-slate-700">First Name</Label>
                    <Input
                      value={profile.first_name}
                      onChange={(e) => setProfile({ ...profile, first_name: e.target.value })}
                      className="text-xs bg-white"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label className="text-xs font-semibold text-slate-700">Last Name</Label>
                    <Input
                      value={profile.last_name}
                      onChange={(e) => setProfile({ ...profile, last_name: e.target.value })}
                      className="text-xs bg-white"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <Label className="text-xs font-semibold text-slate-700">Official Email</Label>
                    <span className="text-[10px] text-blue-600 font-medium">Editable via Provisioning Card</span>
                  </div>
                  <Input value={profile.email} readOnly className="text-xs bg-slate-50 text-slate-700 font-medium" />
                </div>


                <div className="space-y-1.5">
                  <Label className="text-xs font-semibold text-slate-700">Phone Number</Label>
                  <Input
                    value={profile.phone || ""}
                    placeholder="+91 98765 43210"
                    onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                    className="text-xs bg-white"
                  />
                </div>

                <div className="space-y-1.5">
                  <Label className="text-xs font-semibold text-slate-700">Gender</Label>
                  <Select
                    value={profile.gender || "male"}
                    onValueChange={(val) => setProfile({ ...profile, gender: val })}
                  >
                    <SelectTrigger className="text-xs bg-white">
                      <SelectValue placeholder="Select gender" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="male">Male</SelectItem>
                      <SelectItem value="female">Female</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Financial & Address Card */}
            <Card className="border-slate-200 bg-white shadow-2xs">
              <CardHeader className="p-5 pb-3">
                <CardTitle className="text-base font-semibold text-slate-900 flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-emerald-600" />
                  Address & Financial Capacity
                </CardTitle>
                <CardDescription className="text-xs text-slate-500">
                  Required for policy underwriting risk tier determination.
                </CardDescription>
              </CardHeader>
              <CardContent className="p-5 pt-0 space-y-3.5">
                <div className="space-y-1.5">
                  <Label className="text-xs font-semibold text-slate-700">Profession / Occupation</Label>
                  <Input
                    value={profile.occupation || ""}
                    placeholder="e.g. Salaried, Self-Employed"
                    onChange={(e) => setProfile({ ...profile, occupation: e.target.value })}
                    className="text-xs bg-white"
                  />
                </div>

                <div className="space-y-1.5">
                  <Label className="text-xs font-semibold text-slate-700">Annual Gross Income (₹ INR)</Label>
                  <Input
                    type="number"
                    step="50000"
                    value={profile.annual_income || 0}
                    onChange={(e) => setProfile({ ...profile, annual_income: parseFloat(e.target.value) || 0 })}
                    className="text-xs bg-white"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <Label className="text-xs font-semibold text-slate-700">City</Label>
                    <Input
                      value={profile.city || ""}
                      placeholder="e.g. Mumbai, Pune"
                      onChange={(e) => setProfile({ ...profile, city: e.target.value })}
                      className="text-xs bg-white"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label className="text-xs font-semibold text-slate-700">Pincode</Label>
                    <Input
                      value={profile.pincode || ""}
                      placeholder="e.g. 400001"
                      onChange={(e) => setProfile({ ...profile, pincode: e.target.value })}
                      className="text-xs bg-white"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <Label className="text-xs font-semibold text-slate-700">Preferred Language</Label>
                  <Select
                    value={profile.preferred_language || "en"}
                    onValueChange={(val) => setProfile({ ...profile, preferred_language: val })}
                  >
                    <SelectTrigger className="text-xs bg-white">
                      <SelectValue placeholder="Select language" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="hi">हिंदी (Hindi)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="flex justify-end gap-3">
            <Button
              type="submit"
              disabled={saving}
              className="text-xs bg-blue-600 hover:bg-blue-700 text-white px-5"
            >
              <Save className="h-4 w-4 mr-1.5" />
              {saving ? "Saving Changes..." : "Save Profile & Preferences"}
            </Button>
          </div>
        </form>
      )}

      {/* Phase 11: Email Notification Provisioning & Granular Preferences */}
      {profile && (
        <div className="space-y-6 pt-4 border-t border-slate-200">
          <div>
            <h3 className="text-base font-bold text-slate-900">Communication & Notification Controls</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Provision your official delivery email and control automated quote, application, and document notifications.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <EmailProvisionCard
              currentEmail={profile.email}
              onEmailUpdated={(newEmail) => setProfile({ ...profile, email: newEmail })}
            />
            <NotificationPreferencesCard />
          </div>
        </div>
      )}
    </div>
  );
}

