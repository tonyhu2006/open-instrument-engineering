# OpenInstrument 工作日志（append-only）

> 按照全局规则要求维护：每完成一个子任务追加一条记录，记录"修改了什么、为什么"。
> **不要删除或重写历史条目**。日期使用 `YYYY-MM-DD`。

---

## 2026-04-26 — 管理后台前端打磨 + 文档同步

> 关联文档：
> - `docs/IMPLEMENTATION.md` §2.0.3
> - `docs/SPECIFICATION.md` (v0.3.1 变更摘要、Client 业务约束、数据分类表)
> - `docs/DEVELOPMENT_ROADMAP.md` (v0.2.19)

### 架构变更
- **项目级 Membership 概念前端弃用**。删除 `frontend/src/pages/admin/MembershipsPage.tsx`；同步清理 `App.tsx` 路由、`AdminLayout` 侧边标签、`AdminDashboard` 卡片、`Header.tsx` 标题映射、`pages/admin/index.ts` 导出、`usePermissions.canManageMemberships`。
  - 后端 `ProjectMembership` 模型/序列化器/视图与 `lib/api.ts` 中的 `membershipApi` 暂不删除，保留待清理。
  - 用户的项目访问权改为通过加入「工程项目组 (TaskForce)」间接获得。

### 工程项目组（TaskForce）前端集中管理
- `TaskForcesPage` 列表去掉按 `selectedProject` 过滤，加载所有项目下的项目组。
- 新增「所属项目」表格列（双行：项目编号 + 项目名称）。
- 搜索覆盖项目编号/名称 + 项目组代码/名称四字段。
- 编辑对话框新增**必填**「关联工程项目」下拉：管理员可任选；非管理员锁定为当前导航项目；编辑模式整列禁用（关联不可改）。
- `(project_id, code)` 唯一约束冲突给出友好中文提示，提示所选项目下代码已存在。

### 工程项目层级（ProjectHierarchy）
- `ProjectHierarchyPage` 顶部按钮智能切换：项目下无客户 → 「+新建客户」；已有客户 → 「编辑客户」。
- 强制"一项目一客户"业务约束（仅 UI 层；DB 未加 unique 约束保留扩展余地）。

### Admin Dashboard / Layout 重排
- `AdminDashboard` 拆分为三段式：上 = 权限概览；中 = 系统管理（仅管理员）；下 = 项目与团队（PM/PE+）。
- 新增 `ModuleSection` 抽象组件按 `required` 字段分流卡片。
- `AdminLayout` 标签栏顺序：总览 → 组织 → 用户 → 角色 → 审计日志 → 工程项目 → 工程项目组（与 Dashboard 分组对齐）。

### 通用 UI 组件
- `AdminTable` 支持列宽鼠标拖拽调整，双击重置；最小 60px；通过 `<colgroup>` + `tableLayout: fixed` 实现。可选 prop `resizable`（默认 true）。
- `Dialog` 新增 `dismissable` prop（默认 `false`）：点击遮罩 / Esc / X 按钮均**不**关闭，仅显式按钮触发；可加 `dismissable` 属性恢复旧行为。

### 后端 / 配置
- `backend/config/settings.py`：
  - 新增 `CSRF_TRUSTED_ORIGINS = ["http://localhost:*", "http://127.0.0.1:*"]`（Django 4+ 端口通配），修复 Windsurf 浏览器预览随机端口下 CSRF 校验失败。
  - 新增 `CORS_ALLOWED_ORIGIN_REGEXES`（localhost / 127.0.0.1 端口通配）。
  - 两者均从环境变量读取，生产环境可覆盖收紧。
  - 修改 settings 后需手动重启 `runserver`。

### 文档更新
- `IMPLEMENTATION.md`：版本 0.3.0 → **0.3.1**，新增 §2.0.3 "管理后台前端 UI 打磨 (2026-04-26)"，6 个子表格按主题分类。
- `SPECIFICATION.md`：版本 0.3.0 → **0.3.1**，文件头加变更摘要；§2.3.2 数据分类表更新成员关系条目；§3.1.2 Client 加业务约束说明；§3.1 多租户层级架构图更新。
- `DEVELOPMENT_ROADMAP.md`：版本 0.2.18 → **0.2.19**，已实现清单中"项目成员 UI"条目改写为本日集中改进列表。

