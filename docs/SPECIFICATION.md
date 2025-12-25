# OpenInstrument - 软件规格说明书

> **版本**: 0.3.0  
> **最后更新**: 2025-12-25  
> **对标产品**: Hexagon SmartPlant Instrumentation (SPI)

---

## 1. 项目概述

### 1.1 项目目标

构建一个**企业级、Web 端、数据驱动**的过程仪表工程设计系统，完整复刻 SmartPlant Instrumentation (SPI) 的核心功能架构。

### 1.2 SPI 功能模块对标

本系统严格遵循 SPI 的功能模块设计，从系统管理到施工图生成，构成完整的仪表工程工作流：

| 模块编号 | SPI 模块名称 | OpenInstrument 对应模块 |
|----------|--------------|-------------------------|
| 1.1 | Administration (管理模块) | `administration` + `tenants` |
| 1.2 | Instrument Index (仪表索引) | `core_engineering` |
| 1.3 | Engineering Data Editor (EDE) | 前端数据网格 |
| 1.4 | Specifications (规格书) | `specifications` |
| 1.5 | Wiring (接线模块) | `wiring` |
| 1.6 | Loop Drawings (回路图) | `loop_drawings` |
| 1.7 | Rule Manager (规则管理器) | `rules_engine` |
| 1.8 | Version Control (版本控制) | `revisions` + `audit` |

### 1.3 核心价值

- **数据完整性**: 工程软件的第一性原则，所有数据必须经过严格验证
- **多租户支持**: 支持多客户、多项目的数据隔离
- **并发协作**: 支持多用户并行访问和编辑，乐观锁防冲突
- **可追溯性**: 完整的审计日志、版本历史和变更对比
- **规则驱动**: 业务规则引擎，实时校验工程规范
- **文档自动化**: 规格书、回路图基于数据自动生成
- **可扩展性**: 模块化设计，支持功能扩展

---

## 2. 技术架构

### 2.1 技术栈

| 层级 | 技术选型 | 版本要求 |
|------|----------|----------|
| **后端框架** | Django + Django REST Framework | Django 5.0+, DRF 3.14+ |
| **多租户** | django-tenants | 3.6+ |
| **数据库** | PostgreSQL (Schema隔离) | 16+ |
| **缓存** | Redis | 7+ |
| **前端框架** | React + TypeScript | React 18+, TypeScript 5+ |
| **构建工具** | Vite | 5+ |
| **UI 组件** | Shadcn UI + Tailwind CSS | Tailwind 4+ |
| **状态管理** | TanStack Query | 5+ |
| **表格组件** | TanStack Table | 8+ |
| **图形绘制** | React Flow | 11+ |
| **依赖管理** | uv (Python), npm (Node.js) | - |
| **容器化** | Docker Compose | - |

### 2.2 项目结构

```
OpenInstrument/
├── backend/                    # Django 后端
│   ├── config/                # Django 配置
│   │   ├── settings.py        # 主配置文件 (含多租户配置)
│   │   ├── urls.py            # URL 路由
│   │   └── ...
│   ├── apps/                  # Django 应用 (按 SPI 模块组织)
│   │   ├── core/              # 核心功能 (健康检查等)
│   │   ├── tenants/           # [1.1] 多租户管理 (ProjectTenant)
│   │   ├── administration/    # [1.1] 用户/角色/组织管理
│   │   ├── core_engineering/  # [1.2] 仪表索引核心模型 (租户数据)
│   │   ├── specifications/    # [1.4] 规格书管理
│   │   ├── wiring/            # [1.5] 接线模块
│   │   ├── loop_drawings/     # [1.6] 回路图生成
│   │   ├── rules_engine/      # [1.7] 规则管理器
│   │   ├── revisions/         # [1.8] 版本控制
│   │   └── audit/             # [1.8] 审计日志
│   ├── manage.py
│   └── pyproject.toml
├── frontend/                  # React 前端
│   ├── src/
│   │   ├── components/        # UI 组件
│   │   │   ├── layout/        # 布局组件
│   │   │   ├── ui/            # Shadcn UI 基础组件
│   │   │   ├── data-grid/     # [1.3] EDE 数据网格组件
│   │   │   ├── spec-form/     # [1.4] 动态规格书表单
│   │   │   ├── wiring/        # [1.5] 接线拖拽组件
│   │   │   └── loop-diagram/  # [1.6] 回路图组件
│   │   ├── pages/             # 页面组件
│   │   ├── lib/               # 工具库
│   │   ├── hooks/             # 自定义 Hooks
│   │   ├── stores/            # 状态管理 (Zustand)
│   │   └── types/             # TypeScript 类型
│   └── package.json
├── docs/                      # 文档
│   ├── PRD.md                 # 产品需求文档
│   ├── SPECIFICATION.md       # 本文件
│   └── IMPLEMENTATION.md      # 实现状态
├── docker-compose.yml         # Docker 配置
└── README.md                  # 项目说明
```

### 2.3 多租户架构 (Multi-Tenancy)

系统采用 **PostgreSQL Schema 隔离** 实现多租户架构，每个工程项目拥有独立的数据库 Schema。

#### 2.3.1 架构概述
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PostgreSQL 数据库                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    公共 Schema (public)                              │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │Organization │ │    User     │ │    Role     │ │ProjectTenant│   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │ProjectDomain│ │Membership   │ │ TaskForce   │ │  AuditLog   │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ │
│  │ 租户 Schema          │  │ 租户 Schema          │  │ 租户 Schema          │ │
│  │ (project_prj001)    │  │ (project_prj002)    │  │ (project_prj003)    │ │
│  │ ┌───────┐ ┌───────┐ │  │ ┌───────┐ ┌───────┐ │  │ ┌───────┐ ┌───────┐ │ │
│  │ │Client │ │ Site  │ │  │ │Client │ │ Site  │ │  │ │Client │ │ Site  │ │ │
│  │ ├───────┤ ├───────┤ │  │ ├───────┤ ├───────┤ │  │ ├───────┤ ├───────┤ │ │
│  │ │ Plant │ │Hierchy│ │  │ │ Plant │ │Hierchy│ │  │ │ Plant │ │Hierchy│ │ │
│  │ ├───────┤ ├───────┤ │  │ ├───────┤ ├───────┤ │  │ ├───────┤ ├───────┤ │ │
│  │ │ Loop  │ │  Tag  │ │  │ │ Loop  │ │  Tag  │ │  │ │ Loop  │ │  Tag  │ │ │
│  │ ├───────┤ ├───────┤ │  │ ├───────┤ ├───────┤ │  │ ├───────┤ ├───────┤ │ │
│  │ │InstTyp│ │Naming │ │  │ │InstTyp│ │Naming │ │  │ │InstTyp│ │Naming │ │ │
│  │ └───────┘ └───────┘ │  │ └───────┘ └───────┘ │  │ └───────┘ └───────┘ │ │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 2.3.2 数据分类

| 分类 | Schema | 模型 | 说明 |
|------|--------|------|------|
| **共享数据** | public | Organization, User, Role | 跨项目共享 |
| **租户元数据** | public | ProjectTenant, ProjectDomain | 租户配置 |
| **成员关系** | public | ProjectMembership, TaskForce | 用户-项目关联 |
| **审计日志** | public | AuditLog | 全局审计 |
| **项目数据** | project_xxx | Client, Site, Plant | 项目层级 |
| **工程数据** | project_xxx | PlantHierarchy, Loop, Tag | 仪表数据 |
| **配置数据** | project_xxx | InstrumentType, NamingConvention | 项目配置 |

#### 2.3.3 租户切换机制
```
前端请求流程:
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. 用户选择项目 → 前端存储 project_id 到 localStorage                        │
│ 2. API 请求自动添加 Header: X-Project-ID: {project_id}                       │
│ 3. 后端中间件读取 Header，切换到对应 Schema                                   │
│ 4. ORM 查询自动在租户 Schema 中执行                                          │
│ 5. 响应返回当前租户的数据                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 2.3.4 API 端点
```
# 租户管理 API
GET    /api/tenants/projects/              # 项目列表
POST   /api/tenants/projects/              # 创建项目 (自动创建 Schema)
GET    /api/tenants/projects/{id}/         # 项目详情
PUT    /api/tenants/projects/{id}/         # 更新项目
DELETE /api/tenants/projects/{id}/         # 删除项目 (删除 Schema)
POST   /api/tenants/projects/{id}/switch/  # 切换到此项目
GET    /api/tenants/projects/current/      # 当前项目上下文
```

---

## 3. SPI 功能模块详细规格

### 3.1 模块 1.1 - 管理模块 (Administration)

> **SPI 对应**: Administration Module  
> **Django App**: `administration`, `tenants`

#### 3.1.0 基于角色的用户管理系统 (RBAC)

##### 3.1.0.1 角色层级定义
```
系统采用分层角色模型，从低到高依次为:

┌─────────────────────────────────────────────────────────────────────────────┐
│                           角色层级金字塔                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                          ┌─────────────┐                                    │
│                          │Administrator│  ← 系统最高权限                     │
│                          │  (Level 5)  │                                    │
│                          └──────┬──────┘                                    │
│                                 │                                           │
│                    ┌────────────┴────────────┐                              │
│                    │    Project Engineer     │  ← 项目全专业权限             │
│                    │       (Level 4)         │                              │
│                    └────────────┬────────────┘                              │
│                                 │                                           │
│     ┌───────────────────────────┼───────────────────────────┐               │
│     │                           │                           │               │
│ ┌───┴────────────┐  ┌──────────┴──────────┐  ┌─────────────┴───┐           │
│ │ Instrumentation│  │  Process Engineer   │  │   Mechanical    │           │
│ │    Engineer    │  │     (Level 3)       │  │    Engineer     │           │
│ │   (Level 3)    │  │                     │  │   (Level 3)     │           │
│ └───────┬────────┘  └──────────┬──────────┘  └────────┬────────┘           │
│         │                      │                      │                     │
│         └──────────────────────┼──────────────────────┘                     │
│                                │                                            │
│                       ┌────────┴────────┐                                   │
│                       │      Guest      │  ← 只读权限                        │
│                       │    (Level 1)    │                                   │
│                       └─────────────────┘                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

角色定义:
  Level 5 - Administrator (系统管理员):
    - 系统最高权限
    - 管理所有用户账户 (创建/编辑/删除/激活/停用)
    - 管理所有角色和权限
    - 创建和管理所有工程项目组 (Project Task Force)
    - 将任何用户加入/移除任何工程项目组
    - 系统配置和维护
    - 查看所有审计日志
    - 数据库备份和恢复

  Level 4 - Project Engineer (项目工程师):
    - 项目级最高权限
    - 对所有专业数据有完全控制权限 (CRUD)
    - 基于工程项目号创建工程项目组
    - 将用户加入/移除自己创建的工程项目组
    - 审批工程变更
    - 发布规格书和图纸
    - 管理项目层级结构

  Level 3 - Instrumentation Engineer (仪表工程师):
    - 仪表专业数据完全控制权限 (CRUD)
    - 数据范围: Tag, Loop, Specification, Wiring, LoopDrawing, Cable
    - 对其他专业数据只读

  Level 3 - Process Engineer (工艺工程师):
    - 工艺专业数据完全控制权限 (CRUD)
    - 数据范围: ProcessData (工艺过程数据)
    - 对其他专业数据只读

  Level 3 - Mechanical Engineer (机械工程师):
    - 机械/管道专业数据完全控制权限 (CRUD)
    - 数据范围: PipeSpecification, ProcessConnection
    - 对其他专业数据只读

  Level 1 - Guest (访客):
    - 所有数据只读权限
    - 不能创建、编辑或删除任何数据
    - 可以查看和导出数据
    - 可以查看规格书和图纸
```

##### 3.1.0.2 Role (角色模型)
```
目的: 定义系统角色

字段:
  - id: UUID
  - name: 角色名称 (唯一)
    - ADMINISTRATOR
    - PROJECT_ENGINEER
    - INSTRUMENTATION_ENGINEER
    - PROCESS_ENGINEER
    - MECHANICAL_ENGINEER
    - GUEST
  - display_name: 显示名称
  - level: 角色等级 (1-5)
  - description: 角色描述
  - permissions: JSONField (权限配置)
    {
      "data_scopes": ["instrumentation", "process", "mechanical", "all"],
      "actions": ["view", "create", "edit", "delete", "approve", "publish"],
      "system_admin": false,
      "project_admin": false
    }
  - is_system_role: 是否系统预设角色 (不可删除)
  - created_at, updated_at: 时间戳

预设角色:
  - Administrator: level=5, system_admin=true, data_scopes=["all"]
  - Project Engineer: level=4, project_admin=true, data_scopes=["all"]
  - Instrumentation Engineer: level=3, data_scopes=["instrumentation"]
  - Process Engineer: level=3, data_scopes=["process"]
  - Mechanical Engineer: level=3, data_scopes=["mechanical"]
  - Guest: level=1, actions=["view"]
```

##### 3.1.0.3 User (用户模型扩展)
```
目的: 扩展 Django User 模型

字段:
  - id: UUID
  - username: 用户名 (唯一)
  - email: 邮箱 (唯一)
  - first_name: 名
  - last_name: 姓
  - role: FK -> Role (系统角色)
  - department: 部门
  - employee_id: 工号
  - phone: 电话
  - avatar: 头像
  - is_active: 是否激活
  - last_login: 最后登录时间
  - created_at, updated_at: 时间戳

约束:
  - 每个用户必须有一个系统角色
  - 用户可以属于多个工程项目组
```

##### 3.1.0.4 数据权限矩阵
```
┌─────────────────────────┬───────┬───────┬───────┬───────┬───────┬───────┐
│ 数据类型                 │ Admin │ Proj  │ Instr │ Proc  │ Mech  │ Guest │
│                         │       │ Engr  │ Engr  │ Engr  │ Engr  │       │
├─────────────────────────┼───────┼───────┼───────┼───────┼───────┼───────┤
│ 用户管理                 │ CRUD  │ -     │ -     │ -     │ -     │ -     │
│ 角色管理                 │ CRUD  │ -     │ -     │ -     │ -     │ -     │
│ 项目组管理               │ CRUD  │ CR*   │ -     │ -     │ -     │ -     │
├─────────────────────────┼───────┼───────┼───────┼───────┼───────┼───────┤
│ Project (工程项目)       │ CRUD  │ RU    │ R     │ R     │ R     │ R     │
│ Plant Hierarchy         │ CRUD  │ CRUD  │ R     │ R     │ R     │ R     │
├─────────────────────────┼───────┼───────┼───────┼───────┼───────┼───────┤
│ Tag (仪表位号)           │ CRUD  │ CRUD  │ CRUD  │ R     │ R     │ R     │
│ Loop (控制回路)          │ CRUD  │ CRUD  │ CRUD  │ R     │ R     │ R     │
│ Specification (规格书)   │ CRUD  │ CRUD  │ CRUD  │ R     │ R     │ R     │
│ Wiring (接线)            │ CRUD  │ CRUD  │ CRUD  │ R     │ R     │ R     │
│ LoopDrawing (回路图)     │ CRUD  │ CRUD  │ CRUD  │ R     │ R     │ R     │
│ Cable (电缆)             │ CRUD  │ CRUD  │ CRUD  │ R     │ R     │ R     │
├─────────────────────────┼───────┼───────┼───────┼───────┼───────┼───────┤
│ ProcessData (工艺数据)   │ CRUD  │ CRUD  │ R     │ CRUD  │ R     │ R     │
├─────────────────────────┼───────┼───────┼───────┼───────┼───────┼───────┤
│ PipeSpecification       │ CRUD  │ CRUD  │ R     │ R     │ CRUD  │ R     │
│ ProcessConnection       │ CRUD  │ CRUD  │ R     │ R     │ CRUD  │ R     │
├─────────────────────────┼───────┼───────┼───────┼───────┼───────┼───────┤
│ 审计日志                 │ R     │ R     │ R     │ R     │ R     │ -     │
│ 系统配置                 │ CRUD  │ -     │ -     │ -     │ -     │ -     │
└─────────────────────────┴───────┴───────┴───────┴───────┴───────┴───────┘

图例: C=Create, R=Read, U=Update, D=Delete, -=无权限
      CR* = Project Engineer 只能创建自己的项目组
```

#### 3.1.0.5 工程项目组 (Project Task Force)

##### ProjectTaskForce (工程项目组模型)
```
目的: 管理工程项目组，实现项目间数据隔离

字段:
  - id: UUID
  - name: 项目组名称 (如 "乙烯项目组")
  - code: 项目组代码 (唯一)
  - project: FK -> Project (关联的工程项目)
  - description: 描述
  - created_by: FK -> User (创建者)
  - created_by_role: 创建者角色 (Administrator/Project Engineer)
  - is_active: 是否激活
  - created_at, updated_at: 时间戳

约束:
  - 每个 Project 只能关联一个 ProjectTaskForce
  - project 字段唯一 (一对一关系)
  - 项目组代码全局唯一
```

##### TaskForceMembership (项目组成员关系)
```
目的: 记录用户与项目组的关系

字段:
  - id: UUID
  - task_force: FK -> ProjectTaskForce
  - user: FK -> User
  - role_in_project: 用户在该项目中的角色 (可覆盖系统角色)
  - joined_at: 加入时间
  - added_by: FK -> User (添加者)
  - is_active: 是否激活
  - created_at, updated_at: 时间戳

约束:
  - (task_force, user) 唯一
  - 用户可以属于多个项目组
```

##### 项目组创建规则
```
1. Administrator 创建项目组:
   方式一: 先创建项目组，再分配工程项目号
     - 创建空项目组 (name, code)
     - 后续分配 Project (project_no)
   
   方式二: 基于工程项目号创建项目组
     - 选择已存在的 Project
     - 自动创建项目组 (name 默认为项目名称)
     - project 和 task_force 自动关联

   权限:
     - 可以将任何用户加入/移除任何项目组
     - 可以编辑/删除任何项目组

2. Project Engineer 创建项目组:
   方式: 只能基于工程项目号创建项目组
     - 必须选择已存在的 Project
     - 自动创建项目组
     - created_by_role = "PROJECT_ENGINEER"

   权限:
     - 只能将用户加入/移除自己创建的项目组
     - 不能编辑/删除 Administrator 创建的项目组
     - 不能修改项目组的 project 关联

3. 其他角色:
   - 不能创建项目组
   - 不能管理项目组成员
```

##### 项目组权限隔离
```
核心原则: 不同工程项目组之间项目组权限独立，不可互访

实现机制:
  1. 数据隔离:
     - 所有数据查询自动过滤 project_id
     - 用户只能看到自己所属项目组的数据
     - API 层强制检查项目组成员关系

  2. 权限检查流程:
     ┌─────────────────────────────────────────────────────────────────┐
     │                        API 请求                                 │
     └───────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
     ┌─────────────────────────────────────────────────────────────────┐
     │ 1. 身份验证 (JWT Token)                                         │
     └───────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
     ┌─────────────────────────────────────────────────────────────────┐
     │ 2. 获取用户所属项目组列表                                        │
     │    SELECT task_force_id FROM task_force_membership              │
     │    WHERE user_id = ? AND is_active = true                       │
     └───────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
     ┌─────────────────────────────────────────────────────────────────┐
     │ 3. 检查请求的 project_id 是否在用户的项目组中                    │
     │    IF project_id NOT IN user_task_forces:                       │
     │        RETURN 403 Forbidden                                     │
     └───────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
     ┌─────────────────────────────────────────────────────────────────┐
     │ 4. 检查用户角色权限 (RBAC)                                       │
     │    - 检查数据范围 (data_scope)                                   │
     │    - 检查操作权限 (action)                                       │
     └───────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
     ┌─────────────────────────────────────────────────────────────────┐
     │ 5. 执行请求                                                      │
     └─────────────────────────────────────────────────────────────────┘

  3. 特殊情况:
     - Administrator 可以访问所有项目组的数据
     - 用户切换项目时，前端自动切换 project context
```

##### 项目组管理 UI
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Project Task Force Management                              [+ Create] [⚙️]  │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─ Task Force List ─────────────────────────────────────────────────────────┐
│ │ ┌─────────┬────────────────────┬────────────────┬──────────┬───────────┐ │
│ │ │ Code    │ Name               │ Project No.    │ Members  │ Created By│ │
│ │ ├─────────┼────────────────────┼────────────────┼──────────┼───────────┤ │
│ │ │ TF-001  │ 乙烯项目组          │ PRJ-2025-001   │ 12       │ Admin     │ │
│ │ │ TF-002  │ 芳烃项目组          │ PRJ-2025-002   │ 8        │ John (PE) │ │
│ │ │ TF-003  │ 公用工程项目组      │ PRJ-2025-003   │ 5        │ Admin     │ │
│ │ └─────────┴────────────────────┴────────────────┴──────────┴───────────┘ │
│ └───────────────────────────────────────────────────────────────────────────┘
│                                                                             │
│ ┌─ Selected: TF-001 乙烯项目组 ─────────────────────────────────────────────┐
│ │ Project: PRJ-2025-001 - 100万吨乙烯项目                                   │
│ │ Created: 2025-01-15 by Administrator                                      │
│ │                                                                           │
│ │ Members (12):                                                [+ Add User] │
│ │ ┌──────────────┬─────────────────────────┬────────────┬─────────────────┐ │
│ │ │ Name         │ Role                    │ Joined     │ Actions         │ │
│ │ ├──────────────┼─────────────────────────┼────────────┼─────────────────┤ │
│ │ │ John Smith   │ Project Engineer        │ 2025-01-15 │ [Remove]        │ │
│ │ │ Jane Doe     │ Instrumentation Engineer│ 2025-01-16 │ [Remove]        │ │
│ │ │ Bob Wilson   │ Process Engineer        │ 2025-01-16 │ [Remove]        │ │
│ │ │ Alice Chen   │ Mechanical Engineer     │ 2025-01-17 │ [Remove]        │ │
│ │ │ Guest User   │ Guest                   │ 2025-01-20 │ [Remove]        │ │
│ │ └──────────────┴─────────────────────────┴────────────┴─────────────────┘ │
│ └───────────────────────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────────────────┘

Create Task Force Dialog (Administrator):
┌─────────────────────────────────────────────────────────────────────────────┐
│ Create Project Task Force                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ Creation Method:                                                            │
│   (•) Create from existing project                                          │
│   ( ) Create empty task force first                                         │
│                                                                             │
│ Project: [PRJ-2025-001 - 100万吨乙烯项目 ▼]                                  │
│                                                                             │
│ Task Force Code: [TF-001        ]  (auto-generated)                         │
│ Task Force Name: [乙烯项目组     ]  (default: project name)                  │
│ Description:     [                                                        ] │
│                                                                             │
│                                              [Cancel]  [Create Task Force]  │
└─────────────────────────────────────────────────────────────────────────────┘

Create Task Force Dialog (Project Engineer):
┌─────────────────────────────────────────────────────────────────────────────┐
│ Create Project Task Force                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ Select Project: [PRJ-2025-001 - 100万吨乙烯项目 ▼]                           │
│                                                                             │
│ Task Force Code: [TF-001        ]  (auto-generated)                         │
│ Task Force Name: [乙烯项目组     ]  (default: project name)                  │
│ Description:     [                                                        ] │
│                                                                             │
│ Note: Task force will be automatically linked to the selected project.      │
│                                                                             │
│                                              [Cancel]  [Create Task Force]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

##### API 端点
```
# 角色管理 (Administrator only)
GET    /api/roles/                           # 角色列表
POST   /api/roles/                           # 创建角色
GET    /api/roles/{id}/                      # 角色详情
PUT    /api/roles/{id}/                      # 更新角色
DELETE /api/roles/{id}/                      # 删除角色

