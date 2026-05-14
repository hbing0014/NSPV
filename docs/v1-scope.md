# NSPV V1 范围

本文档定义 V1 必须完成的范围、暂缓范围和验收标准。后续开发必须优先保证 V1 闭环完整，再进入 V2/V3 功能。

## V1 核心问题

V1 只回答一个核心问题：

> 输入一个 Amazon 美国站关键词后，这个市场是否适合新店进入？

V1 不追求完整数据平台，不做 AI 顾问，不做复杂 PPC，不做 Chrome 插件。

## V1 必须完成模块

### 1. 用户系统，基础版

目标：

- 支持基础用户身份和未来扩展。

V1 最小范围：

- 用户表存在
- 支持后续注册登录扩展
- 分析报告可关联用户，当前可允许匿名或默认用户

暂不强制：

- 邮箱验证
- 修改密码
- API Key
- 付费套餐

### 2. 项目系统

目标：

- 让一次或多次关键词分析归属于一个选品项目。

V1 最小范围：

- 创建项目
- 查询项目
- 项目包含类目、预算、站点
- 报告关联项目

暂不强制：

- 项目归档
- 项目搜索
- 项目统计仪表盘

### 3. 关键词分析系统

目标：

- 支持单关键词分析。

V1 最小范围：

- 用户输入 `keyword`
- 固定或选择 `marketplace = US`
- 选择 `category`
- 输入 `budget_rmb`
- 输入目标价格区间
- 生成关键词指标

暂不做：

- 多关键词批量分析
- ASIN 分析
- URL 分析
- 长尾关键词扩展

### 4. Amazon 搜索抓取系统

目标：

- 根据关键词抓取 Amazon US 搜索结果 Top20。

V1 最小范围：

- 抓取 Top20 商品
- 提取字段：
  - `asin`
  - `title`
  - `brand`
  - `price`
  - `rating`
  - `review_count`
  - `image_url`
  - `product_url`
  - `is_sponsored`
  - `seller_type`
  - `bsr`，如果可得
- 失败时返回明确错误

允许阶段性方案：

- 开发早期使用 mock crawler 打通业务闭环
- 后续替换为 Playwright 或第三方数据服务

暂不做：

- Review 详情抓取
- 价格历史抓取
- 库存抓取
- Seller 深度分析

### 5. 产品分析系统

目标：

- 从 Top20 商品中提取市场竞争结构。

V1 最小输出：

- `avg_reviews_top10`
- `avg_reviews_top3`
- `min_reviews_top10`
- `avg_price`
- `avg_rating`
- `sponsored_density`
- `brand_concentration`
- `amazon_basics_present`

暂不做：

- 图片质量分析
- 视频覆盖分析
- Listing 深度质量分析

### 6. NSFS 评分引擎

目标：

- 生成可解释的新店适配评分。

V1 必须实现：

- Demand Score
- Competition Score
- Profit Score 简化版
- Opportunity Score 简化版
- NSFS 总分
- Recommendation
- Risk Level

公式：

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

### 7. 利润分析系统，简化版

目标：

- 给出新店能否承受利润和广告成本的初步判断。

V1 最小输出：

- `avg_price`
- `purchase_cost_rmb`，可先估算
- `shipping_cost_rmb`，可先估算
- `fba_fee_usd`
- `referral_fee_usd`
- `estimated_ad_cost_usd`
- `net_margin`
- `roi`
- `break_even_acos`
- `recommended_order_qty`

暂不做：

- 精细 FBA 尺寸重量模型
- 真实物流报价
- PPC 高级预测

### 8. 风险预警系统

目标：

- 明确告诉新店哪些风险会导致不适合进入。

V1 必须规则：

- `avg_reviews_top10 > 2500`
- `sponsored_density > 50%`
- `amazon_basics_present = true`
- `avg_price < 15`
- `avg_rating > 4.8 and avg_reviews_top10 > 2000`
- 目标价格区间不匹配

输出：

- `warnings[]`

### 9. 报告系统

目标：

- 把一次分析沉淀成可回看的报告。

V1 最小范围：

- 分析报告生成
- 报告详情页
- Top20 商品表格
- 四项子分
- 推荐等级
- 风险预警
- 操作建议
- 历史报告列表

暂不做：

- PDF 导出
- Excel 导出
- 分享链接
- 报告对比

### 10. 基础历史记录

目标：

- 保存每次分析结果。

V1 最小范围：

- 保存 `selection_reports`
- 保存 `products`
- 保存 `keyword_product_snapshots`
- 支持历史报告查询

暂不做：

- 长周期趋势图
- 市场成熟度变化
- 价格和 Review 增长曲线

## V1 明确暂缓内容

以下功能不得进入 V1 主线，除非用户明确变更范围：

- AI 聊天
- AI 顾问
- 专利系统
- Chrome 插件
- 多 Marketplace
- 开放 API 平台
- Stripe 支付
- 高级 NLP
- 自动供应链匹配
- PPC 高级预测
- PDF/Excel 导出
- 多关键词批量分析

## V1 验收标准

V1 完成必须满足：

1. 用户可以输入一个 Amazon 关键词。
2. 系统可以返回 Top20 商品数据。
3. 系统可以计算 NSFS 评分。
4. 系统可以输出推荐等级。
5. 系统可以输出风险预警。
6. 系统可以展示分析结果页。
7. 系统可以保存历史报告。
8. 单次分析在合理时间内完成。
9. 抓取失败时有明确错误提示。
10. 用户能通过报告判断该关键词是否值得继续研究。

