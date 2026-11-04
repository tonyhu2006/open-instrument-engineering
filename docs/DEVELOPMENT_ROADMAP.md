# OpenInstrument 开发路线图

> **版本**: 0.2.19  
> **创建日期**: 2025-12-24  
> **最后更新**: 2026-04-26  
> **总体完成度**: ~23%

---

## 一、已实现功能清单

### 1. 基础架构 ✅ (100%)

| 功能 | 状态 | 说明 |
|------|------|------|
| Monorepo 结构 | ✅ | /backend, /frontend |
| Docker Compose | ✅ | PostgreSQL:5433, Redis:6380 |
| Django 5.2 项目 | ✅ | DRF, JWT, OpenAPI |
| React 19 + TypeScript | ✅ | Vite 7, Tailwind v4, Shadcn UI |
| 健康检查 API | ✅ | /api/health/ |
| 侧边栏 Layout | ✅ | Sidebar, Header, MainLayout |
| Dashboard 页面 | ✅ | 显示健康检查状态 |

### 2. 工程数据模型 ✅ (核心模型已完成)

| 功能 | 状态 | 说明 |
|------|------|------|
| PlantHierarchy (MPTT) | ✅ | Plant → Area → Unit 三级架构（租户数据） |
| InstrumentType | ✅ | JSON Schema 模板验证（租户数据） |
| Tag 模型 | ✅ | Unit 级唯一约束, 版本号自动递增 |
| Loop 模型 | ✅ | 控制回路 |
| Tag/Loop/InstrumentType API | ✅ | CRUD + bulk_update + search |
| 演示数据命令 | ✅ | seed_demo_data / seed_demo_project |

### 3. 多租户架构 ✅ (Schema 隔离)

| 功能 | 状态 | 说明 |
|------|------|------|
| django-tenants 集成 | ✅ | PostgreSQL Schema 级隔离 |
| ProjectTenant / ProjectDomain | ✅ | 租户元数据与域名映射 |
| HeaderBasedTenantMiddleware | ✅ | `X-Project-ID` Header 切换 schema |
| SHARED_APPS / TENANT_APPS | ✅ | 公共与租户应用分离 |
| 租户 API | ✅ | `/api/tenants/projects/` |
| 前端租户切换 | ✅ | HierarchyContext + localStorage |
| 双租户隔离验证 | ✅ | `prj_2025_001` / `prj_2025_002` 物理隔离 |

---

## 二、未实现功能清单 (按模块分类)

### 模块 1.1 - 管理模块 (Administration) - 完成度 75%

**已实现 (详 IMPLEMENTATION.md §2):**
- [x] RBAC 角色系统 (Role + display_order, 7 个预置系统角色含 PM/PE)
- [x] 用户认证 (JWT 登录/登出/刷新、/me/ 接口)
- [x] 工程项目组 (ProjectTaskForce + TaskForceMembership + 创建者隔离权限)
- [x] 项目层级 (Project → Client → Site → Plant) 及多租户物理隔离验证
- [x] 用户管理 UI (UsersPage)、角色管理 UI (RolesPage)、项目组 UI (TaskForcesPage)
- [x] 组织管理 UI (OrganizationsPage)、审计日志 UI
- [x] **2026-04-26 管理后台前端打磨** (详 IMPLEMENTATION.md §2.0.3)：
  - 项目级 Membership 概念前端弃用，`/admin/memberships` 页面下线
  - Admin Dashboard 三段式分组（权限概览 / 系统管理 / 项目与团队）
  - AdminLayout 标签栏与 Dashboard 分组对齐
  - TaskForce 集中管理（跨项目列表 + 「所属项目」列 + 关联项目必填）
  - ProjectHierarchy "一项目一客户" 业务约束（按钮智能切换）
  - AdminTable 通用列宽拖拽、Dialog 收紧关闭行为
  - CSRF/CORS 本地开发端口通配（修复 Windsurf 浏览器预览代理）

