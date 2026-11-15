"use client";

import * as React from "react";
import {
  History,
  Shield,
  Search,
  RefreshCw,
  Clock,
  User,
  Calendar,
  CheckCircle2,
  FileText,
  AlertTriangle,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { advisorService } from "@/services/advisor-service";

interface TimelineEvent {
  id: string;
  event_type: string;
  category: string;
  title: string;
  description: string;
  timestamp: string;
  actor: string;
  metadata?: Record<string, any>;
}

export default function AdvisorTimelinePage() {
  const [events, setEvents] = React.useState<TimelineEvent[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [categoryFilter, setCategoryFilter] = React.useState("all");
  const [search, setSearch] = React.useState("");

  const loadTimeline = React.useCallback(async () => {
    try {
      setLoading(true);
      const res = await advisorService.getTimeline();
      setEvents(res);
    } catch (err) {
      console.error("Failed to load timeline events:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadTimeline();
  }, [loadTimeline]);

  const filtered = events.filter((e) => {
    const matchesSearch =
      e.title?.toLowerCase().includes(search.toLowerCase()) ||
      e.description?.toLowerCase().includes(search.toLowerCase()) ||
      e.actor?.toLowerCase().includes(search.toLowerCase());
    const matchesCategory =
      categoryFilter === "all" || e.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <PageHeader
          title="Enterprise Activity Timeline"
          description="Chronological, tamper-evident audit stream of customer submissions, underwriting reviews, document verifications, and employee outreach."
          breadcrumbs={[
            { label: "Advisor Workbench", href: "/advisor" },
            { label: "Activity Timeline" },
          ]}
        />
        <Button
          variant="outline"
          size="sm"
          onClick={loadTimeline}
          disabled={loading}
          className="h-9 gap-1.5 text-xs bg-white border-slate-200 self-start sm:self-auto"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <Tabs value={categoryFilter} onValueChange={setCategoryFilter} className="w-full sm:w-auto">
          <TabsList className="bg-slate-100 p-1 border border-slate-200 text-xs">
            <TabsTrigger value="all" className="text-xs">All Activity</TabsTrigger>
            <TabsTrigger value="audit" className="text-xs">Audit Logs</TabsTrigger>
            <TabsTrigger value="outreach" className="text-xs">Advisor Outreach</TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="relative w-full sm:w-64">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search events or actors..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 h-9 text-xs bg-white border-slate-200"
          />
        </div>
      </div>

      <Card className="bg-white border-slate-200">
        <CardContent className="p-6">
          {loading ? (
            <div className="p-12 text-center text-xs text-slate-400">Loading activity feed...</div>
          ) : filtered.length === 0 ? (
            <div className="p-12 text-center text-xs text-slate-400">
              No activity logs recorded matching criteria.
            </div>
          ) : (
            <div className="relative border-l-2 border-slate-200 ml-4 space-y-6 py-2">
              {filtered.map((evt) => (
                <div key={evt.id} className="relative pl-6">
                  {/* Timeline dot */}
                  <div className="absolute -left-[9px] top-1 h-4 w-4 rounded-full bg-white border-2 border-blue-600 flex items-center justify-center" />

                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-semibold text-xs text-slate-900">{evt.title}</span>
                      <Badge
                        variant="outline"
                        className={
                          evt.category === "audit"
                            ? "bg-slate-50 text-slate-700 border-slate-200 text-[10px]"
                            : "bg-blue-50 text-blue-700 border-blue-200 text-[10px]"
                        }
                      >
                        {evt.category.toUpperCase()}
                      </Badge>
                      <span className="text-[11px] text-slate-400">
                        {evt.timestamp ? new Date(evt.timestamp).toLocaleString() : "—"}
                      </span>
                    </div>

                    <p className="text-xs text-slate-600">{evt.description}</p>

                    <div className="flex items-center gap-2 text-[11px] text-slate-400 pt-0.5">
                      <User className="h-3 w-3" />
                      <span>By {evt.actor}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

