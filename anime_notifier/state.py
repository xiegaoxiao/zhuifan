"""加载与保存 state.json。

损坏处理：解析失败时把原文件备份为 state.json.bak 并返回空 state。
"""
from __future__ import annotations
import json
import shutil
from pathlib import Path
from typing import Any


class StateError(ValueError):
    """state 加载/保存失败（非文件损坏类）。"""


_EMPTY_STATE: dict[str, Any] = {"last_run": None, "episodes": {}}


def load_state(path: str | Path) -> dict[str, Any]:
    """加载 state.json。文件不存在或损坏时返回空 state。"""
    p = Path(path)
    if not p.exists():
        return dict(_EMPTY_STATE)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        bak = p.with_suffix(p.suffix + ".bak")
        shutil.copy2(p, bak)
        return dict(_EMPTY_STATE)
    if not isinstance(data, dict):
        return dict(_EMPTY_STATE)
    data.setdefault("last_run", None)
    data.setdefault("episodes", {})
    if not isinstance(data["episodes"], dict):
        data["episodes"] = {}
    return data


def save_state(path: str | Path, state: dict[str, Any]) -> None:
    """原子写入 state.json。"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    tmp.replace(p)
