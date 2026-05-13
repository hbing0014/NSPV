# NSPV Database Roadmap

本文档定义 NSPV 数据库从当前原型到 V1、V2、V3 的表结构演进。

## Database Principles

- V1 优先保存分析报告和分析时的商品快照。
- 报告必须可复现，不能只引用实时商品表。
- 搜索结果快照和商品主表分开。
- 后续 Review、AI、历史趋势、支付、开放 API 独立扩展。
- 评分规则结果需要保存详细字段，方便后续解释和回归测试。

## Current Implemented Tables

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

## V1 Tables

### users

Purpose:

- 存储用户基础信息。

Current fields:

- `id`
- `email`
- `name`
- `plan_type`
- `created_at`
- `updated_at`

V1 recommended additions:

- `password_hash`
- `email_verified`
- `monthly_analysis_limit`
- `monthly_analysis_used`

Deferred:

- `stripe_customer_id`
- `api_key_hash`
- `last_login_at`

### projects

Purpose:

- 存储用户的选品项目。

Current fields:

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

`status` values:

- `active`
- `archived`

### keywords

Purpose:

- 存储每次分析的关键词指标。

Current fields:

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

V1 recommended additions:

- `search_trend`
- `seasonality_score`
- `keyword_difficulty`

V2 additions:

- `long_tail_keywords`
- `keyword_opportunity`
- `trend_source`

### products

Purpose:

- 存储商品主数据，按 ASIN 去重。

Current fields:

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

V1 recommended additions:

- `category`
- `seller_name`
- `availability`

V2 additions:

- `variation_count`
- `has_video`
- `image_count`
- `listing_quality_score`

### keyword_product_snapshots

Purpose:

- 保存关键词分析当时的搜索结果快照。

Current fields:

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

V1 recommended additions:

- `search_position`
- `raw_badges`
- `scraper_source`

Important:

- 报告展示应优先使用 snapshot 或 report 内保存的产品快照，而不是实时 `products`。

### selection_reports

Purpose:

- 保存完整分析报告。

Current fields:

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

## V1 New Table Candidates

### profit_calculations

Purpose:

- 把利润计算从 report JSON 中拆出来，便于后续单独调整。

Suggested fields:

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

V1 priority:

- Medium. 当前可以先存在 `selection_reports.score_details`。

### scraper_runs

Purpose:

- 记录每次 Amazon 抓取执行状态。

Current fields:

- `id`
- `keyword`
- `marketplace`
- `provider`
- `status`
- `product_count`
- `error_message`
- `started_at`
- `finished_at`

`status` values:

- `running`
- `completed`
- `empty`
- `failed`

## V2 Tables

### review_analysis

Purpose:

- 保存 Review NLP 和 AI 分析结果。

Suggested fields:

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

Purpose:

- 保存长期趋势数据。

Suggested fields:

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

Purpose:

- 保存 AI 输出，支持缓存和回看。

Suggested fields:

- `id`
- `report_id`
- `prompt_version`
- `model`
- `input_hash`
- `output`
- `token_usage`
- `created_at`

## V3 Tables

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

## Migration Guidance

Current project uses `Base.metadata.create_all()` for local speed.

Before production:

1. Add Alembic.
2. Generate initial migration from current models.
3. Stop relying on automatic create-all in production.
4. Add indexes for:
   - `products.asin`
   - `keywords.keyword`
   - `selection_reports.project_id`
   - `selection_reports.created_at`
   - `keyword_product_snapshots.keyword_id`
   - `keyword_product_snapshots.asin`