### 风险与待办
- 后端 `ProjectMembership` 后续考虑：是否生成迁移移除该表，或保留作为审计回溯用。决策时间未定。
- `lib/api.ts` 中 `membershipApi` 已无引用，可在下次清理 PR 中移除。
- AdminTable 拖拽列宽未持久化（刷新后重置）；如有需要可在后续添加 localStorage 持久化。

---

## 2026-04-26 (后续) — 国际化 i18n 框架接入

> 关联文档：`docs/IMPLEMENTATION.md` §2.0.4

### 框架搭建
- 安装 `i18next` + `react-i18next` + `i18next-browser-languagedetector`。
- 新建 `src/i18n/index.ts`：默认 `en-US`，启用 LanguageDetector，存于 `localStorage('openinstrument.lang')`。
- 新建 `src/i18n/locales/en-US.json`（主）和 `zh-CN.json`（镜像，约 500 行翻译）。命名空间：`common` / `header` / `sidebar` / `admin` / `organizations` / `users` / `roles` / `projects` / `hierarchy` / `taskforce` / `auditLogs` / `dialog` / `table`。
- `tsconfig.app.json` 加 `resolveJsonModule: true`。
- `main.tsx` 加 `import './i18n'`，启动时初始化。

### 全部迁移到 t() 调用的文件
**Admin 页面（7 个）**：AdminLayout、AdminDashboard、TaskForcesPage、ProjectHierarchyPage、ProjectsPage、UsersPage、RolesPage、OrganizationsPage、AuditLogsPage。
**共享组件（6 个）**：AdminTable、AdminPageHeader、RoleGuard、Header、Dialog、ResizableSidebar。

### 关键技术决策
- ProjectHierarchyPage 的 EditDialogContent 不能直接调用 hook（属于子组件，签名不变），改为从父组件传入 `t: TFunction` 参数。
- Hierarchy 各层级（client / site / plant / area / unit）共享 5 套对话框结构，使用动态键 `t(\`hierarchy.${ns}.placeholder.code\`)` 等达到 DRY。
- ProjectsPage 状态徽章用 `t(\`projects.status.${r.status}\`)`，避免维护双语 STATUS_LABELS 表。
- AuditLogsPage 时间戳用 `toLocaleString(i18n.language)` 替代硬编码 `'zh-CN'`。
- AdminTable / AdminPageHeader 等共享组件默认 prop 使用 `??` 回退到 i18n 缺省值，调用方零侵入。

### 验证
- 全局 grep `[\u4e00-\u9fff]` 在 `pages/admin/**`、`components/hierarchy/**`、`components/auth/**`、`components/layout/**`、`components/ui/**` 五个目录下结果：**0 处**。
- `npx tsc -b --noEmit` 通过零错误。

### 风险与待办
- 仪表索引 / Dashboard / 状态页 / Login 页面未在本轮范围内，仍可能保留少量英文/中文混杂，下个迭代统一处理。
- 设置页面应增加语言选择器（读取/写入 `i18n.changeLanguage()` + `localStorage`）。当前用户切换语言需手动改 localStorage 后刷新。
- 实现其他翻译包时建议用 i18next 提供的 CLI 提取工具校验键完整性。
- `zh-CN.json` 中部分键值（如 `hierarchy.area.createTitle: "新建区域 (Area)"`）保留了英文括号注释，便于交叉对照；后期可统一去括号。

---

## 2026-04-26 (后续 2) — 项目组成员管理改为独立页面

> 用户反馈：项目组成员管理 UI 当前是弹出对话框，希望改成与"工程项目层级管理"一致的固定页面（独立路由 + 头部 + 操作区 + 列表）。

