# NSPV Development Plan for Codex

本文档用于指导 Codex 分阶段开发 NSPV。每个任务都包含目标、建议修改位置、完成标准和测试方式。

## How Codex Should Use This Document

每次开发前：

1. 先阅读 `docs/v1-scope.md`，确认当前是否属于 V1。
2. 再阅读 `Progress Dashboard` 和本文件对应阶段任务。
3. 创建或切换到任务分支，分支命名建议：`phase-{number}/task-{number}-{short-name}`。
4. 只修改任务涉及的模块，避免扩散到 V2/V3。
5. 每完成一个任务，运行该任务列出的测试。
6. 如果任务影响接口响应，更新 `docs/api-roadmap.md`。
7. 如果任务影响表结构，更新 `docs/db-roadmap.md`。
8. 任务完成后更新本文件中的任务状态、测试状态、分支状态和整体完成度。

## Status Legend

任务状态：

- `[DONE]` 已完成并提交。
- `[IN PROGRESS]` 当前正在执行。
- `[NEXT]` 建议下一个执行。
- `[TODO]` 未开始。
- `[BLOCKED]` 被外部条件阻塞。
- `[DEFERRED]` 明确暂缓。

分支状态：

- `merged` 已合入主分支。
- `active` 当前开发分支。
- `planned` 尚未创建分支。
- `blocked` 分支存在但无法继续。

测试状态：

- `passed` 已运行并通过。
- `not run` 尚未运行。
- `manual` 仅完成手工验证。
- `blocked` 测试无法执行，需要说明原因。

## Progress Dashboard

Last updated: 2026-05-13

Overall V1 progress: 85%

Current branch: `phase-3/task-3.3-scoring-version`

Current branch status: `active`

Remote repository: `https://github.com/hbing0014/NSPV.git`

Latest commits:

- `ef4fa17 Add VSCode workspace`
- `caa2642 Initial NSPV project scaffold`

Current active task: `Task 3.3 Add Scoring Version`

Next recommended task: `Task 4.1 Improve Loading and Error States`

Phase progress:

| Phase | Scope | Status | Progress | Branch Status | Test Status |
| --- | --- | --- | --- | --- | --- |
| Phase 0 | Project bootstrap, docs, Git, VSCode workspace | `[DONE]` | 100% | `merged: main` | `manual` |
| Phase 1 | Stabilize current V1 prototype | `[DONE]` | 100% | `merged: main` | `passed` |
| Phase 2 | Real Amazon data integration | `[DONE]` | 100% | `merged: main` | `passed` |
| Phase 3 | Improve scoring and risk engine | `[DONE]` | 100% | `active: phase-3/task-3.3-scoring-version` | `passed` |
| Phase 4 | Frontend V1 completion | `[NEXT]` | 0% | `planned` | `not run` |
| Phase 5 | Basic auth | `[TODO]` | 0% | `planned` | `not run` |
| Phase 6 | Deployment readiness | `[TODO]` | 0% | `planned` | `not run` |

Task progress:

