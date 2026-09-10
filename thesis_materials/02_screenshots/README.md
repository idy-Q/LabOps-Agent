# 阶段一：界面与数据库截图留存指引

> **对应论文**：第五章 系统实现 与 第四章 数据库设计  
> **重要提示**：本目录用于存放高清截图，写毕业论文时直接按文件名插入 Word 即可。

## 当前阶段（阶段 1）建议留存的 2 张截图：

1. **`01_swagger_api_docs.png`**：
   - **操作步骤**：启动后端服务后，浏览器打开 `http://127.0.0.1:8000/docs`。
   - **截取内容**：截取包含 `/api/tickets/`、`/api/assets/` 的完整 FastAPI Swagger UI 界面。
   - **论文用途**：证明前后端分离开发规范及 RESTful API 完备性。

2. **`02_sqlite_database_tables.png`**：
   - **操作步骤**：在 VS Code 中用 `SQLite Viewer` 插件打开 `backend/app/data/labops.db`，或者使用 DBeaver / Navicat 打开。
   - **截取内容**：展示 tickets 表和 assets 表及其字段与初始 5 条数据。
   - **论文用途**：用于第四章数据库物理实现图。
