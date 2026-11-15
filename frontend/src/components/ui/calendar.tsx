"use client";

import * as React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { buttonVariants } from "@/components/ui/button";

export interface CalendarProps {
  selectedDate?: Date;
  onSelectDate?: (date: Date) => void;
  className?: string;
}

export function Calendar({
  selectedDate = new Date(),
  onSelectDate,
  className,
}: CalendarProps) {
  const [currentMonth, setCurrentMonth] = React.useState(
    new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1)
  );

  const prevMonth = () => {
    setCurrentMonth(
      new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1)
    );
  };

  const nextMonth = () => {
    setCurrentMonth(
      new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1)
    );
  };

  const monthName = currentMonth.toLocaleString("default", {
    month: "long",
    year: "numeric",
  });

  const daysInMonth = new Date(
    currentMonth.getFullYear(),
    currentMonth.getMonth() + 1,
    0
  ).getDate();

  const startDay = new Date(
    currentMonth.getFullYear(),
    currentMonth.getMonth(),
    1
  ).getDay();

  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);
  const blanks = Array.from({ length: startDay }, (_, i) => i);

  return (
    <div className={cn("p-3 bg-white rounded-md border border-slate-200", className)}>
      <div className="flex items-center justify-between pb-3">
        <h4 className="text-sm font-semibold text-slate-900">{monthName}</h4>
        <div className="flex items-center space-x-1">
          <button
            onClick={prevMonth}
            className={cn(buttonVariants({ variant: "outline", size: "icon" }), "h-7 w-7")}
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            onClick={nextMonth}
            className={cn(buttonVariants({ variant: "outline", size: "icon" }), "h-7 w-7")}
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
      <div className="grid grid-cols-7 gap-1 text-center text-xs font-medium text-slate-500 pb-2">
        <span>Su</span>
        <span>Mo</span>
        <span>Tu</span>
        <span>We</span>
        <span>Th</span>
        <span>Fr</span>
        <span>Sa</span>
      </div>
      <div className="grid grid-cols-7 gap-1 text-center text-sm">
        {blanks.map((b) => (
          <div key={`blank-${b}`} className="h-8 w-8" />
        ))}
        {days.map((d) => {
          const dateObj = new Date(
            currentMonth.getFullYear(),
            currentMonth.getMonth(),
            d
          );
          const isSelected =
            selectedDate &&
            dateObj.toDateString() === selectedDate.toDateString();
          return (
            <button
              key={d}
              onClick={() => onSelectDate?.(dateObj)}
              className={cn(
                "h-8 w-8 rounded-md text-xs font-normal transition-colors hover:bg-slate-100",
                isSelected &&
                  "bg-primary text-primary-foreground font-semibold hover:bg-primary"
              )}
            >
              {d}
            </button>
          );
        })}
      </div>
    </div>
  );
}

