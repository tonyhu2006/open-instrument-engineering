# OpenInstrument - 实现状态跟踪

> **版本**: 0.2.0  
> **最后更新**: 2025-12-11  
> **开发阶段**: 基础架构搭建  
> **对标产品**: Hexagon SmartPlant Instrumentation (SPI)

---

## SPI 功能模块完成度总览

| 模块 | SPI 功能 | 完成度 | 状态 |
|------|----------|--------|------|
| 1.1 | Administration (管理模块) | 25% | 🚧 |
| 1.2 | Instrument Index (仪表索引) | 60% | 🚧 |
| 1.3 | Engineering Data Editor (EDE) | 5% | 📋 |
| 1.4 | Specifications (规格书) | 5% | 📋 |
| 1.5 | Wiring (接线模块) | 0% | 📋 |
| 1.6 | Loop Drawings (回路图) | 0% | 📋 |
| 1.7 | Rule Manager (规则管理器) | 10% | 📋 |
| 1.8 | Version Control (版本控制) | 5% | 📋 |
| **总体** | | **~17%** | 🚧 |

---

## 状态图例

| 图标 | 状态 | 说明 |
|------|------|------|
| ✅ | 已完成 | 功能已实现并测试通过 |
| 🚧 | 进行中 | 正在开发 |
| 📋 | 计划中 | 已规划，待开发 |
| ❌ | 未开始 | 尚未规划具体实现 |

---

## 1. 基础架构

### 1.1 项目结构

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| Monorepo 结构 (/backend, /frontend) | ✅ | 2025-12-11 | |
| Docker Compose (PostgreSQL, Redis) | ✅ | 2025-12-11 | PostgreSQL:5433, Redis:6380 |
| .gitignore 配置 | ✅ | 2025-12-11 | |
| README.md | ✅ | 2025-12-11 | |

### 1.2 后端基础

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| Django 项目初始化 | ✅ | 2025-12-11 | Django 5.2.9 |
| PostgreSQL 数据库配置 | ✅ | 2025-12-11 | |
| Redis 缓存配置 | ✅ | 2025-12-11 | |
| CORS 配置 | ✅ | 2025-12-11 | django-cors-headers |
| DRF 配置 | ✅ | 2025-12-11 | |
| JWT 认证框架 | ✅ | 2025-12-11 | simplejwt (框架就绪，未实现登录) |
| API 文档 (OpenAPI) | ✅ | 2025-12-11 | drf-spectacular |
| Health Check API | ✅ | 2025-12-11 | /api/health/ |

### 1.3 前端基础

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| React + TypeScript (Vite) | ✅ | 2025-12-11 | React 19, Vite 7 |
| Tailwind CSS 配置 | ✅ | 2025-12-11 | Tailwind v4 |
| Shadcn UI 组件 | ✅ | 2025-12-11 | Button, Card, Badge |
| React Router 配置 | ✅ | 2025-12-11 | |
| Axios API 客户端 | ✅ | 2025-12-11 | |
| 侧边栏 Layout | ✅ | 2025-12-11 | Sidebar, Header, MainLayout |
| Dashboard 页面 | ✅ | 2025-12-11 | 显示健康检查状态 |

---

## 2. SPI 模块 1.1 - 管理模块 (Administration)

> **完成度**: 25%

### 2.0 基于角色的用户管理系统 (RBAC)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| Role 模型 | 📋 | - | 角色定义 |
| User 模型扩展 | 📋 | - | 关联角色 |
| 角色层级 (Level 1-5) | 📋 | - | Guest → Admin |
| 数据权限矩阵 | 📋 | - | 按专业划分 |
| 角色管理 API | 📋 | - | CRUD |
| 用户管理 API | 📋 | - | CRUD + 激活/停用 |
| 角色管理 UI | 📋 | - | Administrator only |
| 用户管理 UI | 📋 | - | Administrator only |

**角色层级:**
```
Level 5: Administrator (系统管理员) - 系统最高权限
Level 4: Project Engineer (项目工程师) - 项目全专业权限
Level 3: Instrumentation Engineer - 仪表专业数据 CRUD
Level 3: Process Engineer - 工艺专业数据 CRUD
Level 3: Mechanical Engineer - 机械/管道专业数据 CRUD
Level 1: Guest (访客) - 所有数据只读
```

### 2.0.1 工程项目组 (Project Task Force)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| ProjectTaskForce 模型 | 📋 | - | 项目组 |
| TaskForceMembership 模型 | 📋 | - | 成员关系 |
| 项目组创建 (Admin) | 📋 | - | 两种方式 |
| 项目组创建 (PE) | 📋 | - | 只能基于项目号 |
| 成员管理 API | 📋 | - | 添加/移除 |
| 项目组权限隔离 | 📋 | - | 不可互访 |
| 项目组管理 UI | 📋 | - | |

