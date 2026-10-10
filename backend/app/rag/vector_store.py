import os
import json
import math
from typing import List, Dict, Any, Optional
from pathlib import Path
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

from app.config import settings

def _build_default_vocab() -> List[str]:
    import string
    vocab_chars = set(string.ascii_letters + string.digits)
    vocab_chars.update([
        '服', '务', '器', '超', '温', '度', '功', '耗', '4', '5', 'k', 'W', '电', '单', '机', '架',
        '上', '限', '预', '警', '常', '巡', '检', '调', '故', '障', 'P', 'D', 'U', 'G', '批', '处', '理',
        '借', '出', '还', '不', '良', '待', '修', '报', '废', '设', '备', '生', '命', '周', '期', '追', '溯',
        '台', '账', '拦', '截', '空', '调', '℃', '条', '款', '规', '程', '红', '线', '阈', '值', '申', '请',
        '审', '核', '熔', '断', '降', '级', '1', '5', '分', '钟', '3', '0', '双', '路', '关', '机'
    ])
    try:
        reg_dir = settings.DATA_DIR / "regulations"
        if reg_dir.is_dir():
            for md_file in reg_dir.glob("*.md"):
                text = md_file.read_text(encoding="utf-8")
                vocab_chars.update(c for c in text if not c.isspace() and ord(c) > 32)
    except Exception:
        pass
    return sorted(list(vocab_chars))

DEFAULT_VOCAB: List[str] = _build_default_vocab()

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