| Task | Status | Suggested Branch | Branch Status | Test Status |
| --- | --- | --- | --- | --- |
| Task 1.1 Add Backend Test Setup | `[DONE]` | `phase-1/task-1.1-backend-tests` | `merged: main` | `passed` |
| Task 1.2 Add Frontend Test or Smoke Check | `[DONE]` | `phase-1/task-1.2-frontend-smoke` | `merged: main` | `passed` |
| Task 1.3 Normalize API Error Contract | `[DONE]` | `phase-1/task-1.3-api-errors` | `merged: main` | `passed` |
| Task 1.4 Add Project CRUD | `[DONE]` | `phase-1/task-1.4-project-crud` | `merged: main` | `passed` |
| Task 1.5 Add Analysis Input Persistence | `[DONE]` | `phase-1/task-1.5-analysis-persistence` | `merged: main` | `passed` |
| Task 2.1 Define Scraper Interface | `[DONE]` | `phase-2/task-2.1-scraper-interface` | `merged: main` | `passed` |
| Task 2.2 Implement Playwright Amazon Search Scraper | `[DONE]` | `phase-2/task-2.2-playwright-scraper` | `merged: main` | `passed` |
| Task 2.3 Add Scraper Run Logging | `[DONE]` | `phase-2/task-2.3-scraper-logging` | `merged: main` | `passed` |
| Task 3.1 Extract Risk Warning Engine | `[DONE]` | `phase-3/task-3.1-risk-engine` | `merged: main` | `passed` |
| Task 3.2 Add Scoring Fixtures | `[DONE]` | `phase-3/task-3.2-scoring-fixtures` | `merged: main` | `passed` |
| Task 3.3 Add Scoring Version | `[DONE]` | `phase-3/task-3.3-scoring-version` | `active` | `passed` |
| Task 4.1 Improve Loading and Error States | `[NEXT]` | `phase-4/task-4.1-loading-errors` | `planned` | `not run` |
| Task 4.2 Add Project Selection to Home Page | `[TODO]` | `phase-4/task-4.2-project-selection` | `planned` | `not run` |
| Task 4.3 Improve Report Detail Layout | `[TODO]` | `phase-4/task-4.3-report-layout` | `planned` | `not run` |
| Task 5.1 Add Password Hash and JWT | `[TODO]` | `phase-5/task-5.1-auth-jwt` | `planned` | `not run` |
| Task 5.2 Scope Projects and Reports by User | `[TODO]` | `phase-5/task-5.2-user-scope` | `planned` | `not run` |
| Task 6.1 Add Environment Documentation | `[TODO]` | `phase-6/task-6.1-env-docs` | `planned` | `not run` |
| Task 6.2 Add Alembic | `[TODO]` | `phase-6/task-6.2-alembic` | `planned` | `not run` |

## Current Project State

当前已完成：

- FastAPI 后端基础结构
- Next.js 前端基础结构
- SQLite 本地默认数据库
- PostgreSQL docker-compose 配置
- Mock Amazon Top20 数据源
- `POST /api/analyze`
- `GET /api/reports`
- `GET /api/reports/{report_id}`
- `GET /api/projects/{project_id}/reports`
- 报告保存分析输入参数和评分版本
- NSFS 评分引擎基础版
- 首页、报告页、历史报告页

当前主要限制：

- Amazon 数据源仍为 mock。
- 用户系统未真正实现注册登录。
- 前端尚未接入项目选择。
- 缺少真实 scraper 错误处理和监控。

## Phase 1: Stabilize Current V1 Prototype `[IN PROGRESS]`

目标：

- 把当前可运行原型整理成可持续开发的 V1 基线。

### Task 1.1 Add Backend Test Setup `[DONE]`

目标：

- 为 FastAPI 和评分引擎添加测试基础。

建议修改位置：

- `backend/requirements.txt`
- `backend/tests/`
- `backend/tests/test_health.py`
- `backend/tests/test_scoring.py`
- `backend/tests/test_analyze_api.py`

实现要求：

- 添加 `pytest`。
- 添加 FastAPI `TestClient` 测试。
- 测试 `/health` 返回 `{"status": "ok"}`。
- 测试 `POST /api/analyze` 返回 report。
- 测试 NSFS 公式权重计算符合规则。

完成标准：

- `pytest` 可在 `backend` 下运行。
- 测试不依赖外部 Amazon。
- 测试使用临时 SQLite 或独立测试数据库。

测试命令：

```powershell
cd backend
.\.venv\Scripts\pytest
```

Completion record:

- Branch: `phase-1/task-1.1-backend-tests`
- Status: `[DONE]`
- Test result: `30 passed, 2 warnings`
- Notes: warnings are FastAPI `on_event` deprecation warnings and do not block this task.

### Task 1.2 Add Frontend Test or Smoke Check `[DONE]`

目标：

