import Link from "next/link";
import * as React from "react";
import { cn } from "@/lib/utils";

export function Sidebar({ className, ...props }: React.HTMLAttributes<HTMLElement>) {
  return (
    <aside
      className={cn("flex h-full w-64 shrink-0 flex-col border-r border-border bg-card text-card-foreground", className)}
      {...props}
    />
  );
}

export function SidebarHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("border-b border-border p-4", className)} {...props} />;
}

export function SidebarSection({ title, children, className }: { title?: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("grid gap-1 p-3", className)}>
      {title ? <div className="px-2 py-2 text-xs font-semibold uppercase text-muted-foreground">{title}</div> : null}
      {children}
    </div>
  );
}

export function SidebarLink({
  href,
  active,
  icon,
  children,
  className
}: {
  href: string;
  active?: boolean;
  icon?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <Link
      className={cn(
        "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors duration-200",
        active ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-secondary hover:text-foreground",
        className
      )}
      href={href}
    >
      {icon}
      <span className="min-w-0 truncate">{children}</span>
    </Link>
  );
}
