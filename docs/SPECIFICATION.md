# Web-Based Instrumentation Engineering Design System

## 各模块功能需求规格说明书（完善版）

### Enhanced Functional Requirements Specification V2.1

**基于 SmartPlant Instrumentation (SPI) 功能全面深度分析**

参考文档: DB Checker Guide / ERDs / Intrinsic Safety Equations / Rule Manager Guide / Sizing Equations / Import & Merger Utilities / Exporting Cables to SPEL / SP Adapter

技术栈: Django 5.2 + React 19 + TypeScript + PostgreSQL

文档版本: **V2.1（完善版 — 基于V2.0审查报告完善 + SPECIFICATION.md 对齐，可供AI集成开发环境直接编码）**

> **V2.1 变更说明**：本文件在原 V2.0 基础上，依据《V2.0 审查报告》补充了全局数据模型契约、API 契约、权限矩阵、状态机定义、关键算法实现规则、前端页面与路由、导入/导出与集成补全、测试数据与验收标准、完成定义(DoD)、推荐代码目录结构及 AI IDE 实施提示。新增或增强内容以 **【V2.1 新增】** 或 **【V2.1 增强】** 标注。
>
> **V2.1 补充能力整合说明**：进一步评估 `SPECIFICATION.md` 第 3228 行至文末后，新增**第六部分（补充能力规格）**与**附录 A/B**，整合了 V2.0/V2.1 此前缺失的跨模块能力：版本控制（GlobalRevision/EntityRevision/AuditLog/变更标记/变更通知/变更审批/版本对比）、国际化（12 语言 + RTL）、并发控制（记录级 EditLock + 乐观锁 + WebSocket 实时同步）、P&ID 数据集成（SmartPlant/AVEVA/DEXPI/数据库直连/增量同步/一致性检查）、非功能性需求（性能/安全/可用性/可维护性）。V2.0 原始规格的「§8 Excel 导入导出基础」因已被模块8(IFC)覆盖、「§4 API 规格」因已被本文件 §4.2 覆盖，仅作差异协调（见 §6.5.5），不重复整合。
>
> **V2.1 Instrument Schedule 模板吸收说明（2026-09-18）**：对项目方现行 Excel 版《Instrument Schedule》模板（WSP 血统 rev 3.9，138 列 Schedule + 291 条类型码 Instrument Type 主表 + Piping Index + 6 组下拉列表）做工程实践分析后，将以下内容吸收进本规格，全部以 **【V2.1 增强·IS模板】** 标注：(1) 模块2 COMPONENT 新增 SIL/SIF、危险区域、安装/物理位置、采购/安装责任方、P&ID 复核版本、故障动作、早期柜位分配、仪表风引用、变更原因/所在版次等字段；新增 **InstrumentTechnologyType 双层编码**（§2.1.1.1）与 **TagIOAllocation（PCS/SIS × 信号类型）子表**（§2.1.1.2）；新增 IDX-16 I/O 分配、IDX-17 完整度指示器、IDX-18 P&ID 复核标记；IDX-15 新增 I/O 汇总与按类型计数两个报告。(2) 模块3 过程数据模板改以技术类型适用性掩码为键，新增 26 项 **过程数据字段目录**（含 design_pressure/design_temperature 两项设计条件）（含 ISA 75.01 / API 520 阀类选型输入），区分 design_*（自 PipingClass 只读继承）与 operating_*。(3) 模块9 新增 **§9.2 PipingClass 配管等级主表**（DDP-11~13）。(4) §15.5.3 NamingConvention 新增 `equipment` 段类型；ADM-05 新增 7 张支撑表。(5) §5.4 登记全部新端点（遵守决策 D3）；§4.8.1 种子、§4.12 待确认（采购扩展、SIF 实体）、第七部分 WP-04/05/13 范围同步更新。**2026-09-18 后续裁决（§4.12.1 D6–D9）**：WP-13 拆分解除 WP-05 隐式依赖；采购/成本扩展纳入范围（§2.5）；SIF 建为一级实体并按 IEC 61511 语义修正 COMPONENT 的 SIL 字段（§2.4，`sil_capability` + 派生 `required_sil`）；技术类型与字段目录种子文件生成并纳入交付。**2026-09-18 项目方指示补充（D10–D12）**：§15.8 数据模型定制（任意 Item Type 自定义字段 / 自定义表 UDT / 系统字段属性覆盖 / 统一字段元数据服务，元数据驱动不做 DDL）；模块8 Excel/CSV 导入明确化（源格式、全目标表、导入模板下载、自动映射、预置 Instrument Schedule Link、大文件异步）；§6.6 交付物模板库（16 类 C&I 交付物注册、用户模板导入 XLSX/DOCX/SVG/DXF、统一占位符、渲染引擎、图框标题栏、版本与默认）。**2026-09-18 完整性收口（D13 及结构修复）**：(1) **恢复 6 个模块的完整需求与数据模型**——模块9 DDP(§9.0 + DDP-01~10)、模块10 WIR(§10.1 + WIR-01~25)、模块11 LOOP(LOOP-01~10)、模块12 HU(§12.1 + HU-01~08)、模块13 RULE(RULE-01~10)、模块14 DBI(DBI-01~05 + §14.2)——此前仅以"保持 V2.0 内容不变"占位，导致本文件对 agent 不自足；(2) 消除 §5.1–5.4 编号冲突（模块5 子节改为 §M5-1~M5-5）并新增编号约定说明；(3) 新增 §4.5.1 计算测试向量权威来源规则(D13，安全关键)、§5.1.1 环境与版本锁定、§5.5 模型清单、§5.6 可追溯性、附录 C 术语表、§4.4.10 尺寸数据状态机；(4) DoD 扩充至 12 条；(5) 修复全部悬空引用与 §9.1 重号。**2026-10-04 WSP Datasheet 模板库吸收（D14）**：全量提取项目方现行 71 份 Excel datasheet 模板（69 技术类型 + Generic，IGN104 命名），产出 `spec_field_catalog.json`（593 字段）、`wsp_template_bindings.json`（单元格级绑定）、`WSP_TEMPLATE_AUDIT.md`（审计）。规格侧新增 **§4.4.11 文档版次生命周期**（询价→报价→订货→施工→竣工，与 SpecSheet/Procurement 三状态机绑定）、改写 **SPEC-04 文档编号规则**（ISO 19650 分段）、正式化 **SPEC-03 字段目录**、新增 **SPEC-12~16**（五态占位语义、供货文档要求、回标对比、多页分区、模板导入绑定）、**§6.6** 增 DTL-08 模板库健康度检查与 `BID_TABULATION` 交付物、**§4.1.15** 种子清单。**明确不吸收**：138 列扁平化、PCS/SIS 双列块、Norm1/Norm2 平铺、Fluid/MoC 逐行冗余、自由文本 Loop/Line/Units、Material Feeding 项目专用矩阵。

---

> **编号约定（读者与 agent 必读）**：本文件存在两套编号——**第 N 部分下的 §N.x**（如 §4.2 API 契约、§5.4 API 端点规划、§6.6 交付物模板库）与**模块内子节**（如 §2.1.1.1、§9.2、§15.8）。二者仅在"模块号 = 部分号"时可能混淆，全文已消除唯一的冲突点：模块5 的五个子节改用 **§M5-1 ~ §M5-5**。因此：**`§5.x` 一律指第五部分**，`§M5-x` 指模块5。引用模块时写"模块N"，引用需求时写需求 ID（如 WIR-12）。

## 目录

- 第一部分：基础工程模块 (Basic Engineering)
  - 模块1：工程数据编辑器 (EDE)
  - 模块2：仪表索引 (IDX)【V2.1 增强·IS模板：技术类型双层编码 / TagIOAllocation / IDX-16~18 / §2.4 SIF(D8) / §2.5 Procurement(D7)】
  - 模块3：过程数据 (PD)【V2.1 增强·IS模板：字段目录 / 适用性掩码 / design·operating 分组】
  - 模块4：规格书 (SPEC)【V2.1 增强·WSP模板：字段目录 / 五态占位 / 回标对比 / SPEC-12~16】
  - 模块5：计算 (CALC)
  - 模块6：文档管理 (DOC)
  - 模块7：系统集成接口 (INT)
  - 模块8：数据导入/导出 (IFC)【D11：Excel/CSV 导入明确化，IFC-09~11】
- 第二部分：详细工程模块 (Detailed Engineering)
  - 模块9：尺寸数据与管道 (DDP)【V2.1 增强·IS模板：§9.2 PipingClass】
  - 模块10：接线设计 (WIR)
  - 模块11：回路图 (LOOP)
  - 模块12：Hook-Up管理 (HU)
- 第三部分：规则与管理模块
  - 模块13：业务规则引擎 (RULE)
  - 模块14：数据库完整性管理 (DBI)
  - 模块15：系统管理 (ADM)【V2.1 重大更新 — 对齐 SPECIFICATION.md；§15.8 数据模型定制 D10】
- **第四部分：全局工程实施契约 【V2.1 新增】**
  - 4.1 全局数据模型契约
    - 4.1.15 工程种子文件清单【D14】
  - 4.2 API 契约
  - 4.3 权限矩阵
  - 4.4 状态机定义
    - 4.4.9 ProcurementInfo 采购状态机【D7】
    - 4.4.10 ComponentDimensional 尺寸数据状态机【DDP-06】
    - 4.4.11 文档版次生命周期 (Issue Purpose)【D14】
  - 4.5 关键算法和公式实现规则
    - 4.5.1 计算测试向量的来源与权威【D13】
  - 4.6 前端页面与路由
  - 4.7 导入/导出与集成补全
  - 4.8 测试数据与验收标准
  - 4.9 完成定义 (DoD)
  - 4.10 推荐代码目录
  - 4.11 AI IDE 实施提示
  - 4.12 待项目方确认事项
- 第五部分：技术架构与数据模型定义
  - 5.1.1 运行环境与版本锁定
  - **5.5 模型清单 / 5.6 需求可追溯性【V2.1 新增】**
- **第六部分：补充能力规格（对齐 V2.0 原始规格（`Instrumentation_System_Functional_Requirements_Enhanced_V2.pdf`））【V2.1 新增】**
  - 6.1 版本控制 (Version Control)
  - 6.2 国际化 (i18n)
  - 6.3 并发控制 (Concurrency Control)
  - 6.4 P&ID 数据集成
  - 6.5 非功能性需求
  - **6.6 交付物模板库 (Deliverable Template Library)【D12】**
- **第七部分：AI Agent 交付协议**
  - 7.1 交付模式总则
  - 7.2 工作包分解（WBS）
  - 7.3 任务级验证协议（每个 WP 必须全绿）
  - 7.4 spec 入库与上下文策略
  - 7.5 Agent 分工（Devin 看板内）
- **附录 A：仪表功能代码（ISA S5.1）**
- **附录 B：仪表类型代码**
- **附录 C：术语表（Glossary）【V2.1 新增】**

---

# 第一部分：基础工程模块 (Basic Engineering)

本部分功能需求来源于 SPI Basic Engineering Users Guide、Sizing Equations、Rule Manager Guide、Import and Merger Utilities Guide、SP Adapter Guide 等核心文档的深度分析，涵盖仪表工程的基础数据管理、过程数据、规格书、计算、文档管理及集成接口功能。每条需求均细化至可直接编码实现的粒度。

---

## 模块1：工程数据编辑器 (Engineering Data Editor)

工程数据编辑器 (EDE) 提供仪表工程数据的全局视图，允许用户从单一界面浏览、编辑和管理各类工程数据。在新系统中，该模块将作为核心的数据网格编辑平台，支持灵活的查询构建和自定义视图。

### 1.1 查询构建器 (Query Builder)

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| EDE-01 | 提供可视化查询构建界面，用户无需SQL知识即可通过图形化方式选择Item Types（仪表、回路、管线、文档等），定义它们之间的关系，并选择要显示的属性字段。Item Types列表须包含：Instrument(COMPONENT表)、Loop(LOOP表)、Line(LINE表)、Equipment(APPARATUS表)、Cable(CABLE表)、Panel(PANEL表)、Document(DRAWING表)、Spec(SPEC_SHEET_DATA表)、ProcessData(PD_GENERAL表)等全部核心对象。 | React拖拽式查询设计器 + Django ORM动态查询。前端使用ReactFlow绘制关系图。后端通过Django ORM将可视化查询转换为SELECT语句。 |
| EDE-02 | 支持Item Types之间的关系定义：Parent-Child关系须基于ERD定义的外键关系，如COMPONENT→LOOP(通过loop_id)、COMPONENT→LINE(通过line_id)、COMPONENT→DRAWING(通过dwg_id)、COMPONENT→SPEC_SHEET_DATA(通过cmpnt_id)、PANEL→PANEL_STRIP(通过panel_id)、CABLE→WIRE_GROUP→WIRE(通过cable_id/wire_group_id)。关系连线需标注基数(1:1, 1:N, M:N)。 | React Flow/D3.js关系图+DRF嵌套序列化。后端需维护items_relationship配置表记录所有合法的Item Type关联路径和对应的JOIN条件。 |
| EDE-03 | 属性资源管理器(Attribute Explorer)：当用户选择某个Item Type时，系统从数据库元数据（Django Model定义+自定义字段注册表）自动获取该类型的所有可用属性，按分组展示（基本属性/过程数据属性/接线属性/自定义字段）。支持属性搜索过滤和多选。每个属性需显示：字段名、显示标签、数据类型（String/Number/Date/Enum）、最大长度、是否必填、所属表名。 | 树形属性选择器组件+Django Model._meta内省API。自定义字段从custom_field_definitions表加载。 |
| EDE-04 | 查询预览功能：在保存查询前，用户可预览查询返回的前100条数据结果。预览需显示总记录数、执行耗时。支持在预览结果中对列进行临时过滤（文本列支持contains/equals/starts_with、数字列支持>/</>=/<=/<>/=、日期列支持范围选择）。 | DRF分页API(PageNumberPagination, page_size=100)+AG Grid预览面板。后端使用Django ORM .annotate()统计总数。 |
| EDE-05 | 查询保存与组织：将查询定义（选中的Item Types、关系定义、选中的属性列表、过滤条件、排序规则）序列化为JSON存储到saved_queries表中。查询元数据包含：名称、描述、创建人、创建时间、最后修改时间、所属文件夹、是否共享。支持按文件夹树形组织查询。 | PostgreSQL JSONB字段存储查询定义JSON。DRF ModelSerializer处理CRUD。前端用树形导航组件管理查询文件夹。 |

**【V2.1 增强】M1 EDE 逐模块补全要求：**

- 查询 JSON DSL：前端只提交 Query DSL，不提交 SQL；后端根据 `ItemTypeRegistry` 和 `RelationshipRegistry` 生成 ORM QuerySet；禁止任意字段名和任意 JOIN。
- 允许 JOIN 白名单：后端维护可合法 JOIN 的 Item Type 关联路径白名单，拒绝非白名单路径。
- 字段元数据 API：`GET /api/v1/ede/field-metadata/{item_type}/` 返回所有可用字段的 schema（名称、类型、是否可写、枚举值列表、所属表）。**D10：此端点成为 `GET /api/v1/schema/{item_type}/`（ADM-12 统一字段元数据服务）的别名，二者返回同一合并 schema（系统字段 + 覆盖 + 自定义字段）。**
- 批量编辑冲突检测：批量 PATCH 提交时每行需携带 `expected_row_version`，服务端对比 `row_version`，不匹配返回 409 CONFLICT 并标识冲突行。
- 复杂过滤 AST：`filter_ast = {op:"AND", children:[condition|group]}`；`condition={field, operator, value, data_type}`；后端递归转换为 Django Q 对象。
- 保存视图 schema：视图配置 JSON 需包含 `schema_version` 字段，便于后续结构升级迁移。
- 撤销/重做状态格式：布局历史以 `{action_type, timestamp, before_state, after_state}` 结构存储，最多50步，会话内维护。

### 1.2 EDE数据视图

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| EDE-06 | 支持从查询结果生成EDE视图，视图以数据网格形式展示。支持列排序（升序/降序）、多列排序（Shift+点击追加排序列）。排序参数通过URL查询参数传递给后端API（?ordering=field1,-field2）。所有排序在服务端执行（ORDER BY），不做前端排序。 | AG Grid Enterprise + DRF OrderingFilter。后端API接受ordering参数，映射到Django ORM .order_by()。 |
| EDE-07 | 列过滤功能：每列标题区域提供过滤器图标，点击展开过滤面板。文本类型列提供多值勾选过滤（从该列所有不重复值中选择），已过滤的列在图标上显示蓝色标记。过滤参数通过URL查询参数持久化（?filter_field=value1,value2）。支持清除单列过滤和清除全部过滤。 | AG Grid Set Filter + DRF django-filter。后端使用DjangoFilterBackend，每个可过滤字段自动生成CharInFilter。 |
| EDE-08 | 列分组功能：将数据按一个或多个列进行分组展示，拖拽列标题到网格上方的分组区域即可分组。分组后显示每组的记录数统计。支持多级嵌套分组。分组定义保存到视图配置中。 | AG Grid Row Grouping。分组状态通过AG Grid columnApi.getColumnState()序列化保存。 |
| EDE-09 | 数据编辑功能：在网格中直接编辑数据字段值。编辑规则：只读字段（如计算字段、系统字段）设置为不可编辑（灰色背景）；可编辑字段（白色背景）支持单击进入编辑模式。支持单元格级别内联编辑、整行编辑模式、批量复制/粘贴（从Excel复制多行数据到网格）。编辑后的单元格用黄色背景标记为"已修改"，用户点击"保存"按钮批量提交所有修改。后端通过PATCH /api/v1/ede/batch-update/接受JSON数组批量更新。 | AG Grid可编辑单元格(editable:true) + DRF批量更新API。后端使用bulk_update()优化性能。事务内执行所有更新，任一失败则全部回滚。 |
| EDE-10 | 复杂过滤器(Complex Filter)：支持构建多条件组合过滤。每个过滤条件由四部分组成：字段名(Column)、操作符(Operator)、值(Value)、逻辑连接(And/Or)。操作符列表：Contains, Not Contains, Equal To, Not Equal To, Starts With, Ends With, Greater Than, Less Than, Greater Than or Equal, Less Than or Equal, Is Empty, Is Not Empty, In List。支持过滤条件的括号分组（嵌套And/Or逻辑）。 | 自定义React过滤器构建器组件 + Django Q对象动态构建。后端将过滤器JSON递归解析为Q对象链。 |
| EDE-11 | 视图属性管理：每个EDE视图包含以下可配置属性：视图名称(最大50字符)、视图类型(Standard/Custom)、描述(最大200字符)、是否为默认视图(每个用户仅一个默认视图)、重复值抑制开关、列宽配置、列顺序配置、冻结列数(前N列冻结不滚动)。 | 用户级视图配置存储到ede_view_config表（user_id, view_name, config_json）。AG Grid columnApi状态序列化。 |
| EDE-12 | 布局历史(Layout History)：记录用户在视图中的操作历史（列排序变更、过滤条件变更、列顺序变更、分组变更），支持Ctrl+Z撤销和Ctrl+Y重做。布局历史在浏览器会话内维护（最多保留50步），不跨会话持久化。 | React useReducer状态管理 + 历史栈模式。每次布局变更push到历史数组，undo/redo操作移动指针。 |
| EDE-13 | 树视图和搜索：EDE视图操作面板左侧提供树形导航（按工厂层级Plant→Area→Unit展示Item分组）和全局搜索输入框。搜索支持按Tag Number、Loop Number、Description等字段进行模糊匹配，输入延迟300ms后自动触发搜索API。搜索结果在网格中高亮并定位到匹配行。 | 树形组件(Ant Design TreeSelect) + Debounced搜索API(DRF SearchFilter)。后端使用PostgreSQL icontains或Full Text Search。 |

---

## 模块2：仪表索引 (Instrument Index Module)

仪表索引模块是系统的核心数据管理模块，负责仪表标签(Tag Number)、控制回路(Loop)、仪表类型(Instrument Type)等基础数据的创建和维护。以下需求基于SPI ERD中的COMPONENT、LOOP、COMPONENT_FUNCTION_TYPE等核心数据表关系深度细化。

### 2.1 仪表标签管理

#### 2.1.1 数据模型定义（基于SPI ERD）

仪表标签核心数据表COMPONENT的关键字段和关系定义如下。开发时须严格按此数据模型创建Django Model：

| 字段/关系 | 数据类型与约束 | 说明 |
|-----------|---------------|------|
| cmpnt_id | BigAutoField, PK | 仪表标签唯一标识（系统自动生成） |
| cmpnt_name | CharField(max=50), UNIQUE per unit | 完整标签号名称，如 101-FT-100 |
| cmpnt_func_type_id | ForeignKey → ComponentFunctionType | 仪表类型ID |
| loop_id | ForeignKey → Loop, nullable | 所属回路ID |
| line_id | ForeignKey → Line, nullable | 所关联管线ID |
| appar_id | ForeignKey → Apparatus, nullable | 所关联设备ID |
| dwg_id | ForeignKey → Drawing, nullable | P&ID图纸号 |
| proc_func_id | ForeignKey → ProcessFunction | 过程功能ID |
| cmpnt_cat_id | IntegerField, choices | 标签类别(Conventional=0, Telecom=1, FF=2, Typical=3...) |
| cmpnt_serv | CharField(max=100), nullable | 服务描述 |
| io_type | CharField(max=20), nullable | I/O类型(AI/AO/DI/DO/PI/SI等)。**【V2.1 增强·IS模板】降级为派生摘要字段**：由 `TagIOAllocation` 子表（§2.1.1.2）汇总生成，不再手工录入 |
| unit_id | ForeignKey → Unit, NOT NULL | 所属单元 |
| **technology_type_id** | **ForeignKey → InstrumentTechnologyType, nullable** | **【V2.1 增强·IS模板】仪表技术类型**（如 FET50=Coriolis、FE10=孔板、LET75=雷达），与 ISA 功能码分层，见 §2.1.1.1。规格书表单与过程数据模板以此为键 |
| **sil_capability** | **IntegerField, choices(1–4), nullable** | **【V2.1 增强·IS模板 / 决策 D8】设备 SIL 能力**（IEC 61508 系统能力 SC，或 IEC 61511 §11.5 prior-use 论证结果）。**注意**：SIL 是 SIF 的属性而非设备属性，设备只有"能力"。IS 模板每 Tag 一列的「SIL」拆为本字段（设备能力）与派生字段 `required_sil`（下行） |
| *required_sil*（派生，只读） | *IntegerField* | **【决策 D8】** = 该 Tag 参与的全部 SIF（经 `SIFElement`，§2.4.2）的 `sil_target` 最大值；无 SIF 参与时为 null。规则 `sil_capability ≥ required_sil`，否则 DBI `IDX_SIL_CAPABILITY_BELOW_REQUIRED`。IS 模板「Trip/Interlock No.」列由 `SIFElement` 反向关系提供，索引视图显示为 `sif_display`（逗号连接的 SIF 编号） |
| **hazardous_area_id** | **ForeignKey → AreaClassification, nullable** | **【V2.1 增强·IS模板】危险区域分类**（如 Zone 1 IIB T4）。默认从所属 Unit/Area 继承，Tag 级可覆盖 |
| **mounting_location_id** | **ForeignKey → InstrumentLocation, nullable** | **【V2.1 增强·IS模板】安装位置类型**（Field-Local / Field-In Line / Field-In Vessel / Junction Box / Panel / MCC） |
| **physical_location_id** | **ForeignKey → PhysicalLocation, nullable** | **【V2.1 增强·IS模板】物理位置**（Building/Floor/Room，如 Mezzanine Floor）。与 PlantHierarchy 的工艺层级正交 |
| **procured_by_id** | **ForeignKey → ResponsibleParty, nullable** | **【V2.1 增强·IS模板】采购责任方**（Instrument Engineer / Package Plant-Vessel / System Integrator …），划分供货界面 |
| **installed_by_id** | **ForeignKey → ResponsibleParty, nullable** | **【V2.1 增强·IS模板】机械安装责任方** |
| **pid_revision_checked** | **CharField(max=10), nullable** | **【V2.1 增强·IS模板】本 Tag 最后复核所依据的 P&ID 版本**（P&ID Issue）。与 Drawing 当前版本不一致时索引视图高亮"待复核" |
| **fail_action** | **CharField, choices(OPEN/CLOSE/LAST/NA), nullable** | **【V2.1 增强·IS模板】阀类故障动作**。安全审查需在索引级可见，故提升为一级字段而非 spec_data |
| **target_system_panel_id** | **ForeignKey → Panel, nullable** | **【V2.1 增强·IS模板】早期目标系统/柜位分配**（RIO-01…/PCS-001/PLC Panel/MCC）。WIR 详细分配完成后由 DBI 检查项对账 |
| **utility_air_supply_ref** | **CharField(max=30), nullable** | **【V2.1 增强·IS模板】仪表风支管引用**（Air Header，如 IAM-002/1），气动执行机构用 |
| **exotic_moc** | **BooleanField, default=False** | **【V2.1 增强·IS模板】特殊材质标记**（成本驱动因素） |
| **change_reason** | **CharField(max=200), nullable** | **【V2.1 增强·IS模板】本行最近一次变更原因**（如"P&ID update"），索引视图可见 |
| **last_changed_in_issue_id** | **ForeignKey → GlobalRevision(public), nullable** | **【V2.1 增强·IS模板】本行在哪一版文件（GlobalRevision）中最后变更**。跨 schema FK（租户→public，同 User FK 模式）。配合 §6.1 变更标记：新增红字、删除蓝色删除线保留至下一版发布 |
| ~~domain_id~~ | — | **【V2.1 更新】移除**：COMPONENT 属租户 schema 表，由 ProjectTenant Schema 边界天然隔离，无需 domain_id/project_id 判别列（见 §4.1.4） |
| **row_version** | **IntegerField, default=1** | **【V2.1 新增】乐观锁版本号** |
| **is_deleted** | **BooleanField, default=False** | **【V2.1 新增】软删除标记** |
| **created_at** | **DateTimeField, auto_now_add** | **【V2.1 新增】创建时间** |
| **created_by** | **ForeignKey → User** | **【V2.1 新增】创建人** |
| **updated_at** | **DateTimeField, auto_now** | **【V2.1 新增】更新时间** |
| **updated_by** | **ForeignKey → User** | **【V2.1 新增】更新人** |

> **【V2.1 增强·IS模板】来源说明**：本节及后续标注 **「IS模板」** 的内容，源自对项目方现行 Excel 版《Instrument Schedule》模板（WSP 血统，模板修订 3.9，138 列 Schedule + 291 条类型码的 Instrument Type 主表）的工程实践吸收。原则：吸收其**数据字段与工程纪律**，不复制其 Excel 扁平化妥协（138 列单行、PCS/SIS 双列块重复、Norm1/Norm2 平铺、Fluid/MoC 逐行冗余）——这些在 Open Instrument 中分别由子表、多 Case、PipingClass 派生与 EDE 视图承担。

##### 2.1.1.1 InstrumentTechnologyType（仪表技术类型 — 双层编码）【V2.1 增强·IS模板】

**设计动机**：ISA S5.1 功能字母（FT）标识 Tag 的**功能**并构成位号；技术类型代码（FET50 = Coriolis、FE10 = 孔板、LET75 = 雷达）标识**实现技术**。同为 FT 的 Coriolis 与孔板需要不同的规格书表单、不同的过程数据字段和不同的默认 I/O。原 `ComponentFunctionType.code` 将两层合并，无法支撑 SPEC-04（按类型选表单）与 PD-03（按类型选参数模板）的精确映射。

| 字段 | 数据类型与约束 | 说明 |
|------|---------------|------|
| id | BigAutoField, PK | |
| code | CharField(max=10), UNIQUE per tenant | 技术类型代码，如 FET50 / UCV10 / KCV20 / LET75 / QET35。以 `*` 开头的为非仪表辅助项（电缆、面板、文档等），`is_instrument=False` |
| name | CharField(max=100) | 描述，如 "FLOW ELEMENT/TRANSMITTER-CORIOLIS FLOWMETER" |
| function_type_id | ForeignKey → ComponentFunctionType | 所属 ISA 功能类型（FT/FE/LT/…），一个功能类型下挂多个技术类型 |
| category | CharField, choices | 15 值枚举，见本节末 |
| is_instrument | BooleanField, default=True | False 表示辅助项（电缆、面板、文档），不计入仪表数量统计 |
| default_io_profile | JSONField | 默认 I/O 数量 `{"AI":1,"AO":0,"DI":0,"DO":0,"PI":0}`，创建 Tag 时预填 `TagIOAllocation`。取代 IDX-04 Profile 中的单值 `default_io_type` |
| process_data_applicability | JSONField | 过程数据字段适用性掩码 `{"<field_key>": "REQUIRED" \| "OPTIONAL" \| "NA"}`，驱动 PD-03 表单灰显与 IDX-17 完整度计算。**种子数据**从 IS 模板 Instrument Type 表导入（空白→REQUIRED，"N/A"→NA） |
| default_spec_form_id | ForeignKey → SpecForm, nullable | 默认规格书表单（SPEC-04 生成时优先取此值，回退到 function_type 级默认） |
| is_active / display_order | | |
| created_at/by, updated_at/by, row_version | | 按 §4.1.1 |

约束：`(function_type_id, code)` 组合有效——技术类型的 `code` 前缀应与功能类型一致（规则引擎软校验，允许项目方例外）。

**【决策 D9 · 种子文件已生成并纳入交付】**

| 文件 | 路径 | 内容 |
|------|------|------|
| `technology_types.json` | `backend/apps/instruments/fixtures/technology_types.json` | 291 条技术类型（schema_version=1）：`code, name, function_prefix, function_type_code, category, is_instrument, default_io_profile{AI,AO,DI,DO,PI}, process_data_applicability{26 字段键: REQUIRED\|NA}, needs_review, review_note, display_order`；顶层含 `conventions[]`（生成约定）与 `review_summary` |
| `process_data_field_catalog.json` | `backend/apps/process_data/fixtures/process_data_field_catalog.json` | 26 个过程数据字段：`key, label_zh, label_en, group, structure(MNM/MM/LH/S), uom_category, condition_class(design/operating), derived_from_piping_class` |
| `technology_types_REVIEW.md` | `docs/seeds/technology_types_REVIEW.md` | 131 条 `needs_review=true` 条目清单与原因，供项目方逐条确认 |

**加载方式**：管理命令 `python manage.py load_engineering_seeds --tenant <schema>`（按租户 schema 执行；ProjectTenant 创建后由 django-tenants `post_schema_sync` 信号自动调用）。加载逻辑：`function_type_code` 以自然键匹配 `ComponentFunctionType.code`，不存在则创建为 `is_system=False` 的待确认功能类型并写日志；`function_type_code=null` 的阀类条目不关联功能类型（创建 Tag 时由 `Loop.function` 决定）。幂等：按 `code` upsert，不覆盖项目方已手改（`updated_by` 非 system）的记录。

**生成约定（来自种子文件 `conventions`，实施须遵守）**：
1. **分体式元件 + 转换器**（如 FE50 + FT50）：过程数据掩码挂在接液**元件**（FE*/LE*/TE*）上，转换器（FT*/LT*/TT* 的 *CONVERTER 型）全 NA；一体式（FET*/LET*/TET*）掩码挂一体式代码。因此分体式安装须为元件与转换器分别建 Tag，IDX-17 完整度才能正确计算。
2. `*` 前缀为非仪表辅助项（电缆/面板/JB/软件点/文档），`is_instrument=false`，不计入数量统计，默认 I/O 为 0。
3. 阀类 `function_type_code=null`（23 条）：ISA 功能字母由回路测量变量决定。
4. ES2x/ES3x/ES5x 为 MCC/成套设备接口信号点（INTERFACE_SIGNAL），无流体过程数据，全 NA。
5. 模板中 4 行未打掩码（ES20/ES29/LT80/QT40）已按泛型父类型继承并标 `needs_review`；UT10（压力/温度组合变送器）全 NA 疑为模板遗漏，已标注。
6. `OPTIONAL` 值在模板中不存在，预留给项目方调整。

`category` 枚举据实际数据扩充为 15 值：TRANSMITTER / ELEMENT / SWITCH / INDICATOR / CONTROLLER / CONTROL_VALVE / ON_OFF_VALVE / RELIEF_VALVE / ANALYZER / INTERFACE_SIGNAL / SIGNAL_CONDITIONING / ALARM_DEVICE / ACCESSORY / AUXILIARY / PLACEHOLDER。种子中的类别分布：TRANSMITTER 70、SWITCH 46、INDICATOR 30、ELEMENT 29、AUXILIARY 28、ANALYZER 24、INTERFACE_SIGNAL 23、CONTROL_VALVE 12、ON_OFF_VALVE 12、CONTROLLER 7、SIGNAL_CONDITIONING 5、ALARM_DEVICE 2、PLACEHOLDER 2、ACCESSORY 1。

##### 2.1.1.2 TagIOAllocation（Tag I/O 分配子表）【V2.1 增强·IS模板】

**设计动机**：一个 Tag 可同时拥有多种 I/O（如变送器 1×AI + 1×DO 诊断触点），且可同时接入 **PCS（基本过程控制）与 SIS（安全仪表系统）**。IS 模板为此复制了两组 10 列；Open Instrument 以带 `control_system` 维度的子表表达，并在索引早期（接线设计前）即可做 I/O 数量估算，WIR 模块详细分配后由 DBI 对账。

| 字段 | 数据类型与约束 | 说明 |
|------|---------------|------|
| id | BigAutoField, PK | |
| cmpnt_id | ForeignKey → Component, NOT NULL | 所属 Tag |
| control_system | CharField, choices | PCS / SIS / F&G / OTHER |
| signal_kind | CharField, choices | AI / AO / DI / DO / PI（脉冲）/ SI（串行/总线） |
| count | PositiveSmallIntegerField, default=1 | 该类信号数量 |
| connection_type | ForeignKey → SignalConnectionType | 信号接入方式：HW（硬线）/ PB（Profibus）/ FF / MB（Modbus）/ HT（HART）/ ET（Ethernet）/ ASi / PA / RS232 / RS485 |
| is_intrinsically_safe | BooleanField, default=False | 是否本安回路（联动 CALC-11/12 本安计算） |
| wire_system | CharField, choices, nullable | 2-Wire / 3-Wire / 4-Wire（模拟量适用） |
| digital_signal_type | ForeignKey → DigitalSignalType, nullable | VFC（无源触点）/ 24VDC / Namur / Optoisolator（DI/DO 适用） |
| cs_tag_id | ForeignKey → CSTag, nullable | WIR 详细分配后回填，形成早期估算 ↔ 详细分配的闭环 |
| notes | CharField(max=200), nullable | |

约束：`(cmpnt_id, control_system, signal_kind, connection_type)` 唯一。**派生规则**：`Component.io_type` = 各行 `signal_kind` 去重后以 `/` 拼接（如 `AI/DO`），由 Service 层在子表变更时重算，禁止手工编辑。

#### 2.1.2 功能需求

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| IDX-01 | 仪表标签创建：支持按ISA S5.1命名规范创建仪表标签号。标签名由多个可配置段(Segment)组成，段定义存储在naming_convention_config表中。创建时系统自动验证：(1)段格式合规 (2)仪表类型缩写有效 (3)同一Unit内标签名唯一。批量创建时支持自动递增序号。 | React多段输入表单+后端NamingConventionValidator类。Django Model clean()方法执行唯一性校验。 |
| IDX-02 | Tag Number属性编辑：弹出标签属性对话框，编辑以下属性分组：【基本信息】功能类型、技术类型、服务描述、P&ID图纸号与复核版本(pid_revision_checked)、测量范围等；【关联信息】管线号、设备号、控制系统标签(CS Tag)、早期目标柜位(target_system_panel)；【安全信息】设备 SIL 能力(sil_capability)、所属 SIF（只读，经 §2.4 维护）与派生 required_sil、危险区域分类、本安标记、故障动作；【位置与责任】安装位置类型、物理位置、采购责任方、安装责任方；【I/O 分配】TagIOAllocation 子网格（§2.1.1.2）；【制造商信息】制造商、型号、序列号、特殊材质标记；【自定义字段】从custom_field_definitions表加载的用户自定义字段。 | React动态表单(react-hook-form) + DRF ModelSerializer；I/O 分配用嵌套 Serializer + AG Grid 子网格。 |
| IDX-03 | 仪表类型管理（双层）：**功能类型**（COMPONENT_FUNCTION_TYPE：FE/FT/FV/PT/TT/LT…，ISA S5.1，过程功能 proc_func_id 0-7）与**技术类型**（InstrumentTechnologyType：FET50/UCV10/LET75…，§2.1.1.1）分别维护。技术类型页面提供 default_io_profile 编辑器与 process_data_applicability 矩阵编辑器（行=过程数据字段，列=REQUIRED/OPTIONAL/NA）。系统预置 ISA 功能类型与 IS 模板 291 条技术类型。删除任一层类型时检查引用完整性。 | 两级 CRUD API + 引用完整性校验 + 矩阵编辑组件。 |
| IDX-04 | 仪表类型Profile定义：为每种**技术类型**（回退：功能类型）创建Profile配置，定义创建时自动触发的关联创建规则：auto_create_spec（取 default_spec_form_id）, auto_create_wiring, auto_create_cs_tag, auto_create_process_data（按 process_data_applicability 建 REQUIRED 字段占位）, **default_io_profile（取代原 default_io_type，创建时按 `{AI,AO,DI,DO,PI}` 数量批量生成 TagIOAllocation，control_system 默认 PCS）**。 | Profile配置界面 + InstrumentCreationService。 |
| IDX-05 | 自定义字段和表(UDF/UDT)：项目管理员（Administrator/Project Engineer）可为**任意** Item Type（Instrument/Loop/Line/Cable/Panel/Terminal/SIF/PipingClass/…）定义自定义字段与自定义表，并覆盖系统字段属性。**完整规格见 §15.8 数据模型定制（决策 D10）**：字段定义存储在租户 schema 的 `CustomFieldDefinition`，值存 JSONB `custom_data`；自定义表以 `CustomTable/CustomTableRow` 通用行存储；全链路（表单/网格/EDE/导入导出/报告模板/API/规则）生效。 | Django JSONField(custom_data) + 统一字段元数据服务（ADM-12）+ 动态表单字段渲染。 |
| IDX-06 | 设备关联：仪表标签关联设备(APPARATUS表)。支持从标签属性对话框创建新设备或从已有设备列表中选择。 | 设备表CRUD + ForeignKey关联。 |
| **IDX-16** | **【V2.1 增强·IS模板】I/O 分配管理**：在 Tag 上维护 `TagIOAllocation` 子表（§2.1.1.2）。创建 Tag 时按技术类型 `default_io_profile` 预填；支持逐行增删改、按 PCS/SIS 分组显示；`is_intrinsically_safe=True` 的行在本安计算（CALC-11/12）中自动纳入。WIR 模块完成 CSTag 分配后回填 `cs_tag_id`；DBI 新增检查项 **"索引 I/O 估算 vs 详细分配差异"**（按 Tag × control_system × signal_kind 比较 count 与实际 CSTag 数）。 | 嵌套 Serializer（`POST/PATCH /api/v1/instruments/{id}/io-allocations/`）+ Service 层重算 `io_type` 摘要 + DBI 检查项注册。 |
| **IDX-17** | **【V2.1 增强·IS模板】数据完整度指示器**：按技术类型 `process_data_applicability` 中 REQUIRED 的字段集合 ∪ 索引级必填字段（hazardous_area、mounting_location、procured_by、至少 1 行 IOAllocation 等，项目可配置），计算每个 Tag 的 `completeness_pct` 与缺失字段清单。索引视图以进度条列展示，支持按完整度过滤；报告输出"待补齐字段清单"。落实 IS 模板 Guide notes"所有单元格须填写，不适用填 N/A"的纪律，并支撑 FEED→详细设计的阶段推进度量。 | 派生字段（不落库或落缓存列 + 信号重算）；`GET /api/v1/instruments/{id}/completeness/`。 |
| **IDX-18** | **【V2.1 增强·IS模板】P&ID 版本复核标记**：Tag 记录 `pid_revision_checked`；当关联 Drawing 的当前 revision 高于该值时，索引视图标记"P&ID 已升版，待复核"，并提供批量"确认复核至当前版"操作（写入新版本号 + 审计）。与 §6.4 PID-06 一致性检查互补（PID-06 比对数据差异，本项跟踪人工复核状态）。 | 派生比较 + 批量确认 API `POST /api/v1/instruments/confirm-pid-revision/`。 |

**【V2.1 增强】M2 仪表索引逐模块补全要求：**

- 标签命名校验器伪代码：按 `NamingConventionConfig.segments` 顺序拼接；每段先做类型校验、长度校验、必填校验、枚举校验，再做唯一性检查；批量创建在事务内锁定同 Unit 的序号范围。
- 批量创建输入输出：`POST /api/v1/instruments/batch/` 输入 `{items: [{tag_segments, unit_id, ...}], options: {auto_increment: true}}`；输出 `{created: [...], errors: [{row, code, message}]}`。
- 复制回路事务边界：`LoopCopyService` 在 `transaction.atomic()` 内先创建 Loop 记录，再逐个复制选中的 Component 记录（生成新 cmpnt_id 和 cmpnt_name），最后复制关联数据（含 TagIOAllocation 子表）。
- 典型回路模板结构：模板 JSON `{template_name, instruments: [{placeholder, func_type_id, technology_type_id, io_profile, relative_sequence}], default_profile_overrides: {...}}`。
- 浏览器视图 JSON schema：`{view_name, columns: [{field, width, sort_order, visible, frozen}], filters: [...], default_ordering, is_shared, schema_version}`。
- **【IS模板】I/O 分配 JSON**：`TagIOAllocation` 批量提交格式 `{allocations: [{control_system, signal_kind, count, connection_type_code, is_intrinsically_safe, wire_system, digital_signal_type_code}]}`；服务端整体替换或按 id 局部更新，事务内重算 `io_type`。
- **【IS模板】完整度计算规则**：`required_set = applicability[REQUIRED] ∪ project_required_index_fields`；`completeness_pct = filled(required_set) / |required_set| × 100`；`NA` 字段不计入分母；显式填 `"N/A"` 的字符串字段视为已填。
- **【IS模板】default_io_profile schema**：`{"AI": int, "AO": int, "DI": int, "DO": int, "PI": int}`，所有键必填、≥0；缺失键视为 0。
- **【IS模板】"Schedule 视图"预置浏览器视图**：系统预置一个名为 `Instrument Schedule` 的共享浏览器视图（IDX-13），列组与 IS 模板一致（Revision / Instrument Details / PCS I/O / SIS I/O / Specification / Line-Vessel / Process Data 摘要），用于导出与项目方现行交付物格式兼容的 Excel/PDF——**通过 EDE 视图拼装，不改变规范化模型**。

### 2.2 回路管理

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| IDX-07 | 回路创建：回路记录存储在LOOP表。关键字段：loop_id(PK)、loop_name、loop_service、loop_type_id、loop_proc_id、loop_func_id、dwg_id、unit_id。回路号命名规范与标签命名规范独立配置。回路号在Unit内唯一。 | 回路CRUD API + 命名规范引擎。 |
| IDX-08 | 回路属性编辑：编辑回路属性表单显示字段分组，包含关联仪表列表子网格。 | 回路属性表单 + AG Grid子网格。 |
| IDX-09 | 回路复制：选择源回路后展示复制选项对话框，后端在事务中执行深拷贝。 | 深拷贝API + 可选属性复制配置。 |
| IDX-10 | 典型回路和批量创建：在Reference Explorer中创建典型回路模板，批量创建>10个回路时使用Celery异步任务。 | 批量创建服务 + Celery异步任务 + WebSocket进度推送。 |
| IDX-11 | 向已有回路添加标签：在回路上下文中创建新标签时自动设置loop_id。 | 回路上下文标签创建。 |

### 2.3 浏览与搜索

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| IDX-12 | 标准浏览器视图(Standard Browser View)：网格形式展示所有仪表标签。 | AG Grid + 字段权限渲染。 |
| IDX-13 | 浏览器视图管理(Browser Manager)：用户可创建自定义浏览器视图。 | 视图配置持久化到browser_views表。 |
| IDX-14 | 搜索功能：全局搜索框支持按Tag Number、Loop Number、Service Description模糊搜索，支持通配符。 | 全文搜索API。 |
| IDX-15 | 仪表列表报告：生成仪表索引列表报告，支持PDF和Excel输出，支持修订版本比较。**【V2.1 增强·IS模板】新增两个标准报告**：(a) **I/O 数量汇总报告**——按 `control_system(PCS/SIS) × signal_kind × connection_type` 交叉统计，可按 Area / System / target_system_panel 分组，含 IS 回路数小计（对应 IS 模板 Inst Counts 透视）；(b) **仪表数量按技术类型汇总报告**——按 `InstrumentTechnologyType` 统计数量，按 `procured_by` 分列（对应 IS 模板 Inst Cost 透视的数量部分；成本列见 §4.12 待确认项）。两者均支持导出 Excel 并作为 GlobalRevision 快照留存。 | WeasyPrint(PDF) / openpyxl(Excel)报告生成；聚合查询走只读 QuerySet + `values().annotate()`。 |

### 2.4 安全仪表功能 (SIF) 管理 【决策 D8 · 一级实体】

**设计动机**：IS 模板以每 Tag 的「SIL」与「Trip/Interlock No.」两列记录安全信息，这在 IEC 61511 语义下是不精确的——**SIL 是 SIF（安全仪表功能）的属性**，设备只有"SIL 能力"；一个传感器可参与多个 SIF，一个 SIF 由多个 Tag（传感器/逻辑运算器/最终元件）以表决结构组成。Open Instrument 将 SIF 建为一级实体，Tag 与 SIF 为多对多（`SIFElement`），并为后续 SIL 验证（PFDavg/RRF 计算）预留全部输入字段，但 **SIL 验证计算本身不在 Phase 1 范围**（见 §4.12 待确认项）。

#### 2.4.1 SafetyInstrumentedFunction（SIF）

| 字段 | 数据类型与约束 | 说明（IEC 61511-1 §10 SRS 对应） |
|------|---------------|--------------------------------|
| id | BigAutoField, PK | |
| sif_number | CharField(max=50), UNIQUE per tenant | SIF / 联锁编号（IS 模板 Trip/Interlock No.），可套用 NamingConvention（entity_type=SIF） |
| name | CharField(max=200) | 名称 |
| description | TextField | 功能描述（"当…时，使…进入安全状态"） |
| unit_id | ForeignKey → PlantHierarchy(UNIT) | 所属单元 |
| hazard_ref | CharField(max=100), nullable | 危害/风险分析引用（HAZOP 节点、LOPA 场景编号） |
| cause_effect_ref | CharField(max=100), nullable | 因果图 / C&E 矩阵引用 |
| sil_target | IntegerField, choices(1–4) | 目标 SIL（来自 LOPA/风险图；IEC 61511 实践通常 ≤3） |
| demand_mode | CharField, choices | LOW_DEMAND / HIGH_DEMAND / CONTINUOUS |
| target_pfd_avg | DecimalField, nullable | 目标 PFDavg（低要求模式） |
| target_rrf | DecimalField, nullable | 目标风险降低因子（= 1/PFDavg，二者择一录入，另一自动派生） |
| target_pfh | DecimalField, nullable | 目标 PFH（高要求/连续模式） |
| safe_state | CharField(max=200) | 安全状态描述（阀关/泵停/…） |
| process_safety_time_s | DecimalField, nullable | 过程安全时间 (s) |
| required_response_time_s | DecimalField, nullable | 要求的 SIF 响应时间 (s)，须 < process_safety_time |
| trip_setpoint / trip_setpoint_uom | DecimalField / FK → UOM, nullable | 联锁设定值与单位 |
| trip_direction | CharField, choices, nullable | HIGH / LOW / DEVIATION |
| sensor_voting | CharField(max=10), nullable | 传感器表决结构（1oo1 / 1oo2 / 2oo2 / 2oo3 …） |
| final_element_voting | CharField(max=10), nullable | 最终元件表决结构 |
| logic_solver_panel_id | ForeignKey → Panel, nullable | 逻辑运算器（SIS 柜） |
| proof_test_interval_months | PositiveSmallIntegerField, nullable | 验证测试间隔 |
| mission_time_years | PositiveSmallIntegerField, nullable | 任务时间 |
| reset_type | CharField, choices | AUTO / MANUAL |
| bypass_permitted / bypass_conditions | BooleanField / TextField, nullable | 是否允许旁路及条件（IEC 61511 §11.7.4） |
| energize_to_trip | BooleanField, default=False | 通电动作（默认断电动作 de-energize-to-trip） |
| status | CharField, choices | Draft / Approved / Superseded（§4.4.8） |
| revision | CharField(max=10) | 版本 |
| created_at/by, updated_at/by, row_version, is_deleted | | 按 §4.1.1 |

约束：`target_pfd_avg`/`target_rrf` 至少一项非空（demand_mode=LOW_DEMAND 时）；`required_response_time_s < process_safety_time_s`（二者都填时）；Approved 的 SIF 修改须升版（旧版 Superseded）。

#### 2.4.2 SIFElement（SIF 组成元件 — Tag ↔ SIF 多对多）

| 字段 | 数据类型与约束 | 说明 |
|------|---------------|------|
| id | BigAutoField, PK | |
| sif_id | ForeignKey → SafetyInstrumentedFunction | |
| cmpnt_id | ForeignKey → Component | 参与的 Tag |
| element_role | CharField, choices | SENSOR / LOGIC_SOLVER / FINAL_ELEMENT / AUXILIARY（电磁阀、限位开关等） |
| voting_group | CharField(max=10), nullable | 同一表决组标识（如 "A"），用于 2oo3 分组 |
| is_redundant_channel | BooleanField, default=False | 是否为冗余通道 |
| notes | CharField(max=200), nullable | |

约束：`(sif_id, cmpnt_id, element_role)` 唯一；元件 Tag 的 `TagIOAllocation` 中须存在 `control_system=SIS` 的行（DBI 软校验 `SIF_ELEMENT_WITHOUT_SIS_IO`）。

#### 2.4.3 功能需求

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| **IDX-19** | SIF CRUD 与元件分配：创建/编辑 SIF（§2.4.1 全部字段，按 SRS 分组展示：识别 / 风险目标 / 动作与时间 / 结构 / 测试与维护）；元件分配子网格按 SENSOR → LOGIC_SOLVER → FINAL_ELEMENT 三栏拖放 Tag，自动校验 Tag 所在 Unit 与 SIF 一致。Approved 状态下修改走升版。 | `SIFViewSet` + 嵌套 `SIFElement` Serializer + 状态机（§4.4.8）。 |
| **IDX-20** | Tag 侧 SIF 视图与派生字段：Tag 详情显示所参与 SIF 列表（编号/角色/表决组）；派生 `required_sil`、`sif_display`；索引视图提供"按 SIF 过滤"。SIF 报告：SIF 清单、SIF 元件清单（对应 C&E 的设备侧）、按 SIL 目标统计，PDF/Excel 输出并纳入 GlobalRevision 快照。 | 反向关系 + 派生字段缓存；报告走 IDX-15 框架。 |

### 2.5 采购/成本扩展 (Procurement) 【决策 D7 · 纳入范围】

**设计动机**：IS 模板在 Schedule 行内维护「Status - Enquiry/Order」「Cost £」「Cost source」「Manufacturer」「Exotic MoC」，并以 Inst Cost 透视做 FEED 成本估算。纳入范围后建为 Tag 一对一扩展表，**不污染核心索引模型**，权限独立（§4.3），报告复用 IDX-15(b)。

#### 2.5.1 ProcurementInfo

| 字段 | 数据类型与约束 | 说明 |
|------|---------------|------|
| cmpnt_id | OneToOneField → Component, PK | |
| procurement_status | CharField, choices | NotStarted / Enquiry / Quoted / Ordered / Delivered / Installed / Cancelled（§4.4.9） |
| budget_cost | DecimalField(14,2), nullable | 预算成本（数值） |
| currency | CharField(3), default 项目币种 | ISO 4217（IS 模板为 GBP） |
| cost_source | CharField, choices | BudgetaryQuote / HistoricalData / VendorQuote / PurchaseOrder / Estimate |
| cost_source_ref | CharField(max=100), nullable | 报价单/合同/历史项目编号 |
| quoted_cost / po_cost | DecimalField(14,2), nullable | 报价 / 订单实际成本 |
| vendor_id | ForeignKey → Manufacturer, nullable | 供应商（可与制造商不同） |
| po_number | CharField(max=50), nullable | 采购订单号 |
| required_on_site_date / promised_delivery_date | DateField, nullable | 需求到货 / 承诺交货日期 |
| lead_time_weeks | PositiveSmallIntegerField, nullable | 交货周期 |
| is_long_lead | BooleanField, default=False | 长周期设备标记 |
| notes | TextField, nullable | |
| created_at/by, updated_at/by, row_version | | 按 §4.1.1 |

`Component.exotic_moc` 保留在 COMPONENT（既是成本驱动也是设计属性）。

#### 2.5.2 功能需求

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| **IDX-21** | 采购信息维护与成本汇总：Tag 详情增加"采购"页签（权限 §4.3）；索引浏览器视图可选加载采购列；成本汇总报告按技术类型 × 采购责任方 × 状态聚合 `budget_cost / quoted_cost / po_cost`（对应 IS 模板 Inst Cost 透视），支持按 GlobalRevision 快照比较成本变化；长周期设备清单报告。批量更新状态（如整批下单）。 | `ProcurementInfoViewSet`（嵌套于 instruments）+ 报告 `GET /api/v1/reports/cost-summary/`。 |

---

## 模块3：过程数据 (Process Data Module)

过程数据模块管理仪表和管线的工艺过程参数。

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| PD-01 | 管线过程数据管理：管线数据表LINE包含line_id, line_name, fluid_state, fluid_name, pipe_size, pipe_schedule, pipe_material等。**【V2.1 增强·IS模板】新增** `piping_class_id`（FK → PipingClass，§9.2）、`insulation_code_id`（FK → InsulationCode）、`heat_tracing_code_id`（FK → HeatTracingCode）；`fluid_name / pipe_material(MoC Type+Grade) / pipe_spec` 由 PipingClass 派生为只读，Line 上不再自由录入。 | 管线CRUD API + 过程数据关联表单；派生字段以 `@property` + Serializer 只读字段暴露。 |
| PD-02 | 过程数据属性编辑：过程条件参数按三列(Min/Normal/Max)录入。每个参数值关联独立的计量单位。**【V2.1 增强·IS模板】区分两组条件**：(a) **线路设计条件** `design_*`（Design Pressure Min/Max、Design Temp Min/Max、管道 Min/Norm/Max Working Pressure-Temp-Flow）——自 Line → PipingClass **只读继承**，仅 Mechanical Engineer 通过 PipingClass 修改；(b) **仪表操作条件** `operating_*`——仪表工程师/工艺工程师按 Case 录入。两组在表单中并列显示，设计条件灰底。 | 动态参数表单 + UOM单位转换引擎；设计条件字段 `read_only=True` 并标注来源 PipingClass 编码。 |
| PD-03 | 仪表过程数据管理：按过程功能分类管理。每种过程功能对应不同的参数模板。**【V2.1 增强·IS模板】参数模板改以 `InstrumentTechnologyType.process_data_applicability` 为主键**（§2.1.1.1），`proc_func_id × fluid_state` 矩阵作为技术类型缺失时的回退。标记 NA 的字段在表单中灰显且不可编辑；REQUIRED 字段计入 IDX-17 完整度。 | 条件渲染表单 + 字段验证规则；表单 schema 由后端 `GET /api/v1/process-data/field-schema/?technology_type=...` 下发。 |
| PD-04 | 多过程数据Case支持：每个仪表可定义多个Case（正常工况、停车工况等）。同一仪表只能有一个Governing Case。 | Case切换组件 + is_governing唯一约束。 |
| PD-05 | 过程数据复制功能：支持管线→仪表、仪表→仪表、管线→管线三种复制模式。 | 复制API + ProcessDataCopyService。 |
| PD-06 | 过程数据工作流：Draft→ReadyForReview→Approved→Revised。 | Django状态机(django-fsm) + 角色权限控制。 |
| PD-07 | 过程数据报告：生成管线/仪表过程数据表，支持修订管理。 | WeasyPrint PDF报告生成。 |
| PD-08 | 计量单位管理及转换：系统维护unit_of_measure表，支持Temperature/Pressure/Flow/Length/Density/Viscosity等类别。 | UnitConverter Python类 + conversion_factors表。 |

**【V2.1 增强】M3 过程数据逐模块补全要求：**

- Case 状态机：Draft → ReadyForReview → Approved；ReadyForReview → Rejected；Approved 修改时创建新版本（Superseded）。
- 单位换算基准：所有存储值统一以 SI 单位存储，显示时按用户偏好转换。温度转换需特殊处理（非线性偏移）。
- 字段模板矩阵：根据 `proc_func_id × fluid_state` 组合确定显示的参数集合，定义在 `process_data_field_matrix` 表中。**【IS模板】主键改为 `technology_type_id`**（回退 `proc_func_id × fluid_state`），矩阵值由 `InstrumentTechnologyType.process_data_applicability` 提供，种子数据自 IS 模板导入（291 类型 × 65 字段）。
- **【IS模板】过程数据字段目录（`process_data_field_catalog`，字段键 → 分组 / 结构 / UOM 类别）**。每个字段定义 `structure`：`MNM`（Min/Normal/Max，多 Case 各自一组）、`MM`（Min/Max）、`LH`（Lo/Hi 限值）、`S`（单值）。IS 模板的 Norm1/Norm2 不落为独立列，而由 PD-04 的两个 Case 承载，视图平铺展示。

  | 分组 | 字段键 | 结构 | UOM 类别 | 典型适用技术类型 |
  |------|--------|------|---------|----------------|
  | 阀入口压力 P1 | `p1_inlet_pressure` | MNM | Pressure | 控制阀/开关阀/安全阀 |
  | 阀出口压力 P2 | `p2_outlet_pressure` | MNM | Pressure | 控制阀/开关阀 |
  | 关闭压差 | `closed_differential_pressure` | S | Pressure | 控制阀/开关阀（关断 ΔP） |
  | 要求最大阀座泄漏 | `required_max_seat_leakage` | S | Enum(ANSI/FCI 70-2 Class) | 控制阀/开关阀 |
  | 差压 / 容器液位 | `differential_pressure` | MNM | Pressure | 差压流量/液位 |
  | 操作温度 | `operating_temperature` | MNM | Temperature | 全部 |
  | 流量 | `flow_rate` | MNM | Flow（质量/体积可选） | 流量/控制阀/安全阀 |
  | 密度 | `density` | MNM | Density | 流量/液位/阀 |
  | 粘度 | `viscosity` | MNM | Viscosity | 流量/阀 |
  | 比热比 Cp/Cv | `specific_heat_ratio` | MNM | Dimensionless | 气体阀/安全阀（ISA 75.01 / API 520 输入） |
  | 压缩因子 Z | `compressibility_factor` | MNM | Dimensionless | 气体阀/安全阀 |
  | 蒸气压 @37.8°C | `vapour_pressure_37_8c` | MNM | Pressure | 液体阀（闪蒸/空化判断） |
  | 临界温度 / 临界压力 | `critical_temperature` / `critical_pressure` | S / S | Temperature / Pressure | 液体阀（FF 因子）|
  | 分子量 | `molecular_weight` | S | Dimensionless | 气体阀/安全阀/气体流量 |
  | 电导率 | `conductivity` | S | Conductivity | 电磁流量计 |
  | 悬浮固体 | `suspended_solids` | S | Percent w/w | 流量/液位选型 |
  | 流体污染物 | `fluid_contaminant` | S | Text | 流量/液位选型 |
  | 允许最大压降 | `max_allowed_pressure_drop` | S | Pressure | 流量计选型 |
  | 流速 | `fluid_velocity` | S | Velocity | 流量计选型 |
  | pH / 浓度 | `ph_or_concentration` | MM | pH / Percent | 分析仪 |
  | 开关设定值 | `switch_setpoint` | LH | 随功能（Flow/Pressure/Temp） | FS/PS/TS |
  | 蒸汽干度 / 过热度 | `steam_quality_or_superheat` | S | Percent / Temperature | 蒸汽介质 |
  | 起泡倾向 | `foaming` | S | Enum(Yes/No) | 液位选型 |

  以上字段作为 `process_data_field_catalog` 种子；CALC-01/02（控制阀 Cv）、CALC-07~10（安全阀）、CALC-04~06（流量计）的输入 schema **必须引用本目录的字段键**，不得另起字段名。
- **【IS模板】设计条件继承**：`ProcessDataCase.design_*` 字段在 Case 创建及 PipingClass 变更时由 Service 重算（`PipingClass → Line → Component → ProcessDataCase`），并记录 `design_source_piping_class_code`；Approved 的 Case 冻结快照，不随 PipingClass 后续变更自动改动（生成"设计条件已变更"DBI 告警）。
- 复制字段映射：`ProcessDataCopyService` 根据源/目标类型确定可复制的字段映射清单（如管线→仪表仅复制通用过程参数；设计条件永不复制，始终派生）。
- 审批权限：ProcessEngineer 可提交 ReadyForReview，InstrumentEngineer 可确认 Approved。Approved 后普通编辑被拒绝并提示创建新版本。
- 版本保留规则：已 Approved 的过程数据版本永久保留快照，不可硬删除。

---

## 模块4：规格书 (Specifications Module)

> **【V2.1 增强·WSP模板】来源说明**：本模块标注 **「WSP模板」** 的内容，源自对项目方现行《WSP Instrument Datasheet Templates》模板库（**71 份 Excel、69 个技术类型 + 1 份 Generic，模板自身版本 MASTER VER. 01–05，2021–2023 按英国水行业 IGN104 改名**）的全量提取与审计。提取产物作为种子交付：`spec_field_catalog.json`（593 个字段）、`wsp_template_bindings.json`（71 份模板的单元格级绑定清单）、`WSP_TEMPLATE_AUDIT.md`（一致性与卫生审计）。
>
> **核心事实**：该模板库是**询价版基线**——全部 71 份模板首版用途均为 `For Enquiry`。"用于订货"与"用于施工"所需的后续版次由软件的版次生命周期推进（§4.4.11），模板本身不提供。

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| SPEC-01 | 页面编辑器：页面布局以网格坐标系统定义（12列×N行）。 | Web端拖拽表单设计器(react-grid-layout)。 |
| SPEC-02 | 表单编辑器：基于多个页面组合创建规格书表单。 | 表单配置管理API + 页面排序拖拽UI。 |
| SPEC-03 | 规格书数据字典：管理规格书字段属性元数据。**【V2.1 增强·WSP模板】字段清单正式化为 `spec_field_catalog`**（种子 593 字段，见 §4.1.15）：每字段含 `key, label_en, label_i18n, section(枚举 PROCESS/ELEMENT/TRANSMITTER/SWITCH/VALVE_BODY/ACTUATOR/POSITIONER/SOLENOID/…), structure(S\|MNM), uom_category, source_binding(来自 Component/ProcessDataCase/CalculationRun/PipingClass 的派生路径，或 null 表示规格书专有), is_vendor_supplied, validation`。字段按 `InstrumentTechnologyType` 挂集合（`technology_type_spec_fields` 关联表，含 `display_order, section, default_placeholder`），实现"一型一表单"。核心共用字段集 28 个（被 ≥40 份模板使用），长尾 300+ 个为技术类型专有。 | 字段元数据管理CRUD界面；`spec_field_catalog.json` 经 `load_engineering_seeds` 加载；与 §15.8 ADM-12 统一 schema 服务合并输出。 |
| SPEC-04 | 规格书生成：为指定仪表生成规格书，自动填充可映射字段。**【V2.1 增强·WSP模板】文档编号规则改为分段可配置**（原 `{ProjectPrefix}-{FormNumber}-{SequentialNumber}` 不符合 ISO 19650 / IGN104，无法产出合规编号）：复用 NamingConvention 框架，新增 `entity_type=DOCUMENT`，默认分段 `{Project}-{Originator}-{Volume}-{Level}-{DocType}-{Discipline}-{TechCode}-{Sequence}`（实测 `70XXXXXX-WSP-XX-XX-DS-CI-FET50-0001`），文件名另附 ` Iss {IssueRev}`（实测 `Iss P01`）。`TechCode` 取自 `InstrumentTechnologyType.code`——这使文档编号与技术类型天然对齐。自动填充来源按 `spec_field_catalog.source_binding` 解析（Component → ProcessDataCase → CalculationRun → PipingClass 链）。 | SpecificationGenerationService；编号走 `NamingConventionService(entity_type=DOCUMENT)`。 |
| SPEC-05 | 规格书数据录入与编辑：来自COMPONENT表的字段灰色只读，专有字段白色可编辑。 | 条件可编辑规格书表单。 |
| SPEC-06 | 表单数据模板：为同类型仪表创建通用数据模板，支持批量应用。 | 模板管理API + 批量数据填充API。 |
| SPEC-07 | 多标签规格书(SEE LIST)：创建多仪表共用的规格书。 | 主从表结构 + 动态列配置。 |
| SPEC-08 | 规格书流体状态选择：打开规格书时选择流体状态确定显示字段集合。 | 流体状态上下文切换组件。 |
| SPEC-09 | 规格书修订管理：修订记录存储在REVISION表，支持可配置的修订编号方案。 | 修订历史CRUD + 数据快照。 |
| SPEC-10 | 修订比较报告：对比两版快照字段差异，输出变更摘要报告。 | RevisionComparisonService + WeasyPrint。 |
| SPEC-11 | 全局修订：批量修订多个规格书。 | 批量修订API + 事务管理。 |
| **SPEC-12** | **【V2.1 增强·WSP模板】字段值的五态占位语义**：规格书字段值除实值外，支持四种语义化占位态，存储在 `SpecSheetFieldValue.placeholder_state`（枚举 `VALUE / VTA / TBA / TBC / NA`，空值为第五态 `EMPTY`）。语义（取自模板 NOTES 区的自有定义）：`VTA`=Vendor to Advise with Quotation（供应商随报价提供）、`TBA`=To Be Advised, updated prior to order（订货前确认）、`TBC`=To be Confirmed、`NA`=Not Applicable、`EMPTY`=真实缺失。**实测分布**：VALUE 69.4%、VTA 13.2%、NA 13.4%、TBA 1.1%、TBC 0.2%、EMPTY 2.7%。渲染时按模板约定文字输出（`Vendor to Advise (VTA)` 等，文字可在项目设置中改）。**完整度算法必须据此分母**：`NA` 不计入分母；`VTA/TBA/TBC` 计入分母但按"已受控"计分；仅 `EMPTY` 为缺失——否则"询价就绪度"判定完全错误（超过 1/4 字段会被误判为缺失）。 | `placeholder_state` 字段 + 渲染器状态映射表；IDX-17 完整度算法扩展为 `readiness_for_enquiry / readiness_for_order` 两个指标。 |
| **SPEC-13** | **【V2.1 增强·WSP模板】供货文档与附件要求建模**：全部 71 份模板均含 `DOCUMENTATION` 区（General Arrangement、Spares List、Certificate of Conformity、Material Certificates、Calibration Certificate、O&M Manual、ATEX/UKCA Certificate、Sizing Calculation as part of Tender、Final Documentation Requirements–份数…），64 份含 `ACCESSORIES` 区（wire-on 标牌、永久标识、过滤减压阀配管与安装、互连管路材质…）。这些是**供应商供货范围的合同性内容**，必须随 datasheet 一同发出。建模为 `DatasheetRequirement(spec_form_id \| spec_sheet_id, requirement_type: DOCUMENTATION\|ACCESSORY\|NOTE, seq, text, is_active)`：模板级为默认集（随 SpecForm 维护），Tag 级可增删覆盖。渲染时按 seq 输出到对应区。 | DatasheetRequirement 模型 + 模板默认集种子（自 `wsp_template_bindings.json` 的 `documentation_requirements` / `accessories_requirements` 导入）。 |
| **SPEC-14** | **【V2.1 增强·WSP模板】要求值 vs 实际值双列（回标对比 Bid Tabulation）**：模板中 `Accuracy: Required / Actual = ± 0.1% / VTA`、`Calculated Cv` vs `Max Available Cv` 体现了"要求—回标"对照机制。为可回标字段增加 `vendor_value`（供应商填报值）与 `compliance`（枚举 `COMPLY / DEVIATE / ALTERNATIVE / NOT_QUOTED`）、`vendor_remark`。支持按 Tag 或按询价包生成**回标对比表**（要求值 \| 供应商A \| 供应商B \| 偏差标记），作为订货前技术评标依据；偏差项汇总为 `TechnicalDeviationList`。字段是否可回标由 `spec_field_catalog.is_vendor_supplied` 控制（种子中 `VTA` 占比高的字段默认为真）。 | `SpecSheetFieldValue` 增加 vendor_* 列 + 回标导入（经模块8 Import Link，一个供应商一个 Link）+ 对比报告（§6.6 新增交付物类型 `BID_TABULATION`）。 |
| **SPEC-15** | **【V2.1 增强·WSP模板】多页规格书与分区**：实测单页 40 份、2 页 26 份、3 页 1 份；`SHEET x OF y` 为表头字段。`SpecForm` 需支持多页（已有 SPEC-02 的 1–10 页能力），并显式记录每页的分区归属（`SpecPage.sections[]`）与页码渲染。多标签规格书（SPEC-07 SEE LIST）的 `Tag No.: See Sheet 2` 用法实测存在于 KCV50，须与 SEE LIST 机制对齐。 | SpecForm/SpecPage 增加 sections 与分页渲染；页码写入 `SHEET`/`OF` 单元格。 |
| **SPEC-16** | **【V2.1 增强·WSP模板】WSP 模板库导入与绑定**：以 `wsp_template_bindings.json` 为输入，将 71 份模板注册为 `DeliverableTemplate(deliverable_type=INSTRUMENT_DATASHEET, format=XLSX, source=IMPORTED)` 并关联到对应 `InstrumentTechnologyType.default_spec_form_id`。**绑定以单元格坐标为准**——模板内全部命名区域（`_tag_no`/`_service`/`_PID_NO`/`_DOC_NAME`/`_REQ_NO`/`_P_ORDER`/`_HOOKUP`/`PreviousData`/`Rev`/`RevBy`/`RevDate`/`RevList`）与数据有效性下拉源**实测均为 `#REF!` 损坏**，不可作为锚点；其存在仅说明原始设计意图（含预留的请购单号 `_REQ_NO` 与采购订单号 `_P_ORDER`，对应 §2.5 ProcurementInfo）。骨架绑定（表头 13 个单元格 + 修订块 6 列 + MNM 行列式）一次定义复用于全部模板。 | 见 §6.6 DTL-02；骨架绑定存为 `template_skeleton_profile`，模板仅记录差异。 |

**【V2.1 增强】M4 规格书逐模块补全要求：**

- 规格书模板坐标系统：12列×N行网格，每字段定义 `{row, col, row_span, col_span, field_id, is_editable, is_protected}`。
- 字段绑定语法：`source: "component.cmpnt_serv"` 或 `source: "pd_general.temperature_normal"`，明确数据来源链。
- 只读/可写判断：来自其他模块的字段 `is_editable=false`（灰色背景），规格书专有字段 `is_editable=true`（白色背景）。
- 修订快照格式：`{revision_id, snapshot_date, issue_rev, issue_purpose, data: {field_id: {value, placeholder_state, vendor_value, compliance}}, schema_version}`（【WSP模板】增加 issue_rev/issue_purpose 与字段级占位态、回标值）。
- **【WSP模板】规格书表头字段与模板骨架**：`instrument_type_title`(M1)、`sub_class`(M3)、`project`(AB1)、`datasheet_no`(AB3)、`client`(P4)、`sheet_no/sheet_total`(AB4/AE4)、`issue`(AI4)、`tag_no`(D5)、`pid_no`(P5)、`service`(P6)、`manufacturer`(AB5)、`model`(AB6)；修订块表头第 7 行、数据自第 8 行、列 A/D/H/K/AD/AH = ISSUE/BY/DATE/REVISION(用途)/APPROVAL/DATE。
- **【WSP模板】多工况列式**：MNM 字段在 datasheet 中为**单行四工况平铺**（I=Min, N=Norm 1, S=Norm 2, X=Max, AC=Units）。PD-04 的多 Case 模型渲染到 datasheet 时须把 Governing Case 映射为 `Norm 1`、次要 Case 映射为 `Norm 2`（映射规则存 `SpecForm.case_mapping`），不得要求模板改结构。
- **【WSP模板】计算结果落点**：`Calculated Cv @ Flow`（四工况）、`Calculated S.P.L.`（dB(A) @ 某工况）、`Max Available Cv` 等字段的 `source_binding` 指向 `CalculationRun` 输出，规格书生成时自动带入最近一次有效计算（并记录 `calculation_run_id` 以便追溯）。
- PDF/Excel 渲染验收标准：PDF 输出的字段位置与页面编辑器中的坐标一致，字段值与数据库一致。

---

## 模块5：计算 (Calculations Module) — 增强版

计算模块基于SPI Sizing Equations文档和Intrinsic Safety Equations文档全面增强。所有公式需作为后端Python函数实现。

### M5-1 控制阀选型计算

| ID | 功能需求描述 |
|----|-------------|
| CALC-01 | 液体控制阀Cv计算：实现完整的ISA S75.01液体/水控制阀Cv计算流程。 |
| CALC-02 | 气体/蒸汽控制阀Cv计算：增加K/M/Z/T参数，处理壅塞流条件。 |
| CALC-03 | 控制阀噪声计算：实现四种噪声计算标准。 |

### M5-2 流量计计算

| ID | 功能需求描述 |
|----|-------------|
| CALC-04 | 流量计β比计算：支持多种流量计类型的迭代计算。 |
| CALC-05 | 流量计流量计算：已知β和差压正向计算流量。 |
| CALC-06 | 差压范围计算：反算差压范围。 |

### M5-3 安全阀计算

| ID | 功能需求描述 |
|----|-------------|
| CALC-07 | 液体安全阀计算(Blocked Flow)：区分ASME认证/非认证两种模式。 |
| CALC-08 | 气体安全阀计算(Blocked Flow)：临界流/亚临界流分支判断。 |
| CALC-09 | 蒸汽安全阀计算(Blocked Flow)：使用蒸汽特定参数和过热修正。 |
| CALC-10 | 火灾工况安全阀计算：气体膨胀和液体充满容器两种工况。 |

### M5-4 本安计算

| ID | 功能需求描述 |
|----|-------------|
| CALC-11 | 按电路类型本安计算：计算最大允许电缆长度。 |
| CALC-12 | 按回路本安计算：对回路中每个标签执行本安验证。 |
| CALC-13 | 本安计算报告生成。 |

### M5-5 温度套管计算

| ID | 功能需求描述 |
|----|-------------|
| CALC-14 | 温度套管强度计算：根据ASME PTC 19.3标准验证。 |

**【V2.1 增强】M5 计算逐模块补全要求：**

- 每类计算的输入 JSON schema（含字段名、数据类型、单位、有效范围）。
- 所有计算函数统一返回：`{inputs_si, outputs, warnings, standard, formula_version, validation_errors}`。
- 每个公式必须有基准测试向量和容差（如 CALC-01 液体 Cv：给定输入 → 预期输出 ± 0.1%）。
- 公式函数必须实现为独立 Python 模块：`backend/apps/calculations/engines/control_valve.py`、`flow_meter.py`、`relief_valve.py`、`intrinsic_safety.py`、`thermowell.py`。
- 错误码：`CALC_INPUT_OUT_OF_RANGE`、`CALC_NO_CONVERGENCE`、`CALC_DIVISION_BY_ZERO`、`CALC_INVALID_FLUID_STATE`。
- 数值容差：迭代收敛条件 `|Cv_n - Cv_{n-1}| / Cv_n < 1e-6`，最大迭代次数 100。

---

## 模块6：文档管理 (Document Management Module)

| ID | 功能需求描述 |
|----|-------------|
| DOC-01 | 规格书绑定器(Specification Binder)。 |
| DOC-02 | 通用文档绑定器(General Document Binder)。 |
| DOC-03 | 文档分配管理。 |
| DOC-04 | 表单注释模板(Form Note Template)。 |
| DOC-05 | 绑定器修订管理。 |
| DOC-06 | 变更摘要报告(Change Summary Report)。 |
| DOC-07 | 按修订打印：多PDF合并输出。 |

**【V2.1 增强】M6 文档管理逐模块补全要求：**

- Package/Revision 状态机：Working → Published → Superseded；Working → Cancelled。
- 文档编号规则：`{ProjectPrefix}-{PackageType}-{SequentialNumber}`，自动生成，**租户 schema 内（即项目内）唯一**。
- 电子签名/审批流：如需 21 CFR Part 11 合规，须补充签名、不可抵赖、审计留存要求（待项目方确认）。
- 批量发布：选择多个文档一次提交发布，Celery 异步执行。
- 文件存储策略：所有生成文件存储到 `FileAsset` 表，字段含 `file_id, project_id, storage_path, mime_type, sha256, created_by, expires_at`（FileAsset 位于 public schema，以 project_id 关联项目）。

---

## 模块7：系统集成接口 (Integration Module) — 增强版

| ID | 功能需求描述 |
|----|-------------|
| INT-01 | RESTful API平台：OpenAPI 3.0，JWT认证，统一分页/限流。 |
| INT-02 | 数据发布(Publish)服务：类似SPI SmartPlant Adapter的数据发布。 |
| INT-03 | 数据检索(Retrieve)服务：从外部系统检索数据并导入。 |
| INT-04 | 数据交换格式：JSON/XML/CSV/Excel。 |
| INT-05 | 集成事件通知：Webhook + Redis Pub/Sub。 |
| INT-06 | 电缆数据导出到电气系统(SPEL)。 |

**【V2.1 增强】M7 集成接口逐模块补全要求：**

- 外部系统 registry：`ExternalSystemRegistry` 表（`system_id, system_name, system_type, base_url, auth_config, is_active`）。
- 字段映射 DSL：`schema_mapping` 表（`internal_model, internal_field, external_field, transform_expression, direction`）。
- 发布/检索协议：发布返回 `{publish_id, status, object_count, errors}`；检索返回 `{task_id, retrieved_items[], conflicts[]}`。
- Webhook 签名：HMAC-SHA256，重放窗口 5 分钟，失败指数退避重试（初始 1s，最大 1h），死信队列。
- 接口审计：所有集成操作记录到 `integration_audit_log`（`audit_id, system_id, operation, payload_hash, status, timestamp`）。
- SP Adapter 外部对象映射：`ExternalObjectMap` 表维护 `external_system, external_id, local_model, local_id, last_sync_hash`。

---

## 模块8：数据导入/导出管理 (Import/Export Module) — 增强版

| ID | 功能需求描述 |
|----|-------------|
| IFC-01 | 导入链接(Import Link)框架：SingleTable/Module两种模式。**【决策 D11 · 明确】源格式：Excel（.xlsx/.xlsm/.xls）、CSV/TSV（可选分隔符与编码 UTF-8/GBK/Latin-1）、JSON、外部数据库（经模块7/§6.4）。目标表：`ItemTypeRegistry` 中所有 `allow_import=True` 的 Item Type——Instrument Index（Component + TagIOAllocation + ProcurementInfo 子表）、Loop、Line、Apparatus、Cable/Wire、Panel/PanelStrip/Terminal、ProcessDataCase、SpecSheetData、Drawing、SIF/SIFElement、PipingClass、HookUp/BOM、全部支撑表（ADM-05）以及自定义表（§15.8 UDT）。自定义字段（`custom_data.<key>`）与系统字段同等可映射。** |
| IFC-02 | 字段映射引擎：拖拽建立源→目标字段映射，支持公式和宏。**【D11】自动映射**：按表头与目标字段的 label/key/别名（含 ADM-11 覆盖后的标签与 i18n 标签）做归一化匹配并给出置信度，用户确认后保存为可复用的 Import Link；支持多工作表（Module 模式一次导入主表 + 子表，如 Schedule 表 → Component，其 PCS/SIS I/O 列块 → TagIOAllocation）；支持列值转换（查找表、拆分/合并列、单位换算、正则提取、常量）。 |
| IFC-03 | 导入验证规则：命名规范/外键引用/唯一性/数据类型四级验证。 |
| IFC-04 | 导入模式管理：InsertAndUpdate/InsertOnly/Delete/Move。 |
| IFC-05 | 映射代码常量。 |
| IFC-06 | 命名规范匹配。 |
| IFC-07 | 数据合并(Merger)工具。 |
| IFC-08 | 导入测试运行(Test Run)。 |
| **IFC-09** | **【D11】导入模板下载**：对任一可导入目标表生成 Excel 导入模板（`GET /api/v1/import/templates/{item_type}/`）：首行为字段 key、第二行为显示标签（含自定义字段与覆盖标签）、第三行为类型/必填/示例说明，枚举与外键列附数据有效性下拉（取自当前租户数据），日期/数值列附格式；可选带现有数据导出以便"导出-修改-回导"。模板随 `schema_version` 变化，导入时校验模板版本并提示差异。 |
| **IFC-10** | **【D11】预置 Import Link**：系统随种子预置常用映射并允许项目方修改：(a) `IS_TEMPLATE_SCHEDULE`——项目方现行 Excel《Instrument Schedule》138 列 Schedule 表 → Component / TagIOAllocation(PCS、SIS 两组) / ProcessDataCase(operating_*) / ProcurementInfo / Line 关联（按 IS 模板列组逐列映射，见 §2.1.1 注）；(b) `PIPING_INDEX`——机械 Piping Index → PipingClass（DDP-12）；(c) `DCS_IO_LIST`——DCS/SIS 供应商 I/O 清单 → CSTag/TagIOAllocation 回填；(d) `CABLE_SCHEDULE`——电气电缆清册 → Cable/Wire；(e) `GENERIC_SUPPORTING_TABLE`——两列 code/name → 任意支撑表。 |
| **IFC-11** | **【D11】大文件与异步**：>2,000 行或 >5 MB 的导入自动走 Celery 异步（§4.2.4），分批 500 行/事务（可配置），实时进度（WebSocket），中断可续传；Dry Run 同样异步并输出可下载的逐行结果 Excel（原行 + 状态 + 错误列）。导入完成后生成 `ImportSession` 报告并可 24 小时内回滚（现有回滚机制）。 |

**【V2.1 增强】M8 导入/导出逐模块补全要求：**

- Import Link JSON schema：`{link_name, target_item_type, source_type, source_options{sheet_name, header_row, delimiter, encoding}, mapping_config[{source_column, target_field, transform, confidence}], child_mappings[{child_item_type, column_block, mapping_config}], validation_rules, duplicate_policy, merge_key, is_system_preset, schema_version}`（D11：增加 source_options / child_mappings / is_system_preset）。
- Dry Run（测试运行）输出：必须输出 `{created, updated, skipped, errors, warnings}` 计数和逐行错误详情；不得写数据库。
- Merger 冲突类型：`field_conflict, missing_reference, duplicate_key, deleted_target, version_conflict`；每个冲突必须有决策：`use_source / use_target / manual / skip`。
- 回滚机制：导入完成后保留 `import_session` 快照，支持在 24 小时内回滚已导入数据。

---

# 第二部分：详细工程模块 (Detailed Engineering)

## 模块9：尺寸数据与管道 (DDP) — 增强版

尺寸数据与管道(DDP)模块管理仪表的物理尺寸数据和过程连接信息。核心数据表基于 ERD 中的 COMPONENT_DIMENSIONAL 及关联表。注意：DDP 在 SmartPlant Adapter 中需特殊处理——每个尺寸组对应一个独立 MapClass，属性通过 UDF 映射（§15.8）。

### 9.0 数据模型定义

| Django Model | 表名 | 关键字段和关系 |
|--------------|------|---------------|
| DimensionalGroup | dimensional_group | `group_id(PK)`, `group_name(VARCHAR 50)`, `group_description(TEXT)`。定义尺寸字段模板，如"直法兰式变送器"含 F2F(面到面)、FD(法兰直径)、FH(法兰厚度)、Weight_Full、Weight_Empty |
| DimensionalGroupField | dim_group_field | `field_id(PK)`, `group_id(FK→DimensionalGroup)`, `field_name(VARCHAR 50)`, `field_label(VARCHAR 100)`, `field_type(FLOAT/VARCHAR/INT)`, `display_order(INT)`, `uom_category(LENGTH/WEIGHT/PRESSURE)` |
| ComponentDimensional | component_dimensional | `dim_id(PK)`, `cmpnt_id(FK→Component, UNIQUE)`, `group_id(FK→DimensionalGroup)`, `manufacturer_id(FK)`, `model_id(FK)`, `data_status(ENUM: Preliminary/ForApproval/Approved)`, `data_source(ENUM: Default/Working/Vendor)` |
| DimensionalData | dimensional_data | `data_id(PK)`, `dim_id(FK→ComponentDimensional)`, `field_id(FK→DimensionalGroupField)`, `value(VARCHAR 50)`, `uom_id(FK→UnitOfMeasure)` |
| ProcessConnection | process_connection | `conn_id(PK)`, `dim_id(FK→ComponentDimensional)`, `connection_position(ENUM: INLET/OUTLET/CONN3/CONN4)`, `class_rating(VARCHAR 20, 150#/300#/600#)`, `end_preparation(VARCHAR 30, RF/RTJ/BW/SW)`, `size(VARCHAR 20)`, `schedule(VARCHAR 10)` |
| DefaultLibrary | default_library | `lib_id(PK)`, `group_id(FK)`, `manufacturer_id(FK)`, `model_id(FK)`。制造商标准尺寸数据模板，经 DefaultLibraryData 关联具体值 |
| DefaultLibraryData | default_library_data | `id(PK)`, `lib_id(FK→DefaultLibrary)`, `field_id(FK→DimensionalGroupField)`, `value(VARCHAR 50)`, `uom_id(FK)` |

全部表按 §4.1.1 追加审计/软删除/乐观锁字段，位于租户 schema。

### 9.1 功能需求

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| DDP-01 | 尺寸组定义：管理员创建尺寸组并定义组内自定义字段，每字段指定名称(如 F2F)、显示标签(Face-to-Face Distance)、数据类型、显示顺序、计量单位类别。组创建后可复制(含全部字段定义)。不可删除已被仪表引用的组。 | 尺寸组 CRUD + 动态字段定义管理(dim_group_field)。删除校验 `DimensionalData.objects.filter(dim__group_id=X).exists()`。 |
| DDP-02 | 过程连接定义：为每个仪表定义最多 4 个过程连接(INLET/OUTLET/#3/#4)。每连接含等级/压力(ANSI 150#/300#/600#/900#/1500#/2500#)、端部准备(RF/RTJ/BW/SW/Threaded/Flanged)、尺寸(1/2"~8")、壁厚等级(STD/XS/Sch40/Sch80/Sch160)。选项从 supporting 表加载。 | 4 连接分 Tab 表单 + 级联下拉(选 Class 后过滤 End Preparation)。 |
| DDP-03 | 仪表类型与尺寸组关联：技术类型 Profile(§2.1.1.1)增加 `dim_group_id`，创建尺寸数据时自动应用该尺寸组字段模板。一个尺寸组可被多个类型引用。 | Profile 增加 dim_group_id 外键；创建 ComponentDimensional 时自动填充 group_id。 |
| DDP-04 | 规格书表单分配到尺寸组：将规格书页面分配到尺寸组，用于在规格书中展示尺寸数据。关系存 `dim_group_spec_form(group_id, spec_page_id)`。 | DimGroupSpecForm 关联表 + 管理界面；规格书渲染时按仪表尺寸组加载页面。 |
| DDP-05 | 默认库管理：按[制造商+型号+尺寸组]存储标准尺寸数据。三级树形导航(制造商→型号→尺寸组)，右侧尺寸数据网格。支持手动录入和 Excel 批量导入(经 IFC-01)。 | 默认库 CRUD + 三级级联筛选 + openpyxl 导入。 |
| DDP-06 | 工作数据管理：实际使用的仪表尺寸数据，含全部尺寸字段值、满载/空载重量、各字段计量单位。状态 Preliminary→ForApproval→Approved(§4.4.10)；修改已批准数据重新进入审批。 | 按尺寸组动态渲染表单 + django-fsm 状态机。 |
| DDP-07 | 默认→工作数据复制：按[制造商+型号+尺寸组]三元匹配，从默认库复制标准值到工作数据。多条匹配时提示选择。仅填充工作数据中为空的字段(可配置为覆盖)。 | `POST /api/v1/ddp/{dim_id}/copy-from-default/`；查询 `DefaultLibrary.objects.filter(group_id, manufacturer_id, model_id)`。 |
| DDP-08 | 工作数据→默认库复制：将实际工作数据回存为默认库条目(新建或更新)，供后续项目参考。需二次确认(可能影响其他项目)。 | `POST /api/v1/ddp/{dim_id}/save-to-default/`。 |
| DDP-09 | 管道设计区域：为仪表指定 3D CAD 模型中的管道设计区域名 `piping_design_area(VARCHAR 50)`。支持批量选择多个仪表统一设置。 | Component 增加字段 + `PATCH /api/v1/instruments/batch-update-field/`。 |
| DDP-10 | 尺寸数据表报告：为选定仪表生成尺寸数据表 PDF，含标签基本信息 + 过程连接表 + 全部尺寸字段值 + 仪表 SVG 示意图(标注关键尺寸)。 | WeasyPrint + `dim_outline_templates` SVG 模板；经 §6.6 交付物模板库(DIMENSIONAL_DATA_SHEET)渲染。 |

**【V2.1 增强】M9 DDP 逐模块补全要求：**

- 尺寸组模板：每个 DimensionalGroup 的字段集合定义为 JSON template，含 `{fields: [{field_name, label, type, uom_category, display_order}]}`。
- UDF/UDT 映射：尺寸数据中的用户自定义字段通过 `custom_field_definitions` 统一管理，前端动态渲染。
- 过程连接标准字段：`{connection_position, class_rating, end_preparation, size, schedule}`，每字段的可选值从 supporting 表加载。
- SVG 轮廓模板字段：`dim_outline_templates` 表存储 SVG 模板字符串，根据仪表类型维护，包含可替换的尺寸标注占位符。
- 报告验收：尺寸数据表 PDF 中的数值与数据库一致，SVG 轮廓图正确标注关键尺寸。

### 9.2 PipingClass（配管等级 / 流体服务主表）【V2.1 增强·IS模板】

**设计动机**：IS 模板以 Piping Index 表为 Fluid / MoC / Pipe Spec / 设计-最大-最小 T&P / 保温伴热的**唯一数据源**，并在 Guide notes 中明令"只用已批准数据、手动受控更新"。Open Instrument 将其建模为 Mechanical Engineer 拥有的主表（对应 §15.2.4 权限矩阵中的 `PipeSpecification`），Line 引用之，过程数据的设计条件自其只读派生（PD-02），从制度上杜绝仪表工程师擅改配管设计条件。

| 字段 | 数据类型与约束 | 说明 |
|------|---------------|------|
| id | BigAutoField, PK | |
| fluid_code | CharField(max=10), UNIQUE per tenant | 流体代码，如 ACE / MEOH / ACN |
| fluid_name | CharField(max=100) | 流体名称，如 Acetone |
| fluid_state | CharField, choices | Liquid / Gas / Vapour / Steam / TwoPhase / Slurry |
| pipe_spec_code | CharField(max=20) | 配管规格代码，如 SS1 |
| moc_type | CharField(max=50) | 材质类型，如 Stainless Steel |
| moc_grade | CharField(max=50) | 材质牌号，如 X2CrNiMo17-12-2 / 1.4404 |
| gasket_spec | CharField(max=50), nullable | 垫片规格 |
| valve_spec_code | CharField(max=20), nullable | 阀门规格代码 |
| insulation_code_id | ForeignKey → InsulationCode, nullable | 默认保温代码（Line 可覆盖） |
| trace_heating_required | BooleanField, default=False | 是否需要伴热 |
| painting_std / support_std / cleaning_std | CharField(max=50), nullable | 涂装 / 支架 / 清洁标准 |
| design_temperature | DecimalField | 设计温度（SI 存储） |
| max_working_temperature / min_working_temperature | DecimalField | 最高 / 最低工作温度 |
| design_pressure | DecimalField | 设计压力（SI 存储） |
| max_working_pressure / min_working_pressure | DecimalField | 最高 / 最低工作压力 |
| test_pressure | DecimalField, nullable | 试验压力 |
| test_type | CharField, choices, nullable | Hydro / Pneumatic / Service |
| asme_b31_3_category | CharField, choices, nullable | Normal / Category D / Category M / High Pressure |
| ped_fluid_group | CharField, choices, nullable | Group 1 / Group 2（PED 2014/68/EU） |
| ped_fluid_state | CharField, choices, nullable | Gas / Liquid（PED 分类用） |
| approval_status | CharField, choices | Draft / Approved / Superseded —— **仅 Approved 可被 Line 引用** |
| approved_by / approved_at | FK → User / DateTimeField, nullable | |
| source_document_ref | CharField(max=100), nullable | 来源机械配管索引文件编号与版本 |
| notes | TextField, nullable | |
| created_at/by, updated_at/by, row_version, is_deleted | | 按 §4.1.1 |

功能需求：

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| **DDP-11** | PipingClass CRUD 与审批：Mechanical Engineer / PE 维护；`approval_status` 走 Draft → Approved → Superseded；仅 Approved 记录出现在 Line 的 `piping_class` 下拉。修改 Approved 记录时创建新版本并将旧版置 Superseded（引用旧版的 Line 显示"配管等级已升版"提示）。 | `PipingClassViewSet` + 状态机 + 权限（§15.2.4）。 |
| **DDP-12** | 从机械 Piping Index 导入：支持 Excel 导入 PipingClass（通过模块8 Import Link，target_item_type=PipingClass），Dry Run 校验代码唯一、单位可转换、必填齐全；导入结果默认 Draft，需人工 Approved。落实 IS 模板"cut and paste 后受控更新"的纪律。 | 复用 IFC-01~04/08。 |
| **DDP-13** | 设计条件派生与告警：Line 选定 PipingClass 后，其 `fluid_name/moc/pipe_spec/insulation` 与设计 T&P 自动派生（PD-01/02）；PipingClass 升版后，DBI 新增检查项 **"Line 引用已 Superseded 的 PipingClass"** 与 **"Approved ProcessDataCase 的设计条件与当前 PipingClass 不一致"**。 | Service 派生 + DBI 检查项注册（模块14）。 |

支撑表（在 §15.6 ADM-05 登记）：`InsulationCode`（如 LC=Cold Conservation、HC=Hot Conservation、PP=Personnel Protection）、`HeatTracingCode`（电伴热 / 蒸汽伴热 / 无）。

---

## 模块10：接线设计 (WIR) — 增强版

接线设计模块是系统中最复杂的模块，负责工厂仪表接线的完整设计。基于 SPI ERD 中 Panel/Strip/Terminal/Cable/Wire/Channel 等核心实体关系与 Detailed Engineering 完整接线工作流细化。

### 10.1 数据模型定义（基于 SPI ERD - Wiring Overview）

| Django Model | 表名 | 关键字段和关系 |
|--------------|------|---------------|
| Panel | panel | `panel_id(PK)`, `panel_name(VARCHAR 50)`, `panel_category(ENUM: JunctionBox/MarshalingRack/Cabinet/DCSPanel/PLCPanel/DevicePanel/PlugSocketBox)`, `parent_id(FK→Panel SELF, nullable, 面板嵌套)`, `unit_id(FK→PlantHierarchy UNIT)`, `location_id(FK→InstrumentLocation, nullable)`, `is_reference(BOOL, true=参考面板/false=工厂面板)` |
| CabinetRack | cabinet_rack | `rack_id(PK)`, `panel_id(FK→Panel)`, `rack_name(VARCHAR 30)` |
| RackPosition | rack_position | `rack_pos_id(PK)`, `rack_id(FK→CabinetRack)`, `slot_number(INT)`, `slot_name(VARCHAR 20)` |
| PanelStrip | panel_strip | `strip_id(PK)`, `panel_id(FK→Panel)`, `strip_name(VARCHAR 50)`, `strip_type(ENUM: Standard/Channel)`, `terminal_pattern(VARCHAR 20, 如 '3-in-a-row: +/-/SH')`, `channel_id(FK→Channel, nullable)` |
| PanelStripTerm | panel_strip_term | `term_id(PK)`, `strip_id(FK→PanelStrip)`, `term_name(VARCHAR 20, 如 '1+'/'1-'/'1SH')`, `term_sequence(INT)`, `signal(VARCHAR 50, nullable)`, `signal_level(INT, nullable)`, `channel_id(FK→Channel, nullable)` |
| Channel | channel | `channel_id(PK)`, `strip_id(FK→PanelStrip)`, `channel_number(INT)`, `io_type(ENUM: AI/AO/DI/DO/PI/SI)` |
| Apparatus（接线设备） | apparatus | `appar_id(PK)`, `appar_name(VARCHAR 50)`, `strip_id(FK→PanelStrip, nullable)`, `channel_id(FK→Channel, nullable)`, `remote_appar_id(FK→Apparatus SELF, nullable)`, `appar_category(ENUM: IOCard/Barrier/Isolator/Relay/PowerSupply)` |
| Cable | cable | `cable_id(PK)`, `cable_name(VARCHAR 50)`, `cable_type_id(FK→CableType, nullable)`, `is_reference(BOOL)`, `unit_id(FK)`。电缆依赖模式启用时 plant cable 必须关联 reference cable |
| CableSet（缆组/对） | cable_set | `set_id(PK)`, `cable_id(FK→Cable)`, `set_name(VARCHAR 20, 如 'Pr1'/'Tr1')`, `set_type(ENUM: Pair/Triad/Quad)` |
| Wire（导线） | wire | `wire_id(PK)`, `set_id(FK→CableSet)`, `wire_name(VARCHAR 20, 如 '+'/'-'/'Shield')`, `wire_tag(VARCHAR 50, 信号传播后的标签标识)`, `polarity(ENUM: Plus/Minus/Shield/OverallShield/Spare)`, `color_id(FK→WireColor)`, `wire_type_id(FK→WireType)` |
| WireTerminal（导线端子连接） | wire_terminal | `wt_id(PK)`, `term_id(FK→PanelStripTerm)`, `wire_id(FK→Wire)`。一个端子可连接多根导线；一根导线最多连两个端子(§4.5 连接不变量) |
| WireGroup（信号组） | wire_group | `wire_group_id(PK)`, `parent_id(FK→Panel)`, `panel_id(FK→Panel)`, `wire_group_source_id(FK→WireGroup SELF, nullable)` |
| GeneralSignal | general_signal | `signal_id(PK)`, `wire_group_id(FK)`, `wire_group_source_id(FK, nullable)`, `signal_name(VARCHAR 50)`, `signal_type(ENUM: TagSignal/GeneralSignal/LocalSignal)` |
| ControlSystemTag（CS Tag） | control_system_tag | `cs_tag_id(PK)`, `cs_tag_name(VARCHAR 50)`, `cmpnt_id(FK→Component, nullable)`, `channel_id(FK→Channel, nullable)`, `coupled_status(ENUM: Uncoupled/Coupled/Assigned, §4.4.4)` |
| Jumper（跳线） | jumper | `jumper_id(PK)`, `from_term_id(FK→PanelStripTerm)`, `to_term_id(FK→PanelStripTerm)`, `jumper_name(VARCHAR 50)`。跳线不传播信号 |
| ConnectionTypeDefinition | connection_type_definitions | `type_id(PK)`, `type_name(VARCHAR 50)`, `wires_per_block(INT)`, `polarity_mapping(JSONB)` |
| FieldbusSegment | fieldbus_segment | `segment_id(PK)`, `segment_type(ENUM: FF/ProfibusDP/ProfibusPA)`, `panel_id(FK)`, 段参数见 WIR-23/24 |

全部表按 §4.1.1 追加审计/软删除/乐观锁字段，位于租户 schema。

### 10.2 面板管理

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| WIR-01 | 面板创建与管理：按 `panel_category` 区分行为——JunctionBox(现场电缆与多芯电缆中转)、MarshalingRack(含现场侧与系统侧两组端子排，支持跨线)、Cabinet(Rack→Slot→IOCard 层级)、DCSPanel/PLCPanel(含 I/O 卡与通道)、DevicePanel(每现场仪表一个，由类型 Profile 自动创建)。面板在浏览器中同时出现在"按位置"和"按类别"两种视图树。 | panel_category 枚举驱动行为分发；前端 TreeView 双视图共享同一数据源。 |
| WIR-02 | 参考面板(Reference Panel)：在参考库中创建面板模板(含预定义端子排、I/O 卡配置)。实例化时执行深拷贝，创建新工厂面板并复制全部端子排/端子/通道等子对象，生成新 ID。工厂面板修改不影响模板。 | `POST /api/v1/panels/{ref_id}/instantiate/?target_unit_id=X`；`PanelCopyService` 递归复制。 |
| WIR-03 | 面板层级结构：无固定深度限制。典型层级：(1) JunctionBox→Strip→Terminal (2) MarshalingRack→Strip(Field Side)→Terminal + Strip(System Side)→Terminal (3) DCSPanel→Rack→Slot→IOCard→Strip(Channel型)→Channel→Terminal (4) DevicePanel→Strip→Terminal。 | `Panel.parent_id` + `PanelStrip.panel_id` + `PanelStripTerm.strip_id` 递归树；DRF nested serialization；前端 LazyLoad。 |

### 10.3 端子排与端子

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| WIR-04 | 端子排创建与配置：通过 TerminalConfiguration 定义 (1) 端子模式：'2 terminals'(+/-)、'3 in a row'(+/-/Shield)、'2 terminals + shield' (2) 块数 `number_of_blocks`(如 16 块 × 3 端子 = 48 端子) (3) 编号方案：顺序递增或按块编号(1+,1-,1SH,2+…) (4) 类型 Standard 或 Channel(每 3 端子组成一个 Channel)。创建后自动批量生成 PanelStripTerm。 | `TerminalConfigurationService.create_strip(panel_id, config)` + `bulk_create`。 |
| WIR-05 | 端子属性编辑：双击端子打开 Terminal Connection 对话框，显示/编辑信号名(自关联 Wire 传播)、信号级别(1/2/3/0)、连接序号。信号级别决定端子组内位置(Level 1=+极, 2=in/neutral, 3=-极)。 | `GET/PATCH /api/v1/terminals/{term_id}/connection/`。 |
| WIR-06 | 端子排复制：复制已有端子排快速创建相似配置，自动生成新 `strip_name`(追加 '-Copy')和新端子记录；**不复制已有接线连接**。 | `POST /api/v1/strips/{id}/copy/`；深拷贝 strip+term，不拷贝 wire_terminal。 |

### 10.4 电缆管理

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| WIR-07 | 电缆创建与管理：层级 Cable→CableSet(Pair/Triad/Quad)→Wire。CableConfiguration 指定 (1) Set 类型(Pair w/ or w/o Shield, Triad, Quad) (2) Set 数量 (3) 导线规格(12/14/16/18 AWG) (4) 材质(Copper/Aluminum) (5) 绝缘(PE/PVC/XLPE) (6) 是否 Overall Shield。创建时自动生成 CableSet 与 Wire，按 Set 类型自动命名(Pair: +/-/Shield；Triad: +/in/-/Shield)。电缆依赖模式启用后工厂电缆必须关联参考电缆。 | `CableConfigurationService.create_cable()` + `bulk_create`；`cable_dependency` 配置在 `project_settings`。 |
| WIR-08 | 导线属性管理：`wire_name`(如 'PR1+')、`wire_tag`(传播后标识，如 '101-FT-100')、`polarity`、`color_id`、`wire_type_id`。导线颜色方案：按区域为不同导线组批量应用配色(如 +=Red, -=Black, Shield=Green)。 | 颜色方案表 `wire_color_patterns(pattern_id, polarity, color_id)` + 批量应用 API。 |
| WIR-09 | 设备电缆自动创建：创建仪表标签时若类型 Profile `auto_create_wiring=true`，自动 (1) 创建 DevicePanel(命名为标签号) (2) 创建 DeviceCable(命名 `C-{tag_name}`) (3) 按 Profile 参考电缆配置创建 CableSet 与 Wire。设备面板自动含一个端子排，端子数与导线数匹配。 | `InstrumentCreationService.create_wiring_items()`，由 Profile 驱动（验收场景"创建仪表全链路"）。 |

### 10.5 接线连接（核心功能）

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| WIR-10 | 接线连接窗口：中间为端子排(端子编号+螺丝头图标)，左右两侧显示各自连接的电缆/导线信息(cable_name, set_name, wire_tag, signal)。拖拽电缆/缆组到指定端子，弹出 Cable Connection Definition 选择 (1) 电缆端(End 1/End 2) (2) 起始端子 (3) 连接类型。连接写入 WireTerminal。 | React SVG 端子排 + 拖拽；`ConnectionService.connect(cable_id, end, strip_id, start_term, connection_type)`。 |
| WIR-11 | 连接类型定义：预定义 '2 in a row'(+/-)、'3 in a row'(+/-/Shield)、'Single'。管理员可自定义新类型，指定导线极性到端子位置映射(如 4 端子型 +/in/-/Shield)，存 `connection_type_definitions`。 | ConnectionTypeDefinition 模型 + `polarity_mapping` JSON。 |
| WIR-12 | **信号传播(Signal Propagation)**：标签信号沿 DevicePanel→电缆→JunctionBox→多芯电缆→MarshalingRack 路径自动传播。算法：(1) 自 DevicePanel 端子出发 (2) 找连接该端子的 Wire (3) 沿 Wire 找另一端 Terminal (4) 从该 Terminal 找同一 WireGroup 另一侧 Wire (5) 继续直到到达 I/O 通道或路径分叉。更新 `Wire.wire_tag` 与 `PanelStripTerm.signal/signal_level`。I/O 分配后自控制系统端反向传播。**分叉处停止**，需手动干预。停止条件与 `propagation_trace` 见 §4.5 第 4 条。 | `SignalPropagationService.propagate(device_panel_id)`；BFS 遍历 Wire→Terminal→Wire 图；`post_save on WireTerminal` 触发重算。 |
| WIR-13 | 强制信号传播：自动传播因分叉或冲突停止时，右键 DevicePanel 选择 Force Signal Propagation，强制覆盖沿途全部已有信号。 | `POST /api/v1/panels/{id}/force-propagation/`；忽略已有信号直接覆盖。 |
| WIR-14 | 手动信号传播：在 Terminal Connection 对话框手动设置任意端子的 Signal 与 Signal Level（用于分叉点或安全栅模拟点），设置后自该点继续自动传播。 | Terminal PATCH 支持 signal/signal_level，更新后触发正向传播。 |
| WIR-15 | 相邻连接导航：选中导线后点击 Open Adjacent Connection，自动查找该导线另一端所连端子排并打开其连接窗口，实现跨面板接线追踪。 | `GET /api/v1/wires/{wire_id}/adjacent/` 返回另一端 strip_id/panel_id。 |
| WIR-16 | **跨线连接(Cross Wiring)**：编组柜内现场侧与系统侧端子排之间的连接。三模式：(1) 手动——逐一选择两侧端子 (2) 半自动——系统按匹配条件(同一面板内、相同信号级别、一侧来自 DevicePanel 序号<50、另一侧控制系统序号>50)查找目标端子，用户确认 (3) 全自动——自动查找并执行全部匹配跨线。使用 CROSS WIRE 虚拟电缆或实际跨线电缆。跨线后信号在两侧传播。 | `CrossWiringService.cross_wire(primary_strip_id, secondary_strip_id, mode, cable_id)`；匹配算法见 §4.5。 |
| WIR-17 | 点对点接线图：从任意导线出发追踪完整信号路径(现场设备面板→控制系统 I/O 卡)，显示途经每个面板→端子排→端子→电缆→缆组→导线颜色，以表格或 SVG 水平路径图展示。 | `PointToPointService.trace(wire_id)` 递归遍历；SVG + PDF 导出(§6.6 WIRING_DIAGRAM)。 |
| WIR-18 | 跳线管理：端子排内跨端子物理短接(如电源公共线)。**跳线不传播信号**，在连接窗口以虚线显示，命名 `J-{strip}-{from}-{to}`。 | Jumper 模型 + dashed line SVG。 |

### 10.6 I/O 分配

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| WIR-19 | I/O 分配：Step 1 耦合(Coupling)——将 Component 与 CS Tag 配对(cs_tag_name 系统建议、用户可改)；Step 2 分配(Assignment)——拖拽耦合对到 DCS/PLC I/O 卡空闲通道，更新 `channel_id`、状态转 Assigned、自 I/O 通道端触发反向信号传播。窗口布局：左侧 TagList(I/O 类型过滤 + 标签列表)、右侧 Assignment Details(通道号/地址/已分配 CS Tag)。 | `IOAssignmentService.couple()` / `.assign()`；React 拖拽。与 IDX-16 早期估算对账(DBI `IDX_IO_ESTIMATE_VS_ASSIGNED`)。 |
| WIR-20 | CS Tag 管理：CRUD + 重命名、耦合/解耦、取消分配。解耦清除 `cmpnt_id` 但保留 CS Tag 记录；取消分配清除 `channel_id` 但保留耦合。状态机见 §4.4.4。 | 解耦/取消分配需触发信号反传播清除。 |
| WIR-21 | I/O 分配过滤：TagList 可按 (1) I/O 类型(AI/AO/DI/DO/PI/SI) (2) 耦合状态(Uncoupled/Coupled/All) (3) Tag Number 模糊搜索 过滤；选定 I/O 类型后右侧仅显示匹配类型的通道。 | `GET /api/v1/io-assignment/tags/?io_type=AI&coupled=uncoupled&search=101`。 |
| WIR-22 | 接线设备管理：IOCard/Barrier/Isolator/Relay 等存于 APPARATUS。IOCard 增加 `io_type` 与 `channel_count`；Barrier 增加 `resistance/capacitance/inductance`(供 CALC-11/12 本安计算)。设备可关联端子排或通道。自定义设备类别及其属性字段经 §15.8 UDF 定义。 | category 字段区分类型 + 类型驱动动态属性表单。 |

### 10.7 现场总线支持

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| WIR-23 | Foundation Fieldbus 设计：FF 设备经 CONNECTOR(含 CONNECTOR_PIN)连接到 Segment。段参数：最大电缆长度、最大分支长度、最大设备数、最大电流、段电容限制（存 `fieldbus_segment_config`）。创建 FF 仪表(`cmpnt_cat_id=2`)后分配到段。功能块管理：FF 仪表配置功能块(AI/AO/PID)，类型存 FUNCTION_BLOCK_TYPE，实例存 COMPONENT_FUNCTION_BLOCK。虚拟标签(`cmpnt_cat_id=9`)：每个功能块输出可创建虚拟标签并独立参与 I/O 分配。 | FieldbusSegment + Connector/ConnectorPin + FunctionBlock 模型。 |
| WIR-24 | Profibus DP/PA 设计：DP 设备(`cmpnt_cat_id=10`)与 PA 设备(`cmpnt_cat_id=11`)分别管理；PA 经 DP/PA Coupler 连接到 DP 网络。段参数：波特率、最大站数、最大电缆长度。 | ProfibusSegment 模型 + DP/PA 设备分配。 |
| WIR-25 | 段参数验证：验证 (1) 段电缆总长 ≤ 规范最大值 (2) 分支长度 ≤ 最大值 (3) 设备数 ≤ 最大设备数 (4) 段电容 = Σ(设备电容 + 电缆电容×长度) ≤ 限值 (5) 段电流 = Σ设备电流 ≤ 供电电流。结果以 Pass/Fail 列表展示并生成 PDF 报告。 | `SegmentValidationService.validate(segment_id)`；WeasyPrint。 |

**【V2.1 增强】M10 接线设计逐模块补全要求：**

- 完整图模型：`Terminal/Wire/WireTerminal/CrossWire` 构成无向图；图的节点为端子（PanelStripTerm），边为导线连接（WireTerminal）。
- 连接不变量：一根导线最多连接两个端子（两端各一个）；一个端子可连接多根导线。
- 信号传播停止条件：遇到未连接端子、路径分叉、已有不同信号且非 force 模式、设备边界规则不允许时停止传播；记录 `propagation_trace`。
- 跨线算法：遍历两侧端子排的 signal 和 signal_level，匹配条件为同一面板内、相同信号级别。
- I/O 分配状态机：CSTag 状态 `Uncoupled → Coupled → Assigned`；`Assigned → Coupled`（取消分配保留耦合）；`Coupled → Uncoupled`（解耦）。
- FF/Profibus 标准阈值配置：FF 段最大电缆长度、最大分支长度、最大设备数、段电容限制等参数存储在 `fieldbus_segment_config` 表中。

---

## 模块11：回路图 (LOOP) — 增强版

回路图模块自动生成仪表回路接线图，以 SVG/Canvas 完全替代 CAD 方式。

### 11.1 功能需求

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| LOOP-01 | 回路图自动生成引擎：基于完整接线数据链(Panel→Strip→Terminal→Wire→Cable)生成。算法：(1) 取回路关联全部标签 (2) 对每标签追踪完整信号路径(DevicePanel→JB/MR→DCS/PLC I/O Channel) (3) 识别路径上全部面板、端子排、电缆、跨线元素 (4) 自动布局：面板按信号流向从左到右(Field→JB→MR→DCS/PLC)，电缆水平连线 (5) 渲染 SVG：面板=矩形、端子=圆形螺丝头、电缆=连线、信号标签标注在导线旁。 | `LoopDrawingGenerationService.generate(loop_id, mode)`；D3.js/Konva.js；dagre-d3 分层布局。坐标系与元素 schema 见 M11 增强要求。 |
| LOOP-02 | 生成方式选择：(1) By Loop——一张图展示回路全部信号完整路径 (2) By Signal——每个信号(标签)一张独立图。经右键菜单 Apply Generation Method 设置，图标左侧显示标记(E=By Loop, ES=By Signal)。 | `generation_method` 存 `loop_drawing_config`；By Signal 对每个 Component 分别调用生成引擎。 |
| LOOP-03 | 回路图模板与布局：`loop_drawing_templates` 含 (1) 模板名 (2) 图框(Title Block)SVG 定义：项目名/文档编号/修订号/日期/绘图人字段位置 (3) 接线表现方式(Horizontal/Diagonal/Vertical) (4) 面板排列(Linear/Grouped) (5) 图纸尺寸(A3/A4/A1)。可将模板分配给单个或批量回路(`loop_template_assignments`)。**与 §6.6 关系**：本表为 LOOP 模块内置模板；图框与标题栏统一纳入 §6.6 DeliverableTemplate(LOOP_DIAGRAM，DTL-06)，两者以 §6.6 为准，`loop_drawing_templates` 保留布局选项部分。 | 模板 CRUD + SVG 图框编辑器 + 批量分配 API。 |
| LOOP-04 | 回路图标注：(1) 文本(可设字体/大小/颜色) (2) 线条(直线/折线/箭头) (3) 形状(圆/矩形高亮)。持久化两级：图纸级(仅当前回路图)与布局级(应用于使用该模板的全部回路图)。存 `loop_drawing_annotations(annotation_id, drawing_id/template_id, type, position_json, style_json, content)`。 | SVG 标注图层(独立于接线数据层) + Fabric.js overlay。 |
| LOOP-05 | 宏(Macro)功能：`@{ComponentField}` 格式(如 `@{Manufacturer}`、`@{Model}`、`@{CableType}`、`@{WireColor}`)，解析时从 Component/Cable/Wire 关联表查实际值。宏可设标题(Label)、字体、位置(X/Y)、是否显示 Label，存 `loop_drawing_macros`。解析优先级 Component→Cable→Wire→Panel。**与 §6.6 关系**：`@{}` 为 §6.6.3 `{{}}` 语法的别名，二者共用解析器。 | `MacroResolver` 类 + SVG text 渲染。 |
| LOOP-06 | 回路图在线编辑：选择图上元素(面板/电缆/导线)右键 Properties 打开侧边栏属性编辑，修改导线颜色、电缆名等。**不直接修改 SVG**，而是改底层数据后重新生成(§4.5 第 6 条：数据库是唯一事实源)。 | 右键菜单 → 属性表单 → 保存后调用生成引擎刷新。 |
| LOOP-07 | 批量回路图生成：多选回路批量提交；>5 张走 Celery 异步，WebSocket 推送进度(已完成/总数)；完成后每张图可在独立 Tab 查看；支持批量导出为 PDF 合集。 | BatchGenerationService + Celery；PyPDF2 合并。 |
| LOOP-08 | 回路图导出：(1) PDF——按图纸尺寸，含标题栏 (2) SVG——矢量可再编辑 (3) PNG/JPEG——可配置 DPI(150/300)。可选择是否包含标注层。 | SVG→PDF(WeasyPrint/Puppeteer)、SVG→PNG(cairosvg)。 |
| LOOP-09 | 面板条形图(Panel Strip Diagram)：基于面板与端子排数据生成报告，显示每个端子排双侧连接：左侧连接(电缆/信号) \| 端子编号 \| 右侧连接(电缆/信号)。每面板一张。 | `PanelStripReportService.generate(panel_id)`；表格式 SVG/PDF。 |
| LOOP-10 | 条带信号报告(Strip Signal Report)：显示每个端子的端子编号、信号名、信号级别、连接导线与电缆信息，用于审查端子排利用率与信号分配正确性。 | `StripSignalReportService` + PDF/Excel；查询 PanelStripTerm JOIN WireTerminal JOIN Wire。 |

**【V2.1 增强】M11 回路图逐模块补全要求：**

- 布局坐标系统：SVG 画布使用逻辑坐标系，面板按信号流向从左到右排列（Field → JB → MR → DCS/PLC），Y 轴为信号分组。
- SVG 元素 schema：每个面板渲染为 `{type: "panel", id, x, y, width, height, name, category}`；每根导线为 `{type: "wire", from_term_id, to_term_id, path_points, signal, color}`。
- 宏解析优先级：宏 `@{field}` 按优先级从 Component → Cable → Wire → Panel 链查找字段值。
- 批量导出队列：批量 > 5 张图使用 Celery 异步任务，前端通过 WebSocket 接收进度。
- 可视化差异验收：生成的 SVG 中所有面板、端子、导线、信号标注与数据库一致。

---

## 模块12：Hook-Up管理 (HU) — 增强版

Hook-Up 模块管理仪表安装细节图与物料清单(BOM)，含安装物料库管理、物料关联与 BOM 计算。

### 12.1 数据模型定义

| Django Model | 表名 | 关键字段 |
|--------------|------|---------|
| HookUpItemLibrary | hookup_item_library | `lib_id(PK)`, `lib_name(VARCHAR 50)`, `description(TEXT)`, `is_active(BOOL, 每个 Plant 仅一个活动库)` |
| HookUpSubLibrary | hookup_sub_library | `sub_lib_id(PK)`, `lib_id(FK→Library)`, `sub_lib_name(VARCHAR 50)`, `piping_class_id(FK→PipingClass, nullable)` |
| HookUpItem（物料项） | hookup_item | `item_id(PK)`, `sub_lib_id(FK)`, `item_name(VARCHAR 100)`, `item_size(VARCHAR 20)`, `manufacturer_id(FK)`, `material(VARCHAR 50)`, `unit(ENUM: Each/Meter/Foot/Set)`, `description(TEXT)` |
| HookUpType | hookup_type | `type_id(PK)`, `type_name(VARCHAR 50, 如 Flow/Temperature/Level/Valves)`, `description(TEXT)` |
| HookUp | hookup | `hookup_id(PK)`, `type_id(FK→HookUpType)`, `hookup_name(VARCHAR 100, 如 'FLOW INSTR. BELOW RUN-LIQUID')`, `description(TEXT)`, `symbol_file(FileField→FileAsset, 安装符号 SVG)` |
| HookUpTypeInstrType | hookup_type_instr_type | 关联表：`type_id(FK)`, `func_type_id(FK→ComponentFunctionType)`。限定可分配的仪表类型 |
| HookUpTagAssignment | hookup_tag_assignment | `assign_id(PK)`, `hookup_id(FK)`, `cmpnt_id(FK→Component)`, `include_in_bom(BOOL)`, `is_additional(BOOL, 附加仪表)` |
| HookUpItemAssociation | hookup_item_association | `assoc_id(PK)`, `hookup_id(FK)`, `item_id(FK→HookUpItem)`, `quantity(INT, 每仪表需求量)`, `spares_percent(FLOAT, 默认 10.0)` |
| HookUpBOM | hookup_bom | `bom_id(PK)`, `hookup_id(FK, nullable)`/`type_id(FK, nullable)`, `dwg_name(VARCHAR 50)`, `generated_date(DateTime)`, `rev_no(VARCHAR 10)` |
| BOMSnapshot | bom_snapshots | `id(PK)`, `bom_id(FK→HookUpBOM)`, `data_json(JSONB, 完整数据快照)` |

全部表按 §4.1.1 追加审计字段，位于租户 schema。

### 12.2 功能需求

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| HU-01 | Hook-Up 物料库管理：三级 Library→SubLibrary→Item；子库可关联配管等级(§9.2 PipingClass)用于按规格过滤物料。物料项含名称(如 '1/2" Ball Valve')、尺寸、制造商、材质、计量单位、描述。支持搜索(名称/尺寸/材质)与 Excel 批量导入(经 IFC-01)。 | 三级 CRUD + openpyxl 导入。 |
| HU-02 | 活动物料库设置：每个 Plant 仅一个活动物料库；设置后全部物料关联基于该库。切换时提示确认(已有关联可能失效)。 | Plant 增加 `active_hookup_lib_id`；切换 API 校验兼容性。 |
| HU-03 | Hook-Up 类型与 Hook-Up 创建：项目级创建类型(Flow/Temperature/Level/Valves)，类型下创建具体 Hook-Up(含名称、描述、安装符号 SVG)。类型可关联仪表功能类型，限定可分配的仪表。 | HookUpType/HookUp CRUD；SVG 符号经 FileAsset 存储。 |
| HU-04 | 仪表标签分配到 Hook-Up：可用列表按类型关联的仪表类型自动过滤。分配时设置 (1) 是否计入 BOM (2) 是否为附加仪表(不增基础数量但影响备品)。支持批量分配与跨多个 Hook-Up 分配。 | `POST /api/v1/hookups/{id}/assign-tags/`。 |
| HU-05 | 物料关联到 Hook-Up：从活动物料库选择物料项，指定每仪表需求量与备用百分比。物料列表以网格展示，支持内联编辑。 | AG Grid 内联编辑；过滤 `Item.objects.filter(sub_library__library__is_active=True)`。 |
| HU-06 | BOM 生成：按 Hook-Up 类型或特定 Hook-Up 生成。**计算公式**：总数量 = `ceil((关联仪表数 + 附加仪表数) × 单位数量 × (1 + 备用百分比/100))`（向上取整，见 M12 增强要求）。报告含物料名/尺寸/材质/制造商/单位/单位数量/关联仪表数/备品百分比/总数量，支持按制造商分组；PDF 与 Excel 输出。 | `BOMCalculationService.generate()`；聚合 HookUpItemAssociation JOIN HookUpTagAssignment；经 §6.6 BOM_MATERIAL 模板渲染。 |
| HU-07 | BOM 修订管理：每次生成创建修订记录(bom_id, dwg_name, rev_no, generated_date)，文档编号自动生成；可按编号打开历史版本；支持比较两修订版差异(物料数量变化)。 | 复用 §6.1 通用 Revision 机制；快照存 `bom_snapshots`。 |
| HU-08 | Hook-Up 图纸生成：PDF 含 (1) 安装符号图(自 symbol_file 加载 SVG) (2) 关联仪表标签列表(Tag/Type/Service) (3) 物料列表(名称/尺寸/数量) (4) 标题栏(项目名/文档编号/修订号)。 | SVG 嵌入 + 表格合成 → WeasyPrint；经 §6.6 HOOKUP_DRAWING 模板(DTL-06 图框)渲染。 |

**【V2.1 增强】M12 Hook-Up 逐模块补全要求：**

- 物料库层级：Library → SubLibrary → Item，每层有独立的名称、描述、状态。
- BOM 舍入规则：总数量 = ceil((关联仪表数 + 附加仪表数) × 单位数量 × (1 + 备用百分比/100))；按整数向上取整。
- 备品计算：备用百分比默认 10%，可按物料项单独配置。
- 历史版本快照：每次生成 BOM 时存储完整数据快照到 `bom_snapshots` 表。
- 图纸模板和材料编码规则：Hook-Up 图纸使用标准模板，材料编码遵循 `{MaterialCategory}-{Size}-{Spec}` 格式。

---

# 第三部分：规则与管理模块

## 模块13：业务规则引擎 (RULE) — 新增模块

本模块提供可配置业务规则引擎，允许管理员定义数据一致性规则与 GUI 控制规则，替代硬编码业务逻辑。

### 13.1 功能需求

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| RULE-01 | 规则类型：(1) **关系规则**——两个 Item Type 之间的一致性检查(如 Instrument 关联 Channel 时校验 I/O Type 匹配) (2) **单组件规则**——单个 Item Type 属性检查(如 Loop Service 在同一 Unit 内唯一) (3) **GUI 规则**——按条件禁用属性对话框中的特定字段(如 Panel Category='DCS' 时禁用某些字段)。 | `rule_definitions` + RuleEngine 类；`rule_type` 枚举 RELATION/SINGLE_COMPONENT/GUI。 |
| RULE-02 | 规则定义数据模型：`rule_id(PK)`, `rule_name(VARCHAR 100)`, `description(TEXT)`, `rule_category(ENUM: System/Engineering)`, `rule_action(ENUM: CheckData/ControlGUI)`, `is_disabled(BOOL, Engineering 默认 true)`, `priority(1-100, 1=最低)`, `folder_path(树形管理器路径)`。**系统规则不可修改/禁用/删除**；工程规则可完全管理。 | Django Model + TreeView 管理界面；系统规则经 migration 预置。 |
| RULE-03 | 规则组件定义：每条规则定义 1–2 个组件(`rule_components`)，引用 Item Type(Instrument/Loop/Cable/Panel/Channel/TerminalStrip…)。关系规则必须两个组件，单组件规则一个。组件决定触发上下文——修改该 Item Type 属性时触发评估。 | `rule_components(rule_id FK, component_number INT 1/2, item_type VARCHAR)`。 |
| RULE-04 | 过滤条件定义：`rule_filters` 限定规则生效条件。表达式含 `operand`(组件引用)、`property`、`operator`(=/<>/>/</>=/<=/Contains/Like/Empty/Not Empty/IN/Odd/Even)、`value`、`logical_operator`(AND/OR)。例：`[Component2.PanelCategory = 'DCS'] AND [Component2.PanelManufacturer = 'CENTUM CS 3000']`。 | 过滤条件构建器 UI(复用 EDE-10 复杂过滤器)；后端 FilterEvaluator。 |
| RULE-05 | 一致性检查定义：`rule_consistency` 每表达式含 `operand1`(组件 1 或 2)、`property1`、`copy_action`(None/CopyToOperand1/CopyToOperand2)、`compare_operator`(同过滤操作符 + Unique/ExistingList/CustomValidation/CustomUpdate)、`operand2`、`property2_or_value`、`action_on_inconsistency`(Error/Warning/Log/Reject)。Unique=检查值在指定范围内唯一；ExistingList=检查值存在于 supporting 表；Custom*=调用外部函数(RULE-06)。 | ConsistencyEvaluator；`evaluate()` 返回 `RuleResult(pass/fail, message, suggestion)`。AST 结构见 M13 增强要求。 |
| RULE-06 | 外部函数扩展：(1) **CustomValidation**——`def custom_validate(attr_name:str, attr_value:str, attr_modified:bool, item_type:str, primary_attr:str, primary_value:str, unit_id:int) -> bool`，返回 False 则拒绝修改 (2) **CustomUpdate**——`def custom_calculate(params:dict) -> dict`，返回修改后属性值。注册于 `custom_rule_functions(function_name, module_path, function_type, sandbox_level)`。**沙箱**：禁止文件 I/O、网络访问、exec/eval(见 M13 增强要求)。 | `importlib.import_module()` 动态加载 + `RuleEngine.invoke_custom_function()`。 |
| RULE-07 | 规则执行引擎：保存前评估流程 (1) 取被修改 Item 类型与修改属性列表 (2) 查询全部未禁用且相关的规则(按 priority 降序) (3) 逐条：先评估过滤条件→通过则评估一致性表达式 (4) 按 action 执行：**Error**=阻止保存并显示消息(用户可接受或拒绝)、**Warning**=显示警告但允许强制保存、**Log**=写日志不阻止、**Reject**=直接拒绝不可覆盖 (5) 高优先级的 Reject/Error 阻止低优先级规则执行。**性能**：单次评估 ≤100ms，批量保存总计 ≤1s。 | `RuleEngine.evaluate(item, modified_fields)`；在 DRF `Serializer.validate()` 中调用；返回 violations 列表供前端弹窗。 |
| RULE-08 | GUI 规则执行：前端加载属性表单时 (1) 调 `GET /api/v1/rules/gui-evaluation/{item_type}/{item_id}/` (2) 后端评估适用 GUI 规则 (3) 返回 `disabled_fields` 列表 (4) 前端据此设置字段 disabled/readonly。 | 表单初始化时调用；与 §15.8 ADM-11 字段可见性覆盖叠加(两者取并集，任一禁用即禁用)。 |
| RULE-09 | 规则管理界面：左侧树形视图(按模块分组的规则文件夹，每模块下含 Consistency 与 Disable Properties 子文件夹)；右侧 4 个 Tab：General(名称/描述/类型/动作/优先级/禁用开关)、Rule Components、Filter(过滤条件表格编辑器)、Consistency(一致性表达式编辑器)。支持创建/编辑/删除/复制/移动/启用/禁用。 | React 规则管理器 SPA(TreeView + TabPanel + DataGrid)。 |
| RULE-10 | 预置工程规则(默认禁用，管理员可启用)：(1) *Backup Link Master is not Null for DCS/CENTUM CS 3000*——Instrument 关联 CENTUM CS 3000 DCS Panel 通道时，Backup Link Master 必须为 Y 或 N (2) *KKS Cable Name Rule*(默认启用)——电缆采用 KKS 命名规范时验证名称符合 KKS 段规则。 | Django migration 预置到 `rule_definitions` 及关联表。 |

**【V2.1 增强】M13 规则引擎逐模块补全要求：**

- 规则表达式 AST：`{type: "expression", operand1: {component, property}, operator, operand2: {component_or_value, property_or_value}, action_on_fail}`。
- 可调用外部函数 registry：`custom_rule_functions` 表（`function_name, module_path, function_type, sandbox_level`）。
- 安全沙箱：自定义规则函数在受限沙箱中执行，禁止文件 I/O、网络访问、`exec/eval`。
- 执行时机：保存前评估（pre_save hook），GUI 规则在表单加载时评估。
- 规则冲突处理：高优先级规则的 Reject/Error 结果阻止低优先级规则执行；同优先级冲突记录日志。
- 性能约束：单次规则评估 ≤ 100ms；批量保存时规则评估总时间 ≤ 1s。

---

## 模块14：数据库完整性管理 (DBI) — 新增模块

本模块提供数据库完整性检查、问题诊断与自动修复功能。

### 14.1 功能需求

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| DBI-01 | 完整性检查引擎：可选检查范围 (1) **表结构**——验证 Django Model 对应表存在且结构正确 (2) **主键**——验证主键定义正确 (3) **外键**——验证约束有效，检测孤立记录(子记录引用的父记录不存在) (4) **索引**——验证必要查询性能索引存在(含 §15.8.3 自定义字段表达式索引) (5) **初始记录**——验证 supporting 表 ID=0 初始行存在 (6) **参考数据**——验证必要参考数据行存在。**在租户 schema 级别执行**（逐租户或指定 ProjectTenant）。 | `DatabaseIntegrityChecker`；`connection.introspection` 取元数据与 Model 定义对比；孤立记录用 `LEFT JOIN WHERE parent IS NULL`。 |
| DBI-02 | 检查报告生成：三类日志 (1) **complog**——问题分类(表结构/外键/数据一致性)、严重级别(Error/Warning/Info)、描述、涉及表名与记录 ID、SQL 诊断语句 (2) **fix_suggestions**——每个问题的修复 SQL 建议(DELETE 孤立记录、INSERT 缺失初始记录、ALTER TABLE 添加索引) (3) **special_operations**——需人工业务操作修复的问题(如仪表类型 Profile 不匹配)。可在线查看与下载。 | Celery 异步执行；结果存 `integrity_check_results(check_id, check_time, result_json, fix_json, status)`。状态机 §4.4.6。 |
| DBI-03 | 问题修复功能：(1) 逐条勾选要修复的问题 (2) 预览修复 SQL (3) Apply Fix 执行。**修复前强制备份确认**（必须勾选"已完成数据库备份"）。**修复 SQL 仅允许预定义白名单模板**，禁止任意 SQL(见 M14 增强要求)。记录到 `integrity_fix_log(fix_id, check_id, fix_sql, executed_at, executed_by, success)`。修复后建议重跑检查验证。 | `POST /api/v1/db-integrity/apply-fix/`；事务内执行 + 审计日志；权限 Administrator/Project Engineer。 |
| DBI-04 | 定期检查计划：配置频率(Daily/Weekly/Monthly)、范围(全部/仅外键/仅参考数据)、通知方式(邮件/系统内)。结果自动存储；发现 Error 级问题时告警系统管理员。 | Celery Beat 定时任务(存 `integrity_schedule`) + 邮件/WebSocket 通知。 |
| DBI-05 | 检查触发时机建议：在以下操作前/后提供"运行完整性检查"快捷入口：(1) 大规模数据导入后 (2) 数据合并前后 (3) 项目(租户)初始化后 (4) 系统版本升级前后 (5) 跨 Plant 层级复制数据后。 | 在 Import/Merger 等模块前端流程中集成入口按钮。 |

### 14.2 预置检查项 registry

除 M14 增强要求中列出的 IS 模板/SIF/采购相关检查项外，`integrity_check_registry` 还须预置 DBI-01 六类结构性检查（`STRUCT_TABLE_MISSING`、`STRUCT_PK_INVALID`、`FK_ORPHAN_RECORD`、`INDEX_MISSING`、`INITIAL_ROW_MISSING`、`REFERENCE_DATA_MISSING`），severity 依次为 Error/Error/Error/Warning/Error/Warning，全部 `auto_fixable` 按白名单模板判定。

**【V2.1 增强】M14 数据库完整性逐模块补全要求：**

- 检查项 registry：`integrity_check_registry` 表（`check_id, check_name, check_category, check_sql, severity, auto_fixable`）。
- **【V2.1 增强·IS模板】预置检查项（种子）**：`IDX_IO_ESTIMATE_VS_ASSIGNED`（索引 TagIOAllocation 估算 vs WIR 实际 CSTag 数差异，按 Tag × control_system × signal_kind，severity=Warning，IDX-16）；`IDX_SIL_CAPABILITY_BELOW_REQUIRED`（sil_capability < required_sil，Error，D8）；`SIF_MISSING_ELEMENT_ROLE`（Approved SIF 缺 SENSOR 或 FINAL_ELEMENT 元件，Error）；`SIF_ELEMENT_WITHOUT_SIS_IO`（SIF 元件 Tag 无 control_system=SIS 的 IOAllocation，Warning）；`SIF_RESPONSE_TIME_EXCEEDS_PST`（required_response_time_s ≥ process_safety_time_s，Error）；`PROC_LONG_LEAD_WITHOUT_ORDER`（is_long_lead 且状态未达 Ordered 而 required_on_site_date 临近，Warning，D7）；`IDX_PID_REVISION_STALE`（pid_revision_checked 低于 Drawing 当前版本，Warning，IDX-18）；`IDX_TARGET_PANEL_MISMATCH`（early target_system_panel 与 WIR 实际分配柜位不一致，Warning）；`DDP_LINE_SUPERSEDED_PIPING_CLASS`（Line 引用 Superseded 的 PipingClass，Error，DDP-13）；`PD_DESIGN_COND_DRIFT`（Approved ProcessDataCase 的 design_* 与当前 PipingClass 不一致，Warning，DDP-13）；`IDX_COMPLETENESS_BELOW_THRESHOLD`（completeness_pct < 项目阈值，Info，IDX-17）。均 `auto_fixable=False`。
- 修复 SQL 白名单：仅允许预定义的修复 SQL 模板执行，禁止任意 SQL。
- 安全审批：修复操作需 Administrator/Project Engineer 角色，执行前强制备份确认。
- 备份确认：管理员必须勾选"已完成数据库备份"复选框后方可执行修复。
- 结果状态机：`Queued → Running → Completed / CompletedWithErrors / Failed`。
- 定时任务配置：通过 Celery Beat 配置检查频率（Daily/Weekly/Monthly），存储在 `integrity_schedule` 表。

---

## 模块15：系统管理 (Administration Module) — 新增模块【V2.1 重大更新】

> **SPI 对应**：Administration Module
> **Django App**：`administration` + `tenants`
> **对标产品**：Hexagon SmartPlant Instrumentation (SPI)

> **【V2.1 重大更新说明】** 本模块已依据项目知识库中的代码实现规格（`SPECIFICATION.md` v0.3.3，外部文档）之「多租户架构」与「模块 1.1 管理模块」两章全面重写，使功能需求与代码实现规格对齐。主要变更：
> 1. **多租户由"单库共享 schema + domain_id"改为"PostgreSQL Schema 隔离"**（django-tenants），租户单位为 **ProjectTenant（工程项目）**，通过 **X-Project-ID Header + 自定义中间件**切换租户上下文。
> 2. **角色体系由 5 个角色扩展为 7 个分级角色**（Administrator / Project Manager / Project Engineer / Instrumentation Engineer / Process Engineer / Mechanical Engineer / Guest）。
> 3. **新增工程项目组（ProjectTaskForce）** 及项目可见性强约束。
> 4. **工厂层级改为 ProjectTenant → Client → Site → Plant → PlantHierarchy(MPTT: PLANT/AREA/UNIT)**。
> 5. **命名规则（NamingConvention）补齐 SPI 特有的层级格式、段定义、预设模板、验证流程与自动生成**。
>
> 因第四部分 §4.1.4「Domain 隔离」与本节存在架构口径差异，已在 §4.1.4 增补对齐说明，并以本节的 Schema 隔离方案为准。

### 15.1 多租户架构 (Multi-Tenancy)

系统采用 **PostgreSQL Schema 隔离**实现多租户架构，每个工程项目（ProjectTenant）拥有独立的数据库 Schema。

#### 15.1.1 数据分类（Schema 归属）

| 分类 | Schema | 模型 | 说明 |
|------|--------|------|------|
| 共享数据 | public | Organization, User, Role | 跨项目共享 |
| 租户元数据 | public | ProjectTenant | 租户配置（继承 TenantMixin） |
| 框架契约 | public | ProjectDomain *(contract-only)* | 仅满足 django-tenants `TENANT_DOMAIN_MODEL` 契约；本系统不使用域名/子域路由，admin/API 已注销，表保持为空 |
| 成员关系 | public | ProjectTaskForce, TaskForceMembership | 用户-项目组关联（原 ProjectMembership 已删除） |
| 审计日志 | public | AuditLog | 全局审计 |
| 项目数据 | project_xxx | Client, Site, Plant | 项目层级 |
| 工程数据 | project_xxx | PlantHierarchy, Loop, Tag | 仪表数据 |
| 配置数据 | project_xxx | InstrumentType, NamingConvention | 项目配置 |

#### 15.1.2 功能需求

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| ADM-T01 | 租户切换机制：前端用户选择项目后将 `project_id` 存入 localStorage；API 请求由 axios 拦截器自动注入 Header `X-Project-ID: {project_id}`；后端中间件读取 Header 切换到对应 Schema；ORM 查询自动在租户 Schema 中执行。 | `apps.tenants.middleware.HeaderBasedTenantMiddleware`（亦称 `TenantContextMiddleware`）读取 header → `ProjectTenant.objects.get(pk=project_id)` → `connection.set_tenant(tenant)`（`SET search_path TO "project_xxx", public`）。 |
| ADM-T02 | 租户生命周期：创建 ProjectTenant 时自动创建独立 PostgreSQL Schema（`schema_name` 从 `project_no` 自动生成）；删除 ProjectTenant 时自动删除对应 Schema。 | `ProjectTenant` 继承 django-tenants `TenantMixin`，`create_schema()` / `drop_schema()` 由框架封装。 |
| ADM-T03 | 路由机制约束：本系统**不使用** Host-header / 子域路由，统一采用 Header(`X-Project-ID`) + 中间件。`settings.TENANT_DOMAIN_MODEL = "tenants.ProjectDomain"` 不可删除（框架启动契约），但运行时从不查询该表。 | 部署形态（单域名/负载均衡/读写分离/K8s/路径级路由）均不需要 ProjectDomain；仅"子域多租户 SaaS"才需恢复 `TenantMainMiddleware` 及 ProjectDomain admin/API。 |
| ADM-T04 | 租户管理 API。 | `ProjectTenantViewSet`，端点见 §15.6。 |

#### 15.1.3 租户管理 API

```
GET    /api/v1/tenants/projects/              # 项目列表
POST   /api/v1/tenants/projects/              # 创建项目 (自动创建 Schema)
GET    /api/v1/tenants/projects/{id}/         # 项目详情
PUT    /api/v1/tenants/projects/{id}/         # 更新项目
DELETE /api/v1/tenants/projects/{id}/         # 删除项目 (删除 Schema)
POST   /api/v1/tenants/projects/{id}/switch/  # 切换到此项目
GET    /api/v1/tenants/projects/current/      # 当前项目上下文
```

### 15.2 基于角色的用户管理系统 (RBAC)

#### 15.2.1 角色层级定义

> **【已裁决 2026-07-10，决策 D5】权限等级与角色职能双轴模型**：权限等级（`Role.level`）固定为 **5 级**（IntegerChoices 1–5，与现行代码一致，Level 2 预留未用）；角色（`Role`）为 **7 个系统预设**（§15.2.2 预设角色表）。等级决定权限高低的比较与继承，角色决定职能与专业数据范围；**同级可挂多个角色**（如 L4 的 PM/PE、L3 的三个专业工程师）。权限判定一律走 `Role.permissions` JSON 矩阵与 §15.2.4 数据权限矩阵，**禁止在业务代码中以 `role.code` 硬编码分支**（Administrator 旁路除外）。

系统采用分层角色模型，从低到高依次为：

| Level | 角色 | code | 职责 |
|-------|------|------|------|
| 5 | Administrator (系统管理员) | ADMIN | 系统最高权限：管理所有用户/角色/权限、创建管理所有项目组、加入/移除任意用户至任意项目组、系统配置、查看所有审计日志、数据库备份恢复 |
| 4 | Project Manager (项目经理) | PROJ_MGR | 项目级最高权限（业务/进度/资源/商务）。PM 与 PE 同级同权限，仅业务定位不同 |
| 4 | Project Engineer (项目工程师) | PROJ_ENG | 项目级最高权限（技术执行）。对所有专业数据 CRUD、基于工程项目号创建项目组、审批变更、发布规格书和图纸、管理项目层级 |
| 3 | Instrumentation Engineer (仪表工程师) | INST_ENG | 仪表专业数据 CRUD（Tag/Loop/Specification/Wiring/LoopDrawing/Cable）；对其他专业只读 |
| 3 | Process Engineer (工艺工程师) | PROC_ENG | 工艺专业数据 CRUD（ProcessData）；对其他专业只读 |
| 3 | Mechanical Engineer (机械工程师) | MECH_ENG | 机械/管道专业数据 CRUD（PipeSpecification/ProcessConnection）；对其他专业只读 |
| 1 | Guest (访客) | GUEST | 所有数据只读，可查看和导出，不能增删改 |

#### 15.2.2 Role（角色模型）

| 字段 | 说明 |
|------|------|
| id | BigAutoField 主键 |
| organization | FK → Organization（角色按组织隔离） |
| code | 角色代码（组织内唯一，稳定标识符）：ADMIN/PROJ_MGR/PROJ_ENG/INST_ENG/PROC_ENG/MECH_ENG/GUEST |
| name | 角色显示名（人类可读，如 "Project Manager"） |
| level | 角色等级（IntegerChoices：1=Guest .. 5=Administrator） |
| description | 角色描述 |
| permissions | JSONField（按资源粒度的 CRUD 列表，如 `{"tag": ["create","read","update","delete"], "task_force": ["create","read"], "audit_log": ["read"]}`） |
| is_system_role | 是否系统预设角色（不可删除） |
| display_order | 同级排序 tie-breaker（数值小者排前） |
| created_at, updated_at | 时间戳 |

排序规则：`ordering = ["-level", "display_order", "name"]`（高级别在前；同级按 display_order 升序；最后按 name 字母序兜底）。

预设角色（按显示顺序）：

| code | name | level | display_order |
|------|------|-------|---------------|
| ADMIN | Administrator | 5 | 10 |
| PROJ_MGR | Project Manager | 4 | 20 |
| PROJ_ENG | Project Engineer | 4 | 30 |
| INST_ENG | Instrumentation Engineer | 3 | 40 |
| PROC_ENG | Process Engineer | 3 | 50 |
| MECH_ENG | Mechanical Engineer | 3 | 60 |
| GUEST | Guest | 1 | 70 |

#### 15.2.3 User（用户模型扩展）

| 字段 | 说明 |
|------|------|
| id | UUID |
| username | 用户名（唯一） |
| email | 邮箱（唯一） |
| first_name / last_name | 名 / 姓 |
| role | FK → Role（系统角色） |
| department | 部门 |
| employee_id | 工号 |
| phone | 电话 |
| avatar | 头像 |
| is_active | 是否激活 |
| last_login | 最后登录时间 |
| created_at, updated_at | 时间戳 |

约束：每个用户必须有一个系统角色；用户可属于多个工程项目组。

#### 15.2.4 数据权限矩阵

> Level 4 的两个角色（Project Manager / Project Engineer）共用同一权限列。
> 图例：C=Create, R=Read, U=Update, D=Delete, -=无权限；CR* = PM/PE 只能创建/管理自己创建的项目组。

| 数据类型 | Admin (L5) | PM / Proj Eng (L4) | Instr (L3) | Proc (L3) | Mech (L3) | Guest (L1) |
|----------|-----------|--------------------|-----------|-----------|-----------|-----------|
| 用户管理 | CRUD | - | - | - | - | - |
| 角色管理 | CRUD | - | - | - | - | - |
| 项目组管理 | CRUD | CR* | - | - | - | - |
| Project (工程项目) | CRUD | RU | R | R | R | R |
| Plant Hierarchy | CRUD | CRUD | R | R | R | R |
| Tag (仪表位号) | CRUD | CRUD | CRUD | R | R | R |
| Loop (控制回路) | CRUD | CRUD | CRUD | R | R | R |
| Specification (规格书) | CRUD | CRUD | CRUD | R | R | R |
| Wiring (接线) | CRUD | CRUD | CRUD | R | R | R |
| LoopDrawing (回路图) | CRUD | CRUD | CRUD | R | R | R |
| Cable (电缆) | CRUD | CRUD | CRUD | R | R | R |
| ProcessData (工艺数据) | CRUD | CRUD | R | CRUD | R | R |
| PipeSpecification | CRUD | CRUD | R | R | CRUD | R |
| ProcessConnection | CRUD | CRUD | R | R | CRUD | R |
| 审计日志 | R | - | - | - | - | - |
| 系统配置 | CRUD | - | - | - | - | - |

### 15.3 工程项目组 (Project Task Force)

#### 15.3.1 数据模型

**ProjectTaskForce（工程项目组）**

| 字段 | 说明 |
|------|------|
| id | UUID |
| name | 项目组名称（如 "乙烯项目组"） |
| code | 项目组代码（全局唯一） |
| project | FK → ProjectTenant（关联工程项目，一对一，project 字段唯一） |
| description | 描述 |
| created_by | FK → User（创建者） |
| created_by_role | 创建者角色（Administrator / Project Engineer） |
| is_active | 是否激活 |
| created_at, updated_at | 时间戳 |

约束：每个 Project 只能关联一个 ProjectTaskForce；项目组代码全局唯一。

**TaskForceMembership（项目组成员关系）**

| 字段 | 说明 |
|------|------|
| id | UUID |
| task_force | FK → ProjectTaskForce |
| user | FK → User |
| role_in_project | 用户在该项目中的角色（可覆盖系统角色） |
| joined_at | 加入时间 |
| added_by | FK → User（添加者） |
| is_active | 是否激活 |
| created_at, updated_at | 时间戳 |

约束：`(task_force, user)` 唯一；用户可属于多个项目组。

#### 15.3.2 功能需求

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| ADM-TF01 | 项目组创建规则：Administrator 可两种方式创建（①先创建空项目组再分配项目号；②基于已存在 Project 自动创建并关联），并可加入/移除任意用户至任意项目组、编辑/删除任意项目组。Project Engineer 仅能基于已存在 Project 创建项目组（`created_by_role="PROJECT_ENGINEER"`），仅能管理自己创建的项目组，不能修改 project 关联，不能编辑/删除 Admin 创建的项目组。其他角色不能创建/管理项目组。 | `ProjectTaskForceViewSet` + 对象级权限校验（基于 `created_by` 与 `role.level`）。 |
| ADM-TF02 | 项目组权限隔离：不同项目组数据独立、不可互访。所有数据查询自动过滤 `project_id`，用户只能看到所属项目组的数据，API 层强制检查项目组成员关系。Administrator 可访问所有项目组数据。 | 权限检查流程：JWT 身份验证 → 获取用户所属项目组列表 → 校验请求 `project_id` 是否在用户项目组中（否则 403）→ RBAC 角色权限检查（data_scope + action）→ 执行请求。 |
| ADM-TF03 | 项目组管理 UI：左侧项目组列表（Code/Name/Project No./Members/Created By），选中后右侧显示成员列表（Name/Role/Joined/Actions），支持 [+ Add User] / [Remove]。创建对话框区分 Administrator（可选"从已有项目创建"或"先建空组"）与 Project Engineer（必须选择已有项目，自动关联）。 | React 项目组管理 SPA（列表 + 成员面板 + 创建对话框）。 |

#### 15.3.3 项目可见性规则（强约束）

> **核心规则**：未加入任何 `ProjectTaskForce` 的普通用户，不可见也不可操作系统中任何工程项目（`ProjectTenant`）。只有被加入某个 `ProjectTaskForce` 后，才能看到并操作该项目组所对应的工程项目。

| 角色 | 可见项目集合 |
|------|-------------|
| superuser / Administrator (`role.level == ADMINISTRATOR`) | 全部项目（bypass） |
| 其他所有角色（PM / PE / Process / Mechanical / IE / Guest…） | 当前用户作为成员或 leader 的 TaskForce 所关联的 `project_id` 集合 |

判定公式：

```python
accessible_project_ids(user) =
    TaskForceMembership.user == user 的 task_force.project_id 集合
  ∪ ProjectTaskForce.leader == user 的 project_id 集合
```

若集合为空 → 项目列表为空、所有租户级 `/api/v1/*` 请求（带 `X-Project-ID`）返回 403。

实施锚点：

1. **后端辅助**：`apps/administration/access.py::user_accessible_project_ids(user)` — 单一事实来源，返回 `list[int] | None`（`None` 表示管理员全放）。
2. **ProjectTenant 列表/详情**：`ProjectTenantViewSet.get_queryset()` 按该集合过滤（非管理员）。
3. **租户上下文**：`TenantContextMiddleware` 使用该集合填充 `request.available_projects`。
4. **X-Project-ID 校验**：`TenantContextMiddleware` 在请求 `current_project` 不在 `accessible_project_ids` 时返回 `403 {"error": "You are not a member of this project."}` 并重置连接到 public schema。
5. **前端响应**：项目切换器无可见项目时显示「您尚未被加入任何工程项目组，请联系管理员」；直接访问受限 URL 时全局错误处理捕获 403。

与其他权限规则的关系：本规则先于 RBAC（§15.2）执行；与 §15.3.2 的"数据隔离"互补（本规则解决"项目列表可见性"，§15.3.2 解决"项目内数据访问控制"）；Administrator 凭角色身份 bypass。

### 15.4 工程项目层级架构

层级链：**ProjectTenant（public）→ Client → Site → Plant → PlantHierarchy(MPTT: PLANT / AREA / UNIT)**。Client/Site/Plant/PlantHierarchy 均存储在项目独立 Schema（`project_xxx`）中，不同项目数据完全隔离。

#### 15.4.1 ProjectTenant（工程项目/租户 — 顶层对象）

模型 `apps.tenants.models.ProjectTenant`（继承 TenantMixin），Schema：public。

| 字段 | 说明 |
|------|------|
| id | Integer 主键 |
| project_no | 项目编号（全局唯一，如 "PRJ-2025-001"、"ETH-100"） |
| name | 项目名称（如 "100万吨乙烯项目"） |
| schema_name | Schema 名称（自动从 project_no 生成，全局唯一，如 "project_prj2025001"） |
| organization_id | Integer（关联组织） |
| description | 项目描述 |
| status | 项目状态（Active/OnHold/Completed/Archived） |
| start_date / end_date | 开始日期 / 结束日期（可选） |
| hierarchy_config | JSONField（层级结构配置） |
| created_at, updated_at | 时间戳 |

#### 15.4.2 Client（客户/业主 — 租户数据）

模型 `apps.core_engineering.models.Client`，Schema：project_xxx。

| 字段 | 说明 |
|------|------|
| id | Integer 主键 |
| name | 客户名称（如 "中石化"、"巴斯夫"） |
| code | 客户代码（租户内唯一，如 "SINOPEC"、"BASF"） |
| contact_person / contact_email / contact_phone | 联系人信息 |
| address | 地址 |
| created_at, updated_at | 时间戳 |

约束：`code` 在租户 Schema 内唯一；无需 project FK（隐式属于当前租户）。**业务约束**：一个工程项目对应单一客户（前端强制：项目下无客户 → 「+新建客户」，已有客户 → 「编辑客户」，不再提供新建入口；数据库未加 unique 约束，仅 UI/业务流程强制）。

#### 15.4.3 Site（厂区/地点 — 租户数据）

模型 `apps.core_engineering.models.Site`，Schema：project_xxx。

| 字段 | 说明 |
|------|------|
| id | Integer 主键 |
| client | FK → Client |
| name | 厂区名称（如 "镇海炼化"、"上海基地"） |
| code | 厂区代码（如 "ZH"、"SH"） |
| location / address | 地理位置 / 地址 |
| timezone | 时区（默认 "UTC"） |
| created_at, updated_at | 时间戳 |

约束：`(client, code)` 唯一。一个 Client 可有一个或多个 Site。

#### 15.4.4 Plant（工厂/装置 — 租户数据）

模型 `apps.core_engineering.models.Plant`，Schema：project_xxx。

| 字段 | 说明 |
|------|------|
| id | Integer 主键 |
| site | FK → Site |
| name | 工厂/装置名称（如 "乙烯装置"、"芳烃联合装置"） |
| code | 工厂代码（如 "ETH"、"ARO"） |
| description | 描述 |
| capacity | 产能（如 "1000 KTPA"） |
| is_active | 是否激活 |
| created_at, updated_at | 时间戳 |

约束：`(site, code)` 唯一。一个 Site 可有多个 Plant。

#### 15.4.5 PlantHierarchy（工厂层级 — 租户数据）

模型 `apps.core_engineering.models.PlantHierarchy`（MPTT），Schema：project_xxx。

| 字段 | 说明 |
|------|------|
| id | Integer 主键 |
| plant | FK → Plant |
| parent | FK → self（自引用，MPTT） |
| name | 名称（如 "反应区"、"分离区"、"Unit-100"） |
| code | 代码（如 "REACT"、"SEP"、"U100"） |
| node_type | 节点类型（PLANT / AREA / UNIT） |
| description | 描述 |
| lft, rght, tree_id, level | MPTT 字段 |
| created_at, updated_at | 时间戳 |

约束：`(parent, code)` 唯一。PLANT=工厂根节点，AREA=工艺区域，UNIT=工艺单元（仪表 Tag 归属于 Unit）。

#### 15.4.6 层级结构配置（hierarchy_config）

创建项目时通过 `hierarchy_config` 配置层级结构，支持三种预设模板：

- **standard**：完整层级（Client → Site → Plant → Area → Unit）
- **simple**：简化层级（Client → Site → Unit），适合小型项目
- **custom**：用户自定义

配置示例：

```json
{
  "template": "standard",
  "levels": [
    { "name": "Client", "required": true, "default_name": "客户" },
    { "name": "Site", "required": true, "default_name": "主厂区", "allow_multiple": true },
    { "name": "Plant", "required": true, "default_name": "主装置", "allow_multiple": true },
    { "name": "Area", "required": false, "allow_multiple": true },
    { "name": "Unit", "required": true, "allow_multiple": true }
  ],
  "auto_create_defaults": true
}
```

创建项目流程：①输入项目基本信息（Project No./名称/描述）→ ②选择层级模板或自定义配置 → ③系统自动创建默认层级结构 → ④用户随后可编辑调整。

#### 15.4.7 Organization（系统租户 — 可选，SaaS 模式）

| 字段 | 说明 |
|------|------|
| id | UUID 主键 |
| name | 组织名称（如 "XX设计院"、"YY工程公司"） |
| slug | URL 友好标识 |
| settings | JSONField（组织级配置） |
| is_active | 是否激活 |
| created_at, updated_at | 时间戳 |

说明：Organization 用于 SaaS 部署的系统级租户隔离（不同设计院/工程公司数据隔离）；单机部署可忽略此层级。归属关系：Organization（可选）→ ProjectTenant → Client → Site → Plant → Area → Unit。

### 15.5 命名规则 (NamingConvention) — SPI 特有

#### 15.5.1 NamingConvention 模型

目的：强制规范位号格式，从源头杜绝数据录入随意性，支持管理员定义复杂正则表达式命名规则。

| 字段 | 说明 |
|------|------|
| id | UUID |
| project | FK → ProjectTenant |
| name | 规则名称（如 "Standard Tag Naming"、"Cable Naming"） |
| entity_type | 应用实体类型：TAG / LOOP / CABLE / JUNCTION_BOX / TERMINAL_STRIP |
| hierarchy_format | 层级格式类型（见 §15.5.2） |
| pattern | 正则表达式（管理员自定义） |
| pattern_template | 模式模板（用于生成正则表达式） |
| segment_definitions | JSONField（各段定义，见 §15.5.3） |
| separator | 分隔符（默认 "-"） |
| description | 规则说明 |
| examples | JSONField（示例列表） |
| validation_message | 验证失败提示信息 |
| is_active | 是否启用 |
| is_default | 是否为默认规则 |
| priority | 优先级（多规则时的匹配顺序） |
| created_at, updated_at | 时间戳 |

约束：`(project, entity_type, is_default=True)` 唯一；`pattern` 必须是有效正则表达式。

#### 15.5.2 层级格式类型 (Hierarchy Format)

| 格式 | 模式 | 示例 | 说明 |
|------|------|------|------|
| 格式1 | Site-Plant-Area-Unit-Function-Sequence | ZH-ETH-100-U01-FT-001 | 完整层级，大型多厂区项目 |
| 格式2 | Plant-Area-Unit-Function-Sequence | ETH-100-U01-FT-001 | 省略 Site，单厂区项目 |
| 格式3 | Area-Unit-Function-Sequence | 100-U01-FT-001 | 省略 Site/Plant，单装置项目 |
| 格式4 | Unit-Function-Sequence | U01-FT-001 或 FT-001 | 最简格式，小型项目 |
| 格式5 | XXXX-Unit-Function-Sequence | ZH/ETH/100-U01-FT-001 | 灵活前缀，`prefix_source: SITE/PLANT/AREA` 可配置 |
| 格式6 | Custom | 管理员自定义 | 管理员直接输入正则表达式 |

#### 15.5.3 段定义 (Segment Definitions)

每个命名规则由多个段组成，存储在 `segment_definitions` JSONField 中。每段含：`name, display_name, position, type(hierarchy/function/equipment/sequence/custom), source(数据来源), pattern(段正则), min_length/max_length, case(upper/lower/mixed), allowed_values, required, auto_fill, editable`。序列段额外含 `min_value, max_value, padding(前导零), suffix_pattern, auto_increment`。

> **【V2.1 增强·IS模板】新增 `equipment` 段类型**：`source: "apparatus.code"`，位号中嵌入所关联设备/容器编号（如 `BMR-V354-FIT-004-A` 中的 `V354`，或 `BMR-CI374-AIT-008` 中的 `CI374`）。`auto_fill=true` 时从 Tag 的 `appar_id` 取值；Tag 更换设备关联时触发位号一致性校验（规则引擎），提示是否同步重命名。IS 模板实际位号格式 `{Prefix}-{Equipment}-{Function}-{Sequence}[-{Suffix}]` 由此支持（层级格式 5/6 + equipment 段）。

示例（Plant-Area-Unit-Function-Sequence）：

```json
{
  "segments": [
    {"name":"plant","position":1,"type":"hierarchy","source":"plant.code","pattern":"[A-Z]{2,4}","required":true,"auto_fill":true,"editable":false},
    {"name":"area","position":2,"type":"hierarchy","source":"area.code","pattern":"\\d{2,3}","required":true,"auto_fill":true,"editable":false},
    {"name":"unit","position":3,"type":"hierarchy","source":"unit.code","pattern":"U\\d{2}","required":true,"auto_fill":true,"editable":false},
    {"name":"function","position":4,"type":"function","source":"instrument_type.function_code","pattern":"[A-Z]{1,4}","allowed_values":["FT","TT","PT","LT","AT","CV","XV","PSV","PV"],"required":true,"auto_fill":false,"editable":true},
    {"name":"sequence","position":5,"type":"sequence","pattern":"\\d{3,4}[A-Z]?","min_value":1,"max_value":9999,"padding":3,"suffix_pattern":"[A-Z]?","auto_increment":true,"required":true,"editable":true}
  ],
  "separator": "-",
  "case_sensitive": false
}
```

#### 15.5.4 预设命名规则模板

| 模板 | 格式 | 示例 | 正则 |
|------|------|------|------|
| ISA 标准 (ISA-5.1) | {Function}{Sequence}{Suffix} | FT-101, TIC-201A | `^[A-Z]{1,4}-\d{3}[A-Z]?$` |
| 完整层级 | {Site}-{Plant}-{Area}-{Unit}-{Function}-{Sequence} | ZH-ETH-100-U01-FT-001 | `^[A-Z]{2,4}-[A-Z]{2,4}-\d{2,3}-U\d{2}-[A-Z]{1,4}-\d{3}[A-Z]?$` |
| 装置-单元 | {Plant}-{Unit}-{Function}-{Sequence} | ETH-U01-FT-001 | `^[A-Z]{2,4}-U\d{2}-[A-Z]{1,4}-\d{3}[A-Z]?$` |
| 区域-单元 | {Area}-{Unit}-{Function}-{Sequence} | 100-U01-FT-001 | `^\d{2,3}-U\d{2}-[A-Z]{1,4}-\d{3}[A-Z]?$` |
| 简化 | {Function}-{Sequence} | FT-101 | `^[A-Z]{1,4}-\d{3}[A-Z]?$` |
| 电缆 | IC-{Function}-{Sequence}-{Core} | IC-FT-101-01 | `^IC-[A-Z]{1,4}-\d{3}-\d{2}$` |
| 接线箱 | JB-{Area}-{Sequence} | JB-100-01 | `^JB-\d{2,3}-\d{2}$` |

#### 15.5.5 命名规则验证流程

1. 用户输入位号 → 2. 根据 entity_type 查找规则（按 priority 排序，优先 `is_default=True`）→ 3. 正则验证格式并用命名捕获组提取各段值 → 4. 层级一致性验证（plant/area/unit 段与当前选择的层级一致）→ 5. 唯一性验证（位号在 Unit 内唯一）→ 6. 返回结果（成功返回解析后的各段；失败返回 `validation_message` 与期望模式）。

#### 15.5.6 自动生成位号

流程：①用户选择 Unit（自动获取 Site/Plant/Area/Unit 代码）→ ②选择仪表类型（获取 Function 代码）→ ③系统计算下一个 Sequence 号 → ④组合生成完整位号。

```
POST /api/v1/tags/generate-number/
Request:  {"unit_id":"uuid", "instrument_type_id":"uuid", "naming_convention_id":"uuid"(可选)}
Response: {"generated_number":"ETH-100-U01-FT-004",
           "segments":{"plant":"ETH","area":"100","unit":"U01","function":"FT","sequence":"004"},
           "next_sequence":5}
```

### 15.6 系统管理其他功能需求

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| ADM-01 | 用户和用户组管理：基于 §15.2 的 RBAC。权限控制粒度：模块级 + 操作级(C/R/U/D) + 数据级(项目组成员关系决定可见项目)。 | Django Groups/Role + 对象级权限（项目组成员校验）。DRF `permission_classes` 按角色 + 项目组检查。 |
| ADM-02 | 工厂层级管理：见 §15.4，按 ProjectTenant → Client → Site → Plant → PlantHierarchy(MPTT)，数据唯一性在 Unit 级别检查。 | MPTT 管理树形结构 + TreeView 管理界面。 |
| ADM-03 | 工程项目(ProjectTenant)管理：见 §15.1、§15.4。租户隔离单元为 ProjectTenant（独立 Schema）。 | django-tenants + `project_settings` 功能开关。 |
| ADM-04 | 命名规范配置：见 §15.5，分别为 Tag/Loop/Cable/JunctionBox/TerminalStrip 配置独立命名规范。 | NamingConvention 模型 + 段定义 JSON + 验证/生成引擎。 |
| ADM-05 | 支撑表(Supporting Tables)管理：InstrumentLocation/Manufacturer/Model/WireColor/WireType/CableType/AreaClassification/ProcessFunction/LoopFunction/LoopProc 等。每个支撑表统一 CRUD，租户内共享，含 ID=0 初始行。**【V2.1 增强·IS模板】新增支撑表**：`ResponsibleParty`（采购/安装责任方：Instrument Engineer、Electrical Engineer、Mechanical Engineer、E&I Installation Contractor、Mech Installation Contractor、System Integrator、MCC Manufacturer、Package Plant-〈名称〉、Existing、N/A…，含 `party_type: Discipline/Contractor/Package/Other`）；`PhysicalLocation`（Building/Floor/Room 三级，与 PlantHierarchy 正交）；`SignalConnectionType`（HW/PB/FF/MB/HT/ET/ASi/PA/RS232/RS485，含 `is_fieldbus` 标记）；`DigitalSignalType`（VFC/24VDC/Namur/Optoisolator）；`InsulationCode`（LC/HC/PP…）；`HeatTracingCode`（Electric/Steam/None）；`AlarmPriority`（Priority 1: RED … Priority 5: CYN，EEMUA 191 风格，为报警管理预留）。`AreaClassification` 种子扩充为 IS 模板 15 项（Safe、Zone 1/2 × IIA/IIB/IIC、含 T 级与 Ex i/Ex d 变体）。 | 通用 `SupportingTableViewSet`（GenericViewSet），URL 参数 `table_name` 路由。数据迁移预置 ID=0 行；IS 模板下拉列表转为 fixtures。 |
| ADM-06 | 系统参数设置(Preferences)：全局设置（默认计量单位制、日期格式、报告默认语言、并发编辑策略）与用户设置（默认模块、AG Grid 分页大小、通知偏好）。 | SystemSettings 模型(key, value, scope) + user_preferences 表。 |
| ADM-07 | 审计日志(Audit Trail)：记录 user_id/action(CREATE/UPDATE/DELETE)/model_name/object_id/changed_fields/timestamp/ip_address。审计日志存储于 **public Schema**，使用独立数据库连接，记录后不可 UPDATE/DELETE。仅 Administrator 可读。保留策略默认 365 天。 | django-auditlog 或自定义 AuditLog 中间件 + 独立数据库路由(DATABASE_ROUTERS)。 |
| ADM-08 | 数据备份与恢复：手动/定时全库备份(pg_dump)、备份历史、从备份恢复（需 Administrator + 二次确认）。备份前自动运行 DBI 完整性检查。RPO ≤ 24 小时，RTO ≤ 4 小时。 | Django management command + Celery 定时任务 + pg_dump/pg_restore 封装 + backup_history 表。 |

### 15.7 系统管理 API 端点

```
# 角色管理 (Administrator only)
GET/POST          /api/v1/roles/                        # 角色列表/创建
GET/PUT/DELETE    /api/v1/roles/{id}/                   # 角色详情/更新/删除

# 用户管理 (Administrator only)
GET/POST          /api/v1/users/                        # 用户列表/创建
GET/PUT/DELETE    /api/v1/users/{id}/                   # 用户详情/更新/删除
POST              /api/v1/users/{id}/activate/          # 激活用户
POST              /api/v1/users/{id}/deactivate/        # 停用用户
POST              /api/v1/users/{id}/reset-password/    # 重置密码

# 项目组管理
GET/POST          /api/v1/task-forces/                  # 项目组列表/创建
GET/PUT/DELETE    /api/v1/task-forces/{id}/             # 项目组详情/更新/删除
POST              /api/v1/task-forces/{id}/assign-project/  # 分配工程项目 (Admin only)
GET/POST          /api/v1/task-forces/{id}/members/         # 成员列表/添加成员
DELETE            /api/v1/task-forces/{id}/members/{user_id}/  # 移除成员

# 当前用户
GET               /api/v1/me/                           # 当前用户信息
GET               /api/v1/me/task-forces/               # 我的项目组列表
PUT               /api/v1/me/preferences/               # 更新偏好设置

# 命名规则
GET/POST          /api/v1/naming-conventions/           # 列表/创建
GET/PUT/DELETE    /api/v1/naming-conventions/{id}/      # 详情/更新/删除
POST              /api/v1/naming-conventions/{id}/set-default/  # 设为默认
POST              /api/v1/naming-conventions/{id}/validate/     # 验证测试
GET               /api/v1/naming-conventions/templates/         # 预设模板列表
POST              /api/v1/naming-conventions/from-template/     # 从模板创建
POST              /api/v1/tags/validate-number/         # 验证位号格式
POST              /api/v1/tags/generate-number/         # 自动生成位号
POST              /api/v1/tags/parse-number/            # 解析位号各段
```

---

### 15.8 数据模型定制 (Schema Customization / UDF·UDT) 【决策 D10 · 通用性与定制性基座】

**目标**：管理员无需开发介入即可**扩展与定制各数据模型的表结构**——为任意 Item Type 追加字段、创建自定义表、调整系统字段的呈现与校验——使软件适应不同业主/设计院的数据标准。此能力对标 SPI 的 UDF/UDT 与 Custom Fields，并进一步覆盖系统字段属性覆盖与全链路生效。

**定制边界（工程诚实声明）**：
- 定制以**元数据驱动**实现（字段注册表 + JSONB `custom_data` + 自定义表通用行存储），**不对核心表执行 DDL**，因而无需迁移、可按租户独立、可随项目模板复制。
- **系统字段**（如 `cmpnt_name`、`unit_id`、`loop_id`、`signal`、`row_version`）可改显示标签、可见性、必填性、默认值、校验与分组，但**不可删除、不可改类型**——信号传播、计算引擎、命名校验等算法依赖其存在与类型。
- 自定义字段可参与：表单、网格、EDE 查询/过滤/排序/分组、导入/导出、报告与交付物模板占位符、REST API（`custom_data.<key>`）、规则引擎（RULE）条件、浏览器视图列、完整度计算（IDX-17，若标 required）。
- 自定义表（UDT）可与任意 Item Type 建立一对多/多对多关联，但不可成为核心算法的输入（例如不能替代 Terminal 参与接线图）。

#### 15.8.1 数据模型

**CustomFieldDefinition（自定义字段定义 — 正式化 `custom_field_definitions`）**

| 字段 | 数据类型与约束 | 说明 |
|------|---------------|------|
| id | BigAutoField, PK | |
| item_type | CharField(max=50) | 目标 Item Type（`ItemTypeRegistry` 注册的任意类型：Component/Loop/Line/Apparatus/Cable/Wire/Panel/PanelStrip/Terminal/Drawing/SpecSheet/ProcessDataCase/SIF/PipingClass/HookUp/… 及 CustomTable） |
| key | SlugField(max=60) | 字段键，`(item_type, key)` 唯一；正则 `^[a-z][a-z0-9_]{1,59}$`；不得与系统字段名冲突 |
| label / label_i18n | CharField(max=100) / JSONField | 显示标签（多语言，§6.2） |
| data_type | CharField, choices | STRING / TEXT / INTEGER / DECIMAL / BOOLEAN / DATE / DATETIME / ENUM / MULTI_ENUM / UOM_VALUE（数值+单位）/ REFERENCE（FK 到 Item Type 或 CustomTable）/ FILE / URL / JSON |
| enum_list_id | ForeignKey → CustomEnumList, nullable | ENUM/MULTI_ENUM 取值列表 |
| reference_target | CharField(max=50), nullable | REFERENCE 目标 Item Type / CustomTable code |
| uom_category | CharField(max=30), nullable | UOM_VALUE 的单位类别 |
| validation | JSONField | `{min, max, min_length, max_length, regex, decimal_places, required_when: <filter_ast>}` |
| default_value | JSONField, nullable | |
| is_required | BooleanField, default=False | 计入 IDX-17 完整度 |
| is_unique | BooleanField, default=False | 租户内唯一（以 GIN 表达式索引实现） |
| is_searchable / is_filterable / is_sortable | BooleanField | 控制 EDE/网格能力（sortable 需建表达式索引） |
| group / display_order | CharField(max=50) / IntegerField | 表单分组与顺序 |
| visibility | JSONField | `{roles: [...], hidden_when: <filter_ast>}` 按角色/条件可见 |
| help_text | TextField, nullable | |
| scope | CharField, choices | PROJECT（本租户）/ ORGANIZATION_TEMPLATE（组织级模板，复制到新项目） |
| status | CharField, choices | Active / Deprecated（隐藏但保留数据）/ Archived |
| schema_version | IntegerField | 每次定义变更递增（§4.1.11） |
| created_at/by, updated_at/by, row_version | | 按 §4.1.1 |

**CustomTable（自定义表 UDT）与 CustomTableRow**

| 字段 | 说明 |
|------|------|
| CustomTable.code / name / description | 表代码（`^[a-z][a-z0-9_]{1,40}$`，租户内唯一）/ 名称 / 描述 |
| CustomTable.parent_item_type | nullable：设为某 Item Type 时为**子表**（一对多，如 Component 的"校验记录"表）；为空时为**独立主表**（如"供应商合格名录"） |
| CustomTable.key_field_key | 作为业务主键显示的字段键 |
| CustomTable.fields | 通过 `CustomFieldDefinition(item_type='custom:<code>')` 定义列 |
| CustomTable.allow_import / allow_export / allow_ede | 是否开放导入导出与 EDE |
| CustomTableRow.table_id / parent_object_id / data(JSONB) / row_version / audit 字段 | 通用行存储；`parent_object_id` 指向父 Item Type 记录（子表时必填） |

**FieldConfigOverride（系统字段属性覆盖）**

| 字段 | 说明 |
|------|------|
| item_type / field_name | 目标系统字段（须在 `ItemTypeRegistry` 的系统字段清单中） |
| label_override / label_i18n | 改显示名（如把 `cmpnt_serv` 显示为"Service / Loop Description"） |
| is_hidden / is_required_override / default_value_override | 隐藏、加必填、改默认值（不可放宽系统级 NOT NULL） |
| validation_extra | 追加校验（不能放宽系统校验） |
| group_override / display_order_override | 表单分组/顺序 |
| enum_restriction | 对系统枚举字段限制可选子集 |
| scope / schema_version | 同上 |

**CustomEnumList / CustomEnumValue**：管理员维护的取值列表（`code, label_i18n, color, display_order, is_active`），供 ENUM 字段与 `enum_restriction` 引用；与 ADM-05 支撑表的区别：支撑表是系统预定义结构，枚举列表是纯定制。

**SchemaChangeLog**：记录每次定义变更 `{who, when, item_type, change_type(ADD/MODIFY/DEPRECATE/ARCHIVE/RESTORE), before, after, impact_summary, schema_version}`，不可篡改（同 AuditLog 策略）。

#### 15.8.2 功能需求

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| **ADM-09** | **字段定制器**：Administrator / Project Engineer 在"数据模型定制"页选择 Item Type，查看系统字段（只读结构 + 可覆盖属性）与自定义字段并列的字段清单；拖拽排序与分组；新增自定义字段向导（类型 → 校验 → 可见性 → 预览表单）；变更即时生效（无部署/迁移）。 | React 字段设计器 + `ItemTypeRegistry` 内省 + CustomFieldDefinition CRUD。 |
| **ADM-10** | **自定义表（UDT）**：创建独立主表或某 Item Type 的子表；定义列（复用 ADM-09）；自动获得：通用网格 CRUD 页、EDE 可查询、导入/导出（模块8）、报告占位符（§6.6）、API `/api/v1/custom-tables/{code}/rows/`；子表在父对象详情页以页签呈现。 | 通用 `CustomTableRowViewSet` + 动态 Serializer（按定义生成）。 |
| **ADM-11** | **系统字段属性覆盖**：对系统字段修改标签（多语言）、隐藏、加必填、默认值、追加校验、分组与顺序、限制枚举子集；不可删除或改类型（UI 灰显并提示原因）。覆盖对表单、网格、EDE、导入模板、报告标签**全链路生效**。 | FieldConfigOverride + 字段元数据 API 合并输出。 |
| **ADM-12** | **统一字段元数据服务**：`GET /api/v1/schema/{item_type}/` 返回**合并后**的字段 schema（系统字段 + 覆盖 + 自定义字段），含类型/校验/枚举/可见性/分组/i18n 标签；前端所有动态表单、AG Grid 列定义、EDE-03 属性资源管理器、模块8 字段映射、§6.6 模板占位符校验**均以此为唯一来源**（EDE 原 `field-metadata` 端点成为其别名）。OpenAPI 在 `custom_data` 属性上以 `x-custom-fields` 扩展描述当前租户的自定义字段。 | `SchemaService` 带缓存（按 schema_version 失效）；drf-spectacular 扩展钩子。 |
| **ADM-13** | **变更治理**：(a) 修改/弃用字段前显示**影响分析**（引用该字段的浏览器视图、EDE 查询、Import Link 映射、规则、模板占位符、报告数量）；(b) 删除策略：只允许 Deprecate（隐藏、保留数据）→ 90 天后可 Archive（数据快照进 FileAsset 后清除）；(c) 类型变更仅允许**安全放宽**（INTEGER→DECIMAL、STRING 加长），其余需新建字段并提供批量迁移向导；(d) `scope=ORGANIZATION_TEMPLATE` 的定义在创建 ProjectTenant 时复制进租户（§15.4.6 层级模板同机制），项目内可再改；(e) 所有变更写 SchemaChangeLog 并递增 `schema_version`。 | 影响分析走各注册表的反向引用查询；Archive 走 Celery。 |
| **ADM-14** | **导入/导出定制定义**：字段定义、自定义表定义、覆盖、枚举列表可整体导出为 `schema_customization.json`（含 schema_version）并导入其他项目/组织模板，冲突策略 skip/overwrite/rename。 | JSON 导出/导入 + Dry Run。 |

#### 15.8.3 存储与性能约束

- `custom_data` JSONB 使用 GIN 索引（§4.1.7）；`is_sortable/is_unique/is_filterable` 字段自动建表达式索引 `((custom_data->>'key'))`，每 Item Type 上限 20 个索引字段（超限需 Administrator 确认）。
- 每 Item Type 自定义字段上限 200；CustomTable 上限 50 张/租户，单表 100 列；超限为软限制，可由 Administrator 调整 `project_settings`。
- 校验在 Service 层按合并 schema 执行（§4.1.5），API 拒绝未定义键。
- 字段元数据缓存以 `(tenant, item_type, schema_version)` 为键，变更后即时失效。
- **Schema 归属**：`scope=PROJECT` 的定义、覆盖、枚举与全部 `CustomTable/CustomTableRow` 位于**租户 schema**（随项目隔离）；`scope=ORGANIZATION_TEMPLATE` 的定义位于 **public schema**（`apps/administration`），创建 ProjectTenant 时复制进租户。

#### 15.8.4 API 端点

```
# 数据模型定制 (Administrator / Project Engineer)
GET               /api/v1/schema/{item_type}/                       # 合并后的字段 schema（ADM-12，唯一来源）
GET/POST          /api/v1/schema/custom-fields/                     # 自定义字段定义
GET/PUT/PATCH     /api/v1/schema/custom-fields/{id}/
POST              /api/v1/schema/custom-fields/{id}/deprecate/      # 弃用（ADM-13）
POST              /api/v1/schema/custom-fields/{id}/archive/
GET               /api/v1/schema/custom-fields/{id}/impact/         # 影响分析
GET/POST          /api/v1/schema/field-overrides/                   # 系统字段属性覆盖
GET/PUT/DELETE    /api/v1/schema/field-overrides/{id}/
GET/POST          /api/v1/schema/enum-lists/ 、/{id}/values/         # 枚举列表
GET/POST          /api/v1/custom-tables/                            # 自定义表定义
GET/PUT/PATCH     /api/v1/custom-tables/{code}/
GET/POST          /api/v1/custom-tables/{code}/rows/                # 通用行 CRUD
GET/PUT/PATCH/DELETE /api/v1/custom-tables/{code}/rows/{row_id}/
GET               /api/v1/schema/change-log/                        # SchemaChangeLog
POST              /api/v1/schema/export/ 、/import/                  # ADM-14
```

---

# 第四部分：全局工程实施契约 【V2.1 新增】

> 本部分为 V2.1 审查报告中识别的全局性补充内容，为 AI IDE 编码提供明确的工程实施约束，消除自由发挥空间。

---

## 4.1 全局数据模型契约

### 4.1.1 业务表必备字段

所有业务表必须包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| 主键 (id) | BigAutoField | 自增主键 |
| unit_id（可推导时） | ForeignKey → Unit | 工厂单元标识（租户 schema 内的 PlantHierarchy unit） |
| created_at | DateTimeField(auto_now_add) | 创建时间 |
| created_by | ForeignKey → User | 创建人 |
| updated_at | DateTimeField(auto_now) | 更新时间 |
| updated_by | ForeignKey → User | 更新人 |
| row_version | IntegerField(default=1) | 乐观锁版本号 |
| is_deleted | BooleanField(default=False) | 软删除标记 |

> **【V2.1 更新】关于租户判别列**：本系统采用 Schema 隔离（§4.1.4），**租户 schema 的业务表不含 `domain_id`，也不应添加 `project_id`**——租户归属由所在 schema 决定。仅 **public schema 的跨项目模型**（如 `AuditLog`、`GlobalRevision`、`ProjectTaskForce`、`FileAsset`）才需 `project_id`（FK → ProjectTenant，标明所属项目）或 `organization_id`。

### 4.1.2 删除策略

- 默认软删除（`is_deleted=True`）。
- 被支撑表或历史修订引用的数据禁止硬删除。

### 4.1.3 乐观锁

- `row_version` 每次更新自增。
- PATCH/批量更新必须提交 `expected_row_version`；不匹配返回 `409 CONFLICT`。

### 4.1.4 租户隔离 【V2.1 更新，与 SPECIFICATION.md 对齐】

> **架构口径更新**：原 V2.1 此处描述的"单库共享 schema + domain_id"方案，已依据 `SPECIFICATION.md` 调整为 **PostgreSQL Schema 隔离**（django-tenants），以模块15（§15.1）为权威定义。

- 租户单位为 **ProjectTenant（工程项目）**，每个项目拥有独立的 PostgreSQL Schema（`project_xxx`）。
- 租户切换通过 **HTTP Header `X-Project-ID` + `TenantContextMiddleware`** 完成（`SET search_path TO "project_xxx", public`），不使用 Host/子域路由。
- 共享数据（Organization/User/Role/ProjectTenant/TaskForce/TaskForceMembership/AuditLog）位于 **public Schema**；项目/工程/配置数据（Client/Site/Plant/PlantHierarchy/Loop/Tag/InstrumentType/NamingConvention）位于 **租户 Schema**。
- 租户 Schema 内的业务表不再需要 `domain_id` 过滤字段（由 Schema 边界天然隔离）；位于 public 的跨项目模型按需以 `project_id`/`organization_id` 关联。
- 项目可见性受 §15.3.3 强约束：未加入任何 ProjectTaskForce 的普通用户不可见任何项目；非法 `X-Project-ID` 返回 403 并重置连接至 public。

### 4.1.5 JSONB 字段约束

- JSONB 字段必须由 schema 表驱动，禁止写入未定义键。
- `custom_data` 根据 `custom_field_definitions` 校验类型、必填、枚举值和长度。

### 4.1.6 关键唯一约束

> 唯一约束在**租户 schema 内**生效，无需包含 domain_id（schema 即隔离边界）。

- Tag Number 在 `(unit_id, cmpnt_name)` 唯一（租户 schema 内）。
- Loop Number 在 `(unit_id, loop_name)` 唯一（租户 schema 内）。
- Cable Name、Panel Name、Drawing Number 在租户 schema 内按配置唯一。

### 4.1.7 常用索引

- `unit_id`, `name/code` 字段, 外键字段, `status`, `updated_at`（租户 schema 表）；public 跨项目模型额外索引 `project_id`。
- JSONB `custom_data` 使用 GIN 索引。

### 4.1.8 基础抽象类

> **【V2.1 更新】** Schema 隔离下取消 `DomainScopedModel`/`DomainScopedManager`（不再需要按列过滤租户）；`UnitScopedModel` 仅保留对 PlantHierarchy unit 的真实外键。

| 抽象类 | 职责 |
|--------|------|
| TenantBaseModel | 租户 schema 业务表基类，组合 AuditedModel + SoftDeleteModel + VersionedModel（不含租户判别列） |
| UnitScopedModel | 继承 TenantBaseModel，增加 unit_id（FK → PlantHierarchy unit） |
| AuditedModel | 提供 created_at/created_by/updated_at/updated_by |
| SoftDeleteModel | 提供 is_deleted 字段和 SoftDeleteManager |
| VersionedModel | 提供 row_version 字段和乐观锁校验 |
| ProjectScopedModel | public schema 跨项目模型基类，提供 project_id（FK → ProjectTenant） |

### 4.1.9 外键命名

- 数据库字段保留 SPI 风格名称时，在 Django 中使用清晰 `related_name`。
- API 输出同时提供 `id` 与 `display` 字段。

### 4.1.10 枚举

- 所有枚举使用 Django `TextChoices / IntegerChoices`，并生成前端 TypeScript union。

### 4.1.11 JSONB 字段版本

- `custom_data`, `view_config`, `mapping_config`, `template_json` 等必须有 `schema_version`。

### 4.1.12 迁移顺序

> Schema 隔离下分两类迁移：先迁 public（SHARED_APPS），再为每个 ProjectTenant 迁租户 schema（TENANT_APPS）。命令见 §4.10（`migrate_schemas --shared` / `--tenant`）。

```
# public schema (SHARED_APPS)
tenants → administration(RBAC/TaskForce/命名规范/支撑表) → audit → core
# 租户 schema (TENANT_APPS, 每个项目独立)
core_engineering(Client/Site/Plant/PlantHierarchy)
  → IDX → PD → CALC → SPEC
  → WIR → DDP/HU/LOOP
  → DOC → IFC/INT/RULE/DBI/EDE → revisions/concurrency
```

### 4.1.13 审计

- 所有 CREATE/UPDATE/DELETE 写入 `AuditLog`；批量操作记录 `batch_id`。

### 4.1.14 文件存储

- 生成文件存储 `FileAsset` 表，字段含 `file_id, project_id, storage_path, mime_type, sha256, created_by, expires_at`（FileAsset 位于 public schema，以 project_id 关联项目）。
- 所有业务写操作必须通过 Service 层；ViewSet 不直接承载复杂业务规则。

### 4.1.15 工程种子文件清单 【V2.1 新增 — 实施索引】

| 种子文件 | 路径 | 内容 | 来源 | 决策 |
|---------|------|------|------|------|
| `technology_types.json` | `backend/apps/instruments/fixtures/` | **312** 条技术类型（291 原 + 21 自 WSP 模板库补入）；含 `default_io_profile` 与 26 键 `process_data_applicability` | Instrument Schedule 类型主表 + WSP Datasheet 模板库 | D9 / D14 |
| `process_data_field_catalog.json` | `backend/apps/process_data/fixtures/` | 26 个过程数据字段（结构 MNM/MM/LH/S、UOM 类别、design/operating 分类） | Instrument Schedule | D9 |
| `spec_field_catalog.json` | `backend/apps/specifications/fixtures/` | **593** 个规格书字段（分区、结构、单位提示、占位态分布、label 变体、使用该字段的技术类型清单） | WSP Datasheet 模板库全量提取 | D14 |
| `wsp_template_bindings.json` | `backend/apps/deliverables/fixtures/` | **71** 份模板的单元格级绑定清单（表头 13 单元格、修订块 6 列、逐字段 label/value 坐标、DOCUMENTATION/ACCESSORIES/NOTES 文本、MASTER VER. 历史） | 同上 | D14 |
| `WSP_TEMPLATE_AUDIT.md` | `docs/seeds/` | 模板库一致性与卫生审计（38 处措辞不一致、单位冲突、拼写错误、残留工作表、类型码对账） | 同上 | D14 |
| `technology_types_REVIEW.md` | `docs/seeds/` | `needs_review=true` 条目清单（现 **152** 条）与原因 | — | D9 / D14 |

加载统一经 `python manage.py load_engineering_seeds --tenant <schema>`（§2.1.1.1）。

---

## 4.2 API 契约

### 4.2.1 统一 API 约定

| 项目 | 规定 |
|------|------|
| Base URL | `/api/v1` |
| 认证 | `Authorization: Bearer <access_token>` |
| 分页 | `?page=1&page_size=50`，默认 50，最大 500 |
| 排序 | `?ordering=field,-other_field` |
| 简单过滤 | `?field__operator=value`，operator 取 `exact/contains/startswith/in/gt/gte/lt/lte/isnull` |
| 复杂过滤 | POST `body.filter_ast`，使用 AND/OR 递归树 |

### 4.2.2 错误响应格式

```json
{
  "error": {
    "code": "IDX_TAG_DUPLICATE",
    "message": "Tag number already exists in this unit",
    "field": "cmpnt_name",
    "details": {},
    "trace_id": "abc-123-def"
  }
}
```

### 4.2.3 批量写入

- 批量写入必须在单个 database transaction 中执行。
- 任一行失败则回滚；响应包含 `row_errors`。

### 4.2.4 异步任务

- 异步任务返回 `202 + {task_id, status, websocket_url, poll_url}`。
- 任务状态：`PENDING / RUNNING / SUCCESS / FAILED / CANCELLED`。

### 4.2.5 示例：创建仪表标签

**请求：**
```
POST /api/v1/instruments/
{
  "unit_id": 10,
  "tag_segments": {"unit":"101", "function":"FT", "sequence":"100"},
  "cmpnt_func_type_id": 3,
  "loop_id": 20,
  "line_id": 30,
  "cmpnt_serv": "Feed flow transmitter",
  "io_type": "AI",
  "custom_data": {"criticality":"A"}
}
```

**响应：**
```
201 Created
{
  "cmpnt_id": 501,
  "cmpnt_name": "101-FT-100",
  "status": "Draft",
  "auto_created": {"spec_id": 7001, "device_panel_id": 9001, "device_cable_id": 9101}
}
```

### 4.2.6 错误码前缀

| 前缀 | 用途 | 示例 |
|------|------|------|
| AUTH_* | 认证和授权错误 | AUTH_PERMISSION_DENIED, AUTH_TOKEN_EXPIRED |
| IDX_* | 仪表索引错误 | IDX_TAG_DUPLICATE, IDX_INVALID_NAMING_SEGMENT |
| PD_* | 过程数据错误 | PD_CASE_APPROVED_READONLY, PD_UOM_INCOMPATIBLE |
| CALC_* | 计算错误 | CALC_INPUT_OUT_OF_RANGE, CALC_NO_CONVERGENCE |
| SPEC_* | 规格书错误 | SPEC_TEMPLATE_FIELD_MISSING, SPEC_REVISION_LOCKED |
| WIR_* | 接线错误 | WIR_TERMINAL_OCCUPIED, WIR_SIGNAL_CONFLICT |
| IFC_* | 导入/集成错误 | IFC_MAPPING_INVALID, IFC_MERGE_CONFLICT_UNRESOLVED |
| DBI_* | 完整性检查错误 | DBI_FIX_REQUIRES_BACKUP_CONFIRMATION |

---

## 4.3 权限矩阵

> **【V2.1 更新】角色体系以模块15（§15.2）为权威定义**：系统正式角色为 Administrator(L5) / Project Manager(L4) / Project Engineer(L4) / Instrumentation Engineer(L3) / Process Engineer(L3) / Mechanical Engineer(L3) / Guest(L1)，数据级权限矩阵见 §15.2.4。下表为各业务模块的操作级权限映射（角色名已对齐 §15.2）：

| 模块 | 操作 | Administrator | PM / Project Engineer | Instrumentation Eng | Process Eng | Mechanical Eng | Guest |
|------|------|---------------|----------------------|---------------------|-------------|----------------|-------|
| ADM 系统管理 | CRUD | 全部 | 仅自建项目组(CR*) | 无 | 无 | 无 | 只读个人设置 |
| IDX 仪表索引 | CRUD | 全部 | 所属项目内CRUD | 所属项目内CRUD | 只读 | 只读 | 只读 |
| PD 过程数据 | CRUD/Approve | 全部 | CRUD | 只读/确认 | CRUD/提交审核 | 只读 | 只读 |
| CALC 计算 | 执行/保存 | 全部 | 执行/保存 | 执行/保存 | 执行 | 执行 | 只读结果 |
| SPEC 规格书 | CRUD/Revision | 全部 | CRUD/修订 | CRUD/修订 | 只读过程字段 | 只读 | 只读 |
| SPEC 发版（§4.4.11 Issue Purpose，D14） | 推进版次用途 | 全部 | **全部用途**（含 FOR_PURCHASE / FOR_CONSTRUCTION / AS_BUILT，须审批人身份） | FOR_COMMENT / FOR_ENQUIRY / FOR_QUOTATION | 无 | 无 | 只读 |
| SPEC 回标录入（SPEC-14，D14） | 录入 vendor_value / compliance | 全部 | CRUD | CRU | 无 | 无 | 只读 |
| WIR 接线 | CRUD/Assign | 全部 | CRUD/I/O分配 | CRUD/I/O分配 | 无 | 无 | 只读 |
| DOC 文档 | Package/Revise/Publish | 全部 | 发布/修订 | 生成/修订工程文档 | 只读相关文档 | 只读 | 只读 |
| DDP 尺寸/管道 | CRUD | 全部 | CRUD | CRUD | 只读 | CRUD(管道/PipingClass) | 只读 |
| SIF 安全仪表功能（§2.4，D8） | CRUD/Approve | 全部 | CRUD + 批准 | CRUD（提交审批） | CRU（sil_target、hazard_ref、process_safety_time 等风险目标字段） | 只读 | 只读 |
| Procurement 采购/成本（§2.5，D7） | CRUD | 全部 | CRUD + 状态推进 | CRU（状态至 Quoted；成本字段只读） | 只读 | 只读 | 只读（成本列按项目配置可隐藏） |
| 数据模型定制（§15.8，D10） | 定义/覆盖/UDT | 全部（含组织级模板） | 项目级 CRUD（不含组织级） | 只读 schema | 只读 schema | 只读 schema | 无 |
| 交付物模板库（§6.6，D12） | 模板管理/生成 | 全部 | 项目级模板 CRUD/发布/设默认 + 生成 | 项目级 Draft 模板 CRU + 生成 | 生成 | 生成 | 生成（只读模板） |
| IFC/INT 集成 | 配置/执行 | 全部 | 配置并执行 | 执行已授权Link | 导入过程数据 | 无 | 无 |
| RULE/DBI | 规则/检查/修复 | 全部 | 规则配置/检查 | 仅查看结果 | 仅查看结果 | 无 | 无 |

> 项目级访问受 §15.3.3「项目可见性强约束」前置控制：非 Administrator 用户须先加入对应 ProjectTaskForce 方可进入任何工程项目；本规则先于上表的 RBAC 检查执行。

---

## 4.4 状态机定义

### 4.4.1 ProcessDataCase 状态机

| 状态 | 允许转换 |
|------|---------|
| Draft | → ReadyForReview |
| ReadyForReview | → Approved, → Rejected |
| Approved | 修改时创建新版本（原版本 → Superseded） |
| Rejected | → Draft（退回修改） |
| Superseded | 终态，不可转换 |

### 4.4.2 SpecSheet 状态机

| 状态 | 允许转换 |
|------|---------|
| Draft | → IssuedForReview |
| IssuedForReview | → IssuedForDesign |
| IssuedForDesign | → AsBuilt |
| 任意已发布版本 | → Obsolete |

> **【V2.1 · D14】** 本状态机为**内部评审口径**。对外交付的版次用途（For Enquiry / For Purchase / For Construction / As-Built）由 §4.4.11 `DocumentIssue.issue_purpose` 承载，二者映射见 §4.4.11 联动表。实施时以 issue_purpose 为发版驱动，本状态机随之同步。

### 4.4.3 Revision 状态机

| 状态 | 允许转换 |
|------|---------|
| Working | → Published, → Cancelled |
| Published | → Superseded |

### 4.4.4 CSTag 状态机

| 状态 | 允许转换 |
|------|---------|
| Uncoupled | → Coupled |
| Coupled | → Assigned, → Uncoupled |
| Assigned | → Coupled（取消分配） |

### 4.4.5 ImportSession 状态机

| 状态 | 允许转换 |
|------|---------|
| Draft | → Validating |
| Validating | → ReadyToImport |
| ReadyToImport | → Importing |
| Importing | → Completed, → Failed |
| Completed | → RolledBack |

### 4.4.6 IntegrityCheck 状态机

| 状态 | 允许转换 |
|------|---------|
| Queued | → Running |
| Running | → Completed / CompletedWithErrors / Failed |

### 4.4.7 PipingClass 状态机 【V2.1 增强·IS模板】

| 状态 | 允许转换 |
|------|---------|
| Draft | → Approved（Mechanical Engineer / PE 审批） |
| Approved | → Superseded（修改时创建新 Draft 版本并在其 Approved 后自动置旧版 Superseded） |
| Superseded | 终态；仍可被历史 Line 引用与查询，不可被新 Line 选用 |

### 4.4.8 SafetyInstrumentedFunction 状态机 【决策 D8】

| 状态 | 允许转换 |
|------|---------|
| Draft | → Approved（Instrumentation Engineer 提交，PE/PM 批准；批准前校验：sil_target 非空、至少 1 个 SENSOR 与 1 个 FINAL_ELEMENT 元件、PFDavg/RRF 或 PFH 非空） |
| Approved | → Superseded（修改时创建新 Draft 版本，其 Approved 后旧版自动 Superseded） |
| Superseded | 终态；保留历史，元件反向关系仍可查询 |

### 4.4.9 ProcurementInfo 采购状态机 【决策 D7】

| 状态 | 允许转换 |
|------|---------|
| NotStarted | → Enquiry, → Cancelled |
| Enquiry | → Quoted, → Cancelled |
| Quoted | → Ordered, → Enquiry（重新询价）, → Cancelled |
| Ordered | → Delivered, → Cancelled（需 PM 权限） |
| Delivered | → Installed |
| Installed | 终态 |
| Cancelled | 终态；成本字段冻结 |

### 4.4.10 ComponentDimensional 尺寸数据状态机 【DDP-06】

| 状态 | 允许转换 |
|------|---------|
| Preliminary | → ForApproval |
| ForApproval | → Approved, → Preliminary（退回） |
| Approved | → Preliminary（修改已批准数据时自动退回并重新审批） |

### 4.4.11 文档版次生命周期 (Issue Purpose) 【决策 D14 · WSP模板】

**问题**：原 §4.4.2 SpecSheet 状态机用 `Draft → IssuedForReview → IssuedForDesign → AsBuilt`，这是**内部评审口径**；而交付给客户/供应商的 datasheet 实际以**版次用途（Issue Purpose）**标识（实测模板修订块 `REVISION` 列全部为 `For Enquiry`）。二者此前无绑定，导致规格书答不出"同一份 datasheet 如何从询价走到订货再到施工"。

**模型**：`DocumentIssue`（适用于 SpecSheetData / Drawing / Package 等任何可发布文档，经 ContentType 通用外键）

| 字段 | 说明 |
|------|------|
| issue_rev | 版次号。两段制：`P01…P0n`（Preliminary，未正式发布）→ `01…0n`（Issued）。方案可配置（沿用 SPEC-09 修订编号方案） |
| issue_purpose | 见下表 |
| issued_by / issued_date | 发布人 / 日期（映射模板 D/H 列） |
| approved_by / approved_date | 审批人 / 日期（映射模板 AD/AH 列） |
| global_revision_id | FK → GlobalRevision（可选，参与项目里程碑版次） |
| snapshot_id | FK → EntityRevision（该版次的数据快照） |
| superseded_by_id | FK → self，被哪一版取代 |

**Issue Purpose 枚举与状态机**：

| issue_purpose | 含义 | 允许转换到 | 前置校验（Service 层强制） |
|---------------|------|-----------|------------------------|
| FOR_COMMENT | 内部/客户评审 | FOR_ENQUIRY, FOR_COMMENT(新版) | 无 |
| FOR_ENQUIRY | **询价**（模板基线用途） | FOR_QUOTATION, FOR_PURCHASE, FOR_ENQUIRY(新版) | 所有 `EMPTY` 字段为零（`VTA/TBA/TBC` 允许存在）；DOCUMENTATION 要求集非空 |
| FOR_QUOTATION | 供应商报价回标后 | FOR_PURCHASE, FOR_ENQUIRY(重新询价) | 已录入至少一家 `vendor_value`（SPEC-14） |
| FOR_PURCHASE | **订货** | FOR_CONSTRUCTION, AS_BUILT | 全部 `VTA` 已被实值或 vendor_value 替代；`TBA` 为零；Manufacturer/Model 非空；关联 `ProcurementInfo.status ∈ {Ordered}` |
| FOR_CONSTRUCTION | **施工** | AS_BUILT | 关联 Hook-Up（模块12）与接线（模块10）数据已存在；`ProcurementInfo.status ∈ {Delivered, Installed}` |
| AS_BUILT | 竣工 | — （终态） | 记录实际到货 Manufacturer/Model/序列号/标定值 |
| FOR_INFORMATION | 仅供参考 | 任意 | 无 |

**与既有状态机的联动**（三者此前相互独立，现以本表绑定）：

| DocumentIssue.issue_purpose | SpecSheet 状态（§4.4.2） | ProcurementInfo 状态（§4.4.9） |
|---|---|---|
| FOR_COMMENT | Draft / IssuedForReview | NotStarted |
| FOR_ENQUIRY | IssuedForReview | Enquiry |
| FOR_QUOTATION | IssuedForReview | Quoted |
| FOR_PURCHASE | IssuedForDesign | Ordered |
| FOR_CONSTRUCTION | IssuedForDesign | Delivered |
| AS_BUILT | AsBuilt | Installed |

**规则**：推进 `issue_purpose` 时，Service 层同步推进另两个状态机（反之不自动推进 issue_purpose——发版是显式动作）；不一致由 DBI 检查项 `DOC_ISSUE_STATE_MISMATCH`（Warning）捕获。

> **注**：Datasheet 本身不是施工文件；施工依据为 Hook-Up 图（模块12）、接线图与电缆/端接表（§6.6）、回路图（模块11）。`FOR_CONSTRUCTION` / `AS_BUILT` 版次的意义是**使 datasheet 随竣工资料归档并反映实际到货设备**，而非替代上述施工图纸。

---

## 4.5 关键算法和公式实现规则

1. **命名校验**：按 `NamingConventionConfig.segments` 顺序拼接；每段先做类型校验、长度校验、必填校验、枚举校验，再做唯一性检查；批量创建在事务内锁定同 Unit 的序号范围。

2. **EDE 查询**：前端只提交 Query DSL，不提交 SQL；后端根据 `ItemTypeRegistry` 和 `RelationshipRegistry` 生成 ORM QuerySet；禁止任意字段名和任意 JOIN。

3. **复杂过滤**：`filter_ast = {op:"AND", children:[condition|group]}`；`condition={field, operator, value, data_type}`；后端递归转换为 Django Q。

4. **信号传播**：将 Terminal/Wire/WireTerminal/CrossWire 视为图；从源端子 BFS；遇到未连接、分叉、已有不同信号且非 force、设备边界规则不允许时停止；记录 `propagation_trace`。

5. **计算引擎**：所有计算函数返回 `{inputs_si, outputs, warnings, standard, formula_version, validation_errors}`；每个公式必须有基准测试向量和容差。

6. **文档生成原则**：规格书/回路图/Hook-Up 图：生成文件不得直接修改图像结果作为事实源；数据库是唯一事实源，文档和 SVG/PDF 均为可再生成产物。

---

### 4.5.1 计算测试向量的来源与权威（【决策 D13】安全关键）

**问题**：WP-07 要求"先交测试向量再写实现"。若测试向量由实现 agent 自行推导，则测试与实现同源，**只能验证自洽、无法验证正确**——对安全阀泄放量、本安参数、SIL 相关计算，这是不可接受的。

**规则**：
1. 测试向量**必须来自外部权威来源**，不得由 agent 自行推导。每条向量必须记录 `source`（标准条款号、教科书例题、厂商选型软件输出、或项目方历史手算记录）与 `source_ref`（页码/例题号/文件名）。
2. 向量文件路径：`backend/apps/calculations/tests/vectors/<engine>.yaml`，格式：
   ```yaml
   - id: CV-LIQ-001
     standard: "ISA-75.01.01-2012"
     source: "ISA-75.01.01 Annex B, Example 1"
     source_ref: "B.2.1"
     inputs: {flow_rate: 100, flow_uom: "m3/h", p1: 5.0, p2: 3.0, pressure_uom: "bar", ...}
     expected: {cv: 52.3, choked: false}
     tolerance_pct: 0.1
   ```
3. **项目方责任**：向量的权威来源由项目方（持证工程师）提供或签署确认；agent 只负责把向量转成文件并实现通过。缺少权威来源的计算项，**该计算项不得标记为完成**，记入 `docs/OPEN_QUESTIONS.md`。
4. 每个计算引擎至少覆盖：正常工况、边界工况（壅塞流/临界流/闪蒸）、单位换算路径、超范围报错、不收敛报错。
5. 实现与向量**分提交**：向量文件先行合入并由项目方 review，实现 PR 不得修改向量文件（如需修改须单独 PR 并说明）。

---

## 4.6 前端页面与路由

| 路由 | 页面 | 最低功能 |
|------|------|---------|
| /admin | 系统管理 | 用户、角色、工程项目(ProjectTenant)、项目组(TaskForce)、工厂层级、命名规范、支撑表、参数、**数据模型定制（§15.8）** |
| /templates | 交付物模板库 | 交付物类型、模板浏览/导入向导/绑定/预览/发布/设默认、生成任务（§6.6） |
| /instruments | 仪表索引 | 标准浏览器、创建/编辑Tag、Loop、批量创建、报告 |
| /process-data | 过程数据 | Line/Instrument数据、Case、单位转换、审批 |
| /specs | 规格书 | 表单编辑、生成、数据录入、修订、比较、导出 |
| /calculations | 计算 | 控制阀、流量计、安全阀、本安、温度套管计算和报告 |
| /wiring | 接线设计 | 面板/端子/电缆、连接窗口、信号传播、I/O分配、现场总线 |
| /loop-drawings | 回路图 | 生成、在线查看、标注、宏、导出 |
| /hookups | Hook-Up | 物料库、Hook-Up分配、BOM、图纸生成 |
| /documents | 文档管理 | Package、Revision、发布、文档检索 |
| /ede | 工程数据编辑器 | 查询构建、视图、批量编辑、复杂过滤 |
| /import-export | 导入/导出 | Link、映射、Dry Run、导入、合并、导出 |
| /rules | 规则引擎 | 规则树、组件、过滤、一致性、GUI控制 |
| /db-integrity | 完整性管理 | 检查、报告、修复、计划 |

### 前端统一要求

- 所有表格支持分页、排序、过滤、列配置保存、导出当前视图。
- 所有编辑表单支持脏状态提示、保存失败错误定位、`row_version` 冲突提示。
- 所有长任务使用统一 `TaskProgressDrawer` 组件。

---

## 4.7 导入/导出与集成补全

| 对象 | 补全要求 |
|------|---------|
| Import Link | `link_name, target_item_type, source_type, mapping_config, validation_rules, duplicate_policy, merge_key, schema_version` |
| Dry Run | 必须输出 `created/updated/skipped/errors/warnings` 计数和逐行错误；不得写数据库 |
| Merger | 冲突类型：`field_conflict, missing_reference, duplicate_key, deleted_target, version_conflict`；每个冲突必须有决策：`use_source / use_target / manual / skip` |
| SPEL Cable Export | 导出字段、编码、文件名、批次号、checksum、导出历史和重试状态必须落库 |
| SP Adapter | 外部对象采用 `ExternalObjectMap` 表维护 `external_system, external_id, local_model, local_id, last_sync_hash` |
| Webhook | HMAC-SHA256 签名、重放窗口 5 分钟、失败指数退避重试、死信队列 |

---

## 4.8 测试数据与验收标准

### 4.8.1 最小种子数据

- **ProjectTenant**: PRJ-DEMO-001（schema `project_prjdemo001`），status=Active【V2.1 更新：租户单位为 ProjectTenant，见 §15.1】
- **Hierarchy**: Client DEMO_OWNER → Site S1 → Plant P1 → Area A101 → Unit U101（PlantHierarchy MPTT，node_type=PLANT/AREA/UNIT）
- **TaskForce**: TF-DEMO（关联 PRJ-DEMO-001），成员含各角色各一名
- **Instrument types（功能类型）**: FE, FT, FV, PT, TT, LT, XV, ZS, AI, AO, DI, DO
- **Technology types（技术类型，IS模板，D9）**: 全量 291 条自 `technology_types.json` 加载（`load_engineering_seeds`），同时加载 `process_data_field_catalog.json` 26 字段（含 default_io_profile 与 process_data_applicability）；E2E 至少覆盖 FET50（Coriolis）、FE10（孔板）、UCV10（调节阀）、KCV20（开关球阀）、LET75（雷达液位）、QET35（点式气体探测）、FS（流量开关）
- **Supporting tables（IS模板新增）**: ResponsibleParty=Instrument Engineer/Mech Installation Contractor/Package Plant-Vessel/System Integrator；PhysicalLocation=Ground Floor/First Floor/Mezzanine Floor；SignalConnectionType=HW/HT/FF/PB/MB；DigitalSignalType=VFC/24VDC/Namur；InsulationCode=LC/HC/PP；HeatTracingCode=Electric/Steam/None；AreaClassification 含 Zone 1 IIB T4
- **PipingClass**: ACE（Acetone, Liquid, SS1, Stainless Steel 1.4404, Approved），供 Line 4-P-1501-11H 引用并派生设计条件
- **SIF（D8）**: SIF-101-01 "高液位关进料"，sil_target=2，LOW_DEMAND，target_rrf=100，sensor_voting=1oo1，元件：101-LT-100(SENSOR, sil_capability=2) / DCS-101 逻辑运算器 / 101-XV-100(FINAL_ELEMENT)，Approved
- **Procurement（D7）**: 101-FT-100 status=Quoted、budget_cost=15000 GBP、cost_source=BudgetaryQuote；101-XV-100 is_long_lead=True、status=Enquiry
- **Process functions**: Flow, Level, Pressure, Temperature, Analyzer, ControlValve, ReliefValve
- **Supporting tables**: Manufacturer=Generic, Model=Default, WireColor=Red/Black/White/Green/Blue, CableType=PairShielded/TriadShielded, UOM=degC/kPa/bar/m3h/kgm3/cP
- **Example Loop**: 101-F-100，Tags: 101-FE-100, 101-FT-100, 101-FV-100
- **Example Line**: 4-P-1501-11H，fluid_state=Liquid
- **Example Wiring**: DevicePanel 101-FT-100 → Cable C-101-FT-100 → JunctionBox JB-101 → Multicore MC-101 → MarshalingRack MR-101 → DCSPanel DCS-101 Channel AI-01
- **Example Spec**: Flow transmitter spec form with one revision A
- **Example Hook-Up**: FLOW INSTR. BELOW RUN-LIQUID with three material items

### 4.8.2 验收场景

| 验收场景 | 通过标准 |
|---------|---------|
| 创建仪表全链路 | 创建 101-FT-100 后自动生成 Profile 指定的规格书、设备面板、设备电缆和过程数据占位记录 |
| 过程数据审批 | ProcessEngineer 提交 ReadyForReview，InstrumentEngineer 确认 Approved；Approved 后普通编辑被拒绝并提示创建新版本 |
| 规格书修订比较 | 同一规格书 A/B 两版比较只列出变化字段，PDF 输出与页面 diff 一致 |
| 接线信号传播 | 从 DevicePanel 接线到 DCS Channel 后，沿途 Wire/Terminal 的 signal 与 signal_level 正确；冲突时停止并生成 WIR_SIGNAL_CONFLICT |
| EDE 批量编辑 | 从 Excel 粘贴 20 行修改，全部合法则一次提交；任一行非法则整体回滚并返回 row_errors |
| 导入 Dry Run | 导入文件含重复 Tag 时 Dry Run 报告 IDX_TAG_DUPLICATE，数据库无写入 |
| 权限验证 | Viewer 访问写接口返回 403；ProcessEngineer 无法修改接线；对象级 Unit 权限生效 |
| 数据模型定制（D10） | PE 为 Component 新增 ENUM 自定义字段 `criticality`（必填）后：Tag 表单/网格/EDE/导入模板/Instrument Schedule 模板占位符**均无需部署即出现**该字段；IDX-17 完整度分母 +1；弃用该字段后影响分析列出引用它的视图与模板 |
| Excel 导入 Instrument Schedule（D11） | 上传项目方现行 138 列 Schedule 表，自动映射置信度 ≥0.9 的列 ≥80%；Dry Run 报告重复 Tag 与未知类型码；执行后 Component/TagIOAllocation(PCS+SIS)/ProcurementInfo 记录数与源表一致；回滚后数据库恢复 |
| 用户模板导入与生成（D12） | 上传业主 A3 SVG 图框与 Excel Cable Schedule 模板，占位符 100% 绑定后发布并设默认；生成 20 张回路图与 1 份电缆清册，标题栏项目号/图号/版次正确，Excel 保留原样式与冻结窗格；同一 GlobalRevision 二次生成产物字节级一致 |
| **WSP Datasheet 全链路（D14）** | 导入 `FET50` 模板（命名区域全损坏，走坐标绑定）→ 为 Tag `101-FT-100` 生成 datasheet：表头 13 字段、过程数据四工况（Norm 1/Norm 2 自两个 Case 映射）、设计 P/T 自 PipingClass 派生、Calculated Cv 自 CalculationRun 带入、DOCUMENTATION 8 项齐全、`VTA` 字段渲染为 `Vendor to Advise (VTA)`；**文档编号产出 `70XXXXXX-WSP-XX-XX-DS-CI-FET50-0001`、文件名含 `Iss P01`**；版次用途 `FOR_ENQUIRY`。随后：录入两家供应商回标 → 生成 BID_TABULATION → 推进至 `FOR_PURCHASE`（校验拒绝仍存 `VTA` 的字段）→ `ProcurementInfo.status` 自动同步为 `Ordered`；Excel 输出保留原样式、嵌入 logo、A4 打印区与合并单元格 |
| **就绪度判定（D14）** | 同一 Tag 含 10 个 `VTA`、3 个 `NA`、2 个 `EMPTY` 字段时：`readiness_for_enquiry` 判为**未就绪**（因 2 个 EMPTY），`NA` 不计入分母；补齐 2 个 EMPTY 后判为就绪；`readiness_for_order` 仍为未就绪（10 个 VTA 未回填） |
| 性能 | 20 万 Tags 下仪表列表分页首屏 ≤ 2 秒；EDE 100 行预览 ≤ 5 秒 |

---

## 4.9 完成定义 (Definition of Done)

1. 数据模型迁移可从空库一次执行成功，并加载 seed 数据。
2. 每个模块至少包含 Model、Serializer、ViewSet/API、Service、权限、审计、单元测试和最小前端页面。
3. OpenAPI 文档可生成并通过 schema 校验；前端 API client 由 OpenAPI 自动生成或类型严格同步。
4. 所有写接口有权限检查、字段校验、事务边界、审计日志、`row_version` 冲突处理。
5. 异步任务有进度、错误、取消和重试策略。
6. 核心验收场景通过 E2E 测试：创建 ProjectTenant（自动建 schema）→ Client/Site/Plant/Unit 层级 → 加入 TaskForce → Tag → Process Data → Calculation → Spec → Wiring → Loop Drawing → Package → Export。
7. 后端 pytest 覆盖率 ≥ 80%，关键服务类覆盖率 ≥ 90%；前端关键页面组件和 API hook 有 Vitest 测试。
8. 20 万 Instrument、5 万 Loop、50 万 Wire 的测试数据下，主要列表首屏响应 ≤ 2 秒，复杂查询预览 ≤ 5 秒。测试数据由 `scripts/gen_perf_data.py` 生成（幂等、可指定规模、生成后跑一次 DBI 全量检查应无 Error）。
9. **可追溯性**：`docs/TRACEABILITY.md` 由脚本生成且无"未开始"项落在已完成 WP 内（§5.6）。
10. **租户隔离**：V6 回归在每个 WP 通过——跨租户读写越权测试必须全部拒绝；`X-Project-ID` 非法值返回 403 并重置连接至 public（§15.3.3）。
11. **计算类 WP 附加**：测试向量文件具备权威 `source`，且实现 PR 未修改向量（§4.5.1）。
12. **模型边界**：本次 PR 新增的模型全部出现在 §5.5 模型清单中；未列入者不得合入。

---

## 4.10 推荐代码目录 【V2.1 更新 — 对齐多租户架构】

> **架构对齐**：依据模块15（§15.1）的 PostgreSQL Schema 隔离（django-tenants），后端 app 必须显式区分 **public schema（SHARED_APPS）** 与 **租户 schema（TENANT_APPS）**，并独立出 `apps/tenants/`。原 `apps/core/` 注释中的 "domain" 旧口径已移除。

```
backend/
  config/                      # settings(含 SHARED_APPS/TENANT_APPS 划分), urls, celery, asgi
                               #   TENANT_MODEL="tenants.ProjectTenant"
                               #   TENANT_DOMAIN_MODEL="tenants.ProjectDomain" (框架契约,不可删)
                               #   DATABASE_ROUTERS(审计独立连接), MIDDLEWARE(TenantContextMiddleware)
  locale/                      # i18n 翻译 (en/zh_Hans/zh_Hant/ja/ko/fr/es/it/de/ru/ar/he 的 .po)

  # ===== public schema 应用 (SHARED_APPS) =====
  apps/tenants/                # ProjectTenant(TenantMixin), ProjectDomain(contract-only),
                               #   HeaderBasedTenantMiddleware / TenantContextMiddleware,
                               #   schema 创建/删除, X-Project-ID 路由与校验, ProjectTenantViewSet
  apps/administration/         # RBAC(User/Role), ProjectTaskForce/TaskForceMembership,
                               #   schema_customization: CustomFieldDefinition/FieldConfigOverride/CustomEnumList/SchemaChangeLog (D10, public 定义表)
                               #   access.py(user_accessible_project_ids — 项目可见性单一事实来源),
                               #   supporting_tables, naming(NamingConvention), preferences, backup, Organization
  apps/audit/                  # AuditLog(public, 独立 DB 连接), GlobalRevision, 审计中间件/信号, ChangeNotification
  apps/core/                   # 抽象基类(AuditedModel/SoftDeleteModel/VersionedModel),
                               #   permissions, files(FileAsset), tasks(Celery 基础), 通用工具
                               #   (注:不再承载 domain/hierarchy — 已分别迁至 tenants/core_engineering)

  # ===== 租户 schema 应用 (TENANT_APPS) =====
  apps/core_engineering/       # Client, Site, Plant, PlantHierarchy(MPTT: PLANT/AREA/UNIT) — 工厂层级
  apps/custom_tables/          # CustomTable/CustomTableRow 通用行存储 (UDT, D10, 租户 schema)
  apps/instruments/            # models(Component/TechnologyType/TagIOAllocation/SIF/SIFElement/ProcurementInfo),
                               #   serializers, services, viewsets, tests,
                               #   fixtures/technology_types.json (D9), management/commands/load_engineering_seeds.py
  apps/process_data/           # fixtures/process_data_field_catalog.json (D9)
  apps/calculations/
  apps/specifications/
  apps/wiring/
  apps/dimensions/
  apps/loop_drawings/
  apps/hookups/
  apps/documents/
  apps/deliverables/           # DeliverableType/DeliverableTemplate/TemplateRenderJob, render engines (xlsx/docx/svg/dxf/html) (D12)
  apps/ede/
  apps/import_export/          # 含 P&ID 集成: ImportJob/ImportMapping/ImportRecord/SyncSchedule
  apps/integration/
  apps/rules/
  apps/db_integrity/
  apps/revisions/              # EntityRevision(租户实体版本快照), RevisionComparison (§6.1)
  apps/concurrency/            # EditLock(记录级锁定), 锁定 API, WebSocket 实时同步 (§6.3)

frontend/
  src/api/                   # generated, hooks, axios 拦截器(注入 X-Project-ID), Accept-Language
  src/app/                   # routes(项目级 /projects/{project_no}/...), layout, auth,
                             #   ProjectContext(当前租户), HierarchyNavigator, ContextSelector(Ctrl+1~5)
  src/i18n/                  # config.ts, locales/<lang>/*.json (react-i18next), useDirection(RTL)
  src/features/<module>/     # components, pages, schemas, stores, tests
  src/shared/ui/             # grid, forms, task-progress, permissions, lock-indicator, change-marker

infra/
  docker-compose.yml
  nginx/                     # 单 server_name 反代 (Header 路由, 无需子域)
  postgres/
  redis/
```

**SHARED_APPS / TENANT_APPS 划分原则**：

- **SHARED_APPS（public schema）**：`tenants`、`administration`、`audit`、`core`，以及 Django 内置 `contenttypes`/`auth`。跨项目共享的用户、角色、项目组、租户元数据、全局审计。
- **TENANT_APPS（租户 schema）**：`core_engineering` 及全部工程业务模块（instruments、process_data、…、revisions、concurrency）。每个 ProjectTenant 拥有独立 schema 副本。
- **跨 schema 注意事项**：`EntityRevision`/`EditLock` 使用 ContentType 通用外键指向租户数据，须在租户 schema 内迁移；`AuditLog`/`GlobalRevision` 位于 public，记录租户操作时一并存 `project_id` 以便回溯。

**`config/settings.py` 示例配置片段（django-tenants）**：

```python
# ---- django-tenants 多租户配置 ----
# public schema 应用：跨项目共享，仅在 public schema 中迁移一次
SHARED_APPS = [
    "django_tenants",                # 必须置于最前
    "apps.tenants",                  # ProjectTenant / ProjectDomain (租户元数据)
    # Django 内置 (ContentType/auth 必须共享，供全局用户与通用外键使用)
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    # 第三方
    "rest_framework",
    "drf_spectacular",
    "django_celery_beat",
    # 业务共享应用 (public schema)
    "apps.administration",           # User/Role/TaskForce/命名规则/支撑表/偏好/备份/Organization
    "apps.audit",                    # AuditLog / GlobalRevision / ChangeNotification
    "apps.core",                     # 抽象基类 / permissions / files(FileAsset) / tasks
]

# 租户 schema 应用：每个 ProjectTenant 拥有独立 schema 副本
TENANT_APPS = [
    "django.contrib.contenttypes",   # 与 SHARED 并列声明，保证租户 schema 内可用
    "apps.core_engineering",         # Client / Site / Plant / PlantHierarchy(MPTT)
    "apps.instruments",
    "apps.process_data",
    "apps.calculations",
    "apps.specifications",
    "apps.wiring",
    "apps.dimensions",
    "apps.loop_drawings",
    "apps.hookups",
    "apps.documents",
    "apps.ede",
    "apps.import_export",            # 含 P&ID 集成 (ImportJob/ImportMapping/SyncSchedule)
    "apps.integration",
    "apps.rules",
    "apps.db_integrity",
    "apps.revisions",               # EntityRevision / RevisionComparison
    "apps.concurrency",             # EditLock / WebSocket 实时同步
]

# INSTALLED_APPS = SHARED_APPS + 仅在 TENANT_APPS 中、未出现于 SHARED_APPS 的应用 (去重)
INSTALLED_APPS = list(SHARED_APPS) + [a for a in TENANT_APPS if a not in SHARED_APPS]

# 租户模型契约
TENANT_MODEL = "tenants.ProjectTenant"          # 继承 TenantMixin
TENANT_DOMAIN_MODEL = "tenants.ProjectDomain"   # 框架契约，不可删除 (本系统不用子域路由)

DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",   # 多租户后端
        "NAME": "openinstrument",
        # host/port/user/password 由环境变量注入
    }
}

DATABASE_ROUTERS = [
    "django_tenants.routers.TenantSyncRouter",  # 控制 SHARED/TENANT 应用迁移到正确 schema
    # 审计可选独立连接路由 (AuditLog 写入只追加)
]

MIDDLEWARE = [
    # 注意：使用自定义 Header 路由，而非 django_tenants 默认的 TenantMainMiddleware
    "apps.tenants.middleware.TenantContextMiddleware",  # 读取 X-Project-ID → set_tenant + 可见性校验
    "django.middleware.locale.LocaleMiddleware",        # i18n (Accept-Language)
    # ... 其余标准中间件
]

# 迁移命令：
#   python manage.py migrate_schemas --shared     # 迁移 public schema (SHARED_APPS)
#   python manage.py migrate_schemas --tenant     # 迁移所有租户 schema (TENANT_APPS)
#   创建 ProjectTenant 时由 TenantMixin.create_schema() 自动建 schema 并迁移 TENANT_APPS
```

> **要点提示**：`django_tenants` 必须为 `SHARED_APPS` 首项；`contenttypes` 须在两个列表中均声明，以保证通用外键（`EntityRevision`/`EditLock`/`AuditLog`）在 public 与租户 schema 下均可解析；`INSTALLED_APPS` 由两表去重合并得到，避免重复注册。本系统以 `TenantContextMiddleware`(Header 路由) 取代 `TenantMainMiddleware`(子域路由)，故不依赖 `ProjectDomain` 运行时数据（详见 §15.1.2 ADM-T03）。

---

## 4.11 给 AI IDE 的实施提示

1. **先实现基础层**：`backend/apps/tenants`（多租户 Schema 路由）、`administration`（RBAC/项目组/命名规则）、`core_engineering`（Client/Site/Plant/PlantHierarchy）、`instruments` 的模型、迁移、seed、API 和测试，不要跳到复杂图形模块。先打通"创建 ProjectTenant → 自动建 schema → X-Project-ID 切换 → 在租户 schema 内 CRUD"的链路。
2. **Service 层原则**：所有业务写操作必须通过 Service 层；ViewSet 不直接写复杂业务逻辑。
3. **类型同步**：先生成 OpenAPI，再由前端消费类型；禁止前后端手写不一致 DTO。
4. **持续验证**：每完成一个模块，运行 pytest、ruff/mypy、Vitest，并更新 traceability matrix。
5. **高风险模块优先测试**：对 WIR、CALC、RULE 三个高风险模块，先写测试向量和服务类，再写 UI。

---

## 4.12 待项目方确认事项

> **与 `docs/OPEN_QUESTIONS.md` 的关系**：本表为**已识别、待裁决**的事项，仓库建库时应将下表逐条复制为 `docs/OPEN_QUESTIONS.md` 的初始条目（格式 `OQ-<序号> | 问题 | 影响的 WP | 默认假设 | 状态`）。agent 在实现中新发现的 spec 矛盾追加到该文件，不得直接改本文件。裁决后由项目方回写本文件 §4.12.1 决策记录并关闭对应 OQ。


| 待确认项 | 默认假设 |
|---------|---------|
| 是否 100% 复刻 SPI 行为 | 默认复刻核心工程流程，不复刻桌面 UI 的每个交互细节 |
| 计算标准授权和公式版本 | 默认使用公开标准公式，由项目方确认具体版本和商业授权 |
| AG Grid Enterprise 授权 | 默认项目方具备商业授权；否则需替换为 MIT 许可网格并降低部分功能 |
| 多租户隔离方式 | 依据 SPECIFICATION.md 采用 PostgreSQL Schema 隔离（django-tenants）+ X-Project-ID Header 路由，租户单位为 ProjectTenant；若改为子域多租户 SaaS，需恢复 TenantMainMiddleware 及 ProjectDomain admin/API |
| 电子签名/法规合规 | 默认无 21 CFR Part 11；若需要，须补充签名、不可抵赖、审计留存要求 |
| SIL 验证计算（PFDavg / RRF / 架构约束 HFT，IEC 61511 §11.9） | SIF 实体（§2.4，D8）已预留全部输入字段（sil_target、demand_mode、proof_test_interval、mission_time、表决结构）。**计算本身默认不在 Phase 1**：涉及失效率数据库（exida SERH / 制造商 FMEDA）授权与 β 因子等方法学选择。若项目方裁决纳入，编号预留为 **CALC-15**，作为独立 WP（H 风险，先测试向量），本文件当前不含其需求条目 |
| 文档编号分段 `XX-XX` 的项目含义（D14） | 实测 `70XXXXXX-WSP-XX-XX-DS-CI-…` 中两个 `XX` 按 ISO 19650 为 **Volume/System** 与 **Level/Location**，模板中为占位。默认按此两段实现（可配置）；项目方须确认实际填写规则（系统号？楼层？区域？）及是否允许保持 `XX` |
| Issue Purpose 取值集与版次编号方案（D14） | 默认 `FOR_COMMENT / FOR_ENQUIRY / FOR_QUOTATION / FOR_PURCHASE / FOR_CONSTRUCTION / AS_BUILT / FOR_INFORMATION`（实测模板仅用 `For Enquiry`、1 份 `For Review`）；版次两段制 `P01…P0n` → `01…0n`（实测模板 `P01`，MASTER VER. 为 `01–05`）。须项目方确认取值集与 `For Review` 是否等同 `FOR_COMMENT` |
| WSP 模板库 21 个新增技术类型的 I/O 与字段适用性（D14） | 全部标 `needs_review`。实测分三组（明细与建议值见 `technology_types_REVIEW.md`）：**A. 12 条**已继承同前缀裸泛型，数值可用但须确认；**B. 1 条**（`UI15`）继承的泛型 `UI` 本身为 I/O 0、全 NA，实际等同未赋值；**C. 8 条**（`FES55 / LIT42 / LIT80 / QEI65 / QET60 / QET70 / VET10 / XET10`）无裸泛型可继承，I/O 置 0、适用性全 NA——其中 `LIT`、`QET` 有带编号的同族条目但无泛型行，`FES / QEI / VET / XET` 前缀完全缺失。**影响**：I/O 为 0 使 IDX-16 的 I/O 汇总少算；全 NA 使 IDX-17 完整度恒为 100%。**注意全 NA 不一律错误**：区域/环境探测器（`QET60/QET70/QEI65`）、转矩测量（`XET10`）、声光报警器（`UI15`）本无工艺介质，全 NA 可能正确；真正需补的是 B、C 组中 8 条的 **I/O**，以及接液的 `VET10` 的**适用性** |
| 模板库先修复还是先绑定（D14） | 建议**先修模板库**（38 处措辞、单位冲突、拼写、6 份残留工作表、QET20 重复文件），再做绑定——否则绑定会把不一致固化进软件。若工期不允许，可先绑定并由 DTL-08 持续出报告 |
| Tag 过程数据掩码 `OPTIONAL` 值 | 种子仅含 REQUIRED/NA（模板无 OPTIONAL）；是否引入 OPTIONAL 语义（显示但不计入完整度分母）由项目方决定 |

### 4.12.1 决策记录 【V2.1 新增，2026-07-10 项目方裁决】

| 编号 | 决策 | 内容与实施要点 |
|------|------|---------------|
| D1 | 认证路径：双路径别名过渡 | 规范路径 `/api/v1/auth/login\|refresh/`；旧路径 `/api/token/*` 指向同一视图作为废弃别名，响应附 `Deprecation`/`Sunset` 头，保留一个次要版本周期后移除。前端 axios 与所有测试改用新路径；OpenAPI schema 中旧路径标记 `deprecated: true`。 |
| D2 | URL 前缀：彻底迁移，无过渡 | 现行 `/api/engineering/*`、`/api/admin/*` 路由一次性迁移至 `/api/v1/*`（engineering 与 admin 资源平铺至 `/api/v1/<resource>/`；`/api/tenants/*` → `/api/v1/tenants/*`）。除 D1 认证别名外**不设其它双路径**。实施顺序：后端 urls.py 迁移 → 重新生成 OpenAPI → 前端 `generate:api` 重建 client → 更新 axios baseURL 与 Vite 代理 → 全量回归（AGENTS.md V1–V6）。豁免路径：`/admin/`（Django Admin）与 `/api/docs\|redoc\|schema/` 保持原状。 |
| D3 | 前缀归一：全文档消灭无前缀写法 | 文档内所有端点写法已统一为 `/api/v1` 前缀（§15.1.3、§15.7、§15.3.3、§15.5.6、EDE-09、VC-01/05、I18N-04、CC-01、PID-02/05/06）。附带修正：I18N-04 用户偏好路径由 `/api/user/preferences/` 统一为 `/api/v1/me/preferences/`（与 §15.7 一致，消除同功能双路径）。今后规则：任何章节新增端点必须带 `/api/v1` 前缀并同步登记 §5.4。 |
| D4 | P&ID 导入作业 API 收编至 integration 命名空间 | §6.4 的 P&ID 作业端点由 `/api/v1/imports\|exports/*` 改为 `/api/v1/integration/pid/imports\|exports/*`（PID-02/05/06 原文已同步改写，§5.4.17 已登记）。理由：与模块8 IFC 的 `/api/v1/import/` 仅差一字母，跨子系统歧义；P&ID 集成语义上从属 INT 模块。IFC 路径（`/api/v1/import/`、`/api/v1/merger/`）维持不变。 |
| D5 | RBAC：5 级权限等级 + 7 个预设角色 | 维持代码现行 `Role.Level` 五级（1=Guest…5=Administrator，Level 2 预留）；按 §15.2.2 预设角色表补齐 **7 个** `is_system_role=True` 的种子角色（ADMIN/PROJ_MGR/PROJ_ENG/INST_ENG/PROC_ENG/MECH_ENG/GUEST，数据迁移交付于 WP-02）。原"七级 vs 五级"冲突关闭：spec 侧 §15.2 结构无需变更（其本就是 7 角色挂 5 级轴）；代码侧不改 Level 枚举，仅补角色种子与权限矩阵。`docs/OPEN_QUESTIONS.md` 对应条目标记已裁决。 |
| D6 | WBS：拆分 WP-13，解除 WP-05 隐式依赖 | **2026-09-18 裁决**。原 WP-13（DDP + Hook-Up）拆为 **WP-13A「PipingClass 主表」**（§9.2、DDP-11~13、§4.4.7，风险 M，依赖 WP-03 工厂层级）与 **WP-13B「DDP 尺寸数据 + Hook-Up」**（模块9 其余、模块12，风险 L，依赖 WP-04）。**WP-05 过程数据的依赖改为 WP-04 + WP-13A**（PD-02 design_* 派生需要 PipingClass）。WP-13A 提前到与 WP-04 并行，不阻塞关键路径。 |
| D7 | 采购/成本扩展纳入范围 | **2026-09-18 裁决**。以 Tag 一对一 `ProcurementInfo` 扩展表实现（§2.5，IDX-21，§4.4.9 状态机），独立权限行（§4.3），成本/长周期报告复用 IDX-15 框架；`exotic_moc` 留在 COMPONENT。新增 **WP-04B「采购/成本扩展」**（风险 L，依赖 WP-04）。 |
| D8 | SIF 建为一级实体（IEC 61511 语义） | **2026-09-18 裁决**。新增 `SafetyInstrumentedFunction` + `SIFElement`（§2.4，IDX-19/20，§4.4.8）。**COMPONENT 字段修正**：`sil_level` → `sil_capability`（设备 SIL 能力，1–4）；删除文本 `sif_reference`，改由 `SIFElement` 多对多提供，派生 `required_sil` = max(sif_target)。理由：SIL 属 SIF 而非设备；传感器可复用于多个 SIF。SIL 验证**计算**不在本决策范围（见 §4.12 待确认）。新增 **WP-04A「SIF 实体」**（风险 M，依赖 WP-04、WP-08 的 Panel 模型仅作可选 FK）。 |
| D9 | 技术类型与过程数据字段目录种子文件纳入交付 | **2026-09-18 生成**。`technology_types.json`（291 条）、`process_data_field_catalog.json`（26 字段）、`technology_types_REVIEW.md`（131 条待复核）— 路径、加载命令与生成约定见 §2.1.1.1。**项目方动作**：逐条确认 REVIEW 清单（重点：23 条阀类功能字母、UT10 疑似遗漏、4 条继承掩码），确认后将 `needs_review` 置 false 并 bump `schema_version`。 |
| D10 | 数据模型定制（Schema Customization / UDF·UDT）作为通用性基座 | **2026-09-18 项目方指示补充**。新增 §15.8：`CustomFieldDefinition`（覆盖任意 Item Type）、`CustomTable/CustomTableRow`（UDT）、`FieldConfigOverride`（系统字段属性覆盖）、`CustomEnumList`、`SchemaChangeLog`；ADM-09~14；统一字段元数据服务 `GET /api/v1/schema/{item_type}/` 为表单/网格/EDE/导入/模板的唯一来源。**边界**：元数据驱动，不对核心表 DDL；系统字段可改标签/可见/必填/默认/校验但不可删或改类型。IDX-05 改为引用 §15.8。纳入 WP-02（模型与 API）与 WP-09（EDE 消费合并 schema）。 |
| D11 | Excel/CSV 外部数据表导入的明确化 | **2026-09-18 项目方指示补充**。模块8 IFC-01/02 明确源格式（xlsx/xlsm/xls/csv/tsv/json/DB）与目标表（全部 `allow_import` Item Type + 支撑表 + UDT + 自定义字段）；新增 IFC-09 导入模板下载、IFC-10 预置 Import Link（含 `IS_TEMPLATE_SCHEDULE`：项目方现行 Instrument Schedule → Component/TagIOAllocation/PD/Procurement）、IFC-11 大文件异步；Import Link JSON 增 `source_options/child_mappings/is_system_preset`；§5.4.15 登记 5 个端点。纳入 WP-10。 |
| D12 | 交付物模板库（Deliverable Template Library） | **2026-09-18 项目方指示补充**。新增 §6.6：16 类标准 C&I 交付物注册表（含 Instrument Schedule / I/O Schedule / Datasheets / Cable Schedule / Cable Termination / Loop Diagrams 等）、`DeliverableTemplate`（XLSX/DOCX/SVG/DXF/HTML，SYSTEM/IMPORTED/DESIGNED，组织级/项目级，版本与默认）、`TemplateRenderJob`、统一占位符语法（与 M11 `@{}` 宏兼容）、DTL-01~07（导入向导/渲染引擎映射/图框标题栏/版本迁移）；`/api/v1/reports/{type}/` 改为调用默认模板。新增 **WP-15A「交付物模板库」**（风险 M，依赖 WP-06、WP-09、WP-12）。 |
| D13 | 规格自足性收口 + 计算测试向量权威来源 | **2026-09-18 全面核查后裁决**。核查发现本文件此前对 agent **不自足**：模块9/10/11/12/13/14 仅以"保持 V2.0 内容不变"占位，而 V2.0 为仓库外 PDF，致 WP-08(H)/WP-11(H)/WP-12/WP-13B/WP-14 无可实现依据；37 个核心模型无字段级定义。裁决：(a) 自 V2.0 原始规格**恢复全部 6 个模块的数据模型与需求条目**（WIR-01~25、LOOP-01~10、HU-01~08、RULE-01~10、DBI-01~05、DDP-01~10 及 §9.0/§10.1/§12.1 数据模型），本文件自此为唯一且自足的事实来源，不再依赖外部 PDF；(b) 新增 **§4.5.1 计算测试向量权威来源规则**——向量必须来自标准条款/教科书例题/厂商软件/项目方手算并记录 `source`，**禁止 agent 自行推导**（否则测试与实现同源，只验证自洽不验证正确；对安全阀泄放、本安、SIL 相关计算不可接受），缺权威来源的计算项不得标记完成；(c) 新增 §5.5 模型清单（未列入模型不得创建）、§5.6 生成式可追溯性、§5.1.1 环境与版本锁定、附录 C 术语表、§4.4.10 尺寸数据状态机；(d) 消除 §5.1–5.4 与 §9.1 编号冲突（模块5 子节→§M5-1~M5-5；PipingClass→§9.2）；(e) DoD 由 8 条扩至 12 条。 |
| D14 | WSP Datasheet 模板库吸收 + 文档版次生命周期 | **2026-10-04 全量提取 71 份模板后裁决**。(a) **§4.4.11 新增 `DocumentIssue` 版次用途生命周期**（FOR_COMMENT/ENQUIRY/QUOTATION/PURCHASE/CONSTRUCTION/AS_BUILT/INFORMATION）并与 §4.4.2 SpecSheet、§4.4.9 Procurement **三状态机绑定**——此前三者独立，规格书答不出"datasheet 如何从询价走到订货再到施工"；实测全部 71 份模板首版用途均为 `For Enquiry`，证明模板库是询价版基线，后续版次必须由软件推进。(b) **SPEC-04 文档编号规则改写**为 ISO 19650/IGN104 分段（`{Project}-{Originator}-{Volume}-{Level}-{DocType}-{Discipline}-{TechCode}-{Sequence}` + `Iss {Rev}`），复用 NamingConvention（`entity_type=DOCUMENT`）；原 `{ProjectPrefix}-{FormNumber}-{SequentialNumber}` 产不出合规编号。(c) **SPEC-03 字段清单正式化**为 `spec_field_catalog`（593 字段，自模板库提取，按技术类型挂集合）。(d) **新增 SPEC-12~16**：五态占位语义（VALUE/VTA/TBA/TBC/NA + EMPTY，实测 VTA 13.2% + NA 13.4%，若计为缺失则就绪度判定全错）、供货文档与附件要求建模（合同性内容）、回标对比 Bid Tabulation、多页分区、WSP 模板库导入绑定。(e) **§6.6 增强**：DTL-02 必须支持纯坐标绑定与骨架复用（**71/71 份模板的字段级命名区域实测均不可用作绑定锚点**：62 份为 `#REF!`，另 9 份虽可解析但指向空单元格或语义错位的单元格——属上一代版式遗留的失效地址，比 `#REF!` 更危险，因为解析器不报错却绑定到错误数据）、新增 DTL-08 模板库健康度检查、新增 `BID_TABULATION` 交付物类型。(f) **种子**：`spec_field_catalog.json`、`wsp_template_bindings.json`、`WSP_TEMPLATE_AUDIT.md` 入库（§4.1.15）；`technology_types.json` 补 21 个模板库独有类型至 **312** 条。(g) 新增 **WP-06A**。 |

---

# 第五部分：技术架构与数据模型定义

## 5.1 系统技术栈概览

| 层级 | 技术选型 | 版本/说明 |
|------|---------|----------|
| 前端框架 | React 19 + TypeScript 5.x | Vite 7构建，Tailwind v4样式，Shadcn UI组件库 |
| 状态管理 | Zustand + TanStack Query | Zustand管理全局状态，TanStack Query管理服务端状态缓存 |
| 数据网格 | AG Grid Enterprise | 所有大数据量网格统一使用AG Grid |
| 后端框架 | Django 5.2 + DRF 3.15 | JWT认证，OpenAPI文档(drf-spectacular) |
| 数据库 | PostgreSQL 16+ | 主数据库，JSONB字段存储动态属性 |
| 缓存/消息 | Redis 7+ | 会话缓存、Celery队列、WebSocket Channel Layer |
| 异步任务 | Celery 5.x + Redis Broker | 批量导入/导出、报告生成等长时间任务 |
| 实时通信 | Django Channels + WebSocket | 异步任务进度通知、多用户协同编辑冲突提示 |
| 图形渲染 | SVG + Canvas (Konva.js/Fabric.js) | 回路图、Hook-Up图、接线图的浏览器端渲染 |
| 计算引擎 | Python NumPy/SciPy | 流量计/控制阀/安全阀/本安计算 |
| 报告生成 | WeasyPrint (PDF) / openpyxl (Excel) | 规格书、过程数据表、计算报告、BOM报告 |
| 容器化 | Docker Compose | PostgreSQL:5433, Redis:6380, Celery Worker, Django, Nginx |
| 测试框架 | pytest(后端) + Vitest+Testing Library(前端) | 目标覆盖率>80% |

### 5.1.1 运行环境与版本锁定【V2.1 新增 — 实施约束】

> agent 不得自行选择版本。以下为**下限与锁定策略**；确切补丁版以仓库 `pyproject.toml` / `package.json` 的 lockfile 为准，lockfile 一经生成即为事实来源。

| 项 | 约束 |
|----|------|
| Python | 3.12.x（django-tenants 与 psycopg3 兼容性已验证区间） |
| Django | 5.2 LTS |
| djangorestframework | 3.15+ |
| django-tenants | 3.6+（与 Django 5.2 兼容的最新稳定版） |
| psycopg | 3.x（`django_tenants.postgresql_backend` 之上） |
| PostgreSQL | 16+（JSONB GIN、表达式索引、MPTT 递归查询） |
| Redis | 7+ |
| Celery | 5.4+ |
| Node.js | 20 LTS 或 22 LTS |
| React | 19.x；TypeScript 5.x；Vite 7.x |
| 包管理 | 后端 `uv`；前端 `pnpm`（锁定 lockfile，CI 用 `--frozen-lockfile`） |
| 容器端口 | PostgreSQL **5433**、Redis **6380**（避开本机默认端口，与 AGENTS.md 一致） |
| 时区/编码 | 数据库 UTC、`USE_TZ=True`；全库 UTF-8 |

**依赖新增规则**：agent 新增任何三方依赖必须在 PR 描述中说明用途、许可证与替代方案；AG Grid Enterprise、字体、CAD 解析库等**涉及商业授权的依赖须先经项目方确认**（§4.12）。

---

## 5.2 核心数据模型关系图（基于SPI ERD）

| 实体(Django Model) | 主表名 | 主要外键关系 |
|-------------------|--------|-------------|
| Component (仪表标签) | component | → Loop, → Line, → Apparatus, → Drawing, → ComponentFunctionType, → ProcessFunction, → Unit |
| Loop (回路) | loop | → Unit, → Drawing, → LoopFunction, → LoopProc |
| PdGeneral (过程数据) | pd_general | → Component, → Line |
| SpecSheetData (规格书数据) | spec_sheet_data | → Component, → SpecForm, → Drawing |
| Panel (面板) | panel | → Panel(parent_id自引用), → Unit |
| Cable (电缆) | cable | → CableSet → Wire |
| Package (文档绑定器) | package | → PackageItemList → Drawing/SpecSheetData |
| Drawing (图纸/文档) | drawing | → Revision |
| RuleDefinition (规则定义) | rule_definitions | → RuleComponent, → RuleFilter, → RuleConsistency |

## 5.3 模块依赖关系与实施顺序

1. **Phase 1 (基础层)**：系统管理(用户/角色/权限) → 工厂层级 → 命名规范引擎 → 计量单位管理
2. **Phase 2 (核心数据)**：仪表索引模块(IDX) → 包含：仪表类型管理、回路管理、Supporting Tables
3. **Phase 3 (工程数据)**：过程数据模块(PD) ← 依赖IDX
4. **Phase 4 (计算引擎)**：计算模块(CALC) ← 依赖PD
5. **Phase 5 (规格书)**：规格书模块(SPEC) ← 依赖IDX/PD/CALC
6. **Phase 6 (接线设计)**：接线设计模块(WIR) ← 依赖IDX
7. **Phase 7 (详细工程)**：回路图(LOOP) ← 依赖WIR | 尺寸数据(DDP) ← 依赖IDX | Hook-Up(HU) ← 依赖IDX
8. **Phase 8 (文档管理)**：文档管理(DOC) ← 聚合各类文档
9. **Phase 9 (集成与工具)**：导入导出(IFC) + 系统集成(INT) + 规则引擎(RULE) + 数据库完整性(DBI)
10. **Phase 10 (统一入口)**：工程数据编辑器(EDE) ← 横跨所有模块

## 5.4 API 端点规划 【V2.1 更新 — 取代"详见原文第36-37页"占位】

> **约定**：全部端点遵循 §4.2 API 契约（Base URL `/api/v1`、Bearer 认证、分页/排序/过滤、错误格式、批量写入事务、异步任务 202 响应）。
> **前缀归一说明【已执行，见 §4.12.1 决策记录 D3】**：全文档所有端点写法（§15.1.3、§15.7、§15.3.3、§15.5.6、EDE-09、VC-01/05、I18N-04、CC-01、PID-02/05/06）已统一改写为带 `/api/v1` 前缀，以 §4.2.1 为准；本节仍为端点路径的最终权威，新增端点须先登记于此。
> **来源标记**：〔V2.0〕= 原 V2.0 端点清单（API 端点规划.docx）；〔V2.1 补〕= 本次为覆盖 spec 既有要求而补充；〔§x.x〕= 交叉引用既有章节定义。

### 5.4.1 认证与当前用户

| API路径 | HTTP方法 | 功能描述 | 来源 |
|---------|---------|---------|------|
| /api/v1/auth/login/ | POST | JWT Token获取 (username+password → access+refresh) | 〔V2.0〕 |
| /api/v1/auth/refresh/ | POST | JWT Token刷新 (refresh → new_access) | 〔V2.0〕 |
| /api/v1/me/ | GET | 当前用户信息 | 〔§15.7〕 |
| /api/v1/me/task-forces/ | GET | 我的项目组列表 | 〔§15.7〕 |
| /api/v1/me/preferences/ | PUT | 更新用户偏好设置 | 〔§15.7〕 |

> **【已裁决 2026-07-10，见 §4.12.1 决策记录 D1】** 规范路径为 `/api/v1/auth/login/`、`/api/v1/auth/refresh/`。现行 simplejwt 默认路径 `/api/token/`、`/api/token/refresh/` 作为**废弃别名**保留一个次要版本周期（指向同一视图，响应附 `Deprecation: true` 与 `Sunset` 头），下一版本移除。新代码（前端与测试）一律只使用 `/api/v1/auth/*`；引用旧路径视为违反 AGENTS.md 硬性规则。

### 5.4.2 租户与系统管理

租户管理端点见 **§15.1.3**（projects 及 switch/current），角色/用户/项目组/命名规则端点见 **§15.7**，数据模型定制端点见 **§15.8.4**（D10），均为 `/api/v1` 前缀。此处不重复列出，避免双源漂移。

### 5.4.3 工厂层级 〔V2.1 补 — 依据 §15.4/ADM-02〕

| API路径 | HTTP方法 | 功能描述 |
|---------|---------|---------|
| /api/v1/clients/ 、/api/v1/clients/{id}/ | GET/POST；GET/PUT/PATCH/DELETE | 客户/业主 CRUD |
| /api/v1/sites/ 、/api/v1/sites/{id}/ | GET/POST；GET/PUT/PATCH/DELETE | 厂区 CRUD |
| /api/v1/plants/ 、/api/v1/plants/{id}/ | GET/POST；GET/PUT/PATCH/DELETE | 工厂/装置 CRUD |
| /api/v1/plant-hierarchy/ | GET/POST | 层级树查询（MPTT）与节点创建 |
| /api/v1/plant-hierarchy/{id}/move/ | POST | 节点移动（改变父节点/排序） |

### 5.4.4 仪表索引 (IDX)

| API路径 | HTTP方法 | 功能描述 | 来源 |
|---------|---------|---------|------|
| /api/v1/instruments/ | GET/POST | 仪表标签列表(分页/过滤/排序)和创建 | 〔V2.0〕 |
| /api/v1/instruments/{id}/ | GET/PUT/PATCH/DELETE | 仪表标签详情/更新/删除 | 〔V2.0〕 |
| /api/v1/instruments/{id}/process-data/ | GET/POST | 仪表的过程数据 | 〔V2.0〕 |
| /api/v1/instruments/{id}/spec/ | GET/POST | 仪表的规格书 | 〔V2.0〕 |
| /api/v1/instrument-types/ 、/{id}/ | GET/POST；GET/PUT/PATCH/DELETE | 仪表类型 CRUD | 〔V2.1 补 — 依据模块2〕 |
| /api/v1/technology-types/ 、/{id}/ | GET/POST；GET/PUT/PATCH/DELETE | 仪表技术类型 CRUD（含 default_io_profile、process_data_applicability） | 〔V2.1 补 — IS模板 §2.1.1.1〕 |
| /api/v1/instruments/{id}/io-allocations/ 、/{alloc_id}/ | GET/POST/PUT；PATCH/DELETE | Tag I/O 分配子表（PCS/SIS × 信号类型） | 〔V2.1 补 — IS模板 IDX-16〕 |
| /api/v1/instruments/{id}/completeness/ | GET | 数据完整度（completeness_pct + 缺失字段清单） | 〔V2.1 补 — IS模板 IDX-17〕 |
| /api/v1/instruments/confirm-pid-revision/ | POST | 批量确认 P&ID 复核至当前版本 | 〔V2.1 补 — IS模板 IDX-18〕 |
| /api/v1/reports/io-summary/ | GET | I/O 数量汇总报告（PCS/SIS × signal_kind × connection_type，可按 Area/System/柜位分组） | 〔V2.1 补 — IS模板 IDX-15〕 |
| /api/v1/reports/instrument-count-by-type/ | GET | 仪表数量按技术类型 × 采购责任方汇总 | 〔V2.1 补 — IS模板 IDX-15〕 |
| /api/v1/sifs/ 、/{id}/ | GET/POST；GET/PUT/PATCH/DELETE | 安全仪表功能 CRUD | 〔D8 — §2.4 IDX-19〕 |
| /api/v1/sifs/{id}/elements/ 、/{elem_id}/ | GET/POST；PATCH/DELETE | SIF 组成元件（Tag 角色/表决组） | 〔D8 — §2.4.2〕 |
| /api/v1/sifs/{id}/approve/ | POST | SIF 审批 Draft → Approved | 〔D8 — §4.4.8〕 |
| /api/v1/instruments/{id}/sifs/ | GET | Tag 参与的 SIF 列表与派生 required_sil | 〔D8 — IDX-20〕 |
| /api/v1/reports/sif-register/ | GET | SIF 清单 / 元件清单 / 按 SIL 统计 | 〔D8 — IDX-20〕 |
| /api/v1/instruments/{id}/procurement/ | GET/PUT/PATCH | Tag 采购信息（一对一） | 〔D7 — §2.5 IDX-21〕 |
| /api/v1/procurement/batch-status/ | POST | 批量推进采购状态 | 〔D7 — IDX-21〕 |
| /api/v1/reports/cost-summary/ | GET | 成本汇总（技术类型 × 责任方 × 状态；可按 GlobalRevision 比较） | 〔D7 — IDX-21〕 |
| /api/v1/reports/long-lead-items/ | GET | 长周期设备清单 | 〔D7 — IDX-21〕 |
| /api/v1/loops/ | GET/POST | 回路列表和创建 | 〔V2.0〕 |
| /api/v1/loops/{id}/copy/ | POST | 回路复制 | 〔V2.0〕 |
| /api/v1/loops/{id}/tags/ | GET/POST | 回路下的仪表标签 | 〔V2.0〕 |
| /api/v1/lines/ | GET/POST | 管线列表和创建 | 〔V2.0〕 |
| 位号验证/生成/解析 | POST | 见 §15.7（tags/validate-number 等三端点） | 〔§15.7〕 |

### 5.4.5 过程数据 (PD)

| API路径 | HTTP方法 | 功能描述 | 来源 |
|---------|---------|---------|------|
| /api/v1/lines/{id}/process-data/ | GET/POST | 管线过程数据 | 〔V2.0〕 |
| /api/v1/process-data/{id}/cases/ | GET/POST | 过程数据 Case 管理（状态机见 §4.4.1） | 〔V2.0〕 |
| /api/v1/process-data/copy/ | POST | 过程数据复制 | 〔V2.0〕 |
| /api/v1/process-data/field-schema/?technology_type={id} | GET | 按技术类型下发过程数据表单 schema（REQUIRED/OPTIONAL/NA 掩码 + 字段目录） | 〔V2.1 补 — IS模板 PD-03〕 |
| /api/v1/process-data/field-catalog/ | GET | 过程数据字段目录（分组/结构/UOM 类别） | 〔V2.1 补 — IS模板 M3〕 |

### 5.4.6 规格书 (SPEC)

| API路径 | HTTP方法 | 功能描述 | 来源 |
|---------|---------|---------|------|
| /api/v1/specs/ | GET/POST | 规格书列表和生成（状态机见 §4.4.2） | 〔V2.0〕 |
| /api/v1/specs/{id}/revisions/ | GET/POST | 规格书修订管理 | 〔V2.0〕 |
| /api/v1/specs/compare/ | POST | 规格书修订比较 | 〔V2.0〕 |
| /api/v1/specs/apply-template/ | POST | 批量应用规格书模板（异步，见 §4.2.4） | 〔V2.0〕 |
| /api/v1/specs/global-revision/ | POST | 全局修订（见 §6.1） | 〔V2.0〕 |
| /api/v1/specs/field-catalog/ | GET | 规格书字段目录（593 字段；`?technology_type=` 返回该型字段集与分区顺序） | 〔D14 — SPEC-03〕 |
| /api/v1/specs/{id}/fields/ | GET/PATCH | 规格书字段值（含 placeholder_state、vendor_value、compliance） | 〔D14 — SPEC-12/14〕 |
| /api/v1/specs/{id}/requirements/ | GET/POST/DELETE | 供货文档与附件要求（DOCUMENTATION / ACCESSORIES / NOTE） | 〔D14 — SPEC-13〕 |
| /api/v1/specs/{id}/readiness/ | GET | 询价/订货就绪度（按五态占位语义计算，返回缺失字段清单） | 〔D14 — SPEC-12〕 |
| /api/v1/documents/{content_type}/{object_id}/issues/ | GET/POST | 文档版次列表 / 发版（校验见 §4.4.11） | 〔D14 — §4.4.11〕 |
| /api/v1/documents/issues/{id}/advance/ | POST | 推进版次用途（同步 SpecSheet 与 Procurement 状态） | 〔D14 — §4.4.11〕 |
| /api/v1/reports/bid-tabulation/ | GET | 回标对比表 / 技术偏差表 | 〔D14 — SPEC-14〕 |
| /api/v1/deliverable-templates/import-folder/ | POST | 批量导入模板文件夹 + 绑定覆盖率报告 | 〔D14 — DTL-02〕 |
| /api/v1/deliverable-templates/audit/ | GET | 模板库健康度检查报告 | 〔D14 — DTL-08〕 |

### 5.4.7 计算引擎 (CALC)

| API路径 | HTTP方法 | 功能描述 | 来源 |
|---------|---------|---------|------|
| /api/v1/calculations/control-valve/ | POST | 控制阀计算（§5.1，ISA S75.01） | 〔V2.0〕 |
| /api/v1/calculations/flow-meter/ | POST | 流量计计算（§5.2，ISO 5167） | 〔V2.0〕 |
| /api/v1/calculations/relief-valve/ | POST | 安全阀计算（§5.3，API RP 520） | 〔V2.0〕 |
| /api/v1/calculations/intrinsic-safety/circuit/ | POST | 本安计算-按电路类型（§5.4） | 〔V2.0〕 |
| /api/v1/calculations/intrinsic-safety/loop/ | POST | 本安计算-按回路（§5.4） | 〔V2.0〕 |
| /api/v1/calculations/thermowell/ | POST | 温度套管计算（§5.5，ASME PTC 19.3） | 〔V2.0〕 |

### 5.4.8 接线设计 (WIR)

| API路径 | HTTP方法 | 功能描述 | 来源 |
|---------|---------|---------|------|
| /api/v1/panels/ | GET/POST | 面板列表和创建（含 parent_id 自引用层级） | 〔V2.0〕 |
| /api/v1/cables/ | GET/POST | 电缆列表和创建 | 〔V2.0〕 |
| /api/v1/cables/export-spel/ | POST | 电缆导出到电气系统（模块7/SPEL） | 〔V2.0〕 |
| /api/v1/wiring/connections/ | GET/POST | 接线连接管理（信号传播见 §4.5） | 〔V2.0〕 |
| /api/v1/wiring/io-assignment/ | GET/POST | I/O 分配 | 〔V2.0〕 |

### 5.4.9 回路图 (LOOP) 〔V2.1 补 — 依据模块11〕

| API路径 | HTTP方法 | 功能描述 |
|---------|---------|---------|
| /api/v1/loop-drawings/generate/ | POST | 按回路生成回路图（返回 SVG 元素 schema，见 M11） |
| /api/v1/loop-drawings/{id}/ | GET | 回路图详情（SVG/元数据） |
| /api/v1/loop-drawings/batch-export/ | POST | 批量导出；>5 张走 Celery 异步（202 + task_id，进度经 WebSocket） |

### 5.4.10 尺寸数据与管道 (DDP) 〔V2.1 补 — 依据模块9〕

| API路径 | HTTP方法 | 功能描述 |
|---------|---------|---------|
| /api/v1/ddp/dimensional-groups/ 、/{id}/ | GET/POST；GET/PUT/DELETE | 尺寸组及其 JSON 字段模板管理 |
| /api/v1/instruments/{id}/dimensional-data/ | GET/POST | 仪表尺寸数据（UDF 经 custom_field_definitions 渲染） |
| /api/v1/ddp/outline-templates/ | GET/POST | SVG 轮廓模板（dim_outline_templates）管理 |
| /api/v1/piping-classes/ 、/{id}/ | GET/POST；GET/PUT/PATCH/DELETE | 配管等级/流体服务主表 CRUD（§9.2，Mechanical Eng/PE） |
| /api/v1/piping-classes/{id}/approve/ | POST | 审批 Draft → Approved（升版时旧版置 Superseded） |
| /api/v1/piping-classes/{id}/lines/ | GET | 引用该配管等级的 Line 列表（升版影响分析） |

### 5.4.11 Hook-Up (HU) 〔V2.1 补 — 依据模块12〕

| API路径 | HTTP方法 | 功能描述 |
|---------|---------|---------|
| /api/v1/hookup/libraries/ | GET/POST | 物料库（Library → SubLibrary → Item 层级） |
| /api/v1/hookups/ 、/{id}/ | GET/POST；GET/PUT/DELETE | Hook-Up 类型与仪表关联管理 |
| /api/v1/hookups/{id}/generate-bom/ | POST | 生成 BOM（按 M12 舍入/备品规则，快照入 bom_snapshots） |

### 5.4.12 文档管理 (DOC)

| API路径 | HTTP方法 | 功能描述 | 来源 |
|---------|---------|---------|------|
| /api/v1/packages/ | GET/POST | 文档绑定器管理（状态机 Working→Published→Superseded） | 〔V2.0〕 |
| /api/v1/packages/{id}/assign-items/ | POST | 文档分配到绑定器（DOC-03） | 〔V2.0〕 |
| /api/v1/packages/{id}/revise/ | POST | 绑定器修订（DOC-05） | 〔V2.0〕 |
| /api/v1/packages/{id}/print/ | POST | 按修订打印：多 PDF 合并输出，异步（DOC-07） | 〔V2.1 补〕 |
| /api/v1/drawings/ 、/{id}/ | GET/POST；GET/PUT/DELETE | 图纸/文档 CRUD（ERD：Drawing → Revision） | 〔V2.1 补〕 |
| /api/v1/drawings/{id}/revisions/ | GET/POST | 图纸修订管理（状态机见 §4.4.3） | 〔V2.1 补〕 |

### 5.4.13 工程数据编辑器 (EDE)

| API路径 | HTTP方法 | 功能描述 | 来源 |
|---------|---------|---------|------|
| /api/v1/ede/queries/ | GET/POST | EDE 查询定义管理（filter_ast 见 §4.2.1） | 〔V2.0〕 |
| /api/v1/ede/execute/ | POST | 执行 EDE 查询返回数据 | 〔V2.0〕 |
| /api/v1/ede/batch-update/ | PATCH | EDE 批量更新（单事务+row_errors，见 §4.2.3） | 〔V2.0〕 |

### 5.4.14 规则引擎 (RULE)

| API路径 | HTTP方法 | 功能描述 | 来源 |
|---------|---------|---------|------|
| /api/v1/rules/ | GET/POST | 规则定义管理 | 〔V2.0〕 |
| /api/v1/rules/evaluate/ | POST | 规则评估执行 | 〔V2.0〕 |
| /api/v1/rules/gui-evaluation/{item_type}/{id}/ | GET | GUI 规则评估 | 〔V2.0〕 |

### 5.4.15 导入/合并 (IFC)

| API路径 | HTTP方法 | 功能描述 | 来源 |
|---------|---------|---------|------|
| /api/v1/import/links/ | GET/POST | 导入 Link 管理 | 〔V2.0〕 |
| /api/v1/import/execute/ | POST | 执行数据导入（状态机见 §4.4.5，异步） | 〔V2.0〕 |
| /api/v1/import/test-run/ | POST | 导入测试运行（即 §4.4.5 之 Dry Run） | 〔V2.0〕 |
| /api/v1/merger/sessions/ | GET/POST | 合并会话管理 | 〔V2.0〕 |
| /api/v1/merger/compare/ | POST | 合并比较列表 | 〔V2.0〕 |
| /api/v1/merger/execute/ | POST | 执行数据合并（异步） | 〔V2.0〕 |
| /api/v1/import/templates/{item_type}/ | GET | 下载 Excel 导入模板（含自定义字段、下拉校验，随 schema_version） | 〔D11 — IFC-09〕 |
| /api/v1/import/targets/ | GET | 可导入目标表清单（含字段 schema 引用） | 〔D11 — IFC-01〕 |
| /api/v1/import/links/auto-map/ | POST | 上传文件表头 → 自动映射建议（置信度） | 〔D11 — IFC-02〕 |
| /api/v1/import/sessions/{id}/result-file/ | GET | Dry Run / 导入逐行结果 Excel 下载 | 〔D11 — IFC-11〕 |
| /api/v1/export/{item_type}/ | GET/POST | 任意可导出 Item Type / 自定义表的 Excel/CSV 导出（列 = 当前浏览器视图或全字段） | 〔D11〕 |
### 5.4.16 数据库完整性 (DBI)

| API路径 | HTTP方法 | 功能描述 | 来源 |
|---------|---------|---------|------|
| /api/v1/db-integrity/check/ | POST | 完整性检查（状态机见 §4.4.6，异步） | 〔V2.0〕 |
| /api/v1/db-integrity/apply-fix/ | POST | 应用修复建议 | 〔V2.0〕 |

### 5.4.17 系统集成 (INT)

| API路径 | HTTP方法 | 功能描述 | 来源 |
|---------|---------|---------|------|
| /api/v1/integration/publish/ | POST | 数据发布到外部系统（异步） | 〔V2.0〕 |
| /api/v1/integration/retrieve/ | POST | 从外部系统检索数据（异步） | 〔V2.0〕 |
| /api/v1/integration/webhooks/ | GET/POST | Webhook 注册管理 | 〔V2.0〕 |
| /api/v1/integration/pid/imports/ | POST | P&ID 导入作业创建（返回 job_id，见 §6.4 PID-02） | 〔V2.1 补 — D4〕 |
| /api/v1/integration/pid/imports/{job_id}/ | GET | P&ID 导入作业进度 | 〔V2.1 补 — D4〕 |
| /api/v1/integration/pid/imports/{job_id}/errors/ | GET | 逐行错误列表 | 〔V2.1 补 — D4〕 |
| /api/v1/integration/pid/imports/{job_id}/retry/ | POST | 重试指定记录 | 〔V2.1 补 — D4〕 |
| /api/v1/integration/pid/imports/compare/ | GET | P&ID 源数据与本地数据一致性比对（PID-06） | 〔V2.1 补 — D4〕 |
| /api/v1/integration/pid/exports/ | POST | 数据导出到 P&ID（PID-05，返回 download_url） | 〔V2.1 补 — D4〕 |

### 5.4.18 通用服务

| API路径 | HTTP方法 | 功能描述 | 来源 |
|---------|---------|---------|------|
| /api/v1/supporting-tables/{table_name}/ | GET/POST | 支撑表通用 CRUD（ADM-05 通用 ViewSet） | 〔V2.0〕 |
| /api/v1/uom/convert/ | GET | 计量单位转换 | 〔V2.0〕 |
| /api/v1/search/ | GET | 全局搜索 | 〔V2.0〕 |
| /api/v1/reports/{type}/ | GET | 报告生成 PDF/Excel（含 DOC-06 变更摘要；重报告异步）。**D12：实现改为调用 §6.6 DTL-04，使用该类型默认模板** | 〔V2.0 / D12〕 |
| /api/v1/deliverable-types/ 、/deliverable-templates/* 、/deliverables/* | 见 §6.6.5 | 交付物模板库与生成 | 〔D12 — §6.6〕 |
| /api/v1/schema/* 、/custom-tables/* | 见 §15.8.4 | 数据模型定制（字段/自定义表/覆盖/枚举/变更日志） | 〔D10 — §15.8〕 |
| /api/v1/tasks/{task_id}/ | GET | 异步任务状态查询（§4.2.4 之 poll_url 目标） | 〔V2.1 补〕 |
| /api/v1/locks/acquire/ 、/release/ 、/extend/ | POST | 记录级编辑锁获取/释放/心跳延长（CC-01） | 〔V2.1 补 — §6.3〕 |
| /api/v1/locks/status/ | GET | 锁状态查询（content_type+object_id） | 〔V2.1 补 — §6.3〕 |

> **一致性核对记录（2026-07-10）**：V2.0 清单 51 个端点全部保留且未改语义；补充 24 个端点均标注 spec 依据；未采纳任何无 spec 依据的新端点。同日完成三项裁决（§4.12.1 决策记录 D1–D3）：认证双路径过渡、URL 前缀彻底迁移、全文档前缀归一。原待观察项（`/imports/` 与 `/import/` 歧义）已于同日以决策 D4 裁决执行：P&ID 作业端点收编至 `/api/v1/integration/pid/*`，详见 §4.12.1 与 §5.4.17，无需再入 OPEN_QUESTIONS。

---

## 5.5 模型清单（Model Inventory）【V2.1 新增 — 实施索引】

> 用途：agent 建模与迁移前的**唯一清单**。schema 列 P=public、T=租户。"定义处"给出字段级定义所在章节；标注"支撑表"者按 §15.6 ADM-05 的统一 `SupportingTable` 基类实现（字段：`id, code, name, description, display_order, is_active` + 审计）。

| App | 模型 | schema | 定义处 |
|-----|------|--------|--------|
| tenants | ProjectTenant, ProjectDomain | P | §15.4.1、§15.1.1 |
| administration | Organization, User, Role, ProjectTaskForce, TaskForceMembership | P | §15.4.7、§15.2.2、§15.2.3、§15.3.1 |
| administration | NamingConvention | T | §15.5.1 |
| administration | CustomFieldDefinition, FieldConfigOverride, CustomEnumList, CustomEnumValue, SchemaChangeLog | P(组织级)/T(项目级) | §15.8.1、§15.8.3 |
| custom_tables | CustomTable, CustomTableRow | T | §15.8.1 |
| audit | AuditLog, GlobalRevision, ChangeNotification, ChangeRequest | P | §6.1.1、VC-03、VC-04 |
| core | FileAsset | P | §4.1.14 |
| core_engineering | Client, Site, Plant, PlantHierarchy | T | §15.4.2–15.4.5 |
| instruments | Component | T | §2.1.1 |
| instruments | ComponentFunctionType, InstrumentTechnologyType | T | IDX-03、§2.1.1.1 |
| instruments | Loop, Apparatus(设备) | T | IDX-07、IDX-06 |
| instruments | TagIOAllocation | T | §2.1.1.2 |
| instruments | SafetyInstrumentedFunction, SIFElement | T | §2.4.1、§2.4.2 |
| instruments | ProcurementInfo | T | §2.5.1 |
| process_data | Line | T | PD-01 |
| process_data | ProcessDataCase（含 design_*/operating_* 字段组） | T | PD-02、PD-04、M3 字段目录 |
| process_data | UnitOfMeasure, ConversionFactor | T | PD-08 |
| calculations | CalculationRun（保存计算输入/输出/standard/formula_version） | T | M5 增强要求、§4.5.1 |
| specifications | SpecPage, SpecForm, SpecSheetData, SpecFormTemplate | T | SPEC-01、SPEC-02、SPEC-04、SPEC-06 |
| specifications | SpecFieldCatalog, TechnologyTypeSpecField, SpecSheetFieldValue（含 placeholder_state / vendor_value / compliance）, DatasheetRequirement | T | SPEC-03、SPEC-12、SPEC-13、SPEC-14（D14） |
| documents | DocumentIssue（版次用途生命周期，ContentType 通用外键） | T | §4.4.11（D14） |
| wiring | Panel, CabinetRack, RackPosition, PanelStrip, PanelStripTerm, Channel, Cable, CableSet, Wire, WireTerminal, WireGroup, GeneralSignal, ControlSystemTag, Jumper, ConnectionTypeDefinition, FieldbusSegment | T | §10.1 |
| dimensions | DimensionalGroup, DimensionalGroupField, ComponentDimensional, DimensionalData, ProcessConnection, DefaultLibrary, DefaultLibraryData | T | §9.0 |
| dimensions | PipingClass | T | §9.2 |
| hookups | HookUpItemLibrary, HookUpSubLibrary, HookUpItem, HookUpType, HookUp, HookUpTypeInstrType, HookUpTagAssignment, HookUpItemAssociation, HookUpBOM, BOMSnapshot | T | §12.1 |
| loop_drawings | LoopDrawingConfig, LoopDrawingTemplate, LoopDrawingAnnotation, LoopDrawingMacro, LoopTemplateAssignment | T | LOOP-02~05 |
| documents | Drawing, Revision, Package, PackageItemList, FormNoteTemplate | T | 模块6、§5.2 |
| ede | SavedQuery, BrowserView, EDEViewConfig | T | EDE-05、EDE-11、IDX-13 |
| import_export | ImportLink, ImportSession, ImportJob, ImportMapping, ImportRecord, MergerSession, DatabaseConnection, SyncSchedule | T | IFC-01、§4.4.5、§6.4.2 |
| integration | ExternalSystemRegistry, SchemaMapping, ExternalObjectMap, IntegrationAuditLog | T | M7 增强要求 |
| rules | RuleDefinition, RuleComponent, RuleFilter, RuleConsistency, CustomRuleFunction | T | RULE-02~06 |
| db_integrity | IntegrityCheckRegistry, IntegrityCheckResult, IntegrityFixLog, IntegritySchedule | T | DBI-02、DBI-03、§14.2 |
| revisions | EntityRevision | T | §6.1.1 |
| concurrency | EditLock | T | §6.3.1 |
| deliverables | DeliverableType, DeliverableTemplate, TemplateRenderJob | T | §6.6.2 |
| 支撑表（administration，统一基类） | Manufacturer, Model, InstrumentLocation, AreaClassification, WireColor, WireType, CableType, ProcessFunction, LoopFunction, LoopProc, ResponsibleParty, PhysicalLocation, SignalConnectionType, DigitalSignalType, InsulationCode, HeatTracingCode, AlarmPriority | T | §15.6 ADM-05 |

**未在本清单中的模型不得创建**；确需新增时先在 `docs/OPEN_QUESTIONS.md` 提出并由项目方裁决后补入本表。

---

## 5.6 需求可追溯性（Traceability）【V2.1 新增】

DoD 第 9 条（§4.9）要求可追溯性矩阵。为避免手工维护漂移，采用**生成式**：

1. 每个需求 ID（如 `WIR-12`）在实现中以三处标记关联：
   - 代码：Service/ViewSet 的 docstring 首行写 `Spec: WIR-12`
   - 测试：测试函数加 `@pytest.mark.spec("WIR-12")`
   - API：DRF ViewSet 的 `@extend_schema(description=...)` 中包含该 ID
2. 脚本 `scripts/gen_traceability.py` 扫描本文件的需求 ID 表格与代码库标记，生成 `docs/TRACEABILITY.md`：`需求ID | 章节 | WP | 代码位置 | 测试用例 | 端点 | 状态(已实现/部分/未开始)`。
3. CI 门禁（AGENTS.md V3 之后追加 V3a）：**已在 WBS 中标记为完成的 WP，其范围内所有需求 ID 必须有测试标记**，否则 CI 失败。
4. 本文件是需求 ID 的唯一来源；新增需求必须先改本文件再实现。

---

# 第六部分：补充能力规格【V2.1 新增】

> 本部分补充了缺失的跨模块能力：版本控制、国际化、并发控制、P&ID 数据集成与非功能性需求。V2.0 原始规格（`Instrumentation_System_Functional_Requirements_Enhanced_V2.pdf`） §8（Excel 导入导出基础）已被本文件模块8（IFC）的企业级导入框架覆盖，不再重复；§4（API 规格）已被 §4.2 API 契约覆盖，仅在 §6.5 协调差异点。

## 6.1 版本控制 (Version Control) — 对应 SPI 模块 1.8

> **SPI 对应**：Revision Management + Audit Trail；**Django App**：`revisions`, `audit`。
> 本节统一 V2.1 中分散在 SPEC-09~11、DOC-05、ADM-07 及 §4.4.3 的修订/审计概念，提供跨实体的通用版本控制能力。

### 6.1.1 数据模型

**GlobalRevision（全局修订 — 项目里程碑版本）**

| 字段 | 说明 |
|------|------|
| id | BigAutoField |
| project | FK → ProjectTenant |
| revision_code | 版本号（如 "Rev 0"、"Rev A"、"IFC"） |
| description | 版本描述 |
| created_by | FK → User |
| created_at | 创建时间 |
| status | 状态（Draft / Issued / Superseded） |

功能：批量应用版本号到所有选定文档；自动更新图纸标题栏。

**EntityRevision（实体版本历史 — 通用版本模型）**

| 字段 | 说明 |
|------|------|
| id | BigAutoField |
| content_type | FK → ContentType（Django 通用外键） |
| object_id | 对象 ID |
| revision_number | 版本号 |
| global_revision | FK → GlobalRevision（可选） |
| data_snapshot | JSONField（完整数据快照） |
| change_type | CREATE / UPDATE / DELETE / RESTORE |
| change_summary | 变更摘要 |
| changed_by | FK → User |
| changed_at | 变更时间 |

功能：归档（保存数据快照）、字段级版本对比、版本回滚（恢复到历史版本）。

**AuditLog（审计日志 — Who/When/What）** 【与模块15 ADM-07 统一，存储于 public Schema】

| 字段 | 说明 |
|------|------|
| id | UUID |
| organization | FK → Organization |
| project | FK → ProjectTenant（可选） |
| user | FK → User |
| action | CREATE / READ / UPDATE / DELETE |
| model_name | 操作的模型名 |
| object_id / object_repr | 对象 ID / 字符串表示 |
| old_values / new_values | JSONField（变更前/后的值） |
| changed_fields | JSONField（变更字段列表） |
| change_details | JSONField（详细变更记录，见 §6.1.2） |
| ip_address / user_agent | 操作 IP / 浏览器信息 |
| timestamp | 操作时间 |

功能：自动记录（中间件/信号）、细粒度变更历史、支持 PSM（过程安全管理）与 MOC（变更管理）。

### 6.1.2 变更标记规格

`change_details` 数据结构（含每个字段的 old_value/new_value/change_type，数值字段附 change_percent，并含 summary 汇总）：

```json
{
  "changed_fields": ["description", "range_max", "status"],
  "changes": [
    {"field":"description","field_label":"描述","old_value":"Feed Flow Transmitter","new_value":"Feed Flow Transmitter (Revised)","change_type":"modified"},
    {"field":"range_max","field_label":"量程上限","old_value":100,"new_value":150,"change_type":"modified","change_percent":50.0},
    {"field":"status","field_label":"状态","old_value":"ACTIVE","new_value":"UNDER_REVIEW","change_type":"modified"}
  ],
  "summary": {"total_fields_changed":3,"fields_added":0,"fields_removed":0,"fields_modified":3}
}
```

变更类型（change_type）：`added`（空值→有值）、`removed`（有值→空值）、`modified`（旧值→新值）、`unchanged`（用于完整记录）。

### 6.1.3 功能需求

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| VC-01 | 变更追踪 API：`GET /api/v1/audit/{model}/{id}/changes/`（支持 from_date/to_date/field/user_id 过滤）返回完整变更历史；`GET /api/v1/audit/{model}/{id}/field-history/{field_name}/` 返回单字段完整变更历史。 | 基于 AuditLog 查询 + ContentType 通用外键。 |
| VC-02 | 前端变更标记 UI：新增字段绿色背景+"NEW"，修改字段黄色背景+"MODIFIED"，删除字段红色背景+删除线；字段旁变更图标(🔄)悬停显示"由 X 于 时间 修改"；左右对比视图（旧值\|新值）+ 时间线视图；批量变更报告（按类型分组，导出 Excel/PDF）。 | React 差异高亮组件 + 时间线组件。 |
| VC-03 | 变更通知（ChangeNotification）：关键字段变更（如 status、range_max）自动通知；可配置通知规则（按字段/用户/项目）；支持订阅特定记录变更；通知类型 Email/InApp/Both。 | ChangeNotification 模型（audit_log FK, recipients M2M, notification_type, is_sent, sent_at）+ Celery 发送。 |
| VC-04 | 变更审批流程（可选）：关键数据变更需审批。ChangeRequest 模型（model_name, object_id, requested_changes JSON, requester, approver, status: Pending/Approved/Rejected, reason, approval_comment）。流程：提交变更请求 → 通知审批人 → 批准/拒绝 → 批准后自动应用并记审计日志。 | ChangeRequest 模型 + 审批工作流。 |
| VC-05 | 版本对比（RevisionComparison）：`GET /api/v1/revisions/{entity_type}/{id}/compare/?from=1&to=2` 返回字段级差异列表（from_value/to_value/change_type，数值附 change_percent）及 summary 汇总。支持规格书/回路图的增强报表前后版本对比。 | RevisionComparisonService（对比两份 data_snapshot）。 |

## 6.2 国际化 (Internationalization - i18n)

### 6.2.1 设计原则

1. **英语为主语言**：系统默认 `en-US`，源代码 UI 文本使用英语，英语环境必须显示纯英语界面。
2. **多语言支持**：东亚语言 English(en)/简体中文(zh-CN)/繁體中文(zh-TW)/日本語(ja)/한국어(ko)；欧洲语言 Français(fr)/Español(es)/Italiano(it)/Deutsch(de)/Русский(ru)；RTL 语言 العربية(ar)/עברית(he)。语言切换立即生效，无需刷新；RTL 语言自动切换布局方向。
3. **翻译范围**：UI 文本、系统消息、报表标题、帮助文档。
4. **不翻译内容**：用户输入数据（位号/描述/备注）、技术术语缩写（AI/AO/DI/DO/RTD/TC）、行业标准代码（FT/TT/PT/CV）、API 字段名。

### 6.2.2 技术实现

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| I18N-01 | 后端 i18n：`LANGUAGE_CODE='en-us'`，`USE_I18N=True`，配置 12 种 LANGUAGES，`LocaleMiddleware`，模型 verbose_name 用 `gettext_lazy`。API 通过 `Accept-Language` 头返回对应语言消息。 | Django i18n + locale/*.po 文件。 |
| I18N-02 | 前端 i18n：react-i18next + i18next-browser-languagedetector，`fallbackLng='en'`，按命名空间组织（common/instrumentIndex/wiring/loopDrawing/errors）。 | `useTranslation()` hook + 翻译键 JSON。 |
| I18N-03 | RTL 支持：检测 RTL 语言（ar/he）动态设置 `<html dir="rtl">`；使用 CSS 逻辑属性（margin-inline-start 等）+ tailwindcss-rtl；`useDirection()` hook；导航箭头翻转（部分图标不翻转）；表格列顺序自动反转。 | CSS 逻辑属性 + Tailwind RTL 插件 + useDirection hook。 |
| I18N-04 | 用户语言设置：UserPreference 扩展（language/timezone/date_format/number_format，默认 en）；`GET/PATCH /api/v1/me/preferences/`（与 §15.7 统一，原 `/api/user/preferences/` 写法作废）切换语言立即生效。 | UserPreference 模型 + 偏好 API。 |
| I18N-05 | 语言切换 UI：顶部导航栏右侧语言切换器（下拉列表，选择后立即切换并保存到偏好；未登录用户用浏览器语言或默认英语）。 | React 语言切换组件。 |
| I18N-06 | 日期/数字/货币本地化：按语言格式化（en: MM/DD/YYYY、1,234.56；zh-CN: YYYY-MM-DD；de: 1.234,56）。 | Intl API / i18next 格式化器。 |

### 6.2.3 翻译键命名规范

按层级命名空间组织，示例 `common.json`：`app.{name,tagline}`、`nav.{dashboard,instruments,wiring,...}`、`actions.{save,cancel,delete,edit,create,export,import,search,filter,refresh}`、`messages.{saveSuccess,deleteConfirm,unsavedChanges}`、`errors.{required,invalidFormat,networkError,unauthorized}`。各语言提供对应翻译文件。

## 6.3 并发控制 (Concurrency Control)

> **策略**：记录级锁定（悲观锁）+ 乐观锁双重保护。乐观锁部分（`row_version` + 409 CONFLICT）已在 §4.1.3 定义，本节补充记录级锁定与实时同步。

### 6.3.1 EditLock 模型（记录级锁定）

| 字段 | 说明 |
|------|------|
| id | BigAutoField |
| content_type | FK → ContentType（通用外键） |
| object_id | 被锁定对象 ID |
| locked_by | FK → User（锁定者） |
| locked_at | 锁定时间 |
| expires_at | 过期时间（默认 30 分钟） |
| lock_type | 锁定类型（EDIT / REVIEW / APPROVE） |

约束：`(content_type, object_id)` 唯一约束。

### 6.3.2 功能需求

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| CC-01 | 锁定流程：用户点击"编辑"→ 后端检查是否已锁定（已锁定返回锁定者与剩余时间，前端显示只读/等待解锁；未锁定则创建锁定记录返回编辑权限）→ 保存或取消时释放锁定 → 30 分钟无操作自动释放。 | `POST /api/v1/locks/acquire/`、`/release/`、`/extend/`（心跳）、`GET /api/v1/locks/status/`。 |
| CC-02 | 前端锁定 UI：锁定状态指示器（🔒+锁定者名称）、只读模式提示、等待解锁/请求解锁通知、心跳机制（每 5 分钟自动延长）、页面关闭/切换时自动释放。 | React 锁定状态组件 + 心跳定时器。 |
| CC-03 | 批量编辑锁定：尝试锁定所有选中记录；部分已被锁定时提示"以下记录正在被他人编辑，将跳过：…"，用户确认后仅编辑可锁定记录。 | 批量锁定 + 跳过策略。 |
| CC-04 | 实时状态同步（WebSocket）：锁定状态实时广播、解锁通知、在线用户列表、数据变更通知。消息类型：`lock.acquired`、`lock.released`、`record.updated`、`user.viewing`。 | Django Channels + WebSocket。 |
| CC-05 | 锁定超时与清理：默认 30 分钟，心跳 5 分钟；Celery 定时任务每分钟清理过期锁定；管理员可强制解锁。 | Celery Beat 定时清理任务。 |

## 6.4 P&ID 数据集成

> **目的**：从 P&ID（管道仪表流程图）软件导入仪表数据，避免重复录入，保持数据一致性。本节补充模块7(INT)/模块8(IFC)未覆盖的 P&ID 专用集成能力。

### 6.4.1 支持的 P&ID 软件和格式

| P&ID 软件 | 数据格式 | 集成方式 | 优先级 |
|-----------|---------|---------|--------|
| SmartPlant P&ID | XML / Oracle DB | XML 导入 / DB 直连 | 高 |
| AVEVA E3D/PDMS | XML / Oracle DB | XML 导入 | 高 |
| AutoCAD P&ID | XML / DWG | XML 导入 | 中 |
| Bentley OpenPlant | XML / iModel | XML 导入 | 中 |
| 通用格式 | Excel / CSV | 文件导入 | 高 |
| 标准格式 | ISO 15926 / DEXPI | XML 导入 | 中 |

### 6.4.2 数据模型

- **ImportJob（导入任务）**：`project, source_type(Excel/XML/Database/API), source_system(SmartPlant/AVEVA/AutoCAD/Generic), file, connection_config(加密), status(Pending/Processing/Completed/Failed), total/imported/failed_records, error_log, created_by, created_at, completed_at`。
- **ImportMapping（字段映射）**：`organization, name, source_system, entity_type(Tag/Loop/Cable/JunctionBox), field_mappings(JSON: source→target+transform，如 lookup/float), default_values, validation_rules`。
- **ImportRecord（导入记录，支持增量同步）**：`import_job, source_id, entity_type, entity_id, source_data(JSON), status(Created/Updated/Skipped/Failed), error_message, created_at`。
- **DatabaseConnection（数据库直连）**：`organization, name, db_type, host, port, database, username(加密), password(加密), schema, query_template, is_active, last_sync_at`。支持 Oracle(cx_Oracle)/SQL Server(pyodbc)/PostgreSQL(psycopg2)。
- **SyncSchedule（增量同步计划）**：`connection, project, mapping, schedule(Cron), is_active, last_run_at, next_run_at`。

### 6.4.3 功能需求

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| PID-01 | 导入流程：选择数据源（上传文件/配置 DB 连接）→ 选择/创建字段映射（预设或拖拽自定义）→ 数据预览验证（前 100 条预览、必填校验、外键引用检查、标记重复/格式错误）→ 冲突策略（跳过已存在/覆盖更新/合并更新仅更新非空）→ 异步执行（每批 100 条、每批一事务、实时进度）→ 导入报告（成功/失败统计、错误详情下载、导入日志）。 | Celery 异步 + 批处理 + 事务控制 + WebSocket 进度。 |
| PID-02 | 导入 API：`POST /api/v1/integration/pid/imports/`（project_id/source_type/source_system/mapping_id/conflict_strategy/file）返回 job_id；`GET /api/v1/integration/pid/imports/{job_id}/` 查询进度；`GET /api/v1/integration/pid/imports/{job_id}/errors/` 获取逐行错误；`POST /api/v1/integration/pid/imports/{job_id}/retry/` 重试指定记录。 | ImportJobViewSet。 |
| PID-03 | XML 导入格式：支持 SmartPlant P&ID XML（PlantModel/Instruments/Instrument 结构）；支持 DEXPI(ISO 15926) 1.3+（导入 Instrument/ProcessConnection/SignalLine/Equipment Association）。 | defusedxml 安全解析 + 格式适配器。 |
| PID-04 | 数据库直连与增量同步：基于时间戳（WHERE modified_date > last_sync）或变更标记（WHERE sync_flag='N'）增量同步；Celery Beat 定时自动同步 + 手动触发。 | DatabaseConnection + SyncSchedule + Celery Beat。 |
| PID-05 | 数据导出到 P&ID：`POST /api/v1/integration/pid/exports/`（format: Excel/XML/CSV，target_system，entity_types，filters）返回 download_url。 | 多格式导出服务。 |
| PID-06 | 数据一致性检查：`GET /api/v1/integration/pid/imports/compare/`（project_id/connection_id）对比 P&ID 源数据与本地数据，返回 summary（total_source/total_local/new_in_source/modified/deleted_in_source）和 differences 列表，支持双向同步建议。 | 一致性比对服务。 |

## 6.5 非功能性需求

### 6.5.1 性能要求

| 指标 | 要求 |
|------|------|
| API 响应时间 | < 200ms (P95) |
| 页面加载时间 | < 3s（首次），< 1s（后续） |
| 并发用户数 | 支持 100+ 并发 |
| 数据量支持 | 单项目 100,000+ 位号 |

> 与 §4.8.2/§4.9 的性能验收标准互补：§4.8.2/§4.9 给出大数据量（20万 Tags/5万 Loop/50万 Wire）下的列表首屏 ≤2s、复杂查询预览 ≤5s 的具体验收口径，本表为通用基线指标。

### 6.5.2 安全要求

- HTTPS 强制；JWT Token 安全存储；CORS 配置。
- SQL 注入防护（Django ORM）；XSS 防护（React 默认）；CSRF 防护。
- 敏感数据加密存储（如数据库连接凭据、密码）。

### 6.5.3 可用性要求

- 响应式设计（桌面优先）；浏览器支持 Chrome/Firefox/Edge（最新两个版本）。
- 错误处理与用户友好提示；危险操作（删除等）需操作确认。

### 6.5.4 可维护性要求

- 代码注释和文档；API 文档自动生成（OpenAPI）；日志记录。
- 单元测试覆盖率 **≥ 80%**（采用 §4.9 DoD 的更高标准，覆盖 SPECIFICATION.md §6.4 的 70% 基线；关键服务类 ≥ 90%）。

### 6.5.5 API 与前端口径协调

- **JWT Token 时效**：以模块7 INT-01 的 access 30 分钟 / refresh 7 天为准（SPECIFICATION.md §4.2 的 60 分钟为早期稿，统一采用 30 分钟）。
- **Accept-Language 头**：API 须支持 `Accept-Language` 头返回对应语言的消息（见 §6.2.1）。
- **前端项目级路由与层级导航**：前端采用项目级路由（`/projects/{project_no}/...`）与层级导航树（ProjectTenant → Client → Site → Plant → Area → Unit），并提供上下文选择器（Ctrl+1~5 切换层级）与数据过滤联动；此与 §4.6 路由表互补，§4.6 为模块功能路由的扁平视图，本项为多租户项目作用域下的层级视图。
- **核心快捷键**：Ctrl+N 新建、Ctrl+S 保存、Ctrl+F 搜索、Ctrl+1~5 切换层级上下文、F2 编辑、Delete 删除、Ctrl+D 复制。

---

## 6.6 交付物模板库 (Deliverable Template Library) 【决策 D12 · 新增】

**目标**：所有最终 C&I 交付物（Instrument Schedule / I/O Schedule / Instrument Datasheets / Cable Schedule / Cable Termination Schedule / Loop Diagrams 等）的**版式由模板决定，数据由系统提供**；用户可**导入自有模板**（Excel/Word/SVG/DXF 图框）、在线定制、存入模板库并按组织/项目共享与版本化。数据库始终是唯一事实源（§4.5 第 6 条），模板只决定"怎么呈现"。

### 6.6.1 标准 C&I 交付物目录（DeliverableType 注册表）

| type_code | 交付物 | 数据来源模块 | 默认模板格式 | 内置设计器 / 现有关联规格 |
|-----------|--------|-------------|-------------|------------------------|
| INSTRUMENT_INDEX | Instrument Index / Instrument Schedule | IDX（Component + IOAllocation + PD 摘要 + Procurement） | XLSX（列模板）| IDX-13 浏览器视图即列模板（预置 `Instrument Schedule` 视图）；本节 XLSX 模板负责版式（表头分组/冻结/页眉页脚/修订块） |
| IO_SCHEDULE | I/O Schedule / I/O List（按 PCS/SIS/柜位/卡件） | IDX TagIOAllocation + WIR CSTag | XLSX | IDX-15(a) 汇总 + 明细 |
| INSTRUMENT_DATASHEET | Instrument Datasheets（**项目方现行 WSP 模板库：71 份 XLSX，一技术类型一模板**） | SPEC + PD + CALC + PipingClass | **导入 XLSX（主路径，SPEC-16）**；内置表单（SPEC-01/02）为备选 | 模板按 `InstrumentTechnologyType.default_spec_form_id` 选取；绑定清单见 `wsp_template_bindings.json`；版次用途见 §4.4.11 |
| BID_TABULATION | 回标对比表 / 技术偏差表（Bid Tabulation & Technical Deviation List） | SPEC-14 `vendor_value`/`compliance` | XLSX | 按询价包或按 Tag 生成：要求值 \| 各供应商回标 \| 偏差标记；订货前技术评标依据 |
| PROCESS_DATA_SHEET | Process Data Sheets | PD | XLSX / PDF | PD-07 |
| CABLE_SCHEDULE | Cable Schedule（电缆清册：编号/类型/规格/起止/长度/敷设） | WIR Cable/Wire + Panel | XLSX | WIR 报告；SPEL 导出（INT-06）为数据接口，本项为文档 |
| CABLE_TERMINATION | Cable Termination Schedule / JB Termination（电缆端接表：芯线-端子-信号） | WIR WireTerminal/Terminal | XLSX | WIR 报告 |
| PANEL_TERMINATION | Panel / Marshalling Termination Schedule | WIR | XLSX | WIR 报告 |
| LOOP_DIAGRAM | Loop Diagrams | LOOP | SVG 图框模板 + 宏绑定（M11） | M11 宏 `@{field}` 即绑定语法；图框/标题栏为可导入模板 |
| WIRING_DIAGRAM | Panel / JB Wiring Diagrams | WIR / LOOP 渲染引擎 | SVG 图框 | 同上 |
| HOOKUP_DRAWING | Hook-Up Drawings + BOM | HU | SVG 图框 + XLSX（BOM） | M12 图纸模板 |
| DIMENSIONAL_DATA_SHEET | Dimensional Data / Outline | DDP | XLSX + SVG 轮廓 | M9 `dim_outline_templates` |
| SIF_REGISTER | SIF Register / SIF 元件清单 / C&E 设备侧 | SIF（§2.4） | XLSX | IDX-20 |
| CALC_REPORT | Sizing / IS / Thermowell 计算报告 | CALC | DOCX / PDF | CALC-13 等 |
| COST_SUMMARY | Cost Summary / Long-Lead Items | Procurement（§2.5） | XLSX | IDX-21 |
| CHANGE_SUMMARY | Change Summary / Revision Comparison | DOC / §6.1 | XLSX / PDF | DOC-06、VC-05 |
| BOM_MATERIAL | Material Take-Off | HU | XLSX | HU BOM |

DeliverableType 为系统注册表（可由 Administrator 追加自定义类型，指向某 Item Type 或 EDE 查询作为数据源）。

### 6.6.2 数据模型

**DeliverableTemplate**

| 字段 | 数据类型与约束 | 说明 |
|------|---------------|------|
| id | BigAutoField, PK | |
| deliverable_type | ForeignKey → DeliverableType | 交付物类型 |
| code / name / description | | 模板代码（scope 内唯一）/ 名称 / 说明 |
| format | CharField, choices | XLSX / DOCX / SVG / DXF / HTML / PDF_FORM |
| source | CharField, choices | SYSTEM（内置）/ IMPORTED（用户上传）/ DESIGNED（内置设计器产出，如 SPEC-01/02、IDX-13 视图） |
| file_asset_id | ForeignKey → FileAsset, nullable | 模板文件（IMPORTED/SYSTEM） |
| designer_config | JSONField, nullable | DESIGNED 模板的配置（引用 SpecForm id / browser_view id / SVG 布局） |
| binding_manifest | JSONField | 解析出的占位符清单与绑定校验结果 `[{placeholder, path, item_type, field, status: bound\|unbound\|invalid}]` |
| data_source | JSONField | `{root_item_type, query: <EDE Query DSL 或 saved_query_id>, ordering, grouping}`；列表类交付物必填 |
| page_setup | JSONField | 纸张/方向/页眉页脚/标题栏字段映射（项目号、图号、版次、日期、绘/校/审） |
| scope | CharField, choices | ORGANIZATION（组织级，全部项目可见）/ PROJECT（本租户） |
| version / status | CharField(max=10) / choices | 版本；Draft / Published / Deprecated |
| is_default | BooleanField | 该 deliverable_type 在该 scope 内的默认模板（每 scope 每类型唯一） |
| preview_asset_id | ForeignKey → FileAsset, nullable | 用示例数据渲染的预览 |
| created_at/by, updated_at/by, row_version | | 按 §4.1.1 |

**TemplateRenderJob**：`template_id, target_selection{ids 或 query}, revision_id(GlobalRevision), output_format, status(§4.2.4), output_file_asset_id, render_log, rendered_at/by`——每次生成交付物的记录，输出文件进 FileAsset 并可挂到 DOC Package。

### 6.6.3 占位符与绑定语法（统一，跨格式）

- **单值**：`{{tag.cmpnt_name}}`、`{{tag.custom_data.criticality}}`、`{{tag.line.piping_class.moc_grade}}`（点路径沿 FK/反向关系，路径合法性由 ADM-12 字段元数据校验）。
- **格式化**：`{{tag.pd.operating_temperature.max | uom:"degC" | num:1}}`、`{{revision.date | date:"YYYY-MM-DD"}}`。
- **集合**（表格区块）：`{{#each tag.io_allocations as io}} … {{io.control_system}} … {{/each}}`；Excel 中以**命名区域**标记重复行块，Word 中以表格行标记，SVG 中以 `<g data-repeat="…">` 标记。
- **条件**：`{{#if tag.sil_capability}}…{{/if}}`。
- **系统变量**：`{{project.project_no}}`、`{{revision.code}}`、`{{now}}`、`{{user.full_name}}`、`{{page}}/{{pages}}`。
- **【WSP模板】坐标绑定**：Excel 模板可不写占位符，改由绑定清单声明 `{key, label_cell, value_cells{...}, structure}`；渲染器按坐标写值，并据 `placeholder_state`（SPEC-12）输出实值或占位文字（`Vendor to Advise (VTA)` / `To Be Advised (TBA)` / `To be Confirmed` / `Not Applicable`，文字可在项目设置中覆盖）。
- **【WSP模板】版次与审批变量**：`{{issue.rev}}`、`{{issue.purpose}}`、`{{issue.issued_by}}`、`{{issue.issued_date}}`、`{{issue.approved_by}}`、`{{issue.approved_date}}`（映射模板修订块 A/K/D/H/AD/AH 列，见 §4.4.11）。
- **回路图宏兼容**：M11 的 `@{field}` 作为 `{{…}}` 的别名保留，解析优先级不变（Component → Cable → Wire → Panel）。
- **DXF 图框**：以块属性（ATTRIB tag 名）作为占位符名；渲染为 SVG/PDF 时映射到 `page_setup` 标题栏字段。

### 6.6.4 功能需求

| ID | 功能需求描述 | Web技术实现建议 |
|----|-------------|----------------|
| **DTL-01** | **模板库管理**：按交付物类型浏览模板（组织级/项目级分组、版本、默认标记、预览图）；新建（上传导入 / 从内置设计器另存 / 复制系统模板）、发布、设默认、弃用；按项目选择"本项目默认模板集"。 | `DeliverableTemplateViewSet` + FileAsset。 |
| **DTL-02** | **用户模板导入向导**：上传 XLSX/DOCX/SVG/DXF → 系统解析占位符（Excel：`{{}}` 文本、命名区域、**以及单元格坐标绑定表**；Word：docxtpl 语法；SVG：文本节点与 `data-*`；DXF：块属性）→ 逐个显示绑定状态，未绑定项可在字段选择器（ADM-12 schema，含自定义字段）中点选或输入路径 → 选择数据源（Item Type + 可选保存的 EDE 查询）→ 用 §4.8.1 种子或当前项目任一记录**即时预览渲染** → 通过后发布。校验规则：占位符路径必须解析到已注册字段；集合块必须绑定到一对多关系。<br>**【V2.1 增强·WSP模板】坐标绑定与骨架复用（必备，非可选）**：实务中既有模板的命名区域常已失效。WSP 模板库实测：**71/71 份的字段级命名区域均不可用作绑定锚点**——`_PID_NO`/`PreviousData` 在 71 份中 100% 为 `#REF!`，`RevList` 70/70、`_service` 62/62 为 `#REF!`；`_tag_no`/`_DOC_NAME`/`_REQ_NO`/`_P_ORDER`/`_HOOKUP`/`Rev`/`RevBy`/`RevDate` 在 62 份中为 `#REF!`，**在另 9 份中虽能解析却指向空单元格或语义错位的单元格**（例如 `_DOC_NAME`→`AB2` 为空，真实文档号在 `AB3`；`_P_ORDER`→`AD7` 取到的是标题文字 `APPROVAL`；`_REQ_NO`→`AD8` 取到的是审批人缩写 `RTB`）——这类「假完好」地址比 `#REF!` 更危险，因为解析器不报错却绑定到错误数据，故**导入向导必须在绑定后做取值抽样校验，不得以「名称可解析」作为通过条件**。唯一可用的名称是 `CurrentData`（69/71 完好，指向 `'Current Data'!$A$1:$AI$<n>`），只能用于**定位数据工作表与数据区范围**，不能用于字段绑定。故导入向导**必须支持纯单元格坐标绑定**，并提供：(a) **骨架档案 `template_skeleton_profile`**——把共享的表头单元格、修订块列、多工况列式定义一次，供同族模板复用，模板仅存差异；(b) **标签扫描辅助绑定**——扫描指定列（如标签 B/S 列、值 I/Z 列）自动生成候选绑定并按 `spec_field_catalog.key` 匹配（含 label 变体表，命中 label 变体即视为同字段）；(c) **批量导入**——一次导入整个文件夹并输出逐份绑定覆盖率报告。 | 解析器：openpyxl / python-docx(docxtpl) / lxml(SVG) / ezdxf(DXF)；预览走同一渲染引擎；骨架档案 + 标签扫描使 71 份模板的绑定工作量降为"一次骨架 + 逐份差异确认"。 |
| **DTL-03** | **渲染引擎映射**：XLSX → openpyxl 模板填充（保留样式、公式、条件格式、数据有效性，重复块行复制）；DOCX → docxtpl；SVG → 占位符替换 + 重复组克隆 + 可选 CairoSVG → PDF；HTML → Jinja2 + WeasyPrint；DXF → ezdxf 填属性后转 SVG/PDF（或直接输出 DXF）。渲染为纯函数：同一模板 + 同一 GlobalRevision 快照 → 相同输出（可重复生成）。 | 引擎注册表 `RenderEngineRegistry` 按 format 分派；重任务走 Celery（§4.2.4）。 |
| **DTL-04** | **交付物生成**：从索引/回路/电缆等列表多选或按查询 → 选模板（默认已选）→ 选 GlobalRevision（默认当前）→ 生成；输出存 FileAsset，记 TemplateRenderJob，可一键加入 DOC Package（DOC-02）并参与 DOC-07 按修订打印。批量 >5 份异步。 | `POST /api/v1/deliverables/render/`。 |
| **DTL-05** | **列模板 ↔ 版式模板协同**：INSTRUMENT_INDEX/IO_SCHEDULE/CABLE_* 等列表类交付物中，**列集合与顺序**取自所选浏览器视图（IDX-13）或模板 `data_source.columns`，**版式**取自 XLSX 模板；两者可独立替换。预置 `IS_TEMPLATE_SCHEDULE.xlsx`：复刻项目方现行 Instrument Schedule 的表头分组、冻结窗格、修订列与页眉，作为默认 INSTRUMENT_INDEX 模板（对应 IFC-10(a) 的反向：导出格式 = 导入格式）。 | 列定义与版式分离；渲染时按列集合动态生成表头组。 |
| **DTL-06** | **图框/标题栏模板**：LOOP_DIAGRAM / WIRING_DIAGRAM / HOOKUP_DRAWING 使用可导入的 SVG/DXF 图框（A3/A4 等），标题栏字段绑定 `page_setup`；项目可设默认图框；M11 回路图布局引擎在图框内容区绘制。支持业主 CAD 标准图框直接导入。 | 图框作为 SVG 层叠底图；内容区由 `content_area` 矩形定义。 |
| **DTL-08** | **【V2.1 增强·WSP模板】模板库健康度检查**：对导入的模板库运行一致性与卫生检查并出报告：(a) 同一 `spec_field_catalog.key` 在不同模板中的 **label 措辞不一致**（WSP 实测 38 处）；(b) 同一字段 **单位标注冲突**（实测 `design_pressure` 并存 barg / psig（`LIT80`）/ mbarg（`PDT12`），`vapour_pressure` 并存 barg / mbara（`DET45`）——属实质工程风险：表单单位与软件内部单位不符时，填入的数值会差一个换算系数，如 barg↔psig 约 14.5 倍）；(c) 拼写错误；(d) **残留工作表**（实测 6 份模板含非数据工作表，其中 1 份含前项目封面与真实项目编号——信息残留风险，1 份含 34 个模板副本致文件 1.5 MB）；(e) 技术类型代码重复或与 `technology_types.json` 对不上（实测 21 个缺口）；(f) 工作表名非标准、`SHEET x OF y` 单元格偏移。结果以模板库审计报告输出（样例见 `WSP_TEMPLATE_AUDIT.md`），并对每条给出修复建议；检查为只读，不自动改模板。 | 复用 DBI 的检查项 registry 模式（`template_check_registry`），按模板族执行。 <br>**【2026-10-04 实测修正】检查项须含**：(a) 命名区域**三态**判定——`#REF!` / 可解析但取值为空或为标题文字（「假完好」）/ 真完好；仅「可解析」不算通过，必须做取值抽样校验。(b) **跨工作簿外部引用**——KCV50 / QET35 / WT20 三份的下拉源名称（`Instcode`、`IOTYPE`、`Location`、`Suppliedby`、`hazarea`、`digital`）**完好**，但指向 `'[1]Inst Lists'`、`'[1]Instrument Type'`、`'[2]Inst Lists'` 等**外部工作簿**（未随模板库交付）；导入须报缺失依赖并提示改绑系统主数据（`InstrumentTechnologyType` / `InstrumentLocation` / `ResponsibleParty`）。(c) **Excel 4.0 宏表名称（XLM）**——LIT42 / LIT80 / LS40 / LS42 共 4 份的 `Page_No` 定义为 `GET.DOCUMENT(64)` 宏函数而非单元格引用，openpyxl 无法求值且可能触发宏安全提示，导入须剥离并由渲染引擎 `page_setup` 分页逻辑接管。 |
| **DTL-07** | **模板版本与变更**：Published 模板修改自动生成新版本；已生成交付物记录所用模板版本；字段弃用（ADM-13）时影响分析列出引用该字段的模板；模板可导出/导入 `.oitpl`（zip：模板文件 + manifest.json + preview）在组织/项目间迁移。 | 版本表 + 影响分析反向索引。 |

### 6.6.5 权限与 API

权限：Administrator 与 Project Engineer/PM 管理模板库（组织级需 Administrator）；Instrumentation Engineer 可创建/编辑项目级 Draft 模板并生成交付物；其他角色只读与生成。

```
GET/POST          /api/v1/deliverable-types/                        # 交付物类型注册表
GET/POST          /api/v1/deliverable-templates/                    # 模板库（?type=&scope=）
GET/PUT/PATCH     /api/v1/deliverable-templates/{id}/
POST              /api/v1/deliverable-templates/import/             # 上传解析（DTL-02，返回 binding_manifest）
POST              /api/v1/deliverable-templates/{id}/bind/          # 提交占位符绑定
POST              /api/v1/deliverable-templates/{id}/preview/       # 示例渲染
POST              /api/v1/deliverable-templates/{id}/publish/ 、/set-default/ 、/deprecate/
GET               /api/v1/deliverable-templates/{id}/export/        # .oitpl
POST              /api/v1/deliverables/render/                      # 生成交付物（异步，返回 task_id）
GET               /api/v1/deliverables/jobs/ 、/{id}/                # TemplateRenderJob
```

> `GET /api/v1/reports/{type}/`（§5.4.18）保留为**系统默认模板**的快捷入口；其实现改为调用 DTL-04 并使用该类型的默认模板。

---

# 第七部分：AI Agent 交付协议

## 7.1 交付模式总则

1. **任务粒度**：每个 WP 预计 Devin Local 单次会话 ≤ 2 小时可完成。超出者必须拆分。
2. **一 WP 一分支一 PR**：分支命名 `wp/<编号>-<slug>`（如 `wp/01-tenants`）。PR 描述必须引用本部分的 WP 编号和对应 spec 章节号。
3. **验收命令是完成定义**：WP 的"完成"以 §7.3 验证协议中全部命令通过为准，而非 agent 自述完成。**验证命令必须由机制兜底执行（Claude Code hooks / CI），不得仅信任任何 agent 的回报**——历史上 Devin Local 曾偶发跳过验证步骤，该教训固化为本条，对任何 agent 一体适用。
4. **spec 是唯一事实来源**：实现与 spec 冲突时，停止并提出问题，不得擅自变更 spec 语义。发现 spec 内部矛盾时记录到 `docs/OPEN_QUESTIONS.md`。
5. **vibe coding 边界**：仅允许在【L 级】WP（见 §7.2 风险分级）内自由迭代；【H 级】WP 必须严格按 spec 条目逐项实现并先写测试。

## 7.2 工作包分解（WBS）

风险分级：**H**（高风险：算法/资金级正确性/跨模块传播，先写测试向量）、**M**（中）、**L**(低风险：CRUD/UI 为主，可 vibe coding)。
依赖顺序与 §4.11、§5.3 一致：先基础层，禁止跳到图形模块。

| WP | 名称 | 范围（spec 引用） | 风险 | 关键交付物 | 依赖 |
|----|------|------------------|------|-----------|------|
| WP-00 | 仓库脚手架 | §4.10 目录、§5.1 技术栈 | L | monorepo、docker-compose（PG+Redis+Django+Vite）、CI 骨架、pre-commit（ruff/mypy/eslint） | — |
| WP-01 | 多租户基座 | §15.1、§4.1.4、§4.1.12 | **H** | django-tenants 配置（SHARED_APPS/TENANT_APPS）、ProjectTenant、X-Project-ID 中间件、`TenantBaseModel`/`ProjectScopedModel` 抽象类、migrate_schemas 冒烟 | WP-00 |
| WP-01A | URL 前缀迁移（决策 D1/D2） | SPECIFICATION.md §4.2.1、§4.12.1 D1/D2、§5.4 | M | 现行 `/api/engineering\|admin\|tenants/*` 一次性迁移至 `/api/v1/*`（无双路径）；认证 `/api/v1/auth/*` 上线 + `/api/token/*` 废弃别名（附 Deprecation/Sunset 头，OpenAPI 标 deprecated）；重新生成 OpenAPI → 前端 client 重建 → axios baseURL 与 Vite 代理更新；全量 V1–V6 回归。**豁免**：`/admin/`、`/api/docs\|redoc\|schema/`。**纪律**：纯路由迁移，禁止夹带任何功能改动，diff 只允许出现 urls.py/路由注册/生成物/前端配置 | WP-01 |
| WP-02 | 系统管理/RBAC | §15.2–15.6、**§15.8 数据模型定制（D10）**、§4.3 权限矩阵 | M | 7 个预设系统角色 × 5 级等级（决策 D5，种子数据迁移）、User/TaskForce、对象级 Unit 权限、命名规则 NamingConvention、§15.7/§15.8.4 API、CustomFieldDefinition/CustomTable/FieldConfigOverride 模型与统一 schema 服务（ADM-12） | WP-01A |
| WP-03 | 工厂层级 | §15.4、§5.2 | M | Client/Site/Plant/PlantHierarchy(MPTT)、层级 API、seed（§4.8.1 层级部分） | WP-01 |
| WP-04 | 仪表索引 | 模块2（§2.1–2.3，含 §2.1.1.1 技术类型双层编码、§2.1.1.2 TagIOAllocation、IDX-16~18）、§4.1.6 唯一约束、§15.5.3 equipment 段 | M | CSTag 状态机（§4.4.4）、Tag/Loop CRUD、Profile 自动生成链路（验收场景"创建仪表全链路"） | WP-02, WP-03 |
| WP-04A | SIF 实体（决策 D8） | §2.4（IDX-19/20）、§4.4.8、§4.3 SIF 行、DBI SIF_* 检查项 | M | SafetyInstrumentedFunction/SIFElement 模型与 API、Tag 派生 required_sil/sif_display、SIF 清单报告；**不含 PFDavg 计算** | WP-04（logic_solver_panel FK 在 WP-08 前允许为空） |
| WP-04B | 采购/成本扩展（决策 D7） | §2.5（IDX-21）、§4.4.9、§4.3 Procurement 行 | L | ProcurementInfo 模型/API/状态机、成本汇总与长周期报告、批量状态推进 | WP-04 |
| WP-05 | 过程数据 | 模块3（含 IS模板字段目录、按技术类型的适用性掩码、design_*/operating_* 分组）、§4.4.1 状态机 | M | ProcessDataCase、审批流（验收场景"过程数据审批"）、`process_data_field_catalog.json` 加载、design_* 自 PipingClass 派生 | WP-04, **WP-13A**（决策 D6） |
| WP-06 | 规格书 | 模块4（SPEC-01~16，含 D14 的 §4.1.15 种子）、§4.4.2、**§4.4.11 版次生命周期** | M | SpecSheet、`spec_field_catalog.json` 加载与按技术类型挂字段集、五态占位、DocumentIssue 与三状态机联动、供货文档要求、修订比较（验收场景"规格书修订比较"）、PDF 输出 | WP-04, WP-05（过程数据派生）, WP-13A（PipingClass 派生） |
| WP-06A | WSP 模板库导入与回标（决策 D14） | SPEC-16、SPEC-14、§6.6 DTL-02/DTL-08、`wsp_template_bindings.json` | M | 71 份 WSP 模板注册为 DeliverableTemplate 并绑定（骨架 + 差异）、坐标渲染器、回标导入与 BID_TABULATION 报告、模板库健康度检查 | WP-06, WP-15A, WP-04B（采购状态联动） |
| WP-07 | 计算引擎 | 模块5（§M5-1–M5-5，CALC-01~14）、§4.5 算法规则、§4.5.1 测试向量来源 | **H** | ISA S75.01/ISO 5167/API RP 520/本安/温度套管五套计算服务；**先交测试向量文件再写实现** | WP-05 |
| WP-08 | 接线设计 WIR | 模块10（§10.1 数据模型、WIR-01~25）、§4.4.4 CSTag 状态机、§4.5 信号传播规则 | **H** | 信号传播算法（验收场景"接线信号传播"，含 WIR_SIGNAL_CONFLICT）、Panel/Cable/Terminal 模型 | WP-04 |
| WP-09 | EDE 编辑器 | 模块1（§1.1–1.2） | M | 查询构建器（消费 ADM-12 合并 schema，含自定义字段，D10）、AG Grid 批量编辑（验收场景"EDE 批量编辑"：整体回滚+row_errors） | WP-04 |
| WP-10 | 导入/导出 | 模块8（含 IFC-09~11，D11）、§4.4.5、§4.7 | M | ImportSession 状态机、Dry Run（验收场景"导入 Dry Run"）、Excel 导入模板下载、自动映射、预置 `IS_TEMPLATE_SCHEDULE` Link、大文件异步 | WP-04 |
| WP-11 | 规则引擎 RULE | 模块13（RULE-01~10）、M13 增强(AST/沙箱/性能) | **H** | 规则 DSL/触发器；先测试向量后实现 | WP-04 |
| WP-12 | 回路图 LOOP | 模块11（LOOP-01~10）、M11 增强(坐标系/SVG schema) | M | SVG/Canvas 回路图生成 | WP-08 |
| WP-13A | PipingClass 主表（决策 D6） | §9.2、DDP-11~13、§4.4.7 | M | PipingClass CRUD/审批/升版、Excel 导入（复用 WP-10 Dry Run 或先以直接导入过渡）、Line.piping_class FK、设计条件派生 Service、DBI 检查项 `DDP_LINE_SUPERSEDED_PIPING_CLASS`/`PD_DESIGN_COND_DRIFT` | WP-03 |
| WP-13B | DDP 尺寸数据 + Hook-Up（决策 D6） | 模块9（§9.0 数据模型、DDP-01~10，除 §9.2）、§4.4.10、模块12（§12.1、HU-01~08） | L | 尺寸组模板、过程连接、SVG 轮廓、Hook-Up 及物料表 | WP-04 |
| WP-14 | 文档管理 + DBI | 模块6、模块14（DBI-01~05、§14.2 检查项 registry）、§4.4.6 | M | 文档库、IntegrityCheck 状态机 | WP-04 |
| WP-15 | Part 6 能力 | §6.1–6.4 | M | 版本控制、i18n（12 语言/RTL）、EditLock 并发、P&ID/DEXPI 集成 | WP-05, WP-06 |
| WP-15A | 交付物模板库（决策 D12） | §6.6（DTL-01~07）、§4.3 模板库行 | M | DeliverableType/DeliverableTemplate/TemplateRenderJob、导入向导（XLSX/DOCX/SVG/DXF 解析）、渲染引擎注册表、预置 `IS_TEMPLATE_SCHEDULE.xlsx` 与默认图框、`/api/v1/reports/{type}/` 切换到模板渲染 | WP-06, WP-09, WP-12 |
| WP-16 | 集成接口 | 模块7、SPEL 导出 | M | SP Adapter/SPEL 电缆导出 | WP-08 |
| WP-17 | 性能与 E2E 收口 | §4.8.2 性能行、§4.9 DoD 6–8 | **H** | 20万 Tag 数据生成器、E2E 全链路、性能达标报告 | 全部 |

## 7.3 任务级验证协议（每个 WP 必须全绿）

验证命令 V1–V6 以仓库根目录 **`AGENTS.md`「验证协议 V1–V6」** 为唯一事实来源（含实际的 `uv run` 前缀、Docker 端口 5433/6380、seed 命令名），本文不再复制命令清单，避免双源漂移。要点约束保持不变：

- 涉及模型的 WP 必跑 V1（migrate_schemas 冒烟 + seed）；涉及 API 的必跑 V4；触前端的必跑 V5；**V6 租户隔离回归每个 WP 都跑**。
- H 级 WP 的服务类测试覆盖率 ≥ 90%，其余 ≥ 80%。
- 完成定义以命令实际输出为准，agent 自述不作数；重构后必须重跑测试。

**PR 模板必填项**：WP 编号｜spec 章节引用｜V1–V6 各命令的实际输出摘要｜偏离 spec 之处（应为空）｜新增 OPEN_QUESTIONS。

## 7.4 spec 入库与上下文策略

1. 本项目唯一 spec 为 **`docs/SPECIFICATION.md`**（V2.1 全文 + 本第七部分追加于附录 B 之后；本文所有 §x.x 章节号均指该文件）；八份 SPI 参考文档摘要索引入库为 `docs/REFERENCES.md`。**理由**：Devin 会周期性索引仓库（Devin Search/Wiki），spec 入库即成为其持久上下文，避免每次会话粘贴。
2. 仓库根目录放置 `AGENTS.md`（见配套文件），作为所有 agent（Devin Local、Claude Agent via ACP）的共同行为约束；Devin 旧版 `.windsurfrules` 与新 `.devin/` 格式并存有效，可在 `.windsurfrules` 中仅写一行"Read AGENTS.md first"以免规则双源漂移。
3. 每个 WP 开工时的标准开场提示词模板：
   > 阅读 `AGENTS.md` 与 `docs/SPECIFICATION.md` 第七部分 WP-XX 行及其引用章节。只实现 WP-XX 范围。完成前必须逐条执行 AGENTS.md 验证协议 V1–V6 并贴出输出。禁止修改 `docs/` 与其他 WP 的代码目录（`docs/OPEN_QUESTIONS.md` 追加除外）。

## 7.5 Agent 分工（Devin 看板内）
> 项目方裁决：**Claude Code（经 ACP 接入 Devin Desktop）为唯一实现 agent**，Devin Local 不参与实现。风险分级（§7.2 的 H/M/L）不再用于 agent 路由，仅保留其对测试先行（H 级先交测试向量）与覆盖率门槛（AGENTS.md V3）的约束作用。

| 职责 | 承担者 | 说明 |
|------|--------|------|
| 全部 WP 实现（WP-00–17，含 WP-01A） | **Claude Code（ACP）** | 在 Devin 看板中派工；每 WP 独立会话，避免上下文污染 |
| 验证协议强制执行 | **Claude Code hooks** | 以 hooks 将 AGENTS.md V1–V6 由"约定"升级为"机制"：PostToolUse hook 在 git commit 后触发 `npx gitnexus analyze`（已配置）；建议增配 Stop/PreCommit hook 强制跑 V2/V3/V6，未过则拒绝收尾 |
| PR 初筛 | Devin Review（Fast） | 订阅已含，作为独立第三方初筛保留——单 agent 模式下更有价值，避免实现者自审 |
| PR 深审 | Claude Code **独立复审会话** | 与实现会话分离（新会话、不共享上下文），以 AGENTS.md 硬性规则 + 对应 spec 章节为审查清单 |
| 最终把关 | 人工（项目方） | H 级 WP 的 PR 必须人工过目后合并 |

**单 agent 模式注意事项**：
1. **任务粒度 ≤2 小时保留**——该约束服务于 PR 可审性与回滚粒度，不是 agent 能力上限，不因换 agent 放宽。
2. **实现与复审必须分会话**：同一上下文里"自己审自己"会继承同样的盲点；Devin Desktop 看板中为复审单开会话卡片（或使用 Claude Code subagent 隔离上下文）。
3. **Devin Local 条款休眠不删除**：本协议与 AGENTS.md 中针对多 agent 的条款保留，未来重新启用 Devin Local 或其他 ACP agent 时即刻生效。


**注意事项：**
- registry.json 的字段名以 docs.devin.ai/desktop/acp 当前版为准（ACP registry spec 仍在演进）；若启动失败，先在终端手跑 `claude-code-acp` 确认适配器本身可用。
- 通过 ACP 运行时，Claude Code 的 hooks/skills 等本机配置（`~/.claude/`、项目 `.claude/`、`CLAUDE.md`）依然生效——建议在项目 `CLAUDE.md` 中同样写入"先读 AGENTS.md"，保持双 agent 规则单源。
- 外部 ACP agent 的操作由该 agent 全权负责，不适用 Devin 的隐私与法律条款；涉密代码请自行评估两侧的数据合规策略。。

---

# 附录

## 附录 A：仪表功能代码（ISA S5.1）

| 代码 | 含义 | 示例 |
|------|------|------|
| F | Flow（流量） | FT, FIC, FV |
| T | Temperature（温度） | TT, TIC, TV |
| P | Pressure（压力） | PT, PIC, PV |
| L | Level（液位） | LT, LIC, LV |
| A | Analysis（分析） | AT, AIC |
| C | Control（控制） | - |
| H | Hand（手动） | HV |
| I | Indicate（指示） | FI, TI, PI |
| S | Safety（安全） | PSV, TSH |

## 附录 C：术语表（Glossary）【V2.1 新增 — agent 必读】

> SPI/仪表工程领域术语，agent 无先验知识时据此理解需求措辞。

| 术语 | 含义 | 本规格中的对应 |
|------|------|---------------|
| Tag / 位号 | 单台仪表的唯一工程标识（如 101-FT-100） | `Component.cmpnt_name`（§2.1.1） |
| Loop / 回路 | 实现一个控制或监测功能的一组仪表（如 FE+FT+FIC+FV 构成流量回路） | `Loop`（IDX-07） |
| Function Code / 功能字母 | ISA S5.1 的测量变量+功能字母（FT=流量变送器） | `ComponentFunctionType`（附录 A/B） |
| Technology Type / 技术类型 | 实现技术（FET50=科里奥利、FE10=孔板） | `InstrumentTechnologyType`（§2.1.1.1） |
| P&ID | 管道仪表流程图，仪表的上游设计依据 | `Drawing` + `pid_revision_checked`（IDX-18） |
| Line / 管线 | 工艺管道，仪表的安装载体，携带过程条件 | `Line`（PD-01） |
| Piping Class / 配管等级 | 按流体服务定义材质、压力等级、设计 T&P 的机械专业主数据 | `PipingClass`（§9.2） |
| Process Data / 过程数据 | 仪表选型所需的工艺参数（压力/温度/流量/密度…） | `ProcessDataCase`（模块3） |
| Case / 工况 | 同一仪表的不同运行场景（正常/开车/停车），各有 Min/Norm/Max | PD-04，Governing Case 唯一 |
| Datasheet / 规格书 | 单台仪表的完整技术规格文档，对外询价用 | `SpecSheetData`（模块4） |
| Cv | 控制阀流通能力系数（ISA 75.01） | CALC-01/02 |
| Choked Flow / 壅塞流 | 压差增大流量不再增加的临界状态 | CALC-02/08 |
| Panel / 面板 | 接线容器统称：接线箱/编组柜/机柜/DCS 柜/设备面板 | `Panel`（§10.1） |
| Junction Box (JB) / 接线箱 | 现场电缆汇集到多芯电缆的中转点 | `panel_category=JunctionBox` |
| Marshalling Rack (MR) / 编组柜 | 现场侧与系统侧端子排之间做跨接的机柜 | `panel_category=MarshalingRack`，WIR-16 |
| Terminal Strip / 端子排 | 面板内的一排接线端子 | `PanelStrip`（§10.1） |
| Terminal / 端子 | 单个接线点（如 1+、1-、1SH） | `PanelStripTerm` |
| Cable Set / 缆组 | 电缆内的一对/三芯组（Pair/Triad/Quad） | `CableSet` |
| Wire / 导线 | 缆组内单根芯线（+/-/Shield） | `Wire` |
| Signal Propagation / 信号传播 | 位号信号沿接线路径自动填充到各导线端子的算法 | WIR-12（H 风险核心算法） |
| Cross Wiring / 跨线 | 编组柜内现场侧↔系统侧端子的对接 | WIR-16 |
| CS Tag | 控制系统内的位号，与现场 Tag 耦合后分配到 I/O 通道 | `ControlSystemTag`（WIR-19/20） |
| Coupling / Assignment | 耦合=Tag↔CS Tag 配对；分配=CS Tag→通道 | §4.4.4 状态机 |
| I/O Channel / 通道 | I/O 卡上的单个输入输出点 | `Channel` |
| Loop Drawing / 回路图 | 一个回路完整接线路径的图纸 | 模块11 |
| Hook-Up / 安装详图 | 仪表现场安装的配管配线详图与物料表 | 模块12 |
| BOM | 物料清单 | HU-06 |
| Intrinsic Safety (IS) / 本安 | 限制回路能量以防危险区点燃的防爆方式 | CALC-11/12，`is_intrinsically_safe` |
| Hazardous Area / 危险区域 | 爆炸性气体分区（Zone 0/1/2 + 气体组 + 温度组） | `AreaClassification`（IDX-02） |
| SIF | 安全仪表功能，实现一个特定安全动作的完整回路 | §2.4.1（IEC 61511） |
| SIL | 安全完整性等级，**SIF 的属性**而非设备属性 | `sil_target`；设备侧为 `sil_capability`（D8） |
| Proof Test / 验证测试 | 检出 SIF 危险未检出失效的周期性测试 | `proof_test_interval_months` |
| Domain（旧术语） | SPI 中的数据域。**本系统已改为 ProjectTenant** | §15.1（勿再使用 Domain） |
| UDF / UDT | 用户自定义字段 / 自定义表 | §15.8 |
| Revision / 修订 | 文档版次（Rev 0/A/IFC…） | §6.1.1 |
| IFC（歧义警告） | 本文件中 **IFC-xx 指导入/导出模块需求 ID**；工程惯用 IFC=Issued For Construction，指文档版次，见 `GlobalRevision.revision_code` | 模块8 vs §6.1.1 |

---

## 附录 B：仪表类型代码

> **【V2.1 增强·IS模板】** 下表为 ISA **功能类型**示例。完整的 **技术类型**代码（291 条，如 FET50/UCV10/KCV20/LET75/QET35，含默认 I/O 与过程数据适用性掩码）以种子文件 `backend/apps/instruments/fixtures/technology_types.json` 交付（决策 D9，已生成），不在本附录逐条列出；两层关系与加载约定见 §2.1.1.1。

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


