"use client";

import * as React from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface AccordionContextType {
  value?: string | string[];
  onValueChange: (val: string) => void;
  type: "single" | "multiple";
  collapsible?: boolean;
}

const AccordionContext = React.createContext<AccordionContextType | null>(null);

interface AccordionProps extends React.HTMLAttributes<HTMLDivElement> {
  type?: "single" | "multiple";
  collapsible?: boolean;
  defaultValue?: string | string[];
  value?: string | string[];
  onValueChange?: (val: any) => void;
}

const Accordion = React.forwardRef<HTMLDivElement, AccordionProps>(
  (
    {
      type = "single",
      collapsible = true,
      defaultValue,
      value: controlledValue,
      onValueChange,
      className,
      children,
      ...props
    },
    ref
  ) => {
    const [uncontrolledValue, setUncontrolledValue] = React.useState<string | string[]>(
      defaultValue || (type === "multiple" ? [] : "")
    );
    const value = controlledValue !== undefined ? controlledValue : uncontrolledValue;

    const handleValueChange = (itemValue: string) => {
      let nextValue: string | string[];
      if (type === "single") {
        nextValue = value === itemValue && collapsible ? "" : itemValue;
      } else {
        const arr = Array.isArray(value) ? value : [];
        nextValue = arr.includes(itemValue)
          ? arr.filter((v) => v !== itemValue)
          : [...arr, itemValue];
      }
      if (controlledValue === undefined) {
        setUncontrolledValue(nextValue);
      }
      onValueChange?.(nextValue);
    };

    return (
      <AccordionContext.Provider
        value={{ value, onValueChange: handleValueChange, type, collapsible }}
      >
        <div ref={ref} className={cn("space-y-1", className)} {...props}>
          {children}
        </div>
      </AccordionContext.Provider>
    );
  }
);
Accordion.displayName = "Accordion";

const AccordionItemContext = React.createContext<{ value: string; isOpen: boolean } | null>(
  null
);

const AccordionItem = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { value: string }
>(({ className, value, children, ...props }, ref) => {
  const ctx = React.useContext(AccordionContext);
  const isOpen =
    ctx?.type === "multiple"
      ? Array.isArray(ctx.value) && ctx.value.includes(value)
      : ctx?.value === value;

  return (
    <AccordionItemContext.Provider value={{ value, isOpen }}>
      <div
        ref={ref}
        data-state={isOpen ? "open" : "closed"}
        className={cn("border-b border-slate-200", className)}
        {...props}
      >
        {children}
      </div>
    </AccordionItemContext.Provider>
  );
});
AccordionItem.displayName = "AccordionItem";

const AccordionTrigger = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ className, children, ...props }, ref) => {
  const itemCtx = React.useContext(AccordionItemContext);
  const accordionCtx = React.useContext(AccordionContext);
  const isOpen = itemCtx?.isOpen ?? false;

  return (
    <div className="flex">
      <button
        ref={ref}
        type="button"
        data-state={isOpen ? "open" : "closed"}
        onClick={() => itemCtx && accordionCtx?.onValueChange(itemCtx.value)}
        className={cn(
          "flex flex-1 items-center justify-between py-3 font-medium transition-all hover:underline text-left text-xs [&[data-state=open]>svg]:rotate-180",
          className
        )}
        {...props}
      >
        {children}
        <ChevronDown className="h-4 w-4 shrink-0 transition-transform duration-200 text-slate-500" />
      </button>
    </div>
  );
});
AccordionTrigger.displayName = "AccordionTrigger";

const AccordionContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, children, ...props }, ref) => {
  const itemCtx = React.useContext(AccordionItemContext);
  const isOpen = itemCtx?.isOpen ?? false;

  if (!isOpen) return null;

  return (
    <div
      ref={ref}
      data-state={isOpen ? "open" : "closed"}
      className={cn("overflow-hidden text-xs pb-3 pt-0", className)}
      {...props}
    >
      {children}
    </div>
  );
});
AccordionContent.displayName = "AccordionContent";

export { Accordion, AccordionItem, AccordionTrigger, AccordionContent };