**项目组创建规则:**
```
Administrator:
  - 方式一: 先创建项目组，再分配工程项目号
  - 方式二: 基于工程项目号创建项目组
  - 可将任何用户加入/移除任何项目组

Project Engineer:
  - 只能基于工程项目号创建项目组
  - 只能管理自己创建的项目组成员
```

### 2.1 工厂层级 (Plant Hierarchy)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| 三级架构 (Plant→Area→Unit) | ✅ | 2025-12-11 | MPTT 实现 |
| 层级验证规则 | ✅ | 2025-12-11 | 强制层级关系 |
| Unit 级位号唯一性 | ✅ | 2025-12-11 | unique_tag_per_unit 约束 |
| 工厂层级 UI | 📋 | - | 树形组件 |

### 2.2 命名规则 (Naming Conventions)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| NamingConvention 模型 | 📋 | - | 正则表达式验证 |
| 层级格式类型 | 📋 | - | 6 种预定义格式 |
| 段定义 (Segment Definitions) | 📋 | - | JSONField 配置 |
| 预设命名规则模板 | 📋 | - | 7 种预设模板 |
| 位号格式强制规范 | 📋 | - | |
| 命名规则验证流程 | 📋 | - | 正则+层级+唯一性 |
| 自动生成位号 | 📋 | - | 基于规则自动生成 |
| 命名规则管理 UI | 📋 | - | |
| 自定义正则编辑器 | 📋 | - | 高级用户 |
| 命名规则 API | 📋 | - | CRUD + 验证 + 生成 |

**支持的层级格式:**
```
格式 1: Site-Plant-Area-Unit-Function-Sequence (完整层级)
格式 2: Plant-Area-Unit-Function-Sequence (省略 Site)
格式 3: Area-Unit-Function-Sequence (省略 Site+Plant)
格式 4: Unit-Function-Sequence (最简格式)
格式 5: XXXX-Unit-Function-Sequence (灵活前缀: Site/Plant/Area)
格式 6: Custom (管理员自定义正则)
```

**预设模板:**
```
- ISA-5.1 标准格式: FT-101, TIC-201A
- 完整层级格式: ZH-ETH-100-U01-FT-001
- 装置-单元格式: ETH-U01-FT-001
- 区域-单元格式: 100-U01-FT-001
- 简化格式: FT-101
- 电缆命名格式: IC-FT-101-01
- 接线箱命名格式: JB-100-01
```

### 2.3 项目层级管理 (新架构)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| Project 模型 (顶层) | 📋 | - | 工程项目，用 project_no 作为 ID |
| Client 模型 | 📋 | - | 客户/业主 (第二层) |
| Site 模型 | 📋 | - | 厂区/地点 (第三层，支持多个) |
| Plant 模型 | 📋 | - | 工厂/装置 (第四层) |
| PlantHierarchy 模型 | 📋 | - | Area/Unit 层级 |
| Organization 模型 (可选) | 📋 | - | SaaS 多租户隔离 |
| 层级结构配置 | 📋 | - | hierarchy_config JSON |
| 层级模板 (standard/simple) | 📋 | - | 预设模板 |
| 项目创建向导 UI | 📋 | - | 配置层级结构 |
| 层级编辑 UI | 📋 | - | 树形结构管理 |

**新数据层级架构:**
```
Project (工程项目 - 顶层入口)
│
├── 【项目级共享对象】
│   └── InstrumentType, Templates, NamingConvention, SymbolLibrary
│
└── Client (客户/业主)
    └── Site(s) (厂区)
        └── Plant(s) (工厂/装置)
            │   └── PID, ControlSystem, CableRoute
            └── Area(s) (工艺区域)
                │   └── JunctionBox, Cabinet, ControlRoom
                └── Unit(s) (工艺单元)
                    └── Tag★, Loop, Specification, WiringConnection, Cable
```

**对象归属原则:**
- **Tag (仪表位号)** 是核心，归属于 Unit
- **共享库** (仪表类型、模板) 在项目级
- **物理设备** (接线箱、控制柜) 按物理位置归属
- **Cable** 跨层级引用，连接不同位置

### 2.4 用户认证与授权 (RBAC)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| User 模型扩展 | 📋 | - | 扩展 AbstractUser |
| 登录/登出 API | 📋 | - | |
| Token 刷新 | 📋 | - | |
| Role 模型 | 📋 | - | RBAC |
| Permission 模型 | 📋 | - | |
| UserProjectRole 关联 | 📋 | - | |
| 权限检查装饰器 | 📋 | - | |
| 登录页面 UI | 📋 | - | |
| 用户管理 UI | 📋 | - | |

---

## 3. SPI 模块 1.2 - 仪表索引模块 (Instrument Index)

> **完成度**: 60%

