import Link from "next/link";
import { BarChart3 } from "lucide-react";

export function Header() {
  return (
    <header className="border-b border-line bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
        <Link href="/" className="flex items-center gap-3 font-semibold text-ink">
          <span className="flex h-9 w-9 items-center justify-center bg-accent text-white">
            <BarChart3 size={20} aria-hidden="true" />
          </span>
          <span>NSPV</span>
        </Link>
        <nav className="flex items-center gap-5 text-sm text-ink/70">
          <Link href="/">Analyze</Link>
          <Link href="/reports">Reports</Link>
        </nav>
      </div>
    </header>
  );
}

