"""规章规程知识中心数据模式 (Pydantic Schemas)"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class KnowledgeChunkItem(BaseModel):
    """规程分块数据模型"""

    id: int
    chunk_id: str = Field(..., description="切块唯一编号，如 CHK-001-01")
    document_id: str = Field(..., description="所属源文档ID，如 DOC-RAG-001")
    chunk_index: int = Field(..., description="分块顺序序号")
    section_title: str = Field(..., description="所属章节条款层级标题")
    chunk_content: str = Field(..., description="切块文本原始内容")
    token_count: int = Field(default=0, description="Token预估数")
    chroma_id: Optional[str] = Field(default=None, description="底层Chroma向量索引ID")
    created_at: Optional[datetime] = Field(default=None, description="入库切块时间")

    model_config = ConfigDict(from_attributes=True)


class RegulationDocumentItem(BaseModel):
    """规程文档摘要模型"""

    id: int
    doc_id: str = Field(..., description="文档唯一编号，如 DOC-RAG-001")
    title: str = Field(..., description="规章规程文档标题")
    version: str = Field(default="2026版", description="规程版本号")
    category: str = Field(..., description="业务分类：用电规范 / 应急条例 / 维保规程")
    file_hash: str = Field(..., description="文档SHA256哈希指纹")
    char_count: int = Field(default=0, description="全文字符总数")
    effective_date: str = Field(..., description="规程颁布实施日期")
    created_at: Optional[datetime] = Field(default=None, description="入库时间")
    chunk_count: int = Field(default=0, description="下属语义切块数量")

    model_config = ConfigDict(from_attributes=True)


class RegulationDetailResponse(RegulationDocumentItem):
    """规程文档详情模型 (含下属全部切块列表)"""

    chunks: List[KnowledgeChunkItem] = Field(default_factory=list, description="全部切块明细列表")


class RegulationCreateRequest(BaseModel):
    """录入新增规章规程请求数据模式"""

    doc_id: Optional[str] = Field(
        default=None,
        description="文档唯一编号，若不传则自动按 DOC-RAG-XXX 格式递增生成",
    )
    title: str = Field(..., min_length=2, max_length=128, description="规章规程文档标题")
    category: str = Field(..., min_length=1, max_length=64, description="业务分类：用电规范 / 应急条例 / 维保规程 等")
    version: str = Field(default="2026版", max_length=32, description="规程版本号")
    effective_date: str = Field(..., min_length=4, max_length=32, description="规程颁布实施日期，如 2026-09-01")
    content: str = Field(..., min_length=10, description="规程正文 Markdown 内容")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RegulationUpdateRequest(BaseModel):
    """规章规程修改请求数据模式 (字段均为可选，若传递 content 则触发重新切块与向量索引更新)"""

    title: Optional[str] = Field(default=None, min_length=2, max_length=128, description="规章规程文档标题")
    category: Optional[str] = Field(default=None, min_length=1, max_length=64, description="业务分类：用电规范 / 应急条例 / 维保规程 等")
    version: Optional[str] = Field(default=None, max_length=32, description="规程版本号")
    effective_date: Optional[str] = Field(default=None, min_length=4, max_length=32, description="规程颁布实施日期，如 2026-09-01")
    content: Optional[str] = Field(default=None, min_length=10, description="规程正文 Markdown 内容（若修改将自动重新切块与向量更新）")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RegulationSearchRequest(BaseModel):
    """规程语义检索请求模型"""

    query: str = Field(..., min_length=1, max_length=500, description="自然语言查询语句或关键词")
    top_k: int = Field(default=5, ge=1, le=20, description="返回最相关切块条目上限")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RegulationSearchResult(BaseModel):
    """规程语义检索结果项"""

    content: str = Field(..., description="匹配的条款切块文本")
    score: float = Field(..., description="余弦相似度原始分值 (0.0 ~ 1.0)")
    score_percent: str = Field(..., description="相似度百分比显示，如 92.5%")
    doc_id: Optional[str] = Field(default=None, description="溯源规程文档ID")
    doc_title: str = Field(..., description="溯源规程文档标题")
    section: str = Field(..., description="溯源章节标题")
    clause: Optional[str] = Field(default=None, description="条款标号")
    source: str = Field(..., description="格式化溯源标签，如 [来源:《用电安全...》第二条]")
    chunk_id: Optional[str] = Field(default=None, description="对应数据库切块ID")
    category: Optional[str] = Field(default=None, description="所属规程业务分类，如用电规范/应急条例/维保规程")


class RegulationsSummaryResponse(BaseModel):
    """规章知识库概览指标"""

    total_documents: int = Field(..., description="在册规章规程总篇数")
    total_chunks: int = Field(..., description="底层语义切块总数量")
    total_chars: int = Field(..., description="全规程总字符量")
    categories: Dict[str, int] = Field(default_factory=dict, description="各业务分类文档分布统计")
    vector_engine: Dict[str, Any] = Field(default_factory=dict, description="双模向量索引引擎运行状态")
