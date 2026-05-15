const baseUrl = process.env.FRONTEND_BASE_URL ?? "http://127.0.0.1:3000";
const apiBaseUrl = process.env.BACKEND_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";
let productId = process.env.SMOKE_PRODUCT_ID;
let reportId = process.env.SMOKE_REPORT_ID;
const locale = process.env.SMOKE_LOCALE ?? "zh-CN";
const isEnglish = locale === "en";

if (!productId || !reportId) {
  const seeded = await seedSmokeData();
  productId = productId ?? String(seeded.productId);
  reportId = reportId ?? String(seeded.reportId);
}

const checks = [
  {
    path: "/",
    text: [
      isEnglish ? "Find Amazon Products You Can Actually Launch" : "发现你当前真正启动得起的 Amazon 产品",
      isEnglish ? "Discover Products" : "发现产品"
    ]
  },
  {
    path: `/validate?${new URLSearchParams({
      keyword: "under sink organizer",
      category: "Kitchen & Dining",
      budget_rmb: "32692",
      target_price_min: "23",
      target_price_max: "36",
      product_opportunity_id: productId
    }).toString()}`,
    text: [
      isEnglish ? "Amazon New Seller Product Validator" : "Amazon 新店选品风险判断",
      "under sink organizer"
    ]
  },
  {
    path: "/radar",
    text: isEnglish ? "Product Opportunity Radar" : "产品机会雷达"
  },
  {
    path: `/radar/products/${productId}`,
    text: [
      "Under Sink Organizer",
      isEnglish ? "Validate Keyword" : "验证关键词",
      "NPFS",
      "Launch"
    ]
  },
  {
    path: "/reports",
    text: isEnglish ? "Historical Reports" : "历史报告"
  },
  {
    path: `/reports/${reportId}`,
    text: [
      isEnglish ? "NSFS Score" : "NSFS 评分",
      "under sink organizer"
    ]
  }
];

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
  const expectedTexts = Array.isArray(text) ? text : [text];
  for (const expectedText of expectedTexts) {
    if (!html.includes(expectedText)) {
      throw new Error(`${url} did not contain expected text: ${expectedText}`);
    }
  }

  console.log(`OK ${url}`);
}

async function seedSmokeData() {
  const discovery = await postJson("/api/discover/products", {
    category: "Kitchen & Dining",
    marketplace: "US",
    budget_rmb: 100000,
    risk_preference: "low",
    price_min: 20,
    price_max: 40,
    weight_limit_g: 500,
    exclude_red_ocean: true,
    exclude_amazon_basics: true,
    exclude_fragile: true,
    exclude_seasonal: true
  });

  const product = discovery.products?.[0];
  if (!product) {
    throw new Error("Smoke seed did not create a product opportunity.");
  }

  const report = await postJson("/api/analyze", {
    project_id: discovery.project_id,
    product_opportunity_id: product.product_opportunity_id,
    keyword: product.primary_keyword,
    marketplace: "US",
    category: product.category,
    budget_rmb: 100000,
    target_price_min: 20,
    target_price_max: 40,
    exclude_red_ocean: true,
    locale
  });

  console.log(`Seeded smoke product #${product.product_opportunity_id} and report #${report.report_id}`);
  return {
    productId: product.product_opportunity_id,
    reportId: report.report_id
  };
}

async function postJson(path, payload) {
  const url = new URL(path, apiBaseUrl);
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${url} returned ${response.status}: ${body}`);
  }

  return response.json();
}

for (const check of checks) {
  await checkPage(check);
}
