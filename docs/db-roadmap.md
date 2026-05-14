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

当前默认本地数据库：

- SQLite: `backend/nspv.db`

生产目标数据库：

- PostgreSQL

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

- `0001_initial_schema`