### 改动
- 新增页面 `frontend/src/pages/admin/TaskForceMembersPage.tsx`：参考 `ProjectHierarchyPage` 布局（面包屑返回 + 项目组信息卡 + 成员统计 + 添加表单 + 成员列表），样式上保持一致。
- 路由：`/admin/task-forces/:id/members`（在 `App.tsx` 注册，`pages/admin/index.ts` 导出）。
- `TaskForcesPage.tsx`：
  - Members 按钮 onClick 改为 `navigate('/admin/task-forces/${id}/members')`。
  - 移除 `Dialog` Members 弹窗、`membersOf` / `members` / `addingMember` state、`openMembers` / `handleAddMember` / `handleRemoveMember` 函数、`UserPlus` / `UserMinus` / `TaskForceMembership` 导入。
- 新页面使用现有 i18n 命名空间 `taskforce.members.*`，新增 `pageTitle` / `back` / `taskForceNotFound` / `manageTitle` / `stat.*` / `roleOptions.*` / `noMembers` / `addedAt` 等键并在 `en-US.json` 与 `zh-CN.json` 同步。
- 页面级权限：`RoleGuard require="canManageTaskForces"` + 内部 `canEditOwnTaskForce(taskForce.leader)` 控制添加/移除按钮。
- 加载/错误/不存在三态与 `ProjectHierarchyPage` 一致。

### 验证
- `npx tsc -b --noEmit` 通过零错误。
- 路由导航正确（点 Users 图标进入新页面，Back 返回 `/admin/task-forces`）。

---

## 2026-04-26 (后续 3) — 移除 ProjectDomain 在 admin / API 层的暴露（方案 B）

> 用户反馈：django-tenants 默认要求的 `Domain` 模型在本项目 header-based 路由架构下毫无运行时作用，admin 页面里那条 `localhost → PRJ-2025-001` 数据多余且引发混淆。

### 背景
- 本项目通过 `apps.tenants.middleware.HeaderBasedTenantMiddleware` 用 `X-Project-ID` HTTP 头切换 PG schema，**不**依赖 django-tenants 默认的 Host-header 路由。
- `ProjectDomain`（`DomainMixin` 子类）只为满足 `settings.TENANT_DOMAIN_MODEL` 框架契约而存在，运行时永远不会被查询。

### 改动
- `backend/apps/tenants/admin.py`：取消 `@admin.register(ProjectDomain)`，加注释说明原因；移除 `ProjectDomain` import。
- `backend/apps/tenants/views.py`：删除 `ProjectDomainViewSet`，移除 `ProjectDomain` / `ProjectDomainSerializer` / 未使用的 `status` import。
- `backend/apps/tenants/urls.py`：删除 `router.register(r'domains', ...)` 与 `ProjectDomainViewSet` import。
- `backend/apps/tenants/serializers.py`：删除 `ProjectDomainSerializer` 与对 `ProjectDomain` 的 import。
- `backend/apps/tenants/models.py`：将 `ProjectDomain` docstring 重写为「contract-only, no runtime role」明确标注，提示未来若改子域路由的迁移路径。
- 数据清理：`python manage.py shell -c "ProjectDomain.objects.all().delete()"` 删掉残留的 1 条 `localhost` 记录（`Deleted 1 ProjectDomain row(s).`）。

### 保留
- `ProjectDomain` 模型类与底层数据表 — django-tenants 框架契约要求 `settings.TENANT_DOMAIN_MODEL` 必须指向 DomainMixin 子类，删模型会引发框架启动失败。
- `config/settings.py` 的 `TENANT_DOMAIN_MODEL = "tenants.ProjectDomain"` 配置不变。

### 不做的事
- **未**自动在 `ProjectTenant.save()` 创建占位 domain 行。`HeaderBasedTenantMiddleware` 不读 domain，空表无副作用，保留最干净状态。

### 验证
- `python manage.py check` 通过，0 issues。
- Django admin 左侧栏 TENANTS 区不再显示 "Project Domains" 链接。
- 后端 `/api/tenants/domains/` 端点 404（已移除）。
- 前端无任何 domain 调用（grep 已确认）。

