import pytest
import os
import tempfile
from pathlib import Path
from app.rag.chunking import MarkdownChunker
from app.rag.vector_store import KnowledgeBase, cosine_similarity
from app.agent.react_engine import ReActEngine
from app.tools.regulation_tools import query_regulations, _init_kb, _kb

def test_markdown_chunker_basic():
    chunker = MarkdownChunker()
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md', encoding='utf-8') as f:
        f.write("# 测试文档\n\n## 第一条 目的\n内容1\n1. 条款1\n内容1.1\n")
        tmp_path = f.name
        
    try:
        chunks = chunker.chunk_document(tmp_path)
        assert len(chunks) == 2
        assert chunks[0]["section"] == "第一条 目的"
        assert chunks[0]["clause"] == ""
        assert chunks[1]["section"] == "第一条 目的"
        assert chunks[1]["clause"] == "1. 条款1"
    finally:
        os.unlink(tmp_path)

def test_markdown_chunker_no_section():
    chunker = MarkdownChunker()
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md', encoding='utf-8') as f:
        f.write("无标题内容\n这里是一些文字\n")
        tmp_path = f.name
    try:
        chunks = chunker.chunk_document(tmp_path)
        assert len(chunks) == 1
        assert chunks[0]["section"] == ""
        assert "无标题内容" in chunks[0]["content"]
    finally:
        os.unlink(tmp_path)

def test_markdown_chunker_file_not_found():
    chunker = MarkdownChunker()
    with pytest.raises(FileNotFoundError):
        chunker.chunk_document("not_exist.md")

def test_vector_store_idempotency_and_retrieval():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        kb = KnowledgeBase(persist_directory=tmpdir)
        chunks = [
            {"doc_name": "test1", "section": "sec1", "clause": "", "content": "服务器超温告警，大于40度熔断"},
            {"doc_name": "test2", "section": "sec1", "clause": "", "content": "单机架功耗上限4.5kW"}
        ]
        
        kb.add_documents(chunks)
        kb.add_documents(chunks) # idempotency
        
        results = kb.search("服务器超温度", top_k=1)
        assert len(results) == 1
        assert "40度" in results[0]["content"]

        results2 = kb.search("功耗上限是多少", top_k=1)
        assert len(results2) == 1
        assert "4.5kW" in results2[0]["content"]

def test_vector_store_memory_fallback():
    kb = KnowledgeBase(persist_directory="/invalid_path_to_force_fallback\0")
    kb.use_chroma = False # Force memory mode
    chunks = [
        {"doc_name": "test1", "section": "sec1", "clause": "", "content": "单机架功耗上限4.5kW"}
    ]
    kb.add_documents(chunks)
    kb.add_documents(chunks) # idempotency memory
    
    res = kb.search("功耗", top_k=1)
    assert len(res) == 1
    assert "4.5kW" in res[0]["content"]

def test_cosine_similarity():
    v1 = [1.0, 0.0]
    v2 = [1.0, 0.0]
    assert cosine_similarity(v1, v2) == 1.0
    v3 = [0.0, 1.0]
    assert cosine_similarity(v1, v3) == 0.0
    assert cosine_similarity([0, 0], [1, 1]) == 0.0

def test_regulation_tools_init():
    _init_kb()
    res = query_regulations("不存在的奇葩问题")
    assert isinstance(res, str)

def test_regulation_tools_power():
    _init_kb()
    res2 = query_regulations("单机架功耗上限是多少")
    assert "4.5kW" in res2
    assert "power_safety" in res2

def test_regulation_tools_overheat():
    _init_kb()
    res = query_regulations("空调故障超温怎么办")
    assert "40" in res
    assert "overheat_emergency" in res

def test_regulation_tools_inspection():
    _init_kb()
    res = query_regulations("日常巡检怎么做")
    assert "09:00" in res
    assert "inspection_maintenance" in res

def test_agent_e2e_rag_power():
    engine = ReActEngine(max_steps=5)
    result = engine.run(user_prompt="你好，请问机房单机架功耗上限是多少？")
    assert "4.5kW" in result.content or "query_regulations" in [tc.get("name") for tc in result.tool_calls] or "4.5" in result.content

def test_agent_e2e_rag_overheat():
    engine = ReActEngine(max_steps=5)
    result = engine.run(user_prompt="根据规范，温度超过40度怎么处理？")
    assert "40" in result.content or "query_regulations" in [tc.get("name") for tc in result.tool_calls]

def test_agent_e2e_rag_inspection():
    engine = ReActEngine(max_steps=5)
    result = engine.run(user_prompt="根据制度，机房每天的巡检时间是什么时候？")
    assert "09:00" in result.content or "query_regulations" in [tc.get("name") for tc in result.tool_calls]

def test_agent_e2e_rag_gpu():
    engine = ReActEngine(max_steps=5)
    result = engine.run(user_prompt="GPU卡加装审批流程")
    assert "query_regulations" in [tc.get("name") for tc in result.tool_calls] or "审批" in result.content

def test_agent_e2e_rag_unknown():
    engine = ReActEngine(max_steps=5)
    result = engine.run(user_prompt="查一下规章里面的乱七八糟的东西")
    assert "query_regulations" in [tc.get("name") for tc in result.tool_calls]
