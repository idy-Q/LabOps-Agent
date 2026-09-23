"""规章规程知识中心 API 自动化测试套件 (Regulations Knowledge Center Tests)

覆盖范围：
1. GET /api/regulations: 规程源文档列表查询、分类与关键词过滤、切块数与字符量统计关联
2. GET /api/regulations/{doc_id}: 单篇规程详情与下属所有切块按序号严格升序加载、404 未找到容错
3. GET /api/regulations/summary: 知识库宏观统计指标、分类分布字典、双模向量引擎状态
4. POST /api/regulations/search: 语义/关键词检索、Top-K 限制、百分比相似度评分与溯源标签校验、输入校验与边界保护
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    """测试客户端 Fixture"""
    with TestClient(app) as c:
        yield c


def test_list_regulations(client: TestClient):
    """测试获取全量在册规程源文档列表"""
    resp = client.get("/api/regulations")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 3

    # 验证预置的三大核心机房安全规程均在册
    doc_ids = [d["doc_id"] for d in data]
    assert "DOC-RAG-001" in doc_ids
    assert "DOC-RAG-002" in doc_ids
    assert "DOC-RAG-003" in doc_ids

    # 校验文档字段结构完整性
    for item in data:
        assert "id" in item
        assert "doc_id" in item
        assert "title" in item
        assert "version" in item
        assert "category" in item
        assert "file_hash" in item
        assert item["char_count"] > 0
        assert item["chunk_count"] > 0
        assert "effective_date" in item


def test_list_regulations_with_filters(client: TestClient):
    """测试按业务分类及关键词过滤规程列表"""
    # 1. 分类过滤: 用电规范
    resp_cat = client.get("/api/regulations", params={"category": "用电规范"})
    assert resp_cat.status_code == 200
    cat_data = resp_cat.json()
    assert len(cat_data) >= 1
    assert all(d["category"] == "用电规范" for d in cat_data)

    # 2. 关键词模糊检索: 巡检
    resp_kw = client.get("/api/regulations", params={"keyword": "巡检"})
    assert resp_kw.status_code == 200
    kw_data = resp_kw.json()
    assert len(kw_data) >= 1
    assert any("DOC-RAG-003" == d["doc_id"] for d in kw_data)

    # 3. 编号精确检索: DOC-RAG-002
    resp_id = client.get("/api/regulations", params={"keyword": "DOC-RAG-002"})
    assert resp_id.status_code == 200
    id_data = resp_id.json()
    assert len(id_data) == 1
    assert id_data[0]["doc_id"] == "DOC-RAG-002"


def test_get_regulation_detail_success(client: TestClient):
    """测试获取单篇规程详情及其下属全部语义切块明细"""
    resp = client.get("/api/regulations/DOC-RAG-001")
    assert resp.status_code == 200
    data = resp.json()

    assert data["doc_id"] == "DOC-RAG-001"
    assert "用电安全" in data["title"]
    assert data["category"] == "用电规范"
    assert "chunks" in data
    assert isinstance(data["chunks"], list)
    assert len(data["chunks"]) > 0

    # 验证切块按 chunk_index 严格升序排列
    indices = [ck["chunk_index"] for ck in data["chunks"]]
    assert indices == sorted(indices)
    assert indices[0] == 1

    # 校验首个切块数据模式
    first_chunk = data["chunks"][0]
    assert first_chunk["chunk_id"].startswith("CHK-")
    assert first_chunk["document_id"] == "DOC-RAG-001"
    assert len(first_chunk["section_title"]) > 0
    assert len(first_chunk["chunk_content"]) > 0
    assert first_chunk["token_count"] > 0


def test_get_regulation_detail_not_found(client: TestClient):
    """测试查询不存在的规程编号时返回 404"""
    resp = client.get("/api/regulations/DOC-NOT-EXIST-999")
    assert resp.status_code == 404
    err_json = resp.json()
    assert "未找到" in err_json["detail"]


def test_get_regulations_summary(client: TestClient):
    """测试获取规章知识库宏观统计与引擎状态"""
    resp = client.get("/api/regulations/summary")
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_documents"] >= 3
    assert data["total_chunks"] >= 3
    assert data["total_chars"] > 0

    # 分类分布校验
    cats = data["categories"]
    assert isinstance(cats, dict)
    assert "用电规范" in cats
    assert "应急条例" in cats
    assert "维保规程" in cats

    # 向量引擎状态校验
    engine_info = data["vector_engine"]
    assert "engine" in engine_info
    assert engine_info["status"] == "ONLINE"
    assert engine_info["collection"] == "regulations"
    assert engine_info["dual_mode_fallback"] is True


def test_search_regulations_power(client: TestClient):
    """测试用电功耗关键词语义检索与百分比评分及溯源标签"""
    payload = {"query": "单机架功耗上限是多少4.5kW", "top_k": 3}
    resp = client.post("/api/regulations/search", json=payload)
    assert resp.status_code == 200
    results = resp.json()

    assert isinstance(results, list)
    assert len(results) >= 1

    top = results[0]
    assert "content" in top
    assert "score" in top
    assert isinstance(top["score"], float)
    assert "score_percent" in top
    assert top["score_percent"].endswith("%")
    assert "doc_title" in top
    assert "source" in top
    assert top["source"].startswith("[来源:")
    # 命中用电管理相关切块
    assert any("4.5kW" in r["content"] or "功耗" in r["content"] for r in results)


def test_search_regulations_overheat(client: TestClient):
    """测试超温应急条例检索"""
    payload = {"query": "机房超温40度熔断应急预案", "top_k": 2}
    resp = client.post("/api/regulations/search", json=payload)
    assert resp.status_code == 200
    results = resp.json()

    assert len(results) >= 1
    assert any("40" in r["content"] or "OVERHEAT" in r["content"] or "超温" in r["content"] for r in results)


def test_search_regulations_borrow_restriction(client: TestClient):
    """测试热词胶囊设备借用与防重复借出拦截语义检索"""
    payload = {"query": "已借出或标注不良的设备系统如何拦截借用？", "top_k": 3}
    resp = client.post("/api/regulations/search", json=payload)
    assert resp.status_code == 200
    results = resp.json()

    assert len(results) >= 1
    top = results[0]
    assert top["score"] > 0.0
    assert "借出" in top["content"] or "不良" in top["content"] or "防重复借出" in top["content"]
    assert top["doc_id"] == "DOC-RAG-003"
    assert top["category"] == "维保规程"


def test_search_regulations_no_match(client: TestClient):
    """测试完全无匹配关键词检索时返回空列表，触发前端空状态友好提示"""
    payload = {"query": "饕餮龘龘", "top_k": 3}
    resp = client.post("/api/regulations/search", json=payload)
    assert resp.status_code == 200
    results = resp.json()
    assert results == []


def test_get_regulation_detail_by_numeric_id(client: TestClient):
    """测试支持通过数字主键 ID 获取规程详情"""
    # 先获取列表第一项的数字主键
    list_resp = client.get("/api/regulations")
    assert list_resp.status_code == 200
    first_item = list_resp.json()[0]
    numeric_id = first_item["id"]

    resp = client.get(f"/api/regulations/{numeric_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == numeric_id
    assert data["doc_id"] == first_item["doc_id"]
    assert len(data["chunks"]) > 0


def test_search_regulations_validation(client: TestClient):
    """测试语义检索请求参数边界与校验拦截"""
    # 1. 空查询词拦截
    resp1 = client.post("/api/regulations/search", json={"query": "   ", "top_k": 3})
    assert resp1.status_code == 422

    # 2. top_k 小于 1 越界拦截
    resp2 = client.post("/api/regulations/search", json={"query": "功耗", "top_k": 0})
    assert resp2.status_code == 422

    # 3. 未定义字段拦截 (extra='forbid')
    resp3 = client.post("/api/regulations/search", json={"query": "功耗", "top_k": 3, "unwanted_field": 123})
    assert resp3.status_code == 422
