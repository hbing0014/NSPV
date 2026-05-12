# NSPV Testing Guide

本文档定义 NSPV 当前和后续开发的测试方式。

## Current Mandatory Checks

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

API smoke test：

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

Frontend smoke test：

1. Start backend:

```powershell
cd backend
.\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

2. Start frontend:

```powershell
cd frontend
npm run dev
```

3. Open:

```text
http://127.0.0.1:3000
```

4. Submit:

```text
keyword: sink organizer
marketplace: US
category: Kitchen & Dining
budget: 100000
target price: 20 - 40
```

Expected:

- Redirects to `/reports/{id}`.
- Shows NSFS score.
- Shows recommendation.
- Shows risk warnings.
- Shows Top20 products table.
- New report appears in `/reports`.

## Backend Unit Tests To Add

Target command:

```powershell
cd backend
.\.venv\Scripts\pytest
```

Required tests:

- `test_health.py`
  - `/health` returns status ok.
- `test_analyze_api.py`
  - valid request creates report.
  - invalid target price returns 400.
  - report detail returns saved product snapshot.
  - report not found returns 404.
- `test_scoring.py`
  - demand score thresholds.
  - review competition thresholds.
  - sponsored density thresholds.
  - profit margin thresholds.
  - NSFS weighted formula.
- `test_risk.py`
  - high Review warning.
  - high Sponsored warning.
  - Amazon Basics warning.
  - low price warning.
  - mature product warning.

## Frontend Tests To Add

Minimum:

```powershell
cd frontend
npm run build
```

Recommended Playwright tests:

- Home page renders form.
- User submits keyword.
- Loading state appears.
- User lands on report page.
- Report page contains NSFS, recommendation and products table.
- Reports page lists created report.

## Manual Regression Checklist

Run this before considering V1 stable:

- Home page loads.
- Analyze request succeeds with mock provider.
- Analyze request handles invalid price range.
- Report detail loads from saved report ID.
- Reports list loads.
- Top20 table displays all products.
- Warning section handles empty warnings.
- Warning section handles multiple warnings.
- Frontend build passes.
- Backend tests pass.