- 确保首页和报告页不会被基础改动破坏。

建议修改位置：

- `frontend/package.json`
- `frontend/tests/`，如果引入测试框架
- 或新增 `docs/testing.md` 记录手工 smoke test

实现要求：

- 至少保留 `npm run build` 作为前端强制测试。
- 如果引入 Playwright，只测试本地页面能打开和提交表单。

完成标准：

- `npm run build` 通过。
- 首页可加载。
- 报告页可加载。

测试命令：

```powershell
cd frontend
npm run build
```

Completion record:

- Branch: `phase-1/task-1.2-frontend-smoke`
- Status: `[DONE]`
- Build result: `npm run build` passed.
- Smoke result: `SMOKE_REPORT_ID=1 npm run smoke` passed for `/`, `/reports`, and `/reports/1`.

### Task 1.3 Normalize API Error Contract `[DONE]`

目标：

- 统一 API 错误返回格式。

建议修改位置：

- `backend/app/api/routes.py`
- `backend/app/schemas/`
- `backend/app/core/`

实现要求：

- 定义错误结构：

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "target_price_min cannot exceed target_price_max",
    "details": {}
  }
}
```

- 至少覆盖：
  - invalid price range
  - report not found
  - scraper empty result
  - scraper failed

完成标准：

- 前端能显示错误 message。
- 后端测试覆盖 400 和 404。

测试命令：

```powershell
cd backend
.\.venv\Scripts\pytest
```

Completion record:

- Branch: `phase-1/task-1.3-api-errors`
- Status: `[DONE]`
- Test result: `31 passed, 2 warnings`
- Error contract: `{"error": {"code": "...", "message": "...", "details": {...}}}`

### Task 1.4 Add Project CRUD `[DONE]`

目标：

- 实现 V1 项目管理基础 API。

建议修改位置：

- `backend/app/api/routes.py`，或拆分 `backend/app/api/projects.py`
- `backend/app/schemas/project.py`
- `backend/app/models/tables.py`
- `frontend/app/projects/`，可后续

API：

```text
POST   /api/projects
GET    /api/projects
GET    /api/projects/{project_id}
PUT    /api/projects/{project_id}
DELETE /api/projects/{project_id}
```

实现要求：

- 创建项目时保存：
  - `project_name`
  - `category`
  - `budget_rmb`
  - `marketplace`
  - `target_price_min`
  - `target_price_max`
- 删除可以先物理删除，也可以软删除。若软删除，需要 `status` 字段。

完成标准：

- API 可创建、查询、更新、删除项目。
- Analyze 可以选择已有 project，或未传时自动创建。

测试命令：

```powershell
cd backend
.\.venv\Scripts\pytest
```

Completion record:

- Branch: `phase-1/task-1.4-project-crud`
- Status: `[DONE]`
- Test result: `35 passed, 2 warnings`
- Database: Supabase MCP migration `002_add_project_crud_fields.sql` applied.
- Notes: Project CRUD supports create, list, detail, update, delete. Analyze can reuse an existing `project_id` or auto-create a project when omitted.

### Task 1.5 Add Analysis Input Persistence `[DONE]`

目标：

- 报告保存完整输入参数，方便回溯。

建议修改位置：

- `backend/app/models/tables.py`
- `backend/app/api/routes.py`
- `backend/app/schemas/analysis.py`
- `docs/db-roadmap.md`

实现要求：

- `selection_reports` 增加：
  - `input_payload`
  - `scoring_version`
  - `analysis_status`
  - `error_message`
- 成功分析保存输入参数。

完成标准：

- `GET /api/reports/{id}` 可返回或内部保留输入参数。
- 旧报告兼容或在本地重建数据库。

测试命令：

```powershell
cd backend
.\.venv\Scripts\pytest
```

Completion record:

- Branch: `phase-1/task-1.5-analysis-persistence`
- Status: `[DONE]`
- Test result: `35 passed, 2 warnings`
- Database: Supabase MCP migration `003_add_analysis_persistence_fields.sql` applied.
- Notes: Reports now save `input_payload`, `scoring_version`, `analysis_status`, and `error_message`. Report detail and report list expose the status metadata.

## Phase 2: Real Amazon Data Integration `[NEXT]`

目标：

- 替换 mock crawler，接入真实 Amazon 搜索数据。

### Task 2.1 Define Scraper Interface `[DONE]`

目标：

- 让评分和 API 不依赖具体数据源。

建议修改位置：

- `backend/app/services/scrapers/base.py`
- `backend/app/services/scrapers/mock.py`
- `backend/app/services/scrapers/playwright_amazon.py`
- `backend/app/services/mock_crawler.py`，迁移或保留兼容

实现要求：

- 定义统一接口：

```python
class SearchScraper(Protocol):
    def fetch_top20_products(self, keyword: str, marketplace: str) -> list[ProductOut]:
        ...