**未实现:**
- [ ] 命名规则 (NamingConvention) UI / 自定义正则编辑器
- [ ] 工厂层级 UI 中的可视化树编辑 (只读树已有)
- [ ] 项目创建向导 UI (选择层级模板)
- [ ] 二要素身份认证 (2FA) / 密码重置邮件

### 模块 1.2 - 仪表索引 (Instrument Index) - 完成度 60%

**未实现:**
- [ ] 仪表类型管理 UI
- [ ] Schema 编辑器 (JSON Schema 可视化)
- [ ] 回路管理 UI
- [ ] 典型回路 (TypicalLoop) 模型和批量实例化

### 模块 1.3 - 工程数据编辑器 (EDE) - 完成度 5%

**未实现:**
- [ ] SavedView 模型
- [ ] 动态查询构建 API (QueryBuilder)
- [ ] TanStack Table 数据网格
- [ ] 虚拟滚动 (10,000+ 行)
- [ ] 行内编辑
- [ ] 列拖拽排序
- [ ] 视图保存/共享

### 模块 1.4 - 规格书 (Specifications) - 完成度 5%

**未实现:**
- [ ] ProcessData 模型 (工艺过程数据)
- [ ] PipeSpecification 模型 (管道规格)
- [ ] SpecificationTemplate 模型
- [ ] SpecificationDocument 模型
- [ ] PDF 生成
- [ ] External Editor 导入导出 (.oisf)
- [ ] 规格书表单 UI (动态表单)

### 模块 1.5 - 接线模块 (Wiring) - 完成度 0%

**未实现:**
- [ ] JunctionBox, TerminalStrip, Terminal 模型
- [ ] Cable, CableRoute 模型
- [ ] RIOPanel, IOCard, IOChannel 模型
- [ ] WiringConnection, WiringPath 模型
- [ ] I/O 通道分配功能
- [ ] 接线箱端子分配功能
- [ ] 仪表接线制式 (2/3/4/6-Wire)
- [ ] 信号流逻辑检查
- [ ] Cable Schedule 导出
- [ ] 拖拽接线 UI

### 模块 1.6 - 回路图生成 (Loop Drawings) - 完成度 0%

**未实现:**
- [ ] SymbolLibrary 模型 (符号库)
- [ ] LoopDrawingTemplate 模型
- [ ] TitleBlockTemplate 模型 (图框)
- [ ] 回路图生成引擎 (React Flow)
- [ ] 宏自动填充
- [ ] DXF/DWG/PDF/SVG 导出

### 模块 1.7 - 规则管理器 (Rule Manager) - 完成度 10%

**未实现:**
- [ ] Rule 模型 (IF-THEN 规则)
- [ ] RuleExecution 模型
- [ ] 规则引擎
- [ ] 实时校验
- [ ] GB 标准规则库
- [ ] 规则管理 UI

### 模块 1.8 - 版本控制 (Version Control) - 完成度 5%

**未实现:**
- [ ] GlobalRevision 模型
- [ ] EntityRevision 模型
- [ ] AuditLog 模型
- [ ] 版本对比 API
- [ ] 版本回滚 API
- [ ] EditLock 并发控制
- [ ] WebSocket 实时状态同步

### 其他功能

**数据导入导出:**
- [ ] Excel 导入导出
- [ ] P&ID 数据集成 (SmartPlant/AVEVA/AutoCAD)
- [ ] DEXPI (ISO 15926) 导入

**前端 UI:**
- [ ] 层级导航树
- [ ] 上下文选择器
- [ ] 仪表索引表 (核心页面)
- [ ] 规格书表单
- [ ] 接线路径视图
- [ ] 国际化 (12 种语言 + RTL)

**测试与部署:**
- [ ] 后端单元测试
- [ ] 前端单元测试
- [ ] E2E 测试
- [ ] 生产环境 Docker 配置
- [ ] CI/CD 流水线

---

## 三、实施计划 (按软件工程最佳实践排序)

### 原则说明

1. **依赖优先**: 先实现被依赖的模块，再实现依赖它的模块
2. **核心优先**: 先实现核心业务功能，再实现辅助功能
3. **垂直切片**: 每个阶段交付可用的端到端功能
4. **风险前置**: 技术风险高的功能提前验证

