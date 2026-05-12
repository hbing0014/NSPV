# NSPV System Module Architecture

本文档定义 NSPV 从 V1 到后续版本的完整功能模块，用于架构设计、功能拆分、开发排期、数据库扩展、API 规划和后续微服务拆分。

## Product Goal

NSPV 不是传统销量查询工具，而是 Amazon 美国站新店低风险选品决策工具。

核心问题：

> 这个产品或关键词，是否适合新店进入？

最终目标：

- 降低错误选品概率
- 降低进入红海市场概率
- 提高新品成功率
- 提高资金利用率
- 快速判断一个市场是否值得继续研究

产品核心理念：

- 不是告诉用户什么卖得好
- 而是告诉用户什么适合你做、什么别碰、为什么

## System Modules

| No. | Module | Stage | Purpose |
| --- | --- | --- | --- |
| 1 | User System | V1 Basic | 注册、登录、用户资料、额度和套餐基础 |
| 2 | Project System | V1 | 管理用户选品项目 |
| 3 | Keyword Analysis System | V1 | 单关键词分析，后续扩展多关键词、ASIN、URL |
| 4 | Amazon Scraper System | V1 | 抓取搜索结果 Top20，后续抓详情页和 Review |
| 5 | Product Analysis System | V1 | 分析 Top20 商品结构、Review、广告、品牌 |
| 6 | NSFS Scoring Engine | V1 | 核心评分和推荐结论 |
| 7 | Profit Analysis System | V1 Simplified | 简化利润、ROI、Break-even ACOS |
| 8 | Review Analysis System | V2 | 差评抓取、痛点聚类、NLP 和 LLM 分析 |
| 9 | Risk Warning System | V1 | 红海、高 Review、高广告、自营品牌等预警 |
| 10 | Report System | V1 | 分析报告、历史报告，后续导出和分享 |
| 11 | AI Advisor System | V2/V3 | AI 总结、升级建议、竞争策略 |
| 12 | Historical Data System | V2 | 趋势、价格、Review、排名历史 |
| 13 | Data Monitoring System | V2/V3 | 抓取失败、数据缺失、异常波动监控 |
| 14 | Admin System | V2/V3 | 用户、项目、报告、任务、参数和日志管理 |
| 15 | Billing System | V3 | Stripe、套餐、账单、额度 |
| 16 | Open API Platform | V3 | API Key、Rate Limit、第三方接入 |
| 17 | Chrome Extension | V3 | Amazon 页面注入评分和一键分析 |
| 18 | Cache System | V1 Optional/V2 | Keyword、页面、报告、AI 结果缓存 |
| 19 | Task Queue System | V1 Optional/V2 | 抓取、Review、AI 任务队列和重试 |
| 20 | Logging System | V1 Basic/V2 | API、Scraper、错误、行为、性能日志 |

## Module Details

### User System

功能：

- 用户注册
- 用户登录
- JWT 鉴权
- 用户资料管理
- 修改密码
- 邮箱验证
- 用户套餐管理
- 用户使用额度限制
- 用户行为日志
- API Key 管理，后期

主要数据库：

- `users`

主要 API：

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/profile`
- `PUT /auth/profile`

### Project System

功能：

- 创建项目
- 删除项目
- 修改项目
- 项目分类
- 项目归档
- 项目搜索
- 项目统计

主要数据库：

- `projects`

核心字段：

- `project_name`
- `category`
- `budget_rmb`
- `marketplace`
- `target_price_range`

主要 API：

- `POST /projects`
- `GET /projects`
- `PUT /projects/{id}`
- `DELETE /projects/{id}`

### Keyword Analysis System

功能：

- 输入关键词分析
- 多关键词分析，后期
- ASIN 分析
- Amazon URL 分析
- 关键词搜索量分析
- 搜索趋势分析
- 季节性分析
- 长尾关键词扩展
- Keyword Difficulty 分析
- Keyword Opportunity 分析

核心字段：

- `monthly_search_volume`
- `search_trend`
- `seasonality_score`
- `keyword_difficulty`
- `long_tail_keywords`

主要数据库：

- `keywords`

主要 API：

- `POST /analyze/keyword`
- `POST /analyze/asin`

### Amazon Scraper System

功能：

- Amazon 搜索结果抓取
- 商品详情页抓取
- Review 抓取
- 搜索排名抓取
- Sponsored 广告抓取
- 品牌信息抓取
- BSR 抓取
- 价格历史抓取，后期
- 库存状态抓取，后期
- Seller 信息抓取

抓取字段：

- `asin`
- `title`
- `brand`
- `price`
- `rating`
- `review_count`
- `image_url`
- `seller_type`
- `bsr`
- `is_sponsored`

技术候选：

- Playwright
- BrightData
- Oxylabs

建议模块拆分：

- `amazon_search_scraper`
- `amazon_product_scraper`
- `amazon_review_scraper`

### Product Analysis System

功能：

- 产品基础分析
- Top20 商品分析
- 品牌集中度分析
- Review 结构分析
- Sponsored 密度分析
- Listing 质量分析
- 图片质量分析，后期
- 视频覆盖分析，后期
- 商品成熟度分析
- 类目竞争分析

核心输出：

- `avg_reviews_top10`
- `avg_reviews_top3`
- `min_reviews_top10`
- `brand_concentration`
- `sponsored_density`
- `amazon_basics_present`

主要数据库：

- `products`
- `keyword_product_snapshots`

### NSFS Scoring Engine

功能：

- Demand Score 计算
- Competition Score 计算
- Profit Score 计算
- Opportunity Score 计算
- NSFS 总分计算
- Recommendation 推荐等级
- 风险等级计算
- 权重配置系统，后期
- AI 动态评分，后期

核心公式：

```text
NSFS = Demand * 0.25
     + Competition * 0.30
     + Profit * 0.25
     + Opportunity * 0.20