### 3.1 位号管理 (Tag)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| Tag 模型 | ✅ | 2025-12-11 | 核心模型 |
| Unit 级别唯一约束 | ✅ | 2025-12-11 | unique_tag_per_unit |
| spec_data Schema 验证 | ✅ | 2025-12-11 | jsonschema |
| Loop 同 Unit 验证 | ✅ | 2025-12-11 | |
| 版本号自动递增 | ✅ | 2025-12-11 | revision 字段 |
| Tag Serializer | ✅ | 2025-12-11 | |
| Tag ViewSet | ✅ | 2025-12-11 | CRUD + bulk_update/search |
| 批量更新 API | ✅ | 2025-12-11 | /tags/bulk-update/ |
| 高级搜索 API | ✅ | 2025-12-11 | /tags/search/ |

### 3.2 仪表类型概况 (Instrument Type Profile)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| InstrumentType 模型 | ✅ | 2025-12-11 | 含 schema_template |
| JSON Schema 验证 | ✅ | 2025-12-11 | jsonschema 库 |
| InstrumentType Serializer | ✅ | 2025-12-11 | |
| InstrumentType ViewSet | ✅ | 2025-12-11 | CRUD + validate_spec |
| 仪表类型管理 UI | 📋 | - | |
| Schema 编辑器 | 📋 | - | JSON Schema 可视化编辑 |

### 3.3 回路创建 (Loop)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| Loop 模型 | ✅ | 2025-12-11 | |
| Loop Serializer | ✅ | 2025-12-11 | |
| Loop ViewSet | ✅ | 2025-12-11 | CRUD + tags |
| 回路管理 UI | 📋 | - | |

### 3.4 典型回路复制 (Typical Loop)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| TypicalLoop 模型 | 📋 | - | 回路模板 |
| 批量实例化 API | 📋 | - | 一键生成多组回路 |
| 典型回路 UI | 📋 | - | |

---

## 4. SPI 模块 1.3 - 工程数据编辑器 (EDE)

> **完成度**: 5%

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| SavedView 模型 | 📋 | - | 保存用户视图 |
| 动态查询构建 API | 📋 | - | QueryBuilder |
| 跨表查询 | 📋 | - | |
| 视图保存/共享 | 📋 | - | |
| TanStack Table 数据网格 | 📋 | - | 高性能网格 |
| 虚拟滚动 | 📋 | - | 支持 10,000+ 行 |
| 列排序/过滤/分组 | 📋 | - | |
| 行内编辑 | 📋 | - | |
| 批量填充 (Bulk Fill) | ⚠️ | 2025-12-11 | 有 bulk_update API |
| 列拖拽排序 | 📋 | - | |

---

## 5. SPI 模块 1.4 - 规格书模块 (Specifications)

> **完成度**: 5%

### 5.1 工艺与管道数据 (Process & Piping Data)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| ProcessData 模型 | 📋 | - | 工艺过程数据 |
| PipeSpecification 模型 | 📋 | - | 管道规格库 |
| ProcessConnection 模型 | 📋 | - | 工艺连接 |
| 工艺数据输入 UI | 📋 | - | Process Engineer 使用 |
| 管道连接数据输入 UI | 📋 | - | Mechanical Engineer 使用 |
| 工艺数据 API | 📋 | - | CRUD + 批量更新 |
| 管道规格 API | 📋 | - | CRUD + 导入 |
| 工艺连接 API | 📋 | - | CRUD |
| 从模拟软件导入 | 📋 | - | HYSYS/Aspen Plus/PRO-II |
| 从 P&ID 导入管线号 | 📋 | - | |
| 物性计算器 | 📋 | - | 基于介质和条件 |
| 数据流向规格书 | 📋 | - | 自动填充规格书字段 |

**工艺数据字段:**
```
介质: 名称、状态、组分、腐蚀性、毒性、易燃性
工况: 操作/设计 压力、温度、流量
物性: 密度、粘度、比重、分子量、蒸汽压
报警: HH/H/L/LL 设定值
```

**管道连接字段:**
```
位置: 管线号、设备位号
连接: 尺寸、类型 (FLG/THD/SW/BW)、法兰等级
附件: 根部阀、排放阀、阀组
安装: 方式、方向、插入长度
```

### 5.2 规格书模板与文档

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| SpecificationTemplate 模型 | 📋 | - | 规格书模板 |
| SpecificationDocument 模型 | 📋 | - | 规格书实例 |
| 数据驱动文档 | ⚠️ | 2025-12-11 | 有 spec_data，无文档生成 |
| 自动更新 | 📋 | - | 数据变更→文档更新 |
| PDF 生成 | 📋 | - | |
| External Editor 导出 (.oisf) | 📋 | - | 供应商数据交换 |
| External Editor 导入 | 📋 | - | |
| 规格书表单 UI | 📋 | - | 动态表单 |
| 版本对比 UI | 📋 | - | |

---

## 6. SPI 模块 1.5 - 接线模块 (Wiring)

> **完成度**: 0%

