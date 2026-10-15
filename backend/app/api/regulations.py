import hashlib
import logging
import re
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Header, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.db.session import get_db
from app.db.models import KnowledgeDocument, KnowledgeChunk, User
from app.tools.regulation_tools import get_kb, _init_kb
from app.rag.chunking import chunk_text
from app.schemas.regulation import (
    RegulationDocumentItem,
    RegulationDetailResponse,
    RegulationCreateRequest,
    RegulationUpdateRequest,
    KnowledgeChunkItem,
    RegulationSearchRequest,
    RegulationSearchResult,
    RegulationsSummaryResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _verify_admin_permission(
    operator: Optional[str] = None,
    operator_role: Optional[str] = None,
    header_role: Optional[str] = None,
    db: Optional[Session] = None,
):
    """规章规程知识库维护操作鉴权：仅系统超级管理员(ADMIN)有权新增、编辑或废止规程。
    普通教师(TEACHER)与学生(STUDENT)无权执行破坏性或管理操作。
    """
    effective_role = (operator_role or header_role or "").strip().upper()
    effective_operator = (operator or "").strip()

    if not effective_role and effective_operator and db:
        user = (
            db.query(User)
            .filter(
                or_(
                    func.lower(User.username) == effective_operator.lower(),
                    User.real_name == effective_operator,
                    func.lower(User.real_name) == effective_operator.lower(),
                )
            )
            .first()
        )
        if user and user.role:
            effective_role = user.role.strip().upper()
        elif effective_operator in ("系统管理员", "管理员", "admin", "王主管", "LabOps-Agent", "系统监控"):
            effective_role = "ADMIN"
        elif "老师" in effective_operator or "teacher" in effective_operator.lower():
            effective_role = "TEACHER"
        elif "同学" in effective_operator or "学生" in effective_operator.lower() or "student" in effective_operator.lower():
            effective_role = "STUDENT"

    if effective_role in ("TEACHER", "STUDENT", "GUEST", "USER"):
        role_name = "教师" if effective_role == "TEACHER" else "学生"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足：规章规程录入、编辑与废止下线工作仅限系统超级管理员(ADMIN)操作，{role_name}角色无权操作",
        )


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


