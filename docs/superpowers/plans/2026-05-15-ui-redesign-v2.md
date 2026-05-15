# NSPV V2 UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不改变 NSPV V2 业务逻辑、接口和数据结构的前提下，将现有 UI 改造成更专业的 B2B SaaS 数据决策平台和产品机会雷达。

**Architecture:** 保留现有 Next.js App Router 页面、API 调用和 i18n 数据结构，先补齐共享 UI primitives 和页面布局组件，再逐页替换裸 Tailwind 表单、卡片、表格和状态展示。所有页面继续使用 `frontend/lib/api.ts` 中的既有接口函数，不改后端协议。

**Tech Stack:** Next.js 16, React 19, Tailwind CSS 3.4, TypeScript, lucide-react, FastAPI, pytest, gstack browser QA.

---

## 执行边界

- 不改后端业务逻辑、数据库模型、API 路由或响应结构。
- 不删除已有功能、页面、接口调用或多语言能力。
- 不在 `main` 直接开发。执行前创建 `feature/ui-redesign-v2` 隔离分支或 worktree。
- 不提交 `.codex/`、`.gstack/`、`.next/`、`node_modules/`、`backend/.venv/`。
- 遵守 `AGENTS.md`：禁止批量删除文件或目录，不使用 `Remove-Item -Recurse`、`rm -rf`、`rmdir /s` 等命令。

## 文件职责

- `frontend/app/globals.css`：全局 CSS token、body 背景、focus、基础控件样式。
- `frontend/tailwind.config.ts`：设计 token 映射、阴影、radius、语义色。
- `frontend/components/ui/*`：共享组件。允许新增 `badge.tsx`、`metric-card.tsx`、`page-shell.tsx`、`section-header.tsx`、`filter-panel.tsx`、`empty-state.tsx`、`status-alert.tsx`、`score-pill.tsx`。
- `frontend/components/Header.tsx`：全局导航组合层，继续使用 `LanguageSwitcher`。
- `frontend/components/ProductOpportunityCard.tsx`：Radar 产品机会卡。
- `frontend/components/ReportView.tsx`：V1 报告详情数据展示。
- `frontend/components/ScoreGauge.tsx`：评分条展示组件。
- `frontend/app/page.tsx`：V2 Discover 首页。
- `frontend/app/radar/page.tsx`：Product Radar 页面。
- `frontend/app/radar/products/[id]/page.tsx`：产品详情页。
- `frontend/app/validate/page.tsx`：V1 Keyword Validator。
- `frontend/app/reports/page.tsx`：历史报告列表。
- `frontend/app/reports/[id]/page.tsx`：报告详情入口。
- `frontend/scripts/smoke-check.mjs`：保持现有 smoke 流程，必要时只补充 UI 文案检查，不改变业务种子逻辑。

## 全局验证命令

在每个主要任务后至少运行相关子集，阶段完成后运行完整集合：

```powershell
cd D:\aws\frontend
npm run lint
npx tsc --noEmit
npm run build
npm run smoke
```

```powershell
cd D:\aws\backend
pytest
```

gstack QA 在前后端启动后执行：

```bash
$B goto http://127.0.0.1:3000/
$B snapshot -i
$B console --errors
$B responsive C:/Users/ice/AppData/Local/Temp/nspv-ui-home
$B goto http://127.0.0.1:3000/radar
$B snapshot -i
$B console --errors
```

---

### Task 0: 创建隔离分支 / Worktree

**Files:**
- 不修改业务文件。

- [ ] **Step 1: 确认 main 干净且已同步远程**

Run:

```powershell
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
```

Expected:

```text
## main...origin/main
HEAD 与 origin/main hash 一致
```

- [ ] **Step 2: 创建 UI redesign 分支**

Run:

```powershell
git switch -c feature/ui-redesign-v2
```

Expected:

```text
Switched to a new branch 'feature/ui-redesign-v2'
```