### 未来迁移路径（如需启用子域路由）
1. 把 `MIDDLEWARE` 中的 `HeaderBasedTenantMiddleware` 换回 `django_tenants.middleware.TenantMainMiddleware`。
2. 重新注册 `ProjectDomainAdmin`，恢复 `ProjectDomainViewSet/Serializer/URL`。
3. 给每个 `ProjectTenant` 写入对应 `ProjectDomain` 行（手工或脚本）。
4. DNS 加泛解析、Nginx `server_name *.example.com`、Django `ALLOWED_HOSTS` 配置同步。

---

## 2026-04-27 — 清理三项遗留 TODO

> 处理上一轮记录的"风险与待办"：
> 1) 后端 `ProjectMembership` 表彻底删除；2) 前端 `membershipApi` 死代码删除；3) `AdminTable` 列宽 localStorage 持久化。

### 1. 后端 ProjectMembership 彻底清理

ProjectMembership 自项目改用 `ProjectTaskForce + TaskForceMembership` 体系后已废弃，前端无引用、`audit_log_service` 无 hook 调用、admin 也只剩孤立的 CRUD 页面。

**改动**：
- `backend/apps/administration/models.py`：删除整个 `ProjectMembership` 类，加注释说明历史。
- `backend/apps/administration/admin.py`：取消 `@admin.register(ProjectMembership)`，移除 import。
- `backend/apps/administration/views.py`：删除 `ProjectMembershipViewSet`，移除 model/serializer import。
- `backend/apps/administration/serializers.py`：删除 `ProjectMembershipSerializer`，移除 import。
- `backend/apps/administration/urls.py`：删除 `r"project-memberships"` 路由注册。
- 生成迁移：`python manage.py makemigrations administration --name remove_projectmembership`，得到 `0004_remove_projectmembership.py`（`Delete model ProjectMembership`）。
- 应用：`python manage.py migrate_schemas --shared` 成功，`Applying administration.0004_remove_projectmembership... OK`。

**验证**：
- `python manage.py check` 通过 0 issues。
- 后端 `/api/admin/project-memberships/` 端点 404。

### 2. 前端 membershipApi 删除

`frontend/src/lib/api.ts`：
- 删除 `ProjectMembership` interface（约 12 行）。
- 删除 `membershipApi` 对象（list/create/update/delete 共 10 行）。
- 全局 grep `membershipApi|ProjectMembership|project-memberships` 无残留引用。

### 3. AdminTable 列宽 localStorage 持久化

`frontend/src/pages/admin/components/AdminTable.tsx`：
- 新增可选 prop `storageKey?: string`。
- 新增模块级辅助函数 `loadStoredWidths` / `saveStoredWidths`，键名前缀 `openinstrument.adminTable.cols.`。
- `useState` 初始化时若 `storageKey` 存在则合并 localStorage 中的宽度（覆盖默认值，再被新增列默认值补齐）。
- 新增 `useEffect([widths, storageKey])` 在每次宽度变化时持久化（含拖动结束、双击重置、新列插入）。
- 异常路径（quota / parse 失败 / 非法值）静默吞掉，不影响渲染。

各 admin 页面接入：
- `UsersPage` → `admin.users`
- `OrganizationsPage` → `admin.organizations`
- `RolesPage` → `admin.roles`
- `ProjectsPage` → `admin.projects`
- `TaskForcesPage` → `admin.taskForces`
- `AuditLogsPage` → `admin.auditLogs`

未传 `storageKey` 的 AdminTable 实例仍按"会话级"行为运行，零侵入。

### 验证
- `python manage.py check` ✅
- `npx tsc -b --noEmit` ✅
- 拖宽列后刷新页面，列宽保持。
- `localStorage` 中可见 6 个 `openinstrument.adminTable.cols.admin.<name>` 键。

