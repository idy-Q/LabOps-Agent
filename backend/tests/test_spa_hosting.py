"""便携整合包与生产模式下前端静态文件托管及 SPA 路由回退专项测试"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse


def test_spa_hosting_routing(tmp_path: Path):
    """测试当前端静态目录存在时，FastAPI 具备同时服务 API、Vue SPA 及安全隔离的能力"""
    # 模拟外部敏感文件
    secret_file = tmp_path / "secret.env"
    secret_file.write_text("SECRET_KEY=123456", encoding="utf-8")

    # 模拟前端编译产物目录
    web_dir = tmp_path / "web"
    assets_dir = web_dir / "assets"
    assets_dir.mkdir(parents=True)

    index_html = web_dir / "index.html"
    index_html.write_text("<!DOCTYPE html><html><body><div id='app'>LabOps Web</div></body></html>", encoding="utf-8")

    sample_js = assets_dir / "app.bundle.js"
    sample_js.write_text("console.log('LabOps Bundle');", encoding="utf-8")

    # 构建模拟应用
    app = FastAPI()

    # 注册 API 路由
    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    # 注册 SPA 托管逻辑 (与 main.py 完全一致)
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_spa_root():
        return FileResponse(web_dir / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa_fallback(full_path: str):
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")

        try:
            target_path = (web_dir / full_path).resolve()
            web_root = web_dir.resolve()
            if target_path.is_file() and target_path.is_relative_to(web_root):
                return FileResponse(target_path)
        except (ValueError, Exception):
            pass

        return FileResponse(web_dir / "index.html")

    client = TestClient(app)

    # 1. API 路由正常且优先响应
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

    # 2. 未匹配的 API 路由必须返回 404 JSON，严禁误回退 index.html
    resp_missing_api = client.get("/api/unknown_endpoint")
    assert resp_missing_api.status_code == 404
    assert resp_missing_api.json() == {"detail": "API route not found"}

    # 3. 根路径正确返回 index.html
    resp = client.get("/")
    assert resp.status_code == 200
    assert "LabOps Web" in resp.text

    # 4. 静态资源直接访问
    resp = client.get("/assets/app.bundle.js")
    assert resp.status_code == 200
    assert "LabOps Bundle" in resp.text

    # 5. SPA 任意子页面刷新回退至 index.html
    resp = client.get("/dashboard/devices/201")
    assert resp.status_code == 200
    assert "LabOps Web" in resp.text

    # 6. 路径穿越安全防护：不可读取 web 目录外的敏感文件
    resp_traversal = client.get("/assets/../secret.env")
    assert "SECRET_KEY" not in resp_traversal.text