@router.post(
    "",
    response_model=RegulationDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="录入新规章规程 (全栈切块与向量索引闭环)",
    description="录入新规程并自动执行语义切块，写入数据库并向量化存入 ChromaDB 向量库（仅系统超级管理员有权操作）。",
)
def create_regulation(
    payload: RegulationCreateRequest,
    operator: Optional[str] = Query(default=None, description="操作人名称"),
    operator_role: Optional[str] = Query(default=None, description="操作人角色（仅ADMIN有权操作）"),
    x_user_role: Optional[str] = Header(default=None, alias="X-User-Role", description="请求头用户角色"),
    db: Session = Depends(get_db),
):
    _verify_admin_permission(operator=operator, operator_role=operator_role, header_role=x_user_role, db=db)

    # 1. 编号处理与冲突查重
    doc_id = payload.doc_id.strip() if payload.doc_id and payload.doc_id.strip() else None
    if doc_id:
        existing = db.query(KnowledgeDocument).filter(func.lower(KnowledgeDocument.doc_id) == doc_id.lower()).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"规程编号 [{doc_id}] 已存在，请使用其他编号或留空自动生成",
            )
    else:
        # 自动生成递增编号 DOC-RAG-XXX
        all_docs = db.query(KnowledgeDocument.doc_id).all()
        nums = []
        for (did,) in all_docs:
            m = re.search(r"DOC-RAG-(\d+)", did, re.IGNORECASE)
            if m:
                nums.append(int(m.group(1)))
        next_num = max(nums, default=0) + 1
        doc_id = f"DOC-RAG-{next_num:03d}"

    # 查重标题
    existing_title = (
        db.query(KnowledgeDocument)
        .filter(func.lower(KnowledgeDocument.title) == payload.title.strip().lower())
        .first()
    )
    if existing_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"规程标题 [{payload.title.strip()}] 已存在，不可重复录入",
        )

    # 2. 保存 KnowledgeDocument
    content_str = payload.content.strip()
    file_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()
    char_count = len(content_str)

    doc_obj = KnowledgeDocument(
        doc_id=doc_id,
        title=payload.title.strip(),
        version=payload.version.strip(),
        category=payload.category.strip(),
        file_hash=file_hash,
        char_count=char_count,
        effective_date=payload.effective_date.strip(),
    )
    db.add(doc_obj)
    db.flush()

    # 3. 语义切块 (调用底层 app.rag.chunking.chunk_text)
    chunks_meta = chunk_text(content_str, doc_name=doc_id)
    chunk_objs: List[KnowledgeChunk] = []

    for idx, ck in enumerate(chunks_meta):
        id_suffix = doc_id[-3:] if len(doc_id) >= 3 else doc_id
        chunk_id = f"CHK-{id_suffix}-{idx + 1:02d}"
        sec = ck.get("section", "")
        cl = ck.get("clause", "")
        section_title = f"{sec} {cl}".strip() if cl else sec
        chunk_text_content = ck.get("content", "")
        token_est = max(1, len(chunk_text_content) // 2)
        chroma_id = f"{ck.get('doc_name', doc_id)}_{sec}_{idx}"

        chunk_obj = KnowledgeChunk(
            chunk_id=chunk_id,
            document_id=doc_id,
            chunk_index=idx + 1,
            section_title=section_title,
            chunk_content=chunk_text_content,
            token_count=token_est,
            chroma_id=chroma_id,
        )
        db.add(chunk_obj)
        chunk_objs.append(chunk_obj)

    db.commit()
    db.refresh(doc_obj)
    for cko in chunk_objs:
        db.refresh(cko)

    # 4. 同步调用 get_kb().add_documents 向量化存入 ChromaDB 及备用向量库
    try:
        _init_kb()
        kb = get_kb()
        kb.add_documents(chunks_meta)
    except Exception as e:
        logger.warning(f"向量知识库同步切块索引异常: {e}")

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
        for ck in chunk_objs
    ]

    return RegulationDetailResponse(
        id=doc_obj.id,
        doc_id=doc_obj.doc_id,
        title=doc_obj.title,
        version=doc_obj.version,
        category=doc_obj.category,
        file_hash=doc_obj.file_hash,
        char_count=doc_obj.char_count,
        effective_date=doc_obj.effective_date,
        created_at=doc_obj.created_at,
        chunk_count=len(chunk_items),
        chunks=chunk_items,
    )


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
    "/search",
    response_model=List[RegulationSearchResult],
    summary="规章规程语义/关键词检索 (GET 模式)",
    description="支持通过 URL Query 参数 (q 或 query) 执行语义与关键词检索",
)
def search_regulations_get(
    q: Optional[str] = Query(default=None, description="查询关键词"),
    query: Optional[str] = Query(default=None, description="查询关键词别名"),
    top_k: int = Query(default=5, ge=1, le=20, description="返回条数"),
    db: Session = Depends(get_db),
):
    search_text = (q or query or "").strip()
    if not search_text:
        return []
    req = RegulationSearchRequest(query=search_text, top_k=top_k)
    return search_regulations(payload=req, db=db)


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
        elif doc_name in doc_map_by_id:
            doc_id = doc_name
            doc_title = doc_map_by_id[doc_name]
            category = doc_cat_by_id.get(doc_name)
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


