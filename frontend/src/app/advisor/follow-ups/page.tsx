"use client";

import * as React from "react";
import {
  CalendarClock,
  Phone,
  Mail,
  MessageSquare,
  Users,
  Plus,
  CheckCircle2,
  Clock,
  Search,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { advisorService } from "@/services/advisor-service";
import { FollowUpItem } from "@/types/advisor";

export default function AdvisorFollowUpsPage() {
  const [items, setItems] = React.useState<FollowUpItem[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [statusFilter, setStatusFilter] = React.useState("pending");
  const [search, setSearch] = React.useState("");

  // Create Modal State
  const [createOpen, setCreateOpen] = React.useState(false);
  const [newChannel, setNewChannel] = React.useState("phone");
  const [newPriority, setNewPriority] = React.useState("medium");
  const [newDueDate, setNewDueDate] = React.useState("");
  const [newNotes, setNewNotes] = React.useState("");
  const [creating, setCreating] = React.useState(false);

  // Complete Modal State
  const [completeItem, setCompleteItem] = React.useState<FollowUpItem | null>(null);
  const [outcomeNotes, setOutcomeNotes] = React.useState("");
  const [updating, setUpdating] = React.useState(false);

  const loadFollowUps = React.useCallback(async () => {
    try {
      setLoading(true);
      const res = await advisorService.getFollowUps(statusFilter === "all" ? undefined : statusFilter);
      setItems(res);
    } catch (err) {
      console.error("Failed to load follow-ups:", err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  React.useEffect(() => {
    loadFollowUps();
  }, [loadFollowUps]);

  const handleCreate = async () => {
    if (!newDueDate) return;
    try {
      setCreating(true);
      await advisorService.createFollowUp({
        channel: newChannel,
        priority: newPriority,
        due_date: new Date(newDueDate).toISOString(),
        notes: newNotes,
      });
      setCreateOpen(false);
      setNewDueDate("");
      setNewNotes("");
      await loadFollowUps();
    } catch (err: any) {
      alert(err?.message || "Failed to schedule follow-up.");
    } finally {
      setCreating(false);
    }
  };

  const handleComplete = async () => {
    if (!completeItem) return;
    try {
      setUpdating(true);
      await advisorService.updateFollowUpStatus(completeItem.id, {
        status: "completed",
        notes: outcomeNotes ? `${completeItem.notes || ""}\nOutcome: ${outcomeNotes}` : completeItem.notes || "",
      });
      setCompleteItem(null);
      setOutcomeNotes("");
      await loadFollowUps();
    } catch (err: any) {
      alert(err?.message || "Failed to complete follow-up.");
    } finally {
      setUpdating(false);
    }
  };

  const filtered = items.filter(
    (i) =>
      i.target_name?.toLowerCase().includes(search.toLowerCase()) ||
      i.notes?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <PageHeader
          title="Customer Follow-up Management"
          description="Schedule and track customer engagement calls, emails, verification queries, and quote review follow-ups."
          breadcrumbs={[
            { label: "Advisor Workbench", href: "/advisor" },
            { label: "Follow-ups" },
          ]}
        />
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <Button
            variant="outline"
            size="sm"
            onClick={loadFollowUps}
            disabled={loading}
            className="h-9 gap-1.5 text-xs bg-white border-slate-200"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>

          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger asChild>
              <Button size="sm" className="h-9 gap-1.5 text-xs bg-blue-600 hover:bg-blue-700 text-white">
                <Plus className="h-3.5 w-3.5" />
                Schedule Follow-up
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md bg-white border-slate-200">
              <DialogHeader>
                <DialogTitle className="text-base font-bold text-slate-900">
                  Schedule Customer Engagement
                </DialogTitle>
                <DialogDescription className="text-xs text-slate-500">
                  Plan customer outreach for proposal questions, missing KYC documents, or quotation review.
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-3 py-2 text-xs">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Channel *</label>
                  <Select value={newChannel} onValueChange={setNewChannel}>
                    <SelectTrigger className="h-9 text-xs bg-white border-slate-200">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="phone">Phone Call</SelectItem>
                      <SelectItem value="email">Email Follow-up</SelectItem>
                      <SelectItem value="meeting">Video Consultation</SelectItem>
                      <SelectItem value="chat">Portal Chat</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Priority</label>
                  <Select value={newPriority} onValueChange={setNewPriority}>
                    <SelectTrigger className="h-9 text-xs bg-white border-slate-200">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="high">High Priority</SelectItem>
                      <SelectItem value="medium">Medium Priority</SelectItem>
                      <SelectItem value="low">Low Priority</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Due Date & Time *</label>
                  <Input
                    type="datetime-local"
                    value={newDueDate}
                    onChange={(e) => setNewDueDate(e.target.value)}
                    className="h-9 text-xs bg-white border-slate-200"
                  />
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Agenda / Objective *</label>
                  <Textarea
                    rows={3}
                    value={newNotes}
                    onChange={(e) => setNewNotes(e.target.value)}
                    placeholder="e.g. Call customer to verify declared medical history and nominee PAN..."
                    className="text-xs bg-white border-slate-200"
                  />
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" size="sm" onClick={() => setCreateOpen(false)} className="text-xs">
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={handleCreate}
                  disabled={creating || !newDueDate}
                  className="text-xs bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {creating ? "Scheduling..." : "Schedule Task"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <Tabs value={statusFilter} onValueChange={setStatusFilter} className="w-full sm:w-auto">
          <TabsList className="bg-slate-100 p-1 border border-slate-200 text-xs">
            <TabsTrigger value="pending" className="text-xs">Upcoming Agenda</TabsTrigger>
            <TabsTrigger value="completed" className="text-xs">Completed</TabsTrigger>
            <TabsTrigger value="all" className="text-xs">All Tasks</TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="relative w-full sm:w-64">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search tasks..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 h-9 text-xs bg-white border-slate-200"
          />
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading follow-ups...</div>
      ) : filtered.length === 0 ? (
        <Card className="bg-white border-slate-200">
          <CardContent className="flex flex-col items-center justify-center p-12 text-center">
            <CalendarClock className="h-10 w-10 text-slate-300 mb-2" />
            <p className="text-sm font-semibold text-slate-800">No Follow-ups Found</p>
            <p className="text-xs text-slate-400 max-w-sm mt-1">
              Your engagement agenda is clear for the selected category.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {filtered.map((item) => (
            <Card key={item.id} className="bg-white border-slate-200 hover:border-slate-300 transition-colors">
              <CardContent className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div className="h-9 w-9 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                    {item.channel === "phone" ? (
                      <Phone className="h-4 w-4" />
                    ) : item.channel === "email" ? (
                      <Mail className="h-4 w-4" />
                    ) : (
                      <MessageSquare className="h-4 w-4" />
                    )}
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-xs text-slate-900">
                        {item.target_name || "Assigned Customer / Prospect"}
                      </span>
                      <Badge
                        variant="outline"
                        className={
                          item.priority === "high"
                            ? "bg-red-50 text-red-700 border-red-200 text-[10px]"
                            : "bg-blue-50 text-blue-700 border-blue-200 text-[10px]"
                        }
                      >
                        {item.priority.toUpperCase()}
                      </Badge>
                      <Badge variant="outline" className="text-[10px] bg-slate-50 border-slate-200">
                        {item.channel.toUpperCase()}
                      </Badge>
                    </div>
                    <p className="text-xs text-slate-600">{item.notes || "No notes provided."}</p>
                    <div className="flex items-center gap-2 text-[11px] text-slate-400">
                      <Clock className="h-3 w-3" />
                      <span>Due: {new Date(item.due_date).toLocaleString()}</span>
                      {item.target_contact && (
                        <>
                          <span>•</span>
                          <span>Contact: {item.target_contact}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-auto shrink-0">
                  {item.status === "pending" && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setCompleteItem(item)}
                      className="text-xs h-8 text-emerald-600 border-emerald-200 hover:bg-emerald-50"
                    >
                      <CheckCircle2 className="h-3.5 w-3.5 mr-1" /> Mark Complete
                    </Button>
                  )}
                  {item.status === "completed" && (
                    <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200 text-xs">
                      Completed
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Complete Task Dialog */}
      {completeItem && (
        <Dialog open={!!completeItem} onOpenChange={() => setCompleteItem(null)}>
          <DialogContent className="max-w-md bg-white border-slate-200">
            <DialogHeader>
              <DialogTitle className="text-base font-bold text-slate-900">
                Complete Follow-up Task
              </DialogTitle>
              <DialogDescription className="text-xs text-slate-500">
                Record outcome summary for this engagement with {completeItem.target_name || "the applicant"}.
              </DialogDescription>
            </DialogHeader>

            <div className="py-2">
              <label className="text-xs font-semibold text-slate-700 block mb-1">
                Outcome Summary *
              </label>
              <Textarea
                rows={3}
                value={outcomeNotes}
                onChange={(e) => setOutcomeNotes(e.target.value)}
                placeholder="e.g. Applicant confirmed KYC replacement will be uploaded today..."
                className="text-xs bg-white border-slate-200"
              />
            </div>

            <DialogFooter>
              <Button variant="outline" size="sm" onClick={() => setCompleteItem(null)} className="text-xs">
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={handleComplete}
                disabled={updating}
                className="text-xs bg-emerald-600 hover:bg-emerald-700 text-white"
              >
                {updating ? "Saving..." : "Confirm Completed"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}