```

- API 通过配置选择：
  - `SCRAPER_PROVIDER=mock`
  - `SCRAPER_PROVIDER=playwright`
  - `SCRAPER_PROVIDER=brightdata`

完成标准：

- mock provider 仍可工作。
- API 不直接 import mock crawler。

测试命令：

```powershell
cd backend
.\.venv\Scripts\pytest
```

Completion record:

- Branch: `phase-2/task-2.1-scraper-interface`
- Status: `[DONE]`
- Test result: `37 passed, 2 warnings`
- Notes: API now uses `get_search_scraper()` and supports `SCRAPER_PROVIDER=mock|playwright|brightdata`. Mock provider remains the default and the only implemented provider in this task.

### Task 2.2 Implement Playwright Amazon Search Scraper `[DONE]`

目标：

- 抓取 Amazon US 搜索结果 Top20。

建议修改位置：

- `backend/app/services/scrapers/playwright_amazon.py`
- `backend/requirements.txt`
- `backend/app/core/config.py`

实现要求：

- 使用 Playwright。
- 输入 keyword 和 marketplace。
- 输出统一 `ProductOut`。
- 提取：
  - `asin`
  - `title`
  - `brand`，如果页面可得
  - `price`
  - `rating`
  - `review_count`
  - `image_url`
  - `product_url`
  - `is_sponsored`
- Top20 不足时返回实际数量，并给出 warning 或 partial status。
- 处理 captcha、空结果、页面结构变化。

完成标准：

- 对 `sink organizer` 能返回商品列表。
- 抓取失败时 API 返回明确错误。
- 不影响 mock provider 测试。

测试命令：

```powershell
cd backend
.\.venv\Scripts\pytest
.\.venv\Scripts\python -m playwright install chromium
```

手工验证：

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/analyze -Method Post -ContentType 'application/json' -Body '{"keyword":"sink organizer","marketplace":"US","category":"Kitchen & Dining","budget_rmb":100000,"target_price_min":20,"target_price_max":40,"exclude_red_ocean":true}'
```

Completion record:

- Branch: `phase-2/task-2.2-playwright-scraper`
- Status: `[DONE]`
- Test result: `40 passed, 2 warnings`
- Build result: `frontend npm run build` passed.
- Manual scraper result: `PlaywrightAmazonSearchScraper().fetch_top20_products("sink organizer", "US")` returned 20 products.
- Notes: Current local Amazon response displays JPY prices by geolocation, so the scraper normalizes JPY to approximate USD for scoring. This should be replaced with proxy/location control or a live FX source before production.

### Task 2.3 Add Scraper Run Logging `[DONE]`

目标：

- 记录抓取状态，便于定位失败。

建议修改位置：

- `backend/app/models/tables.py`
- `backend/app/services/scrapers/`
- `backend/app/api/routes.py`

实现要求：

- 新增 `scraper_runs` 表。
- 保存：
  - keyword
  - marketplace
  - provider
  - status
  - product_count
  - error_message
  - started_at
  - finished_at