---

### Phase 3: 企业级基础 (预计 3-4 周)

> **目标**: 建立多租户、认证授权、命名规则等企业级基础能力

#### Sprint 3.1: 多租户与项目层级 (1 周) ✅ 完成

| 优先级 | 任务 | 依赖 | 工作量 | 状态 |
|--------|------|------|--------|------|
| P0 | Organization 模型（公共 schema） | - | 2h | ✅ |
| P0 | ProjectTenant 模型（django-tenants TenantMixin） | Organization | 4h | ✅ |
| P0 | ProjectDomain 模型 | ProjectTenant | 2h | ✅ |
| P0 | Client 模型（租户 schema） | 租户初始化 | 2h | ✅ |
| P0 | Site 模型（租户 schema） | Client | 2h | ✅ |
| P0 | Plant 模型关联 Site（租户 schema） | Site | 2h | ✅ |
| P0 | HeaderBasedTenantMiddleware | 中间件栈 | 4h | ✅ |
| P0 | SHARED_APPS / TENANT_APPS 配置 | Django settings | 2h | ✅ |
| P1 | 层级结构配置 (hierarchy_config) | ProjectTenant | 4h | ✅ |
| P1 | 层级模板 (standard/simple/custom) | - | 2h | 📋 |
| P1 | 项目层级 API（含租户路由） | 所有模型 | 8h | ✅ |

**交付物**: 完整的多租户 Schema 隔离架构 + 项目层级数据模型与 API
**验证**: 通过 `seed_demo_project` 创建第 2 个租户 (`prj_2025_002`)，确认与 `prj_2025_001` 数据物理隔离

#### Sprint 3.2: 用户认证与 RBAC (1 周) ✅ 完成

| 优先级 | 任务 | 依赖 | 工作量 | 状态 |
|--------|------|------|--------|------|
| P0 | User 模型扩展 (AbstractUser) | - | 4h | ✅ |
| P0 | Role 模型 (层级化 + display_order) | - | 4h | ✅ |
| P0 | Permission 模型化为资源粒度 JSON | Role | 4h | ✅ |
| P0 | ProjectMembership 关联 | User, Role, Project | 4h | ✅ |
| P0 | 登录/登出 API (JWT) | User | 4h | ✅ |
| P0 | Token 刷新 API | - | 2h |
| P1 | 权限检查装饰器 | Permission | 4h |
| P1 | 登录页面 UI | 登录 API | 8h |

**交付物**: 完整的用户认证和角色权限系统

#### Sprint 3.3: 命名规则与审计 (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | NamingConvention 模型 | Project | 4h |
| P0 | 6 种层级格式实现 | NamingConvention | 8h |
| P0 | 7 种预设模板 | NamingConvention | 4h |
| P0 | 位号验证流程 | NamingConvention | 4h |
| P1 | 自动生成位号 API | NamingConvention | 4h |
| P1 | AuditLog 模型 | - | 4h |
| P1 | 自动审计中间件 | AuditLog | 4h |
| P2 | EditLock 并发控制 | - | 8h |

**交付物**: 命名规则验证、审计日志、并发控制

#### Sprint 3.4: 工程项目组 (0.5 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P1 | ProjectTaskForce 模型 | Project | 4h |
| P1 | TaskForceMembership 模型 | ProjectTaskForce, User | 4h |
| P1 | 项目组权限隔离 | TaskForceMembership | 4h |
| P1 | 项目组管理 API | 所有模型 | 4h |

**交付物**: 项目组管理和权限隔离

---

### Phase 4: 前端核心页面 (预计 4-5 周)

> **目标**: 实现核心业务页面，提供可用的用户界面

#### Sprint 4.1: 布局与导航 (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | 主界面布局重构 | - | 8h |
| P0 | 层级导航树组件 | 项目层级 API | 16h |
| P0 | 上下文选择器组件 | 层级导航树 | 8h |
| P0 | 面包屑导航 | 上下文选择器 | 4h |
| P1 | 数据过滤联动 | 上下文选择器 | 4h |

