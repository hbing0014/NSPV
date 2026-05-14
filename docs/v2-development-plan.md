# NSPV V2 开发任务计划

本文档把 V2 Product Discovery Engine 拆成可执行任务。每个任务包含目标、建议分支、改动范围、验收标准和测试方式。执行时应保持 V1 关键词验证功能可用。

## 执行原则

1. V2 不推翻 V1，新增 Discovery Layer。
2. 每个任务使用独立分支，建议命名：`v2/task-{number}-{short-name}`。
3. 每个任务完成后运行后端测试和前端构建，影响页面时运行 smoke。
4. 涉及数据库结构时必须新增 Alembic migration。
5. 涉及 API 输出时同步更新 API 文档。
6. `docs/` 文档继续使用中文。

## 状态图例

| 状态 | 含义 |
| --- | --- |
| `[TODO]` | 未开始 |
| `[NEXT]` | 建议下一个执行 |
| `[IN PROGRESS]` | 正在执行 |
| `[DONE]` | 已完成 |
| `[BLOCKED]` | 被外部条件阻塞 |
| `[DEFERRED]` | 明确暂缓 |

## V2 总体阶段

| 阶段 | 范围 | 状态 | 目标 |
| --- | --- | --- | --- |
| Phase 0 | V2 文档和任务拆分 | `[DONE]` | 固化产品设计和开发计划 |
| Phase 1 | 数据库与模型 | `[IN PROGRESS]` | 建立 Discovery Layer 数据结构 |
| Phase 2 | 种子数据与规则引擎 | `[IN PROGRESS]` | 跑通产品机会生成 |
| Phase 3 | Launch Score 与 NPFS | `[IN PROGRESS]` | 完成 V2 评分闭环 |
| Phase 4 | Product Radar API | `[TODO]` | 提供发现结果接口 |
| Phase 5 | V2 首页与 Radar 页面 | `[TODO]` | 前端 Discover-first 体验 |
| Phase 6 | V1 兼容与验证链路 | `[TODO]` | Product → Validate Keyword |
| Phase 7 | 测试、验收与部署准备 | `[TODO]` | 稳定 V2 MVP |

## Phase 1：数据库与模型

### Task 1.1 新增 V2 Alembic 迁移 `[BLOCKED]`

建议分支：

```text
v2/task-1.1-discovery-schema
```

目标：

- 新增 V2 P0 数据表。
- 给 `selection_reports` 增加 `product_opportunity_id`。

涉及文件：

- `backend/alembic/versions/`
- `backend/app/models/tables.py`
- `docs/db-roadmap.md`

新增表：

- `categories`
- `category_scan_jobs`
- `category_products`
- `product_opportunities`
- `launch_scores`
- `discovery_reports`

字段范围：

- 按 `docs/v2-product-design.md` 的 P0 设计实现。
- JSON 字段使用 SQLAlchemy `JSON`。
- 金额、价格、评分字段使用 `Float`。
- 布尔过滤字段保留默认值。

验收标准：

- Alembic migration 是 V2 数据库结构的唯一正式来源，不再为 Supabase 单独手写结构 SQL。
- 本地 SQLite 测试库执行 `alembic upgrade head` 通过，可创建所有 V2 新表。
- Supabase PostgreSQL 使用同一份 Alembic migration 执行 `alembic upgrade head` 通过。
- Supabase 中可以看到 V2 新表：
  - `categories`
  - `category_scan_jobs`
  - `category_products`
  - `product_opportunities`
  - `launch_scores`
  - `discovery_reports`
- Supabase 的 `alembic_version` 已更新到最新 revision。
- `selection_reports.product_opportunity_id` 可为空。
- 不在 pytest 中直接连接或污染 Supabase；pytest 继续使用隔离测试库。

测试：

```powershell
cd backend
.\.venv\Scripts\alembic upgrade head
.\.venv\Scripts\pytest
```

Supabase 正式迁移验证：

```powershell
cd backend
.\.venv\Scripts\alembic upgrade head
```

说明：

