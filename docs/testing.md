# NSPV 测试指南

本文档定义 NSPV 当前和后续开发的测试方式。

## 当前必须检查项

后端语法检查：

```powershell
cd backend
.\.venv\Scripts\python -m compileall app
```

前端生产构建：

```powershell
cd frontend
npm run build
```

API 冒烟测试：

```powershell
$body = @{
  keyword = 'sink organizer'
  marketplace = 'US'
  category = 'Kitchen & Dining'
  budget_rmb = 100000
  target_price_min = 20
  target_price_max = 40
  exclude_red_ocean = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri http://127.0.0.1:8000/api/analyze -Method Post -ContentType 'application/json' -Body $body
```

前端冒烟测试：

1. 启动后端：

```powershell
cd backend
.\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

2. 启动前端：

```powershell
cd frontend
npm run dev
```

3. 打开：

```text
http://127.0.0.1:3000
```

4. 提交：

```text
keyword: sink organizer
marketplace: US
category: Kitchen & Dining
budget: 100000
target price: 20 - 40
```

预期结果：

- 跳转到 `/reports/{id}`。
- 显示 NSFS 分数。
- 显示推荐等级。
- 显示风险预警。
- 显示 Top20 商品表格。
- 新报告出现在 `/reports`。

自动化前端冒烟检查：

```powershell
cd frontend
npm run smoke
```

这会针对 `http://127.0.0.1:3000` 检查 V2 Discovery 首页、V1 Validate、Radar、产品详情、报告列表和报告详情。

默认情况下，脚本会通过后端 API 自动创建 smoke 所需的 V2 产品机会和 V1 报告。需要先确保后端可访问。

可配置环境变量：

```powershell
$env:FRONTEND_BASE_URL="http://127.0.0.1:3000"
$env:BACKEND_BASE_URL="http://127.0.0.1:8000"
$env:SMOKE_LOCALE="zh-CN"
npm run smoke
```

如果已经有固定数据，可以跳过自动创建：

```powershell
$env:SMOKE_PRODUCT_ID="1"
$env:SMOKE_REPORT_ID="1"
npm run smoke
```

Smoke 覆盖路径：

- `/`
- `/validate?...product_opportunity_id=...`
- `/radar`
- `/radar/products/{id}`
- `/reports`
- `/reports/{id}`

## 后端测试

目标命令：

```powershell
cd backend
.\.venv\Scripts\pytest
```

当前后端测试覆盖：

- `test_health.py`
  - `/health` 返回状态 ok。
- `test_analyze_api.py`
  - 有效请求会创建报告。
  - 无效目标价格返回 400。
  - 报告详情返回已保存的商品快照。
  - 报告不存在时返回 404。
- `test_scoring.py`
  - 需求分阈值。
  - Review 竞争阈值。
  - 广告密度阈值。
  - 利润率阈值。
  - NSFS 加权公式。
- `test_risk.py`
  - 高 Review 预警。
  - 高广告预警。
  - Amazon Basics 预警。
  - 低价格预警。
  - 成熟产品预警。
- `test_category_scanner.py`
  - V2 Category Scanner 硬过滤和软过滤规则。
- `test_launch_score.py`
  - Launch Score 六个维度和预算输出。
- `test_supplier_score.py`
  - Supplier Score 简化版。
- `test_npfs.py`
  - NPFS 权重、推荐等级和风险等级。
- `test_discover_api.py`
  - Discover API 创建项目、报告和产品机会。
- `test_radar_api.py`
  - Radar 列表、筛选、排序和详情。
- `test_v2_backend_suite.py`
  - 固定 V2 样例得分稳定。
  - Discover → Radar Detail → Validate → Report 端到端后端链路。

## 前端测试

最低要求：

```powershell
cd frontend
npm run build
npm run smoke
```

当前自动 smoke 已覆盖主要页面。后续如果引入 Playwright，优先覆盖：

- Discovery 首页提交并跳转 Radar。
- Radar 产品卡片进入产品详情。
- 产品详情页点击 Validate Keyword。
- Validate 提交后进入报告页。
- 报告页包含 NSFS、推荐等级和商品表格。

## 手工回归检查清单

在确认 V2 稳定前运行以下检查：

- `/` 是 Discovery 首页。
- `/validate` 保留 V1 关键词验证。
- 使用 mock provider 时 Discover 和 Analyze 请求成功。
- Analyze 请求能够处理无效价格区间。
- Discover 请求能够处理无效价格区间。
- Radar 页面能显示产品机会卡片。
- 产品详情页能显示 NPFS、Launch、Supplier、风险和差异化建议。
- Product Opportunity 的 Validate Keyword 可以生成 V1 报告。
- 报告详情可以通过已保存的 report ID 加载。
- 报告列表可加载。
- Top20 表格显示全部商品。
- 预警区域可处理空预警。
- 预警区域可处理多条预警。
- 前端构建通过。
- 后端测试通过。
