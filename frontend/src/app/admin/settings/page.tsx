"use client";

import React, { useEffect, useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { AdminAPI } from "@/services/admin.service";
import { SystemSetting } from "@/types/admin";
import { RefreshCw, Save, Sliders, AlertCircle, CheckCircle2 } from "lucide-react";

export default function AdminSettingsPage() {
  const [settingsList, setSettingsList] = useState<SystemSetting[]>([]);
  const [editedValues, setEditedValues] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [savingKey, setSavingKey] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadSettings = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await AdminAPI.listSettings();
      setSettingsList(data);
      const initialMap: Record<string, string> = {};
      data.forEach((s) => {
        initialMap[s.key] = JSON.stringify(s.value_json, null, 2);
      });
      setEditedValues(initialMap);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load platform settings.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleSave = async (key: string) => {
    try {
      setSavingKey(key);
      setError(null);
      setSuccessMessage(null);
      const parsed = JSON.parse(editedValues[key]);
      await AdminAPI.updateSetting(key, parsed);
      setSuccessMessage(`Setting '${key}' updated successfully.`);
      await loadSettings();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(`Failed to save ${key}: ${err.message}`);
      } else {
        setError(`Failed to save ${key}. Invalid JSON.`);
      }
    } finally {
      setSavingKey(null);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dynamic Platform Settings & Operational Policies"
        description="Configure underwriting SLA timers, lead assignment algorithms, and statutory compliance parameters."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Settings" },
        ]}
        actions={
          <Button variant="outline" size="sm" onClick={loadSettings} disabled={isLoading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        }
      />

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg text-sm text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {successMessage && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-700 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          {successMessage}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-64 rounded-lg bg-slate-100" />
          ))
        ) : settingsList.length === 0 ? (
          <div className="col-span-2 p-12 text-center text-slate-400">
            No system settings loaded.
          </div>
        ) : (
          settingsList.map((setting) => (
            <Card key={setting.key} className="bg-white border-slate-200 shadow-sm flex flex-col justify-between">
              <CardHeader className="pb-3 border-b border-slate-100">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-bold text-slate-900 font-mono">
                    {setting.key}
                  </CardTitle>
                  <Sliders className="w-4 h-4 text-blue-600" />
                </div>
                <CardDescription className="text-xs text-slate-500">
                  {setting.description || "Dynamic platform runtime configuration."}
                </CardDescription>
              </CardHeader>

              <CardContent className="p-4 space-y-3">
                <div className="space-y-1">
                  <Label className="text-[11px] font-semibold uppercase text-slate-400">
                    Configuration Payload (JSON)
                  </Label>
                  <textarea
                    rows={6}
                    value={editedValues[setting.key] || ""}
                    onChange={(e) =>
                      setEditedValues((prev) => ({ ...prev, [setting.key]: e.target.value }))
                    }
                    className="w-full p-2.5 font-mono text-xs bg-slate-50 border border-slate-200 rounded-md text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-600"
                  />
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-[11px] text-slate-400">
                  <span>Updated: {new Date(setting.updated_at).toLocaleDateString()}</span>
                  <Button
                    size="sm"
                    className="h-8 bg-blue-600 hover:bg-blue-700 text-white text-xs"
                    onClick={() => handleSave(setting.key)}
                    disabled={savingKey === setting.key}
                  >
                    <Save className="w-3.5 h-3.5 mr-1.5" />
                    {savingKey === setting.key ? "Saving..." : "Save Config"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
