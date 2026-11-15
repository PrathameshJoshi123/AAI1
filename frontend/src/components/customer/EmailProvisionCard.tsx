"use client";

import * as React from "react";
import { Mail, CheckCircle2, Edit2, AlertCircle, Loader2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { CustomerAPI } from "@/services/customer-api";

interface EmailProvisionCardProps {
  currentEmail: string;
  onEmailUpdated?: (newEmail: string) => void;
}

export function EmailProvisionCard({ currentEmail, onEmailUpdated }: EmailProvisionCardProps) {
  const [email, setEmail] = React.useState(currentEmail);
  const [isEditing, setIsEditing] = React.useState(false);
  const [newEmail, setNewEmail] = React.useState(currentEmail);
  const [loading, setLoading] = React.useState(false);
  const [successMsg, setSuccessMsg] = React.useState<string | null>(null);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);

  React.useEffect(() => {
    setEmail(currentEmail);
    setNewEmail(currentEmail);
  }, [currentEmail]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmail || !newEmail.includes("@")) {
      setErrorMsg("Please enter a valid email address.");
      return;
    }
    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      const res = await CustomerAPI.updateEmail(newEmail.trim());
      setEmail(res.email);
      setIsEditing(false);
      setSuccessMsg(`Email updated successfully to ${res.email}. Official notifications will be routed here.`);
      if (onEmailUpdated) {
        onEmailUpdated(res.email);
      }
    } catch (err: any) {
      setErrorMsg(err?.message || "Failed to update email address. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="border-slate-200 bg-white shadow-2xs">
      <CardHeader className="p-5 pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold text-slate-900 flex items-center gap-2">
            <Mail className="h-4 w-4 text-blue-600" />
            Official Notification Email
          </CardTitle>
          <Badge variant="outline" className="text-xs bg-emerald-50 text-emerald-700 border-emerald-200 font-medium">
            <CheckCircle2 className="h-3 w-3 mr-1 text-emerald-600" />
            Active Delivery Address
          </Badge>
        </div>
        <CardDescription className="text-xs text-slate-500">
          This email receives your policy documents, actuarial quote breakdowns, underwriting decisions, and verification alerts.
        </CardDescription>
      </CardHeader>
      <CardContent className="p-5 pt-0 space-y-4">
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

        {!isEditing ? (
          <div className="flex items-center justify-between p-3.5 bg-slate-50 border border-slate-200 rounded-lg">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Current Delivery Email</p>
              <p className="text-sm font-bold text-slate-900 mt-0.5">{email || "No email registered"}</p>
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setIsEditing(true)}
              className="text-xs bg-white hover:bg-slate-50 border-slate-200 text-slate-700"
            >
              <Edit2 className="h-3.5 w-3.5 mr-1 text-slate-500" />
              Change Email
            </Button>
          </div>
        ) : (
          <form onSubmit={handleUpdate} className="p-4 bg-blue-50/40 border border-blue-200 rounded-lg space-y-3">
            <div className="space-y-1.5">
              <Label className="text-xs font-semibold text-slate-800">New Notification Email Address</Label>
              <Input
                type="email"
                required
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                placeholder="name@example.com"
                className="text-xs bg-white border-slate-300"
              />
              <p className="text-[11px] text-slate-500">
                Updating your email address updates both your login identity and all system notification delivery logs.
              </p>
            </div>
            <div className="flex items-center gap-2 pt-1">
              <Button
                type="submit"
                disabled={loading}
                size="sm"
                className="text-xs bg-blue-600 hover:bg-blue-700 text-white"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                    Updating Email...
                  </>
                ) : (
                  "Confirm & Save Email"
                )}
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                disabled={loading}
                onClick={() => {
                  setNewEmail(email);
                  setIsEditing(false);
                  setErrorMsg(null);
                }}
                className="text-xs text-slate-600"
              >
                Cancel
              </Button>
            </div>
          </form>
        )}
      </CardContent>
    </Card>
  );
}