- [ ] **Step 3: 再次确认工作区干净**

Run:

```powershell
git status --short --branch
```

Expected:

```text
## feature/ui-redesign-v2
```

---

### Task 1: 设计系统和共享 UI primitives

**Files:**
- Modify: `frontend/app/globals.css`
- Modify: `frontend/tailwind.config.ts`
- Modify: `frontend/components/ui/button.tsx`
- Modify: `frontend/components/ui/input.tsx`
- Modify: `frontend/components/ui/select.tsx`
- Modify: `frontend/components/ui/card.tsx`
- Modify: `frontend/components/ui/table.tsx`
- Modify: `frontend/components/ui/tabs.tsx`
- Modify: `frontend/components/ui/modal.tsx`
- Modify: `frontend/components/ui/sidebar.tsx`
- Modify: `frontend/components/ui/header.tsx`
- Modify: `frontend/components/ui/index.ts`
- Create: `frontend/components/ui/badge.tsx`
- Create: `frontend/components/ui/metric-card.tsx`
- Create: `frontend/components/ui/page-shell.tsx`
- Create: `frontend/components/ui/section-header.tsx`
- Create: `frontend/components/ui/filter-panel.tsx`
- Create: `frontend/components/ui/empty-state.tsx`
- Create: `frontend/components/ui/status-alert.tsx`
- Create: `frontend/components/ui/score-pill.tsx`

- [ ] **Step 1: 固化 design tokens**

要求：

- `background` 保持浅灰工作台背景。
- `card` 保持白色卡片背景。
- `primary` 用于主品牌和导航。
- `accent` 用于产品发现核心 CTA。
- `success/warning/destructive` 分别用于低风险、中风险、高风险。
- 保持 `.dark` token，但本阶段不强制新增暗色切换入口。

Run:

```powershell
cd D:\aws\frontend
npx tsc --noEmit
```

Expected:

```text
TypeScript 无类型错误
```

- [ ] **Step 2: 新增 Badge 和 ScorePill**

组件行为：

- `Badge` 支持 `neutral | accent | success | warning | danger`。
- `ScorePill` 接收 `label`、`value`、`tone`，用于 NPFS、Launch、Risk。
- 不在组件内写业务判断，业务判断留给页面或业务组件。

Run:

```powershell
cd D:\aws\frontend
npx tsc --noEmit
```

Expected:

```text
新增组件可被 TypeScript 正确导出和引用
```

- [ ] **Step 3: 新增页面布局组件**

组件行为：

- `PageShell`：统一 `main` 容器宽度、padding、垂直间距。
- `SectionHeader`：统一 eyebrow、title、description、actions。
- `FilterPanel`：统一筛选区标题、内容区和 footer actions。
- `EmptyState`：统一空状态图标、标题、描述、CTA。
- `StatusAlert`：统一错误、警告、成功提示。

Run:

```powershell
cd D:\aws\frontend
npx tsc --noEmit
npm run build
```

Expected:

```text
Next.js build successful
```

- [ ] **Step 4: 提交基础组件**

Run:

```powershell
git add frontend/app/globals.css frontend/tailwind.config.ts frontend/components/ui
git commit -m "feat: add ui redesign primitives"
```

Expected:

```text
Commit created
```

---

### Task 2: Header 和全局页面骨架

**Files:**
- Modify: `frontend/components/Header.tsx`
- Modify: `frontend/components/LanguageSwitcher.tsx`
- Modify: `frontend/app/layout.tsx`

- [ ] **Step 1: Header 使用统一组件**

要求：

- 保留 `NSPV` logo。
- 保留 Discover、Validate、Reports。
- 保留语言切换。
- 当前路径可标识 active 状态。
- 移动端不横向溢出。

Run:

```powershell
cd D:\aws\frontend
npx tsc --noEmit
npm run build
```

Expected:

```text
Header 编译通过
```

- [ ] **Step 2: gstack Header 快速 QA**

Run after dev server starts:

