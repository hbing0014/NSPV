"use client";

import * as React from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export function Modal({
  open,
  onOpenChange,
  title,
  description,
  children,
  footer,
  className
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
}) {
  React.useEffect(() => {
    if (!open) {
      return;
    }

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onOpenChange(false);
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [onOpenChange, open]);

  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="presentation">
      <button
        className="absolute inset-0 cursor-default bg-slate-950/55 backdrop-blur-sm"
        type="button"
        aria-label="Close modal"
        onClick={() => onOpenChange(false)}
      />
      <div
        className={cn("relative z-10 w-full max-w-lg rounded-lg border border-border bg-card text-card-foreground shadow-elevated", className)}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div className="flex items-start justify-between gap-4 border-b border-border p-5">
          <div>
            <h2 id="modal-title" className="text-lg font-semibold text-foreground">
              {title}
            </h2>
            {description ? <p className="mt-1 text-sm leading-6 text-muted-foreground">{description}</p> : null}
          </div>
          <Button variant="ghost" size="icon" type="button" onClick={() => onOpenChange(false)}>
            <X className="h-4 w-4" aria-hidden="true" />
            <span className="sr-only">Close</span>
          </Button>
        </div>
        <div className="p-5">{children}</div>
        {footer ? <div className="flex justify-end gap-3 border-t border-border p-5">{footer}</div> : null}
      </div>
    </div>
  );
}
