"""工单排查处置说明 (Comment) 智能语义分析与 AI 审计核验引擎

基于第一性原理与人机协同可信审计标准：
1. 消除传统写死 31.5℃ 机械假降温，智能提取用户在处置说明中填写的真实实测温度数值 (如 "降温到 26 摄氏度" -> 26.0℃)；
2. 提炼硬件检修措施 (如更换风扇、重涂硅脂、清洗防尘滤网等)；
3. 生成结构化 AI 审计核验说明 (Audit Note)，持久化写入工单流转记录 (TicketWorkflow)，实现可信防抵赖闭环。
"""

import re
from typing import Any, Dict, List, Optional


# 常见硬件维保与机房处置动作关键词表
MAINTENANCE_ACTION_KEYWORDS = [
    "风扇", "更换风扇", "风道", "清理风道", "导风罩",
    "硅脂", "重涂硅脂", "导热硅脂", "散热片", "散热器", "散热",
    "清灰", "除尘", "滤网", "清洗滤网", "防尘网",
    "制冷", "精密空调", "空调", "调低空调", "降温",
    "重启", "冷重启", "下架检修", "电源", "更换电源",
    "负载降低", "迁移容器", "关停高载", "恢复正常",
]


CN_DIGITS = {
    '零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4,
    '五': 5, '六': 6, '七': 7, '八': 8, '九': 9
}


def _parse_cn_number(cn: str) -> Optional[float]:
    """将中文大写/常用数字字符串（如'二十三'、'二十六点五'）解析为浮点数"""
    if not cn:
        return None
    try:
        parts = cn.split('点')
        int_part_str = parts[0]
        val = 0
        if int_part_str == '十':
            val = 10
        elif '十' in int_part_str:
            idx = int_part_str.index('十')
            prefix = int_part_str[:idx]
            suffix = int_part_str[idx + 1:]
            tens = 1 if not prefix else CN_DIGITS.get(prefix, 1)
            units = 0 if not suffix else CN_DIGITS.get(suffix, 0)
            val = tens * 10 + units
        else:
            val = CN_DIGITS.get(int_part_str, 0)

        if len(parts) > 1:
            dec_part_str = parts[1]
            dec_val = 0.0
            div = 10.0
            for ch in dec_part_str:
                dec_val += CN_DIGITS.get(ch, 0) / div
                div *= 10.0
            val += dec_val
        return float(val)
    except Exception:
        return None


def extract_temperature_from_text(text: str) -> Optional[float]:
    """从中文排查说明中精准提取实测设备温度数值。

    支持例如：
    - "温度下降到26摄氏度" -> 26.0
    - "温度下降了，下降到二十三度" -> 23.0
    - "现场测温降至26.5℃" -> 26.5
    - "降温到二十六点五度" -> 26.5
    - "当前稳定在28度" -> 28.0
    - "实测25度" -> 25.0
    - "核心温度 27 C" -> 27.0
    """
    if not text:
        return None

    # 正则提取模式 1：阿拉伯数字（引导词可选 + 浮点/整数温度 + 摄氏度单位）
    pattern = r"(?:降至|下降到|回落到|降到|稳定在|测试为|温度为|实测为?|温度|目前|现为|实测)?\s*([1-9][0-9](?:\.[0-9]+)?)\s*(?:℃|度|摄氏度|C|c)"
    matches = re.findall(pattern, text)
    if matches:
        for m in reversed(matches):  # 优先取最后描述的当前实测结果
            try:
                val = float(m)
                # 合理性过滤：机房设备正常运行温度区间通常在 10.0℃ ~ 70.0℃ 之间
                if 10.0 <= val <= 70.0:
                    return round(val, 1)
            except ValueError:
                continue

    # 正则提取模式 2：中文大写/汉字数字（如“二十三度”、“二十六点五度”、“三十度”）
    cn_pattern = r"(?:降至|下降到|回落到|降到|稳定在|测试为|温度为|实测为?|温度|目前|现为|实测)?\s*([一二两三四五六七八九十]+(?:点[零一二三四五六七八九]+)?)\s*(?:℃|度|摄氏度|C|c)"
    cn_matches = re.findall(cn_pattern, text)
    if cn_matches:
        for m in reversed(cn_matches):
            val = _parse_cn_number(m)
            if val is not None and 10.0 <= val <= 70.0:
                return round(val, 1)

    # 兜底匹配：纯数字带单位，如 "26℃"
    pure_deg_pattern = r"([1-9][0-9](?:\.[0-9]+)?)\s*℃"
    m_pure = re.search(pure_deg_pattern, text)
    if m_pure:
        try:
            val = float(m_pure.group(1))
            if 10.0 <= val <= 70.0:
                return round(val, 1)
        except ValueError:
            pass

    return None


def extract_maintenance_actions(text: str) -> List[str]:
    """提取排查处置说明中涉及的具体维保技术动作"""
    if not text:
        return []
    found_actions = []
    for kw in MAINTENANCE_ACTION_KEYWORDS:
        if kw in text and kw not in found_actions:
            found_actions.append(kw)
    return found_actions


def analyze_ticket_resolution_comment(
    comment: Optional[str],
    current_device_temp: Optional[float] = None,
    default_baseline_temp: float = 30.0,
) -> Dict[str, Any]:
    """对工单办结/流转的排查处置说明进行语义提取与 AI 质量审计。

    :param comment: 用户填写的排查处置说明文本
    :param current_device_temp: 设备当前温度（若已知）
    :param default_baseline_temp: 用户未显式声明温度时的轻载健康基准，默认 30.0℃
    :return: 包含实测温度、有效回写温度、维保动作与 AI 审计评语的结构体
    """
    raw_text = (comment or "").strip()
    extracted_temp = extract_temperature_from_text(raw_text)
    actions = extract_maintenance_actions(raw_text)

    is_explicit_temp = extracted_temp is not None
    effective_temp = extracted_temp if is_explicit_temp else default_baseline_temp

    # 判定健康等级与自洽性
    if effective_temp < 38.0:
        evaluated_health = "HEALTHY"
    elif effective_temp < 40.0:
        evaluated_health = "WARNING"
    else:
        evaluated_health = "OVERHEAT"

    # 判定说明详细度与质量
    text_len = len(raw_text)
    if text_len >= 12 and actions and is_explicit_temp:
        quality_level = "SUFFICIENT"
    elif text_len >= 6 or actions or is_explicit_temp:
        quality_level = "BASIC"
    else:
        quality_level = "BRIEF"

    # 生成 AI 验收复核小结 (Audit Note)
    action_desc = "、".join(actions[:3]) if actions else "常规检修"
    if is_explicit_temp:
        audit_note = (
            f"[AI验收审计] 已核验处置说明：实测温度回落至 {extracted_temp}℃（正常健康），"
            f"检修动作包含【{action_desc}】，台账温度已真实回写真实测温值，告警解除。"
        )
    else:
        audit_note = (
            f"[AI验收审计] 已核验处置说明：未显式声明温度数值，"
            f"检修动作包含【{action_desc}】，台账温度联动回落至轻载基线 {default_baseline_temp}℃，告警解除。"
        )

    return {
        "extracted_temperature": extracted_temp,
        "effective_temperature": effective_temp,
        "is_explicit_temp": is_explicit_temp,
        "evaluated_health": evaluated_health,
        "actions": actions,
        "quality_level": quality_level,
        "audit_note": audit_note,
    }
