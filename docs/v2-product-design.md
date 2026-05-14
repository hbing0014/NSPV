# NSPV V2 产品设计说明书

本文档定义 NSPV V2 的产品目标、系统边界、核心模块、页面逻辑、评分体系和数据流。V2 不推翻 V1，而是在 V1 关键词验证能力前新增产品发现层。

## 版本定位

V1 是 `Keyword Validation Engine`：

- 用户输入关键词。
- 系统判断这个关键词是否适合新店进入。
- 核心问题是：这个词能不能做？

V2 是 `Product Discovery Engine`：

- 用户输入类目、预算、风险偏好和基础限制。
- 系统主动推荐适合新手卖家的产品机会。
- 核心问题是：我现在应该卖什么？

产品路径升级为：

```text
Discover → Validate → Launch
```

其中：

- `Discover` 是 V2 新增产品发现层。
- `Validate` 复用 V1 关键词验证引擎。
- `Launch` 是后续 V3 可继续扩展的执行规划层。

## 产品原则

1. 不重做 V1，V1 继续作为验证引擎。
2. V2 先做产品发现闭环，再逐步接入更真实的数据源。
3. 首页从关键词搜索页升级为产品机会雷达。
4. 系统不只告诉用户“市场上有什么”，而是告诉用户“你现在最值得做什么”。
5. 对新手而言，预算安全、低 Review 切入、低运营复杂度优先于理论高销量。

## 目标用户

- Amazon 美国站新卖家。
- 启动资金约 5 万到 20 万人民币。
- 主做厨房、家居、收纳、清洁、日用品类目。
- 不知道应该卖什么。
- 不会判断 Review 门槛、红海风险、利润空间、启动预算和供应链复杂度。

## V2 核心用户场景

场景 A：新手完全不知道卖什么。

- 输入：Kitchen、10 万预算、低风险。
- 输出：系统推荐 10 到 50 个产品方向。

场景 B：用户只想找低风险产品。

- 输入：低风险、排除红海、排除 Amazon Basics、价格 20 到 40 美元。
- 输出：低 Review、低启动预算、可验证的产品池。

场景 C：用户看到推荐产品后继续深挖。

- 点击 `Validate Keyword`。
- 系统将产品的 `primary_keyword` 送入 V1 分析。
- 生成 V1 `selection_report`，并关联回 V2 产品机会。

## V2 系统结构

```text
用户条件输入
↓
Product Radar
↓
Category Scanner
↓
Raw Product Pool
↓
Product Opportunity Finder
↓
Launch Score / Supplier Score
↓
NPFS
↓
Product Opportunity Pool
↓
V1 Keyword Validation
↓
Final Decision
```

## 核心模块

### Category Scanner

职责：

- 扫描指定 Amazon 类目。
- 形成原始候选产品池。
- 支持 Best Sellers、New Releases、Search Pool、BSR 扫描等数据源。

V2 P0 支持类目：

- Kitchen & Dining
- Home & Kitchen
- Storage & Organization

P1/P2 类目：

- Cleaning Tools
- Household Supplies

暂缓类目：

- Electronics
- Beauty
- Apparel
- Supplements
- Seasonal

P0 必抓字段：

- `asin`
- `title`
- `brand`
- `category`
- `price`
- `rating`
- `review_count`
- `bsr`
- `seller_type`
- `is_sponsored`
- `weight`
- `dimensions`
- `is_fragile`
- `amazon_basics_present`
- `estimated_monthly_sales`
- `estimated_monthly_revenue`

### Product Opportunity Finder

职责：

- 对原始产品池做硬过滤和软过滤。
- 输出 `Rejected`、`Research`、`Opportunity` 三个层级。
- 给产品打机会标签和风险标签。

硬过滤默认规则：

