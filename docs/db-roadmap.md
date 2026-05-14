# NSPV 数据库路线图

本文档定义 NSPV 数据库从当前原型到 V1、V2、V3 的表结构演进。

## 数据库原则

- V1 优先保存分析报告和分析时的商品快照。
- 报告必须可复现，不能只引用实时商品表。
- 搜索结果快照和商品主表分开。
- 后续 Review、AI、历史趋势、支付、开放 API 独立扩展。
- 评分规则结果需要保存详细字段，方便后续解释和回归测试。

## 当前已实现数据表

当前项目已有 SQLAlchemy models：

- `users`
- `projects`
- `keywords`
- `products`
- `keyword_product_snapshots`
- `selection_reports`
- `scraper_runs`
- `categories`
- `category_scan_jobs`
- `category_products`
- `product_opportunities`
- `launch_scores`
- `discovery_reports`

当前默认本地数据库：

- SQLite: `backend/nspv.db`

生产目标数据库：

- Supabase PostgreSQL

当前正式迁移版本：

- `0001_initial_schema`
- `0002_v2_discovery_schema`

## V1 数据表

### users

用途：

- 存储用户基础信息。

当前字段：

- `id`
- `email`
- `name`
- `password_hash`
- `plan_type`
- `created_at`
- `updated_at`

V1 建议新增字段：

- `email_verified`
- `monthly_analysis_limit`
- `monthly_analysis_used`

暂缓：

- `stripe_customer_id`
- `api_key_hash`
- `last_login_at`

### projects

用途：

- 存储用户的选品项目。

当前字段：

- `id`
- `user_id`
- `project_name`
- `category`
- `budget_rmb`
- `marketplace`
- `target_price_min`
- `target_price_max`
- `status`
- `created_at`
- `updated_at`

`status` 取值：

- `active`
- `archived`

### keywords

用途：

- 存储每次分析的关键词指标。

当前字段：

- `id`
- `project_id`
- `keyword`
- `marketplace`
- `category`
- `monthly_search_volume`
- `avg_price`
- `avg_rating`
- `avg_reviews_top10`
- `avg_reviews_top3`
- `min_reviews_top10`
- `sponsored_density`
- `amazon_basics_present`
- `created_at`
- `updated_at`

V1 建议新增字段：

- `search_trend`
- `seasonality_score`
- `keyword_difficulty`

V2 新增字段：

- `long_tail_keywords`
- `keyword_opportunity`
- `trend_source`

### products

用途：

- 存储商品主数据，按 ASIN 去重。

当前字段：

- `id`
- `asin`
- `marketplace`
- `title`
- `brand`
- `price`
- `rating`
- `review_count`
- `monthly_sales_est`
- `monthly_revenue_est`
- `bsr`
- `is_sponsored`
- `seller_type`
- `image_url`
- `product_url`
- `created_at`
- `updated_at`

V1 建议新增字段：

- `category`
- `seller_name`
- `availability`

V2 新增字段：

- `variation_count`
- `has_video`
- `image_count`
- `listing_quality_score`

### keyword_product_snapshots

用途：

- 保存关键词分析当时的搜索结果快照。

当前字段：

- `id`
- `keyword_id`
- `product_id`
- `asin`
- `organic_rank`
- `sponsored_rank`
- `page_no`
- `is_sponsored`
- `price`
- `rating`
- `review_count`
- `captured_at`

V1 建议新增字段：

- `search_position`
- `raw_badges`
- `scraper_source`

重要说明：

- 报告展示应优先使用 snapshot 或 report 内保存的产品快照，而不是实时 `products`。

### selection_reports

用途：

- 保存完整分析报告。

当前字段：

- `id`
- `project_id`
- `keyword_id`
- `scraper_run_id`
- `nsfs_score`
- `demand_score`
- `competition_score`
- `profit_score`
- `opportunity_score`
- `recommendation`
- `risk_level`
- `summary`
- `key_risks`
- `key_opportunities`
- `action_suggestions`
- `products_snapshot`
- `score_details`
- `analysis_status`
- `error_message`
- `input_payload`
- `scoring_version`
- `created_at`

`analysis_status` values:

- `completed`
- `failed`
- `partial`

## V1 新增候选表

### profit_calculations

用途：

- 把利润计算从 report JSON 中拆出来，便于后续单独调整。

建议字段：

- `id`
- `report_id`
- `avg_price`
- `purchase_cost_rmb`
- `shipping_cost_rmb`
- `fba_fee_usd`
- `referral_fee_usd`
- `estimated_ad_cost_usd`
- `gross_margin`
- `net_margin`
- `roi`
- `break_even_acos`
- `recommended_order_qty`
- `created_at`

V1 优先级：

- 中等。当前可以先存在 `selection_reports.score_details`。

### scraper_runs

用途：

- 记录每次 Amazon 抓取执行状态。

当前字段：

- `id`
- `keyword`
- `marketplace`
- `provider`
- `status`
- `product_count`
- `error_message`
- `started_at`
- `finished_at`

`status` 取值：

- `running`
- `completed`
- `empty`
- `failed`

## V2 数据表

V2 采用兼容升级方案：V1 表保留，新增 Discovery Layer 表。V1 继续作为关键词验证层，V2 新增产品发现层。

### categories

