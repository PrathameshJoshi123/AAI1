"use client";

import * as React from "react";
import { Mail, Send, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AdminAPI } from "@/services/admin.service";

interface SendTestEmailModalProps {
  onDispatched?: () => void;
}

export function SendTestEmailModal({ onDispatched }: SendTestEmailModalProps) {
  const [open, setOpen] = React.useState(false);
  const [email, setEmail] = React.useState("admin@ps21-insurance.com");
  const [loading, setLoading] = React.useState(false);
  const [status, setStatus] = React.useState<"idle" | "success" | "warning" | "error">("idle");
  const [resultMsg, setResultMsg] = React.useState<string | null>(null);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !email.includes("@")) {
      setStatus("error");
      setResultMsg("Please provide a valid recipient email address.");
      return;
    }

    setLoading(true);
    setStatus("idle");
    setResultMsg(null);

    try {
      const res = await AdminAPI.sendTestEmail(email.trim());
      if (res.status === "SENT") {
        setStatus("success");
        setResultMsg(`SMTP handshake successful! Diagnostic probe message delivered to ${email}.`);
      } else if (res.status === "NOT_CONFIGURED") {
        setStatus("warning");
        setResultMsg(
          "Honest Status: SMTP_HOST or credentials are placeholder in backend/.env. The delivery log was recorded, but network dispatch requires live SMTP credentials."
        );
      } else {
        setStatus("error");
        setResultMsg(res.message || "Failed to transmit test email.");
      }
      if (onDispatched) onDispatched();
    } catch (err: any) {
      setStatus("error");
      setResultMsg(err?.message || "An error occurred while connecting to SMTP host.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" className="text-xs bg-blue-600 hover:bg-blue-700 text-white">
          <Mail className="h-3.5 w-3.5 mr-1.5" />
          Send Test Probe Email
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md bg-white border-slate-200 p-6">
        <DialogHeader className="space-y-1">
          <DialogTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Mail className="h-4 w-4 text-blue-600" />
            Live SMTP Diagnostic Probe
          </DialogTitle>
          <DialogDescription className="text-xs text-slate-500">
            Dispatch an official diagnostic test email to verify SMTP host, port handshake, and TLS negotiation.
          </DialogDescription>
        </DialogHeader>

        {status === "success" && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 flex items-start gap-2">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600 mt-0.5" />
            <div>
              <p className="font-semibold text-emerald-900">Probe Completed</p>
              <p className="mt-0.5">{resultMsg}</p>
            </div>
          </div>
        )}

        {status === "warning" && (
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 flex items-start gap-2">
            <AlertCircle className="h-4 w-4 shrink-0 text-amber-600 mt-0.5" />
            <div>
              <p className="font-semibold text-amber-900">Unconfigured Development Mode</p>
              <p className="mt-0.5">{resultMsg}</p>
            </div>
          </div>
        )}

        {status === "error" && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-start gap-2">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
            <span>{resultMsg}</span>
          </div>
        )}

        <form onSubmit={handleSend} className="space-y-4 pt-2">
          <div className="space-y-1.5">
            <Label className="text-xs font-semibold text-slate-700">Probe Recipient Email Address</Label>
            <Input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@example.com"
              className="text-xs bg-white border-slate-300"
            />
            <p className="text-[11px] text-slate-500">
              The test email contains connection latency, TLS status, and server handshake timestamps.
            </p>
          </div>

          <DialogFooter className="gap-2 sm:gap-0 pt-2">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setOpen(false)}
              className="text-xs text-slate-600"
            >
              Close
            </Button>
            <Button
              type="submit"
              disabled={loading}
              size="sm"
              className="text-xs bg-blue-600 hover:bg-blue-700 text-white"
            >
              {loading ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                  Testing Socket & Dispatching...
                </>
              ) : (
                <>
                  <Send className="h-3.5 w-3.5 mr-1.5" />
                  Send Probe Email
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

