const baseUrl = process.env.FRONTEND_BASE_URL ?? "http://127.0.0.1:3000";
const reportId = process.env.SMOKE_REPORT_ID;
const locale = process.env.SMOKE_LOCALE ?? "zh-CN";
const isEnglish = locale === "en";

const checks = [
  {
    path: "/",
    text: isEnglish ? "Find Amazon Products You Can Actually Launch" : "发现你当前真正启动得起的 Amazon 产品"
  },
  {
    path: "/validate",
    text: isEnglish ? "Amazon New Seller Product Validator" : "Amazon 新店选品风险判断"
  },
  {
    path: "/radar",
    text: isEnglish ? "Product Opportunity Radar" : "产品机会雷达"
  },
  {
    path: "/reports",
    text: isEnglish ? "Historical Reports" : "历史报告"
  }
];

if (reportId) {
  checks.push({
    path: `/reports/${reportId}`,
    text: isEnglish ? "NSFS Score" : "NSFS 评分"
  });
}

async function checkPage({ path, text }) {
  const url = new URL(path, baseUrl);
  const response = await fetch(url, {
    headers: {
      Cookie: `nspv-locale=${locale}`
    }
  });
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