```bash
$B goto http://127.0.0.1:3000/
$B snapshot -i
$B console --errors
```

Expected:

```text
导航链接和语言选择器可见；console 无新增前端错误
```

- [ ] **Step 3: 提交 Header 改造**

Run:

```powershell
git add frontend/components/Header.tsx frontend/components/LanguageSwitcher.tsx frontend/app/layout.tsx
git commit -m "feat: refine app header layout"
```

---

### Task 3: V2 Discover 首页改造

**Files:**
- Modify: `frontend/app/page.tsx`

- [ ] **Step 1: 保留现有表单状态和跳转逻辑**

不得改变：

- `category`
- `budget_max`
- `risk_preference`
- `price_min`
- `price_max`
- `weight_limit_g`
- `exclude_red_ocean`
- `exclude_amazon_basics`
- `exclude_fragile`
- `exclude_seasonal`
- `low_moq_only`
- `easy_launch_only`
- `high_margin_only`
- `window.location.assign('/radar?...')`

- [ ] **Step 2: 使用 UI primitives 改造视觉结构**

结构：

- `PageShell`
- `SectionHeader`
- 左侧价值说明和 CTA。
- 右侧 `FilterPanel`。
- 筛选项使用 `Field + Select + Input`。
- CTA 使用 `Button`，loading 使用 `Button loading`。

Run:

```powershell
cd D:\aws\frontend
npx tsc --noEmit
npm run build
```

Expected:

```text
首页编译通过；Discover 表单仍生成 /radar query
```

- [ ] **Step 3: gstack 验证 Discover 跳转**

Run:

```bash
$B goto http://127.0.0.1:3000/
$B snapshot -i
$B click "@e_discover_button"
$B url
$B console --errors
```

Expected:

```text
URL 进入 /radar?...；console 无新增错误
```

如果 gstack ref 不是 `@e_discover_button`，先运行 `$B snapshot -i`，使用实际按钮 ref。

- [ ] **Step 4: 提交首页改造**

Run:

```powershell
git add frontend/app/page.tsx
git commit -m "feat: redesign discovery homepage"
```

---

### Task 4: Product Radar 页面和产品机会卡

**Files:**
- Modify: `frontend/app/radar/page.tsx`
- Modify: `frontend/components/ProductOpportunityCard.tsx`

- [ ] **Step 1: 保留 Radar 数据逻辑**

不得改变：

- `getRadarProducts`
- `discoverProducts`
- `autoDiscoverIfEmpty`
- `readBooleanParam`
- `readRiskPreference`
- `sortOptions`
- `ProductOpportunityCard` 的 `validateHref`

- [ ] **Step 2: 改造 Radar 筛选器**

要求：

- 顶部显示总数和当前排序。
- 筛选器使用 `FilterPanel`。
- 数字字段使用 `Field + Input`。
- 下拉字段使用 `Field + Select`。
- Apply 使用 `Button`。

- [ ] **Step 3: 改造产品机会卡**

要求：

- 左侧产品占位图或图像区域稳定尺寸。
- 标题区显示 category、product_name、primary_keyword。
- 评分区突出 `NPFS`、`Launch`、`Risk`、`Budget`。
- Tags 使用 `Badge`。
- CTA：`View Detail`、`Validate Keyword`、`Save`。
- `Save` 保持按钮，不新增业务行为。

Run:

```powershell
cd D:\aws\frontend
npx tsc --noEmit
npm run build
```

Expected:

```text
Radar 页面和产品卡编译通过
```

- [ ] **Step 4: gstack Radar QA**

Run:

```bash
$B goto http://127.0.0.1:3000/radar
$B snapshot -i
$B console --errors
$B responsive C:/Users/ice/AppData/Local/Temp/nspv-ui-radar
```

Expected:

```text
筛选器、产品卡、CTA 可见；移动端无水平溢出；console 无新增错误
```

- [ ] **Step 5: 提交 Radar 改造**