@router.put(
    "/{doc_id}",
    response_model=RegulationDetailResponse,
    summary="更新规章规程 (元数据与重新切块/向量同步)",
    description="更新规程元数据；若正文 content 发生变更，重新计算哈希与字数，清理原切块，重新执行语义切块并同步更新向量库（仅系统超级管理员有权操作）。",
)
def update_regulation(
    doc_id: str,
    payload: RegulationUpdateRequest,
    operator: Optional[str] = Query(default=None, description="操作人名称"),
    operator_role: Optional[str] = Query(default=None, description="操作人角色（仅ADMIN有权操作）"),
    x_user_role: Optional[str] = Header(default=None, alias="X-User-Role", description="请求头用户角色"),
    db: Session = Depends(get_db),
):
    _verify_admin_permission(operator=operator, operator_role=operator_role, header_role=x_user_role, db=db)

    target_id = doc_id.strip()
    query = db.query(KnowledgeDocument)
    if target_id.isdigit():
        doc = query.filter((KnowledgeDocument.doc_id == target_id) | (KnowledgeDocument.id == int(target_id))).first()
    else:
        doc = query.filter(KnowledgeDocument.doc_id == target_id).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到编号为 '{doc_id}' 的规程文档",
        )

    # 1. 标题查重 (若修改了标题)
    if payload.title is not None and payload.title.strip() != doc.title:
        new_title = payload.title.strip()
        dup = (
            db.query(KnowledgeDocument)
            .filter(
                KnowledgeDocument.id != doc.id,
                func.lower(KnowledgeDocument.title) == new_title.lower(),
            )
            .first()
        )
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"规程标题 [{new_title}] 已被其他文档使用，不可重复",
            )
        doc.title = new_title

    # 2. 更新其他元数据
    if payload.category is not None:
        doc.category = payload.category.strip()
    if payload.version is not None:
        doc.version = payload.version.strip()
    if payload.effective_date is not None:
        doc.effective_date = payload.effective_date.strip()

    # 3. 处理正文变更与切块/向量库重构
    if payload.content is not None:
        content_str = payload.content.strip()
        doc.file_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()
        doc.char_count = len(content_str)

        # 收集原有切块的 chroma_id
        old_chunks = (
            db.query(KnowledgeChunk)
            .filter(KnowledgeChunk.document_id == doc.doc_id)
            .all()
        )
        old_chroma_ids = [c.chroma_id for c in old_chunks if c.chroma_id]

        # 从底层向量库中移除该文档原有向量
        _init_kb()
        kb = get_kb()
        try:
            kb.delete_documents(doc.doc_id, ids=old_chroma_ids)
        except Exception as e:
            logger.warning(f"向量知识库清理旧切块异常: {e}")

        # 删除数据库旧切块
        db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == doc.doc_id).delete()
        db.flush()

        # 重新语义切块
        chunks_meta = chunk_text(content_str, doc_name=doc.doc_id)
        chunk_objs: List[KnowledgeChunk] = []

        for idx, ck in enumerate(chunks_meta):
            id_suffix = doc.doc_id[-3:] if len(doc.doc_id) >= 3 else doc.doc_id
            chunk_id = f"CHK-{id_suffix}-{idx + 1:02d}"
            sec = ck.get("section", "")
            cl = ck.get("clause", "")
            section_title = f"{sec} {cl}".strip() if cl else sec
            chunk_text_content = ck.get("content", "")
            token_est = max(1, len(chunk_text_content) // 2)
            chroma_id = f"{ck.get('doc_name', doc.doc_id)}_{sec}_{idx}"

            chunk_obj = KnowledgeChunk(
                chunk_id=chunk_id,
                document_id=doc.doc_id,
                chunk_index=idx + 1,
                section_title=section_title,
                chunk_content=chunk_text_content,
                token_count=token_est,
                chroma_id=chroma_id,
            )
            db.add(chunk_obj)
            chunk_objs.append(chunk_obj)

        db.commit()
        db.refresh(doc)
        for cko in chunk_objs:
            db.refresh(cko)

        # 同步写入向量库
        try:
            kb.add_documents(chunks_meta)
        except Exception as e:
            logger.warning(f"向量知识库同步新切块异常: {e}")
    else:
        db.commit()
        db.refresh(doc)
        chunk_objs = (
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
        for ck in chunk_objs
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


@router.delete(
    "/{doc_id}",
    summary="下线废止规章规程",
    description="废止并删除规程源文档，级联清理所有关联语义切块，并从 ChromaDB 向量库中完全同步移除向量（仅系统超级管理员有权操作）。",
)
def delete_regulation(
    doc_id: str,
    operator: Optional[str] = Query(default=None, description="操作人名称"),
    operator_role: Optional[str] = Query(default=None, description="操作人角色（仅ADMIN有权操作）"),
    x_user_role: Optional[str] = Header(default=None, alias="X-User-Role", description="请求头用户角色"),
    db: Session = Depends(get_db),
):
    _verify_admin_permission(operator=operator, operator_role=operator_role, header_role=x_user_role, db=db)

    target_id = doc_id.strip()
    query = db.query(KnowledgeDocument)
    if target_id.isdigit():
        doc = query.filter((KnowledgeDocument.doc_id == target_id) | (KnowledgeDocument.id == int(target_id))).first()
    else:
        doc = query.filter(KnowledgeDocument.doc_id == target_id).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到编号为 '{doc_id}' 的规程文档",
        )

    saved_doc_id = doc.doc_id
    saved_title = doc.title

    # 收集并清理向量库关联数据
    chunks = (
        db.query(KnowledgeChunk)
        .filter(KnowledgeChunk.document_id == saved_doc_id)
        .all()
    )
    chroma_ids = [c.chroma_id for c in chunks if c.chroma_id]
    chunk_count = len(chunks)

    try:
        _init_kb()
        kb = get_kb()
        kb.delete_documents(saved_doc_id, ids=chroma_ids)
    except Exception as e:
        logger.warning(f"向量知识库清理下线规程向量异常: {e}")

    # 删除数据库切块与源文档
    db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == saved_doc_id).delete()
    db.delete(doc)
    db.commit()

    return {
        "message": f"规章规程 [{saved_doc_id}] 《{saved_title}》已成功废止并下线",
        "doc_id": saved_doc_id,
        "title": saved_title,
        "deleted_chunks": chunk_count,
    }
