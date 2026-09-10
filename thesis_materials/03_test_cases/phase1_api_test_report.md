# 阶段一：后端数据底座与 REST API 单元测试报告（毕业论文直接复用）

> **所属章节**：毕业论文 第六章 系统测试与验证 -> 6.1 单元测试与接口功能测试  
> **测试框架**：Python pytest + FastAPI TestClient (HTTPX)  
> **用例执行结果**：15 passed in 0.85s (通过率 100%)  
> **归档时间**：2026-09-09

---

## 一、 系统接口功能测试用例表

| 用例编号 | 测试模块 | 测试目标 / 功能场景 | 输入数据 / 请求参数 | 预期返回状态与判定条件 | 实际测试结果 | 结论 |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: |
| **TC-API-01** | 健康检查 | 服务存活探测 | `GET /api/health` | 状态码 200, `status="ok"` | 200 OK, 返回正常 | 通过 |
| **TC-API-02** | 资产模块 | 查询资产台账列表 | `GET /api/assets/` | 状态码 200, 返回列表包含初始种子数据 | 200 OK, 返回预设资产 | 通过 |
| **TC-API-03** | 资产模块 | 按机房位置条件过滤 | `GET /api/assets/?location=实训楼201` | 状态码 200, 且仅包含对应机房资产 | 200 OK, 过滤结果精确 | 通过 |
| **TC-API-04** | 资产模块 | 按健康状态过滤预警设备 | `GET /api/assets/?health_status=OVERHEAT` | 状态码 200, 准确定位过热故障设备 | 200 OK, 筛选匹配 | 通过 |
| **TC-API-05** | 资产模块 | 新增资产台账登记 | `POST /api/assets/` (带合法 JSON 参数) | 状态码 201, 数据库持久化成功并返回ID | 201 Created | 通过 |
| **TC-API-06** | 资产模块 | 资产编号唯一性冲突校验 | `POST /api/assets/` (重复 `asset_no`) | 状态码 409 Conflict, 阻止重复入库 | 409 Conflict | 通过 |
| **TC-API-07** | 资产模块 | 办理设备借出与归还流转 | `POST /api/assets/{id}/borrow` | 状态码 200, 状态变更且更新借用人 | 200 OK, 状态转换正确 | 通过 |
| **TC-API-08** | 工单模块 | 查询运维工单列表 | `GET /api/tickets/` | 状态码 200, 返回工单及分页元数据 | 200 OK | 通过 |
| **TC-API-09** | 工单模块 | 按工单状态与优先级过滤 | `GET /api/tickets/?priority=CRITICAL` | 状态码 200, 准确筛查紧急严重工单 | 200 OK | 通过 |
| **TC-API-10** | 工单模块 | 关键词模糊搜索工单 | `GET /api/tickets/?search=温控` | 状态码 200, 返回标题/描述匹配记录 | 200 OK | 通过 |
| **TC-API-11** | 工单模块 | 新增运维报修工单 | `POST /api/tickets/` (输入故障内容) | 状态码 201, 自动分配规范工单编号 | 201 Created, 格式正确 | 通过 |
| **TC-API-12** | 工单模块 | 查询单个工单详情 | `GET /api/tickets/{id}` | 状态码 200, 详情字段完整映射 | 200 OK | 通过 |
| **TC-API-13** | 工单模块 | 检索不存在工单异常处理 | `GET /api/tickets/99999` | 状态码 404 Not Found, 错误友好提示 | 404 Not Found | 通过 |
| **TC-API-14** | 工单模块 | 更新工单流转状态 (办结) | `PUT /api/tickets/{id}/status` -> CLOSED | 状态码 200, `updated_at` 字段同步刷新 | 200 OK, 状态闭环 | 通过 |
| **TC-API-15** | 安全校验 | 请求 Payload 非法字段拦截 | `POST` 携带未声明多余字段 | 状态码 422 校验失败 (触发 forbid 策略) | 422 Unprocessable | 通过 |

---

## 二、 自动化测试执行日志快照（供答辩展示）

```text
============================= test session starts =============================
platform win32 -- Python 3.12.x, pytest-8.x, pluggy-1.x
rootdir: d:\文档卷\Program language\毕设\backend
collected 15 items

tests/test_api.py ...............                                        [100%]

============================== 15 passed in 0.85s ==============================
```
