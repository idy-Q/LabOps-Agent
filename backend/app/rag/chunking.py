import re
from typing import List, Dict, Any
from pathlib import Path

class MarkdownChunker:
    """
    基于 Markdown 层级与条款编号的结构化语义切块器
    """
    
    def __init__(self, chunk_size: int = 500):
        self.chunk_size = chunk_size

    def chunk_document(self, file_path: str) -> List[Dict[str, Any]]:
        """
        解析 Markdown 文档并按条款进行切块
        返回格式: [{'doc_name': '...', 'section': '...', 'clause': '...', 'content': '...'}, ...]
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        doc_name = path.stem
        chunks = []
        
        current_section = ""
        current_clause = ""
        current_content = []
        
        def save_chunk():
            if current_content:
                text = "\n".join(current_content).strip()
                if text:
                    chunks.append({
                        "doc_name": doc_name,
                        "section": current_section,
                        "clause": current_clause,
                        "content": text
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
        return chunks