### 6.1 数据模型

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| JunctionBox 模型 | 📋 | - | 接线箱 |
| TerminalStrip 模型 | 📋 | - | 端子排 |
| Terminal 模型 | 📋 | - | 端子 |
| Cable 模型 (扩展) | 📋 | - | 含规格、路由、施工信息 |
| CableRoute 模型 | 📋 | - | 电缆桥架/穿线管 |
| WiringConnection 模型 | 📋 | - | 含芯号、芯线颜色 |
| CableInstallationLog 模型 | 📋 | - | 施工日志 |
| RIOPanel 模型 | 📋 | - | 现场 I/O 盘柜 |
| IOCard 模型 | 📋 | - | I/O 卡件 (AI/AO/DI/DO) |
| IOChannel 模型 | 📋 | - | I/O 通道 (回路图基础) |
| IOChannelAssignment 模型 | 📋 | - | 通道分配记录 |
| TerminalStrip 模型 | 📋 | - | 端子排 |
| JunctionBoxTerminal 模型 | 📋 | - | 接线箱端子 (回路图基础) |
| WiringPath 模型 | 📋 | - | 完整接线路径 |
| EquipmentNode 概念 | 📋 | - | 统一设备节点类型 |

**支持的信号路径类型:**
```
路径 1: Tag → JB → Main Cabinet/DCS (集中式)
路径 2: Tag → RIO Panel → DCS (分布式)
路径 3: Tag → JB → RIO Panel → DCS (大型项目)
路径 4: Tag → JB1 → JB2 → RIO → DCS (复杂布线)
```

### 6.3 I/O 通道分配功能 (回路图生成基础)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| I/O 通道自动分配 | 📋 | - | 按仪表类型匹配 AI/AO/DI/DO |
| I/O 通道手动分配 | 📋 | - | 拖拽分配 |
| I/O 通道批量分配 | 📋 | - | 选择多个仪表 |
| 信号类型匹配检查 | 📋 | - | AI 只能分配模拟量输入 |
| 通道容量检查 | 📋 | - | 防止超分配 |
| 防爆等级匹配 | 📋 | - | IS 仪表→IS 卡件 |
| I/O 清单报表 | 📋 | - | Excel/PDF 导出 |
| 通道使用率统计 | 📋 | - | |
| I/O 分配 UI | 📋 | - | 拖拽+卡件视图 |

### 6.4 接线箱端子分配功能 (回路图生成基础)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| 端子自动分配 | 📋 | - | 按电缆芯数分配 |
| 端子手动分配 | 📋 | - | 拖拽分配 |
| 端子批量分配 | 📋 | - | |
| 跳线管理 | 📋 | - | 端子间短接 |
| 端子容量检查 | 📋 | - | 额定电压/电流 |
| 信号隔离检查 | 📋 | - | IS/非IS 分开 |
| 端子接线表报表 | 📋 | - | Excel/PDF 导出 |
| 端子使用率统计 | 📋 | - | |
| 端子分配 UI | 📋 | - | 表格视图 |

### 6.4.1 仪表接线制式支持

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| InstrumentWiringConfig 模型 | 📋 | - | 仪表类型接线配置 |
| TagWiring 模型 | 📋 | - | 仪表接线实例 |
| 2-Wire (两线制) 支持 | 📋 | - | 4-20mA 变送器 |
| 3-Wire (三线制) 支持 | 📋 | - | RTD, 部分变送器 |
| 4-Wire (四线制) 支持 | 📋 | - | 高精度变送器, 执行器 |
| 6-Wire (六线制) 支持 | 📋 | - | 高精度 RTD |
| 端子/芯线自动计算 | 📋 | - | 根据接线制式 |
| 电缆规格推荐 | 📋 | - | 根据接线制式 |
| 预设接线配置库 | 📋 | - | FT/TT/PT/CV 等 |

**支持的接线制式:**
```
2-Wire: 信号+供电共用 (4-20mA 变送器)
3-Wire: 独立供电+信号 (RTD)
4-Wire: 独立供电+独立信号 (高精度/执行器)
6-Wire: 高精度 RTD 测量
DI/DO: 干接点/有源信号/继电器
```

### 6.5 接线功能

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| 信号流逻辑检查 | 📋 | - | 防止错误连接 |
| 电压/类型匹配验证 | 📋 | - | |
| 接线管理 API | 📋 | - | |
| 拖拽接线 UI | 📋 | - | |
| 端子接线图生成 | 📋 | - | |

### 6.6 Cable Schedule (电缆清单表)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| Cable Schedule API | 📋 | - | 查询、过滤、排序 |
| Cable Schedule 导出 (Excel) | 📋 | - | |
| Cable Schedule 导出 (PDF) | 📋 | - | |
| CableScheduleTemplate 模型 | 📋 | - | 可定制列和格式 |
| 汇总统计 API | 📋 | - | 按类型/状态/规格统计 |
| 施工进度跟踪 | 📋 | - | 甘特图、测试记录 |
| Cable Schedule UI | 📋 | - | 数据网格 + 导出 |

