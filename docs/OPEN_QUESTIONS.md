# OPEN QUESTIONS

## OQ-001 (2026-11-04) — AGENTS.md V6 命令路径与 uv 工作目录不一致

- **现象**：AGENTS.md「验证协议」V6 写作 `uv run pytest backend/tests/test_tenant_isolation.py -x`，但 V1–V3 约定在 `backend/` 目录下执行，而 uv 项目（`pyproject.toml`）位于 `backend/`，仓库根目录没有 uv 项目。按字面执行：在根目录 `uv run` 找不到项目；在 `backend/` 下路径 `backend/tests/...` 不存在。
- **当前可用的等效命令**：在 `backend/` 下执行 `uv run pytest tests/test_tenant_isolation.py -x`；或在仓库根目录执行 `uv run --directory backend pytest tests/test_tenant_isolation.py -x`。
- **另**：V6 需要 pytest 配置（`DJANGO_SETTINGS_MODULE`），已在 `backend/pyproject.toml` 增加 `[tool.pytest.ini_options]`。AGENTS.md「已知残缺与坑」中"pytest 无配置文件"的描述已过时。
- **待裁决**：由人工更新 AGENTS.md 的 V6 命令与上述描述。
- **✅ 已解决（2026-11-04，经用户指令）**：AGENTS.md V6 改为在 `backend/` 下执行 `uv run pytest tests/test_tenant_isolation.py -x`（注释给出仓库根目录等效命令），与 V1–V3 的工作目录约定一致；「已知残缺与坑」中 pytest 条目改为记录现行配置；CLAUDE.md 同步更新。两种写法均已实测通过。

---

> 以下 OQ-002 ~ OQ-011 由 2026-11-04「已实现功能对齐 SPECIFICATION」改造中发现并按"默认假设"先行实现，待项目方裁决。

## OQ-002 (2026-11-04) — 主键类型：§15 的 UUID 与 §4.1.1 的 BigAutoField 不一致

- **现象**：§15.2.3/§15.3.1/§15.4.7/§15.5.1 将 User、ProjectTaskForce、TaskForceMembership、Organization、NamingConvention 的 `id` 写为 UUID；§4.1.1 规定业务表主键为 BigAutoField；现有代码均为整数主键。
- **影响的 WP**：WP-02
- **默认假设（已实施）**：仅新建的 `audit.AuditLog`（§6.1.1 明确 UUID）使用 UUID；其余保持整数主键。把 User 等表的主键改为 UUID 需要破坏性迁移（JWT `user_id`、所有外键、前端 `id: number`），须项目方确认后作为独立 WP 执行。
- **状态**：待裁决

## OQ-003 (2026-11-04) — 租户表 `created_by/updated_by` 的跨 schema 外键

- **现象**：§4.1.1 写 `created_by | ForeignKey → User`，§2.1.1 也提到"跨 schema FK（租户→public）"；AGENTS.md 硬性规则 2 禁止 tenant ↔ shared 之间的真实 ForeignKey。
- **影响的 WP**：WP-01 / 全部租户模块
- **默认假设（已实施）**：遵循 AGENTS.md 规则 2，`apps.core.models.AuditedModel` 以 `created_by_id/updated_by_id` 整型字段存储，并提供 `created_by/updated_by` property 显式查询。
- **状态**：待裁决（建议在 §4.1.1 注明 Schema 隔离下的实现方式）

## OQ-004 (2026-11-04) — AuditLog「独立数据库连接」

- **现象**：ADM-07 / §4.10 要求审计日志使用独立数据库连接（DATABASE_ROUTERS），以便与业务事务解耦。
- **影响的 WP**：WP-02 / WP-15
- **默认假设（已实施）**：审计记录在同一事务内写入（数据回滚时审计也回滚，保证"有审计 ⇔ 变更已提交"），表为 append-only（ORM 层禁止 update/delete，admin 只读）。独立连接会让失败/回滚的操作也留下审计行，且与 pytest-django 的多库事务配置相关，待确认是否需要"记录失败尝试"的语义。
- **状态**：待裁决

## OQ-005 (2026-11-04) — PE 基于任意已存在项目创建项目组即可获得该项目访问权

- **现象**：ADM-TF01 允许 Project Engineer「基于已存在 Project 创建项目组」，§15.3.3 可见性公式包含 `ProjectTaskForce.leader == user`。两条合并后，PE 可为任何尚无项目组的项目建组并自动成为 leader，从而获得该项目访问权。
- **影响的 WP**：WP-02
- **默认假设（已实施）**：按 spec 字面实现，但加了两道限制：① 每个项目只能有一个项目组（§15.3.1 约束），已有项目组的项目无法再被 PE 建组；② PE 不能修改项目关联、不能管理 Admin 创建的组；前端下拉框只列出 PE 可见的项目。若需进一步收紧（例如 PE 只能为自己已是成员的项目建组），请裁决。
- **状态**：待裁决

## OQ-006 (2026-11-04) — §15.4.6 `simple` 层级模板与 PlantHierarchy 节点规则冲突

- **现象**：`simple` 模板为 Client → Site → Unit，而 §15.4.5 PlantHierarchy 只允许 PLANT → AREA → UNIT，Unit 不能直接挂在 Site 下。
- **影响的 WP**：WP-03
- **默认假设（已实施）**：选择 `simple` 时只自动创建 Client 与 Site，不自动创建 Unit。
- **状态**：待裁决

## OQ-007 (2026-11-04) — RBAC 矩阵未覆盖的资源键