```

推荐等级：

- `Strongly Recommended`: `NSFS >= 85`
- `Worth Research`: `70 <= NSFS < 85`
- `Caution`: `50 <= NSFS < 70`
- `Avoid`: `NSFS < 50`

主要数据库：

- `selection_reports`

### Profit Analysis System

功能：

- FBA 费用计算
- Referral Fee 计算
- 毛利润计算
- 净利润计算
- ROI 计算
- Break-even ACOS 计算
- 首单建议量
- 库存周期建议
- 广告成本估算
- 物流成本估算

输入：

- `purchase_cost`
- `shipping_cost`
- `sale_price`

输出：

- `gross_margin`
- `net_margin`
- `roi`
- `recommended_order_qty`

主要数据库：

- `profit_calculations`

### Review Analysis System

功能：

- 差评抓取
- 高频词分析
- 情绪分析
- 用户痛点聚类
- 高频抱怨识别
- 差评严重度分析
- AI 升级建议
- 产品优化建议
- 用户需求提取
- 竞争产品缺陷分析

核心输出：

- `pain_points`
- `negative_keywords`
- `upgrade_suggestions`

技术候选：

- NLP
- LLM

主要数据库：

- `review_analysis`

### Risk Warning System

功能：

- 红海预警
- 高 Review 预警
- 高 Sponsored 预警
- Amazon Basics 预警
- 低利润预警
- 高退货风险预警，后期
- 品牌垄断预警
- 季节性风险预警
- Listing 成熟度预警
- 价格战风险预警

输出：

- `warnings[]`

示例：

- `Top10 average reviews exceed 2500`
- `High sponsored density detected`

### Report System

功能：

- 分析报告生成
- 历史报告保存
- PDF 导出，后期
- Excel 导出，后期
- 报告分享
- 报告复制
- 报告对比
- 报告收藏
- 报告标签系统
- AI 报告摘要

主要数据库：

- `selection_reports`

### AI Advisor System

功能：

- AI 选品顾问
- AI 差评总结
- AI 升级建议
- AI 风险分析
- AI 关键词建议
- AI 竞争策略
- AI 差异化建议
- AI 新品方向推荐
- AI 标题建议，后期
- AI Listing 优化，后期

输入：

- `keyword`
- `report`

输出：

- `ai_suggestions`

技术：

- OpenAI API

### Historical Data System

功能：

- 历史趋势记录
- 搜索量变化
- Review 增长记录
- 价格变化
- Ranking 变化
- 市场成熟度变化
- 品牌增长分析
- 历史报告对比
- 市场趋势分析
- 长周期竞争分析

主要数据库：

- `history_snapshots`

### Data Monitoring System

功能：

- Amazon 页面结构变化检测
- 抓取失败监控
- 数据缺失监控
- 异常波动检测
- API 失败监控
- 队列积压监控
- Redis 状态监控
- Proxy 状态监控
- Token 消耗监控
- 模型调用监控

### Admin System

功能：

- 用户管理
- 项目管理
- 报告管理
- 抓取任务监控
- API 监控
- 系统日志
- 评分参数配置
- 黑名单管理
- 使用统计
- 支付管理

### Billing System

功能：

- 免费版限制
- Pro 订阅
- Agency 订阅
- Stripe 支付
- 使用次数统计
- API 额度限制
- 月度账单
- 套餐升级
- 套餐降级
- 发票系统

### Open API Platform

功能：

- API Key
- Rate Limit
- 第三方接入
- API 文档
- API 统计
- Webhook，后期
- SDK，后期

主要 API：

- `/api/analyze`
- `/api/report`
- `/api/keyword`

### Chrome Extension

功能：

- Amazon 页面注入评分
- 实时 NSFS 显示
- 一键分析 ASIN
- Review 快速分析
- 红海提示
- 利润提示
- Quick Export
- Listing 对比

### Task Queue System

功能：

- 抓取队列
- Review 分析队列
- AI 分析队列
- Retry 机制
- 超时处理
- Dead Letter Queue
- Priority Queue

技术：

- Redis
- Celery

### Cache System

功能：

- Keyword 缓存
- Amazon 页面缓存
- Report 缓存
- 热门关键词缓存
- AI 结果缓存
- API 缓存

技术：

- Redis

### Logging System

功能：

- API 日志
- Scraper 日志
- 错误日志
- 用户行为日志
- AI 调用日志
- 性能日志