### 风险与待办（更新）
- 当用户在不同浏览器/设备登录时，列宽不同步（仅本机持久）。如未来需要服务端同步，可在用户偏好表中增加 `tablePreferences` JSONField。
- localStorage key 命名一旦发布需保持兼容；如需强制重置可改前缀版本号。

---

## 2026-04-27 (后续 4) — SPECIFICATION.md 补充 ProjectDomain 部署说明

- `docs/SPECIFICATION.md` 版本号升至 0.3.2，变更摘要同步更新。
- 数据分类表 (§2.3.2) 修正：ProjectDomain 标注 *(contract-only)*，ProjectMembership 标注已删除。
- 新增 §2.3.5「ProjectDomain 与部署说明」：完整阐述 Header-based 路由机制、部署场景兼容性矩阵、唯一框架约束、以及未来迁移到子域 SaaS 的逆向操作清单。

---

## 2026-05-03 (后续 6) — i18n 全量补全：剩余页面 + Settings + 校验脚本

> 目标：落实「风险与待办」全部四条。

### 改动清单

**1. 页面 i18n 迁移（5 个页面）**
- `Dashboard.tsx`：标题、欢迎语、4 张状态卡、快速开始步骤、系统信息 → 全部 `t()` 键。
- `StatusPage.tsx`：页头、刷新按钮、上次检查时间（`toLocaleTimeString(i18n.language)`）、连接错误卡、3 张服务卡 → 全部 `t()` 键。
- `LoginPage.tsx`：副标题、字段标签、占位符、按钮文字、演示账号区、页脚 → 全部 `t()` 键。
- `InstrumentsPage.tsx`：页头、工具栏、列标题（依赖 `[t, i18n.language]`）、状态徽章（`t('instruments.status.STATUS')`）、空状态、分页文字 → 全部 `t()` 键。`SpecField.label` 重构为 `labelKey`（i18n 路径）。
- `TagDetailPage.tsx`：页头、操作按钮、分组标题、字段标签、下拉占位符、未保存提示 → 全部 `t()` 键。

**2. 翻译文件**
- `en-US.json` + `zh-CN.json`：新增 `dashboard / statusPage / login / instruments / tagDetail / settings` 六个根命名空间，各包含全量键。

**3. Settings 页（新建 `SettingsPage.tsx`）**
- 路由：`/settings`（替换 PlaceholderPage）。
- Tabs：「通用 / 账户 / 通知 / 高级」；非通用 tab 展示占位文本。
- 通用 Tab：`<Select>` 语言下拉（`SUPPORTED_LANGUAGES`），`i18n.changeLanguage()` + `localStorage` 持久化，切换后即时显示确认消息。
- 新增 `pages/index.ts` 导出；`App.tsx` 注册路由。

**4. i18n key-completeness 校验脚本**
- 新建 `frontend/scripts/i18n-check.mjs`：flatten → 对比所有 locale 与 en-US 的叶节点键集合，报告缺失键/多余键/类型不符/空值，CI 可直接 `exit 1`。
- `package.json` 新增 `"i18n:check": "node scripts/i18n-check.mjs"`。

**5. zh-CN.json 括号注释清理**
- `hierarchy.area.createTitle`: `"新建区域 (Area)"` → `"新建区域"`
- `hierarchy.unit.createTitle`: `"新建单元 (Unit)"` → `"新建单元"`
- `roles.fields.permissions`: `"权限矩阵 (JSON)"` 保留（JSON 为技术规范术语）。

---

## 2026-05-03 (后续 7) — AdminTable 列宽持久化：版本化 key + 服务端同步

> 落实后续 3 中「风险与待办」两条：跨设备同步 + localStorage key 兼容性。

### 改动清单

**1. localStorage key 版本化**
- `STORAGE_PREFIX` 从 `openinstrument.adminTable.cols.` → `openinstrument.adminTable.v1.cols.`。
- 新增 `migrateV0()` 辅助函数：首次读取 v1 key 为空时，自动从旧 key 迁移并删除旧 key，实现无感升级。
- 未来如需强制重置所有用户列宽，只需将 `v1` 改为 `v2`。

