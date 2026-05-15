# NSPV UI 组件规范

## 设计方向

NSPV 采用“企业级数据决策平台 + 产品机会雷达”的融合风格。

核心目标：

1. 保持 B2B SaaS 的可信、专业和稳定。
2. 让 Product Radar 更像产品机会榜单，而不是普通筛选表单。
3. 用语义化颜色表达推荐、风险、预警和成功状态。
4. 用统一组件减少页面之间的视觉差异。

## 设计 Token

颜色使用 CSS 变量 + Tailwind 语义色：

- `background`：页面背景
- `card`：卡片和导航容器
- `foreground`：主文字
- `muted-foreground`：辅助文字
- `primary`：主操作和主品牌色
- `accent`：产品机会、验证入口等强调色
- `success`：低风险、推荐、通过状态
- `warning`：中风险、PPC、红海提醒
- `destructive`：高风险、错误、避免进入
- `border` / `input`：边框和输入框边界

暗色模式通过 `.dark` class 启用，组件默认兼容亮色和暗色。

## 组件目录

组件位于：

`frontend/components/ui`

已建立组件：

1. `Button`
2. `Input`
3. `Select`
4. `Card`
5. `Table`
6. `Tabs`
7. `Modal`
8. `Sidebar`
9. `AppHeader`

统一导出文件：

`frontend/components/ui/index.ts`

## 组件使用原则

### Button

用于所有明确操作。

推荐：

- 主流程：`variant="primary"`
- 次级操作：`variant="outline"` 或 `variant="secondary"`
- 危险操作：`variant="danger"`
- 成功确认：`variant="success"`
- 图标按钮：`size="icon"`

### Input / Select

用于表单和筛选器。

规则：

- 默认高度为 `40px`
- 复杂筛选区优先做紧凑 toolbar
- 不再使用超大输入框作为常规后台控件
- 错误态使用 `invalid`

### Card

用于产品机会卡、指标卡、报告模块和弹窗容器。

规则：

- 页面区块不要嵌套太多 Card
- 重复项、指标项、报告模块可以用 Card
- 关键指标使用 `CardHeader + CardContent` 分层

### Table

用于 Top20 商品、历史报告、项目列表。

规则：

- 表头使用 muted 背景
- 行 hover 提供扫描反馈
- 风险列需要使用 badge 或语义色
- 大表格必须保留横向滚动

### Tabs

用于 Radar 榜单切换、报告视图切换、风险/机会切换。

规则：

- Tab 文案应短
- 不要把关键 CTA 放进隐藏 tab
- 默认 tab 应是用户最常用路径

### Modal

用于确认、保存、导出、项目选择等轻量任务。

规则：

- 不用于复杂长表单
- 支持 Escape 关闭
- 主要操作放右下角

### Sidebar

用于后续 Dashboard / Projects / Radar / Reports 的工作台导航。

规则：

- 当前 V2 可先不强制启用
- 当页面数量继续增加时，建议引入左侧 Sidebar

### Header

用于全局顶部导航。

规则：

- 保持 sticky
- 导航项不超过 5 个
- 右侧放语言切换、账户、设置等系统操作

## 后续页面改造顺序

1. 首页 `/`：用 Card、Button、Select 重做 Product Discovery First。
2. Radar `/radar`：用 Card、Tabs、Table 建立产品机会榜单视图。
3. Product Detail：用 Card 和 Badge 强化启动预算、风险、机会。
4. Report：用 Table 和 Metric Card 提升 Top20 与评分可读性。
5. Validate：用 Field、Input、Select 收敛 V1 验证表单。
