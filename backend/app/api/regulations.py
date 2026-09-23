"""机房规章规程知识中心与 RAG 检索端点 (Regulations Knowledge Center API)"""

import logging
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.db.models import KnowledgeDocument, KnowledgeChunk
from app.tools.regulation_tools import get_kb, _init_kb
from app.schemas.regulation import (
    RegulationDocumentItem,
    RegulationDetailResponse,
    KnowledgeChunkItem,
    RegulationSearchRequest,
    RegulationSearchResult,
    RegulationsSummaryResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# 预置文件名词干与规程元数据对应表 (加速 RAG 检索逆向溯源映射)
STEM_DOC_MAP: Dict[str, Dict[str, str]] = {
    "power_safety": {
        "doc_id": "DOC-RAG-001",
        "title": "用电安全与高功耗设备接入管理规范",
        "category": "用电规范",
    },
    "overheat_emergency": {
        "doc_id": "DOC-RAG-002",
        "title": "空调故障与超温应急预案",
        "category": "应急条例",
    },
    "inspection_maintenance": {
        "doc_id": "DOC-RAG-003",
        "title": "日常巡检维保与设备全生命周期制度",
        "category": "维保规程",
    },
}


@router.get(
    "",
    response_model=List[RegulationDocumentItem],
    summary="查询规程源文档列表",
    description="获取知识库中全部在册安全规章文档，包含切块数、总字数、颁布版本与生效日期，支持按分类与关键字检索过滤。",
)
def list_regulations(
    category: Optional[str] = Query(default=None, description="按规程分类过滤，如：用电规范、应急条例、维保规程"),
    keyword: Optional[str] = Query(default=None, description="按文档标题或编号关键词搜索"),
    db: Session = Depends(get_db),
):
    query = db.query(KnowledgeDocument)
    if category:
        query = query.filter(KnowledgeDocument.category == category.strip())
    if keyword:
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            (KnowledgeDocument.title.ilike(kw)) | (KnowledgeDocument.doc_id.ilike(kw))
        )

    docs = query.order_by(KnowledgeDocument.doc_id.asc()).all()

    # 统计各文档关联的切块数量
    chunk_counts = dict(
        db.query(KnowledgeChunk.document_id, func.count(KnowledgeChunk.id))
        .group_by(KnowledgeChunk.document_id)
        .all()
    )

    results = []
    for doc in docs:
        results.append(
            RegulationDocumentItem(
                id=doc.id,
                doc_id=doc.doc_id,
                title=doc.title,
                version=doc.version,
                category=doc.category,
                file_hash=doc.file_hash,
                char_count=doc.char_count,
                effective_date=doc.effective_date,
                created_at=doc.created_at,
                chunk_count=chunk_counts.get(doc.doc_id, 0),
            )
        )
    return results


@router.get(
    "/summary",
    response_model=RegulationsSummaryResponse,
    summary="获取规程知识库概览指标",
    description="返回知识库宏观统计（在册文档数、总语义切块数、字符总数、业务分类分布、向量引擎运行模式与健康状态）。",
)
def get_regulations_summary(db: Session = Depends(get_db)):
    docs = db.query(KnowledgeDocument).all()
    total_docs = len(docs)
    total_chunks = db.query(KnowledgeChunk).count()
    total_chars = sum(d.char_count for d in docs)

    categories: Dict[str, int] = {}
    for d in docs:
        categories[d.category] = categories.get(d.category, 0) + 1

    _init_kb()
    kb = get_kb()
    engine_name = "ChromaDB (持久化向量库)" if kb.use_chroma else "In-Memory Cosine (内存余弦引擎)"
    vector_engine = {
        "engine": engine_name,
        "status": "ONLINE",
        "collection": kb.collection_name,
        "dual_mode_fallback": True,
        "persist_dir": kb.persist_directory,
    }

    return RegulationsSummaryResponse(
        total_documents=total_docs,
        total_chunks=total_chunks,
        total_chars=total_chars,
        categories=categories,
        vector_engine=vector_engine,
    )


