"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

type TabsContextValue = {
  value: string;
  setValue: (value: string) => void;
};

const TabsContext = React.createContext<TabsContextValue | null>(null);

export function Tabs({
  value,
  defaultValue,
  onValueChange,
  children,
  className
}: {
  value?: string;
  defaultValue: string;
  onValueChange?: (value: string) => void;
  children: React.ReactNode;
  className?: string;
}) {
  const [internalValue, setInternalValue] = React.useState(defaultValue);
  const selectedValue = value ?? internalValue;

  function setValue(nextValue: string) {
    setInternalValue(nextValue);
    onValueChange?.(nextValue);
  }

  return (
    <TabsContext.Provider value={{ value: selectedValue, setValue }}>
      <div className={className}>{children}</div>
    </TabsContext.Provider>
  );
}

export function TabsList({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("inline-flex rounded-md border border-border bg-secondary p-1 text-sm text-muted-foreground", className)}
      role="tablist"
      {...props}
    />
  );
}

export function TabsTrigger({
  value,
  className,
  children,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { value: string }) {
  const context = React.useContext(TabsContext);
  if (!context) {
    throw new Error("TabsTrigger must be used within Tabs.");
  }

  const selected = context.value === value;
  return (
    <button
      className={cn(
        "cursor-pointer rounded-sm px-3 py-1.5 font-medium transition-colors duration-200",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        selected ? "bg-card text-foreground shadow-sm" : "hover:text-foreground",
        className
      )}
      role="tab"
      type="button"
      aria-selected={selected}
      onClick={() => context.setValue(value)}
      {...props}
    >
      {children}
    </button>
  );
}

export function TabsContent({
  value,
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & { value: string }) {
  const context = React.useContext(TabsContext);
  if (!context) {
    throw new Error("TabsContent must be used within Tabs.");
  }

  if (context.value !== value) {
    return null;
  }

  return <div className={cn("mt-4", className)} role="tabpanel" {...props} />;
}
