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


def test_create_regulation_auto_doc_id(client: TestClient):
    """测试录入新规程 (自动生成 DOC-RAG-XXX 编号、自动语义切块与全栈闭环)"""
    new_reg_payload = {
        "title": "机房微模块UPS蓄电池组充放电维保规范",
        "category": "维保规程",
        "version": "2026版",
        "effective_date": "2026-10-01",
        "content": (
            "# 机房微模块UPS蓄电池组充放电维保规范\n\n"
            "## 第一条 巡检维护周期与测量指标\n"
            "1. 每月必须对所有铅酸蓄电池单体电压进行逐一巡检测量，浮充电压偏差不得超过标称值5%。\n\n"
            "## 第二条 核对性放电安全红线\n"
            "1. 蓄电池组每年实施一次核对性充放电试验，放电深度严格控制在30%~50%安全范围，严禁深度过放导致断电故障。"
        ),
    }

    resp = client.post("/api/regulations", json=new_reg_payload)
    assert resp.status_code == 201
    data = resp.json()

    assert data["doc_id"].startswith("DOC-RAG-")
    assert data["title"] == new_reg_payload["title"]
    assert data["category"] == "维保规程"
    assert data["char_count"] > 50
    assert len(data["chunks"]) >= 2

    # 校验各切块的数据与序号
    first_chunk = data["chunks"][0]
    assert first_chunk["document_id"] == data["doc_id"]
    assert "第一条" in first_chunk["section_title"]
    assert "浮充电压" in first_chunk["chunk_content"]

    # 通过生成的 doc_id 查询单篇详情
    detail_resp = client.get(f"/api/regulations/{data['doc_id']}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["doc_id"] == data["doc_id"]


def test_create_regulation_custom_doc_id(client: TestClient):
    """测试指定自定义 doc_id 录入规程"""
    payload = {
        "doc_id": "DOC-RAG-099",
        "title": "机房网络布线与综合走线架管理条例",
        "category": "用电规范",
        "version": "2026-V2",
        "effective_date": "2026-10-15",
        "content": (
            "## 第一条 强弱电分离与走线规范\n"
            "1. 强电线缆与弱电网线、光纤必须在走线架不同层物理隔离，最小间距不得小于300mm。"
        ),
    }

    resp = client.post("/api/regulations", json=payload)
    assert resp.status_code == 201
    assert resp.json()["doc_id"] == "DOC-RAG-099"


def test_create_regulation_duplicate_id_failure(client: TestClient):
    """测试重复 doc_id 拦截 (HTTP 400)"""
    payload = {
        "doc_id": "DOC-RAG-001",
        "title": "测试重复编号规程",
        "category": "用电规范",
        "effective_date": "2026-10-01",
        "content": "## 第一条 规程内容\n1. 内容测试规范文本",
    }
    resp = client.post("/api/regulations", json=payload)
    assert resp.status_code == 400
    assert "已存在" in resp.json()["detail"]


def test_create_regulation_duplicate_title_failure(client: TestClient):
    """测试重复标题拦截 (HTTP 400)"""
    payload = {
        "title": "用电安全与高功耗设备接入管理规范",
        "category": "用电规范",
        "effective_date": "2026-10-01",
        "content": "## 第一条 规程内容\n1. 内容测试规范文本",
    }
    resp = client.post("/api/regulations", json=payload)
    assert resp.status_code == 400
    assert "已存在" in resp.json()["detail"]


def test_create_regulation_instant_rag_search(client: TestClient):
    """测试新规程录入后 ChromaDB / 向量引擎即刻生效支持语义检索"""
    payload = {
        "title": "数据中心机房液冷冷却液更换操作规程",
        "category": "维保规程",
        "effective_date": "2026-11-01",
        "content": (
            "## 第一条 浸没式冷却液电导率红线\n"
            "1. 浸没式氟化液与合成油电导率必须低于10uS/cm，一旦超标必须在24小时内启动在线离子交换树脂净化。"
        ),
    }
    create_resp = client.post("/api/regulations", json=payload)
    assert create_resp.status_code == 201
    created_doc = create_resp.json()

    # 立即发起语义检索
    search_resp = client.post(
        "/api/regulations/search",
        json={"query": "浸没式冷却液电导率必须低于多少", "top_k": 3},
    )
    assert search_resp.status_code == 200
    results = search_resp.json()
    assert len(results) >= 1

    # 验证命中新规程
    matched = [r for r in results if created_doc["doc_id"] == r.get("doc_id") or "冷却液" in r["content"]]
    assert len(matched) >= 1
    assert "浸没式" in matched[0]["content"]
    assert matched[0]["doc_title"] == payload["title"]


def test_update_regulation_metadata_success(client: TestClient):
    """测试更新规程元数据 (标题、版本、分类、生效日期)"""
    # 1. 录入一份测试规程
    create_payload = {
        "title": "测试可更新元数据的临时规程",
        "category": "用电规范",
        "version": "2026-v1.0",
        "effective_date": "2026-05-01",
        "content": "## 第一条 临时条款\n1. 本条为用于测试更新元数据的规程正文。",
    }
    c_resp = client.post("/api/regulations", json=create_payload)
    assert c_resp.status_code == 201
    created = c_resp.json()
    doc_id = created["doc_id"]

    # 2. 发起 PUT 更新
    update_payload = {
        "title": "已更名的测试规程-修订版",
        "category": "应急条例",
        "version": "2026-v2.0",
        "effective_date": "2026-06-01",
    }
    u_resp = client.put(f"/api/regulations/{doc_id}", json=update_payload)
    assert u_resp.status_code == 200
    updated = u_resp.json()

    assert updated["doc_id"] == doc_id
    assert updated["title"] == "已更名的测试规程-修订版"
    assert updated["category"] == "应急条例"
    assert updated["version"] == "2026-v2.0"
    assert updated["effective_date"] == "2026-06-01"
    # 原有切块保持不变
    assert updated["chunk_count"] == created["chunk_count"]


def test_update_regulation_content_and_rechunk(client: TestClient):
    """测试更新规程正文 content，触发自动重新切块与向量知识库即刻同步"""
    # 1. 创建待更新正文的规程
    create_payload = {
        "title": "测试正文切块更新的规程",
        "category": "维保规程",
        "effective_date": "2026-07-01",
        "content": "## 第一条 初始条款A\n1. 初始条文内容A。\n\n## 第二条 初始条款B\n1. 初始条文内容B。",
    }
    c_resp = client.post("/api/regulations", json=create_payload)
    assert c_resp.status_code == 201
    doc_id = c_resp.json()["doc_id"]

    # 2. 更新正文为全新内容 (含有专属高辨识度关键词)
    new_content = (
        "## 第一条 超导磁悬浮轴承风机极限制动\n"
        "1. 当超导磁悬浮风机转速超过每分钟12000转且出现偏心谐波时，必须在3秒内实施电磁阻尼制动锁死。"
    )
    u_resp = client.put(
        f"/api/regulations/{doc_id}",
        json={"content": new_content},
    )
    assert u_resp.status_code == 200
    updated = u_resp.json()
    assert updated["char_count"] == len(new_content)
    assert len(updated["chunks"]) >= 1
    assert "超导磁悬浮" in updated["chunks"][0]["section_title"]

    # 3. 验证即刻支持 RAG 语义检索
    s_resp = client.post(
        "/api/regulations/search",
        json={"query": "超导磁悬浮风机电磁阻尼制动", "top_k": 3},
    )
    assert s_resp.status_code == 200
    s_results = s_resp.json()
    assert any("超导磁悬浮" in r["content"] for r in s_results)


def test_update_regulation_errors(client: TestClient):
    """测试更新规程的 404 与标题冲突 400 校验"""
    # 404 不存在
    resp_404 = client.put(
        "/api/regulations/DOC-RAG-9999",
        json={"title": "不存在的规程"},
    )
    assert resp_404.status_code == 404

    # 400 标题与已有规程冲突
    resp_400 = client.put(
        "/api/regulations/DOC-RAG-001",
        json={"title": "空调故障与超温应急预案"}, # DOC-RAG-002 的标题
    )
    assert resp_400.status_code == 400
    assert "已被其他文档使用" in resp_400.json()["detail"]


def test_delete_regulation_cascade_and_vector_cleanup(client: TestClient):
    """测试下线废止规程：级联删除数据库切块并从向量库中完全移除"""
    # 1. 录入一份专门用于测试删除的规程
    create_payload = {
        "title": "待废止下线的机房微模块旧制度",
        "category": "用电规范",
        "effective_date": "2026-08-01",
        "content": (
            "## 第一条 微模块旧电缆排布规范\n"
            "1. 历史专用电缆架设废止条款微模块专用测试标志X99。"
        ),
    }
    c_resp = client.post("/api/regulations", json=create_payload)
    assert c_resp.status_code == 201
    doc_id = c_resp.json()["doc_id"]

    # 验证此时可检索到
    s_before = client.post(
        "/api/regulations/search",
        json={"query": "废止条款微模块专用测试标志X99", "top_k": 5},
    )
    assert s_before.status_code == 200
    assert any("X99" in r["content"] for r in s_before.json())

    # 2. 执行 DELETE
    d_resp = client.delete(f"/api/regulations/{doc_id}")
    assert d_resp.status_code == 200
    del_data = d_resp.json()
    assert del_data["doc_id"] == doc_id
    assert "已成功废止" in del_data["message"]

    # 3. 再次获取详情应返回 404
    get_resp = client.get(f"/api/regulations/{doc_id}")
    assert get_resp.status_code == 404

    # 4. 检索应不再包含该废止规程切块
    s_after = client.post(
        "/api/regulations/search",
        json={"query": "废止条款微模块专用测试标志X99", "top_k": 5},
    )
    assert s_after.status_code == 200
    assert not any("X99" in r["content"] for r in s_after.json())

    # 5. 重复删除同一 doc_id 返回 404
    d_again = client.delete(f"/api/regulations/{doc_id}")
    assert d_again.status_code == 404


def test_update_regulation_same_title_allowed(client: TestClient):
    """测试更新规程时若传递自身当前标题不应误报标题冲突"""
    resp = client.put(
        "/api/regulations/DOC-RAG-001",
        json={"title": "用电安全与高功耗设备接入管理规范", "version": "2026-V3"},
    )
    assert resp.status_code == 200
    assert resp.json()["version"] == "2026-V3"


def test_update_regulation_validation_edges(client: TestClient):
    """测试更新规程入参校验边界 (extra='forbid', content 长度过短等)"""
    # 1. content 小于 10 字符拦截
    resp_short = client.put(
        "/api/regulations/DOC-RAG-001",
        json={"content": "短文本"},
    )
    assert resp_short.status_code == 422

    # 2. extra 字段拦截
    resp_extra = client.put(
        "/api/regulations/DOC-RAG-001",
        json={"unknown_field": "val"},
    )
    assert resp_extra.status_code == 422

