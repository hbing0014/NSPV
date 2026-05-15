import * as React from "react";
import { cn } from "@/lib/utils";

export type InputProps = React.InputHTMLAttributes<HTMLInputElement> & {
  invalid?: boolean;
};

export const Input = React.forwardRef<HTMLInputElement, InputProps>(({ className, invalid = false, ...props }, ref) => {
  return (
    <input
      ref={ref}
      className={cn(
        "flex h-10 w-full rounded-md border bg-card px-3 py-2 text-sm text-foreground shadow-sm transition-colors duration-200",
        "placeholder:text-muted-foreground",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
        "disabled:cursor-not-allowed disabled:bg-secondary disabled:opacity-60",
        invalid ? "border-destructive focus-visible:ring-destructive" : "border-input",
        className
      )}
      aria-invalid={invalid || undefined}
      {...props}
    />
  );
});

Input.displayName = "Input";

export function Field({
  label,
  hint,
  error,
  children,
  className
}: {
  label: string;
  hint?: string;
  error?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <label className={cn("grid gap-2", className)}>
      <span className="text-sm font-medium text-foreground">{label}</span>
      {children}
      {error ? <span className="text-xs font-medium text-destructive">{error}</span> : null}
      {!error && hint ? <span className="text-xs text-muted-foreground">{hint}</span> : null}
    </label>
  );
}
