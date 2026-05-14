import Link from "next/link";
import { Header } from "@/components/Header";
import { ReportView } from "@/components/ReportView";
import { getReport } from "@/lib/api";
import { getDictionary } from "@/lib/i18n/dictionaries";
import { getServerLocale } from "@/lib/i18n/server";

type ReportPageProps = {
  params: Promise<{ id: string }>;
};

export default async function ReportPage({ params }: ReportPageProps) {
  const { id } = await params;
  const locale = await getServerLocale();
  const t = getDictionary(locale);
  const report = await getReport(id);

  return (
    <>
      <Header />
      <main className="mx-auto max-w-7xl px-5 py-8">
        <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
          <div>
            <div className="text-sm text-ink/60">{t.report.report} #{report.report_id}</div>
            <h1 className="mt-1 text-3xl font-semibold text-ink">{report.keyword}</h1>
          </div>
          <Link className="bg-accent px-4 py-2 text-sm font-medium text-white" href="/validate">
            {t.report.newAnalysis}
          </Link>
        </div>
        <ReportView report={report} locale={locale} />
      </main>
    </>
  );
}