| 规则 | 默认处理 | 原因 |
| --- | --- | --- |
| `avg_price < 15` | 排除 | 利润和广告空间不足 |
| `avg_price > 80` | 排除 | 高客单冷启动难 |
| `top10_avg_reviews > 1500` | 排除 | Review 门槛过高 |
| `amazon_basics_present = true` | 排除，可由用户关闭 | 品牌壁垒和价格战 |
| `weight > 1kg` | 排除 | 物流和 FBA 成本高 |
| `is_fragile = true` | 排除 | 退货、包装、差评风险高 |
| 强季节性 | 默认排除 | 新手库存风险高 |

软过滤规则：

| 指标 | 优先 | 中风险 | 高风险 |
| --- | --- | --- | --- |
| Sponsored Density | `<30%` | `30%-50%` | `>50%` |
| Avg Rating | `4.2-4.7` | `<4.2` 需人工判断 | `>4.8` 市场成熟 |
| Top10 Avg Reviews | `<800` | `800-1500` | `>1500` |
| Lowest Review Top10 | `<150` 强机会 | `150-300` | `>300` |

标签：

- `LOW_REVIEW`
- `LOW_RISK`
- `HIGH_MARGIN`
- `HIGH_PPC`
- `RED_OCEAN`
- `AMAZON_BASICS`
- `HEAVY`
- `FRAGILE`
- `SEASONAL`
- `STRONG_OPPORTUNITY`

### Launch Score Engine

职责：

- 判断新手是否启动得起某个产品。
- 输出执行可行性分数和启动预算建议。

公式：

```text
Launch Score =
Budget × 0.30 +
PPC × 0.20 +
Review × 0.15 +
MOQ × 0.15 +
Inventory × 0.10 +
Operations × 0.10
```

维度：

| 维度 | 权重 | 关键字段 |
| --- | --- | --- |
| Budget Feasibility | 30% | unit cost、MOQ、shipping、packaging、PPC seed budget |
| PPC Launch Difficulty | 20% | CPC、sponsored density、keyword competition |
| Review Acquisition Difficulty | 15% | Top10 Avg Reviews、Lowest Review Top10 |
| MOQ Accessibility | 15% | avg supplier MOQ、customization requirement |
| Inventory Pressure | 10% | first order qty、monthly sales、turn days |
| Operational Complexity | 10% | fragile、heavy、variation count、return risk |

等级：

| 分数 | 等级 | 含义 |
| --- | --- | --- |
| `90-100` | Excellent Launch Product | 极适合新手启动 |
| `80-89` | Strong Launch Candidate | 较适合 |
| `70-79` | Launchable with Caution | 可做但需控制 |
| `60-69` | Difficult for Beginners | 启动偏难 |
| `<60` | Poor Launch Fit | 不建议 |

输出字段：

- `launch_score`
- `budget_score`
- `ppc_score`
- `review_score`
- `moq_score`
- `inventory_score`
- `operations_score`
- `estimated_total_launch_budget`
- `estimated_launch_days`
- `estimated_break_even_days`

风险标签：

- `LOW_BUDGET_FRIENDLY`
- `HIGH_PPC_RISK`
- `HIGH_MOQ`
- `INVENTORY_HEAVY`
- `REVIEW_BARRIER`
- `OPERATION_COMPLEX`
- `BEGINNER_FRIENDLY`

### Supplier Score Engine

职责：

- 判断供应链是否适合新手。
- V2 P0 可以先用估算规则，P1 再接入 1688 或第三方数据。

核心指标：

- `supplier_count_1688`
- `avg_supplier_moq`
- `supplier_price_range`
- `mold_complexity`
- `packaging_complexity`
- `supply_chain_maturity`

### NPFS Engine

NPFS 是 V2 产品机会总评分。

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

其中 Demand、Competition、Profit、Opportunity 可以复用 V1 评分逻辑，Launch 和 Supplier 是 V2 新增。

### Product Radar

职责：

- V2 默认首页。
- 展示系统主动推荐的产品机会。
- 支持筛选、排序、查看详情、保存、进入 V1 验证。

默认排序：

```text
NPFS Score DESC
```

可选排序：