**2. 后端：User.ui_preferences JSONField**
- `administration/models.py` → `User` 新增 `ui_preferences = JSONField(default=dict, blank=True)`，help_text 说明 `{ tableWidths: { <storageKey>: { <colKey>: <px> } } }` 结构。
- migration: `0005_user_ui_preferences.py`。

**3. 后端：/api/admin/users/me/preferences/ 端点**
- `UserViewSet` 新增 `@action(detail=False, methods=["get","patch"], url_path="me/preferences")`。
- `GET` 返回 `ui_preferences` 原始 JSON。
- `PATCH` 执行二级深合并（top-level shallow + second-level dict merge），只写 `update_fields=["ui_preferences"]`。

**4. 前端：preferencesApi (api.ts)**
- `preferencesApi.get()` → `GET /admin/users/me/preferences/`。
- `preferencesApi.patch(data)` → `PATCH /admin/users/me/preferences/`。

**5. 前端：useTablePreferencesSync hook**
- 新建 `hooks/useTablePreferencesSync.ts`。
- `useEffect` (mount): 拉取服务端 `tableWidths`，对本地不存在的 storageKey 种子写入 localStorage（server→local，本地优先）。
- `save(storageKey, widths)`: localStorage 即时写入 + 2s debounce PATCH 到服务端。
- 卸载时 flush 未发送的 pending batch。
- 离线 / 未认证时静默降级为 localStorage-only。
- 导出 `loadStoredWidths(storageKey)` 供 `AdminTable` 初始化时读取（含 v0→v1 自动迁移）。

**6. AdminTable 重构**
- 移除内联 `loadStoredWidths` / `saveStoredWidths` / `STORAGE_PREFIX`。
- 引入 `useTablePreferencesSync` hook，persist effect 调用 `syncSave(storageKey, widths)`。
- 6 个 admin 页面（UsersPage / OrganizationsPage / RolesPage / ProjectsPage / TaskForcesPage / AuditLogsPage）零改动——接口不变。

### 验证
- `python manage.py check` ✅
- `npx tsc -b --noEmit` ✅

---

## 2026-05-03 — GitNexus 代码图谱索引

> 目标：使用GitNexus索引整个项目仓库，构建全面完整的代码图谱，确保彻底了解项目各个方面。

### 索引执行
- 命令：`npx gitnexus analyze --embeddings`（项目根目录执行）
- 索引时间：2026-05-03T10:58:40.890Z
- 最后提交：ca3edd6d135528b17a2347109bb68bba3a57716b
- 耗时：54.2秒

### 索引统计
- **文件数**：138
- **符号数**：636（函数、类、方法等）
- **关系数**：1,325（调用、导入、继承等）
- **社区数**：63（功能模块聚类）
- **流程数**：45（执行流追踪）
- **嵌入向量**：519（语义搜索支持）

### 功能模块（社区聚类）
1. **Admin**（53个符号，内聚度86%）：管理后台核心功能
2. **Core_engineering**（29个符号，内聚度98%）：核心工程逻辑
3. **Administration**（22个符号，内聚度95%）：系统管理
4. **Hierarchy**（12个符号，内聚度95%）：项目层级管理
5. **Tenants**（10个符号，内聚度94%）：多租户架构
6. **Pages**（10个符号，内聚度100%）：页面组件
7. **Hooks**（9个符号，内聚度100%）：React Hooks
8. **Contexts**（5个符号，内聚度100%）：React Contexts

### 执行流示例（45个流程）
- 跨社区流程：TaskForcesPageInner → UseCurrentUser/GetDiscipline
- 社区内流程：AdminTable → SafeParseWidths/FlushToServer
- 权限流程：Get_queryset → Is_administrator
- 用户管理：UsersPageInner → Deactivate/Activate/Load
- 保存流程：HandleSave → User（跨社区）

### GitNexus MCP工具可用性
- `query`：按概念查找执行流（BM25+语义向量混合检索）
- `context`：360度符号视图（调用者/被调用者/流程参与）
- `impact`：爆炸半径分析（修改影响范围）
- `detect_changes`：Git变更影响分析
- `rename`：多文件安全重命名
- `cypher`：原始图查询
- `list_repos`：索引仓库列表

