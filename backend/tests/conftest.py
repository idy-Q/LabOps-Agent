"""全局 Pytest 测试配置与环境隔离 Fixture"""

import os
import shutil
import tempfile
import pytest

from app.tools import regulation_tools
from app.rag.vector_store import KnowledgeBase


@pytest.fixture(scope="session", autouse=True)
def isolate_test_knowledge_base():
    """测试会话级别隔离向量知识库，避免写入开发/生产 chroma_db 目录导致 Git 状态被写污染"""
    tmp_dir = tempfile.mkdtemp(prefix="labops_test_chroma_")
    test_kb = KnowledgeBase(persist_directory=tmp_dir)
    original_kb = regulation_tools._kb
    original_initialized = regulation_tools._kb_initialized

    regulation_tools._kb = test_kb
    regulation_tools._kb_initialized = False

    yield test_kb

    regulation_tools._kb = original_kb
    regulation_tools._kb_initialized = original_initialized
    shutil.rmtree(tmp_dir, ignore_errors=True)