---

## 7. SPI 模块 1.6 - 回路图生成 (Loop Drawings / ESL)

> **完成度**: 0%

### 7.1 数据模型

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| SymbolLibrary 模型 | 📋 | - | 符号库 (SVG + DXF) |
| LoopDrawingTemplate 模型 | 📋 | - | 回路图模板 |
| TitleBlockTemplate 模型 | 📋 | - | 图框模板 |

### 7.2 图纸导出

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| DXF 导出 (ezdxf) | 📋 | - | 核心功能 |
| DWG 导出 (ODA Converter) | 📋 | - | DXF → DWG 转换 |
| PDF 导出 | 📋 | - | WeasyPrint/ReportLab |
| SVG 导出 | 📋 | - | 前端直接导出 |
| 批量导出 API | 📋 | - | ZIP 打包 |
| DXF 图层规划 | 📋 | - | CAD 标准图层 |
| 符号库 DXF 映射 | 📋 | - | SVG → DXF Block |

### 7.3 回路图生成引擎

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| 符号编辑器 | 📋 | - | SVG + 宏定义 |
| 回路图生成引擎 | 📋 | - | React Flow |
| 宏自动填充 | 📋 | - | 端子号、线号等 |
| 实时数据更新 | 📋 | - | 数据库更新→图纸更新 |
| 回路图 UI | 📋 | - | |

---

## 8. SPI 模块 1.7 - 规则管理器 (Rule Manager)

> **完成度**: 10%

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| Rule 模型 | 📋 | - | IF-THEN 规则 |
| RuleExecution 模型 | 📋 | - | 执行记录 |
| 规则引擎 | 📋 | - | |
| 实时校验 | ⚠️ | 2025-12-11 | 仅有 JSON Schema 验证 |
| 规则管理 API | 📋 | - | |
| 规则管理 UI | 📋 | - | |
| GB 标准规则库 | 📋 | - | |

---

## 9. SPI 模块 1.8 - 版本控制 (Version Control)

> **完成度**: 5%

### 9.1 内部版本管理

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| GlobalRevision 模型 | 📋 | - | 全局修订 |
| EntityRevision 模型 | 📋 | - | 实体版本历史 |
| revision 字段 | ✅ | 2025-12-11 | Tag 模型已有 |
| 归档 (Archiving) | 📋 | - | 数据快照 |
| 版本对比 API | 📋 | - | 字段级差异 |
| 版本回滚 API | 📋 | - | |
| 版本对比 UI | 📋 | - | |

### 9.2 审计日志 (Audit Trail)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| AuditLog 模型 | 📋 | - | Who/When/What |
| 自动审计中间件 | 📋 | - | |
| 审计日志查询 API | 📋 | - | |
| 审计日志 UI | 📋 | - | |
| 审计报告导出 | 📋 | - | |

### 9.3 变更标记功能

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| changed_fields 字段 | 📋 | - | 变更字段列表 |
| change_details 字段 | 📋 | - | 详细变更记录 (JSON) |
| 变更类型标记 | 📋 | - | added/removed/modified |
| 变更追踪 API | 📋 | - | /api/audit/{model}/{id}/changes/ |
| 字段历史 API | 📋 | - | /api/audit/.../field-history/ |
| 前端变更高亮 UI | 📋 | - | 绿/黄/红背景标记 |
| 变更指示器 (🔄) | 📋 | - | 悬停显示变更信息 |
| 变更对比视图 | 📋 | - | 左右对比 + 差异高亮 |
| ChangeNotification 模型 | 📋 | - | 变更通知 |
| ChangeRequest 模型 | 📋 | - | 变更审批流程 (可选) |
| 批量变更报告导出 | 📋 | - | Excel/PDF |

### 9.4 并发控制 (记录级锁定 + 乐观锁)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| EditLock 模型 | 📋 | - | 记录级锁定 |
| 锁定 API (acquire/release/extend) | 📋 | - | |
| 锁定超时自动释放 | 📋 | - | Celery 定时任务 |
| 乐观锁 (version 字段) | 📋 | - | 二次保护 |
| 并发冲突检测 | 📋 | - | |
| 前端锁定状态 UI | 📋 | - | 🔒 图标 + 只读模式 |
| 批量编辑锁定 | 📋 | - | |
| WebSocket 实时状态同步 | 📋 | - | Django Channels |

---

## 10. 数据导入导出

### 10.1 Excel 导入导出

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| Excel 导入 API | 📋 | - | |
| Excel 导出 API | 📋 | - | |
| 导入模板下载 | 📋 | - | |
| 导入验证报告 | 📋 | - | |
| 导入导出 UI | 📋 | - | |

