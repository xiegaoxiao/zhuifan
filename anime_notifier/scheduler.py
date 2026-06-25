"""核心调度算法：根据今天 weekday 决定推送哪些番剧。"""
from __future__ import annotations
from datetime import date
from typing import Any


def run(today: date, config: dict[str, Any], state: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """根据 `today` 找出今天 weekday 匹配的番剧，自增集数，返回 (新 state, 消息)。

    `today` 必须已转换为 Asia/Shanghai 时区（由调用方负责）。
    state 会被浅拷贝后再修改。
    """
    weekday = today.isoweekday()  # 周一=1, 周日=7
    new_state: dict[str, Any] = {
        "last_run": today.isoformat(),
        "episodes": dict(state.get("episodes", {})),
    }
    updates: list[str] = []

    for entry in config["schedule"]:
        if entry["weekday"] != weekday:
            continue
        name = entry["name"]
        ep = new_state["episodes"].get(name, 0) + 1
        new_state["episodes"][name] = ep
        updates.append(f"📺 {name}  第 {ep} 集")

    if updates:
        msg = "🎉 今日追番更新：\n" + "\n".join(updates)
    else:
        msg = "💤 今天没有要追的番，好好休息～"

    return new_state, msg
