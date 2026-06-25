"""核心调度算法：根据当前时间决定推送哪些番剧。"""
from __future__ import annotations
from datetime import datetime
from typing import Any


def run(now: datetime, config: dict[str, Any]) -> tuple[str | None, str]:
    """根据 `now` 找出"今天 weekday 匹配且 air_time == 当前分钟"的番剧。

    返回 (title, msg)：
    - 有匹配：title = "动漫更新：X、Y..."，msg 含 📺 列表
    - 无匹配：title = None，msg = "💤 今天没有要追的番"

    `now` 必须是带时区的 datetime（Asia/Shanghai，由调用方负责）。
    """
    weekday = now.isoweekday()              # 周一=1, 周日=7
    current_time = now.strftime("%H:%M")    # "10:00"
    names: list[str] = []

    for entry in config["schedule"]:
        if entry["weekday"] != weekday:
            continue
        if entry["air_time"] != current_time:
            continue
        names.append(entry["name"])

    if not names:
        return None, "💤 今天没有要追的番"

    title = "动漫更新：" + "、".join(names)
    msg = "🎉 今日追番更新：\n" + "\n".join(f"📺 {n}" for n in names)
    return title, msg
