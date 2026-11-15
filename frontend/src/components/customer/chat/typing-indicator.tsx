"use client";

import * as React from "react";
import { Bot } from "lucide-react";

export function TypingIndicator() {
  return (
    <div className="flex gap-3 max-w-[85%] mr-auto items-end">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-medium bg-slate-100 text-slate-800 border border-slate-200">
        <Bot className="h-4 w-4 text-blue-600 animate-pulse" />
      </div>
      <div className="rounded-xl px-4 py-3 bg-slate-50 text-slate-700 border border-slate-100 shadow-2xs flex items-center space-x-1.5">
        <span className="text-xs text-slate-500 mr-1.5">Advisor is analyzing</span>
        <span className="h-1.5 w-1.5 rounded-full bg-blue-600 animate-bounce [animation-delay:-0.3s]" />
        <span className="h-1.5 w-1.5 rounded-full bg-blue-600 animate-bounce [animation-delay:-0.15s]" />
        <span className="h-1.5 w-1.5 rounded-full bg-blue-600 animate-bounce" />
      </div>
    </div>
  );
}