- 上述 Supabase 命令必须在 `backend/.env` 的 `DATABASE_URL` 指向 Supabase PostgreSQL 时执行。
- 如果是全新 Supabase 数据库，直接运行 `alembic upgrade head`。
- 如果数据库已由历史 SQL 手工迁移过，必须先确认当前 `alembic_version` 状态，再决定是否需要 `alembic stamp head`，避免重复建表。

当前状态：

- 本地代码、SQLite Alembic 迁移、pytest、SQLAlchemy mapper 检查已完成。
- Supabase 执行 `alembic current` 时返回数据库密码认证失败，需要更新有效 `DATABASE_URL` 后继续远端迁移验收。

### Task 1.2 新增 V2 Pydantic Schema `[DONE]`

建议分支：

```text
v2/task-1.2-discovery-schemas
```

目标：

- 定义 V2 API 输入输出结构。

涉及文件：

- `backend/app/schemas/discovery.py`

Schema：

- `DiscoveryRequest`
- `ProductOpportunityOut`
- `DiscoveryReportOut`
- `LaunchScoreOut`
- `CategoryOut`

验收标准：

- 所有 V2 API 可复用 schema。
- 字段命名与数据库保持一致。
- `DiscoveryRequest` 支持 V2 首页与 Product Radar 的核心筛选条件。
- 输出 schema 支持 SQLAlchemy ORM 对象转换。

测试：

```powershell
cd backend
.\.venv\Scripts\pytest
```

完成记录：

- 分支：`v2/task-1.2-discovery-schemas`
- 新增：`backend/app/schemas/discovery.py`
- 新增：`backend/tests/test_discovery_schemas.py`
- 验证：`tests/test_discovery_schemas.py` 通过。

## Phase 2：种子数据与规则引擎

### Task 2.1 添加 V2 种子产品池 `[DONE]`

建议分支：

```text
v2/task-2.1-seed-product-pool
```

目标：

- 在真实 Category Scanner 完成前，用稳定 seed 数据验证 V2 产品发现流程。

涉及文件：

- `backend/app/services/discovery/seed_products.py`
- `backend/tests/fixtures/v2_seed_products.json`

数据要求：

- 至少 30 个候选产品。
- 覆盖 Kitchen、Home、Storage 三个 P0 类目。
- 覆盖低风险、中风险、红海、Amazon Basics、过重、易碎、低价等样例。
- 不生成假 Amazon 链接和假图片。

验收标准：

- seed 数据可稳定生成。
- 测试中每次结果一致。
- seed 数据不包含伪 Amazon 链接和伪图片。
- seed 数据覆盖 Kitchen、Home、Storage 三个 P0 类目以及主要规则样本。

测试：

```powershell
cd backend
.\.venv\Scripts\pytest tests\test_discovery_seed.py
```

完成记录：

- 分支：`v2/task-2.1-seed-product-pool`
- 新增：`backend/app/services/discovery/seed_products.py`
- 新增：`backend/tests/fixtures/v2_seed_products.json`
- 新增：`backend/tests/test_discovery_seed.py`
- 验证：`tests/test_discovery_seed.py` 通过。

### Task 2.2 实现 Category Scanner 规则引擎 `[DONE]`

建议分支：

```text
v2/task-2.2-category-scanner-rules
```

目标：

- 实现硬过滤、软过滤、标签生成和输出层级。

涉及文件：

- `backend/app/services/discovery/category_scanner.py`
- `backend/app/services/discovery/rules.py`
- `backend/tests/test_category_scanner.py`

规则：

- 价格 `<15` 排除。
- 价格 `>80` 默认排除。
- Top10 Avg Reviews `>1500` 默认排除。
- Amazon Basics 默认排除。
- 重量 `>1kg` 默认排除。
- 易碎默认排除。
- 强季节性默认排除。
- Sponsored Density、Avg Rating、Lowest Review Top10 作为软过滤和标签依据。

输出层级：

- `Rejected`
- `Research`
- `Opportunity`

验收标准：

- 每条规则有单元测试。
- 每个样例产品有可解释标签。
- Opportunity 产品不会包含默认硬过滤失败项。
- 支持默认严格过滤，也支持关闭部分排除规则进入人工研究。
- 输出结果稳定分为 `Rejected`、`Research`、`Opportunity` 三层。