### 10.2 P&ID 数据集成

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| ImportJob 模型 | 📋 | - | 导入任务管理 |
| ImportMapping 模型 | 📋 | - | 字段映射配置 |
| ImportRecord 模型 | 📋 | - | 导入记录跟踪 |
| Excel/CSV 导入 | 📋 | - | 通用格式 |
| XML 导入 (SmartPlant) | 📋 | - | |
| XML 导入 (AVEVA) | 📋 | - | |
| DEXPI (ISO 15926) 导入 | 📋 | - | 行业标准 |
| DatabaseConnection 模型 | 📋 | - | 数据库直连 |
| Oracle 直连 | 📋 | - | SmartPlant/AVEVA |
| 增量同步 (SyncSchedule) | 📋 | - | 定时自动同步 |
| 数据一致性检查 | 📋 | - | 差异对比 |
| P&ID 导出 (XML) | 📋 | - | 双向同步 |
| 导入向导 UI | 📋 | - | 字段映射拖拽 |

---

## 11. 前端 UI 功能

### 11.1 布局与导航

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| 主界面布局 | 📋 | - | 顶部导航+侧边栏+主工作区 |
| 层级导航树 (Hierarchy Navigator) | 📋 | - | 树形展示项目层级 |
| 上下文选择器 (Context Selector) | 📋 | - | 快速切换层级范围 |
| 面包屑导航 | 📋 | - | 显示当前位置 |
| 数据过滤联动 | 📋 | - | 层级选择自动过滤数据 |

### 11.2 核心页面

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| 项目仪表盘 | 📋 | - | 概览统计+层级树 |
| 仪表索引表 ★ | 📋 | - | 核心页面，TanStack Table |
| 位号详情/规格书 | 📋 | - | 动态表单 |
| 回路管理 | 📋 | - | 回路列表 |
| 回路图查看 | 📋 | - | React Flow |
| 接线路径视图 | 📋 | - | 可视化接线路径 |
| RIO 盘柜管理 | 📋 | - | I/O 卡件+通道分配 |
| 电缆管理 | 📋 | - | 电缆表 |

### 11.3 核心组件

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| 层级导航树组件 | 📋 | - | 树形+搜索+右键菜单 |
| 上下文选择器组件 | 📋 | - | 级联下拉 |
| 仪表索引表组件 | 📋 | - | 虚拟滚动+行内编辑 |
| 规格书表单组件 | 📋 | - | 动态表单生成 |
| 接线路径图组件 | 📋 | - | 可视化节点连接 |
| RIO 卡件视图组件 | 📋 | - | 槽位+通道显示 |
| 详情面板组件 | 📋 | - | 右侧可折叠面板 |

### 11.4 快捷操作

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| 快捷键支持 | 📋 | - | Ctrl+N/S/F, F2, Delete |
| 右键菜单 | 📋 | - | 上下文相关操作 |
| 批量操作 | 📋 | - | 批量编辑/删除 |
| 拖拽操作 | 📋 | - | 层级调整/接线 |

