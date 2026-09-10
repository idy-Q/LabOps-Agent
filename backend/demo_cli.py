"""LabOps-Agent 阶段 2 命令行交互式玩赏体验脚本

运行方式：
    cd backend
    .venv/Scripts/python.exe demo_cli.py

功能：
    在终端直接输入运维指令，体验手写 ReAct 调度引擎的【思考链】、【工具调用】与【数据库状态闭环】！
"""

import sys
from pathlib import Path

# 将 backend 根目录加入路径
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.agent.react_engine import ReActEngine
from app.db.session import SessionLocal


def main():
    print("=" * 65)
    print(" 欢迎体验 LabOps-Agent 高校机房智能运维管家 (阶段 2 体验版)")
    print(" 调度核心：手写白盒 ReAct 状态机 (带本地确定性 Mock 容灾大脑)")
    print("=" * 65)
    print("推荐体验指令：")
    print(" 1. 查询指标：'查询 DEV-SRV-201 的监控指标，若超温请按规范提单'")
    print(" 2. 借用设备：'帮李老师办理 DEV-SRV-202 借出登记'")
    print(" 3. 归还设备：'归还设备 DEV-SRV-202'")
    print(" 4. 查工单表：'查询当前待办工单列表'")
    print(" 5. 推进工单：'将工单 TK-20260901-001 状态更新为 RESOLVED'")
    print(" 6. 退出程序：输入 'exit' 或 'q'")
    print("-" * 65)

    engine = ReActEngine()

    while True:
        try:
            user_input = input("\n[管理员输入] > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n已退出会话。")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            print("感谢体验，会话已结束！")
            break

        print("\n--- [Agent ReAct 调度开始] ---")
        db = SessionLocal()
        try:
            for event in engine.stream_run(user_prompt=user_input, db=db):
                e_type = event.get("type")
                if e_type == "think":
                    print(f"[思考过程] (Step {event.get('step', 1)}): {event.get('thought')}")
                elif e_type == "tool_start":
                    print(f"  └─> [调用工具]: {event.get('name')}(参数={event.get('args')})")
                elif e_type == "tool_end":
                    res = event.get("result")
                    res_status = res.get("status") if isinstance(res, dict) else "ok"
                    print(f"  └─< [执行结果]: [{res_status}] {res}")
                elif e_type == "content":
                    print(f"\n[管家回复]:\n{event.get('text')}")
                elif e_type == "done":
                    print(f"--- [调度结束: 耗时 {event.get('total_steps')} 步, 跟踪ID: {event.get('trace_id')}] ---")
        except Exception as e:
            print(f"[错误] 调度过程发生异常: {e}")
        finally:
            db.close()


if __name__ == "__main__":
    main()
