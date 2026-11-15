"use client";

import * as React from "react";
import { Sparkles } from "lucide-react";

interface SuggestionChipsProps {
  chips: string[];
  onSelect: (chip: string) => void;
  disabled?: boolean;
}

export function SuggestionChips({ chips, onSelect, disabled = false }: SuggestionChipsProps) {
  if (!chips || chips.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-1.5 p-2 bg-slate-50/80 border-t border-slate-100">
      <span className="text-[11px] font-semibold text-slate-400 flex items-center mr-1">
        <Sparkles className="h-3 w-3 mr-1 text-blue-500" />
        Suggested:
      </span>
      {chips.map((chip, i) => (
        <button
          key={`${chip}-${i}`}
          onClick={() => onSelect(chip)}
          disabled={disabled}
          className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs text-slate-700 shadow-2xs transition-colors hover:border-blue-400 hover:bg-blue-50 hover:text-blue-700 disabled:opacity-50"
        >
          {chip}
        </button>
      ))}
    </div>
  );
}

