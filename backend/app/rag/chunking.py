import re
from typing import List, Dict, Any
from pathlib import Path

class MarkdownChunker:
    """
    基于 Markdown 层级与条款编号的结构化语义切块器
    """
    
    def __init__(self, chunk_size: int = 500):
        self.chunk_size = chunk_size

    def chunk_text(self, text: str, doc_name: str = "regulation") -> List[Dict[str, Any]]:
        """
        解析 Markdown 文本内容并按条款进行切块
        返回格式: [{'doc_name': '...', 'section': '...', 'clause': '...', 'content': '...'}, ...]
        """
        lines = text.splitlines(keepends=True)
        chunks = []

        current_section = ""
        current_clause = ""
        current_content = []

        def save_chunk():
            if current_content:
                chunk_str = "\n".join(current_content).strip()
                if chunk_str:
                    chunks.append({
                        "doc_name": doc_name,
                        "section": current_section,
                        "clause": current_clause,
                        "content": chunk_str,
                    })
                current_content.clear()

        for line in lines:
            line_stripped = line.strip()

            # Match ## Section
            if line_stripped.startswith("## "):
                save_chunk()
                current_section = line_stripped[3:].strip()
                current_clause = ""
            # Match 1. Clause
            elif re.match(r"^\d+\.\s", line_stripped):
                save_chunk()
                current_clause = line_stripped
                current_content.append(line_stripped)
            else:
                if line_stripped:
                    if not current_section and line_stripped.startswith("# "):
                        # Title
                        pass
                    else:
                        current_content.append(line_stripped)

        save_chunk()

        # 容错后备兜底：若文档未采用标准二级标题或编号，但存在有效文本内容，生成单一切块以防数据丢失
        if not chunks and text.strip():
            chunks.append({
                "doc_name": doc_name,
                "section": current_section,
                "clause": current_clause,
                "content": text.strip(),
            })

        return chunks

    def chunk_document(self, file_path: str) -> List[Dict[str, Any]]:
        """
        解析 Markdown 文档并按条款进行切块
        返回格式: [{'doc_name': '...', 'section': '...', 'clause': '...', 'content': '...'}, ...]
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        return self.chunk_text(text, doc_name=path.stem)


def chunk_text(text: str, doc_name: str = "regulation") -> List[Dict[str, Any]]:
    """语义切块便捷函数 (供全栈闭环规程动态入库调用)"""
    return MarkdownChunker().chunk_text(text, doc_name=doc_name)
