import Link from "next/link";
import * as React from "react";
import { cn } from "@/lib/utils";

export function AppHeader({ className, ...props }: React.HTMLAttributes<HTMLElement>) {
  return (
    <header
      className={cn("sticky top-0 z-40 border-b border-border bg-card/95 text-card-foreground backdrop-blur supports-[backdrop-filter]:bg-card/80", className)}
      {...props}
    />
  );
}

export function AppHeaderInner({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-5", className)} {...props} />;
}

export function AppLogo({
  href = "/",
  icon,
  children,
  className
}: {
  href?: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <Link className={cn("flex items-center gap-3 font-semibold text-foreground", className)} href={href}>
      {icon ? <span className="flex h-9 w-9 items-center justify-center rounded-md bg-primary text-primary-foreground">{icon}</span> : null}
      <span>{children}</span>
    </Link>
  );
}

export function AppNav({ className, ...props }: React.HTMLAttributes<HTMLElement>) {
  return <nav className={cn("hidden items-center gap-1 text-sm md:flex", className)} {...props} />;
}

export function AppNavLink({
  href,
  active,
  children,
  className
}: {
  href: string;
  active?: boolean;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <Link
      className={cn(
        "rounded-md px-3 py-2 font-medium transition-colors duration-200",
        active ? "bg-secondary text-foreground" : "text-muted-foreground hover:bg-secondary hover:text-foreground",
        className
      )}
      href={href}
    >
      {children}
    </Link>
  );
}

export function AppHeaderActions({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex items-center gap-2", className)} {...props} />;
}