- **现象**：§15.2.4 数据权限矩阵没有 Instrument Type、Naming Convention、Organization 三行；另外 ADM-TF03 要求 PM/PE 在项目组页「+ Add User」，而矩阵中用户/角色管理对 PM/PE 为"-"。
- **影响的 WP**：WP-02
- **默认假设（已实施，见 `backend/apps/administration/rbac.py`）**：`instrument_type` 按 Tag 行；`naming_convention` 按 Plant Hierarchy 行；`organization` 所有角色可读、仅 Administrator 可写。用户、角色列表的**只读**权限授予拥有 `task_force.create` 的角色，仅用于成员选择器，写权限仍只属于 Administrator。
- **状态**：待裁决

## OQ-008 (2026-11-04) — 现有 Tag / InstrumentType 不在 §5.5 模型清单中

- **现象**：§5.5 / DoD #12 要求模型必须出现在清单中（instruments app：Component、ComponentFunctionType、InstrumentTechnologyType…）。现有 `core_engineering.Tag / InstrumentType` 是 WP-04 之前的简化实现；NamingConvention 在 §5.5 中归属 administration（T），代码位于 core_engineering（同为租户 schema）。
- **影响的 WP**：WP-04
- **默认假设（已实施）**：本次只让已实现部分符合全局契约（审计字段、软删除、乐观锁、Unit 内唯一、命名规则校验），API 挂载到 §5.4.4 的 `/api/v1/instruments/`，不改模型名。迁移到 Component 模型（及数据迁移路径）留给 WP-04 统一处理。
- **状态**：待裁决

## OQ-009 (2026-11-04) — 已实现但未在 §5.4 登记的端点

- **现象**：决策 D3 要求新端点必须先登记于 §5.4。
- **默认假设（已实施）**：前端未使用且未登记的附加端点已移除（`tags/search`、`tags/by_unit`、`tags/bulk_update`、`hierarchy/tree|units|children`、`instrument-types/{id}/validate_spec`、`task-force-memberships/*`）；树查询改为 §5.4.3 列表端点的 `?tree=true` 参数。以下端点仍在使用，需项目方补登记或裁决：`GET /api/v1/health/`、`/api/v1/organizations/*`、`GET /api/v1/audit-logs/`（VC-01 的 `/api/v1/audit/{model}/{id}/changes/` 属 WP-15），以及 `POST /api/v1/tenants/projects/{id}/switch/` 的语义（实际租户选择按请求经 X-Project-ID 完成）。
- **状态**：待裁决

## OQ-010 (2026-11-04) — i18n 语言覆盖

- **现象**：§6.2 要求 12 种语言与 RTL。
- **默认假设（已实施）**：后端已配置 12 种 `LANGUAGES` 与 `LocaleMiddleware`（I18N-01），`/api/v1/me/preferences/` 接受 12 种语言代码；前端目前只提供 en-US / zh-CN 两套翻译，其余 10 种语言的翻译与 RTL 布局（I18N-03）属 WP-15。
- **状态**：待裁决（排期）

## OQ-011 (2026-11-04) — D1 废弃别名的 Sunset 日期

- **现象**：D1 要求 `/api/token/*` 别名保留"一个次要版本周期"，并返回 `Sunset` 头，但未给出具体日期。
- **默认假设（已实施）**：`Sunset: Sun, 31 Jan 2027 00:00:00 GMT`（`backend/apps/core/auth.py::SUNSET`）。
- **状态**：待确认

---

> 以下 OQ-012 ~ OQ-022 按 §4.12「仓库建库时应将下表逐条复制为 OPEN_QUESTIONS 初始条目」补录（格式 `OQ-<序号> | 问题 | 影响的 WP | 默认假设 | 状态`），内容与 SPECIFICATION.md §4.12 一致，以 spec 原文为准。

| OQ | 问题 | 影响的 WP | 默认假设 | 状态 |
|----|------|-----------|----------|------|
| OQ-012 | 是否 100% 复刻 SPI 行为 | 全部 | 复刻核心工程流程，不复刻桌面 UI 的每个交互细节 | 待裁决 |
| OQ-013 | 计算标准授权和公式版本 | WP-07 | 使用公开标准公式，由项目方确认具体版本和商业授权 | 待裁决 |
| OQ-014 | AG Grid Enterprise 授权 | WP-09 / 全部网格 | 项目方具备商业授权；否则替换为 MIT 许可网格并降低部分功能（现前端使用 TanStack Table） | 待裁决 |
| OQ-015 | 多租户隔离方式 | WP-01 | PostgreSQL Schema 隔离 + X-Project-ID Header 路由，租户单位为 ProjectTenant | 已按默认实施 |
| OQ-016 | 电子签名/法规合规 | WP-15 | 无 21 CFR Part 11 | 待裁决 |
| OQ-017 | SIL 验证计算（PFDavg / RRF / HFT） | WP-04A / CALC-15 | 不在 Phase 1 | 待裁决 |
| OQ-018 | 文档编号分段 `XX-XX` 的项目含义（D14） | WP-06 | 按 ISO 19650 Volume/System 与 Level/Location 两段实现（可配置） | 待裁决 |
| OQ-019 | Issue Purpose 取值集与版次编号方案（D14） | WP-06 | 七种取值 + `P01…P0n → 01…0n` 两段制 | 待裁决 |
| OQ-020 | WSP 模板库 21 个新增技术类型的 I/O 与字段适用性（D14） | WP-04 / WP-06A | 全部标 `needs_review` | 待裁决 |
| OQ-021 | 模板库先修复还是先绑定（D14） | WP-06A | 先修模板库再绑定 | 待裁决 |
| OQ-022 | Tag 过程数据掩码 `OPTIONAL` 值 | WP-05 | 种子仅含 REQUIRED/NA | 待裁决 |
