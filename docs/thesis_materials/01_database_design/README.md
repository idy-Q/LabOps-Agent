# 毕业设计材料：数据库详细设计与数据字典索引中心

> **所属章节**：毕业设计（论文）第四章 系统设计 -> 4.2 数据库概念结构设计 & 4.3 数据库逻辑结构设计 & 4.4 数据库物理设计与完整性控制  
> **数据底座**：SQLite 3 (支持生产级 ACID 事务、WAL 模式与外键约束) / SQLAlchemy 2.0 ORM Declarative Base  
> **归档位置**：`docs/thesis_materials/01_database_design/`

---

## 一、 文件清单与职责划分

本目录归档了系统全量关系型数据库设计成果，包含物理 DDL 实施脚本与学术级数据字典，供毕业论文写作与答辩直接查阅、引用及排版：

| 文件名称 | 文件格式 | 核心内容与学术定位 | 对应论文章节 |
| :--- | :---: | :--- | :--- |
| [schema.sql](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/01_database_design/schema.sql) | SQL (DDL) | 系统建表 DDL、主外键定义、唯一约束与 B-Tree 索引优化脚本 | 4.4 数据库物理设计 |
| [database_data_dictionary.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/01_database_design/database_data_dictionary.md) | Markdown | 5 张核心业务表的规范数据字典（字段、数据类型、是否可空、默认值、约束、业务语义） | 4.3 数据库逻辑结构设计 |
| [README.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/01_database_design/README.md) | Markdown | 数据库设计总览导航、E-R 实体关系推导、答辩核心学术创新点与写论文复用指南 | 4.2 & 4.3 导航 |

---

## 二、 核心实体与概念结构设计 (E-R 关系映射)

在高校机房智能运维场景中，系统围绕**“设备资产监控 -> 异常感知与规约匹配 -> 智能提单流转 -> 闭环归档 -> 全程审计跟踪”**构建数据闭环，核心实体关系如下：

```text
       ┌──────────────┐                  1:N                  ┌─────────────────┐
       │  用户表       │ ────────────────────────────────────> │   运维工单表     │
       │  (users)     │ (1. 申报人/处置人 creator)             │   (tickets)     │
       └──────┬───────┘                                       └────────┬────────┘
              │                                                        │
              │ 1:N (实名借用绑定)                                       │ N:1 (关联设备)
              ▼                                                        ▼
       ┌──────────────┐                  1:N                  ┌─────────────────┐
       │  设备资产表   │ <──────────────────────────────────── │ 审计日志表       │
       │  (assets)    │     (设备状态变更与指标采集记录)          │ (audit_logs)    │
       └──────────────┘                                       └─────────────────┘
                                                                       ▲
                                                                       │ 1:N (Trace ID 关联)
                                                              ┌────────┴────────┐
                                                              │ 会话与思考链表   │
                                                              │ (chat_history)  │
                                                              └─────────────────┘
```

### 实体间业务逻辑约束
1. **用户与资产 (users -> assets)**：教师（`TEACHER`）和管理员（`ADMIN`）可发起借调，系统强制将借用人绑定为当前登录用户（防冒名机制），学生（`STUDENT`）角色受限；
2. **设备与工单 (assets -> tickets)**：设备发生超温（>40℃）或硬件故障时，ReAct 引擎调用 `create_ticket` 自动生成与 `device_id` 绑定的检修工单；
3. **会话与审计 (chat_history -> audit_logs)**：每一条 ReAct 调度产生唯一的 `trace_id`，将模型思考链（`thought`）与每一次真实工具调用的输入/输出快照在 `audit_logs` 中建立强关联审计追踪。

---

## 三、 五大核心表数据结构与论文字段映射

系统采用 5 张核心数据表支撑全套业务逻辑，论文撰写时可直接将下述内容与 [database_data_dictionary.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/01_database_design/database_data_dictionary.md) 的标准表格插入论文第 4 章：

### 1. 运维工单表 (`tickets`) —— 表 4-1
* **核心字段**：`ticket_no` (唯一编号), `title`, `description`, `priority` (LOW/MEDIUM/HIGH/CRITICAL), `status` (PENDING/PROCESSING/RESOLVED/CLOSED), `device_id`, `creator`
* **状态机设计**：严格遵循 `PENDING -> PROCESSING -> RESOLVED -> CLOSED` 单向确定性状态流转，杜绝逆向跳变。

### 2. 实验设备资产台账表 (`assets`) —— 表 4-2
* **核心字段**：`asset_no` (资产唯一编码), `name`, `category`, `location`, `health_status` (HEALTHY/WARNING/OVERHEAT/OFFLINE), `borrow_status` (AVAILABLE/IN_USE/MAINTENANCE), `borrower`, `specs`
* **生命周期**：支持从设备入库、健康监测、领用借出、检修维护到归还完好的完整生命周期闭环。

### 3. Agent 工具调用审计日志表 (`audit_logs`) —— 表 4-3
* **核心字段**：`trace_id`, `tool_name`, `tool_args`, `tool_result`, `status`, `created_at`
* **🎓 答辩防“套壳”核心论据**：以物理落库的入参快照与执行结果，证明系统并非简单调用 LLM 文本接口，而是手写白盒 ReAct 驱动的真自主 Function Calling 调度系统。

### 4. 会话历史与思考链记录表 (`chat_history`) —— 表 4-4
* **核心字段**：`session_id`, `role` (user/assistant/tool/system), `content`, `thought`, `created_at`
* **学术价值**：完整持久化大语言模型的深度思考过程（Thinking Chain），为可解释性 AI（XAI）在运维领域的落地提供学术论据。

### 5. 系统用户与角色权限表 (`users`) —— 表 4-5
* **核心字段**：`username`, `password_hash`, `real_name`, `role` (ADMIN/TEACHER/STUDENT), `department`, `phone`
* **安全机制**：
  - 加盐哈希安全散列：`SHA-256("labops_secure_salt_2026:" + password)`，杜绝彩虹表碰撞；
  - 超管防提权口令：注册申请 `ADMIN` 必须校验专属动态密令 `admin666`；
  - 借调防冒名约束：借用设备时，系统强制锁定前端当前登录人的真实姓名与所属学院，后端二次硬核防线校验。

---

## 四、 论文第四章“数据库设计”写作指引

在编写毕业论文第 4 章时，建议按如下结构组织：
1. **4.1 总体设计架构**：阐述前后端分离体系与数据持久化层职责；
2. **4.2 数据库概念结构设计**：
   - 绘制实体关系图（E-R 图），展现用户、设备资产、工单、审计日志、会话历史五大实体；
   - 阐述各实体属性定义与联系类型（1:1, 1:N）。
3. **4.3 数据库逻辑结构设计**：
   - 直接复用 [database_data_dictionary.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/01_database_design/database_data_dictionary.md) 中的表 4-1 至表 4-5；
   - 针对字段选型、长度定义与枚举取值做学术合理解释。
4. **4.4 数据库物理实现与完整性控制**：
   - 引用 [schema.sql](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/01_database_design/schema.sql) 的标准建表 DDL；
   - 说明索引规划：为高频查询列（`ticket_no`, `asset_no`, `trace_id`, `username`）建立唯一索引或 B-Tree 辅助索引，大幅降低检索时延；
   - 阐述 SQLite 并发写入超时机制（`timeout=30.0`）与 Docker 命名卷（`labops_data`）数据持久化保障。