# 用户管理 (Administrator only)
GET    /api/users/                           # 用户列表
POST   /api/users/                           # 创建用户
GET    /api/users/{id}/                      # 用户详情
PUT    /api/users/{id}/                      # 更新用户
DELETE /api/users/{id}/                      # 删除用户
POST   /api/users/{id}/activate/             # 激活用户
POST   /api/users/{id}/deactivate/           # 停用用户
POST   /api/users/{id}/reset-password/       # 重置密码

# 项目组管理
GET    /api/task-forces/                     # 项目组列表
POST   /api/task-forces/                     # 创建项目组
GET    /api/task-forces/{id}/                # 项目组详情
PUT    /api/task-forces/{id}/                # 更新项目组
DELETE /api/task-forces/{id}/                # 删除项目组
POST   /api/task-forces/{id}/assign-project/ # 分配工程项目 (Admin only)

# 项目组成员管理
GET    /api/task-forces/{id}/members/        # 成员列表
POST   /api/task-forces/{id}/members/        # 添加成员
DELETE /api/task-forces/{id}/members/{user_id}/ # 移除成员

# 当前用户
GET    /api/me/                              # 当前用户信息
GET    /api/me/task-forces/                  # 我的项目组列表
PUT    /api/me/preferences/                  # 更新偏好设置
```

#### 3.1.1 ProjectTenant (工程项目/租户 - 顶层对象)
```
目的: 工程项目是系统的顶层入口，同时作为多租户的租户单位
模型: apps.tenants.models.ProjectTenant (继承 TenantMixin)
Schema: public (共享)

字段:
  - id: Integer (主键)
  - project_no: 项目编号 (唯一标识，如 "PRJ-2025-001", "ETH-100")
  - name: 项目名称 (如 "100万吨乙烯项目")
  - schema_name: Schema 名称 (自动生成，如 "project_prj2025001")
  - organization_id: Integer (关联组织)
  - description: 项目描述
  - status: 项目状态 (Active/OnHold/Completed/Archived)
  - start_date: 项目开始日期
  - end_date: 项目结束日期 (可选)
  - hierarchy_config: JSONField (层级结构配置)
  - created_at, updated_at: 时间戳

约束:
  - project_no 全局唯一
  - schema_name 全局唯一 (自动从 project_no 生成)

说明:
  - 创建项目时自动创建独立的 PostgreSQL Schema
  - 项目数据 (Client, Site, Plant, Tag 等) 存储在项目 Schema 中
  - 用户通过 X-Project-ID Header 切换项目上下文
  - 删除项目时自动删除对应 Schema
```

#### 3.1.2 Client (客户/业主 - 租户数据)
```
目的: 记录工程项目的客户/业主信息
模型: apps.core_engineering.models.Client
Schema: project_xxx (租户)

字段:
  - id: Integer (主键)
  - name: 客户名称 (如 "中石化", "巴斯夫")
  - code: 客户代码 (如 "SINOPEC", "BASF") - 租户内唯一
  - contact_person: 联系人
  - contact_email: 联系邮箱
  - contact_phone: 联系电话
  - address: 地址
  - created_at, updated_at: 时间戳

约束:
  - code 在租户 Schema 内唯一
  - 无需 project FK (隐式属于当前租户)

说明:
  - Client 存储在项目的独立 Schema 中
  - 不同项目的 Client 数据完全隔离
  - 客户信息用于文档生成、报表抬头等
```

#### 3.1.3 Site (厂区/地点 - 租户数据)
```
目的: 支持客户在不同地理位置的多个厂区
模型: apps.core_engineering.models.Site
Schema: project_xxx (租户)

字段:
  - id: Integer (主键)
  - client: FK -> Client
  - name: 厂区名称 (如 "镇海炼化", "上海基地")
  - code: 厂区代码 (如 "ZH", "SH")
  - location: 地理位置/地址
  - address: 地址
  - timezone: 时区 (默认 "UTC")
  - created_at, updated_at: 时间戳

约束:
  - (client, code) 唯一

说明:
  - Site 存储在项目的独立 Schema 中
  - 一个 Client 可以有一个或多个 Site
  - 典型场景：同一客户在不同城市/国家的工厂
```

#### 3.1.4 Plant (工厂/装置 - 租户数据)
```
目的: 定义具体的工厂或生产装置，对应 P&ID 的范围
模型: apps.core_engineering.models.Plant
Schema: project_xxx (租户)

字段:
  - id: Integer (主键)
  - site: FK -> Site
  - name: 工厂/装置名称 (如 "乙烯装置", "芳烃联合装置")
  - code: 工厂代码 (如 "ETH", "ARO")
  - description: 描述
  - capacity: 产能 (如 "1000 KTPA")
  - is_active: 是否激活
  - created_at, updated_at: 时间戳

约束:
  - (site, code) 唯一

说明:
  - Plant 存储在项目的独立 Schema 中
  - Plant 对应一套完整的生产工艺
  - 一个 Site 可以有多个 Plant
```

#### 3.1.5 PlantHierarchy (工厂层级 - 租户数据)
```
目的: 定义工厂内部的层级结构 (Plant → Area → Unit)
模型: apps.core_engineering.models.PlantHierarchy (MPTT)
Schema: project_xxx (租户)

字段:
  - id: Integer (主键)
  - plant: FK -> Plant
  - parent: FK -> self (自引用，MPTT)
  - name: 名称 (如 "反应区", "分离区", "Unit-100")
  - code: 代码 (如 "REACT", "SEP", "U100")
  - node_type: 节点类型 (PLANT/AREA/UNIT)
  - description: 描述
  - lft, rght, tree_id, level: MPTT 字段
  - created_at, updated_at: 时间戳

约束:
  - (parent, code) 唯一

说明:
  - 使用 MPTT 实现高效的树形查询
  - PLANT: 工厂根节点
  - AREA: 工艺区域 (如反应区、分离区)
  - UNIT: 工艺单元 (仪表 Tag 归属于 Unit)
```

#### 数据层级架构图 (多租户)
```
公共 Schema (public):
├── ProjectTenant (工程项目/租户)
│   ├── project_no: "PRJ-2025-001"
│   └── schema_name: "project_prj2025001"
└── ProjectMembership (用户-项目关联)

租户 Schema (project_prj2025001):
└── Client (客户/业主)
    └── Site(s) (厂区)
        └── Plant(s) (工厂/装置)
            └── PlantHierarchy (MPTT)
                ├── Area(s) (工艺区域)
                └── Unit(s) (工艺单元)
                    └── Tags, Loops, Wiring, P&IDs...

完整示例:
PRJ-2025-001 (100万吨乙烯项目)
└── 中石化 (Client)
    ├── 镇海炼化 (Site)
    │   ├── 乙烯装置 (Plant)
    │   │   ├── 裂解区 (Area)
    │   │   │   ├── Unit-100 (裂解炉)
    │   │   │   │   └── FT-101, TT-102, PT-103...
    │   │   │   └── Unit-110 (急冷)
    │   │   └── 分离区 (Area)
    │   │       ├── Unit-200 (压缩)
    │   │       └── Unit-210 (精馏)
    │   └── 公用工程 (Plant)
    │       └── 循环水 (Area)
    │           └── Unit-900
    └── 茂名石化 (Site) [可选，多厂区项目]
        └── ...

简单项目示例 (单厂区):
PRJ-2025-002 (小型改造项目)
└── 某化工厂 (Client)
    └── 主厂区 (Site - 默认)
        └── 反应装置 (Plant)
            └── Unit-100
                └── Tags...
```

#### 3.1.6 层级结构配置
```
目的: 允许用户在创建项目时配置层级结构

hierarchy_config 示例:
{
  "template": "standard",  // 使用的模板: standard/simple/custom
  "levels": [
    { "name": "Client", "required": true, "default_name": "客户" },
    { "name": "Site", "required": true, "default_name": "主厂区", "allow_multiple": true },
    { "name": "Plant", "required": true, "default_name": "主装置", "allow_multiple": true },
    { "name": "Area", "required": false, "allow_multiple": true },
    { "name": "Unit", "required": true, "allow_multiple": true }
  ],
  "auto_create_defaults": true  // 是否自动创建默认层级
}

预设模板:
  - standard: 完整层级 (Client → Site → Plant → Area → Unit)
  - simple: 简化层级 (Client → Site → Unit)，适合小型项目
  - custom: 用户自定义

创建项目流程:
  1. 输入项目基本信息 (Project No., 名称, 描述)
  2. 选择层级模板或自定义配置
  3. 系统自动创建默认层级结构
  4. 用户可随后编辑和调整层级
```

#### 3.1.6.1 仪表自控对象组织架构

##### 对象归属层级总览
```
Project (工程项目)
│
├── 【项目级共享对象】
│   ├── InstrumentTypeLibrary (仪表类型库)
│   ├── SymbolLibrary (符号库)
│   ├── NamingConvention (命名规则)
│   ├── SpecificationTemplate (规格书模板)
│   ├── LoopDrawingTemplate (回路图模板)
│   └── CableScheduleTemplate (电缆表模板)
│
└── Client → Site → Plant
                      │
                      ├── 【Plant 级别对象】
                      │   ├── PID (P&ID 图纸列表)
                      │   ├── ControlSystem (控制系统: DCS/PLC/SIS)
                      │   ├── CableRoute (电缆路由/桥架)
                      │   └── PlantSettings (装置级配置)
                      │
                      ├── 【Area 级别对象】
                      │   ├── JunctionBox (接线箱)
                      │   ├── ControlRoom (控制室)
                      │   └── Cabinet (控制柜/MCC)
                      │
                      └── 【Unit 级别对象 - 核心】
                          ├── Tag (仪表位号) ★核心对象
                          │   └── Specification (规格书)
                          │   └── WiringConnection (接线连接)
                          ├── Loop (控制回路)
                          │   └── LoopDrawing (回路图)
                          ├── TerminalStrip (端子排)
                          │   └── Terminal (端子)
                          └── Cable (电缆) [跨层级引用]
```

##### 各层级对象详细说明
```
| 对象 | 归属层级 | 外键 | 说明 |
|------|----------|------|------|
| InstrumentType | Project | project | 仪表类型库，项目级共享 |
| SymbolLibrary | Project | project | 符号库，项目级共享 |
| NamingConvention | Project | project | 命名规则，项目级共享 |
| SpecificationTemplate | Project | project | 规格书模板 |
| LoopDrawingTemplate | Project | project | 回路图模板 |
| PID | Plant | plant | P&ID 图纸，覆盖整个装置 |
| ControlSystem | Plant | plant | 控制系统 (DCS/PLC/SIS) |
| CableRoute | Plant | plant | 电缆桥架/穿线管 |
| JunctionBox | Area | area (PlantHierarchy) | 接线箱，服务于区域内多个 Unit |
| ControlRoom | Area | area (PlantHierarchy) | 控制室 |
| Cabinet | Area | area (PlantHierarchy) | 控制柜/MCC |
| Tag | Unit | unit (PlantHierarchy) | 仪表位号 ★核心 |
| Loop | Unit | unit (PlantHierarchy) | 控制回路 |
| Specification | Tag | tag | 规格书，每个位号一份 |
| TerminalStrip | JunctionBox/Cabinet | junction_box/cabinet | 端子排 |
| Terminal | TerminalStrip | terminal_strip | 端子 |
| Cable | Project | project (跨层级) | 电缆，连接不同位置 |
| WiringConnection | Tag | tag | 接线连接，属于具体仪表 |
| LoopDrawing | Loop | loop | 回路图，属于具体回路 |
```

##### 对象关系图
```
                    ┌─────────────────────────────────────────────────────┐
                    │                    Project                          │
                    │  (InstrumentType, Templates, NamingConvention)      │
                    └─────────────────────────────────────────────────────┘
                                            │
                    ┌─────────────────────────────────────────────────────┐
                    │              Plant (P&ID, ControlSystem, CableRoute)│
                    └─────────────────────────────────────────────────────┘
                                            │
        ┌───────────────────────────────────┼───────────────────────────────────┐
        │                                   │                                   │
   ┌────▼────┐                        ┌─────▼─────┐                       ┌─────▼─────┐
   │  Area   │                        │   Area    │                       │   Area    │
   │ (现场)  │                        │ (现场RIO) │                       │ (控制室)  │
   │ JB-01   │                        │ RIO-01    │                       │ Cabinet   │
   └────┬────┘                        └─────┬─────┘                       └─────┬─────┘
        │                                   │                                   │
   ┌────▼────┐                        ┌─────▼─────┐                       ┌─────▼─────┐
   │ Unit-100│                        │ RIO Panel │                       │   DCS     │
   │         │                        │  I/O Card │                       │ Controller│
   │ FT-101 ─┼────── Cable ───────────┼─ AI-001   │─── Fieldbus/Cable ────┼─ CPU-01   │
   │ TT-102  │      IC-FT-101-01      │ TS-RIO-01 │                       │           │
   │         │                        │           │                       │           │
   │ Loop    │                        │           │                       │           │
   │ FC-101  │                        │           │                       │           │
   └─────────┘                        └───────────┘                       └───────────┘
```

##### 信号路径类型
```
支持多种信号路径配置，适应不同工程场景:

路径类型 1: 直接到控制室 (小型项目/集中式)
  Tag → JB → Main Cabinet/DCS
  示例: FT-101 --Cable1--> JB-01 --Cable2--> DCS(AI-001)

路径类型 2: 经过现场 RIO (分布式控制)
  Tag → RIO Panel → Main Cabinet/DCS
  示例: FT-101 --Cable1--> RIO-01(AI-001) --Fieldbus--> DCS(CPU-01)

路径类型 3: 经过接线箱和 RIO (大型项目)
  Tag → JB → RIO Panel → Main Cabinet/DCS
  示例: FT-101 --Cable1--> JB-01 --Cable2--> RIO-01(AI-001) --Fieldbus--> DCS(CPU-01)

路径类型 4: 多级接线箱 (复杂布线)
  Tag → JB1 → JB2 → RIO Panel → Main Cabinet/DCS
```

##### 设备节点模型 (EquipmentNode)
```
目的: 统一表示信号路径中的各类设备节点，支持任意数量的中间节点

EquipmentNode 类型:
  - Tag: 现场仪表 (信号起点)
  - JunctionBox: 接线箱 (中间节点)
  - RIOPanel: 现场 I/O 盘柜 (中间节点，含 I/O 卡件)
  - Cabinet: 控制柜/MCC (中间或终点)
  - DCSController: DCS 控制器 (信号终点)
  - PLCRack: PLC 机架 (信号终点)
  - SISController: SIS 控制器 (信号终点)
  - Marshalling: 汇线柜 (中间节点)

通用字段:
  - id: UUID
  - node_type: 节点类型 (上述枚举)
  - name: 名称/编号
  - location: 物理位置 (FK -> PlantHierarchy)
  - description: 描述
```

##### WiringPath (接线路径)
```
目的: 定义仪表信号的完整接线路径

字段:
  - id: UUID
  - tag: FK -> Tag (信号起点)
  - path_segments: JSONField (路径段列表)
    [
      {
        "sequence": 1,
        "from_node_type": "Tag",
        "from_node_id": "uuid-of-ft-101",
        "from_terminal": "1+",
        "to_node_type": "JunctionBox",
        "to_node_id": "uuid-of-jb-01",
        "to_terminal": "TS-01/1",
        "cable_id": "uuid-of-cable-1"
      },
      {
        "sequence": 2,
        "from_node_type": "JunctionBox",
        "from_node_id": "uuid-of-jb-01",
        "from_terminal": "TS-01/1",
        "to_node_type": "RIOPanel",
        "to_node_id": "uuid-of-rio-01",
        "to_terminal": "AI-001/CH01+",
        "cable_id": "uuid-of-cable-2"
      },
      {
        "sequence": 3,
        "from_node_type": "RIOPanel",
        "from_node_id": "uuid-of-rio-01",
        "from_terminal": "Fieldbus-01",
        "to_node_type": "DCSController",
        "to_node_id": "uuid-of-dcs-cpu",
        "to_terminal": "FB-Port-1",
        "cable_id": "uuid-of-fieldbus-cable",
        "connection_type": "Fieldbus"  // 区分硬接线和通讯
      }
    ]
  - path_type: 路径类型 (Direct/ViaJB/ViaRIO/ViaJBAndRIO)
  - status: 状态 (Designed/Wired/Tested/Commissioned)
  - created_at, updated_at: 时间戳

说明:
  - 支持任意数量的中间节点
  - 每个路径段包含起点、终点、端子和电缆信息
  - connection_type 区分硬接线 (Hardwired) 和通讯 (Fieldbus/Ethernet)
```

##### RIOPanel (现场 I/O 盘柜)
```
目的: 表示分布式控制系统中的现场 I/O 盘柜

字段:
  - id: UUID
  - plant: FK -> Plant
  - area: FK -> PlantHierarchy (物理位置)
  - name: 盘柜名称 (如 "RIO-01", "RIO-U100")
  - code: 盘柜编号
  - rio_type: 类型 (DCS-RIO/PLC-Remote/SIS-RIO)
  - control_system: FK -> ControlSystem (所属控制系统)
  - communication_type: 通讯类型 (Fieldbus/Ethernet/Fiber)
  - communication_address: 通讯地址
  - power_supply: 供电信息
  - hazardous_area: 是否在危险区域
  - hazardous_cert: 防爆认证
  - description: 描述
  - created_at, updated_at: 时间戳

关联:
  - 包含多个 IOCard (I/O 卡件)
  - 包含多个 TerminalStrip (端子排)
```

##### IOCard (I/O 卡件)
```
目的: 表示 RIO 或控制柜中的 I/O 卡件

字段:
  - id: UUID
  - parent: FK -> RIOPanel 或 Cabinet (所属盘柜)
  - slot_number: 槽位号
  - card_type: 卡件类型 (AI/AO/DI/DO/PI/RTD/TC/HART/Fieldbus)
  - manufacturer: 制造商
  - model: 型号
  - channel_count: 通道数
  - signal_type: 信号类型 (4-20mA/0-10V/24VDC/Dry-Contact/RTD/TC)
  - status: 状态 (Spare/Assigned/Wired/Tested)
  - created_at, updated_at: 时间戳
```

##### IOChannel (I/O 通道) - 回路图生成基础
```
目的: 表示 I/O 卡件上的单个通道，支持通道分配和回路图生成

字段:
  - id: UUID
  - io_card: FK -> IOCard (所属卡件)
  - channel_number: 通道号 (1, 2, 3...)
  - channel_address: 通道地址 (如 "AI-001/CH01", "DI-002/CH16")
  - terminal_positive: 正极端子号 (如 "1+", "CH01+")
  - terminal_negative: 负极端子号 (如 "1-", "CH01-")
  - terminal_common: 公共端子号 (可选，用于 DI/DO)
  - terminal_shield: 屏蔽端子号 (可选)
  
  # 分配信息
  - assigned_tag: FK -> Tag (分配的仪表位号，可为空)
  - assignment_date: 分配日期
  - assigned_by: FK -> User
  
  # 信号配置
  - signal_range_low: 信号下限 (如 4 mA)
  - signal_range_high: 信号上限 (如 20 mA)
  - engineering_low: 工程量下限 (如 0)
  - engineering_high: 工程量上限 (如 100)
  - engineering_unit: 工程单位 (如 "m³/h", "°C")
  - alarm_low: 低报警值 (可选)
  - alarm_high: 高报警值 (可选)
  - alarm_low_low: 低低报警值 (可选)
  - alarm_high_high: 高高报警值 (可选)
  
  # 状态
  - status: 状态 (Spare/Reserved/Assigned/Wired/Tested/Commissioned)
  - remarks: 备注
  - created_at, updated_at: 时间戳

约束:
  - channel_number 在 io_card 内唯一
  - assigned_tag 的信号类型必须与 io_card.card_type 兼容
  
I/O 类型与信号匹配规则:
  - AI (Analogue Input): 4-20mA, 1-5V, 0-10V, RTD, TC
  - AO (Analogue Output): 4-20mA, 0-10V
  - DI (Digital Input): 24VDC, Dry-Contact, NAMUR
  - DO (Digital Output): 24VDC, Relay
```

##### 仪表接线制式 (Wiring Configuration)
```
目的: 支持不同类型仪表的接线制式，正确计算所需端子和芯线数量