用途：

- 存储系统支持扫描和推荐的 Amazon 类目。

当前字段：

- `id`
- `category_name`
- `parent_category`
- `amazon_category_id`
- `marketplace`
- `is_active`
- `priority_level`
- `created_at`
- `updated_at`

### category_scan_jobs

用途：

- 记录 Category Scanner 每次扫描任务的来源、类型和状态。

当前字段：

- `id`
- `category_id`
- `marketplace`
- `scan_type`
- `source_type`
- `status`
- `total_products_found`
- `total_products_filtered`
- `started_at`
- `finished_at`
- `created_at`

### category_products

用途：

- 存储类目扫描得到的原始候选产品池。

当前字段：

- `id`
- `scan_job_id`
- `category_id`
- `asin`
- `title`
- `brand`
- `price`
- `rating`
- `review_count`
- `bsr`
- `is_sponsored`
- `seller_type`
- `weight`
- `dimensions`
- `is_fragile`
- `estimated_monthly_sales`
- `estimated_monthly_revenue`
- `amazon_basics_present`
- `seasonality_score`
- `patent_risk_level`
- `created_at`
- `updated_at`

### product_opportunities

用途：

- 存储经过硬过滤、软过滤和评分后的 V2 产品机会池。

当前字段：

- `id`
- `category_id`
- `asin`
- `product_name`
- `brand`
- `primary_keyword`
- `keyword_cluster_id`
- `avg_price`
- `avg_rating`
- `avg_reviews_top10`
- `min_reviews_top10`
- `monthly_search_volume`
- `estimated_monthly_sales`
- `estimated_monthly_revenue`
- `demand_score`
- `competition_score`
- `profit_score`
- `opportunity_score`
- `launch_score`
- `supplier_score`
- `npfs_score`
- `estimated_budget_rmb`
- `estimated_moq`
- `estimated_first_order_qty`
- `estimated_launch_days`
- `risk_level`
- `recommendation`
- `is_red_ocean`
- `is_amazon_basics`
- `is_fragile`
- `is_seasonal`
- `is_heavy`
- `is_patent_risk`
- `differentiation_paths`
- `key_risks`
- `key_opportunities`
- `created_at`
- `updated_at`

### launch_scores

用途：

- 存储 Launch Feasibility Score，用于判断新手是否启动得起某个产品。

当前字段：

- `id`
- `product_opportunity_id`
- `asin`
- `estimated_moq`
- `estimated_unit_cost_rmb`
- `estimated_shipping_cost_rmb`
- `estimated_packaging_complexity`
- `estimated_ppc_launch_cost`
- `estimated_review_difficulty`
- `estimated_inventory_cycle_days`
- `estimated_total_launch_budget`
- `launch_score`
- `created_at`
- `updated_at`

### discovery_reports

用途：

- 存储用户 Discover 模式生成的产品发现报告。

当前字段：

- `id`
- `project_id`
- `user_id`
- `input_category`
- `input_budget_rmb`
- `input_risk_preference`
- `input_price_min`
- `input_price_max`
- `input_weight_limit`
- `exclude_red_ocean`
- `exclude_amazon_basics`
- `total_products_scanned`
- `total_products_filtered`
- `total_recommendations`
- `recommended_products`
- `summary`
- `strategy_advice`
- `created_at`
- `updated_at`

### selection_reports V2 关联字段

V2 新增字段：

- `product_opportunity_id`

用途：

- 将 V2 Product Opportunity 与 V1 Keyword Validation 报告绑定，支持 Discover → Validate → Launch 链路。

## V2 后续候选表

### review_analysis

用途：

- 保存 Review NLP 和 AI 分析结果。

建议字段：

- `id`
- `report_id`
- `asin`
- `negative_keywords`
- `pain_points`
- `sentiment_summary`
- `upgrade_suggestions`
- `severity_score`
- `created_at`

### history_snapshots

用途：

- 保存长期趋势数据。

建议字段：

- `id`
- `entity_type`
- `entity_id`
- `keyword`
- `asin`
- `marketplace`
- `avg_price`
- `avg_rating`
- `avg_reviews_top10`
- `sponsored_density`
- `nsfs_score`
- `captured_at`

### ai_advisor_outputs

用途：

- 保存 AI 输出，支持缓存和回看。

建议字段：

- `id`
- `report_id`
- `prompt_version`
- `model`
- `input_hash`
- `output`
- `token_usage`
- `created_at`

## V3 数据表

### subscriptions

- `id`
- `user_id`
- `stripe_customer_id`
- `stripe_subscription_id`
- `plan_type`
- `status`
- `current_period_start`
- `current_period_end`

### api_keys

- `id`
- `user_id`
- `name`
- `key_hash`
- `last_used_at`
- `created_at`
- `revoked_at`

### api_usage_logs

- `id`
- `user_id`
- `api_key_id`
- `endpoint`
- `status_code`
- `cost_units`
- `created_at`

## 迁移指南

当前项目使用 Alembic 进行正式数据库结构迁移。

`Base.metadata.create_all()` 仅保留给 SQLite 本地快速启动和测试使用。

当前迁移命令：

```powershell
cd backend
.\.venv\Scripts\alembic upgrade head
```

当前 Alembic 版本：

- `0002_v2_discovery_schema`