测试：

```powershell
cd backend
.\.venv\Scripts\pytest tests\test_category_scanner.py
```

完成记录：

- 分支：`v2/task-2.2-category-scanner-rules`
- 新增：`backend/app/services/discovery/rules.py`
- 新增：`backend/app/services/discovery/category_scanner.py`
- 新增：`backend/tests/test_category_scanner.py`
- 验证：`tests/test_category_scanner.py` 通过。

### Task 2.3 实现关键词生成器 `[DONE]`

建议分支：

```text
v2/task-2.3-keyword-cluster-generator
```

目标：

- 从产品名生成 `primary_keyword`、`secondary_keywords`、`long_tail_keywords`。

涉及文件：

- `backend/app/services/discovery/keyword_clusters.py`
- `backend/tests/test_keyword_clusters.py`

V2 MVP 规则：

- 清理品牌词、尺寸词、营销词。
- 生成主关键词。
- 用类目模板生成长尾词。

验收标准：

- `Under Sink Organizer` 可生成：
  - `primary_keyword = under sink organizer`
  - secondary 包含 `sink organizer`
  - long tail 包含厨房/收纳语义。
- 能清理品牌词、尺寸词和营销词。
- 所有 seed 产品都能生成非空关键词聚类。
- 同一批 seed 产品多次生成结果一致。

测试：

```powershell
cd backend
.\.venv\Scripts\pytest tests\test_keyword_clusters.py
```

完成记录：

- 分支：`v2/task-2.3-keyword-cluster-generator`
- 新增：`backend/app/services/discovery/keyword_clusters.py`
- 新增：`backend/tests/test_keyword_clusters.py`
- 验证：`tests/test_keyword_clusters.py` 通过。

## Phase 3：Launch Score 与 NPFS

### Task 3.1 实现 Launch Score Engine `[DONE]`

建议分支：

```text
v2/task-3.1-launch-score-engine
```

目标：

- 按 PRD 公式实现 Launch Score。

涉及文件：

- `backend/app/services/discovery/launch_score.py`
- `backend/tests/test_launch_score.py`

维度：

- Budget Feasibility
- PPC Launch Difficulty
- Review Acquisition Difficulty
- MOQ Accessibility
- Inventory Pressure
- Operational Complexity

验收标准：

- 输出总分和 6 个子分。
- 输出预算建议。
- 输出风险标签。
- 覆盖 Sink Organizer 和 Air Fryer Accessory Set 两个典型样例。
- 子分按 PRD 阈值可单独测试。
- 输出启动天数、回本天数和预算拆解。

测试：

```powershell
cd backend
.\.venv\Scripts\pytest tests\test_launch_score.py
```

完成记录：

- 分支：`v2/task-3.1-launch-score-engine`
- 新增：`backend/app/services/discovery/launch_score.py`
- 新增：`backend/tests/test_launch_score.py`
- 验证：`tests/test_launch_score.py` 通过。

### Task 3.2 实现 Supplier Score 简化版 `[DONE]`

建议分支：

```text
v2/task-3.2-supplier-score-lite
```

目标：

- 在无真实 1688 数据前，用规则估算 Supplier Score。

涉及文件：

- `backend/app/services/discovery/supplier_score.py`
- `backend/tests/test_supplier_score.py`

规则输入：

- MOQ
- 产品复杂度
- 是否模具开发
- 包装复杂度
- 供应链成熟度估算

验收标准：

- 低 MOQ、标准件得分高。
- 模具复杂、高 MOQ 得分低。
- 输出供应商数量、MOQ、价格稳定、模具、包装、成熟度 6 个子分。
- 输出供应链等级和风险标签。

测试：

```powershell
cd backend
.\.venv\Scripts\pytest tests\test_supplier_score.py
```

完成记录：

- 分支：`v2/task-3.2-supplier-score-lite`
- 新增：`backend/app/services/discovery/supplier_score.py`
- 新增：`backend/tests/test_supplier_score.py`
- 验证：`tests/test_supplier_score.py` 通过。

