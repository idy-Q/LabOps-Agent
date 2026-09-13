"""Agent 智能对话与细粒度 SSE 流式交互路由"""

import json
import logging
from typing import Any, Dict, Generator, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.db.session import get_db, SessionLocal
from app.db.models import ChatHistory
from app.schemas.chat import ChatStreamRequest, ChatHistoryResponse
from app.agent.react_engine import ReActEngine

logger = logging.getLogger(__name__)

router = APIRouter()


def _sse_event_stream(
    prompt: str,
    session_id: Optional[str] = None,
    db: Optional[Session] = None,
    user_role: str = "ADMIN",
    user_name: str = "管理员",
    user_department: Optional[str] = None,
) -> Generator[str, None, None]:
    """生成标准 Server-Sent Events (SSE) 数据流

    事件契约包括：
    - think: 思考过程分块 (thought, step)
    - tool_start: 工具调用启动 (name, args, step)
    - tool_end: 工具调用完毕返回结果 (name, result, step)
    - citation: 机房安全条例溯源依据 (source, section, content, step)
    - ticket_mutation: 实时工单新增/更新突变事件 (action, ticket, ticket_no, step)
    - asset_mutation: 实时资产状态变更突变事件 (action, asset, asset_no, step)
    - content: 助手最终业务回复文本 (text, delta)
    - done: 整个推理周期结束信号 (session_id, trace_id, total_steps)
    - error: 异常错误兜底事件 (message)
    """
    close_db = False
    active_db = db
    if active_db is None:
        active_db = SessionLocal()
        close_db = True

    try:
        engine = ReActEngine()
        for event in engine.stream_run(
            user_prompt=prompt,
            session_id=session_id,
            db=active_db,
            user_role=user_role,
            user_name=user_name,
            user_department=user_department,
        ):
            payload = json.dumps(event, ensure_ascii=False, default=str)
            yield f"data: {payload}\n\n"
    except Exception as exc:
        logger.error("SSE 流式生成异常: %s", str(exc), exc_info=True)
        err_payload = json.dumps(
            {"type": "error", "message": f"处理流式响应时发生内部错误: {str(exc)}"},
            ensure_ascii=False,
        )
        yield f"data: {err_payload}\n\n"
    finally:
        if close_db and active_db is not None:
            active_db.close()


@router.post(
    "/stream",
    summary="Agent 细粒度流式对话 (SSE)",
    description="基于标准 SSE 协议实时分发思考过程、工具调用、规章溯源、业务突变与最终回答",
)
def chat_stream(
    request: ChatStreamRequest,
    db: Session = Depends(get_db),
):
    """接收用户指令并开启 SSE 流式交互通道"""
    if not request.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="对话输入内容不能为空",
        )

    headers = {
        "Content-Type": "text/event-stream; charset=utf-8",
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }

    return StreamingResponse(
        _sse_event_stream(
            prompt=request.prompt,
            session_id=request.session_id,
            db=db,
            user_role=request.user_role or "ADMIN",
            user_name=request.user_name or "管理员",
            user_department=request.user_department,
        ),
        media_type="text/event-stream",
        headers=headers,
    )


@router.get(
    "/history",
    response_model=List[ChatHistoryResponse],
    summary="获取会话消息历史列表",
    description="按会话ID查询或获取系统最新历史记录，按时间顺序排列",
)
def get_chat_history(
    session_id: Optional[str] = Query(default=None, description="指定会话ID过滤"),
    limit: int = Query(default=50, ge=1, le=200, description="返回条目数上限"),
    db: Session = Depends(get_db),
):
    query = db.query(ChatHistory)
    if session_id and session_id.strip():
        records = (
            query.filter(ChatHistory.session_id == session_id.strip())
            .order_by(ChatHistory.created_at.desc(), ChatHistory.id.desc())
            .limit(limit)
            .all()
        )
        return list(reversed(records))

    # 未指定 session_id 时获取最近全局历史记录并按时间升序返回
    records = (
        query.order_by(ChatHistory.created_at.desc(), ChatHistory.id.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(records))


@router.get(
    "/sessions",
    summary="获取历史会话列表概要",
    description="返回系统历史活跃的会话列表及最后一条交互消息",
)
def list_chat_sessions(
    limit: int = Query(default=20, ge=1, le=50, description="最多返回会话数"),
    db: Session = Depends(get_db),
):
    """聚合获取最近会话列表"""
    # 查询所有唯一的 session_id 及对应最新记录
    subq = (
        db.query(
            ChatHistory.session_id,
            func.max(ChatHistory.id).label("max_id"),
            func.max(ChatHistory.created_at).label("last_activity"),
            func.count(ChatHistory.id).label("message_count"),
        )
        .group_by(ChatHistory.session_id)
        .subquery()
    )

    sessions = (
        db.query(
            subq.c.session_id,
            subq.c.last_activity,
            subq.c.message_count,
            ChatHistory.content.label("last_message"),
            ChatHistory.role.label("last_role"),
        )
        .join(ChatHistory, ChatHistory.id == subq.c.max_id)
        .order_by(desc(subq.c.last_activity))
        .limit(limit)
        .all()
    )

    result = []
    for s in sessions:
        result.append(
            {
                "session_id": s.session_id,
                "last_activity": s.last_activity.strftime("%Y-%m-%d %H:%M:%S") if s.last_activity else None,
                "message_count": s.message_count,
                "last_message": (s.last_message[:60] + ("..." if len(s.last_message) > 60 else "")) if s.last_message else "",
                "last_role": s.last_role,
            }
        )

    return {"status": "success", "data": result}
