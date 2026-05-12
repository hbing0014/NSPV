import Link from "next/link";
import { Header } from "@/components/Header";
import { getReports } from "@/lib/api";

export default async function ReportsPage() {
  const reports = await getReports().catch(() => []);

  return (
    <>
      <Header />
      <main className="mx-auto max-w-7xl px-5 py-8">
        <div className="mb-6 flex items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-semibold text-ink">Historical Reports</h1>
            <p className="mt-2 text-sm text-ink/60">Latest 50 keyword analyses.</p>
          </div>
          <Link className="bg-accent px-4 py-2 text-sm font-medium text-white" href="/">
            New Analysis
          </Link>
        </div>

        <div className="border border-line bg-white">
          {reports.length ? (
            <table className="w-full border-collapse text-left text-sm">
              <thead className="bg-field text-ink/70">
                <tr>
                  <th className="p-3">Keyword</th>
                  <th className="p-3">NSFS</th>
                  <th className="p-3">Recommendation</th>
                  <th className="p-3">Risk</th>
                  <th className="p-3">Created</th>
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
                    <td className="p-3">{report.recommendation}</td>
                    <td className="p-3">{report.risk_level}</td>
                    <td className="p-3">{new Date(report.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-sm text-ink/60">No reports yet.</div>
          )}
        </div>
      </main>
    </>
  );
}