接线制式类型:
  - 2-Wire (两线制): 信号和供电共用两根线
    适用: 4-20mA 变送器 (如 FT, TT, PT, LT)
    端子: +, - (或 L+, L-)
    芯线: 2 芯 (+ 屏蔽)
    特点: 回路供电，信号叠加在供电回路上
    
  - 3-Wire (三线制): 独立供电，信号输出
    适用: RTD (Pt100), 部分变送器
    端子: V+, V-, Signal (或 +, -, S)
    芯线: 3 芯 (+ 屏蔽)
    特点: 供电和信号分开，减少线路电阻影响
    
  - 4-Wire (四线制): 独立供电，独立信号
    适用: 高精度变送器, 分析仪表, 电动执行器
    端子: 
      - 信号: S+, S- (或 4+, 4-) - 4-20mA 信号输出
      - 供电: L+, L- (DC) 或 L, N (AC) - 独立供电
    芯线: 4 芯 (+ 屏蔽)，信号和供电分开
    供电类型:
      - 24VDC: 常用于变送器、执行器
      - 110VAC: 部分进口仪表
      - 230VAC (220VAC): 分析仪表、大功率执行器
    特点: 供电和信号完全独立，精度最高，抗干扰能力强
    
  - 6-Wire (六线制): RTD 高精度测量
    适用: 高精度 RTD 测量
    端子: I+, I-, V+, V-, S+, S-
    芯线: 6 芯
    特点: 电流激励和电压测量分开，消除引线电阻

数字信号接线:
  - DI (数字输入):
    - 干接点 (Dry Contact): 2 线 (NO/NC, COM)
    - 有源信号 (Active): 2 线 (+, -)
    - NAMUR: 2 线 (+, -)
    
  - DO (数字输出):
    - 继电器输出: 2-3 线 (NO, NC, COM)
    - 晶体管输出: 2 线 (+, -)
    - 24VDC 输出: 2 线 (+, -)

特殊接线:
  - 热电偶 (TC): 2 线 (+, -) + 补偿导线
  - HART 通讯: 叠加在 4-20mA 信号上，无需额外接线
  - Fieldbus (FF/PA): 2 线总线 + 屏蔽
```

##### InstrumentWiringConfig (仪表接线配置)
```
目的: 定义仪表类型的标准接线配置

字段:
  - id: UUID
  - instrument_type: FK -> InstrumentType
  - wiring_type: 接线制式 (2-Wire/3-Wire/4-Wire/6-Wire)
  - power_supply_type: 供电类型 (Loop-Powered/24VDC/110VAC/230VAC/Battery)
  - power_voltage: 供电电压 (V)
  - power_frequency: 供电频率 (Hz，AC 时适用)
  - signal_type: 信号类型 (4-20mA/0-10V/RTD/TC/Digital/Fieldbus)
  - wire_count: 芯线数量 (不含屏蔽)
  - signal_wire_count: 信号芯线数 (四线制时区分)
  - power_wire_count: 供电芯线数 (四线制时区分)
  - shield_required: 是否需要屏蔽
  - terminal_definition: JSONField (端子定义)
    {
      "signal_terminals": [
        { "name": "S+", "function": "Signal Positive", "color": "Red" },
        { "name": "S-", "function": "Signal Negative", "color": "Black" }
      ],
      "power_terminals": [
        { "name": "L+", "function": "Power Positive (DC)", "color": "Red" },
        { "name": "L-", "function": "Power Negative (DC)", "color": "Blue" }
        // 或 AC 供电:
        // { "name": "L", "function": "Line (AC)", "color": "Brown" },
        // { "name": "N", "function": "Neutral (AC)", "color": "Blue" },
        // { "name": "PE", "function": "Protective Earth", "color": "Green/Yellow" }
      ],
      "shield_terminal": { "name": "SH", "function": "Shield", "color": "Bare/Green" }
    }
  - cable_spec_recommendation: 推荐电缆规格
  - power_cable_spec: 供电电缆规格 (四线制 AC 供电时可能需要单独电缆)
  - remarks: 备注

预设配置示例:
  两线制 (Loop-Powered):
  - FT (流量变送器): 2-Wire, 4-20mA, Loop-Powered, 2芯+屏蔽
  - TT (温度变送器): 2-Wire, 4-20mA, Loop-Powered, 2芯+屏蔽
  - PT (压力变送器): 2-Wire, 4-20mA, Loop-Powered, 2芯+屏蔽
  - LT (液位变送器): 2-Wire, 4-20mA, Loop-Powered, 2芯+屏蔽
  
  三线制:
  - RTD (热电阻): 3-Wire, RTD, 24VDC, 3芯+屏蔽
  
  四线制 (24VDC 供电):
  - CV (调节阀): 4-Wire, 4-20mA, 24VDC, 信号2芯+供电2芯+屏蔽
  - FT (高精度): 4-Wire, 4-20mA, 24VDC, 信号2芯+供电2芯+屏蔽
  
  四线制 (110VAC 供电):
  - AT (进口分析仪): 4-Wire, 4-20mA, 110VAC, 信号2芯+供电2芯(L,N)+PE
  
  四线制 (230VAC 供电):
  - AT (分析仪): 4-Wire, 4-20mA, 230VAC, 信号2芯+供电3芯(L,N,PE)
  - MOV (电动阀): 4-Wire, 4-20mA, 230VAC, 信号2芯+供电3芯(L,N,PE)
  
  特殊:
  - TE (热电偶): 2-Wire, TC, 无供电, 补偿导线
  - XV (开关阀): DI+DO, 24VDC, 4芯 (2DI+2DO)
  - PSL/PSH (压力开关): DI, Dry-Contact, 2芯
```

##### 四线制供电详细规格
```
目的: 详细定义四线制仪表的不同供电配置

1. 四线制 24VDC 供电
   端子: S+, S-, L+, L- (或 4+, 4-, 24+, 24-)
   电缆: DJYPVP-4×1.5 (4芯+屏蔽)
   接线:
     - 芯1 (红): S+ 信号正
     - 芯2 (黑): S- 信号负
     - 芯3 (红): L+ 24VDC 正
     - 芯4 (蓝): L- 24VDC 负
     - 屏蔽: 接地
   适用: 调节阀定位器、高精度变送器

2. 四线制 110VAC 供电
   端子: S+, S-, L, N (部分需要 PE)
   电缆: 
     - 信号: DJYPVP-2×1.5 (2芯+屏蔽)
     - 供电: RVV-3×1.5 (3芯，含 PE)
   接线:
     - 信号芯1 (红): S+ 信号正
     - 信号芯2 (黑): S- 信号负
     - 供电芯1 (棕): L 火线 110VAC
     - 供电芯2 (蓝): N 零线
     - 供电芯3 (黄绿): PE 保护接地
   适用: 部分进口分析仪表

3. 四线制 230VAC (220VAC) 供电
   端子: S+, S-, L, N, PE
   电缆:
     - 信号: DJYPVP-2×1.5 (2芯+屏蔽)
     - 供电: RVV-3×1.5 或 3×2.5 (3芯，含 PE)
   接线:
     - 信号芯1 (红): S+ 信号正
     - 信号芯2 (黑): S- 信号负
     - 供电芯1 (棕): L 火线 230VAC
     - 供电芯2 (蓝): N 零线
     - 供电芯3 (黄绿): PE 保护接地
   适用: 分析仪表、电动执行器、大功率设备

注意事项:
  - AC 供电仪表通常需要单独的供电电缆
  - AC 供电必须有 PE 保护接地
  - 信号电缆和供电电缆应分开敷设，避免干扰
  - AC 供电接线箱需要配置空气开关或熔断器
```

##### TagWiring (仪表接线实例)
```
目的: 记录单个仪表的实际接线配置

字段:
  - id: UUID
  - tag: FK -> Tag
  - wiring_config: FK -> InstrumentWiringConfig (基于仪表类型)
  - actual_wiring_type: 实际接线制式 (可覆盖默认)
  - actual_wire_count: 实际芯线数
  - terminal_assignments: JSONField (端子分配)
    {
      "field_terminals": [
        { "terminal": "+", "cable": "IC-001", "core": 1, "color": "Red" },
        { "terminal": "-", "cable": "IC-001", "core": 2, "color": "Black" },
        { "terminal": "SH", "cable": "IC-001", "core": "Shield", "color": "Bare" }
      ],
      "jb_terminals": [
        { "terminal": "+", "jb": "JB-01", "strip": "TS-01", "terminal_no": 1 },
        { "terminal": "-", "jb": "JB-01", "strip": "TS-01", "terminal_no": 2 },
        { "terminal": "SH", "jb": "JB-01", "strip": "TS-GND", "terminal_no": 1 }
      ],
      "io_terminals": [
        { "terminal": "+", "channel": "AI-001/CH01", "terminal_no": "+" },
        { "terminal": "-", "channel": "AI-001/CH01", "terminal_no": "-" }
      ]
    }
  - wiring_status: 接线状态 (Designed/Wired/Tested/Commissioned)
  - created_at, updated_at: 时间戳
```

##### 接线制式与端子/芯线计算
```
自动计算功能:
  1. 根据仪表类型自动确定接线制式
  2. 根据接线制式计算所需端子数量
  3. 根据接线制式推荐电缆规格和芯数
  4. 自动分配端子时考虑接线制式

端子需求计算示例:
  - 2-Wire 变送器: 2 个信号端子 + 1 个屏蔽端子 = 3 端子
  - 3-Wire RTD: 3 个信号端子 + 1 个屏蔽端子 = 4 端子
  - 4-Wire 变送器: 4 个信号端子 + 1 个屏蔽端子 = 5 端子
  - 调节阀 (带反馈): 4 个信号端子 + 2 个反馈端子 + 1 个屏蔽 = 7 端子

电缆芯数推荐:
  - 2-Wire: DJYPVP-2×1.5 (2 芯 + 屏蔽)
  - 3-Wire: DJYPVP-3×1.5 (3 芯 + 屏蔽)
  - 4-Wire: DJYPVP-4×1.5 (4 芯 + 屏蔽)
  - 多信号: DJYPVP-8×1.5 或更多芯

接线箱端子分配规则:
  - 同一仪表的端子应分配在相邻位置
  - 屏蔽线统一接到接地端子排
  - IS 信号和非 IS 信号分开端子排
  - 预留 10-20% 备用端子
```

##### IOChannelAssignment (I/O 通道分配记录)
```
目的: 记录 I/O 通道分配的历史和变更

字段:
  - id: UUID
  - io_channel: FK -> IOChannel
  - tag: FK -> Tag
  - action: 操作类型 (Assign/Unassign/Modify)
  - previous_tag: FK -> Tag (之前分配的位号，可为空)
  - reason: 变更原因
  - assigned_by: FK -> User
  - assigned_at: 分配时间
  - approved_by: FK -> User (可选，需要审批时)
  - approved_at: 审批时间 (可选)
```

##### JunctionBoxTerminal (接线箱端子) - 回路图生成基础
```
目的: 表示接线箱内端子排上的单个端子，支持端子分配和回路图生成

字段:
  - id: UUID
  - terminal_strip: FK -> TerminalStrip (所属端子排)
  - terminal_number: 端子号 (1, 2, 3... 或 1A, 1B...)
  - terminal_address: 端子地址 (如 "JB-01/TS-01/1")
  - terminal_type: 端子类型 (Standard/Fused/Grounding/Spare)
  - rated_voltage: 额定电压 (V)
  - rated_current: 额定电流 (A)
  
  # 分配信息 - 来源侧 (From)
  - from_tag: FK -> Tag (来源仪表，可为空)
  - from_wire_number: 来源芯线号 (如 "1+", "SH")
  - from_cable: FK -> Cable (来源电缆)
  - from_core: 来源芯号
  
  # 分配信息 - 去向侧 (To)
  - to_tag: FK -> Tag (去向仪表/设备，可为空)
  - to_wire_number: 去向芯线号
  - to_cable: FK -> Cable (去向电缆)
  - to_core: 去向芯号
  
  # 跳线信息 (端子间短接)
  - jumper_to: FK -> self (跳线到另一端子，可为空)
  - jumper_type: 跳线类型 (None/Wire/Bar/Comb)
  
  # 状态
  - status: 状态 (Spare/Reserved/Assigned/Wired/Tested)
  - remarks: 备注
  - created_at, updated_at: 时间戳

约束:
  - terminal_number 在 terminal_strip 内唯一
  - 一个端子最多连接两侧 (from 和 to)
```

##### TerminalStrip (端子排)
```
目的: 表示接线箱或控制柜内的端子排

字段:
  - id: UUID
  - parent_type: 父对象类型 (JunctionBox/RIOPanel/Cabinet)
  - parent_id: 父对象 ID
  - strip_number: 端子排编号 (如 "TS-01", "TS-AI-001")
  - strip_type: 端子排类型 (Signal/Power/Grounding/Intrinsic-Safe)
  - terminal_count: 端子数量
  - manufacturer: 制造商
  - model: 型号
  - din_rail: DIN 导轨编号 (可选)
  - position: 安装位置描述
  - created_at, updated_at: 时间戳
```

##### 通道/端子分配功能 (Channel & Terminal Assignment)
```
目的: 提供 I/O 通道分配和接线箱端子分配功能，作为回路图生成的基础

1. I/O 通道分配功能
   
   1.1 自动分配
     - 根据仪表类型自动匹配 I/O 类型 (AI/AO/DI/DO)
     - 按顺序分配空闲通道
     - 支持按 Unit/Area 分组分配
     - 预留备用通道 (可配置比例，如 10%)
   
   1.2 手动分配
     - 拖拽仪表到指定通道
     - 批量分配 (选择多个仪表，分配到连续通道)
     - 交换分配 (两个仪表交换通道)
   
   1.3 分配规则检查
     - 信号类型匹配检查 (AI 只能分配模拟量输入仪表)
     - 通道容量检查 (防止超分配)
     - 重复分配检查 (一个仪表只能分配一个通道)
     - 防爆等级匹配 (IS 仪表必须分配到 IS 卡件)
   
   1.4 分配报表
     - I/O 清单 (I/O List)
     - 通道使用率统计
     - 未分配仪表列表
     - 空闲通道列表

2. 接线箱端子分配功能
   
   2.1 自动分配
     - 根据电缆芯数自动分配端子
     - 按信号类型分组 (AI/AO/DI/DO 分开)
     - 自动生成跳线 (如需要)
   
   2.2 手动分配
     - 拖拽电缆芯线到指定端子
     - 批量分配
     - 端子交换
   
   2.3 分配规则检查
     - 端子容量检查 (额定电压/电流)
     - 信号隔离检查 (IS 信号与非 IS 信号分开)
     - 跳线逻辑检查
   
   2.4 分配报表
     - 端子接线表 (Terminal Wiring Schedule)
     - 端子使用率统计
     - 接线箱布置图

3. 回路图生成关联
   
   回路图自动生成依赖以下分配数据:
   - Tag → IOChannel 分配 (确定 DCS/PLC 端)
   - Tag → JunctionBoxTerminal 分配 (确定接线箱端)
   - Cable → Terminal 连接 (确定电缆路径)
   
   数据完整性检查:
   - 回路内所有仪表必须有 I/O 分配
   - 所有电缆必须有端子分配
   - 信号路径必须完整 (Tag → JB → RIO/Cabinet → DCS)
```

##### I/O 分配 API
```
# 获取可分配的 I/O 通道
GET /api/io-channels/available/
  Query:
    - card_type: AI/AO/DI/DO
    - rio_panel_id: RIO 盘柜 ID (可选)
    - cabinet_id: 控制柜 ID (可选)
  Response: [
    { "id": "uuid", "address": "AI-001/CH01", "status": "Spare" },
    { "id": "uuid", "address": "AI-001/CH02", "status": "Spare" }
  ]

# 分配 I/O 通道
POST /api/io-channels/{channel_id}/assign/
  Body: {
    "tag_id": "uuid",
    "signal_range_low": 4,
    "signal_range_high": 20,
    "engineering_low": 0,
    "engineering_high": 100,
    "engineering_unit": "m³/h"
  }
  Response: { "success": true, "channel": {...} }

# 批量分配 I/O 通道
POST /api/io-channels/bulk-assign/
  Body: {
    "assignments": [
      { "tag_id": "uuid1", "channel_id": "uuid-ch1" },
      { "tag_id": "uuid2", "channel_id": "uuid-ch2" }
    ]
  }

# 自动分配 I/O 通道
POST /api/io-channels/auto-assign/
  Body: {
    "tag_ids": ["uuid1", "uuid2", "uuid3"],
    "rio_panel_id": "uuid",
    "strategy": "sequential"  // sequential/grouped-by-unit/grouped-by-loop
  }

# 取消分配
POST /api/io-channels/{channel_id}/unassign/
  Body: { "reason": "设计变更" }

# 获取可分配的端子
GET /api/terminals/available/
  Query:
    - junction_box_id: 接线箱 ID
    - terminal_strip_id: 端子排 ID (可选)
  Response: [...]

# 分配端子
POST /api/terminals/{terminal_id}/assign/
  Body: {
    "from_tag_id": "uuid",
    "from_wire_number": "1+",
    "from_cable_id": "uuid",
    "from_core": 1,
    "to_cable_id": "uuid",
    "to_core": 1
  }

# 生成 I/O 清单报表
GET /api/reports/io-list/
  Query:
    - project_id: 项目 ID
    - plant_id: 装置 ID (可选)
    - format: json/excel/pdf
  Response: I/O 清单数据或文件

# 生成端子接线表
GET /api/reports/terminal-schedule/
  Query:
    - junction_box_id: 接线箱 ID
    - format: json/excel/pdf
```

##### I/O 分配 UI 设计
```
┌─────────────────────────────────────────────────────────────────────────┐
│ I/O 通道分配                                    上下文: [Unit-100 ▼]    │
├─────────────────────────────────────────────────────────────────────────┤
│ [自动分配] [批量分配] [导出 I/O 清单]                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─ 待分配仪表 ─────────────────┐  ┌─ RIO-01 I/O 卡件 ───────────────┐ │
│  │                             │  │                                 │ │
│  │ 📋 AI 类型 (5)              │  │ ┌─ AI-001 (8CH) ──────────────┐ │ │
│  │   ├── FT-101 (未分配)       │  │ │ CH01: FT-101 ✅ 4-20mA      │ │ │
│  │   ├── TT-102 (未分配)       │  │ │ CH02: TT-102 ✅ 4-20mA      │ │ │
│  │   ├── PT-103 (未分配)       │  │ │ CH03: [空闲] ○              │ │ │
│  │   ├── LT-104 (未分配)       │  │ │ CH04: [空闲] ○              │ │ │
│  │   └── FT-105 (未分配)       │  │ │ CH05: [空闲] ○              │ │ │
│  │                             │  │ │ CH06: [空闲] ○              │ │ │
│  │ 📋 AO 类型 (2)              │  │ │ CH07: [预留] ◐              │ │ │
│  │   ├── FV-101 (未分配)       │  │ │ CH08: [预留] ◐              │ │ │
│  │   └── TV-102 (未分配)       │  │ └─────────────────────────────┘ │ │
│  │                             │  │                                 │ │
│  │ 📋 DI 类型 (3)              │  │ ┌─ AO-001 (4CH) ──────────────┐ │ │
│  │   └── ...                   │  │ │ CH01: FV-101 ✅ 4-20mA      │ │ │
│  │                             │  │ │ CH02: [空闲] ○              │ │ │
│  │ 📋 DO 类型 (2)              │  │ │ CH03: [空闲] ○              │ │ │
│  │   └── ...                   │  │ │ CH04: [空闲] ○              │ │ │
│  │                             │  │ └─────────────────────────────┘ │ │
│  └─────────────────────────────┘  └─────────────────────────────────┘ │
│                                                                         │
│  拖拽仪表到通道进行分配，或选择多个仪表点击 [自动分配]                   │
└─────────────────────────────────────────────────────────────────────────┘

端子分配 UI:
┌─────────────────────────────────────────────────────────────────────────┐
│ 端子分配 - JB-01                                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─ TS-01 (信号端子排) ─────────────────────────────────────────────┐   │
│  │                                                                   │   │
│  │  端子  │ 来源 (From)              │ 去向 (To)                    │   │
│  │ ──────┼──────────────────────────┼────────────────────────────── │   │
│  │   1   │ FT-101/1+ (IC-001/芯1)   │ RIO-01/AI-001/CH01+ (IC-002) │   │
│  │   2   │ FT-101/1- (IC-001/芯2)   │ RIO-01/AI-001/CH01- (IC-002) │   │
│  │   3   │ FT-101/SH (IC-001/芯3)   │ 接地                         │   │
│  │   4   │ TT-102/1+ (IC-003/芯1)   │ RIO-01/AI-001/CH02+ (IC-002) │   │
│  │   5   │ TT-102/1- (IC-003/芯2)   │ RIO-01/AI-001/CH02- (IC-002) │   │
│  │   6   │ [空闲]                   │ [空闲]                        │   │
│  │  ...  │                          │                              │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  [添加端子] [批量分配] [生成端子接线表]                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

##### 关键设计原则
```
1. Tag (仪表位号) 是核心
   - 所有数据围绕 Tag 组织
   - Tag 是规格书、接线、回路图的基础

2. Unit 是主要容器
   - 大多数仪表对象归属于 Unit
   - 位号命名通常包含 Unit 编号 (如 FT-101 属于 Unit-100)

3. 跨层级引用
   - Cable 连接不同位置，通过外键引用两端
   - from_equipment/to_equipment 可以是 Tag、JunctionBox、Cabinet

4. 共享库在项目级
   - 仪表类型、模板等可复用资源放在项目级
   - 避免重复定义，保证一致性

5. 物理位置决定归属
   - JunctionBox、CableRoute 等按物理位置归属
   - 便于施工管理和现场定位

6. 层级可配置
   - 简单项目可省略 Area 层级
   - 复杂项目可添加 SubUnit 层级
```