### Task 3.3 实现 NPFS Engine `[DONE]`

建议分支：

```text
v2/task-3.3-npfs-engine
```

目标：

- 整合 V1 四项分数、Launch Score、Supplier Score。

涉及文件：

- `backend/app/services/discovery/npfs.py`
- `backend/tests/test_npfs.py`

公式：

```text
NPFS =
Demand × 0.20 +
Competition × 0.25 +
Profit × 0.20 +
Opportunity × 0.15 +
Launch × 0.10 +
Supplier × 0.10
```

验收标准：

- 输出 `npfs_score`。
- 输出推荐等级：
  - `strongly_recommended`
  - `worth_research`
  - `caution`
  - `avoid`
- 输出风险等级。
- 输出各维度加权贡献，便于报告解释。
- 对异常子分做 0-100 裁剪。
- 风险 warning 会影响 `risk_level`。

测试：

```powershell
cd backend
.\.venv\Scripts\pytest tests\test_npfs.py
```

完成记录：

- 分支：`v2/task-3.3-npfs-engine`
- 新增：`backend/app/services/discovery/npfs.py`
- 新增：`backend/tests/test_npfs.py`
- 验证：`tests/test_npfs.py` 通过。

## Phase 4：Product Radar API

### Task 4.1 新增 Discover API `[DONE]`

建议分支：

```text
v2/task-4.1-discover-api
```

目标：

- 用户输入条件，返回推荐产品列表。

新增 API：

```text
POST /api/discover/products
```

Request：

```json
{
  "category": "Kitchen & Dining",
  "budget_rmb": 100000,
  "risk_preference": "low",
  "price_min": 20,
  "price_max": 40,
  "weight_limit_g": 500,
  "exclude_red_ocean": true,
  "exclude_amazon_basics": true,
  "exclude_fragile": true,
  "exclude_seasonal": true
}
```

Response：

- `discovery_report_id`
- `total_products_scanned`
- `total_products_filtered`
- `total_recommendations`
- `products[]`

验收标准：

- 可基于 seed 数据返回产品机会。
- 返回结果按 `npfs_score DESC` 排序。
- 保存 `discovery_reports`。
- 保存 `product_opportunities`，供后续 Radar API 复用。
- 支持空结果，返回空产品列表而不是报错。
- 支持复用已有项目或自动创建 Discovery 项目。

测试：

```powershell
cd backend
.\.venv\Scripts\pytest tests\test_discover_api.py
```

完成记录：

- 分支：`v2/task-4.1-discover-api`
- 新增：`backend/app/services/discovery/discovery_service.py`
- 更新：`backend/app/api/routes.py`
- 更新：`backend/app/schemas/discovery.py`
- 新增：`backend/tests/test_discover_api.py`
- 验证：`tests/test_discover_api.py` 通过。

### Task 4.2 新增 Product Radar API `[DONE]`

建议分支：

```text
v2/task-4.2-product-radar-api
```

目标：

- 为 Radar 页面提供榜单数据。

新增 API：

```text
GET /api/radar/products
GET /api/radar/products/{opportunity_id}
```

支持 query：

- `category`
- `risk_level`
- `budget_max`
- `price_min`
- `price_max`
- `sort`
- `limit`

验收标准：

- 支持默认 Top Product Opportunities。
- 支持排序：
  - `highest_npfs`
  - `lowest_risk`
  - `lowest_budget`
  - `highest_profit`
  - `easiest_launch`
- 支持类目、风险、预算、价格区间筛选。
- 支持产品机会详情查询和不存在时 404。
- Discover API 保存的机会产品可被 Radar 按类目查询。

测试：

```powershell
cd backend
.\.venv\Scripts\pytest tests\test_radar_api.py
```

完成记录：

- 分支：`v2/task-4.2-product-radar-api`
- 更新：`backend/app/api/routes.py`
- 更新：`backend/app/schemas/discovery.py`
- 新增：`backend/tests/test_radar_api.py`
- 验证：`tests/test_radar_api.py` 通过。

## Phase 5：V2 首页与 Radar 页面

### Task 5.1 迁移 V1 首页到 `/validate` `[DONE]`