### 可访问资源
- `gitnexus://repo/Open Instrument/clusters`：所有功能区域
- `gitnexus://repo/Open Instrument/processes`：所有执行流
- `gitnexus://repo/Open Instrument/cluster/{name}`：模块详情
- `gitnexus://repo/Open Instrument/process/{name}`：流程追踪

### 验证
- 索引完整性：636个符号，1325条关系，覆盖138个文件
- 嵌入向量：519个，支持语义搜索
- 社区聚类：8个主要模块，内聚度86%-100%
- 执行流：45个流程，包含跨社区和社区内交互

---

## 2026-05-04 — 项目可见性规则（SPECIFICATION §3.1.0.5.6）

> 规则：未加入任何 `ProjectTaskForce` 的普通用户，不可见也不可操作系统中任何工程项目（`ProjectTenant`）。Administrator / superuser 全局 bypass。

### 改动清单

**1. SPECIFICATION.md**
- 版本 `0.3.2 → 0.3.3`，添加变更摘要。
- 新增 §3.1.0.5.6「项目可见性规则（强约束）」：核心规则、判定公式（成员 ∪ leader）、5 个实施锚点、与 RBAC/数据隔离的关系。

**2. 后端：`apps/administration/access.py`（新建）**
- `is_administrator(user) -> bool`：superuser 或 role.level == ADMINISTRATOR。
- `user_accessible_project_ids(user) -> list[int] | None`：返回 user 可访问的 project_id 列表；`None` 表示管理员 bypass；`[]` 表示无成员关系（看不到任何项目）。
- `user_can_access_project(user, project_id) -> bool`：单点校验。

**3. 后端：`apps/tenants/views.py::ProjectTenantViewSet`**
- `get_queryset()` 由 `organization_id` 过滤改为 `pk__in=user_accessible_project_ids(user)`。

**4. 后端：`apps/tenants/middleware.py::TenantContextMiddleware`**
- `request.available_projects` 由 organization 过滤改为 membership 过滤。
- 新增 X-Project-ID 校验：当前 tenant 不在 accessible 集合中时，重置 schema 到 public 并返回 `403 {"error": "You are not a member of this project."}`。
- 适用于 session-auth 路径（如 Django admin）。

**5. 后端：`apps/administration/permissions.py::IsProjectMemberOrPublicSchema`（新建）**
- DRF 权限类，作用于 JWT-auth 路径。
- 公共 schema 通过；项目 schema 必须用户在 accessible 集合中（admin bypass）。
- 注册到 `REST_FRAMEWORK.DEFAULT_PERMISSION_CLASSES`，**全局生效，所有 ViewSet 自动启用**。

**6. 前端**
- 无需改动：`/tenants/projects/` 由后端 queryset 自动过滤，普通用户列表为空时 UI 自然显示空态。

### 验证
- `python manage.py check` ✅
- 中间件顺序：`HeaderBasedTenantMiddleware`（first，set tenant）→ `AuthenticationMiddleware` → `TenantContextMiddleware`（after auth）。
- DRF 双层防御：middleware 拦截 session-auth + 权限类拦截 JWT-auth。
- Admin bypass 路径：`is_administrator()` 在两处统一判定，避免分裂。

### 行为变化对比

| 场景 | 旧行为 | 新行为 |
|---|---|---|
| Org A 用户 + 加入 Project A 的 TaskForce | 看到 Org A 全部项目 | 仅看到 Project A |
| Org A 用户 + 未加入任何 TaskForce | 看到 Org A 全部项目 | **列表为空，无法访问任何项目** |
| Administrator | 全部项目 | 全部项目（不变） |
| 跨 org 加入 TaskForce | 不可见 | 可见对应项目 |
| 伪造 X-Project-ID | 切换成功，可读租户数据 | 中间件/权限类双重 403 拦截 |