##### 数据模型外键关系
```python
# 项目级共享对象
class InstrumentType(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class SpecificationTemplate(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

# Plant 级别对象
class PID(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)

class CableRoute(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)

# Area 级别对象
class JunctionBox(models.Model):
    area = models.ForeignKey(PlantHierarchy, on_delete=models.CASCADE)
    # area.level == 'Area'

# Unit 级别对象 (核心)
class Tag(models.Model):
    unit = models.ForeignKey(PlantHierarchy, on_delete=models.CASCADE)
    # unit.level == 'Unit'
    instrument_type = models.ForeignKey(InstrumentType, on_delete=models.PROTECT)
    loop = models.ForeignKey(Loop, on_delete=models.SET_NULL, null=True)

class Loop(models.Model):
    unit = models.ForeignKey(PlantHierarchy, on_delete=models.CASCADE)

class Specification(models.Model):
    tag = models.OneToOneField(Tag, on_delete=models.CASCADE)

# 跨层级对象
class Cable(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    from_equipment = models.CharField()  # 可以是 Tag、JB、Cabinet
    to_equipment = models.CharField()
    # 或使用 GenericForeignKey 实现多态引用

class WiringConnection(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    cable = models.ForeignKey(Cable, on_delete=models.CASCADE)
    from_terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)
    to_terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)
```

#### 3.1.7 Organization (系统租户 - 可选)
```
目的: 多租户数据隔离 (SaaS 模式)
字段:
  - id: UUID (主键)
  - name: 组织名称 (如 "XX设计院", "YY工程公司")
  - slug: URL 友好标识
  - settings: JSONField (组织级配置)
  - is_active: 是否激活
  - created_at, updated_at: 时间戳
说明:
  - Organization 是系统级别的租户隔离
  - 用于 SaaS 部署，不同设计院/工程公司的数据隔离
  - 单机部署可忽略此层级
  - Project 归属于 Organization
关系:
  - Organization (可选) → Project → Client → Site → Plant → Area → Unit
```

#### 3.1.8 User & Permission (用户与权限) - RBAC
```
目的: 基于角色的访问控制 (RBAC)
模型:
  - User: 扩展 Django AbstractUser
    - organization: FK -> Organization
    - is_org_admin: 是否组织管理员
  - Role: 角色定义
    - name: 角色名 (Admin, Engineer, Viewer 等)
    - permissions: M2M -> Permission
  - Permission: 细粒度权限
    - codename: 权限代码 (如 tag.create, tag.edit, tag.delete)
    - model: 关联模型
  - UserProjectRole: 用户-项目-角色关联
    - user: FK -> User
    - project: FK -> Project
    - role: FK -> Role
权限级别:
  - Organization Admin: 组织管理员 (管理所有项目和用户)
  - Project Admin: 项目管理员 (管理单个项目)
  - Engineer: 工程师 (读写数据)
  - Viewer: 查看者 (只读)
```

#### 3.1.9 NamingConvention (命名规则) - SPI 特有

##### 3.1.9.1 NamingConvention 模型
```
目的: 强制规范位号格式，从源头杜绝数据录入随意性
       支持管理员定义复杂的正则表达式命名规则

字段:
  - id: UUID
  - project: FK -> Project
  - name: 规则名称 (如 "Standard Tag Naming", "Cable Naming")
  - entity_type: 应用实体类型
    - TAG: 仪表位号
    - LOOP: 控制回路
    - CABLE: 电缆
    - JUNCTION_BOX: 接线箱
    - TERMINAL_STRIP: 端子排
  - hierarchy_format: 层级格式类型 (见下方定义)
  - pattern: 正则表达式 (管理员自定义)
  - pattern_template: 模式模板 (用于生成正则表达式)
  - segment_definitions: JSONField (各段定义)
  - separator: 分隔符 (默认 "-")
  - description: 规则说明
  - examples: JSONField (示例列表)
  - validation_message: 验证失败提示信息
  - is_active: 是否启用
  - is_default: 是否为默认规则
  - priority: 优先级 (多规则时的匹配顺序)
  - created_at, updated_at: 时间戳

约束:
  - (project, entity_type, is_default=True) 唯一
  - pattern 必须是有效的正则表达式
```

##### 3.1.9.2 层级格式类型 (Hierarchy Format)
```
系统支持以下预定义的层级格式:

格式 1: Site-Plant-Area-Unit-Function-Sequence
  示例: ZH-ETH-100-U01-FT-001
  说明: 完整层级，适用于大型多厂区项目
  正则模板: ^{site}-{plant}-{area}-{unit}-{function}-{sequence}$

格式 2: Plant-Area-Unit-Function-Sequence
  示例: ETH-100-U01-FT-001
  说明: 省略 Site，适用于单厂区项目
  正则模板: ^{plant}-{area}-{unit}-{function}-{sequence}$

格式 3: Area-Unit-Function-Sequence
  示例: 100-U01-FT-001
  说明: 省略 Site 和 Plant，适用于单装置项目
  正则模板: ^{area}-{unit}-{function}-{sequence}$

格式 4: Unit-Function-Sequence
  示例: U01-FT-001 或 FT-001
  说明: 最简格式，适用于小型项目
  正则模板: ^{unit}-{function}-{sequence}$ 或 ^{function}-{sequence}$

格式 5: XXXX-Unit-Function-Sequence (灵活前缀)
  说明: XXXX 可以是 Site、Plant 或 Area 中的任意一个
  变体:
    - Site-Unit-Function-Sequence: ZH-U01-FT-001
    - Plant-Unit-Function-Sequence: ETH-U01-FT-001
    - Area-Unit-Function-Sequence: 100-U01-FT-001
  正则模板: ^{prefix}-{unit}-{function}-{sequence}$
  prefix_source: SITE | PLANT | AREA (配置项)

格式 6: 自定义 (Custom)
  说明: 管理员完全自定义正则表达式
  正则模板: 由管理员直接输入
```

##### 3.1.9.3 段定义 (Segment Definitions)
```
每个命名规则由多个段组成，每段有独立的验证规则:

segment_definitions: JSONField
{
  "segments": [
    {
      "name": "site",
      "display_name": "Site Code",
      "position": 1,
      "type": "hierarchy",           # hierarchy | function | sequence | custom
      "source": "site.code",         # 数据来源
      "pattern": "[A-Z]{2,4}",       # 段正则
      "min_length": 2,
      "max_length": 4,
      "case": "upper",               # upper | lower | mixed
      "required": true,
      "auto_fill": true,             # 是否自动填充
      "editable": false              # 是否可编辑
    },
    {
      "name": "plant",
      "display_name": "Plant Code",
      "position": 2,
      "type": "hierarchy",
      "source": "plant.code",
      "pattern": "[A-Z]{2,4}",
      "required": true,
      "auto_fill": true,
      "editable": false
    },
    {
      "name": "area",
      "display_name": "Area Code",
      "position": 3,
      "type": "hierarchy",
      "source": "area.code",
      "pattern": "\\d{2,3}",
      "required": true,
      "auto_fill": true,
      "editable": false
    },
    {
      "name": "unit",
      "display_name": "Unit Code",
      "position": 4,
      "type": "hierarchy",
      "source": "unit.code",
      "pattern": "U\\d{2}",
      "required": true,
      "auto_fill": true,
      "editable": false
    },
    {
      "name": "function",
      "display_name": "Function Code",
      "position": 5,
      "type": "function",
      "source": "instrument_type.function_code",
      "pattern": "[A-Z]{1,4}",       # FT, TT, PT, LT, CV, etc.
      "allowed_values": ["FT", "TT", "PT", "LT", "AT", "CV", "XV", "PSV", "PV"],
      "required": true,
      "auto_fill": false,
      "editable": true
    },
    {
      "name": "sequence",
      "display_name": "Sequence Number",
      "position": 6,
      "type": "sequence",
      "pattern": "\\d{3,4}[A-Z]?",   # 001, 001A, 0001
      "min_value": 1,
      "max_value": 9999,
      "padding": 3,                   # 前导零填充
      "suffix_pattern": "[A-Z]?",     # 可选后缀
      "auto_increment": true,
      "required": true,
      "editable": true
    }
  ],
  "separator": "-",
  "case_sensitive": false
}
```

##### 3.1.9.4 预设命名规则模板
```
系统提供以下预设模板，管理员可直接使用或修改:

1. ISA 标准格式 (ISA-5.1)
   格式: {Function}{Sequence}{Suffix}
   示例: FT-101, TIC-201A, PSV-001
   正则: ^[A-Z]{1,4}-\\d{3}[A-Z]?$

2. 完整层级格式 (Full Hierarchy)
   格式: {Site}-{Plant}-{Area}-{Unit}-{Function}-{Sequence}
   示例: ZH-ETH-100-U01-FT-001
   正则: ^[A-Z]{2,4}-[A-Z]{2,4}-\\d{2,3}-U\\d{2}-[A-Z]{1,4}-\\d{3}[A-Z]?$

3. 装置-单元格式 (Plant-Unit)
   格式: {Plant}-{Unit}-{Function}-{Sequence}
   示例: ETH-U01-FT-001
   正则: ^[A-Z]{2,4}-U\\d{2}-[A-Z]{1,4}-\\d{3}[A-Z]?$

4. 区域-单元格式 (Area-Unit)
   格式: {Area}-{Unit}-{Function}-{Sequence}
   示例: 100-U01-FT-001
   正则: ^\\d{2,3}-U\\d{2}-[A-Z]{1,4}-\\d{3}[A-Z]?$

5. 简化格式 (Simplified)
   格式: {Function}-{Sequence}
   示例: FT-101
   正则: ^[A-Z]{1,4}-\\d{3}[A-Z]?$

6. 电缆命名格式 (Cable)
   格式: IC-{Function}-{Sequence}-{Core}
   示例: IC-FT-101-01
   正则: ^IC-[A-Z]{1,4}-\\d{3}-\\d{2}$

7. 接线箱命名格式 (Junction Box)
   格式: JB-{Area}-{Sequence}
   示例: JB-100-01
   正则: ^JB-\\d{2,3}-\\d{2}$
```

##### 3.1.9.5 命名规则管理 UI
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Naming Convention Management                          [+ New Rule] [Import] │
├─────────────────────────────────────────────────────────────────────────────┤
│ Entity Type: [All ▼]  Status: [Active ▼]                         [🔍 Search]│
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Name                    │ Entity │ Format              │ Default│ Status│ │
│ ├─────────────────────────┼────────┼─────────────────────┼────────┼───────┤ │
│ │ Standard Tag Naming     │ TAG    │ Plant-Area-Unit-... │ ✓      │ Active│ │
│ │ ISA-5.1 Tag Format      │ TAG    │ Function-Sequence   │        │ Active│ │
│ │ Cable Naming Convention │ CABLE  │ IC-Function-Seq-... │ ✓      │ Active│ │
│ │ Junction Box Naming     │ JB     │ JB-Area-Sequence    │ ✓      │ Active│ │
│ └─────────────────────────┴────────┴─────────────────────┴────────┴───────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

Edit Naming Convention:
┌─────────────────────────────────────────────────────────────────────────────┐
│ Edit Naming Convention                                       [Save] [Cancel]│
├─────────────────────────────────────────────────────────────────────────────┤
│ Basic Information:                                                          │
│ Name: [Standard Tag Naming                                                ] │
│ Entity Type: [TAG ▼]                                                        │
│ Description: [Standard tag naming for ethylene project                    ] │
│                                                                             │
│ ┌─ Hierarchy Format ───────────────────────────────────────────────────────┐│
│ │ Format Type: [Plant-Area-Unit-Function-Sequence ▼]                       ││
│ │                                                                          ││
│ │ Available Formats:                                                       ││
│ │   ( ) Site-Plant-Area-Unit-Function-Sequence                             ││
│ │   (•) Plant-Area-Unit-Function-Sequence                                  ││
│ │   ( ) Area-Unit-Function-Sequence                                        ││
│ │   ( ) Unit-Function-Sequence                                             ││
│ │   ( ) XXXX-Unit-Function-Sequence  Prefix: [Plant ▼]                     ││
│ │   ( ) Custom (define your own regex)                                     ││
│ └──────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│ ┌─ Segment Configuration ──────────────────────────────────────────────────┐│
│ │ Separator: [-]                                                           ││
│ │                                                                          ││
│ │ Segments:                                                                ││
│ │ ┌────┬──────────┬────────────────┬──────────┬──────────┬───────────────┐ ││
│ │ │ #  │ Name     │ Pattern        │ Source   │ Auto-fill│ Editable      │ ││
│ │ ├────┼──────────┼────────────────┼──────────┼──────────┼───────────────┤ ││
│ │ │ 1  │ Plant    │ [A-Z]{2,4}     │ plant    │ ✓        │               │ ││
│ │ │ 2  │ Area     │ \d{2,3}        │ area     │ ✓        │               │ ││
│ │ │ 3  │ Unit     │ U\d{2}         │ unit     │ ✓        │               │ ││
│ │ │ 4  │ Function │ [A-Z]{1,4}     │ manual   │          │ ✓             │ ││
│ │ │ 5  │ Sequence │ \d{3}[A-Z]?    │ auto     │ ✓        │ ✓             │ ││
│ │ └────┴──────────┴────────────────┴──────────┴──────────┴───────────────┘ ││
│ │                                                    [+ Add Segment] [↑] [↓]││
│ └──────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│ ┌─ Generated Pattern ──────────────────────────────────────────────────────┐│
│ │ Regex: ^[A-Z]{2,4}-\d{2,3}-U\d{2}-[A-Z]{1,4}-\d{3}[A-Z]?$                ││
│ │                                                                          ││
│ │ Test: [ETH-100-U01-FT-001    ] [Validate]  ✓ Valid                       ││
│ │                                                                          ││
│ │ Examples:                                                                ││
│ │   ✓ ETH-100-U01-FT-001                                                   ││
│ │   ✓ ARO-200-U02-TIC-201A                                                 ││
│ │   ✗ FT-001 (missing hierarchy)                                          ││
│ └──────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│ [✓] Set as default for TAG  [✓] Active                                     │
│ Validation Message: [Tag number must follow format: Plant-Area-Unit-Func...]│
└─────────────────────────────────────────────────────────────────────────────┘

Custom Regex Editor (for advanced users):
┌─────────────────────────────────────────────────────────────────────────────┐
│ Custom Regular Expression                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ Pattern:                                                                    │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ ^(?P<site>[A-Z]{2,4})-(?P<plant>[A-Z]{2,4})-(?P<area>\d{2,3})-         │ │
│ │ (?P<unit>U\d{2})-(?P<function>[A-Z]{1,4})-(?P<sequence>\d{3}[A-Z]?)$   │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│ Named Groups Detected:                                                      │
│   - site: [A-Z]{2,4}                                                        │
│   - plant: [A-Z]{2,4}                                                       │
│   - area: \d{2,3}                                                           │
│   - unit: U\d{2}                                                            │
│   - function: [A-Z]{1,4}                                                    │
│   - sequence: \d{3}[A-Z]?                                                   │
│                                                                             │
│ [Validate Regex] [Test with Sample]                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

##### 3.1.9.6 命名规则验证流程
```
验证流程:

1. 用户输入位号 (Tag Number)
   ┌─────────────────────────────────────────────────────────────────┐
   │ Tag Number: [ETH-100-U01-FT-001    ]                            │
   └─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
2. 获取适用的命名规则
   - 根据 entity_type (TAG) 查找规则
   - 按 priority 排序
   - 优先使用 is_default = True 的规则
                                 │
                                 ▼
3. 正则表达式验证
   - 使用 pattern 验证格式
   - 提取各段值 (使用命名捕获组)
                                 │
                                 ▼
4. 层级一致性验证
   - 验证 plant 段与当前选择的 Plant 一致
   - 验证 area 段与当前选择的 Area 一致
   - 验证 unit 段与当前选择的 Unit 一致
                                 │
                                 ▼
5. 唯一性验证
   - 检查位号在 Unit 内是否唯一
                                 │
                                 ▼
6. 返回验证结果
   ┌─────────────────────────────────────────────────────────────────┐
   │ ✓ Valid: Tag number follows naming convention                   │
   │   Parsed: Plant=ETH, Area=100, Unit=U01, Function=FT, Seq=001   │
   └─────────────────────────────────────────────────────────────────┘
   
   或
   
   ┌─────────────────────────────────────────────────────────────────┐
   │ ✗ Invalid: Tag number must follow format: Plant-Area-Unit-...   │
   │   Expected pattern: ^[A-Z]{2,4}-\d{2,3}-U\d{2}-[A-Z]{1,4}-...   │
   │   Your input: FT-001                                            │
   └─────────────────────────────────────────────────────────────────┘
```

##### 3.1.9.7 自动生成位号
```
系统支持基于命名规则自动生成位号:

自动生成流程:
1. 用户选择 Unit (自动获取 Site/Plant/Area/Unit 代码)
2. 用户选择仪表类型 (获取 Function 代码)
3. 系统自动计算下一个 Sequence 号
4. 组合生成完整位号

示例:
  选择: Unit = U01 (in Area 100, Plant ETH, Site ZH)
  选择: InstrumentType = Flow Transmitter (Function = FT)
  现有最大序号: FT-003
  
  自动生成: ZH-ETH-100-U01-FT-004 (完整格式)
           或 ETH-100-U01-FT-004 (Plant-Area-Unit 格式)
           或 FT-004 (简化格式)

API:
  POST /api/tags/generate-number/
  Request:
    {
      "unit_id": "uuid",
      "instrument_type_id": "uuid",
      "naming_convention_id": "uuid" (可选，使用默认)
    }
  Response:
    {
      "generated_number": "ETH-100-U01-FT-004",
      "segments": {
        "plant": "ETH",
        "area": "100",
        "unit": "U01",
        "function": "FT",
        "sequence": "004"
      },
      "next_sequence": 5
    }
```

##### 3.1.9.8 API 端点
```
# 命名规则管理
GET    /api/naming-conventions/                    # 列表
POST   /api/naming-conventions/                    # 创建
GET    /api/naming-conventions/{id}/               # 详情
PUT    /api/naming-conventions/{id}/               # 更新
DELETE /api/naming-conventions/{id}/               # 删除
POST   /api/naming-conventions/{id}/set-default/   # 设为默认
POST   /api/naming-conventions/{id}/validate/      # 验证测试

# 预设模板
GET    /api/naming-conventions/templates/          # 获取预设模板列表
POST   /api/naming-conventions/from-template/      # 从模板创建

# 位号验证和生成
POST   /api/tags/validate-number/                  # 验证位号格式
POST   /api/tags/generate-number/                  # 自动生成位号
POST   /api/tags/parse-number/                     # 解析位号各段
```

### 3.2 模块 1.2 - 仪表索引模块 (Instrument Index)

> **SPI 对应**: Instrument Index Module  
> **Django App**: `core_engineering`

#### 3.2.1 PlantHierarchy (工厂层级)
```
目的: 定义工厂物理结构，SPI 强制执行的三级架构
结构: Plant -> Area -> Unit (使用 MPTT)
字段:
  - id: BigAutoField
  - project: FK -> Project
  - name: 节点名称
  - code: 节点代码
  - node_type: PLANT | AREA | UNIT
  - parent: TreeForeignKey (自引用)
  - description: 描述
  - is_active: 是否激活
约束:
  - code 在同一 parent 下唯一
  - 层级规则: PLANT 只能是根节点, AREA 只能在 PLANT 下, UNIT 只能在 AREA 下
```

#### 3.2.2 Loop (控制回路)
```
目的: 组织相关仪表位号
字段:
  - id: BigAutoField
  - project: FK -> Project
  - loop_tag: 回路标识 (唯一)
  - function: 功能类型 (F/T/P/L/A/C/H/I/S/X)
  - suffix: 回路后缀
  - unit: FK -> PlantHierarchy (限制为 UNIT 类型)
  - description: 描述
  - is_active: 是否激活
约束:
  - loop_tag 在 project 内唯一
```

#### 3.2.3 InstrumentType (仪表类型)
```
目的: 定义仪表规格模板
字段:
  - id: BigAutoField
  - organization: FK -> Organization (可共享)
  - name: 类型名称
  - code: 类型代码 (FT, TT, CV, PT 等)
  - category: 类别 (TRANSMITTER, CONTROL_VALVE, SWITCH 等)
  - schema_template: JSONField (JSON Schema 定义规格字段)
  - default_spec_data: JSONField (默认规格值)
  - is_active: 是否激活
约束:
  - code 在 organization 内唯一
```

#### 3.2.4 Tag (仪表位号) - 核心模型
```
目的: 表示单个仪表，系统核心数据实体
字段:
  - id: BigAutoField
  - project: FK -> Project
  - tag_number: 位号 (如 FT-101)
  - unit: FK -> PlantHierarchy (必须, 限制为 UNIT)
  - loop: FK -> Loop (可选)
  - instrument_type: FK -> InstrumentType
  - service: 服务描述
  - description: 详细描述
  - spec_data: JSONField (规格数据, 必须符合 instrument_type.schema_template)
  - status: 状态 (ACTIVE/INACTIVE/DELETED/PENDING/UNDER_REVIEW)
  - revision: 版本号
  - version: 乐观锁版本 (并发控制)
  - created_by: FK -> User
  - updated_by: FK -> User
约束:
  - tag_number 在 unit 内唯一 (SPI 核心要求)
  - loop 必须与 tag 属于同一 unit
  - spec_data 必须通过 schema_template 验证
  - tag_number 必须符合 NamingConvention 规则
```

#### 3.2.5 TypicalLoop (典型回路模板) - SPI 特有
```
目的: 支持"典型回路"复制功能，一键生成多组实体数据
字段:
  - id: BigAutoField
  - project: FK -> Project
  - name: 模板名称 (如 "标准流量控制回路")
  - function: 功能类型
  - description: 模板描述
  - template_data: JSONField (包含回路内所有位号的模板定义)
功能:
  - 定义回路模板 (包含 FE, FT, FIC, FV 等位号)
  - 批量实例化：输入数量和起始编号，自动生成多组回路
  - 支持参数化替换 (如 Unit、序号等)
```