建议分支：

```text
v2/task-5.1-validate-page
```

目标：

- 保留 V1 关键词验证能力。
- 为 V2 首页腾出 `/`。

涉及文件：

- `frontend/app/page.tsx`
- `frontend/app/validate/page.tsx`
- `frontend/components/Header.tsx`

验收标准：

- `/validate` 保持原 V1 关键词分析流程。
- `/reports/{id}` 仍可打开。
- Header 有 `Discover Products` 和 `Validate Keyword`。
- `/` 已释放为 V2 Discover 入口。
- 历史报告页和报告详情页的“新分析”入口指向 `/validate`。

测试：

```powershell
cd frontend
npm run build
```

完成记录：

- 分支：`v2/task-5.1-validate-page`
- 新增：`frontend/app/validate/page.tsx`
- 更新：`frontend/app/page.tsx`
- 更新：`frontend/components/Header.tsx`
- 更新：`frontend/lib/i18n/dictionaries.ts`
- 验证：`npm run build` 通过。

### Task 5.2 实现 V2 首页 Hero 和 Smart Filter `[DONE]`

建议分支：

```text
v2/task-5.2-discovery-home
```

目标：

- `/` 变成 Product Discovery 首页。

模块：

- Top Navigation
- Hero Section
- Smart Filter Section

Hero 字段：

- Category
- Budget
- Risk Preference
- Price Range
- Weight Limit

验收标准：

- 用户 30 秒内可完成选择并点击 `Discover Products`。
- 点击后跳转 `/radar` 或调用 Discover API。
- `Validate My Keyword` 可进入 `/validate`。
- 首页支持类目、预算、风险、价格、重量和智能筛选项。
- Discover API 调用成功后展示推荐数量和首个产品机会。
- 加载和错误状态有明确反馈。

测试：

```powershell
cd frontend
npm run build
npm run smoke
```

完成记录：

- 分支：`v2/task-5.2-discovery-home`
- 更新：`frontend/app/page.tsx`
- 更新：`frontend/lib/api.ts`
- 更新：`frontend/lib/i18n/dictionaries.ts`
- 更新：`frontend/scripts/smoke-check.mjs`
- 验证：`npm run build`、`npm run smoke` 通过。

### Task 5.3 实现 Product Opportunity Card `[DONE]`

建议分支：

```text
v2/task-5.3-product-opportunity-card
```

目标：

- 展示 V2 产品机会卡片。

涉及文件：

- `frontend/components/ProductOpportunityCard.tsx`

展示字段：

- Product Name
- Primary Keyword
- Category
- Avg Price
- NPFS Score
- Launch Score
- Risk Level
- Estimated Budget
- Tags

CTA：

- `View Detail`
- `Validate Keyword`
- `Save`

验收标准：

- mock/seed 产品可以稳定展示。
- 无图片时使用安全 fallback，不显示破图。
- 无真实链接时不渲染无效外链。
- 卡片展示 Product Name、Primary Keyword、Category、Avg Price、NPFS、Launch、Risk、Budget、Tags。
- CTA 包含 View Detail、Validate Keyword、Save。
- 首页 Discover 成功后使用该组件展示首个机会产品。

测试：

```powershell
cd frontend
npm run build
```

完成记录：

- 分支：`v2/task-5.3-product-opportunity-card`
- 新增：`frontend/components/ProductOpportunityCard.tsx`
- 更新：`frontend/app/page.tsx`
- 更新：`frontend/lib/i18n/dictionaries.ts`
- 验证：`npm run build` 通过。

### Task 5.4 实现 `/radar` 页面 `[DONE]`

建议分支：

```text
v2/task-5.4-radar-page
```

目标：

- 展示产品机会榜单。

模块：

- 筛选器
- 排序
- 产品卡片列表
- 结果摘要

验收标准：

- 默认展示 Top Product Opportunities。
- 筛选条件可影响 API 请求。
- 排序可切换。
- 页面包含结果摘要、筛选器、排序器和产品机会卡片列表。
- 空结果和加载失败有明确状态。
- smoke 覆盖 `/radar` 路由。

