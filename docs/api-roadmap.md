# NSPV API 路线图

本文档定义 NSPV API 从当前原型到 V1、V2、V3 的演进规划。

## API 设计原则

- V1 优先完成单关键词分析闭环。
- API 输出必须可解释，不能只返回一个分数。
- 抓取失败、无结果、字段缺失必须返回明确错误。
- 后续 AI、支付、开放平台不得污染 V1 核心路径。
- 内部 API 和开放 API 分开规划，V1 不做第三方开放平台。

## 当前已实现 API

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

当前 `POST /api/analyze` 默认使用 mock Amazon Top20 数据源，用于打通业务闭环。

Scraper provider 由后端配置选择：

```text
SCRAPER_PROVIDER=mock
SCRAPER_PROVIDER=playwright
SCRAPER_PROVIDER=brightdata
```

当前已实现：

- `mock`：确定性的本地商品数据，用于稳定开发和测试。
- `playwright`：抓取实时 Amazon US 搜索页 Top20 商品卡片。

`brightdata` 仍是占位 provider，正式实现前会返回结构化抓取失败。

Playwright 抓取器说明：

- 需要执行 `python -m playwright install chromium`。
- 提取 ASIN、标题、价格、评分、Review 数、图片 URL、商品 URL 和广告状态。
- Amazon 可能根据运行网络位置渲染本地货币。当前抓取器会将 JPY 粗略换算为 USD 参与评分；生产环境应使用美国代理/地区控制或实时汇率来源。

## V1 API 目标

### 关键词分析

推荐最终路径：

```text
POST /api/analyze/keyword
```

兼容当前路径：

```text
POST /api/analyze
```

请求：

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

响应：

```json
{
  "report_id": 1,
  "project_id": 1,
  "keyword_id": 1,
  "scraper_run_id": 1,
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

V1 必需行为：

- 校验 `target_price_min <= target_price_max`。
- 校验 `marketplace = US`。
- 无效输入返回 `400`。
- 抓取器或数据 provider 失败时返回 `502` 或 `503`。
- 分析成功时保存报告。
- 如果传入 `project_id`，报告归属到该项目。
- 如果未传 `project_id`，根据分析输入自动创建项目。
- 在报告中保存 `input_payload`、`scoring_version`、`analysis_status` 和 `error_message`。
- 对成功、空结果和失败的抓取尝试保存 `scraper_runs` 记录。

### 报告详情

```text
GET /api/reports/{report_id}
```

V1 必需行为：

- 返回完整报告详情。
- 包含分析时使用的商品快照。
- 包含分析输入和评分版本元数据。
- 报告由抓取运行创建时包含 `scraper_run_id`。
- 报告不存在时返回 `404`。

### 报告列表

```text
GET /api/reports
```

V1 必需行为：

- 返回最新报告。
- 包含 `analysis_status`。
- 包含 `scraper_run_id`。
- 为后续分页字段预留支持：
  - `limit`
  - `offset`
  - `project_id`
  - `keyword`

### 项目报告

```text
GET /api/projects/{project_id}/reports
```

V1 必需行为：

- 返回某个项目下的报告。
- 无报告时返回空列表。

## V1 项目 API

已实现：

```text
POST   /api/projects
GET    /api/projects
GET    /api/projects/{project_id}
PUT    /api/projects/{project_id}
DELETE /api/projects/{project_id}
```

项目创建请求：

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

V1 项目 API 可以支持匿名或默认用户模式。在核心分析流程稳定之前，不要求完整认证。

项目更新支持部分字段。创建或更新时，`target_price_min` 不能大于 `target_price_max`。

## V1 基础认证 API

V1 阶段可选，但对外部用户开放前必须完成：

```text
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/profile
PUT  /api/auth/profile
```

注册请求：

```json
{
  "email": "seller@example.com",
  "password": "safe-password-123",
  "name": "New Seller"
}
```

登录请求：

```json
{
  "email": "seller@example.com",
  "password": "safe-password-123"
}
```

认证响应：

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "seller@example.com",
    "name": "New Seller",
    "plan_type": "free",
    "created_at": "2026-05-14T00:00:00Z",
    "updated_at": "2026-05-14T00:00:00Z"
  }
}
```

用户资料请求：

```text
Authorization: Bearer {access_token}
```

V1 基础认证行为：

- 密码哈希。
- JWT access token。
- 当前用户资料。
- 已认证时，报告和项目按 bearer token 用户隔离。
- 匿名请求仍受支持，但只能访问匿名项目和报告。

暂缓：

- 邮箱验证。
- 密码重置。
- OAuth 登录。
- API Key 管理。

## V2 API

### Review NLP

```text
POST /api/reviews/analyze
GET  /api/reviews/analysis/{analysis_id}
```

用途：

- 分析差评。
- 提取痛点。
- 生成升级建议。

### 多关键词

```text
POST /api/analyze/keywords
```

用途：

- 在一个任务中分析多个关键词。
- 应使用任务队列。

### 导出

```text
GET /api/reports/{report_id}/export/pdf
GET /api/reports/{report_id}/export/xlsx
```

### 历史趋势

```text
GET /api/keywords/{keyword_id}/history
GET /api/products/{asin}/history
```

## V3 API

### 开放 API 平台

```text
POST /api/developer/api-keys
GET  /api/developer/api-keys
DELETE /api/developer/api-keys/{key_id}
```

开放 API 示例：

```text
POST /v1/analyze
GET  /v1/reports/{report_id}
GET  /v1/keywords/{keyword}
```

### 订阅支付

```text
POST /api/billing/checkout
POST /api/billing/portal
POST /api/billing/webhooks/stripe
GET  /api/billing/subscription
```

### Chrome 插件

```text
POST /api/extension/analyze-page
POST /api/extension/analyze-asin
```

## 错误契约

所有 API 错误最终应使用以下结构：

```json
{
  "error": {
    "code": "SCRAPER_FAILED",
    "message": "Amazon search results could not be fetched.",
    "details": {}
  }
}
```

建议错误码：

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

当前已实现：

- Analyze 价格区间无效时返回 `400` 和 `VALIDATION_ERROR`。
- Pydantic 请求校验失败时返回 `422` 和 `VALIDATION_ERROR`。
- 报告不存在时返回 `404` 和 `REPORT_NOT_FOUND`。
- 项目不存在时返回 `404` 和 `PROJECT_NOT_FOUND`。
- 抓取结果为空时返回 `503` 和 `SCRAPER_EMPTY_RESULT`。
- 未实现的 scraper provider 返回 `503` 和 `SCRAPER_FAILED`。
- scraper provider 配置无效时返回 `500` 和 `SCRAPER_PROVIDER_INVALID`。
