# 毕业设计材料：全生命周期自动化测试用例矩阵与报告索引中心

> **所属章节**：毕业设计（论文）第六章 系统测试与验证 (6.1 ~ 6.6 全节覆盖)  
> **自动化测试框架**：pytest 8.x + TestClient (FastAPI) + SQLite In-Memory / 沙箱隔离隔离池  
> **归档位置**：`docs/thesis_materials/03_test_cases/`  
> **当前状态**：**115 项自动化单测 100% 绿灯全通 (115 passed in < 5.0s)**

---

## 一、 测试报告文件全景导航与论文章节映射

本目录归档了系统研发全生命周期（阶段一至阶段五及安全专项）沉淀的 6 份详实测试报告，论文第 6 章的用例表、断言结果与性能数据均可直接自本中心索引并引用：

| 序号 | 测试报告文件 | 核心验证维度 | 用例数 | 对应毕业论文章节 |
| :---: | :--- | :--- | :---: | :--- |
| 1 | [phase1_api_test_report.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/03_test_cases/phase1_api_test_report.md) | **数据底座与 RESTful 接口**：工单与资产 CRUD、事务原子性、唯一编号碰撞与并发锁 | 15 项 | 6.1 接口与基础数据层测试 |
| 2 | [phase2_agent_test_report.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/03_test_cases/phase2_agent_test_report.md) | **手写 ReAct 引擎与三大工具集**：硬件探针采集、超温闭环提单、状态机单向流转、幻觉清洗 | 24+ 项 | 6.2 Agent 调度引擎与工具链测试 |
| 3 | [phase3_rag_test_report.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/03_test_cases/phase3_rag_test_report.md) | **规章制度 RAG 知识库检索**：层级结构化语义切块、ChromaDB 向量检索、余弦相似度降级引擎 | 15 项 | 6.3 知识库与 RAG 检索召回测试 |
| 4 | [phase4_frontend_sse_test_report.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/03_test_cases/phase4_frontend_sse_test_report.md) | **前端 SSE 流式穿透与全双工联动**：分词流式吐出、工具卡片动画、大盘脉冲刷新、深浅色无闪烁切换 | 12 项 | 6.4 前端流式交互与协同联动测试 |
| 5 | [auth_and_rbac_test_report.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/03_test_cases/auth_and_rbac_test_report.md) | **身份认证与 RBAC 权限防冒名**：SHA-256 加盐防撞库、借调强制实名只读绑定、学生借机前端置灰+后端硬拦截 | 16 项 | 6.5 系统认证安全与权限控制测试 |
| 6 | [phase5_deployment_and_acceptance_report.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/03_test_cases/phase5_deployment_and_acceptance_report.md) | **Docker 容器化、系统集成与封板验收**：多阶段镜像构建、Nginx 动静分离、数据持久卷安全、双轨启动自适应 | 10 项 | 6.6 系统集成、容器化部署与验收测试 |

---

## 二、 全系统 115 项自动化单测套件分布矩阵

后端测试代码统一置于 `backend/tests/` 目录下，执行 `pytest backend/tests/ -q` 即可触发全量测试，通过率 100%：

```text
============================= test session starts =============================
platform win32 -- Python 3.11.8, pytest-8.3.5
rootdir: backend
configfile: pytest.ini
testpaths: tests
collected 115 items

tests/test_api.py ...............                                        [ 13%]
tests/test_auth.py ................                                      [ 27%]
tests/test_phase4_api.py ............                                    [ 37%]
tests/test_rag.py ...............                                        [ 50%]
tests/test_react_engine.py ..................................             [ 79%]
tests/test_tools.py ........................                             [100%]

============================= 115 passed in 4.75s =============================
```

### 测试套件与功能覆盖矩阵

| 测试文件 | 用例数 | 关键测试点与学术防伪要件 |
| :--- | :---: | :--- |
| **`tests/test_api.py`** | 15 项 | 工单增删改查 REST 语义合规、工单唯一流水号 `TK-` 规则防碰撞、资产台账分类/状态过滤查询、SQLAlchemy 事务原子性与失败自动回滚。 |
| **`tests/test_tools.py`** | 24 项 | 硬件探针温度异常阈值触发机制（>40℃）、设备借还防重复借出冲突防御、模型幻觉入参自适应容错清洗、工具执行循环引用安全阻断。 |
| **`tests/test_rag.py`** | 15 项 | Markdown 标题语义分块与重叠窗口划分、ChromaDB 向量检索幂等性、无网络/纯内存余弦相似度保底降级算法、Top-K 规约召回溯源校验。 |
| **`tests/test_react_engine.py`** | 33 项 | 手写白盒 ReAct 状态机循环（Think -> Act -> Observe -> Finish）、超温主动提单自主决策流、最大步数限制（防止无限死循环）、学生口语越权拦截、实名借用绑定校验。 |
| **`tests/test_phase4_api.py`** | 12 项 | SSE 流式长连接标准事件分发（`think` 思考帧、`tool_start` 执行帧、`tool_end` 结果帧、`citation` 溯源帧、`mutation` 状态帧）、前端多轮会话持久化与上下文追踪。 |
| **`tests/test_auth.py`** | 16 项 | `SHA-256` 加盐哈希加密不可逆性测试、大小写敏感性用户名清洗、管理员专属激活口令 `admin666` 校验防越权提权、Token 失效安全阻断。 |
| **全系统总计** | **115 项** | **115 项自动化单测全通过，用例覆盖率高，无已知致命漏洞** |

---

## 三、 毕业论文第六章“系统测试与分析”撰写指南

在撰写毕业论文第 6 章时，建议按照软件测试工程标准划分以下 6 个小节进行排版：

1. **6.1 测试目标与测试环境搭建**：
   - 介绍测试硬件环境、操作系统、Python 3.11、Node.js 20、pytest 框架及 SQLite 独立测试沙箱设计；
2. **6.2 接口与基础数据层功能测试 (对应 `test_api.py`)**：
   - 展示工单 CRUD、资产台账查询测试用例表及实际测试截图；
3. **6.3 垂直工具链与 ReAct 智能调度测试 (对应 `test_tools.py` + `test_react_engine.py`)**：
   - 重点论述“设备超温 -> 自动告警 -> 自主调用 `create_ticket` 闭环”的测试流程；
   - 重点说明 ReAct 状态机防死循环与模型参数幻觉清洗机制的鲁棒性；
4. **6.4 RAG 知识库检索召回率与准确性测试 (对应 `test_rag.py`)**：
   - 呈现 Markdown 分块准确率与 ChromaDB / 内存余弦相似度召回测试数据；
5. **6.5 身份认证安全与 RBAC 权限测试 (对应 `test_auth.py`)**：
   - 呈现加盐哈希防撞库实验结果、超管激活口令防御拦截率、借调防冒名闭环测试记录；
6. **6.6 系统综合集成与全链路性能评估 (对应 `phase5_deployment_and_acceptance_report.md`)**：
   - 汇总 115 项用例执行耗时 (< 5s)；
   - 展现前端秒级打包构建 (< 1s) 与 Gzip 体积压缩效率；
   - 展现 Docker 容器化编排验证与双轨自适应启动实测成果。