**交付物**: 完整的导航和层级选择系统

#### Sprint 4.2: 仪表索引表 ★ (2 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | TanStack Table 集成 | - | 8h |
| P0 | 虚拟滚动实现 | TanStack Table | 8h |
| P0 | 列排序/过滤/分组 | TanStack Table | 8h |
| P0 | 行内编辑 | TanStack Table | 16h |
| P0 | 批量选择和操作 | TanStack Table | 8h |
| P1 | 列拖拽排序 | TanStack Table | 4h |
| P1 | 列宽调整和固定 | TanStack Table | 4h |
| P1 | 导出选中/全部数据 | TanStack Table | 8h |

**交付物**: 高性能仪表索引表 (核心页面)

#### Sprint 4.3: 规格书表单 (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | 动态表单生成器 | JSON Schema | 16h |
| P0 | 规格书表单组件 | 动态表单生成器 | 8h |
| P0 | 位号详情页面 | 规格书表单 | 8h |
| P1 | 表单验证 | 动态表单 | 4h |

**交付物**: 基于 JSON Schema 的动态规格书表单

#### Sprint 4.4: 其他管理页面 (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P1 | 工厂层级管理 UI | 层级导航树 | 8h |
| P1 | 回路管理页面 | TanStack Table | 8h |
| P1 | 仪表类型管理 UI | - | 8h |
| P2 | 用户管理 UI | RBAC | 8h |
| P2 | 命名规则管理 UI | NamingConvention | 8h |

**交付物**: 完整的管理页面集

---

### Phase 5: 版本控制系统 (预计 2 周)

> **目标**: 实现完整的版本历史和变更追踪

#### Sprint 5.1: 版本模型与 API (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | GlobalRevision 模型 | Project | 4h |
| P0 | EntityRevision 模型 | GlobalRevision | 8h |
| P0 | 版本对比 API | EntityRevision | 8h |
| P0 | 版本回滚 API | EntityRevision | 8h |
| P1 | 变更标记字段 | EntityRevision | 4h |

**交付物**: 完整的版本控制后端

#### Sprint 5.2: 版本控制 UI (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | 版本对比 UI | 版本对比 API | 16h |
| P1 | 变更高亮显示 | 版本对比 UI | 8h |
| P1 | 审计日志查询 UI | AuditLog | 8h |
| P2 | 变更通知 | - | 8h |

**交付物**: 版本对比和审计日志界面

---

### Phase 6: 规格书模块 (预计 3 周)

> **目标**: 实现完整的规格书管理和生成

#### Sprint 6.1: 工艺数据 (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | ProcessData 模型 | Tag | 8h |
| P0 | PipeSpecification 模型 | - | 4h |
| P0 | ProcessConnection 模型 | ProcessData | 4h |
| P0 | 工艺数据 API | 所有模型 | 8h |
| P1 | 工艺数据输入 UI | 工艺数据 API | 16h |

**交付物**: 工艺过程数据管理

#### Sprint 6.2: 规格书模板与生成 (2 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | SpecificationTemplate 模型 | InstrumentType | 8h |
| P0 | SpecificationDocument 模型 | SpecificationTemplate | 8h |
| P0 | 数据驱动文档生成 | SpecificationDocument | 16h |
| P0 | PDF 生成 (WeasyPrint) | 文档生成 | 16h |
| P1 | External Editor 导出 (.oisf) | SpecificationDocument | 8h |
| P1 | External Editor 导入 | - | 8h |

**交付物**: 完整的规格书生成和导出

---

### Phase 7: 规则引擎 (预计 2 周)

> **目标**: 实现业务规则验证和自动化

#### Sprint 7.1: 规则模型与引擎 (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | Rule 模型 | Project | 8h |
| P0 | RuleExecution 模型 | Rule | 4h |
| P0 | 规则引擎核心 | Rule | 16h |
| P0 | 实时校验集成 | 规则引擎 | 8h |

**交付物**: 规则引擎后端

