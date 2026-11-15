"use client";

import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, RotateCcw, Download } from "lucide-react";

interface AuditFilterPanelProps {
  onSearch: (params: {
    action?: string;
    resource_type?: string;
    resource_id?: string;
  }) => void;
  onReset: () => void;
  onExport: () => void;
}

export const AuditFilterPanel: React.FC<AuditFilterPanelProps> = ({
  onSearch,
  onReset,
  onExport,
}) => {
  const [action, setAction] = useState("");
  const [resourceType, setResourceType] = useState("all");
  const [resourceId, setResourceId] = useState("");

  const handleApply = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch({
      action: action || undefined,
      resource_type: resourceType === "all" ? undefined : resourceType,
      resource_id: resourceId || undefined,
    });
  };

  const handleReset = () => {
    setAction("");
    setResourceType("all");
    setResourceId("");
    onReset();
  };

  return (
    <form
      onSubmit={handleApply}
      className="p-4 bg-white border border-slate-200 rounded-lg shadow-sm space-y-3"
    >
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <div>
          <label className="text-[11px] font-semibold uppercase text-slate-500 mb-1 block">
            Action / Event
          </label>
          <Input
            value={action}
            onChange={(e) => setAction(e.target.value)}
            placeholder="e.g. SUBMIT_UNDERWRITING"
            className="text-xs"
          />
        </div>

        <div>
          <label className="text-[11px] font-semibold uppercase text-slate-500 mb-1 block">
            Resource Type
          </label>
          <Select value={resourceType} onValueChange={setResourceType}>
            <SelectTrigger className="text-xs">
              <SelectValue placeholder="All Resources" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Resources</SelectItem>
              <SelectItem value="Application">Application</SelectItem>
              <SelectItem value="UnderwritingCase">Underwriting Case</SelectItem>
              <SelectItem value="Quote">Quote</SelectItem>
              <SelectItem value="Document">Document</SelectItem>
              <SelectItem value="User">User</SelectItem>
              <SelectItem value="AgentConfiguration">Agent Configuration</SelectItem>
              <SelectItem value="SystemSetting">System Setting</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-[11px] font-semibold uppercase text-slate-500 mb-1 block">
            Resource ID
          </label>
          <Input
            value={resourceId}
            onChange={(e) => setResourceId(e.target.value)}
            placeholder="e.g. APP-2026-..."
            className="text-xs"
          />
        </div>

        <div className="flex items-end gap-2">
          <Button type="submit" size="sm" className="bg-blue-600 hover:bg-blue-700 text-white flex-1">
            <Search className="w-3.5 h-3.5 mr-1.5" />
            Filter
          </Button>
          <Button type="button" variant="outline" size="sm" onClick={handleReset}>
            <RotateCcw className="w-3.5 h-3.5" />
          </Button>
          <Button type="button" variant="outline" size="sm" onClick={onExport} title="Export CSV">
            <Download className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>
    </form>
  );
};