### 11.5 国际化 (i18n)

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| react-i18next 集成 | 📋 | - | 前端国际化框架 |
| 英语翻译文件 (主语言) | 📋 | - | en/*.json |
| 简体中文翻译文件 | 📋 | - | zh-CN/*.json |
| 繁體中文翻译文件 | 📋 | - | zh-TW/*.json |
| 日语翻译文件 | 📋 | - | ja/*.json |
| 韩语翻译文件 | 📋 | - | ko/*.json |
| 法语翻译文件 | 📋 | - | fr/*.json |
| 西班牙语翻译文件 | 📋 | - | es/*.json |
| 意大利语翻译文件 | 📋 | - | it/*.json |
| 德语翻译文件 | 📋 | - | de/*.json |
| 俄语翻译文件 | 📋 | - | ru/*.json |
| 阿拉伯语翻译文件 (RTL) | 📋 | - | ar/*.json |
| 希伯来语翻译文件 (RTL) | 📋 | - | he/*.json |
| RTL 布局支持 | 📋 | - | 阿拉伯语/希伯来语 |
| 语言切换 UI | 📋 | - | 顶部导航栏下拉 |
| 用户语言偏好保存 | 📋 | - | UserPreference 模型 |
| 日期/数字本地化 | 📋 | - | 格式化显示 |

**支持的语言 (12 种):**
```
主语言: English (en) - 默认

东亚语言:
  - 简体中文 (zh-CN)
  - 繁體中文 (zh-TW)
  - 日本語 (ja)
  - 한국어 (ko)

欧洲语言:
  - Français (fr)
  - Español (es)
  - Italiano (it)
  - Deutsch (de)
  - Русский (ru)

RTL 语言:
  - العربية (ar) - 阿拉伯语
  - עברית (he) - 希伯来语
```

---

## 12. 演示数据

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| seed_demo_data 命令 | ✅ | 2025-12-11 | |
| 演示工厂层级 | ✅ | 2025-12-11 | 1 Plant, 2 Areas, 2 Units |
| 演示仪表类型 | ✅ | 2025-12-11 | FT, TT, CV, PT |
| 演示回路 | ✅ | 2025-12-11 | FIC-101, TIC-102 |
| 演示位号 | ✅ | 2025-12-11 | FT-101, FV-101, TT-102, PT-103 |

---

## 12. 测试

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| 后端单元测试 | 📋 | - | pytest-django |
| API 集成测试 | 📋 | - | |
| 前端单元测试 | 📋 | - | Vitest |
| E2E 测试 | 📋 | - | Playwright |

---

## 13. 部署

| 功能 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| 开发环境 Docker Compose | ✅ | 2025-12-11 | |
| 生产环境 Docker 配置 | 📋 | - | |
| CI/CD 流水线 | 📋 | - | GitHub Actions |
| 环境变量管理 | ✅ | 2025-12-11 | .env 文件 |

---

## 开发里程碑

### Phase 1: 基础架构 ✅ (已完成)
- [x] 项目初始化
- [x] 后端框架搭建
- [x] 前端框架搭建
- [x] 数据库配置
- [x] 健康检查 API

### Phase 2: 工程数据模型 ✅ (已完成)
- [x] PlantHierarchy (MPTT)
- [x] Loop
- [x] InstrumentType (JSON Schema)
- [x] Tag (核心模型)
- [x] DRF Serializers & ViewSets

### Phase 3: 企业级基础 📋 (计划中)
- [ ] Organization + Site + Project 模型
- [ ] User 扩展 + RBAC
- [ ] NamingConvention 命名规则
- [ ] 乐观锁并发控制
- [ ] AuditLog 审计日志

### Phase 4: 前端核心页面 📋 (计划中)
- [ ] 仪表索引表 (TanStack Table)
- [ ] 规格书表单 (动态表单)
- [ ] 工厂层级管理 (树形组件)
- [ ] 回路管理

### Phase 5: 版本控制系统 📋 (计划中)
- [ ] EntityRevision 版本历史
- [ ] GlobalRevision 全局修订
- [ ] 版本对比 API 和 UI
- [ ] 版本回滚

### Phase 6: 规格书模块 📋 (计划中)
- [ ] SpecificationTemplate 模板
- [ ] PDF 生成
- [ ] External Editor 导入导出

### Phase 7: 规则引擎 📋 (计划中)
- [ ] Rule 模型和引擎
- [ ] 实时校验
- [ ] GB 标准规则库

### Phase 8: 接线模块 📋 (计划中)
- [ ] 接线设备模型
- [ ] 信号流逻辑检查
- [ ] 拖拽接线 UI

### Phase 9: 回路图生成 📋 (计划中)
- [ ] 符号库
- [ ] 回路图模板
- [ ] React Flow 动态生成

### Phase 10: 生产就绪 📋 (计划中)
- [ ] 测试覆盖
- [ ] 性能优化
- [ ] 安全加固
- [ ] 部署配置

---

## 变更日志

### 2025-12-24 (v0.2.17)
- 扩展国际化语言支持至 12 种语言
- 新增: 法语 (fr), 西班牙语 (es), 意大利语 (it), 德语 (de), 俄语 (ru)
- 新增 RTL 语言: 阿拉伯语 (ar), 希伯来语 (he)
- 添加 RTL 布局支持规格 (CSS 逻辑属性, Tailwind RTL)

### 2025-12-24 (v0.2.16)
- 增强命名规则 (Naming Conventions) 功能
- 支持 6 种层级格式类型
- 添加段定义 (Segment Definitions) 配置
- 添加 7 种预设命名规则模板
- 支持管理员自定义正则表达式
- 添加命名规则验证流程
- 添加自动生成位号功能
- 添加自定义正则编辑器 UI

### 2025-12-13 (v0.2.15)
- 添加基于角色的用户管理系统 (RBAC)
- 定义角色层级: Administrator, Project Engineer, Instrumentation/Process/Mechanical Engineer, Guest
- 添加数据权限矩阵 (按专业划分)
- 添加工程项目组 (Project Task Force) 功能
- 项目组创建规则: Admin 两种方式, PE 只能基于项目号
- 项目组权限隔离: 不同项目组之间不可互访

### 2025-12-13 (v0.2.14)
- 添加工艺过程数据 (ProcessData) 模型和 UI
- 添加管道规格 (PipeSpecification) 模型
- 添加工艺连接 (ProcessConnection) 模型
- 添加 Process Engineer 工艺数据输入界面
- 添加 Mechanical Engineer 管道连接数据输入界面
- 定义工艺数据和管道数据流向规格书的映射
- 支持从工艺模拟软件导入 (HYSYS/Aspen Plus)

### 2025-12-12 (v0.2.13)
- 添加国际化 (i18n) 功能规格
- 英语为主语言 (Primary Language)
- 支持语言: English, 简体中文, 繁體中文, 日本語, 한국어
- 前端 react-i18next 集成规格
- 后端 Django i18n 配置
- 用户语言偏好设置
- 日期/数字本地化

### 2025-12-12 (v0.2.12)
- 添加仪表接线制式支持 (2-Wire/3-Wire/4-Wire/6-Wire)
- 添加 InstrumentWiringConfig、TagWiring 模型
- 添加端子/芯线自动计算功能
- 添加电缆规格推荐功能
- 添加预设接线配置库 (FT/TT/PT/RTD/CV 等)

### 2025-12-12 (v0.2.11)
- 添加 I/O 通道分配功能规格 (回路图生成基础)
- 添加 IOChannel、IOChannelAssignment 模型
- 添加接线箱端子分配功能规格 (回路图生成基础)
- 添加 JunctionBoxTerminal、TerminalStrip 模型
- 添加 I/O 分配 API 和 UI 设计
- 添加端子分配 API 和 UI 设计
- 定义 I/O 类型与信号匹配规则

### 2025-12-12 (v0.2.10)
- 全面更新前端 UI 规格
- 添加层级导航树 (Hierarchy Navigator)
- 添加上下文选择器 (Context Selector)
- 添加接线路径视图 (Wiring Path View)
- 添加 RIO 盘柜管理页面
- 更新路由结构，按功能模块组织
- 添加快捷键和右键菜单规格

### 2025-12-12 (v0.2.9)
- 添加 RIO Panel (现场 I/O 盘柜) 支持
- 添加 IOCard (I/O 卡件) 模型
- 添加 WiringPath (接线路径) 模型
- 支持多种信号路径类型 (直接/经JB/经RIO/经JB和RIO)
- 添加 EquipmentNode 统一设备节点概念

### 2025-12-12 (v0.2.8)
- 添加仪表自控对象组织架构规格
- 定义各层级对象归属关系
- Tag 为核心对象，归属于 Unit
- 共享库 (仪表类型、模板) 在项目级
- Cable 跨层级引用设计

### 2025-12-12 (v0.2.7)
- 重新设计数据层级架构
- Project 作为顶层对象 (用 project_no 作为 ID)
- 新增 Client (客户/业主) 模型
- 新增 Plant (工厂/装置) 模型
- 层级结构: Project → Client → Site → Plant → Area → Unit
- 支持层级结构配置和预设模板

### 2025-12-12 (v0.2.6)
- 增强变更标记功能规格
- 添加 changed_fields、change_details 字段
- 添加变更追踪 API 和字段历史 API
- 添加前端变更高亮 UI 规格
- 添加 ChangeNotification、ChangeRequest 模型
- 添加变更审批流程 (可选)

### 2025-12-12 (v0.2.5)
- 添加 P&ID 数据集成规格
- 支持 SmartPlant P&ID、AVEVA、AutoCAD P&ID 等系统
- 添加 ImportJob、ImportMapping、ImportRecord 模型
- 添加数据库直连 (Oracle/SQL Server) 支持
- 添加 DEXPI (ISO 15926) 标准格式支持
- 添加增量同步和数据一致性检查功能

### 2025-12-12 (v0.2.4)
- 添加详细的 Cable Schedule (电缆清单表) 规格
- 扩展 Cable 模型 (规格、路由、施工信息)
- 添加 CableRoute、CableInstallationLog 模型
- 添加 Cable Schedule API 和导出功能
- 添加施工进度跟踪功能

### 2025-12-12 (v0.2.3)
- 添加 DWG/DXF 导出技术方案 (ezdxf + ODA Converter)
- 添加图纸导出 API 规格
- 添加 TitleBlockTemplate 图框模板模型
- 添加 DXF 图层规划和符号库映射

### 2025-12-12 (v0.2.2)
- 添加记录级锁定 (EditLock) 并发控制方案
- 支持多用户同时编辑不同记录，防止同一记录冲突
- 添加 WebSocket 实时状态同步规划

### 2025-12-11 (v0.2.1)
- 添加 Site 模型支持多厂区架构
- 更新数据层级：Organization → Site → Project → PlantHierarchy

### 2025-12-11 (v0.2.0)
- 更新文档结构，按 SPI 功能模块组织
- 添加 SPI 功能模块完成度总览
- 详细规划所有 SPI 模块的实现状态
- 更新开发里程碑为 10 个阶段

### 2025-12-11 (v0.1.0)
- 初始化项目结构
- 创建 Django 后端基础架构
- 创建 React 前端基础架构
- 实现 Health Check API
- 创建 core_engineering app
- 实现 PlantHierarchy, Loop, InstrumentType, Tag 模型
- 实现 DRF Serializers 和 ViewSets
- 创建演示数据命令
- 创建 SPECIFICATION.md 和 IMPLEMENTATION.md

---

*本文档将随开发进度持续更新。每次代码修改后请检查并更新此文档。*
