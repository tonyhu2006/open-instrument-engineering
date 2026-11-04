# AGENTS.md — Open Instrument 项目 Agent 行为契约

适用于本仓库内运行的所有编码 agent。**当前唯一实现 agent 为 Claude Code（经 ACP 接入 Devin Desktop）**；Devin Review 仅承担 PR 初筛；Devin Local 休眠不参与实现。本契约对未来接入的任何 agent 同样适用，不因 agent 更换而修改。
本文件是行为约束；事实来源是唯一 spec **`docs/SPECIFICATION.md`**（含架构与数据模型、15 个模块功能需求、§4 全局契约、§5.4 API 端点权威清单、§4.12.1 决策记录 D1–D5、第七部分 WP 分解与交付协议；本文引用的 §x.x 章节号均指此文件）。实现与 spec 冲突时，停下提问，不得擅自变更 spec 语义；发现 spec 内部矛盾记录到 `docs/OPEN_QUESTIONS.md`。
**注意**：文末 `<!-- gitnexus:start -->` 到 `<!-- gitnexus:end -->` 之间是 GitNexus 自动管理块，**任何 agent 和人都不得手工编辑该块**；本节内容一律写在标记之外。

## 项目一句话

Web 版仪表工程设计系统（对标 Hexagon SPI）：Django 5.2 + DRF（Python ≥3.11，`uv` 管理）+ React 19/TypeScript（Vite 7, Tailwind v4, Shadcn）+ PostgreSQL 16 + Redis 7 **均运行于本地 Docker**（docker-compose，**非标端口 5433 / 6380**——刻意避让本机已安装、供其它应用使用的 PostgreSQL/Redis 实例；**禁止改回 5432/6379，禁止连接宿主机原生实例**），django-tenants 多租户（PostgreSQL Schema 隔离），monorepo。许可证 **AGPL-3.0**（README 的 MIT 徽章是错的，勿引用）。

## 硬性规则（违反即返工）

1. **租户边界**：TENANT_APPS 业务表**禁止**出现 `domain_id`/`project_id` 列——schema 即隔离边界。仅 public schema 跨项目模型使用 `project_id`。
2. **跨 schema 引用模式**：tenant 模型与 shared 模型之间**禁止真实 ForeignKey**。跨 schema 引用一律存 `project_id` 纯 `IntegerField` 并暴露 `project` property 显式查询（参照 `apps/administration/models.py` 的 `ProjectMembership`/`ProjectTaskForce`/`AuditLog`）。
3. **迁移命令**：一律 `migrate_schemas`，禁用裸 `migrate`（只动 public schema）。新增 tenant 迁移后必须跑 `migrate_schemas` 让所有既有租户生效。`ProjectTenant` 的 `auto_create_schema=True` 意味着保存新行即建 schema——测试中慎用。
4. **用户模型**：只经 `settings.AUTH_USER_MODEL` 引用（`administration.User`），禁止直接 import。
5. **Service 层**：业务写操作经 Service 层；ViewSet 不写复杂业务逻辑。
6. **契约先行**：模型/序列化器变更 → OpenAPI（`/api/schema/`）→ 前端 client。禁止手写不一致 DTO。
7. **写接口五件套**：权限、校验、事务、审计、`row_version` 乐观锁，缺一不可。
8. **只做当前 WP**（SPECIFICATION.md §7.2）：禁止顺手改其他 WP 目录、禁止改 `docs/` 下任何 spec 文档。疑问 → 追加到 `docs/OPEN_QUESTIONS.md`（此文件是唯一例外，允许 agent 追加、不允许删改既有条目）。
9. **完成 = 验证全绿**：结束前逐条执行下方 V1–V6 并贴输出。**不允许以"应该没问题"替代实际运行；重构后必须重跑测试。**
10. **高风险模块（计算/接线 WIR/规则引擎）**：先测试向量与服务类，后 UI；公式标注标准出处与版本。
11. **Git 纪律**：禁止 force push main、禁止 `--no-verify`。前端所有租户级请求必须带 `X-Project-ID` 头。

## 验证协议 V1–V6（按本仓库实际命令）

