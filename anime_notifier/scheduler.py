"""核心调度算法：根据当前时间决定推送哪些番剧。"""
from __future__ import annotations
from datetime import datetime
from typing import Any


# 容错窗口：now 落在 air_time ±TOLERANCE_MINUTES 分钟内都视为匹配
# 原因：GitHub Actions cron 实际触发可能延迟 5~30 分钟
# 权衡：容错越大推送成功率越高，但 GitHub cron 偶发多次触发时可能重复推送
TOLERANCE_MINUTES = 30


def _minutes_since_midnight(dt: datetime) -> int:
    """把 datetime 转换为自当天 00:00 起的分钟数。"""
    return dt.hour * 60 + dt.minute


def _air_time_to_minutes(air_time: str) -> int:
    """把 'HH:MM' 字符串转换为分钟数。"""
    h, m = air_time.split(":")
    return int(h) * 60 + int(m)


def run(now: datetime, config: dict[str, Any]) -> tuple[str | None, str]:
    """根据 `now` 找出"今天 weekday 匹配且 now 落在 air_time ±30 分钟内"的番剧。

    返回 (title, msg)：
    - 有匹配：title = "动漫更新：X、Y..."，msg 含 📺 列表
    - 无匹配：title = None，msg = "💤 今天没有要追的番"

    `now` 必须是带时区的 datetime（Asia/Shanghai，由调用方负责）。
    """
    weekday = now.isoweekday()              # 周一=1, 周日=7
    now_minutes = _minutes_since_midnight(now)
    names: list[str] = []

    for entry in config["schedule"]:
        if entry["weekday"] != weekday:
            continue
        target = _air_time_to_minutes(entry["air_time"])
        if abs(now_minutes - target) > TOLERANCE_MINUTES:
            continue
        names.append(entry["name"])

    if not names:
        return None, "💤 今天没有要追的番"

    title = "动漫更新：" + "、".join(names)
    msg = "🎉 今日追番更新：\n" + "\n".join(f"📺 {n}" for n in names)
    return title, msg
