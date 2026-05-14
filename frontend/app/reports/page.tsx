import Link from "next/link";
import { Header } from "@/components/Header";
import { getReports } from "@/lib/api";
import { getDictionary, translateRecommendation, translateRisk } from "@/lib/i18n/dictionaries";
import { getServerLocale } from "@/lib/i18n/server";

export default async function ReportsPage() {
  const locale = await getServerLocale();
  const t = getDictionary(locale);
  const reports = await getReports().catch(() => []);

  return (
    <>
      <Header />
      <main className="mx-auto max-w-7xl px-5 py-8">
        <div className="mb-6 flex items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-semibold text-ink">{t.reports.title}</h1>
            <p className="mt-2 text-sm text-ink/60">{t.reports.subtitle}</p>
          </div>
          <Link className="bg-accent px-4 py-2 text-sm font-medium text-white" href="/">
            {t.reports.newAnalysis}
          </Link>
        </div>

        <div className="border border-line bg-white">
          {reports.length ? (
            <table className="w-full border-collapse text-left text-sm">
              <thead className="bg-field text-ink/70">
                <tr>
                  <th className="p-3">{t.reports.columns.keyword}</th>
                  <th className="p-3">{t.reports.columns.nsfs}</th>
                  <th className="p-3">{t.reports.columns.recommendation}</th>
                  <th className="p-3">{t.reports.columns.risk}</th>
                  <th className="p-3">{t.reports.columns.created}</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report) => (
                  <tr key={report.report_id} className="border-t border-line">
                    <td className="p-3">
                      <Link className="font-medium text-accent" href={`/reports/${report.report_id}`}>
                        {report.keyword}
                      </Link>
                    </td>
                    <td className="p-3">{report.nsfs_score}</td>
                    <td className="p-3">{translateRecommendation(locale, report.recommendation)}</td>
                    <td className="p-3">{translateRisk(locale, report.risk_level)}</td>
                    <td className="p-3">{new Date(report.created_at).toLocaleString(locale)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-sm text-ink/60">{t.reports.empty}</div>
          )}
        </div>
      </main>
    </>
  );
}
