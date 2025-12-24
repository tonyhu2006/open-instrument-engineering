# 项目名称: OpenInstrument (AI-Driven Instrumentation Design Platform) 目标: 构建一个基于 Web 的、数据驱动的过程仪表工程设计系统，复刻并现代化 SmartPlant Instrumentation (SPI) 的核心功能。

## 2.1 核心数据模型 (Data Models)

### 2.1.1 Plant Hierarchy (工厂层级):
#### 层级：Plant (工厂) -> Area (区域) -> Unit (单元)。
#### 规则：所有仪表位号 (Tag) 必须归属于一个 Unit。

### 2.1.2 Tag (位号):
#### 字段：Tag Number (唯一键), Function, Loop Number, Service, Status (Active/Deleted)。
#### 关联：属于一个 Loop，关联一种 Instrument Type。

### 2.1.3Loop (回路):
#### 字段：Loop Number, Function, Measured Variable (Flow, Temp, Pressure)。
#### 逻辑：一个 Loop 包含多个 Tag（如 FE, FT, FIC, FV）。

### 2.1.4 Instrument Type (仪表类型):
#### 定义仪表的属性模板（例如：控制阀需要 CV, FL, Body Size；变送器需要 Range Min, Range Max）。
#### 技术策略：使用 Django JSONField 存储动态属性模板。

## 2.2 关键功能模块 (Features)

### 2.2.1 TagInstrument Index (仪表索引表):
#### 一个高性能的数据网格（Grid），显示所有 Tag 的关键信息。
#### 功能：增删改查、Excel 导入/导出、批量修改。

### 2.2.2 Specification Sheets (规格书):
#### 动态表单：根据选择的仪表类型（如 "Control Valve"），自动渲染对应的输入字段。
#### 版本控制：每次保存生成一个 Revision 记录，支持对比差异。

### 2.2.3 Loop Wiring Manager (接线管理):
#### 定义接线箱 (Junction Box)、端子排 (Terminal Strip)、电缆 (Cable)。
#### 实现 "Drag & Drop" (拖拽) 接线功能：将仪表电缆连接到接线箱端子。

### 2.2.4 Auto-Loop Diagram (自动回路图):
#### 基于数据库中的连接关系，使用 React Flow 自动生成回路图。不需要人工画图。

## 2.3 技术约束

### 前端: React 18+, TypeScript, Tailwind CSS, Shadcn UI (UI组件), TanStack Table (表格), React Flow (绘图).
### 后端: Django 5.0+, Django REST Framework (DRF), SimpleJWT (认证).
### 数据库: PostgreSQL 16+.
### API: RESTful API, 遵循 OpenAPI 规范。