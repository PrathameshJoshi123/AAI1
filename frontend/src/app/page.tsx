import Link from "next/link";
import { ShieldCheck, User, Users, Scale, ArrowRight, Lock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-white">
      {/* Top Banner */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-xs">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <span className="text-base font-bold tracking-tight text-slate-900">
                PS-21 Insure
              </span>
              <span className="hidden sm:inline-block ml-2 text-xs font-medium text-slate-500">
                Enterprise Acquisition & Onboarding
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm" asChild>
              <Link href="/login">Sign In</Link>
            </Button>
            <Button size="sm" asChild>
              <Link href="/customer">Launch Customer Portal</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <section className="mx-auto max-w-5xl px-4 py-16 sm:px-6 sm:py-24 lg:px-8 text-center">
          <Badge variant="outline" className="mb-4 border-blue-200 bg-blue-50 text-blue-700">
            Phase 1 — Frontend Foundation & Design System
          </Badge>
          <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl">
            Conversational Insurance Acquisition & Onboarding
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-base text-slate-600 leading-relaxed">
            A unified multi-agent financial technology platform connecting prospective policyholders,
            underwriting advisors, and platform administrators through compliant workflows.
          </p>

          {/* Three Portals Grid */}
          <div className="mt-12 grid grid-cols-1 gap-6 sm:grid-cols-3 text-left">
            {/* Customer Portal */}
            <Card className="hover:border-primary/50 transition-all shadow-xs flex flex-col justify-between">
              <CardHeader>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-primary border border-blue-100 mb-3">
                  <User className="h-5 w-5" />
                </div>
                <CardTitle className="text-lg">Customer Portal</CardTitle>
                <CardDescription className="text-xs">
                  Discover policies, converse with the AI assistant, obtain quotes, and track proposals.
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <Button className="w-full" size="sm" asChild>
                  <Link href="/customer">
                    Enter Portal <ArrowRight className="ml-1 h-3.5 w-3.5" />
                  </Link>
                </Button>
              </CardContent>
            </Card>

            {/* Admin Dashboard */}
            <Card className="hover:border-primary/50 transition-all shadow-xs flex flex-col justify-between">
              <CardHeader>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-800 border border-slate-200 mb-3">
                  <Users className="h-5 w-5" />
                </div>
                <CardTitle className="text-lg">Admin & Owner</CardTitle>
                <CardDescription className="text-xs">
                  Lead pipeline monitoring, AI agent configuration, product rules, and compliance audit logs.
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <Button variant="outline" className="w-full" size="sm" asChild>
                  <Link href="/admin">
                    Enter Dashboard <ArrowRight className="ml-1 h-3.5 w-3.5" />
                  </Link>
                </Button>
              </CardContent>
            </Card>

            {/* Advisor Workbench */}
            <Card className="hover:border-primary/50 transition-all shadow-xs flex flex-col justify-between">
              <CardHeader>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-100 mb-3">
                  <Scale className="h-5 w-5" />
                </div>
                <CardTitle className="text-lg">Advisor Workbench</CardTitle>
                <CardDescription className="text-xs">
                  Human-in-the-loop review queue for escalated risk cases, document audits, and decisions.
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <Button variant="outline" className="w-full" size="sm" asChild>
                  <Link href="/advisor">
                    Enter Workbench <ArrowRight className="ml-1 h-3.5 w-3.5" />
                  </Link>
                </Button>
              </CardContent>
            </Card>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-slate-50 py-6 text-center text-xs text-slate-500">
        <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>PS-21 Insurance Acquisition & Onboarding Platform</span>
          <span className="flex items-center gap-1.5">
            <Lock className="h-3 w-3 text-slate-400" /> Compliant with Insurance Regulatory Frameworks
          </span>
        </div>
      </footer>
    </div>
  );
}