```bash
docker-compose up -d          # 前提：Docker 容器 PG:5433 / Redis:6380（唯一合法数据源，勿连宿主机 5432/6379）

# V1 迁移与种子（backend/ 目录下）
uv run python manage.py migrate_schemas --shared
uv run python manage.py migrate_schemas
uv run python manage.py seed_admin_data && uv run python manage.py seed_demo_data

# V2 静态检查
uv run ruff check . && uv run black --check .

# V3 单元测试（本 WP 范围；H 级服务类覆盖率 ≥90%）
uv run pytest <本WP路径> -x

# V4 OpenAPI 契约（backend/ 目录下；0 error 且 0 warning 才算通过）
uv run python manage.py spectacular --validate --fail-on-warn > /dev/null

# V5 前端（frontend/ 目录下）
npm run lint && npm run build

# V6 租户隔离回归（backend/ 目录下；仓库根目录等效：uv run --directory backend pytest tests/test_tenant_isolation.py -x）
uv run pytest tests/test_tenant_isolation.py -x
```

## 已知残缺与坑（agent 撞到时按此处理，不要自作主张绕过）

- `frontend/src/lib/`（`api.ts` 与 `utils.ts`）已纳入版本控制。根 `.gitignore` 的 Python `lib/` 规则曾误忽略该目录，现由 `!frontend/src/lib/` 例外放行——**禁止删除该例外**；在其它 `lib/` 目录下新增前端文件前，先用 `git check-ignore -v <路径>` 确认未被忽略。
- mypy 未配置：暂不作为 V 门槛；引入配置属于独立小 WP，不得夹带。
- pytest 已配置于 `backend/pyproject.toml` 的 `[tool.pytest.ini_options]`（`DJANGO_SETTINGS_MODULE=config.settings`、`testpaths=["tests"]`）；pytest-django 自建 `test_` 数据库，不触碰开发库。跨 app / 租户级测试放 `backend/tests/`，共享 fixture（含会话级双租户 `isolation_tenants`）在 `backend/tests/conftest.py`。
- **RBAC（已裁决，决策 D5，见 SPECIFICATION.md §4.12.1/§15.2.1）**：权限等级维持代码现行 **5 级** `Role.Level`（禁止增改枚举，Level 2 预留）；系统预设角色为 **7 个**（§15.2.2 表，`is_system_role=True`），缺失的角色以数据迁移补齐（WP-02 交付物）。权限判定走 `Role.permissions` 矩阵，禁止按 `role.code` 硬编码业务分支（Administrator 旁路除外）。
- `docs/` 内部优先级：SPECIFICATION.md（唯一 spec，架构与功能双重权威）> IMPLEMENTATION.md（现状记录，只描述已建成的，不构成需求）> DEVELOPMENT_ROADMAP.md / PRD.md > README（最旧，License 徽章已知有误）。IMPLEMENTATION.md 与代码不符时，以代码为准并更新 IMPLEMENTATION.md。

## 常用路径与约定

- 所有模型继承 `apps.core.models.TimeStampedModel`。
- 路由：工程 `/api/engineering/`，管理 `/api/admin/` 与 `/api/tenants/`；JWT `/api/token/`；DRF 默认 `IsAuthenticated`，`PAGE_SIZE=50`。
- 租户切换：`HeaderBasedTenantMiddleware` 按 `X-Project-ID` 头选 schema；`/admin/` 与 `/api/token` 恒走 public。
- Ruff/Black line-length 88；Vite alias `@` → `src`；前端 dev 代理 `/api` → `:8000`。

## GitNexus 使用边界

下方 GitNexus 块的 MUST 规则适用于**已接入 GitNexus MCP 工具的 agent**。当前唯一实现 agent Claude Code 已通过 `.claude/skills/gitnexus/` 与 PostToolUse hook 完整接入，MUST 规则对其**全量生效，无豁免**。（休眠条款：未来接入未配置 GitNexus MCP 的 agent 时，以"改动前检索理解调用方 + 改动后运行受影响测试"为等效替代，并在 PR 中注明未做图谱级影响分析。）

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **Open Instrument** (636 symbols, 1325 relationships, 45 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/Open Instrument/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/Open Instrument/context` | Codebase overview, check index freshness |
| `gitnexus://repo/Open Instrument/clusters` | All functional areas |
| `gitnexus://repo/Open Instrument/processes` | All execution flows |
| `gitnexus://repo/Open Instrument/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## Keeping the Index Fresh

After committing code changes, the GitNexus index becomes stale. Re-run analyze to update it:

```bash
npx gitnexus analyze
```

If the index previously included embeddings, preserve them by adding `--embeddings`:

```bash
npx gitnexus analyze --embeddings
```

To check whether embeddings exist, inspect `.gitnexus/meta.json` — the `stats.embeddings` field shows the count (0 means no embeddings). **Running analyze without `--embeddings` will delete any previously generated embeddings.**

> Claude Code users: A PostToolUse hook handles this automatically after `git commit` and `git merge`.

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