### 3.3 模块 1.3 - 工程数据编辑器 (EDE)

> **SPI 对应**: Engineering Data Editor  
> **实现**: 前端 TanStack Table + 后端 QueryBuilder API

#### 3.3.1 SavedView (保存的视图)
```
目的: 保存用户自定义的数据视图，可共享为项目标准
字段:
  - id: BigAutoField
  - project: FK -> Project
  - name: 视图名称
  - created_by: FK -> User
  - is_shared: 是否共享给项目成员
  - view_config: JSONField
    - columns: 显示的列及顺序
    - filters: 过滤条件
    - sort: 排序规则
    - grouping: 分组设置
功能:
  - 跨表查询 (仪表索引 + 过程数据)
  - 动态 SQL 构建 (用户无需懂 SQL)
  - 视图保存和共享
```

#### 3.3.2 前端 EDE 组件规格
```
技术: TanStack Table v8 + 虚拟滚动
功能:
  - 高性能数据网格 (支持 10,000+ 行)
  - 列排序、多条件过滤、分组
  - 行内编辑 (双击编辑)
  - 批量选择和操作
  - 批量填充 (Bulk Fill)
  - 列拖拽排序
  - 列宽调整和固定
  - 导出选中/全部数据
```

### 3.4 模块 1.4 - 规格书模块 (Specifications)

> **SPI 对应**: Specifications Module  
> **Django App**: `specifications`

#### 3.4.0 工艺与管道数据 (Process & Piping Data)

##### 3.4.0.1 ProcessData (工艺过程数据)
```
目的: 供 Process Engineer 输入和编辑工艺过程数据，用于生成仪表规格书

字段:
  - id: UUID
  - tag: FK -> Tag (关联仪表位号)
  - project: FK -> Project
  
  # 工艺介质 (Process Fluid)
  - fluid_name: 介质名称 (如 "Crude Oil", "Steam", "Natural Gas")
  - fluid_state: 介质状态 (Liquid/Gas/Vapor/Two-Phase/Solid/Slurry)
  - fluid_composition: JSONField (介质组分)
    {
      "components": [
        { "name": "Methane", "percentage": 85.5 },
        { "name": "Ethane", "percentage": 8.2 },
        { "name": "Propane", "percentage": 4.1 }
      ]
    }
  - corrosive: 是否腐蚀性
  - toxic: 是否有毒
  - flammable: 是否易燃
  
  # 工艺条件 - 正常工况 (Normal Operating Conditions)
  - operating_pressure: 操作压力 (barg)
  - operating_temperature: 操作温度 (°C)
  - operating_flow_rate: 操作流量
  - flow_rate_unit: 流量单位 (m³/h, kg/h, Nm³/h, t/h)
  
  # 工艺条件 - 设计工况 (Design Conditions)
  - design_pressure: 设计压力 (barg)
  - design_temperature_max: 设计温度上限 (°C)
  - design_temperature_min: 设计温度下限 (°C)
  - max_flow_rate: 最大流量
  - min_flow_rate: 最小流量
  
  # 工艺条件 - 报警/联锁 (Alarm/Interlock)
  - alarm_high: 高报警值
  - alarm_low: 低报警值
  - alarm_high_high: 高高报警值 (联锁)
  - alarm_low_low: 低低报警值 (联锁)
  
  # 物性数据 (Physical Properties)
  - density: 密度 (kg/m³)
  - viscosity: 粘度 (cP)
  - specific_gravity: 比重
  - molecular_weight: 分子量
  - vapor_pressure: 蒸汽压 (kPa)
  - critical_pressure: 临界压力 (MPa)
  - critical_temperature: 临界温度 (°C)
  - compressibility_factor: 压缩系数 (Z)
  - specific_heat_ratio: 比热比 (Cp/Cv)
  
  # 元数据
  - data_source: 数据来源 (Process Simulation/Lab Test/Field Measurement/Estimated)
  - simulation_case: 模拟工况名称
  - last_updated_by: FK -> User
  - created_at, updated_at: 时间戳
  - remarks: 备注

约束:
  - 每个 Tag 可以有多个 ProcessData 记录 (不同工况)
  - 至少需要一个 "Normal" 工况的数据
```

##### 3.4.0.2 PipeSpecification (管道规格)
```
目的: 定义管道规格 (Pipe Spec)，供 Mechanical Engineer 管理

字段:
  - id: UUID
  - project: FK -> Project
  - spec_code: 规格代号 (如 "A1A", "B2B", "C3C")
  - description: 描述 (如 "Carbon Steel, 150#, ASME B16.5")
  
  # 管道材质
  - pipe_material: 管道材质 (Carbon Steel/Stainless Steel/Alloy/Duplex/Plastic)
  - material_grade: 材质牌号 (如 "A106 Gr.B", "316L", "A335 P11")
  - corrosion_allowance: 腐蚀裕量 (mm)
  
  # 压力等级
  - pressure_class: 压力等级 (150#/300#/600#/900#/1500#/2500#)
  - design_pressure: 设计压力 (barg)
  - design_temperature_max: 设计温度上限 (°C)
  - design_temperature_min: 设计温度下限 (°C)
  
  # 法兰标准
  - flange_standard: 法兰标准 (ASME B16.5/ASME B16.47/EN 1092-1/JIS B2220)
  - flange_face: 法兰面型式 (RF/RTJ/FF)
  - gasket_type: 垫片类型 (Spiral Wound/Ring Joint/PTFE/Graphite)
  
  # 连接方式
  - connection_types: JSONField (允许的连接方式)
    {
      "small_bore": ["SW", "THD", "FNPT"],  # 小口径 (≤2")
      "large_bore": ["BW", "FLG"]            # 大口径 (>2")
    }
  
  # 适用范围
  - service_type: 适用介质类型 (Hydrocarbon/Utility/Chemical/Steam)
  - is_active: 是否激活
  - created_at, updated_at: 时间戳

预设规格示例:
  - A1A: Carbon Steel, 150#, RF, Hydrocarbon Service
  - A2B: Carbon Steel, 300#, RF, Hydrocarbon Service
  - B1A: 316L Stainless Steel, 150#, RF, Chemical Service
  - C1A: Carbon Steel, 150#, RF, Utility (Water/Air)
  - S1A: Carbon Steel, 300#, RF, Steam Service
```

##### 3.4.0.3 ProcessConnection (工艺过程连接)
```
目的: 定义仪表与工艺管道/设备的连接方式和尺寸

字段:
  - id: UUID
  - tag: FK -> Tag (关联仪表位号)
  - pipe_spec: FK -> PipeSpecification (管道规格)
  
  # 连接位置
  - connection_location: 连接位置类型 (Pipe/Vessel/Equipment/Tank)
  - line_number: 管线号 (如 "6"-HC-101-A1A")
  - equipment_tag: 设备位号 (如 "V-101", "P-101A")
  
  # 连接尺寸
  - process_connection_size: 工艺连接尺寸 (如 "2"", "DN50")
  - size_unit: 尺寸单位 (inch/DN)
  - instrument_connection_size: 仪表连接尺寸 (如 "1/2"", "DN15")
  
  # 连接类型
  - connection_type: 连接类型
    - FLG: 法兰连接 (Flanged)
    - THD: 螺纹连接 (Threaded)
    - SW: 承插焊 (Socket Weld)
    - BW: 对焊 (Butt Weld)
    - FNPT: 内螺纹 (Female NPT)
    - MNPT: 外螺纹 (Male NPT)
    - TRI-CLAMP: 卡箍连接 (卫生级)
    - WAFER: 对夹式
  
  # 法兰详情 (当 connection_type = FLG 时)
  - flange_rating: 法兰等级 (150#/300#/600#/900#/1500#/2500#)
  - flange_face: 法兰面 (RF/RTJ/FF)
  - flange_standard: 法兰标准 (ASME B16.5/EN 1092-1)
  
  # 附件
  - requires_root_valve: 是否需要根部阀
  - root_valve_type: 根部阀类型 (Gate/Globe/Ball/Needle)
  - root_valve_size: 根部阀尺寸
  - requires_bleed_valve: 是否需要排放阀
  - requires_manifold: 是否需要阀组 (用于差压变送器)
  - manifold_type: 阀组类型 (3-Valve/5-Valve)
  
  # 安装方式
  - mounting_type: 安装方式 (Inline/Insertion/Remote/Direct)
  - orientation: 安装方向 (Horizontal/Vertical/Angled)
  - insertion_length: 插入长度 (mm，用于插入式仪表)
  
  # 元数据
  - created_at, updated_at: 时间戳
  - remarks: 备注

约束:
  - 每个 Tag 至少有一个 ProcessConnection
  - 差压变送器需要两个连接 (High/Low)
```

##### 3.4.0.4 工艺数据输入 UI (Process Data Entry)
```
目的: 供 Process Engineer 输入和编辑工艺数据

页面布局:
┌─────────────────────────────────────────────────────────────────────────────┐
│ Process Data Entry                                           [Save] [Cancel]│
├─────────────────────────────────────────────────────────────────────────────┤
│ Tag: FT-101 | Service: Feed Flow to Reactor                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─ Process Fluid ──────────────────────────────────────────────────────────┐│
│ │ Fluid Name: [Crude Oil        ▼]  State: [Liquid ▼]                      ││
│ │ Corrosive: [No ▼]  Toxic: [No ▼]  Flammable: [Yes ▼]                     ││
│ │ [+ Add Composition]                                                       ││
│ └───────────────────────────────────────────────────────────────────────────┘│
│ ┌─ Operating Conditions ────────────────────────────────────────────────────┐│
│ │           │ Normal  │ Design Max │ Design Min │ Unit                      ││
│ │ Pressure  │ [5.5  ] │ [10.0    ] │ [0.0     ] │ barg                      ││
│ │ Temperature│ [85   ] │ [150     ] │ [-10     ] │ °C                        ││
│ │ Flow Rate │ [100  ] │ [150     ] │ [20      ] │ [m³/h ▼]                  ││
│ └───────────────────────────────────────────────────────────────────────────┘│
│ ┌─ Physical Properties ─────────────────────────────────────────────────────┐│
│ │ Density: [850    ] kg/m³   Viscosity: [5.2   ] cP                         ││
│ │ Specific Gravity: [0.85 ]  Molecular Weight: [     ]                      ││
│ │ [Calculate from Simulation] [Import from HYSYS/Aspen]                     ││
│ └───────────────────────────────────────────────────────────────────────────┘│
│ ┌─ Alarm/Interlock Settings ────────────────────────────────────────────────┐│
│ │ HH: [140   ]  H: [120   ]  L: [30    ]  LL: [20    ]                      ││
│ └───────────────────────────────────────────────────────────────────────────┘│
│ Data Source: [Process Simulation ▼]  Simulation Case: [Normal Operation   ] │
│ Remarks: [                                                                 ] │
└─────────────────────────────────────────────────────────────────────────────┘

功能:
  - 表格式数据输入，支持批量编辑
  - 从工艺模拟软件导入 (HYSYS, Aspen Plus, PRO/II)
  - 物性计算器 (基于介质和条件)
  - 数据验证 (范围检查、一致性检查)
  - 变更追踪 (谁在什么时候改了什么)
```

##### 3.4.0.5 管道连接数据输入 UI (Piping Connection Entry)
```
目的: 供 Mechanical Engineer 输入管道和连接数据

页面布局:
┌─────────────────────────────────────────────────────────────────────────────┐
│ Piping & Connection Data                                     [Save] [Cancel]│
├─────────────────────────────────────────────────────────────────────────────┤
│ Tag: FT-101 | Type: Flow Transmitter                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─ Process Connection ──────────────────────────────────────────────────────┐│
│ │ Line Number: [6"-HC-101-A1A    ]  Equipment: [         ]                  ││
│ │ Pipe Spec: [A1A - Carbon Steel, 150# ▼]                                   ││
│ │                                                                            ││
│ │ Process Connection:                                                        ││
│ │   Size: [2"    ▼]  Type: [FLG ▼]  Rating: [150# ▼]  Face: [RF ▼]          ││
│ │                                                                            ││
│ │ Instrument Connection:                                                     ││
│ │   Size: [1/2"  ▼]  Type: [FNPT ▼]                                         ││
│ └───────────────────────────────────────────────────────────────────────────┘│
│ ┌─ Root Valve & Accessories ────────────────────────────────────────────────┐│
│ │ Root Valve: [✓] Required  Type: [Ball ▼]  Size: [1/2" ▼]                  ││
│ │ Bleed Valve: [✓] Required                                                 ││
│ │ Manifold: [ ] Required  Type: [3-Valve ▼]                                 ││
│ └───────────────────────────────────────────────────────────────────────────┘│
│ ┌─ Mounting ────────────────────────────────────────────────────────────────┐│
│ │ Type: [Inline ▼]  Orientation: [Horizontal ▼]                             ││
│ │ Insertion Length: [     ] mm (for insertion type)                         ││
│ └───────────────────────────────────────────────────────────────────────────┘│
│ Remarks: [                                                                 ] │
└─────────────────────────────────────────────────────────────────────────────┘

Pipe Specification Library:
┌─────────────────────────────────────────────────────────────────────────────┐
│ Pipe Specifications                                    [+ Add Spec] [Import]│
├──────┬────────────────────────────────────┬────────┬────────┬───────────────┤
│ Code │ Description                        │ Rating │ Flange │ Service       │
├──────┼────────────────────────────────────┼────────┼────────┼───────────────┤
│ A1A  │ Carbon Steel, ASME B16.5           │ 150#   │ RF     │ Hydrocarbon   │
│ A2B  │ Carbon Steel, ASME B16.5           │ 300#   │ RF     │ Hydrocarbon   │
│ B1A  │ 316L Stainless Steel, ASME B16.5   │ 150#   │ RF     │ Chemical      │
│ C1A  │ Carbon Steel, ASME B16.5           │ 150#   │ RF     │ Utility       │
│ S1A  │ Carbon Steel, ASME B16.5           │ 300#   │ RF     │ Steam         │
└──────┴────────────────────────────────────┴────────┴────────┴───────────────┘

功能:
  - 管道规格库管理 (项目级)
  - 从 P&ID 数据导入管线号和规格
  - 连接类型自动推荐 (基于管道规格和仪表类型)
  - 法兰等级匹配验证
  - 批量编辑支持
```

##### 3.4.0.6 数据流向规格书
```
工艺数据和管道数据如何流向仪表规格书:

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   ProcessData    │    │ ProcessConnection│    │ PipeSpecification│
│ (Process Engr)   │    │ (Mech Engr)      │    │ (Mech Engr)      │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   Tag (Instrument)     │
                    │   + InstrumentType     │
                    │   + spec_data (JSON)   │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │ SpecificationDocument  │
                    │ (Auto-generated)       │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   PDF / Print Output   │
                    └────────────────────────┘

规格书字段映射示例 (Flow Transmitter):
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INSTRUMENT SPECIFICATION SHEET                           │
│                         Flow Transmitter                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ TAG NUMBER: FT-101              SERVICE: Feed Flow to Reactor               │
├─────────────────────────────────────────────────────────────────────────────┤
│ PROCESS DATA (from ProcessData)                                             │
│ ─────────────────────────────────────────────────────────────────────────── │
│ Fluid: Crude Oil                State: Liquid                               │
│ Operating Pressure: 5.5 barg    Design Pressure: 10.0 barg                  │
│ Operating Temperature: 85°C     Design Temperature: -10 to 150°C            │
│ Normal Flow: 100 m³/h           Max Flow: 150 m³/h    Min Flow: 20 m³/h     │
│ Density: 850 kg/m³              Viscosity: 5.2 cP                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ PROCESS CONNECTION (from ProcessConnection + PipeSpecification)             │
│ ─────────────────────────────────────────────────────────────────────────── │
│ Line Number: 6"-HC-101-A1A      Pipe Spec: A1A                              │
│ Process Connection: 2" 150# RF Flange                                       │
│ Instrument Connection: 1/2" FNPT                                            │
│ Root Valve: Ball Valve, 1/2"    Bleed Valve: Required                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ INSTRUMENT DATA (from Tag + InstrumentType)                                 │
│ ─────────────────────────────────────────────────────────────────────────── │
│ Manufacturer: [          ]      Model: [          ]                         │
│ Range: 0-150 m³/h               Output: 4-20mA + HART                       │
│ Accuracy: ±0.1%                 Power Supply: 24VDC                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

##### 3.4.0.7 API 端点
```
# 工艺数据 API
GET    /api/process-data/                    # 列表
POST   /api/process-data/                    # 创建
GET    /api/process-data/{id}/               # 详情
PUT    /api/process-data/{id}/               # 更新
DELETE /api/process-data/{id}/               # 删除
GET    /api/tags/{tag_id}/process-data/      # 获取位号的工艺数据
POST   /api/process-data/import/             # 从模拟软件导入
POST   /api/process-data/bulk-update/        # 批量更新

# 管道规格 API
GET    /api/pipe-specifications/             # 列表
POST   /api/pipe-specifications/             # 创建
GET    /api/pipe-specifications/{id}/        # 详情
PUT    /api/pipe-specifications/{id}/        # 更新
DELETE /api/pipe-specifications/{id}/        # 删除
POST   /api/pipe-specifications/import/      # 从 P&ID 导入

# 工艺连接 API
GET    /api/process-connections/             # 列表
POST   /api/process-connections/             # 创建
GET    /api/process-connections/{id}/        # 详情
PUT    /api/process-connections/{id}/        # 更新
DELETE /api/process-connections/{id}/        # 删除
GET    /api/tags/{tag_id}/process-connection/ # 获取位号的连接数据
```

#### 3.4.1 SpecificationTemplate (规格书模板)
```
目的: 定义规格书的布局和字段映射
字段:
  - id: BigAutoField
  - organization: FK -> Organization
  - instrument_type: FK -> InstrumentType
  - name: 模板名称
  - version: 模板版本
  - layout: JSONField (规格书布局定义)
    - sections: 分区定义
    - fields: 字段映射 (数据库字段 -> 规格书位置)
    - styles: 样式定义
  - is_active: 是否激活
```

#### 3.4.2 SpecificationDocument (规格书文档)
```
目的: 规格书实例，关联到具体位号
字段:
  - id: BigAutoField
  - tag: FK -> Tag
  - template: FK -> SpecificationTemplate
  - revision: 版本号
  - status: 状态 (Draft/Issued/Superseded)
  - issued_date: 发布日期
  - issued_by: FK -> User
功能:
  - 数据驱动：规格书是数据库的视图，数据变更自动更新
  - PDF 生成：基于模板生成 PDF
  - 版本管理：每次发布生成新版本
```

#### 3.4.3 External Editor 数据交换
```
目的: 与供应商的数据协同
格式: JSON (.oisf - OpenInstrument Spec File)
功能:
  - 导出规格书为 .oisf 文件
  - 供应商填写后导入
  - 导入时验证和差异对比
  - 保留数据安全 (仅导出必要字段)
```

### 3.5 模块 1.5 - 接线模块 (Wiring)

> **SPI 对应**: Wiring Module  
> **Django App**: `wiring`

#### 3.5.1 JunctionBox (接线箱)
```
字段:
  - id: BigAutoField
  - project: FK -> Project
  - name: 接线箱名称
  - code: 接线箱编号
  - location: 安装位置
  - unit: FK -> PlantHierarchy
  - box_type: 类型 (Standard/Explosion-proof/Intrinsically-safe)
  - description: 描述
```

#### 3.5.2 TerminalStrip (端子排)
```
字段:
  - id: BigAutoField
  - junction_box: FK -> JunctionBox
  - name: 端子排名称
  - terminal_count: 端子数量
  - terminal_type: 端子类型
```

#### 3.5.3 Terminal (端子)
```
字段:
  - id: BigAutoField
  - terminal_strip: FK -> TerminalStrip
  - number: 端子号
  - signal_type: 信号类型 (AI/AO/DI/DO/Power/Ground)
  - voltage_rating: 额定电压
  - is_occupied: 是否已占用
```

#### 3.5.4 Cable (电缆)
```
字段:
  - id: BigAutoField
  - project: FK -> Project
  - cable_number: 电缆编号 (如 "IC-FT-101-01")
  - cable_type: 电缆类型 (Instrument/Power/Control/Intrinsically-safe)
  - cable_spec: 电缆规格 (如 "DJYPVP-2×1.5")
  - core_count: 芯数
  - core_size: 芯线截面积 (mm²)
  - shielding: 屏蔽类型 (None/Overall/Individual/Both)
  - armor: 铠装类型 (None/Steel-Wire/Steel-Tape)
  - insulation: 绝缘材料 (PVC/XLPE/PE/FEP)
  - voltage_rating: 额定电压 (V)
  - temperature_rating: 额定温度 (°C)
  - hazardous_area_cert: 防爆认证 (None/Ex-ia/Ex-ib/Ex-d/Ex-e)
  
  # 端到端路径
  - from_equipment: 起点设备/接线箱
  - from_terminal_strip: FK -> TerminalStrip (起点端子排)
  - to_equipment: 终点设备/接线箱
  - to_terminal_strip: FK -> TerminalStrip (终点端子排)
  
  # 长度信息
  - estimated_length: 估算长度 (m)
  - actual_length: 实际长度 (m)
  - spare_length: 预留长度 (m)
  - total_length: 总长度 (m) = actual + spare
  
  # 路由信息
  - routing_path: JSONField (路由路径)
    - segments: [
        { "type": "cable_tray", "name": "CT-01", "length": 50 },
        { "type": "conduit", "name": "C-101", "length": 10 },
        { "type": "junction_box", "name": "JB-01" }
      ]
  
  # 施工信息
  - installation_status: 安装状态 (Not-Started/In-Progress/Installed/Tested/Commissioned)
  - installation_date: 安装日期
  - installed_by: 安装人员/单位
  - test_date: 测试日期
  - test_result: 测试结果 (Pass/Fail/Pending)
  - remarks: 备注
  
  - status: 状态 (Active/Inactive/Deleted)
  - created_at, updated_at: 时间戳
