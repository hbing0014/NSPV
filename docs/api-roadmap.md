# NSPV API Roadmap

本文档定义 NSPV API 从当前原型到 V1、V2、V3 的演进规划。

## API Design Principles

- V1 优先完成单关键词分析闭环。
- API 输出必须可解释，不能只返回一个分数。
- 抓取失败、无结果、字段缺失必须返回明确错误。
- 后续 AI、支付、开放平台不得污染 V1 核心路径。
- 内部 API 和开放 API 分开规划，V1 不做第三方开放平台。

## Current Implemented APIs

当前项目已有：

```text
GET  /health
POST /api/analyze
POST /api/projects
GET  /api/projects
GET  /api/projects/{project_id}
PUT  /api/projects/{project_id}
DELETE /api/projects/{project_id}
GET  /api/reports
GET  /api/reports/{report_id}
GET  /api/projects/{project_id}/reports
```

当前 `POST /api/analyze` 使用 mock Amazon Top20 数据源，用于打通业务闭环。

Scraper provider is selected by backend configuration:

```text
SCRAPER_PROVIDER=mock
SCRAPER_PROVIDER=playwright
SCRAPER_PROVIDER=brightdata
```

Currently only `mock` is implemented. `playwright` and `brightdata` return a structured scraper failure until their providers are implemented.

## V1 API Target

### Analyze Keyword

推荐最终路径：

```text
POST /api/analyze/keyword
```

兼容当前路径：

```text
POST /api/analyze
```

Request:

```json
{
  "keyword": "sink organizer",
  "marketplace": "US",
  "category": "Kitchen & Dining",
  "budget_rmb": 100000,
  "target_price_min": 20,
  "target_price_max": 40,
  "project_id": 1,
  "exclude_red_ocean": true
}
```

Response:

```json
{
  "report_id": 1,
  "project_id": 1,
  "keyword_id": 1,
  "keyword": "sink organizer",
  "nsfs_score": 82,
  "recommendation": "Worth Research",
  "risk_level": "Medium",
  "demand_score": 88,
  "competition_score": 62,
  "profit_score": 79,
  "opportunity_score": 91,
  "summary": "需求稳定，但首页Review偏高，建议通过差异化切入。",
  "warnings": [
    "Sponsored density is high",
    "Top10 average reviews are moderate"
  ],
  "suggestions": [
    "Avoid competing on main keyword only",
    "Focus on long-tail keywords",
    "Recommended first order quantity: 300-500 units"
  ],
  "score_details": {},
  "products": [],
  "input_payload": {
    "keyword": "sink organizer",
    "marketplace": "US",
    "category": "Kitchen & Dining",
    "budget_rmb": 100000,
    "target_price_min": 20,
    "target_price_max": 40,
    "project_id": 1,
    "exclude_red_ocean": true
  },
  "scoring_version": "v1.0.0",
  "analysis_status": "completed",
  "error_message": null
}
```

V1 required behavior:

- Validate `target_price_min <= target_price_max`.
- Validate `marketplace = US`.
- Return `400` for invalid input.
- Return `502` or `503` for scraper/data provider failure.
- Save report if analysis succeeds.
- If `project_id` is provided, attach the report to that project.
- If `project_id` is omitted, create a project automatically from the analysis input.
- Save `input_payload`, `scoring_version`, `analysis_status`, and `error_message` on the report.

### Report Detail

```text
GET /api/reports/{report_id}
```

V1 required behavior:

- Return full report detail.
- Include products snapshot used at analysis time.
- Include analysis input and scoring version metadata.
- Return `404` if report does not exist.

### Report List

```text
GET /api/reports
```

V1 required behavior:

- Return latest reports.
- Include `analysis_status`.
- Support future pagination fields:
  - `limit`
  - `offset`
  - `project_id`
  - `keyword`

### Project Reports

```text
GET /api/projects/{project_id}/reports
```

V1 required behavior:

- Return reports under one project.
- Return empty list if no reports.

## V1 Project APIs

Implemented:

```text
POST   /api/projects
GET    /api/projects
GET    /api/projects/{project_id}
PUT    /api/projects/{project_id}
DELETE /api/projects/{project_id}
```

Project create request:

```json
{
  "project_name": "Kitchen Q2",
  "category": "Kitchen & Dining",
  "budget_rmb": 100000,
  "marketplace": "US",
  "target_price_min": 20,
  "target_price_max": 40
}
```

V1 project API can be anonymous or default-user based. Full auth is not required before the core analysis workflow is stable.

Project update accepts partial fields. `target_price_min` cannot exceed `target_price_max` on create or update.

## V1 Auth APIs, Basic

Optional within V1, required before external users:

```text
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/profile
PUT  /api/auth/profile
```

V1 basic auth behavior:

- Password hashing.
- JWT access token.
- Current user profile.
- Reports and projects scoped to user after auth is enabled.

Deferred:

- Email verification.
- Password reset.
- OAuth login.
- API key management.

## V2 APIs

### Review NLP

```text
POST /api/reviews/analyze
GET  /api/reviews/analysis/{analysis_id}
```

Purpose:

- Analyze negative reviews.
- Extract pain points.
- Generate upgrade suggestions.

### Multi Keyword

```text
POST /api/analyze/keywords
```

Purpose:

- Analyze multiple keywords in one job.
- Should use task queue.

### Export

```text
GET /api/reports/{report_id}/export/pdf
GET /api/reports/{report_id}/export/xlsx
```

### Historical Trends

```text
GET /api/keywords/{keyword_id}/history
GET /api/products/{asin}/history
```

## V3 APIs

### Open API Platform

```text
POST /api/developer/api-keys
GET  /api/developer/api-keys
DELETE /api/developer/api-keys/{key_id}
```

Public API examples:

```text
POST /v1/analyze
GET  /v1/reports/{report_id}
GET  /v1/keywords/{keyword}
```

### Billing

```text
POST /api/billing/checkout
POST /api/billing/portal
POST /api/billing/webhooks/stripe
GET  /api/billing/subscription
```

### Chrome Extension

```text
POST /api/extension/analyze-page
POST /api/extension/analyze-asin
```

## Error Contract

All API errors should eventually use this shape:

```json
{
  "error": {
    "code": "SCRAPER_FAILED",
    "message": "Amazon search results could not be fetched.",
    "details": {}
  }
}
```

Suggested error codes:

- `VALIDATION_ERROR`
- `REPORT_NOT_FOUND`
- `PROJECT_NOT_FOUND`
- `SCRAPER_FAILED`
- `SCRAPER_EMPTY_RESULT`
- `SCRAPER_PROVIDER_INVALID`
- `SCORING_FAILED`
- `RATE_LIMITED`
- `UNAUTHORIZED`
- `FORBIDDEN`

Currently implemented:

- Invalid analyze price range returns `400` with `VALIDATION_ERROR`.
- Pydantic request validation returns `422` with `VALIDATION_ERROR`.
- Missing report returns `404` with `REPORT_NOT_FOUND`.
- Missing project returns `404` with `PROJECT_NOT_FOUND`.
- Empty scraper result returns `503` with `SCRAPER_EMPTY_RESULT`.
- Unimplemented scraper provider returns `503` with `SCRAPER_FAILED`.
- Invalid scraper provider config returns `500` with `SCRAPER_PROVIDER_INVALID`.