测试：

```powershell
cd frontend
npm run build
npm run smoke
```

完成记录：

- 分支：`v2/task-5.4-radar-page`
- 新增：`frontend/app/radar/page.tsx`
- 更新：`frontend/lib/api.ts`
- 更新：`frontend/components/ProductOpportunityCard.tsx`
- 更新：`frontend/lib/i18n/dictionaries.ts`
- 更新：`frontend/scripts/smoke-check.mjs`
- 验证：`npm run build`、`npm run smoke` 通过。

## Phase 6：V1 兼容与验证链路

### Task 6.1 实现 Validate Keyword CTA `[NEXT]`

建议分支：

```text
v2/task-6.1-product-to-validate
```

目标：

- 从 V2 产品卡片进入 V1 关键词验证。

方案：

- 点击 `Validate Keyword` 后携带：
  - `primary_keyword`
  - `category`
  - `budget_rmb`
  - `target_price_min`
  - `target_price_max`
  - `product_opportunity_id`

可选路径：

```text
/validate?keyword=under%20sink%20organizer&product_opportunity_id=1
```

验收标准：

- `/validate` 自动填入产品关键词。
- Analyze 成功后生成 V1 报告。
- 报告保存 `product_opportunity_id`。

测试：

```powershell
cd backend
.\.venv\Scripts\pytest
cd ..\frontend
npm run build
```

### Task 6.2 新增 Product Detail 页面 `[TODO]`

建议分支：

```text
v2/task-6.2-product-detail
```

目标：

- 用户可查看产品机会详情。

路径：

```text
/radar/products/{opportunity_id}
```

展示：

- 产品总览
- Keyword Cluster
- Top10 竞争结构
- 利润分析
- Launch Budget
- Supplier Score
- 差异化建议
- 风险预警
- Validate 入口

验收标准：

- 可以从产品卡片进入详情页。
- 详情页可以进入 `/validate`。

测试：

```powershell
cd frontend
npm run build
```

## Phase 7：测试、验收与部署准备

### Task 7.1 增加 V2 后端完整测试套件 `[TODO]`

建议分支：

```text
v2/task-7.1-v2-backend-tests
```

覆盖：

- Category Scanner rules
- Launch Score
- Supplier Score
- NPFS
- Discover API
- Radar API
- Product → Validate linkage

验收标准：

- 后端测试覆盖 V2 核心规则。
- 固定样例得分稳定。

测试：

```powershell
cd backend
.\.venv\Scripts\pytest
```

### Task 7.2 增加 V2 前端 smoke `[TODO]`

建议分支：

```text
v2/task-7.2-v2-frontend-smoke
```

覆盖路径：

- `/`
- `/validate`
- `/radar`
- `/radar/products/{id}`
- `/reports/{id}`

验收标准：

- 首页能显示 Discovery Hero。
- Radar 能显示产品机会卡片。
- Validate Keyword 可进入 V1 分析流程。

测试：

```powershell
cd frontend
npm run smoke
```

### Task 7.3 更新部署和环境文档 `[TODO]`

建议分支：

```text
v2/task-7.3-v2-docs
```

目标：

- 更新 V2 API、数据库和部署说明。

涉及文件：

- `docs/api-roadmap.md`
- `docs/db-roadmap.md`
- `docs/deployment.md`
- `docs/testing.md`

验收标准：

- 新 API 有请求和响应示例。
- 新表有字段说明。
- V2 smoke 有测试步骤。

## V2 MVP 验收清单

V2 MVP 完成时必须验证：

- `/` 是 Product Discovery 首页。
- `/validate` 保留 V1 关键词验证。
- 用户可以按类目、预算、风险、价格、重量发现产品。
- Radar 页面返回产品机会卡片。
- Product Opportunity 包含 NPFS、Launch Score、预算、风险和标签。
- 点击 `Validate Keyword` 可以进入 V1 流程。
- V1 报告能关联 V2 `product_opportunity_id`。
- 后端 V2 测试通过。
- 前端 build 通过。
- 前端 smoke 通过。
- mock/seed 数据不生成假图片和无效 Amazon 链接。