#### Sprint 7.2: 规则管理 UI (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | 规则管理 API | Rule | 8h |
| P0 | 规则管理 UI | 规则管理 API | 16h |
| P1 | GB 标准规则库 | Rule | 8h |
| P1 | 规则测试功能 | 规则引擎 | 8h |

**交付物**: 规则管理界面和预设规则库

---

### Phase 8: 接线模块 (预计 4-5 周)

> **目标**: 实现完整的接线管理和电缆清单

#### Sprint 8.1: 接线设备模型 (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | JunctionBox 模型 | Area | 4h |
| P0 | TerminalStrip 模型 | JunctionBox | 4h |
| P0 | Terminal 模型 | TerminalStrip | 4h |
| P0 | RIOPanel 模型 | Plant | 4h |
| P0 | IOCard 模型 | RIOPanel | 4h |
| P0 | IOChannel 模型 | IOCard | 4h |
| P0 | Cable 模型 | - | 8h |
| P0 | CableRoute 模型 | Plant | 4h |

**交付物**: 完整的接线设备数据模型

#### Sprint 8.2: 接线连接模型 (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | WiringConnection 模型 | Terminal, Cable | 8h |
| P0 | WiringPath 模型 | WiringConnection | 8h |
| P0 | InstrumentWiringConfig 模型 | InstrumentType | 4h |
| P0 | TagWiring 模型 | Tag, InstrumentWiringConfig | 4h |
| P0 | 接线设备 API | 所有模型 | 16h |

**交付物**: 接线连接和路径模型

#### Sprint 8.3: I/O 通道分配 (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | IOChannelAssignment 模型 | IOChannel, Tag | 4h |
| P0 | I/O 通道分配 API | IOChannelAssignment | 8h |
| P0 | 信号类型匹配检查 | I/O 分配 API | 4h |
| P0 | 通道容量检查 | I/O 分配 API | 4h |
| P1 | I/O 分配 UI | I/O 分配 API | 16h |

**交付物**: I/O 通道分配功能

#### Sprint 8.4: 端子分配与电缆管理 (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | JunctionBoxTerminal 模型 | JunctionBox | 4h |
| P0 | 端子分配 API | JunctionBoxTerminal | 8h |
| P0 | Cable Schedule API | Cable | 8h |
| P0 | Cable Schedule 导出 (Excel/PDF) | Cable Schedule API | 8h |
| P1 | 端子分配 UI | 端子分配 API | 12h |

**交付物**: 端子分配和电缆清单

#### Sprint 8.5: 接线 UI (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | 接线路径视图 | WiringPath | 16h |
| P0 | RIO 盘柜管理页面 | RIOPanel, IOCard | 12h |
| P1 | 拖拽接线 UI | 接线路径视图 | 12h |

**交付物**: 接线管理界面

---

### Phase 9: 回路图生成 (预计 4 周)

> **目标**: 实现数据驱动的回路图自动生成

#### Sprint 9.1: 符号库 (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | SymbolLibrary 模型 | Project | 8h |
| P0 | 符号 SVG 模板 | SymbolLibrary | 16h |
| P0 | 宏定义 (数据填充位置) | SymbolLibrary | 8h |
| P1 | 符号编辑器 UI | SymbolLibrary | 8h |

**交付物**: 可定制的符号库

#### Sprint 9.2: 回路图模板 (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | LoopDrawingTemplate 模型 | Project | 8h |
| P0 | TitleBlockTemplate 模型 | Project | 4h |
| P0 | 布局规则定义 | LoopDrawingTemplate | 8h |
| P0 | 符号映射配置 | LoopDrawingTemplate | 8h |

**交付物**: 回路图模板系统

#### Sprint 9.3: 回路图生成引擎 (1.5 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | React Flow 集成 | - | 8h |
| P0 | 回路图生成引擎 | LoopDrawingTemplate, WiringPath | 24h |
| P0 | 宏自动填充 | 生成引擎 | 8h |
| P0 | 实时数据更新 | 生成引擎 | 8h |

**交付物**: 数据驱动的回路图生成