Run:

```powershell
git add frontend/app/radar/page.tsx frontend/components/ProductOpportunityCard.tsx
git commit -m "feat: redesign product radar experience"
```

---

### Task 5: 产品详情页改造

**Files:**
- Modify: `frontend/app/radar/products/[id]/page.tsx`

- [ ] **Step 1: 保留产品详情数据和 Validate CTA**

不得改变：

- `getRadarProduct(id)`
- `validateHref` 参数生成逻辑。
- `product_opportunity_id` 传递。

- [ ] **Step 2: 重组详情页信息层级**

结构：

- 顶部 back + Validate Keyword。
- Hero summary card：产品名、类目、primary keyword、NPFS。
- 侧栏：Launch Budget、MOQ、Launch Days、Avg Price。
- 主体：Competition、Profit、Risk Flags、Differentiation、Key Risks。

Run:

```powershell
cd D:\aws\frontend
npx tsc --noEmit
npm run build
```

- [ ] **Step 3: gstack 产品详情 QA**

Run:

```bash
$B goto http://127.0.0.1:3000/radar
$B snapshot -i
$B click "@e_first_view_detail"
$B snapshot -D
$B console --errors
```

Expected:

```text
进入 /radar/products/{id}；Validate Keyword CTA 可见
```

- [ ] **Step 4: 提交产品详情改造**

Run:

```powershell
git add "frontend/app/radar/products/[id]/page.tsx"
git commit -m "feat: redesign product opportunity detail"
```

---

### Task 6: Validate 页面改造

**Files:**
- Modify: `frontend/app/validate/page.tsx`

- [ ] **Step 1: 保留分析业务逻辑**

不得改变：

- `getProjects`
- `analyzeKeyword`
- `router.push('/reports/{report_id}')`
- `productOpportunityId`
- `locale`
- 项目选择后回填 marketplace、category、budget、price range 的逻辑。

- [ ] **Step 2: 统一表单和状态**

要求：

- 使用 `PageShell`、`Card`、`Field`、`Input`、`Select`、`Button`、`StatusAlert`。
- 项目为空时显示“创建新分析 / 不选择项目”语义，不长时间显示 loading。
- 错误提示保留 `code` 和 `HTTP status`。

Run:

```powershell
cd D:\aws\frontend
npx tsc --noEmit
npm run build
```

- [ ] **Step 3: gstack Validate QA**

Run:

```bash
$B goto "http://127.0.0.1:3000/validate?keyword=under%20sink%20organizer&category=Kitchen%20%26%20Dining&budget_rmb=100000&target_price_min=20&target_price_max=40"
$B snapshot -i
$B console --errors
```

Expected:

```text
表单字段正常预填；Analyze 按钮可见；console 无新增错误
```

- [ ] **Step 4: 提交 Validate 改造**

Run:

```powershell
git add frontend/app/validate/page.tsx
git commit -m "feat: redesign keyword validation form"
```

---

### Task 7: Reports 列表和报告详情改造

**Files:**
- Modify: `frontend/app/reports/page.tsx`
- Modify: `frontend/app/reports/[id]/page.tsx`
- Modify: `frontend/components/ReportView.tsx`
- Modify: `frontend/components/ScoreGauge.tsx`

- [ ] **Step 1: 历史报告列表使用统一 Table**

要求：

- 保留 `getReports()`。
- 表格使用 `Table` primitives。
- 空状态使用 `EmptyState`。
- New Analysis 使用 `Button` 样式 Link。

- [ ] **Step 2: 报告详情使用统一卡片和指标组件**

要求：

- NSFS 总分保持首屏重点。
- 四项子分使用统一 score/metric 组件。
- 风险、机会、建议使用 `StatusAlert` 或 list card。
- Top20 商品表格保留图片 fallback 和 URL 校验逻辑。

Run:

```powershell
cd D:\aws\frontend
npx tsc --noEmit
npm run build
```

