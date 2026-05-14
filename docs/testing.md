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

这会针对 `http://127.0.0.1:3000` 检查首页和报告列表。

如需包含报告详情页：

```powershell
cd frontend
$env:SMOKE_REPORT_ID="1"
npm run smoke
```

使用 `FRONTEND_BASE_URL` 指向不同的前端服务。

## 待补充后端单元测试

目标命令：

```powershell
cd backend
.\.venv\Scripts\pytest
```

必要测试：

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

## 待补充前端测试

最低要求：

```powershell
cd frontend
npm run build
```

建议的 Playwright 测试：

- 首页渲染表单。
- 用户提交关键词。
- 出现加载状态。
- 用户进入报告页。
- 报告页包含 NSFS、推荐等级和商品表格。
- 报告页列出已创建报告。

## 手工回归检查清单

在确认 V1 稳定前运行以下检查：

- 首页可加载。
- 使用 mock provider 时 Analyze 请求成功。
- Analyze 请求能够处理无效价格区间。
- 报告详情可以通过已保存的 report ID 加载。
- 报告列表可加载。
- Top20 表格显示全部商品。
- 预警区域可处理空预警。
- 预警区域可处理多条预警。
- 前端构建通过。
- 后端测试通过。