```

#### 3.5.5 CableRoute (电缆路由)
```
目的: 定义电缆敷设路径的物理构件
字段:
  - id: BigAutoField
  - project: FK -> Project
  - name: 路由名称 (如 "CT-01", "C-101")
  - route_type: 路由类型 (CableTray/Conduit/Duct/Direct-Burial)
  - location: 位置描述
  - capacity: 容量 (根数或截面积)
  - used_capacity: 已用容量
  - from_location: 起点位置
  - to_location: 终点位置
  - length: 长度 (m)
```

#### 3.5.6 WiringConnection (接线连接)
```
字段:
  - id: BigAutoField
  - tag: FK -> Tag
  - from_terminal: FK -> Terminal
  - to_terminal: FK -> Terminal
  - cable: FK -> Cable
  - wire_number: 线号
  - core_number: 芯号 (电缆中的第几芯)
  - core_color: 芯线颜色
  - signal_type: 信号类型
功能:
  - 信号流逻辑检查 (防止错误连接)
  - 电压/类型匹配验证
  - 自动生成端子接线图
  - 自动生成电缆表
```

#### 3.5.7 Cable Schedule (电缆清单表)

##### 3.5.7.1 报表内容
```
Cable Schedule 是供仪表安装公司使用的施工文档，包含以下信息：

基本信息列:
  - Cable No.: 电缆编号
  - Cable Type: 电缆类型
  - Cable Spec: 电缆规格 (型号、芯数×截面积)
  - Cores: 芯数
  - Size: 截面积 (mm²)

端到端路径列:
  - From Equipment: 起点设备
  - From Location: 起点位置
  - From Terminal: 起点端子
  - To Equipment: 终点设备
  - To Location: 终点位置
  - To Terminal: 终点端子

长度信息列:
  - Estimated Length: 估算长度 (m)
  - Actual Length: 实际长度 (m)
  - Spare: 预留长度 (m)
  - Total: 总长度 (m)

路由信息列:
  - Routing: 路由路径 (如 "CT-01 → JB-01 → C-101")
  - Cable Tray: 电缆桥架
  - Conduit: 穿线管

施工信息列:
  - Status: 安装状态
  - Install Date: 安装日期
  - Test Result: 测试结果
  - Remarks: 备注
```

##### 3.5.7.2 Cable Schedule API
```
GET /api/wiring/cable-schedule/
  Query 参数:
    - project_id: 项目 ID (必填)
    - unit_id: 按 Unit 过滤
    - cable_type: 按电缆类型过滤
    - status: 按安装状态过滤
    - from_equipment: 按起点设备过滤
    - to_equipment: 按终点设备过滤
  Response: {
    "count": 150,
    "results": [
      {
        "cable_number": "IC-FT-101-01",
        "cable_type": "Instrument",
        "cable_spec": "DJYPVP-2×1.5",
        "core_count": 2,
        "core_size": 1.5,
        "from_equipment": "FT-101",
        "from_location": "Field",
        "from_terminal": "JB-01/TS-01/1",
        "to_equipment": "MCC-01",
        "to_location": "Control Room",
        "to_terminal": "TB-01/1",
        "estimated_length": 120,
        "actual_length": 125,
        "spare_length": 5,
        "total_length": 130,
        "routing": "CT-01 → JB-01 → CT-02",
        "status": "Installed",
        "test_result": "Pass"
      }
    ]
  }

POST /api/wiring/cable-schedule/export/
  Body: {
    "project_id": 1,
    "format": "excel" | "pdf",
    "filters": { ... },
    "columns": ["cable_number", "cable_spec", "from_equipment", ...],
    "sort_by": "cable_number",
    "include_summary": true
  }
  Response: {
    "download_url": "/api/downloads/{file_id}/",
    "filename": "Cable_Schedule_Project_ETH100_2025-12-12.xlsx"
  }
```

##### 3.5.7.3 Cable Schedule 报表模板
```
CableScheduleTemplate 模型:
  - id: BigAutoField
  - organization: FK -> Organization
  - name: 模板名称 (如 "标准电缆清单", "施工用电缆表")
  - columns: JSONField (列配置)
    - [
        { "field": "cable_number", "header": "Cable No.", "width": 15 },
        { "field": "cable_spec", "header": "Specification", "width": 20 },
        { "field": "from_equipment", "header": "From", "width": 15 },
        { "field": "to_equipment", "header": "To", "width": 15 },
        { "field": "total_length", "header": "Length (m)", "width": 10 }
      ]
  - grouping: 分组方式 (None/ByUnit/ByCableType/ByRoute)
  - include_summary: 是否包含汇总
  - header_template: 表头模板
  - footer_template: 表尾模板
```

##### 3.5.7.4 Cable Schedule 汇总统计
```
GET /api/wiring/cable-schedule/summary/
  Query: project_id=1
  Response: {
    "total_cables": 150,
    "total_length": 18500,
    "by_type": {
      "Instrument": { "count": 100, "length": 12000 },
      "Power": { "count": 30, "length": 4500 },
      "Control": { "count": 20, "length": 2000 }
    },
    "by_status": {
      "Not-Started": 50,
      "In-Progress": 30,
      "Installed": 60,
      "Tested": 10
    },
    "by_spec": {
      "DJYPVP-2×1.5": { "count": 80, "length": 9600 },
      "DJYPVP-4×1.5": { "count": 20, "length": 2400 }
    }
  }
```

##### 3.5.7.5 施工进度跟踪
```
功能:
  - 按电缆状态统计施工进度
  - 甘特图显示安装计划
  - 测试结果记录和报告
  - 施工问题跟踪

CableInstallationLog 模型:
  - id: BigAutoField
  - cable: FK -> Cable
  - action: 操作类型 (Pulled/Terminated/Tested/Commissioned)
  - action_date: 操作日期
  - performed_by: 执行人
  - notes: 备注
  - attachments: 附件 (照片、测试报告)
```

### 3.6 模块 1.6 - 回路图生成 (Loop Drawings)

> **SPI 对应**: Enhanced SmartLoop (ESL)  
> **Django App**: `loop_drawings`

#### 3.6.1 SymbolLibrary (符号库)
```
字段:
  - id: BigAutoField
  - organization: FK -> Organization
  - name: 符号名称
  - code: 符号代码
  - category: 类别 (Transmitter/Valve/Switch/Junction 等)
  - svg_content: SVG 图形内容
  - connection_points: JSONField (连接点定义)
  - macros: JSONField (宏定义 - 数据填充位置)
```

#### 3.6.2 LoopDrawingTemplate (回路图模板)
```
字段:
  - id: BigAutoField
  - organization: FK -> Organization
  - name: 模板名称
  - loop_type: 回路类型 (Flow/Temperature/Pressure/Level)
  - layout_rules: JSONField (布局规则)
  - symbol_mapping: JSONField (仪表类型 -> 符号映射)
```

#### 3.6.3 回路图生成引擎
```
技术: React Flow + 后端规则引擎
功能:
  - 不存储图纸文件，存储"绘图逻辑"
  - 实时读取接线数据和仪表属性
  - 调用符号库动态生成图纸
  - 宏自动填充 (端子号、线号、设备型号)
  - 数据库更新 -> 图纸自动更新
  - 导出为 PDF/DWG/DXF/SVG
```

#### 3.6.4 图纸导出规格

##### 3.6.4.1 导出格式支持
```
| 格式 | 用途 | 技术方案 |
|------|------|----------|
| PDF  | 打印、分发、归档 | WeasyPrint / ReportLab |
| DWG  | AutoCAD 交互 | ezdxf + ODA File Converter |
| DXF  | CAD 通用交换格式 | ezdxf (Python 库) |
| SVG  | Web 显示、矢量编辑 | 前端直接导出 |
| PNG  | 快速预览 | html2canvas |
```

##### 3.6.4.2 DWG/DXF 导出技术方案
```
核心库: ezdxf (Python)
  - 开源、纯 Python 实现
  - 支持 DXF R12 到 R2018
  - 支持图层、块、标注、填充等 CAD 元素

DWG 转换: ODA File Converter (免费工具)
  - DXF → DWG 格式转换
  - 支持 AutoCAD 2000-2024 版本
  - 命令行调用，可集成到后端

导出流程:
  1. 前端请求导出 (POST /api/loop-drawings/{id}/export/)
  2. 后端读取回路数据 (Loop + Tags + Wiring + Symbols)
  3. 调用 ezdxf 生成 DXF 文件
  4. (可选) 调用 ODA Converter 转换为 DWG
  5. 返回文件下载链接
```

##### 3.6.4.3 DXF 图层规划
```
图层结构 (遵循 CAD 标准):
  - 0-BORDER          # 图框
  - 1-TITLE           # 标题栏
  - 2-INSTRUMENTS     # 仪表符号
  - 3-WIRING          # 接线连接
  - 4-CABLES          # 电缆
  - 5-TERMINALS       # 端子
  - 6-ANNOTATIONS     # 标注文字
  - 7-DIMENSIONS      # 尺寸标注

颜色规范:
  - 仪表符号: 白色 (7)
  - 信号线: 青色 (4)
  - 电源线: 红色 (1)
  - 接地线: 绿色 (3)
  - 标注文字: 黄色 (2)
```

##### 3.6.4.4 符号库 DXF 映射
```
SymbolLibrary 扩展字段:
  - dxf_block: TextField (DXF 块定义代码)
  - dxf_attributes: JSONField (属性标签定义)
    - TAG_NUMBER: 位号
    - SERVICE: 服务描述
    - RANGE: 量程
    - MANUFACTURER: 制造商

符号转换流程:
  SVG 符号 → DXF 块 (Block)
  连接点 → 属性插入点 (Attribute)
  宏定义 → 属性标签 (Attribute Tag)
```

##### 3.6.4.5 导出 API
```
POST /api/loop-drawings/{id}/export/
  Body: {
    "format": "dwg" | "dxf" | "pdf" | "svg",
    "paper_size": "A3" | "A4" | "A1",
    "scale": "1:1" | "1:2" | "1:5",
    "include_title_block": true,
    "include_revision_history": true,
    "dwg_version": "2018" | "2013" | "2010" | "2007"
  }
  Response: {
    "success": true,
    "download_url": "/api/downloads/{file_id}/",
    "expires_at": "2025-12-12T20:00:00Z"
  }

GET /api/downloads/{file_id}/
  Response: 文件流 (Content-Disposition: attachment)
```

##### 3.6.4.6 批量导出
```
POST /api/loop-drawings/batch-export/
  Body: {
    "loop_ids": [1, 2, 3, 4, 5],
    "format": "dwg",
    "package_type": "zip" | "individual"
  }
  Response: {
    "job_id": "abc123",
    "status": "processing"
  }

GET /api/export-jobs/{job_id}/
  Response: {
    "status": "completed",
    "download_url": "/api/downloads/{file_id}/",
    "files": [
      { "name": "LOOP-FT-101.dwg", "size": 125000 },
      { "name": "LOOP-TT-102.dwg", "size": 118000 }
    ]
  }
```

##### 3.6.4.7 图框模板
```
TitleBlockTemplate 模型:
  - id: BigAutoField
  - organization: FK -> Organization
  - name: 模板名称 (如 "A3 横向标准图框")
  - paper_size: 纸张尺寸 (A0/A1/A2/A3/A4)
  - orientation: 方向 (Landscape/Portrait)
  - dxf_template: TextField (DXF 图框定义)
  - field_mapping: JSONField (字段映射)
    - PROJECT_NAME: 项目名称
    - DRAWING_NUMBER: 图号
    - REVISION: 版本
    - DATE: 日期
    - DRAWN_BY: 绘制人
    - CHECKED_BY: 审核人
    - APPROVED_BY: 批准人
```

### 3.7 模块 1.7 - 规则管理器 (Rule Manager)

> **SPI 对应**: Rule Manager  
> **Django App**: `rules_engine`

#### 3.7.1 Rule (业务规则)
```
字段:
  - id: BigAutoField
  - organization: FK -> Organization
  - project: FK -> Project (可选，项目级规则)
  - name: 规则名称
  - description: 规则描述
  - entity_type: 应用实体 (TAG/LOOP/CABLE 等)
  - condition: JSONField (IF 条件)
    - field: 字段名
    - operator: 操作符 (equals/contains/greater_than 等)
    - value: 比较值
  - action: JSONField (THEN 动作)
    - type: 动作类型 (REQUIRE/SET_DEFAULT/VALIDATE/WARN)
    - target_field: 目标字段
    - value: 设置值或验证规则
  - priority: 优先级
  - is_active: 是否启用
示例:
  - IF 服务介质 = "氧气" THEN 接液材质 MUST IN ["蒙乃尔", "脱脂不锈钢"]
  - IF 仪表类型 = "PSV" THEN 必须填写 "设定压力"
```

#### 3.7.2 RuleExecution (规则执行记录)
```
字段:
  - id: BigAutoField
  - rule: FK -> Rule
  - entity_type: 实体类型
  - entity_id: 实体 ID
  - triggered_at: 触发时间
  - result: 执行结果 (PASS/FAIL/WARN)
  - message: 结果消息
功能:
  - 规则驻留在数据库层
  - 界面录入和批量导入都会触发
  - 确保设计符合工程规范 (包括 GB 标准)
```

### 3.8 模块 1.8 - 版本控制 (Version Control)

> **SPI 对应**: Revision Management + Audit Trail  
> **Django App**: `revisions`, `audit`

#### 3.8.1 GlobalRevision (全局修订)
```
目的: 项目里程碑版本管理
字段:
  - id: BigAutoField
  - project: FK -> Project
  - revision_code: 版本号 (如 "Rev 0", "Rev A", "IFC")
  - description: 版本描述
  - created_by: FK -> User
  - created_at: 创建时间
  - status: 状态 (Draft/Issued/Superseded)
功能:
  - 批量应用版本号到所有选定文档
  - 自动更新图纸标题栏
```

#### 3.8.2 EntityRevision (实体版本历史)
```
目的: 记录任何实体的完整变更历史 (通用版本模型)
字段:
  - id: BigAutoField
  - content_type: FK -> ContentType (Django 通用外键)
  - object_id: 对象 ID
  - revision_number: 版本号
  - global_revision: FK -> GlobalRevision (可选)
  - data_snapshot: JSONField (完整数据快照)
  - change_type: CREATE | UPDATE | DELETE | RESTORE
  - change_summary: 变更摘要
  - changed_by: FK -> User
  - changed_at: 变更时间
功能:
  - 归档 (Archiving): 保存数据快照
  - 版本对比: 字段级差异对比
  - 版本回滚: 恢复到历史版本
```

#### 3.8.3 AuditLog (审计日志)
```
目的: 记录所有数据操作 (Who/When/What)
字段:
  - id: UUID
  - organization: FK -> Organization
  - project: FK -> Project (可选)
  - user: FK -> User
  - action: CREATE | READ | UPDATE | DELETE
  - model_name: 操作的模型名
  - object_id: 操作的对象 ID
  - object_repr: 对象字符串表示
  - old_values: JSONField (变更前的值)
  - new_values: JSONField (变更后的值)
  - changed_fields: JSONField (变更字段列表)
  - change_details: JSONField (详细变更记录)
  - ip_address: 操作 IP
  - user_agent: 浏览器信息
  - timestamp: 操作时间
功能:
  - 自动记录 (中间件/信号)
  - 细粒度变更历史
  - 支持 PSM (过程安全管理) 和 MOC (变更管理)
```

#### 3.8.4 变更标记详细规格

##### 3.8.4.1 change_details 数据结构
```json
{
  "changed_fields": ["description", "range_max", "status"],
  "changes": [
    {
      "field": "description",
      "field_label": "描述",
      "old_value": "Feed Flow Transmitter",
      "new_value": "Feed Flow Transmitter (Revised)",
      "change_type": "modified"
    },
    {
      "field": "range_max",
      "field_label": "量程上限",
      "old_value": 100,
      "new_value": 150,
      "change_type": "modified",
      "change_percent": 50.0
    },
    {
      "field": "status",
      "field_label": "状态",
      "old_value": "ACTIVE",
      "new_value": "UNDER_REVIEW",
      "change_type": "modified"
    }
  ],
  "summary": {
    "total_fields_changed": 3,
    "fields_added": 0,
    "fields_removed": 0,
    "fields_modified": 3
  }
}
```

##### 3.8.4.2 变更类型 (change_type)
```
| 类型 | 说明 | 示例 |
|------|------|------|
| added | 新增字段值 | 空值 → 有值 |
| removed | 删除字段值 | 有值 → 空值 |
| modified | 修改字段值 | 旧值 → 新值 |
| unchanged | 未变更 | 用于完整记录 |
```

##### 3.8.4.3 变更追踪 API
```
GET /api/audit/{model}/{id}/changes/
  Query:
    - from_date: 开始日期
    - to_date: 结束日期
    - field: 指定字段 (可选)
    - user_id: 指定用户 (可选)
  Response: {
    "object": { "id": 1, "tag_number": "FT-101" },
    "change_history": [
      {
        "timestamp": "2025-12-12T10:30:00Z",
        "user": "张三",
        "action": "UPDATE",
        "changed_fields": ["description", "range_max"],
        "changes": [...]
      },
      {
        "timestamp": "2025-12-11T14:20:00Z",
        "user": "李四",
        "action": "UPDATE",
        "changed_fields": ["status"],
        "changes": [...]
      }
    ]
  }

GET /api/audit/{model}/{id}/field-history/{field_name}/
  目的: 获取单个字段的完整变更历史
  Response: {
    "field": "range_max",
    "field_label": "量程上限",
    "current_value": 150,
    "history": [
      { "value": 150, "changed_at": "2025-12-12T10:30:00Z", "changed_by": "张三" },
      { "value": 100, "changed_at": "2025-12-10T09:00:00Z", "changed_by": "李四" },
      { "value": 80, "changed_at": "2025-12-01T08:00:00Z", "changed_by": "王五" }
    ]
  }
```

##### 3.8.4.4 前端变更标记 UI
```
功能:
  1. 变更高亮显示
     - 新增字段: 绿色背景 + "NEW" 标签
     - 修改字段: 黄色背景 + "MODIFIED" 标签
     - 删除字段: 红色背景 + 删除线

  2. 变更指示器
     - 字段旁显示变更图标 (🔄)
     - 悬停显示: "由 张三 于 2025-12-12 10:30 修改"
     - 点击显示完整变更历史

  3. 变更对比视图
     - 左右对比: 旧值 | 新值
     - 差异高亮: 文本差异用颜色标记
     - 时间线视图: 按时间顺序显示所有变更

  4. 批量变更报告
     - 导入后显示所有变更的记录
     - 按变更类型分组 (新增/修改/删除)
     - 支持导出变更报告 (Excel/PDF)
```

##### 3.8.4.5 变更通知
```
ChangeNotification 模型:
  - id: BigAutoField
  - audit_log: FK -> AuditLog
  - recipients: M2M -> User (通知接收人)
  - notification_type: 通知类型 (Email/InApp/Both)
  - is_sent: 是否已发送
  - sent_at: 发送时间

触发规则:
  - 关键字段变更自动通知 (如 status, range_max)
  - 可配置通知规则 (按字段、按用户、按项目)
  - 支持订阅特定记录的变更
```

##### 3.8.4.6 变更审批流程 (可选)
```
适用场景: 关键数据变更需要审批

ChangeRequest 模型:
  - id: BigAutoField
  - model_name: 模型名
  - object_id: 对象 ID
  - requested_changes: JSONField (请求的变更)
  - requester: FK -> User
  - approver: FK -> User (可选)
  - status: Pending | Approved | Rejected
  - reason: 变更原因
  - approval_comment: 审批意见
  - created_at, approved_at: 时间戳

流程:
  1. 用户提交变更请求
  2. 系统通知审批人
  3. 审批人批准/拒绝
  4. 批准后自动应用变更并记录审计日志
```

#### 3.8.5 RevisionComparison (版本对比)
```
功能:
  - 数据级差异: 具体列出哪个字段变了
  - 视觉标记: 高亮显示差异
  - 增强报表对比: 规格书/回路图前后版本对比
API:
  - GET /api/revisions/{entity_type}/{id}/compare/?from=1&to=2
  - 返回字段级差异列表
  
Response 示例:
{
  "from_revision": 1,
  "to_revision": 2,
  "from_date": "2025-12-10T09:00:00Z",
  "to_date": "2025-12-12T10:30:00Z",
  "differences": [
    {
      "field": "description",
      "field_label": "描述",
      "from_value": "Feed Flow Transmitter",
      "to_value": "Feed Flow Transmitter (Revised)",
      "change_type": "modified"
    },
    {
      "field": "range_max",
      "field_label": "量程上限",
      "from_value": 100,
      "to_value": 150,
      "change_type": "modified",
      "change_percent": 50.0
    }
  ],
  "summary": {
    "total_differences": 2,
    "added": 0,
    "removed": 0,
    "modified": 2
  }
}
```

---

## 3.9 国际化 (Internationalization - i18n)

### 3.9.1 设计原则
```
1. 英语为主语言 (Primary Language)
   - 系统默认语言为英语 (en-US)
   - 所有 UI 文本、标签、消息的源代码使用英语
   - 英语环境下必须显示纯英语界面，无任何其他语言混杂

2. 多语言支持
   - 用户可在设置中切换语言
   - 支持的语言:
     - 东亚语言: English (en), 简体中文 (zh-CN), 繁體中文 (zh-TW), 日本語 (ja), 한국어 (ko)
     - 欧洲语言: Français (fr), Español (es), Italiano (it), Deutsch (de), Русский (ru)
     - RTL 语言: العربية (ar), עברית (he)
   - 语言切换后立即生效，无需刷新页面
   - RTL 语言自动切换布局方向

3. 翻译范围
   - UI 文本: 按钮、标签、菜单、提示信息
   - 系统消息: 错误消息、成功提示、确认对话框
   - 报表标题: 报表和导出文件的标题和表头
   - 帮助文档: 用户帮助和文档