- [ ] **Step 3: smoke 验证报告页面**

Run:

```powershell
cd D:\aws\frontend
npm run smoke
```

Expected:

```text
所有 smoke 页面 OK
```

- [ ] **Step 4: 提交 Reports 改造**

Run:

```powershell
git add frontend/app/reports/page.tsx "frontend/app/reports/[id]/page.tsx" frontend/components/ReportView.tsx frontend/components/ScoreGauge.tsx
git commit -m "feat: redesign report pages"
```

---

### Task 8: 全局 loading、error、empty 和响应式 QA

**Files:**
- Modify as needed: `frontend/app/page.tsx`
- Modify as needed: `frontend/app/radar/page.tsx`
- Modify as needed: `frontend/app/validate/page.tsx`
- Modify as needed: `frontend/app/reports/page.tsx`
- Modify as needed: `frontend/components/*`

- [ ] **Step 1: 检查全局状态一致性**

要求：

- loading：按钮 loading 和页面 loading 可区分。
- error：用户能看到错误原因和下一步动作。
- empty：告诉用户为什么为空，以及可执行 CTA。
- disabled：所有提交按钮防重复提交。

- [ ] **Step 2: 响应式检查**

Viewport：

- 375x812
- 768x1024
- 1280x720
- 1440x900

Run:

```bash
$B goto http://127.0.0.1:3000/
$B responsive C:/Users/ice/AppData/Local/Temp/nspv-ui-home
$B goto http://127.0.0.1:3000/radar
$B responsive C:/Users/ice/AppData/Local/Temp/nspv-ui-radar
```

Expected:

```text
无水平滚动；按钮文字不溢出；卡片和表格不互相遮挡
```

- [ ] **Step 3: 完整验证**

Run:

```powershell
cd D:\aws\frontend
npm run lint
npx tsc --noEmit
npm run build
npm run smoke
```

```powershell
cd D:\aws\backend
pytest
```

Expected:

```text
lint/typecheck/build/smoke/pytest 全部通过，或记录明确失败原因和修复提交
```

- [ ] **Step 4: 提交最终 polish**

Run:

```powershell
git add frontend docs
git commit -m "chore: finalize ui redesign qa polish"
```

---

### Task 9: 最终 Review 和收尾

**Files:**
- Modify: `docs/v2-development-plan.md` only if task status needs同步。
- Modify: `docs/ui-component-guidelines.md` only if组件规范有新增事实。

- [ ] **Step 1: 检查业务边界**

Run:

```powershell
git diff main...HEAD -- backend
git diff main...HEAD -- frontend/lib/api.ts
```

Expected:

```text
backend 无无关业务改动；api.ts 无接口破坏性改动
```

- [ ] **Step 2: 检查组件规范一致性**

Run:

```powershell
rg -n "border border-line bg-white|bg-accent px|bg-field px-3 py-3" frontend/app frontend/components
```

Expected:

```text
裸样式显著减少；剩余项有明确理由或后续任务
```

- [ ] **Step 3: 最终命令验证**

Run:

```powershell
cd D:\aws\frontend
npm run lint
npx tsc --noEmit
npm run build
npm run smoke
```

```powershell
cd D:\aws\backend
pytest
```

- [ ] **Step 4: gstack 最终 QA 报告**

Run:

```bash
$B goto http://127.0.0.1:3000/
$B snapshot -i
$B console --errors
$B goto http://127.0.0.1:3000/radar
$B snapshot -i
$B console --errors
$B goto http://127.0.0.1:3000/validate
$B snapshot -i
$B console --errors
```

Expected:

```text
核心页面可访问；关键 CTA 可见；console 无新增错误
```

- [ ] **Step 5: 输出验收结论**

验收结论必须包含：

- 已改造页面列表。
- 已使用共享组件列表。
- 未改变的业务逻辑说明。
- 验证命令结果。
- gstack QA 发现的问题和处理结果。
- 是否建议合并回 `main`。

