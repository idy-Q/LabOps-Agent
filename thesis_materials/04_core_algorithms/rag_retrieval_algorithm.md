# RAG 语义切块与向量相似度计算原理

## 1. 结构化语义切块算法
常规的按固定长度进行切块（Chunking）容易割裂自然语言的上下文，导致召回的条款不完整。本项目针对机房规章 Markdown 文件格式，设计了基于 DOM 层级的结构化切块。

**算法伪代码：**
```python
def chunk_markdown(file_lines):
    chunks = []
    current_section = ""
    current_clause = ""
    current_content = []
    
    for line in file_lines:
        if line starts with "##":
            save(current_content)
            current_section = line
            current_clause = ""
        elif line starts with number clause ("1. "):
            save(current_content)
            current_clause = line
            current_content.append(line)
        else:
            current_content.append(line)
            
    save(current_content)
    return chunks
```
该算法将保证每一块文本都附带其所属的篇章 `doc_name`、章节 `section`、以及条款编号 `clause`。

## 2. 向量相似度计算 (Cosine Similarity)
由于部署环境的差异，知识库设计了双模高可用：优先使用 ChromaDB 计算，在依赖缺失或环境受限时，自动降级为余弦相似度（Cosine Similarity）内存计算。

余弦相似度计算公式：
$$
\text{similarity}(A, B) = \frac{A \cdot B}{||A|| \times ||B||} = \frac{\sum_{i=1}^{n} A_i \times B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \times \sqrt{\sum_{i=1}^{n} B_i^2}}
$$

**实现原理：**
- $A, B$ 为由 Embedding 模型提取出的文本特征向量；
- 在降级方案中，采用诸如文本长度与简单词频的 Mock Embedding 用于演示；
- 检索时计算 query 与所有库中文档的夹角余弦值，值越接近 1 则语义越相近，排序后截取 Top-K 返回结果。