完成标准：

- 成功和失败抓取都有记录。
- 报告可关联 scraper run，后续可选。

测试命令：

```powershell
cd backend
.\.venv\Scripts\pytest
```

Completion record:

- Branch: `phase-2/task-2.3-scraper-logging`
- Status: `[DONE]`
- Test result: `41 passed, 2 warnings`
- Database: Supabase MCP migration `004_add_scraper_runs.sql` applied.
- Notes: Successful, empty, and failed scraper attempts are recorded in `scraper_runs`. Reports now include `scraper_run_id`.

## Phase 3: Improve Scoring and Risk Engine `[DONE]`

目标：

- 让 NSFS 更稳定、可解释、可回归测试。

### Task 3.1 Extract Risk Warning Engine `[DONE]`

目标：

- 风险预警从 scoring 中拆出独立模块。

建议修改位置：

- `backend/app/services/risk.py`
- `backend/app/services/scoring.py`
- `backend/tests/test_risk.py`

实现要求：

- 输入 `ScoreDetails`。
- 输出 `warnings[]`。
- 规则覆盖：
  - Top10 平均 Review 过高
  - Sponsored 密度过高
  - Amazon Basics
  - 客单价过低
  - 产品成熟度高
  - 目标售价区间不匹配

完成标准：

- 每条规则有单元测试。
- API 输出不变。

测试命令：

```powershell
cd backend
.\.venv\Scripts\pytest
```

Completion record:

- Branch: `phase-3/task-3.1-risk-engine`
- Status: `[DONE]`
- Test result: `48 passed, 2 warnings`
- Notes: Risk warning rules now live in `backend/app/services/risk.py`; scoring output remains unchanged.

### Task 3.2 Add Scoring Fixtures `[DONE]`

目标：

- 用固定样本验证推荐等级和风险等级。

建议修改位置：

- `backend/tests/fixtures/`
- `backend/tests/test_scoring.py`

测试场景：

- 低 Review、利润高、需求强，应为 Strongly Recommended。
- 高 Review、高广告、Amazon Basics，应为 Avoid 或 Caution。
- 需求中等、竞争中等，应为 Worth Research 或 Caution。

完成标准：

- 评分规则改动时测试能发现推荐等级变化。

测试命令：

```powershell
cd backend
.\.venv\Scripts\pytest
```

Completion record:

- Branch: `phase-3/task-3.2-scoring-fixtures`
- Status: `[DONE]`
- Test result: `51 passed, 2 warnings`
- Notes: Added fixed scoring cases for strong recommendation, red-ocean avoidance, and moderate-market worth-research paths.

### Task 3.3 Add Scoring Version `[DONE]`

目标：

- 每份报告知道使用哪个评分版本。

建议修改位置：

- `backend/app/services/scoring.py`
- `backend/app/models/tables.py`
- `backend/app/api/routes.py`

实现要求：

- 定义 `SCORING_VERSION = "v1.0.0"`。
- 保存到 report。
- 后续评分规则变更时提升版本。

完成标准：

- Report detail 能看到或内部保存评分版本。

测试命令：

```powershell
cd backend
.\.venv\Scripts\pytest
```

Completion record:

- Branch: `phase-3/task-3.3-scoring-version`
- Status: `[DONE]`
- Test result: `51 passed, 2 warnings`
- Notes: Scoring output now carries `scoring_version`; report persistence uses the version returned by the scoring engine.

## Phase 4: Frontend V1 Completion `[NEXT]`

目标：

- 让用户可以完整使用 V1。

### Task 4.1 Improve Loading and Error States `[TODO]`

目标：

- Analyze 过程中显示明确状态，失败时给用户可理解错误。

建议修改位置：

- `frontend/app/page.tsx`
- `frontend/lib/api.ts`

实现要求：

- Analyze 按钮 loading。
- 后端错误显示 `error.message`。
- 抓取失败给出重新尝试提示。

完成标准：

