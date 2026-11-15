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
import { CustomerAPI } from "@/services/customer-api";

interface SendQuoteEmailDialogProps {
  quoteId: string;
  quoteNumber: string;
}

export function SendQuoteEmailDialog({ quoteId, quoteNumber }: SendQuoteEmailDialogProps) {
  const [open, setOpen] = React.useState(false);
  const [email, setEmail] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [status, setStatus] = React.useState<"idle" | "success" | "warning" | "error">("idle");
  const [resultMsg, setResultMsg] = React.useState<string | null>(null);

  // Pre-fill email from profile when opened
  React.useEffect(() => {
    if (open) {
      setStatus("idle");
      setResultMsg(null);
      CustomerAPI.getProfile()
        .then((p) => {
          if (p?.email) setEmail(p.email);
        })
        .catch(() => {});
    }
  }, [open]);

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
      const res = await CustomerAPI.sendQuoteEmail(quoteId, email.trim());
      if (res.status === "SENT") {
        setStatus("success");
        setResultMsg(`Quote breakdown was successfully delivered to ${email}. Check your inbox!`);
      } else if (res.status === "NOT_CONFIGURED") {
        setStatus("warning");
        setResultMsg(
          "Notice: SMTP server is currently in unconfigured development mode. Your quote was recorded to delivery logs, but outgoing network delivery requires live SMTP credentials in backend/.env."
        );
      } else {
        setStatus("error");
        setResultMsg(res.message || "Failed to dispatch email. Please check credentials.");
      }
    } catch (err: any) {
      setStatus("error");
      setResultMsg(err?.message || "An unexpected error occurred during dispatch.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          size="sm"
          variant="outline"
          className="w-full text-xs border-slate-200 text-slate-700 hover:bg-slate-50 hover:text-blue-600 h-9"
        >
          <Mail className="h-3.5 w-3.5 mr-1.5 text-blue-600" />
          Email Me This Quote
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md bg-white border-slate-200 p-6">
        <DialogHeader className="space-y-1">
          <DialogTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Mail className="h-4 w-4 text-blue-600" />
            Email Quote Breakdown ({quoteNumber})
          </DialogTitle>
          <DialogDescription className="text-xs text-slate-500">
            Send an official actuarial breakdown of this quotation, including base premium, GST, and riders.
          </DialogDescription>
        </DialogHeader>

        {status === "success" && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 flex items-start gap-2">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600 mt-0.5" />
            <div>
              <p className="font-semibold text-emerald-900">Email Dispatched</p>
              <p className="mt-0.5">{resultMsg}</p>
            </div>
          </div>
        )}

        {status === "warning" && (
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 flex items-start gap-2">
            <AlertCircle className="h-4 w-4 shrink-0 text-amber-600 mt-0.5" />
            <div>
              <p className="font-semibold text-amber-900">Honest Status: Not Configured</p>
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
            <Label className="text-xs font-semibold text-slate-700">Destination Email Address</Label>
            <Input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="customer@example.com"
              className="text-xs bg-white border-slate-300"
            />
            <p className="text-[11px] text-slate-500">
              You can confirm your registered profile email or enter an alternate address to receive this quote.
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
                  Sending via SMTP...
                </>
              ) : (
                <>
                  <Send className="h-3.5 w-3.5 mr-1.5" />
                  Dispatch Quote Email
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

