"use client";

import * as React from "react";

function parseInline(text: string): React.ReactNode[] {
  // Regex to detect **bold**, __bold__, *italic*, _italic_, and `inline code`
  const regex = /(\*\*.*?\*\*|__.*?__|`.*?`|\*.*?\*|_.*?_)/g;
  const parts = text.split(regex);

  return parts.map((part, i) => {
    if (!part) return null;

    // Bold (**text** or __text__)
    if (
      (part.startsWith("**") && part.endsWith("**") && part.length >= 4) ||
      (part.startsWith("__") && part.endsWith("__") && part.length >= 4)
    ) {
      const inner = part.slice(2, -2);
      return (
        <strong key={i} className="font-semibold">
          {inner}
        </strong>
      );
    }

    // Inline Code (`code`)
    if (part.startsWith("`") && part.endsWith("`") && part.length >= 2) {
      const inner = part.slice(1, -1);
      return (
        <code
          key={i}
          className="rounded bg-black/10 dark:bg-white/10 px-1 py-0.5 font-mono text-[0.85em]"
        >
          {inner}
        </code>
      );
    }

    // Italic (*text* or _text_)
    if (
      (part.startsWith("*") && part.endsWith("*") && part.length >= 2) ||
      (part.startsWith("_") && part.endsWith("_") && part.length >= 2)
    ) {
      const inner = part.slice(1, -1);
      return (
        <em key={i} className="italic">
          {inner}
        </em>
      );
    }

    return <React.Fragment key={i}>{part}</React.Fragment>;
  });
}

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export function MarkdownRenderer({ content, className = "" }: MarkdownRendererProps) {
  if (!content) return null;

  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];
  let currentList: { type: "ul" | "ol"; items: React.ReactNode[] } | null = null;

  const flushList = () => {
    if (currentList) {
      if (currentList.type === "ul") {
        elements.push(
          <ul key={`ul-${elements.length}`} className="my-1 ml-4 list-disc space-y-1">
            {currentList.items.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        );
      } else {
        elements.push(
          <ol key={`ol-${elements.length}`} className="my-1 ml-4 list-decimal space-y-1">
            {currentList.items.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ol>
        );
      }
      currentList = null;
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const line = rawLine.trim();

    if (!line) {
      flushList();
      continue;
    }

    // Numbered list item: "1. text"
    const numMatch = line.match(/^(\d+)\.\s+(.*)/);
    if (numMatch) {
      if (!currentList || currentList.type !== "ol") {
        flushList();
        currentList = { type: "ol", items: [] };
      }
      currentList.items.push(parseInline(numMatch[2]));
      continue;
    }

    // Bullet list item: "- text" or "* text"
    const bulletMatch = line.match(/^[-*]\s+(.*)/);
    if (bulletMatch) {
      if (!currentList || currentList.type !== "ul") {
        flushList();
        currentList = { type: "ul", items: [] };
      }
      currentList.items.push(parseInline(bulletMatch[1]));
      continue;
    }

    flushList();

    // Markdown Headers
    if (line.startsWith("### ")) {
      elements.push(
        <h3 key={i} className="mt-2 mb-1 text-sm font-semibold">
          {parseInline(line.slice(4))}
        </h3>
      );
    } else if (line.startsWith("## ")) {
      elements.push(
        <h2 key={i} className="mt-2 mb-1 text-base font-bold">
          {parseInline(line.slice(3))}
        </h2>
      );
    } else if (line.startsWith("# ")) {
      elements.push(
        <h1 key={i} className="mt-2 mb-1 text-lg font-bold">
          {parseInline(line.slice(2))}
        </h1>
      );
    } else {
      elements.push(
        <p key={i} className="leading-relaxed">
          {parseInline(line)}
        </p>
      );
    }
  }

  flushList();

  return <div className={`space-y-1.5 ${className}`}>{elements}</div>;
}

