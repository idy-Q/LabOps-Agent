import os
from app.tools.registry import tool
from app.rag.chunking import MarkdownChunker
from app.rag.vector_store import KnowledgeBase

from typing import Optional

# Ensure we have a global KB instance for tools to use
# We also initialize chunks to guarantee idempotent setup in this mock environment

_kb: Optional[KnowledgeBase] = None
_kb_initialized = False

def get_kb() -> KnowledgeBase:
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
    return _kb

def _init_kb():
    global _kb, _kb_initialized
    if _kb is None:
        _kb = KnowledgeBase()
    if _kb_initialized:
        return
    chunker = MarkdownChunker()
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "regulations")
    all_chunks = []
    
    if os.path.exists(base_dir):
        for md_file in os.listdir(base_dir):
            if md_file.endswith(".md"):
                file_path = os.path.join(base_dir, md_file)
                chunks = chunker.chunk_document(file_path)
                all_chunks.extend(chunks)
                
    if all_chunks:
        _kb.add_documents(all_chunks)
    _kb_initialized = True

@tool(
    name="query_regulations",
    description="查询机房管理规章制度。当用户询问用电安全、功耗限制、PDU、GPU卡申请、空调故障应急、OVERHEAT、日常巡检、设备借用规则等，应调用此工具。"
)
def query_regulations(query: str, top_k: int = 3) -> str:
    """
    语义检索相关规章内容。
    返回格式化的结果，包含溯源标签。
    """
    _init_kb()
    results = _kb.search(query, top_k=top_k)
    if not results:
        return "未找到相关的规章制度。"
        
    formatted_results = []
    for r in results:
        meta = r["metadata"]
        doc_name = meta.get("doc_name", "未知")
        section = meta.get("section", "")
        clause = meta.get("clause", "")
        # format: [来源:《doc_name》section clause]
        source = f"[来源:《{doc_name}》{section} {clause}]".strip()
        formatted_results.append(f"{source}\n{r['content']}")
        
    return "\n\n".join(formatted_results)