4. 不翻译的内容
   - 用户输入的数据 (位号、描述、备注等)
   - 技术术语和缩写 (如 AI, AO, DI, DO, RTD, TC)
   - 行业标准代码 (如 FT, TT, PT, CV)
   - API 响应中的字段名
```

### 3.9.2 技术实现

#### 后端 (Django)
```python
# settings.py
LANGUAGE_CODE = 'en-us'  # 默认语言: 英语
USE_I18N = True
USE_L10N = True

LANGUAGES = [
    ('en', 'English'),
    ('zh-hans', '简体中文'),
    ('zh-hant', '繁體中文'),
    ('ja', '日本語'),
    ('ko', '한국어'),
    ('fr', 'Français'),
    ('es', 'Español'),
    ('it', 'Italiano'),
    ('de', 'Deutsch'),
    ('ru', 'Русский'),
    ('ar', 'العربية'),
    ('he', 'עברית'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# 中间件
MIDDLEWARE = [
    ...
    'django.middleware.locale.LocaleMiddleware',
    ...
]

# API 响应消息国际化
from django.utils.translation import gettext_lazy as _

class Tag(models.Model):
    class Meta:
        verbose_name = _("Instrument Tag")
        verbose_name_plural = _("Instrument Tags")
```

#### 前端 (React + react-i18next)
```typescript
// i18n/config.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',  // 默认回退到英语
    defaultNS: 'common',
    interpolation: {
      escapeValue: false,
    },
    resources: {
      en: { ... },
      'zh-CN': { ... },
      'zh-TW': { ... },
      ja: { ... },
      ko: { ... },
      fr: { ... },
      es: { ... },
      it: { ... },
      de: { ... },
      ru: { ... },
      ar: { ... },
      he: { ... },
    },
  });

// 使用示例
import { useTranslation } from 'react-i18next';

function InstrumentIndex() {
  const { t } = useTranslation();
  return (
    <div>
      <h1>{t('instrumentIndex.title')}</h1>
      <button>{t('common.save')}</button>
    </div>
  );
}
```

### 3.9.3 翻译文件结构
```
locale/
├── en/                          # English (主语言)
│   └── LC_MESSAGES/
│       └── django.po
├── zh_Hans/                     # 简体中文
│   └── LC_MESSAGES/
│       └── django.po
├── zh_Hant/                     # 繁體中文
├── ja/                          # 日本語
├── ko/                          # 한국어
├── fr/                          # Français
├── es/                          # Español
├── it/                          # Italiano
├── de/                          # Deutsch
├── ru/                          # Русский
├── ar/                          # العربية (RTL)
└── he/                          # עברית (RTL)

frontend/src/i18n/
├── locales/
│   ├── en/
│   │   ├── common.json          # 通用文本
│   │   ├── instrumentIndex.json # 仪表索引
│   │   ├── wiring.json          # 接线管理
│   │   ├── loopDrawing.json     # 回路图
│   │   └── errors.json          # 错误消息
│   ├── zh-CN/
│   │   ├── common.json
│   │   └── ...
│   ├── fr/                      # Français
│   ├── es/                      # Español
│   ├── it/                      # Italiano
│   ├── de/                      # Deutsch
│   ├── ru/                      # Русский
│   ├── ar/                      # العربية (RTL)
│   ├── he/                      # עברית (RTL)
│   └── ...
└── config.ts
```

### 3.9.4 RTL (Right-to-Left) 语言支持
```
目的: 支持阿拉伯语和希伯来语等从右到左书写的语言

RTL 语言列表:
  - ar: العربية (阿拉伯语)
  - he: עברית (希伯来语)

技术实现:

1. HTML 方向属性
   - 检测当前语言是否为 RTL
   - 动态设置 <html dir="rtl"> 或 <html dir="ltr">

2. CSS 逻辑属性 (推荐)
   使用逻辑属性替代物理属性:
   - margin-left → margin-inline-start
   - margin-right → margin-inline-end
   - padding-left → padding-inline-start
   - padding-right → padding-inline-end
   - text-align: left → text-align: start
   - text-align: right → text-align: end
   - left → inset-inline-start
   - right → inset-inline-end

3. Tailwind CSS RTL 支持
   // tailwind.config.js
   module.exports = {
     plugins: [
       require('tailwindcss-rtl'),
     ],
   }
   
   // 使用示例
   <div className="ms-4 me-2">  // margin-start, margin-end
   <div className="ps-4 pe-2">  // padding-start, padding-end
   <div className="text-start"> // 文本对齐

4. React 组件适配
   // hooks/useDirection.ts
   import { useTranslation } from 'react-i18next';
   
   const RTL_LANGUAGES = ['ar', 'he'];
   
   export function useDirection() {
     const { i18n } = useTranslation();
     const isRTL = RTL_LANGUAGES.includes(i18n.language);
     return { isRTL, direction: isRTL ? 'rtl' : 'ltr' };
   }
   
   // App.tsx
   function App() {
     const { direction } = useDirection();
     useEffect(() => {
       document.documentElement.dir = direction;
       document.documentElement.lang = i18n.language;
     }, [direction]);
     return <RouterProvider router={router} />;
   }

5. 图标和箭头翻转
   - 导航箭头 (← →) 需要在 RTL 模式下翻转
   - 使用 CSS transform: scaleX(-1) 或条件渲染
   - 某些图标不应翻转 (如播放按钮、时钟)

6. 表格和数据网格
   - 列顺序在 RTL 模式下自动反转
   - 滚动条位置调整
   - 排序图标方向调整
```

### 3.9.5 翻译键命名规范
```json
// en/common.json (英语 - 主语言)
{
  "app": {
    "name": "OpenInstrument",
    "tagline": "Enterprise Instrument Engineering System"
  },
  "nav": {
    "dashboard": "Dashboard",
    "instruments": "Instruments",
    "wiring": "Wiring",
    "loopDrawings": "Loop Drawings",
    "settings": "Settings"
  },
  "actions": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "create": "Create",
    "export": "Export",
    "import": "Import",
    "search": "Search",
    "filter": "Filter",
    "refresh": "Refresh"
  },
  "messages": {
    "saveSuccess": "Saved successfully",
    "deleteConfirm": "Are you sure you want to delete this item?",
    "unsavedChanges": "You have unsaved changes. Do you want to leave?"
  },
  "errors": {
    "required": "This field is required",
    "invalidFormat": "Invalid format",
    "networkError": "Network error. Please try again.",
    "unauthorized": "You are not authorized to perform this action"
  }
}

// zh-CN/common.json (简体中文)
{
  "app": {
    "name": "OpenInstrument",
    "tagline": "企业级仪表工程设计系统"
  },
  "nav": {
    "dashboard": "仪表盘",
    "instruments": "仪表管理",
    "wiring": "接线管理",
    "loopDrawings": "回路图",
    "settings": "设置"
  },
  "actions": {
    "save": "保存",
    "cancel": "取消",
    "delete": "删除",
    "edit": "编辑",
    "create": "新建",
    "export": "导出",
    "import": "导入",
    "search": "搜索",
    "filter": "筛选",
    "refresh": "刷新"
  },
  "messages": {
    "saveSuccess": "保存成功",
    "deleteConfirm": "确定要删除此项吗？",
    "unsavedChanges": "您有未保存的更改，确定要离开吗？"
  },
  "errors": {
    "required": "此字段为必填项",
    "invalidFormat": "格式无效",
    "networkError": "网络错误，请重试",
    "unauthorized": "您无权执行此操作"
  }
}
```

### 3.9.5 用户语言设置

#### UserPreference 模型扩展
```python
class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    language = models.CharField(
        max_length=10,
        choices=[
            ('en', 'English'),
            ('zh-hans', '简体中文'),
            ('zh-hant', '繁體中文'),
            ('ja', '日本語'),
            ('ko', '한국어'),
        ],
        default='en'  # 默认英语
    )
    timezone = models.CharField(max_length=50, default='UTC')
    date_format = models.CharField(max_length=20, default='YYYY-MM-DD')
    number_format = models.CharField(max_length=20, default='1,234.56')
```

#### 语言切换 API
```
GET /api/user/preferences/
  Response: { "language": "en", "timezone": "UTC", ... }

PATCH /api/user/preferences/
  Body: { "language": "zh-hans" }
  Response: { "language": "zh-hans", ... }
  Effect: 立即切换用户界面语言
```

### 3.9.6 语言切换 UI
```
位置: 顶部导航栏右侧 或 用户设置页面

┌─────────────────────────────────────────────────────────────────┐
│ ... | 🌐 English ▼ | 🔔 | 👤 User                               │
│     ├─────────────────┤                                         │
│     │ ✓ English       │                                         │
│     │   简体中文       │                                         │
│     │   繁體中文       │                                         │
│     │   日本語         │                                         │
│     │   한국어         │                                         │
│     └─────────────────┘                                         │
└─────────────────────────────────────────────────────────────────┘

交互:
  - 点击当前语言显示下拉菜单
  - 选择语言后立即切换，无需刷新
  - 语言设置保存到用户偏好
  - 未登录用户使用浏览器语言或默认英语
```

### 3.9.7 日期/数字本地化
```
日期格式:
  - en: MM/DD/YYYY (12/12/2025)
  - zh-CN: YYYY-MM-DD (2025-12-12)
  - ja: YYYY年MM月DD日 (2025年12月12日)

数字格式:
  - en: 1,234.56
  - zh-CN: 1,234.56
  - de: 1.234,56

货币格式:
  - en-US: $1,234.56
  - zh-CN: ¥1,234.56
  - ja: ¥1,234
```

---

## 4. API 规格

### 4.1 API 设计原则

- RESTful 风格
- 遵循 OpenAPI 3.0 规范
- 统一响应格式
- 分页、过滤、排序支持
- 版本控制 (/api/v1/)
- 国际化支持 (Accept-Language 头)

### 4.2 认证与授权

```
认证方式: JWT (JSON Web Token)
- Access Token: 60 分钟有效期
- Refresh Token: 7 天有效期
- 支持 Token 刷新和黑名单

授权检查:
- Organization 级别: 用户必须属于该组织
- Project 级别: 用户必须有项目访问权限
- Object 级别: 基于角色的 CRUD 权限
```

### 4.3 API 端点规划

```
/api/v1/
├── auth/
│   ├── login/                 # 登录
│   ├── logout/                # 登出
│   ├── refresh/               # 刷新 Token
│   └── me/                    # 当前用户信息
├── organizations/
│   ├── GET, POST              # 列表, 创建
│   └── {id}/                  # 详情, 更新, 删除
├── projects/
│   ├── GET, POST              # 列表, 创建
│   ├── {id}/                  # 详情, 更新, 删除
│   └── {id}/members/          # 项目成员管理
├── engineering/
│   ├── hierarchy/             # 工厂层级
│   │   ├── GET, POST
│   │   ├── {id}/
│   │   ├── tree/              # 树状结构
│   │   └── units/             # 所有 Unit
│   ├── loops/                 # 控制回路
│   │   ├── GET, POST
│   │   ├── {id}/
│   │   └── {id}/tags/         # 回路内的位号
│   ├── instrument-types/      # 仪表类型
│   │   ├── GET, POST
│   │   ├── {id}/
│   │   └── {id}/validate-spec/ # 验证规格数据
│   └── tags/                  # 仪表位号
│       ├── GET, POST
│       ├── {id}/
│       ├── {id}/revisions/    # 版本历史
│       ├── bulk-update/       # 批量更新
│       ├── search/            # 高级搜索
│       ├── export/            # 导出
│       └── import/            # 导入
├── specifications/            # 规格书模块
│   ├── templates/            # 规格书模板
│   ├── documents/            # 规格书文档
│   └── export/               # 导出 (PDF/OISF)
├── wiring/                    # 接线管理
│   ├── junction-boxes/
│   ├── terminal-strips/
│   ├── terminals/
│   ├── cables/
│   └── connections/
├── loop-drawings/             # 回路图生成
│   ├── symbols/              # 符号库
│   ├── templates/            # 回路图模板
│   └── generate/             # 动态生成
├── rules/                     # 规则管理器
│   ├── GET, POST             # 规则 CRUD
│   ├── {id}/
│   └── validate/             # 规则验证
├── revisions/                 # 版本控制
│   ├── global/               # 全局修订
│   ├── {entity_type}/{id}/   # 实体版本历史
│   └── compare/              # 版本对比
└── audit/                     # 审计日志
    ├── logs/                 # 查询日志
    └── export/               # 导出审计报告
```

---

## 5. 前端规格

### 5.1 整体布局架构

#### 5.1.1 主界面布局
```
┌─────────────────────────────────────────────────────────────────────────┐
│  顶部导航栏                                                              │
│  Logo | 项目选择器 [PRJ-2025-001 ▼] | 全局搜索 | 通知 | 用户菜单         │
├─────────┬───────────────────────────────────────────────────────────────┤
│         │  面包屑: 项目 > 中石化 > 镇海炼化 > 乙烯装置 > Unit-100        │
│  侧边栏  ├───────────────────────────────────────────────────────────────┤
│         │                                                               │
│ 📊 仪表盘│                      主工作区                                 │
│ 🏭 层级  │                                                               │
│ 📋 索引  │   ┌─────────────────────────────────────────────────────┐   │
│ 📄 规格书│   │  工具栏                                              │   │
│ 🔌 接线  │   ├─────────────────────────────────────────────────────┤   │
│ 📐 回路图│   │                                                     │   │
│ 📦 电缆  │   │              数据网格 / 表单 / 图形                  │   │
│ ⚙️ 设置  │   │                                                     │   │
│         │   └─────────────────────────────────────────────────────┘   │
│         │                                                               │
│         ├───────────────────────────────────────────────────────────────┤
│         │  详情面板 (可折叠): 选中项的详细信息 / 关联数据                │
└─────────┴───────────────────────────────────────────────────────────────┘
```

#### 5.1.2 层级导航树 (Hierarchy Navigator)
```
目的: 在侧边栏或专用面板中显示完整的项目层级结构

层级树结构:
┌─────────────────────────────────────┐
│ 🔍 搜索层级...                       │
├─────────────────────────────────────┤
│ 📁 PRJ-2025-001 (100万吨乙烯项目)   │
│ └── 🏢 中石化 (Client)              │
│     ├── 📍 镇海炼化 (Site)          │
│     │   ├── 🏭 乙烯装置 (Plant)     │
│     │   │   ├── 📂 裂解区 (Area)    │
│     │   │   │   ├── 📦 Unit-100 ✓  │ ← 当前选中
│     │   │   │   │   ├── 📋 仪表 (45)│
│     │   │   │   │   ├── 🔄 回路 (12)│
│     │   │   │   │   └── 🔌 接线箱   │
│     │   │   │   └── 📦 Unit-110    │
│     │   │   └── 📂 分离区 (Area)    │
│     │   │       ├── 📦 Unit-200    │
│     │   │       └── 📦 Unit-210    │
│     │   └── 🏭 公用工程 (Plant)     │
│     │       └── 📂 循环水 (Area)    │
│     └── 📍 茂名石化 (Site)          │
│         └── ...                     │
├─────────────────────────────────────┤
│ 🔧 现场设备                          │
│ ├── 📦 接线箱 (JB)                  │
│ │   ├── JB-01 (Unit-100)           │
│ │   └── JB-02 (Unit-200)           │
│ ├── 📦 RIO 盘柜                     │
│ │   ├── RIO-01 (裂解区)            │
│ │   └── RIO-02 (分离区)            │
│ └── 📦 控制室                       │
│     ├── DCS Cabinet                │
│     └── SIS Cabinet                │
└─────────────────────────────────────┘

交互:
  - 点击节点: 展开/折叠子节点
  - 双击节点: 导航到该层级的数据视图
  - 右键菜单: 新建子节点、编辑、删除
  - 拖拽: 调整层级顺序
  - 数字徽章: 显示子项数量
```

### 5.2 页面结构 (路由)

```
/                                      # 重定向到 /projects
/login                                 # 登录页
/projects                              # 项目列表 (选择工程项目)
/projects/{project_no}                 # 项目仪表盘 (概览)
│
├── /hierarchy                         # 层级管理 (Client/Site/Plant/Area/Unit)
│   ├── /clients                       # 客户管理
│   ├── /sites                         # 厂区管理
│   ├── /plants                        # 装置管理
│   └── /units                         # 单元管理
│
├── /instruments                       # 仪表管理
│   ├── /tags                          # 仪表索引表 ★核心页面
│   ├── /tags/{tag_number}             # 位号详情/规格书
│   ├── /loops                         # 回路管理
│   ├── /loops/{loop_number}           # 回路详情/回路图
│   └── /specifications                # 规格书列表
│
├── /wiring                            # 接线管理
│   ├── /junction-boxes                # 接线箱管理
│   ├── /rio-panels                    # RIO 盘柜管理
│   ├── /cabinets                      # 控制柜管理
│   ├── /cables                        # 电缆管理
│   ├── /cable-schedule                # 电缆表
│   └── /wiring-paths                  # 接线路径
│
├── /drawings                          # 图纸管理
│   ├── /pids                          # P&ID 列表
│   ├── /loop-drawings                 # 回路图列表
│   └── /wiring-diagrams               # 接线图列表
│
├── /reports                           # 报表中心
│   ├── /instrument-index              # 仪表索引报表
│   ├── /cable-schedule                # 电缆表报表
│   └── /io-list                       # I/O 清单
│
└── /settings                          # 项目设置
    ├── /instrument-types              # 仪表类型库
    ├── /naming-conventions            # 命名规则
    ├── /templates                     # 模板管理
    └── /users                         # 用户权限

/admin                                 # 系统管理 (超级管理员)
├── /organizations                     # 租户管理
└── /system-settings                   # 系统配置
```

### 5.3 层级上下文切换

#### 5.3.1 上下文选择器 (Context Selector)
```
目的: 快速切换当前工作的层级范围

位置: 顶部导航栏或工具栏

┌─────────────────────────────────────────────────────────────────┐
│ 当前上下文:                                                      │
│ [PRJ-2025-001 ▼] > [中石化 ▼] > [镇海炼化 ▼] > [乙烯装置 ▼] > [Unit-100 ▼] │
└─────────────────────────────────────────────────────────────────┘

功能:
  - 每个下拉框可独立选择
  - 选择上级会自动过滤下级选项
  - 支持"全部"选项查看所有数据
  - 快捷键: Ctrl+1/2/3/4/5 切换层级
  - 记住用户上次选择的上下文
```

#### 5.3.2 数据过滤联动
```
当用户选择层级上下文时:
  - 仪表索引表: 自动过滤显示该层级下的所有位号
  - 回路列表: 自动过滤显示该层级下的所有回路
  - 接线箱列表: 自动过滤显示该区域的接线箱
  - 电缆列表: 自动过滤显示相关电缆

示例:
  选择 "Unit-100" → 仪表索引表只显示 Unit-100 的位号
  选择 "乙烯装置" → 仪表索引表显示该装置所有 Unit 的位号
  选择 "全部" → 显示整个项目的所有位号
```

### 5.4 核心页面设计

#### 5.4.1 项目仪表盘 (Project Dashboard)
```
┌─────────────────────────────────────────────────────────────────────────┐
│ PRJ-2025-001 - 100万吨乙烯项目                          [编辑] [设置]   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ 📋 仪表总数  │  │ 🔄 回路总数  │  │ 📦 电缆总数  │  │ 📄 规格书   │   │
│  │    1,234    │  │     156     │  │     892     │  │  完成 85%   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                                         │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────┐ │
│  │ 📊 按装置统计                │  │ 📈 最近活动                      │ │
│  │                             │  │                                 │ │
│  │ 乙烯装置    ████████ 856    │  │ • 张三 修改了 FT-101 规格书     │ │
│  │ 公用工程    ████ 378        │  │ • 李四 新增了 10 个位号         │ │
│  │                             │  │ • 王五 完成了 Cable-001 接线    │ │
│  └─────────────────────────────┘  └─────────────────────────────────┘ │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 🏭 项目层级概览                                                  │   │
│  │                                                                 │   │
│  │ 中石化 (Client)                                                 │   │
│  │ └── 镇海炼化 (Site)                                             │   │
│  │     ├── 乙烯装置 (Plant) - 856 仪表, 98 回路                    │   │
│  │     │   ├── 裂解区 (Area) - 4 Units                            │   │
│  │     │   └── 分离区 (Area) - 3 Units                            │   │
│  │     └── 公用工程 (Plant) - 378 仪表, 58 回路                    │   │
│  │         └── 循环水 (Area) - 2 Units                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 5.4.2 仪表索引表 (Instrument Index) ★核心页面
```
┌─────────────────────────────────────────────────────────────────────────┐
│ 仪表索引表                                    上下文: [Unit-100 ▼]      │
├─────────────────────────────────────────────────────────────────────────┤
│ 工具栏                                                                   │
│ [+ 新建] [📥 导入] [📤 导出] [🔄 刷新] | 筛选: [类型 ▼] [状态 ▼] [回路 ▼] │
│ 视图: [表格] [卡片] [分组] | 已选: 5 项 [批量编辑] [批量删除]            │
├─────────────────────────────────────────────────────────────────────────┤
│ ☐ │ 位号 ▲    │ 描述          │ 类型   │ 回路    │ 状态   │ 操作       │
├───┼───────────┼───────────────┼────────┼─────────┼────────┼────────────┤
│ ☐ │ FT-101    │ Feed Flow     │ FT     │ FC-101  │ ✅ 活跃 │ [📄][✏️][🔗]│
│ ☐ │ FV-101    │ Feed Valve    │ CV     │ FC-101  │ ✅ 活跃 │ [📄][✏️][🔗]│
│ ☑ │ TT-102 🔄 │ Reactor Temp  │ TT     │ TC-102  │ 🔄 修改 │ [📄][✏️][🔗]│
│ ☑ │ PT-103    │ Outlet Press  │ PT     │ -       │ 📋 待审 │ [📄][✏️][🔗]│
├───┴───────────┴───────────────┴────────┴─────────┴────────┴────────────┤
│ 显示 1-50 / 共 45 条 | [◀ 上一页] [1] [下一页 ▶]                        │
└─────────────────────────────────────────────────────────────────────────┘

右侧详情面板 (选中 FT-101 时):
┌─────────────────────────┐
│ FT-101 - Feed Flow      │
├─────────────────────────┤
│ 📍 位置                  │
│   Client: 中石化        │
│   Site: 镇海炼化        │
│   Plant: 乙烯装置       │
│   Unit: Unit-100        │
├─────────────────────────┤
│ 📊 基本信息              │
│   类型: Flow Transmitter│
│   回路: FC-101          │
├─────────────────────────┤
│ 🔌 接线路径              │
│   FT-101                │
│   ↓ IC-FT-101-01        │
│   JB-01 (TS-01/1-2)     │
│   ↓ IC-FT-101-02        │
│   RIO-01 (AI-001/CH01)  │
│   ↓ Fieldbus            │
│   DCS (CPU-01)          │
├─────────────────────────┤
│ 📄 规格书 [打开]         │
│ 📐 回路图 [查看]         │
│ 📝 变更历史 [展开]       │
└─────────────────────────┘
```

