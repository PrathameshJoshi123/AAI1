"use client";

import * as React from "react";
import {
  MessageSquare,
  Search,
  User,
  Bot,
  Clock,
  Sparkles,
  RefreshCw,
  ArrowRight,
  ShieldCheck,
  Tag,
  AlertCircle,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { advisorService } from "@/services/advisor-service";
import { MarkdownRenderer } from "@/components/shared/markdown-renderer";

interface ConvItem {
  id: string;
  customer_id: string;
  customer_name: string;
  customer_email: string;
  title: string;
  status: string;
  mode: string;
  channel: string;
  message_count: number;
  last_message: string;
  last_turn_at: string;
}

export default function AdvisorConversationsPage() {
  const [conversations, setConversations] = React.useState<ConvItem[]>([]);
  const [selectedId, setSelectedId] = React.useState<string | null>(null);
  const [selectedThread, setSelectedThread] = React.useState<any | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [loadingThread, setLoadingThread] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState("");

  const loadConversations = React.useCallback(async () => {
    try {
      setLoading(true);
      const res = await advisorService.getConversations();
      setConversations(res);
      if (res.length > 0 && !selectedId) {
        setSelectedId(res[0].id);
      }
    } catch (err) {
      console.error("Failed to load conversations:", err);
    } finally {
      setLoading(false);
    }
  }, [selectedId]);

  React.useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  React.useEffect(() => {
    if (!selectedId) return;
    const fetchThread = async () => {
      try {
        setLoadingThread(true);
        const data = await advisorService.getConversation(selectedId);
        setSelectedThread(data);
      } catch (err) {
        console.error("Failed to load thread:", err);
      } finally {
        setLoadingThread(false);
      }
    };
    fetchThread();
  }, [selectedId]);

  const filtered = conversations.filter(
    (c) =>
      c.customer_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.customer_email?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <PageHeader
          title="Customer Conversations"
          description="Inspect live AI consultation transcripts, extracted needs assessments, and advisor recommendations."
          breadcrumbs={[
            { label: "Advisor Workbench", href: "/advisor" },
            { label: "Conversations" },
          ]}
        />
        <Button
          variant="outline"
          size="sm"
          onClick={loadConversations}
          disabled={loading}
          className="h-9 gap-1.5 text-xs bg-white border-slate-200 self-start sm:self-auto"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[700px]">
        {/* Left column: Conversation list */}
        <div className="lg:col-span-4 flex flex-col h-full bg-white border border-slate-200 rounded-lg overflow-hidden">
          <div className="p-3 border-b border-slate-100 bg-slate-50/50">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search by customer name or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 h-9 text-xs bg-white border-slate-200"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
            {filtered.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">
                {loading ? "Loading conversations..." : "No conversation records found."}
              </div>
            ) : (
              filtered.map((c) => {
                const isSelected = c.id === selectedId;
                return (
                  <button
                    key={c.id}
                    onClick={() => setSelectedId(c.id)}
                    className={`w-full text-left p-3.5 transition-colors flex flex-col gap-1.5 ${
                      isSelected ? "bg-blue-50/70 border-l-4 border-blue-600" : "hover:bg-slate-50"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-xs text-slate-900 truncate">
                        {c.customer_name}
                      </span>
                      <span className="text-[10px] text-slate-400">
                        {new Date(c.last_turn_at).toLocaleDateString("en-IN", {
                          month: "short",
                          day: "numeric",
                        })}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 line-clamp-1">{c.last_message}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline" className="text-[10px] py-0 px-1.5 font-normal bg-white border-slate-200 text-slate-600">
                        {c.message_count} msgs
                      </Badge>
                      <Badge variant="outline" className="text-[10px] py-0 px-1.5 font-normal bg-blue-50 text-blue-700 border-blue-200">
                        {c.mode.replace("_", " ")}
                      </Badge>
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>

        {/* Right column: Multi-turn chat transcript */}
        <div className="lg:col-span-8 flex flex-col h-full bg-white border border-slate-200 rounded-lg overflow-hidden">
          {selectedThread ? (
            <>
              {/* Header */}
              <div className="p-4 border-b border-slate-200 bg-white flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-sm text-slate-900">{selectedThread.title}</h3>
                  <div className="flex items-center gap-2 text-xs text-slate-500 mt-0.5">
                    <span>Session ID: {selectedThread.id.slice(0, 8)}...</span>
                    <span>•</span>
                    <span>Status: {selectedThread.status}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200 text-xs">
                    <ShieldCheck className="h-3 w-3 mr-1" />
                    Mistral AI Logged
                  </Badge>
                </div>
              </div>

              {/* Message History */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/40">
                {selectedThread.messages?.length === 0 ? (
                  <div className="p-12 text-center text-xs text-slate-400">
                    No transcript entries recorded for this thread.
                  </div>
                ) : (
                  selectedThread.messages.map((m: any) => {
                    const isBot = m.sender_type !== "user";
                    return (
                      <div
                        key={m.id}
                        className={`flex gap-3 max-w-[85%] ${
                          isBot ? "mr-auto" : "ml-auto flex-row-reverse"
                        }`}
                      >
                        <div
                          className={`h-7 w-7 rounded-full flex items-center justify-center shrink-0 text-xs font-semibold ${
                            isBot
                              ? "bg-blue-600 text-white shadow-xs"
                              : "bg-slate-200 text-slate-700"
                          }`}
                        >
                          {isBot ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                        </div>
                        <div className="space-y-1">
                          <div
                            className={`p-3.5 rounded-lg text-xs leading-relaxed ${
                              isBot
                                ? "bg-white border border-slate-200 text-slate-800 shadow-2xs"
                                : "bg-blue-600 text-white shadow-xs"
                            }`}
                          >
                            <MarkdownRenderer content={m.content} />
                          </div>
                          <div
                            className={`flex items-center gap-1.5 text-[10px] text-slate-400 ${
                              isBot ? "justify-start" : "justify-end"
                            }`}
                          >
                            <span>{m.sender_name}</span>
                            <span>•</span>
                            <span>{new Date(m.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>

              {/* Footer Notice */}
              <div className="p-3 border-t border-slate-200 bg-white text-[11px] text-slate-500 flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <Sparkles className="h-3.5 w-3.5 text-blue-600" />
                  <span>AI Advisor conversations are auditable under IRDAI digital communication compliance.</span>
                </div>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center p-8">
              <MessageSquare className="h-10 w-10 text-slate-300 mb-2" />
              <p className="text-sm font-semibold text-slate-700">Select a Conversation</p>
              <p className="text-xs text-slate-400 mt-1">
                Choose a customer thread from the left panel to inspect the multi-turn AI consultation.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

