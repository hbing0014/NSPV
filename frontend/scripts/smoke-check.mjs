const baseUrl = process.env.FRONTEND_BASE_URL ?? "http://127.0.0.1:3000";
const reportId = process.env.SMOKE_REPORT_ID;

const checks = [
  {
    path: "/",
    text: "Amazon 新店选品风险判断"
  },
  {
    path: "/reports",
    text: "Historical Reports"
  }
];

if (reportId) {
  checks.push({
    path: `/reports/${reportId}`,
    text: "NSFS Score"
  });
}

async function checkPage({ path, text }) {
  const url = new URL(path, baseUrl);
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${url} returned ${response.status}`);
  }

  const html = await response.text();
  if (!html.includes(text)) {
    throw new Error(`${url} did not contain expected text: ${text}`);
  }

  console.log(`OK ${url}`);
}

for (const check of checks) {
  await checkPage(check);
}

