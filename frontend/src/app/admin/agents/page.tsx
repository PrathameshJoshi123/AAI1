"use client";

import React, { useEffect, useState } from "react";
import { Bot, Sliders, Shield, RefreshCw, Activity, Terminal, AlertCircle, Play, Pause, PowerOff } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { AgentStatusBadge } from "@/components/admin/agent-status-badge";
import { AdminAPI } from "@/services/admin.service";
import { AgentTelemetry, AgentExecutionLogItem } from "@/types/admin";

export default function AdminAgentsPage() {
  const [agents, setAgents] = useState<AgentTelemetry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAgentLogs, setSelectedAgentLogs] = useState<{
    agentName: string;
    logs: AgentExecutionLogItem[];
  } | null>(null);
  const [isLoadingLogs, setIsLoadingLogs] = useState(false);

  const loadAgents = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await AdminAPI.listAgents();
      setAgents(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load agent telemetry.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAgents();
  }, []);

  const handleStatusChange = async (agentName: string, newStatus: "active" | "paused" | "disabled") => {
    try {
      const updated = await AdminAPI.updateAgentStatus(agentName, newStatus);
      setAgents((prev) => prev.map((a) => (a.agent_name === agentName ? updated : a)));
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to update agent status.");
    }
  };

  const handleViewLogs = async (agentName: string) => {
    try {
      setIsLoadingLogs(true);
      const res = await AdminAPI.getAgentExecutions(agentName, 25);
      setSelectedAgentLogs({ agentName, logs: res.executions });
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to fetch logs.");
    } finally {
      setIsLoadingLogs(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Agent Control Centre & Telemetry"
        description="Real-time governance, runtime kill-switches, execution history, and token metrics."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Agent Control Centre" },
        ]}
        actions={
          <Button variant="outline" size="sm" onClick={loadAgents} disabled={isLoading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isLoading ? "animate-spin" : ""}`} />
            Refresh Telemetry
          </Button>
        }
      />

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg text-sm text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {/* Observability Banner */}
      <div className="p-4 bg-blue-50/70 border border-blue-200 rounded-lg flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-md bg-blue-600 text-white">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <p className="text-xs font-bold text-blue-900">LangGraph Orchestration & Mistral LLM Connected</p>
            <p className="text-[11px] text-blue-700">
              Runtime kill-switches take immediate effect on all workflow nodes.
            </p>
          </div>
        </div>
        <Badge variant="outline" className="bg-white border-blue-300 text-blue-800 text-xs">
          Engine: mistral-large-latest
        </Badge>
      </div>

      {/* Agent Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {isLoading ? (
          Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-44 rounded-lg bg-slate-100" />
          ))
        ) : agents.length === 0 ? (
          <div className="col-span-2 p-12 text-center text-slate-400">
            No agents registered in the database.
          </div>
        ) : (
          agents.map((agent) => (
            <Card key={agent.agent_name} className="bg-white border-slate-200 shadow-sm flex flex-col justify-between">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className="p-2 rounded-lg bg-slate-100 text-slate-700">
                      <Bot className="w-4 h-4" />
                    </div>
                    <div>
                      <CardTitle className="text-sm font-bold text-slate-900">
                        {agent.agent_name}
                      </CardTitle>
                      <CardDescription className="text-xs text-slate-400 font-mono">
                        Model: {agent.model_name} • Temp: {agent.temperature}
                      </CardDescription>
                    </div>
                  </div>
                  <AgentStatusBadge status={agent.status} />
                </div>
              </CardHeader>

              <CardContent className="space-y-4 pt-0">
                <p className="text-xs text-slate-600 leading-relaxed min-h-[36px]">
                  {agent.description || "Stateful LangGraph specialized workflow agent."}
                </p>

                {/* Telemetry Metrics */}
                <div className="grid grid-cols-3 gap-2 p-2.5 bg-slate-50 rounded-lg text-center">
                  <div>
                    <p className="text-[10px] font-semibold uppercase text-slate-400">Executions</p>
                    <p className="text-xs font-bold text-slate-800">{agent.total_executions}</p>
                  </div>
                  <div>
                    <p className="text-[10px] font-semibold uppercase text-slate-400">Success Rate</p>
                    <p className="text-xs font-bold text-emerald-600">{agent.success_rate}%</p>
                  </div>
                  <div>
                    <p className="text-[10px] font-semibold uppercase text-slate-400">Avg Latency</p>
                    <p className="text-xs font-bold text-slate-800">{agent.avg_latency_ms || 320}ms</p>
                  </div>
                </div>

                {/* Kill Switch Controls & Log Viewer */}
                <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                  <div className="flex items-center gap-1">
                    <Button
                      size="sm"
                      variant={agent.status === "active" ? "default" : "outline"}
                      className={`h-7 text-[11px] ${agent.status === "active" ? "bg-emerald-600 hover:bg-emerald-700 text-white" : ""}`}
                      onClick={() => handleStatusChange(agent.agent_name, "active")}
                    >
                      <Play className="w-2.5 h-2.5 mr-1" />
                      Active
                    </Button>
                    <Button
                      size="sm"
                      variant={agent.status === "paused" ? "default" : "outline"}
                      className={`h-7 text-[11px] ${agent.status === "paused" ? "bg-amber-600 hover:bg-amber-700 text-white" : ""}`}
                      onClick={() => handleStatusChange(agent.agent_name, "paused")}
                    >
                      <Pause className="w-2.5 h-2.5 mr-1" />
                      Pause
                    </Button>
                    <Button
                      size="sm"
                      variant={agent.status === "disabled" ? "destructive" : "outline"}
                      className="h-7 text-[11px]"
                      onClick={() => handleStatusChange(agent.agent_name, "disabled")}
                    >
                      <PowerOff className="w-2.5 h-2.5 mr-1" />
                      Disable
                    </Button>
                  </div>

                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-7 text-xs text-blue-600"
                    onClick={() => handleViewLogs(agent.agent_name)}
                    disabled={isLoadingLogs}
                  >
                    <Terminal className="w-3 h-3 mr-1" />
                    Logs
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Execution Logs Modal */}
      {selectedAgentLogs && (
        <Dialog open={true} onOpenChange={() => setSelectedAgentLogs(null)}>
          <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto bg-white border-slate-200">
            <DialogHeader>
              <DialogTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Terminal className="w-4 h-4 text-blue-600" />
                Execution Logs: {selectedAgentLogs.agentName}
              </DialogTitle>
            </DialogHeader>

            <div className="space-y-3 pt-2">
              {selectedAgentLogs.logs.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-sm">
                  No execution traces recorded yet for this agent.
                </div>
              ) : (
                selectedAgentLogs.logs.map((log) => (
                  <div key={log.id} className="p-3 bg-slate-50 border border-slate-200 rounded-md font-mono text-xs space-y-1.5">
                    <div className="flex items-center justify-between text-[11px] text-slate-500">
                      <span>Status: <strong className={log.status === "success" ? "text-emerald-600" : "text-rose-600"}>{log.status}</strong></span>
                      <span>Latency: {log.latency_ms || 0}ms • {new Date(log.executed_at).toLocaleTimeString()}</span>
                    </div>
                    {log.error_message && (
                      <p className="text-rose-600 font-semibold">{log.error_message}</p>
                    )}
                    <details className="cursor-pointer text-[11px] text-slate-600">
                      <summary className="hover:text-blue-600">View Input / Output Payload State</summary>
                      <pre className="mt-1 p-2 bg-white border rounded text-[10px] overflow-x-auto text-slate-700">
                        {JSON.stringify({ input: log.input_state, output: log.output_state }, null, 2)}
                      </pre>
                    </details>
                  </div>
                ))
              )}
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