#### 5.4.3 接线路径视图 (Wiring Path View)
```
┌─────────────────────────────────────────────────────────────────────────┐
│ 接线路径 - FT-101                                         [编辑] [导出] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐       │
│  │ FT-101  │      │  JB-01  │      │ RIO-01  │      │   DCS   │       │
│  │ (现场)  │      │ (现场)  │      │ (现场)  │      │ (控制室) │       │
│  │         │      │         │      │         │      │         │       │
│  │ ○ 1+    │──────│ TS-01/1 │──────│ AI-001  │      │         │       │
│  │ ○ 1-    │ IC-001│ TS-01/2 │ IC-002│ CH01+  │──FB──│ CPU-01  │       │
│  │ ○ SH    │──────│ TS-01/3 │──────│ CH01-   │      │         │       │
│  └─────────┘      └─────────┘      └─────────┘      └─────────┘       │
│                                                                         │
│  电缆信息:                                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 电缆号      │ 规格         │ 起点      │ 终点      │ 长度  │ 状态 │   │
│  │ IC-001     │ DJYPVP-2×1.5 │ FT-101    │ JB-01     │ 50m   │ ✅   │   │
│  │ IC-002     │ DJYPVP-2×1.5 │ JB-01     │ RIO-01    │ 80m   │ ✅   │   │
│  │ FB-001     │ Fieldbus     │ RIO-01    │ DCS       │ 200m  │ ✅   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 5.4.4 RIO 盘柜管理 (RIO Panel Management)
```
┌─────────────────────────────────────────────────────────────────────────┐
│ RIO 盘柜管理                                  上下文: [裂解区 ▼]        │
├─────────────────────────────────────────────────────────────────────────┤
│ [+ 新建 RIO] [📥 导入 I/O 分配] [📤 导出 I/O 清单]                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ RIO-01 (裂解区)                                    [编辑] [删除] │   │
│  │ 类型: DCS-RIO | 通讯: Profibus | 地址: 01                       │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ I/O 卡件:                                                       │   │
│  │ ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐ │   │
│  │ │ Slot 1  │ Slot 2  │ Slot 3  │ Slot 4  │ Slot 5  │ Slot 6  │ │   │
│  │ │ AI-001  │ AI-002  │ AO-001  │ DI-001  │ DO-001  │ [空]    │ │   │
│  │ │ 8CH     │ 8CH     │ 4CH     │ 16CH    │ 16CH    │         │ │   │
│  │ │ 6/8 用  │ 4/8 用  │ 2/4 用  │ 12/16用 │ 8/16用  │         │ │   │
│  │ └─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘ │   │
│  │                                                                 │   │
│  │ AI-001 通道分配:                                                │   │
│  │ CH01: FT-101 (4-20mA, 0-100 m³/h)                              │   │
│  │ CH02: TT-102 (4-20mA, 0-500 °C)                                │   │
│  │ CH03: PT-103 (4-20mA, 0-10 MPa)                                │   │
│  │ CH04: LT-104 (4-20mA, 0-100 %)                                 │   │
│  │ CH05: FT-105 (4-20mA, 0-50 m³/h)                               │   │
│  │ CH06: TT-106 (4-20mA, 0-300 °C)                                │   │
│  │ CH07: [空闲]                                                    │   │
│  │ CH08: [空闲]                                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ RIO-02 (分离区)                                    [编辑] [删除] │   │
│  │ ...                                                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.5 核心组件

#### 5.5.1 仪表索引表 (Instrument Index)
```
功能:
  - 高性能数据网格 (TanStack Table)
  - 列排序、过滤、分组
  - 行内编辑
  - 批量选择和操作
  - Excel 导入/导出
  - 虚拟滚动 (支持 10000+ 行)
  - 层级上下文过滤
  - 变更标记显示
```

#### 5.5.2 规格书表单 (Specification Sheet)
```
功能:
  - 动态表单 (基于 InstrumentType.schema_template)
  - 表单验证
  - 版本对比
  - 打印/PDF 导出
  - 层级位置显示
```

#### 5.5.3 回路图 (Loop Diagram)
```
功能:
  - 基于 React Flow 自动生成
  - 显示回路内所有仪表
  - 显示信号流向和接线路径
  - 可交互 (点击查看详情)
  - 支持 RIO Panel 节点
```

#### 5.5.4 接线管理器 (Wiring Manager)
```
功能:
  - 拖拽接线
  - 端子分配
  - 电缆管理
  - 接线图生成
  - 支持多种信号路径类型
  - RIO Panel I/O 分配
```

#### 5.5.5 层级导航树 (Hierarchy Navigator)
```
功能:
  - 树形展示项目层级
  - 快速导航和上下文切换
  - 右键菜单操作
  - 拖拽调整顺序
  - 搜索过滤
  - 数量徽章
```

### 5.6 快捷操作

```
快捷键:
  - Ctrl+N: 新建位号
  - Ctrl+S: 保存
  - Ctrl+F: 搜索
  - Ctrl+1~5: 切换层级上下文
  - F2: 编辑选中项
  - Delete: 删除选中项
  - Ctrl+D: 复制选中项

右键菜单:
  - 查看详情
  - 编辑
  - 复制
  - 删除
  - 查看规格书
  - 查看接线路径
  - 查看回路图
  - 查看变更历史
```

---

## 6. 非功能性需求

### 6.1 性能要求

| 指标 | 要求 |
|------|------|
| API 响应时间 | < 200ms (P95) |
| 页面加载时间 | < 3s (首次), < 1s (后续) |
| 并发用户数 | 支持 100+ 并发 |
| 数据量支持 | 单项目 100,000+ 位号 |

### 6.2 安全要求

- HTTPS 强制
- JWT Token 安全存储
- CORS 配置
- SQL 注入防护 (Django ORM)
- XSS 防护 (React 默认)
- CSRF 防护
- 敏感数据加密存储

### 6.3 可用性要求

- 响应式设计 (桌面优先)
- 浏览器支持: Chrome, Firefox, Edge (最新两个版本)
- 错误处理和用户友好提示
- 操作确认 (删除等危险操作)

### 6.4 可维护性要求

- 代码注释和文档
- 单元测试覆盖率 > 70%
- API 文档自动生成 (OpenAPI)
- 日志记录

---

## 7. 并发控制规格

> **策略**: 记录级锁定 + 乐观锁双重保护

### 7.1 记录级锁定 (Record-Level Locking)

#### 7.1.1 EditLock 模型
```
目的: 防止多用户同时编辑同一条记录
字段:
  - id: BigAutoField
  - content_type: FK -> ContentType (Django 通用外键)
  - object_id: 被锁定对象的 ID
  - locked_by: FK -> User (锁定者)
  - locked_at: 锁定时间
  - expires_at: 过期时间 (默认 30 分钟)
  - lock_type: 锁定类型 (EDIT/REVIEW/APPROVE)
约束:
  - (content_type, object_id) 唯一约束
```

#### 7.1.2 锁定流程
```
1. 用户点击"编辑"按钮
   ↓
2. 后端检查是否已被锁定
   ├── 已锁定 → 返回锁定信息 (谁在编辑、剩余时间)
   │            前端显示"只读模式"或"等待解锁"
   └── 未锁定 → 创建锁定记录，返回编辑权限
   ↓
3. 用户进入编辑模式
   ↓
4. 用户保存或取消
   ├── 保存 → 释放锁定
   └── 取消 → 释放锁定
   ↓
5. 锁定超时自动释放 (30 分钟无操作)
```

#### 7.1.3 锁定 API
```
POST   /api/locks/acquire/           # 获取锁定
  Body: { "model": "tag", "id": 123 }
  Response: { "success": true, "expires_at": "..." }
           或 { "success": false, "locked_by": "张三", "expires_in": 1200 }

POST   /api/locks/release/           # 释放锁定
  Body: { "model": "tag", "id": 123 }

POST   /api/locks/extend/            # 延长锁定 (心跳)
  Body: { "model": "tag", "id": 123 }

GET    /api/locks/status/            # 查询锁定状态
  Query: ?model=tag&id=123
```

#### 7.1.4 前端锁定 UI
```
功能:
  - 锁定状态指示器 (🔒 图标 + 锁定者名称)
  - 只读模式提示 ("此记录正在被 张三 编辑")
  - 等待解锁按钮 (可选：请求解锁通知)
  - 心跳机制 (每 5 分钟自动延长锁定)
  - 页面关闭/切换时自动释放锁定
```

#### 7.1.5 批量编辑锁定
```
场景: 用户在 Instrument Index 中选择多条记录进行批量编辑
策略:
  - 尝试锁定所有选中记录
  - 如果部分记录已被锁定，提示用户：
    "以下 3 条记录正在被他人编辑，将跳过：FT-101, TT-102, PT-103"
  - 用户确认后，仅编辑可锁定的记录
```

### 7.2 乐观锁 (Optimistic Locking) - 二次保护

```python
# 作为记录级锁定的补充，防止极端情况下的数据覆盖
class Tag(models.Model):
    version = models.PositiveIntegerField(default=1)
    
    def save(self, *args, **kwargs):
        if self.pk:
            # 更新时检查版本
            updated = Tag.objects.filter(
                pk=self.pk, 
                version=self.version
            ).update(version=F('version') + 1, ...)
            if updated == 0:
                raise ConcurrentModificationError("数据已被他人修改，请刷新后重试")
```

### 7.3 实时状态同步 (WebSocket)

```
技术: Django Channels + WebSocket
功能:
  - 锁定状态实时广播 (用户 A 锁定后，用户 B 立即看到)
  - 解锁通知 (锁定释放后通知等待的用户)
  - 在线用户列表 (显示当前查看同一记录的用户)
  - 数据变更通知 (记录被修改后通知其他用户刷新)

消息类型:
  - lock.acquired: { "model": "tag", "id": 123, "user": "张三" }
  - lock.released: { "model": "tag", "id": 123 }
  - record.updated: { "model": "tag", "id": 123, "version": 5 }
  - user.viewing: { "model": "tag", "id": 123, "users": ["张三", "李四"] }
```

### 7.4 锁定超时与清理

```
策略:
  - 默认锁定时长: 30 分钟
  - 心跳间隔: 5 分钟 (前端自动发送)
  - 超时清理: Celery 定时任务，每分钟清理过期锁定
  - 强制解锁: 管理员可强制释放任何锁定
```

---

## 8. 数据导入导出规格

### 8.1 Excel 导入

```
支持格式: .xlsx, .xls, .csv
功能:
  - 模板下载
  - 数据验证
  - 错误报告
  - 批量创建/更新
  - 事务回滚 (失败时)
```

### 8.2 Excel 导出

```
支持格式: .xlsx, .csv
功能:
  - 列选择
  - 过滤条件保留
  - 大数据量异步导出
```

---

## 9. P&ID 数据集成规格

> **目的**: 从 P&ID (Piping & Instrumentation Diagram) 软件导入仪表数据，避免重复录入，保持数据一致性

### 9.1 支持的 P&ID 软件和格式

```
| P&ID 软件 | 数据格式 | 集成方式 | 优先级 |
|-----------|----------|----------|--------|
| SmartPlant P&ID | XML / Oracle DB | XML 导入 / DB 直连 | 高 |
| AVEVA E3D/PDMS | XML / Oracle DB | XML 导入 | 高 |
| AutoCAD P&ID | XML / DWG | XML 导入 | 中 |
| Bentley OpenPlant | XML / iModel | XML 导入 | 中 |
| 通用格式 | Excel / CSV | 文件导入 | 高 |
| 标准格式 | ISO 15926 / DEXPI | XML 导入 | 中 |
```

### 9.2 数据导入模型

#### 9.2.1 ImportJob (导入任务)
```
字段:
  - id: BigAutoField
  - project: FK -> Project
  - source_type: 数据源类型 (Excel/XML/Database/API)
  - source_system: 源系统 (SmartPlant/AVEVA/AutoCAD/Generic)
  - file: 上传的文件 (可选)
  - connection_config: JSONField (数据库连接配置，加密存储)
  - status: 状态 (Pending/Processing/Completed/Failed)
  - total_records: 总记录数
  - imported_records: 成功导入数
  - failed_records: 失败记录数
  - error_log: JSONField (错误详情)
  - created_by: FK -> User
  - created_at: 创建时间
  - completed_at: 完成时间
```

#### 9.2.2 ImportMapping (字段映射)
```
目的: 定义源系统字段到 OpenInstrument 字段的映射关系
字段:
  - id: BigAutoField
  - organization: FK -> Organization
  - name: 映射配置名称 (如 "SmartPlant P&ID 标准映射")
  - source_system: 源系统
  - entity_type: 目标实体 (Tag/Loop/Cable/JunctionBox)
  - field_mappings: JSONField (字段映射)
    - [
        { "source": "TAG_NO", "target": "tag_number", "transform": null },
        { "source": "DESCRIPTION", "target": "description", "transform": null },
        { "source": "INST_TYPE", "target": "instrument_type", "transform": "lookup:instrument_type_code" },
        { "source": "UNIT_NO", "target": "unit", "transform": "lookup:unit_code" },
        { "source": "LOOP_NO", "target": "loop", "transform": "lookup:loop_number" },
        { "source": "P_RANGE_MIN", "target": "spec_data.range_min", "transform": "float" },
        { "source": "P_RANGE_MAX", "target": "spec_data.range_max", "transform": "float" }
      ]
  - default_values: JSONField (默认值)
  - validation_rules: JSONField (验证规则)
```

#### 9.2.3 ImportRecord (导入记录)
```
目的: 记录每条数据的导入状态，支持增量同步
字段:
  - id: BigAutoField
  - import_job: FK -> ImportJob
  - source_id: 源系统中的唯一标识
  - entity_type: 实体类型
  - entity_id: 导入后的实体 ID (成功时)
  - source_data: JSONField (原始数据)
  - status: 状态 (Created/Updated/Skipped/Failed)
  - error_message: 错误信息
  - created_at: 时间戳
```

### 9.3 导入流程

```
1. 选择数据源
   ├── 上传文件 (Excel/XML)
   └── 配置数据库连接 (Oracle/SQL Server)
   ↓
2. 选择/创建字段映射
   ├── 使用预设映射 (SmartPlant/AVEVA 标准)
   └── 自定义映射 (拖拽配置)
   ↓
3. 数据预览和验证
   ├── 显示前 100 条数据预览
   ├── 验证必填字段
   ├── 检查外键引用 (InstrumentType, Unit, Loop)
   └── 标记潜在问题 (重复、格式错误)
   ↓
4. 冲突处理策略
   ├── 跳过已存在: 不更新已有数据
   ├── 覆盖更新: 用新数据覆盖
   └── 合并更新: 仅更新非空字段
   ↓
5. 执行导入 (异步任务)
   ├── 批量处理 (每批 100 条)
   ├── 事务控制 (每批一个事务)
   └── 实时进度显示
   ↓
6. 导入报告
   ├── 成功/失败统计
   ├── 错误详情下载 (Excel)
   └── 导入日志
```

### 9.4 导入 API

```
POST /api/imports/
  Body: {
    "project_id": 1,
    "source_type": "excel",
    "source_system": "smartplant",
    "mapping_id": 5,
    "conflict_strategy": "skip" | "overwrite" | "merge",
    "file": <multipart file>
  }
  Response: {
    "job_id": "abc123",
    "status": "pending"
  }

GET /api/imports/{job_id}/
  Response: {
    "status": "processing",
    "progress": 45,
    "total_records": 500,
    "imported_records": 225,
    "failed_records": 3
  }

GET /api/imports/{job_id}/errors/
  Response: {
    "errors": [
      { "row": 15, "field": "instrument_type", "error": "Unknown type: XYZ" },
      { "row": 28, "field": "tag_number", "error": "Duplicate: FT-101" }
    ]
  }

POST /api/imports/{job_id}/retry/
  Body: { "record_ids": [15, 28] }
```

### 9.5 XML 导入格式

#### 9.5.1 SmartPlant P&ID XML 格式
```xml
<?xml version="1.0" encoding="UTF-8"?>
<PlantModel xmlns="http://www.intergraph.com/sppid">
  <Instruments>
    <Instrument>
      <TagNumber>FT-101</TagNumber>
      <Description>Feed Flow Transmitter</Description>
      <InstrumentType>FT</InstrumentType>
      <LoopNumber>FC-101</LoopNumber>
      <Unit>UNIT-100</Unit>
      <ProcessData>
        <RangeMin>0</RangeMin>
        <RangeMax>100</RangeMax>
        <Unit>m³/h</Unit>
      </ProcessData>
    </Instrument>
  </Instruments>
</PlantModel>
```

#### 9.5.2 DEXPI (ISO 15926) 格式支持
```
DEXPI (Data Exchange in the Process Industry) 是基于 ISO 15926 的行业标准
支持版本: DEXPI 1.3+
导入内容:
  - 仪表位号 (Instrument)
  - 工艺连接 (ProcessConnection)
  - 信号线 (SignalLine)
  - 设备关联 (Equipment Association)
```

### 9.6 数据库直连

#### 9.6.1 支持的数据库
```
| 数据库 | 驱动 | 典型用途 |
|--------|------|----------|
| Oracle | cx_Oracle | SmartPlant, AVEVA |
| SQL Server | pyodbc | 企业系统 |
| PostgreSQL | psycopg2 | 开源系统 |
```

#### 9.6.2 数据库连接配置
```
DatabaseConnection 模型:
  - id: BigAutoField
  - organization: FK -> Organization
  - name: 连接名称
  - db_type: 数据库类型
  - host: 主机地址
  - port: 端口
  - database: 数据库名
  - username: 用户名 (加密)
  - password: 密码 (加密)
  - schema: Schema 名称
  - query_template: 查询模板 (SQL)
  - is_active: 是否启用
  - last_sync_at: 最后同步时间
```

### 9.7 增量同步

```
功能:
  - 基于时间戳的增量同步 (WHERE modified_date > last_sync)
  - 基于变更标记的同步 (WHERE sync_flag = 'N')
  - 定时自动同步 (Celery Beat)
  - 手动触发同步

SyncSchedule 模型:
  - id: BigAutoField
  - connection: FK -> DatabaseConnection
  - project: FK -> Project
  - mapping: FK -> ImportMapping
  - schedule: Cron 表达式 (如 "0 2 * * *" 每天凌晨 2 点)
  - is_active: 是否启用
  - last_run_at: 最后运行时间
  - next_run_at: 下次运行时间
```

### 9.8 数据导出到 P&ID

```
目的: 将 OpenInstrument 中的数据导出，供 P&ID 软件更新

导出格式:
  - Excel (通用)
  - XML (SmartPlant/AVEVA 格式)
  - CSV (通用)

导出 API:
POST /api/exports/pid/
  Body: {
    "project_id": 1,
    "format": "xml",
    "target_system": "smartplant",
    "entity_types": ["tag", "loop"],
    "filters": { "status": "ACTIVE" }
  }
  Response: {
    "download_url": "/api/downloads/{file_id}/",
    "filename": "PID_Export_2025-12-12.xml"
  }
```

### 9.9 数据一致性检查

```
功能:
  - 对比 P&ID 源数据和 OpenInstrument 数据
  - 识别差异 (新增、修改、删除)
  - 生成差异报告
  - 支持双向同步建议

API:
GET /api/imports/compare/
  Query: {
    "project_id": 1,
    "connection_id": 3
  }
  Response: {
    "summary": {
      "total_source": 500,
      "total_local": 480,
      "new_in_source": 25,
      "modified": 10,
      "deleted_in_source": 5
    },
    "differences": [
      { "tag_number": "FT-105", "status": "new", "source_data": {...} },
      { "tag_number": "FT-101", "status": "modified", "fields": ["description", "range_max"] }
    ]
  }
```

---

## 附录 A: 仪表功能代码

| 代码 | 含义 | 示例 |
|------|------|------|
| F | Flow (流量) | FT, FIC, FV |
| T | Temperature (温度) | TT, TIC, TV |
| P | Pressure (压力) | PT, PIC, PV |
| L | Level (液位) | LT, LIC, LV |
| A | Analysis (分析) | AT, AIC |
| C | Control (控制) | - |
| H | Hand (手动) | HV |
| I | Indicate (指示) | FI, TI, PI |
| S | Safety (安全) | PSV, TSH |

---

## 附录 B: 仪表类型代码

| 代码 | 名称 | 类别 |
|------|------|------|
| FT | Flow Transmitter | TRANSMITTER |
| TT | Temperature Transmitter | TRANSMITTER |
| PT | Pressure Transmitter | TRANSMITTER |
| LT | Level Transmitter | TRANSMITTER |
| CV | Control Valve | CONTROL_VALVE |
| PSV | Pressure Safety Valve | CONTROL_VALVE |
| FE | Flow Element | SENSOR |
| TE | Temperature Element | SENSOR |

---

*本文档将随项目开发持续更新*