- 后端返回 400/404/503 时前端不会白屏。

测试命令：

```powershell
cd frontend
npm run build
```

### Task 4.2 Add Project Selection to Home Page `[TODO]`

目标：

- 用户可以选择已有项目或创建新项目后分析。

建议修改位置：

- `frontend/app/page.tsx`
- `frontend/lib/api.ts`
- `backend/app/api/projects.py`

实现要求：

- 加载项目列表。
- 表单支持选择 project。
- 未选择时保留自动创建项目逻辑。

完成标准：

- 报告正确关联 project。
- Project reports 页面可看到该项目报告。

### Task 4.3 Improve Report Detail Layout `[TODO]`

目标：

- 结果页能更清晰地回答“能不能做、为什么”。

建议修改位置：

- `frontend/components/ReportView.tsx`

实现要求：

- 顶部突出：
  - NSFS 总分
  - 推荐等级
  - 风险等级
  - 一句话结论
- 中部展示：
  - 四项子分
  - Review 竞争结构
  - 红海预警
  - 利润估算
- 底部展示：
  - Top20 商品列表
  - 操作建议

完成标准：

- 移动端和桌面端文字不重叠。
- Top20 表格可横向滚动。

测试命令：

```powershell
cd frontend
npm run build
```

手工验证：

- 打开 `http://127.0.0.1:3000`
- 提交 `sink organizer`
- 查看结果页
- 查看 `Reports`

## Phase 5: Basic Auth `[TODO]`

目标：

- 支持真实用户注册登录，并将项目和报告归属用户。

### Task 5.1 Add Password Hash and JWT `[TODO]`

建议修改位置：

- `backend/requirements.txt`
- `backend/app/api/auth.py`
- `backend/app/core/security.py`
- `backend/app/models/tables.py`
- `backend/app/schemas/auth.py`

实现要求：

- 使用 password hash。
- 登录返回 JWT。
- `GET /api/auth/profile` 返回当前用户。

完成标准：

- 注册、登录、获取 profile 全流程通过测试。

测试命令：

```powershell
cd backend
.\.venv\Scripts\pytest
```

### Task 5.2 Scope Projects and Reports by User `[TODO]`

目标：

- 用户只能看到自己的项目和报告。

建议修改位置：

- `backend/app/api/routes.py`
- `backend/app/api/projects.py`
- `backend/app/api/auth.py`

实现要求：

- Analyze 需要用户上下文，或支持匿名模式配置。
- Report list 按 user 过滤。
- Project list 按 user 过滤。

完成标准：

- 测试不同用户不能访问彼此报告。

## Phase 6: Deployment Readiness `[TODO]`

目标：

- 可以部署到 Vercel + Render/Railway/Fly.io + Supabase/Neon。

### Task 6.1 Add Environment Documentation `[TODO]`

建议修改位置：

- `README.md`
- `backend/.env.example`
- `frontend/.env.example`
- `docs/deployment.md`

实现要求：

- 记录后端环境变量。
- 记录前端 `NEXT_PUBLIC_API_BASE`。
- 记录 PostgreSQL `DATABASE_URL`。

### Task 6.2 Add Alembic `[TODO]`

目标：

- 用正式 migration 管理数据库。

建议修改位置：

- `backend/alembic.ini`
- `backend/alembic/`
- `backend/requirements.txt`

完成标准：

- 可以生成和执行 migration。
- 生产环境不依赖 `create_all()`。

测试命令：

```powershell
cd backend
.\.venv\Scripts\alembic upgrade head
```

## Definition of Done

任一任务完成必须满足：

- 代码符合现有项目结构。
- 不引入 V1 范围外功能，除非任务明确要求。
- 后端相关任务至少运行 `pytest` 或说明为什么无法运行。
- 前端相关任务至少运行 `npm run build`。
- API 响应变更同步更新文档。
- 数据库结构变更同步更新文档。
- 报告页仍能完成一次关键词分析闭环。