@router.get(
    "/{doc_id}",
    response_model=RegulationDetailResponse,
    summary="获取单篇规程详情及其下属全部切块列表",
    description="根据 doc_id 精确查询规程元数据，并按 chunk_index 升序加载下属全部语义切块记录 (KnowledgeChunk)。",
)
def get_regulation_detail(doc_id: str, db: Session = Depends(get_db)):
    target_id = doc_id.strip()
    query = db.query(KnowledgeDocument)
    if target_id.isdigit():
        doc = query.filter((KnowledgeDocument.doc_id == target_id) | (KnowledgeDocument.id == int(target_id))).first()
    else:
        doc = query.filter(KnowledgeDocument.doc_id == target_id).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到编号为 '{doc_id}' 的规程源文档",
        )

    chunks = (
        db.query(KnowledgeChunk)
        .filter(KnowledgeChunk.document_id == doc.doc_id)
        .order_by(KnowledgeChunk.chunk_index.asc())
        .all()
    )

    chunk_items = [
        KnowledgeChunkItem(
            id=ck.id,
            chunk_id=ck.chunk_id,
            document_id=ck.document_id,
            chunk_index=ck.chunk_index,
            section_title=ck.section_title,
            chunk_content=ck.chunk_content,
            token_count=ck.token_count,
            chroma_id=ck.chroma_id,
            created_at=ck.created_at,
        )
        for ck in chunks
    ]

    return RegulationDetailResponse(
        id=doc.id,
        doc_id=doc.doc_id,
        title=doc.title,
        version=doc.version,
        category=doc.category,
        file_hash=doc.file_hash,
        char_count=doc.char_count,
        effective_date=doc.effective_date,
        created_at=doc.created_at,
        chunk_count=len(chunk_items),
        chunks=chunk_items,
    )


@router.post(
    "/search",
    response_model=List[RegulationSearchResult],
    summary="规章规程语义/关键词检索",
    description="调用底层双模向量知识库执行 Top-K 语义检索，返回匹配条款切块、余弦相似度、溯源文档及章节标号。",
)
def search_regulations(payload: RegulationSearchRequest, db: Session = Depends(get_db)):
    _init_kb()
    kb = get_kb()
    raw_results = kb.search(payload.query, top_k=payload.top_k)
    if not raw_results:
        return []

    # 预加载数据库切块以匹配 chunk_id 和文档信息
    all_chunks = db.query(KnowledgeChunk).all()
    chunk_map_by_content = {c.chunk_content.strip(): c for c in all_chunks}
    chunk_map_by_chroma = {c.chroma_id: c for c in all_chunks if c.chroma_id}

    # 文档 ID 与标题、业务分类映射
    all_docs = db.query(KnowledgeDocument).all()
    doc_map_by_id = {d.doc_id: d.title for d in all_docs}
    doc_cat_by_id = {d.doc_id: d.category for d in all_docs}

    search_items: List[RegulationSearchResult] = []
    for r in raw_results:
        content = r.get("content", "")
        meta = r.get("metadata", {})
        raw_score = float(r.get("score", 0.0))
        if raw_score <= 0.0:
            continue
        
        # 规整化得分百分比
        score_percent = f"{max(0.0, min(100.0, raw_score * 100)):.1f}%"

        doc_name = meta.get("doc_name", "")
        section = meta.get("section", "")
        clause = meta.get("clause", "")

        # 尝试匹配数据库切块记录
        matched_chunk = chunk_map_by_content.get(content.strip())
        if not matched_chunk and doc_name and section:
            for idx in range(20):
                cid = f"{doc_name}_{section}_{idx}"
                if cid in chunk_map_by_chroma:
                    matched_chunk = chunk_map_by_chroma[cid]
                    break

        # 逆向解析文档编号、标题与业务分类
        doc_id = None
        doc_title = "机房安全管理规程"
        category = None
        chunk_id = None

        if matched_chunk:
            doc_id = matched_chunk.document_id
            doc_title = doc_map_by_id.get(doc_id, doc_title)
            category = doc_cat_by_id.get(doc_id)
            chunk_id = matched_chunk.chunk_id
        elif doc_name in STEM_DOC_MAP:
            mapping = STEM_DOC_MAP[doc_name]
            doc_id = mapping["doc_id"]
            doc_title = mapping["title"]
            category = mapping.get("category")

        # 构建规范化溯源引用标签
        clause_str = f" {clause}" if clause else ""
        source = f"[来源:《{doc_title}》{section}{clause_str}]".strip()

        search_items.append(
            RegulationSearchResult(
                content=content,
                score=round(raw_score, 4),
                score_percent=score_percent,
                doc_id=doc_id,
                doc_title=doc_title,
                section=section,
                clause=clause or None,
                source=source,
                chunk_id=chunk_id,
                category=category,
            )
        )

    return search_items