#### Sprint 9.4: 图纸导出 (0.5 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | DXF 导出 (ezdxf) | 生成引擎 | 16h |
| P1 | DWG 导出 (ODA Converter) | DXF 导出 | 8h |
| P1 | PDF 导出 | 生成引擎 | 8h |
| P1 | SVG 导出 | 生成引擎 | 4h |
| P2 | 批量导出 API | 所有导出 | 4h |

**交付物**: 多格式图纸导出

---

### Phase 10: 生产就绪 (预计 3-4 周)

> **目标**: 测试、优化、安全加固、部署

#### Sprint 10.1: 测试覆盖 (1.5 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | 后端单元测试 (pytest) | - | 24h |
| P0 | API 集成测试 | 单元测试 | 16h |
| P0 | 前端单元测试 (Vitest) | - | 16h |
| P1 | E2E 测试 (Playwright) | 所有 UI | 24h |

**交付物**: 完整的测试套件

#### Sprint 10.2: 国际化 (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | react-i18next 集成 | - | 8h |
| P0 | 英语翻译文件 (主语言) | - | 4h |
| P0 | 简体中文翻译文件 | - | 8h |
| P1 | 其他语言翻译文件 (10 种) | - | 20h |
| P1 | RTL 布局支持 | - | 8h |
| P1 | 语言切换 UI | - | 4h |

**交付物**: 12 种语言国际化支持

#### Sprint 10.3: 性能与安全 (1 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | 数据库索引优化 | - | 8h |
| P0 | API 响应缓存 | Redis | 8h |
| P0 | 安全审计 | - | 8h |
| P0 | HTTPS 配置 | - | 4h |
| P1 | 性能测试 | - | 8h |

**交付物**: 性能优化和安全加固

#### Sprint 10.4: 部署配置 (0.5 周)

| 优先级 | 任务 | 依赖 | 工作量 |
|--------|------|------|--------|
| P0 | 生产环境 Docker 配置 | - | 8h |
| P0 | CI/CD 流水线 (GitHub Actions) | - | 8h |
| P1 | 监控和日志 | - | 8h |
| P1 | 备份策略 | - | 4h |

**交付物**: 生产就绪的部署配置

---

## 四、时间线总览

| 阶段 | 内容 | 预计时间 | 累计 |
|------|------|----------|------|
| Phase 3 | 企业级基础 | 3-4 周 | 3-4 周 |
| Phase 4 | 前端核心页面 | 4-5 周 | 7-9 周 |
| Phase 5 | 版本控制系统 | 2 周 | 9-11 周 |
| Phase 6 | 规格书模块 | 3 周 | 12-14 周 |
| Phase 7 | 规则引擎 | 2 周 | 14-16 周 |
| Phase 8 | 接线模块 | 4-5 周 | 18-21 周 |
| Phase 9 | 回路图生成 | 4 周 | 22-25 周 |
| Phase 10 | 生产就绪 | 3-4 周 | 25-29 周 |

**总计**: 约 **6-7 个月** 完成全部功能

---

## 五、关键里程碑

| 里程碑 | 目标 | 预计完成 |
|--------|------|----------|
| M1 | 用户可登录，管理项目层级 | Phase 3 结束 |
| M2 | 仪表索引表可用 (核心功能) | Phase 4 结束 |
| M3 | 规格书可生成和导出 | Phase 6 结束 |
| M4 | 接线管理可用 | Phase 8 结束 |
| M5 | 回路图可自动生成 | Phase 9 结束 |
| M6 | 生产环境上线 | Phase 10 结束 |

---

## 六、风险与缓解措施

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| DWG 导出依赖 ODA Converter | 回路图导出 | 优先实现 DXF 导出，DWG 作为可选 |
| 大数据量性能 | 仪表索引表 | 虚拟滚动 + 分页 + 索引优化 |
| 复杂接线逻辑 | 接线模块 | 分阶段实现，先简单后复杂 |
| 国际化工作量 | 多语言支持 | 先实现英语和中文，其他语言后续补充 |

---

*本文档将随开发进度持续更新。*