- Highest NPFS
- Lowest Risk
- Lowest Budget
- Highest Profit
- Easiest Launch
- Trending Now

Radar Score 可作为榜单排序增强：

```text
Radar Score =
NPFS × 0.40 +
Launch Score × 0.25 +
Trend Score × 0.15 +
Supplier Score × 0.10 -
Risk Penalty × 0.10
```

产品卡片展示字段：

- Product Name
- Primary Keyword
- Category
- Avg Price
- Weight
- NPFS Score
- Launch Score
- Competition Score
- Profit Score
- Risk Level
- Estimated Budget
- MOQ
- Estimated Launch Days
- Key Opportunity
- Tags

CTA：

- `Validate Keyword`
- `View Product Detail`
- `Save to Project`

## V2 首页 UI

V2 首页是 Product Discovery Dashboard，不是关键词搜索页。

页面结构：

1. Top Navigation
2. Hero Section
3. Smart Filter Section
4. Featured Product Radar
5. Weekly Product Opportunities
6. Product Categories Explorer
7. Risk Alert Section
8. How It Works
9. Saved Projects CTA
10. Footer

P0 首页必须包含：

- Hero Discovery 表单。
- Smart Filter。
- Top 6 产品机会卡片。
- V1 `Validate Keyword` 入口。

Hero 输入：

- Category
- Budget
- Risk Preference
- Price Range
- Weight Limit

主按钮：

- `Discover Products`

辅助按钮：

- `Try Weekly Radar`
- `Validate My Keyword`

## V1 兼容方案

V2 首页改为 Product Radar 后，V1 关键词验证页迁移到：

```text
/validate
```

V2 调用 V1 的路径：

```text
Product Opportunity
↓
primary_keyword
↓
POST /api/analyze
↓
selection_report
```

建议给 `selection_reports` 新增：

- `product_opportunity_id`

用于把 V1 报告绑定回 V2 推荐产品。

## 数据库设计

V2 新增核心表：

- `categories`
- `category_scan_jobs`
- `category_products`
- `product_keyword_clusters`
- `product_opportunities`
- `launch_scores`
- `supplier_scores`
- `product_radar_snapshots`
- `discovery_reports`

P0 必须：

- `categories`
- `category_scan_jobs`
- `category_products`
- `product_opportunities`
- `launch_scores`
- `discovery_reports`

P1：

- `product_keyword_clusters`
- `supplier_scores`

P2：

- `product_radar_snapshots`

核心索引：

- `products.asin`
- `product_opportunities.asin`
- `product_opportunities.npfs_score`
- `product_opportunities.category_id`
- `product_opportunities.recommendation`
- `product_radar_snapshots.snapshot_date`
- `keywords.keyword`

## V2 MVP 范围

V2 MVP 不直接追求完整真实 Amazon 类目全量扫描。建议先做：

1. P0 数据表和迁移。
2. 种子产品池。
3. Category Scanner 规则引擎。
4. Product Opportunity Finder。
5. Launch Score 简化版。
6. NPFS 计算。
7. Product Radar 页面。
8. Discover → Validate Keyword 链路。

暂缓：

- 真实 Best Sellers 全量扫描。
- 真实 New Releases 每日扫描。
- 1688 供应链真实接入。
- Trend Radar。
- Saved Product Pool。
- Risk Alert Center 完整后台。

## 验收标准

V2 MVP 完成时必须满足：

1. 用户进入首页可以按类目、预算、风险、价格、重量发现产品。
2. 系统返回产品机会列表，而不是要求用户先输入关键词。
3. 产品卡片展示 NPFS、Launch Score、预算、风险和标签。
4. 用户可以点击 `Validate Keyword` 进入 V1 验证。
5. V1 报告可以关联到 V2 产品机会。
6. Category Scanner 规则有单元测试。
7. Launch Score 有单元测试和固定样例。
8. Product Radar 页面有前端 smoke 测试。
9. 后端 API 使用统一错误契约。
10. mock/seed 数据不会生成假图片和无效 Amazon 链接。