class KnowledgeBase:
    """
    双模高可用向量知识库引擎
    优先使用 ChromaDB，回退至内存余弦相似度检索
    """
    
    def __init__(self, persist_directory: Optional[str] = None):
        if persist_directory is None:
            persist_directory = str(settings.DATA_DIR / "chroma_db")
        self.persist_directory = str(persist_directory)
        self.use_chroma = CHROMA_AVAILABLE
        self.collection_name = "regulations"
        self.memory_store = []
        
        if self.use_chroma:
            try:
                self.client = chromadb.PersistentClient(path=self.persist_directory)
                self.collection = self.client.get_or_create_collection(name=self.collection_name)
                # 检查现有集合的向量维度是否与当前特征词表一致，不一致则自动重建集合以避免维度冲突
                sample = self.collection.get(include=['embeddings'], limit=1)
                expected_dim = len(DEFAULT_VOCAB)
                if sample and sample.get('embeddings') is not None and len(sample['embeddings']) > 0:
                    existing_dim = len(sample['embeddings'][0])
                    if existing_dim != expected_dim:
                        self.client.delete_collection(name=self.collection_name)
                        self.collection = self.client.create_collection(name=self.collection_name)
            except Exception as e:
                print(f"ChromaDB init failed: {e}, fallback to memory store.")
                self.use_chroma = False
                
    def _mock_embedding(self, text: str) -> List[float]:
        # 基于全域规程词表构建字符频次特征向量与 L2 归一化
        vec = [float(text.count(c)) for c in DEFAULT_VOCAB]
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def add_documents(self, chunks: List[Dict[str, Any]]):
        """幂等加载"""
        if not chunks:
            return
            
        if self.use_chroma:
            try:
                # Check idempotency by checking existing ids
                existing = self.collection.get()
                existing_ids = set(existing['ids']) if existing and 'ids' in existing else set()
                
                ids = []
                documents = []
                metadatas = []
                embeddings = []
                
                for i, chunk in enumerate(chunks):
                    doc_id = f"{chunk['doc_name']}_{chunk['section']}_{i}"
                    if doc_id not in existing_ids:
                        ids.append(doc_id)
                        documents.append(chunk['content'])
                        metadatas.append({
                            "doc_name": chunk['doc_name'],
                            "section": chunk['section'],
                            "clause": chunk.get('clause', '')
                        })
                        embeddings.append(self._mock_embedding(chunk['content']))
                
                if ids:
                    self.collection.add(
                        ids=ids,
                        embeddings=embeddings,
                        documents=documents,
                        metadatas=metadatas
                    )
            except Exception as e:
                print(f"Error adding to ChromaDB: {e}")
                self.use_chroma = False
                self._add_to_memory(chunks)
        else:
            self._add_to_memory(chunks)
            
    def _add_to_memory(self, chunks: List[Dict[str, Any]]):
        # idempotency for memory store
        existing_ids = {doc['id'] for doc in self.memory_store}
        for i, chunk in enumerate(chunks):
            doc_id = f"{chunk['doc_name']}_{chunk['section']}_{i}"
            if doc_id not in existing_ids:
                self.memory_store.append({
                    "id": doc_id,
                    "content": chunk['content'],
                    "metadata": {
                        "doc_name": chunk['doc_name'],
                        "section": chunk['section'],
                        "clause": chunk.get('clause', '')
                    },
                    "embedding": self._mock_embedding(chunk['content'])
                })

    def delete_documents(self, doc_name: str, ids: Optional[List[str]] = None):
        """
        从向量库中同步删除指定文档对应的向量索引切块
        支持按 doc_name 元数据删除及指定具体向量 ID 清理，适配 ChromaDB 与内存引擎
        """
        if self.use_chroma:
            try:
                # 1. 优先尝试直接按 where 过滤删除
                try:
                    self.collection.delete(where={"doc_name": doc_name})
                except Exception:
                    pass

                # 2. 若传入了具体的 chroma_id 列表，批量删除
                if ids:
                    try:
                        self.collection.delete(ids=ids)
                    except Exception:
                        pass

                # 3. 双重保险：检查集合中所有 ID，移除以 doc_name 开头的条目
                try:
                    existing = self.collection.get()
                    if existing and "ids" in existing:
                        matching_ids = []
                        metas = existing.get("metadatas") or []
                        for i, cid in enumerate(existing["ids"]):
                            m = metas[i] if i < len(metas) else None
                            if (m and m.get("doc_name") == doc_name) or cid.startswith(f"{doc_name}_"):
                                matching_ids.append(cid)
                        if matching_ids:
                            self.collection.delete(ids=matching_ids)
                except Exception:
                    pass
            except Exception as e:
                print(f"Error deleting documents from ChromaDB: {e}")

        # 同步清理内存备用引擎
        target_ids_set = set(ids or [])
        self.memory_store = [
            doc for doc in self.memory_store
            if doc.get("metadata", {}).get("doc_name") != doc_name
            and not doc.get("id", "").startswith(f"{doc_name}_")
            and doc.get("id") not in target_ids_set
        ]

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Top-K 检索过滤 (按相关度评分降序排列，仅返回分值 > 0 的有效匹配切块)"""
        query_emb = self._mock_embedding(query)
        if self.use_chroma:
            try:
                col_count = self.collection.count()
                if col_count == 0:
                    return []
                n_results = min(col_count, max(top_k * 3, 10))
                results = self.collection.query(
                    query_embeddings=[query_emb],
                    n_results=n_results
                )
                
                ret = []
                if results and results.get('documents') and results['documents'][0]:
                    docs = results['documents'][0]
                    metas = results['metadatas'][0]
                    for doc, meta in zip(docs, metas):
                        doc_emb = self._mock_embedding(doc)
                        score = cosine_similarity(query_emb, doc_emb)
                        if score > 0.0:
                            ret.append({
                                "content": doc,
                                "metadata": meta,
                                "score": round(score, 4)
                            })
                    ret.sort(key=lambda x: x["score"], reverse=True)
                    return ret[:top_k]
                return ret
            except Exception as e:
                print(f"Error querying ChromaDB: {e}")
                self.use_chroma = False
                
        # Memory fallback search
        scored_docs = []
        for doc in self.memory_store:
            score = cosine_similarity(query_emb, doc["embedding"])
            if score > 0.0:
                scored_docs.append((score, doc))
            
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        ret = []
        for score, doc in scored_docs[:top_k]:
            ret.append({
                "content": doc["content"],
                "metadata": doc["metadata"],
                "score": round(score, 4)
            })
        return ret
