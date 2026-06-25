"""加载与校验 config.yaml。

约定：
- weekday: 1=周一, 7=周日
- send_key 支持 ${ENV_VAR} 占位符，从环境变量读取
"""
from __future__ import annotations
import os
import re
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """配置校验失败。"""


_ENV_PATTERN = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")


def _resolve_env(value: Any) -> Any:
    """将 '${VAR}' 形式的字符串从环境变量替换。"""
    if not isinstance(value, str):
        return value
    match = _ENV_PATTERN.fullmatch(value)
    if not match:
        return value
    var = match.group(1)
    if var not in os.environ:
        raise ConfigError(f"environment variable {var} is not set")
    return os.environ[var]


def load_config(path: str | Path) -> dict[str, Any]:
    """加载并校验 config.yaml。失败抛 ConfigError。"""
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"config file not found: {p}")

    try:
        raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise ConfigError(f"invalid yaml: {e}") from e

    if not isinstance(raw, dict):
        raise ConfigError("config root must be a mapping")

    if "schedule" not in raw:
        raise ConfigError("missing required key: schedule")
    if "wechat" not in raw:
        raise ConfigError("missing required key: wechat")

    schedule = raw["schedule"]
    if not isinstance(schedule, list) or not schedule:
        raise ConfigError("schedule must be a non-empty list")

    seen_names: set[str] = set()
    for i, entry in enumerate(schedule):
        if not isinstance(entry, dict):
            raise ConfigError(f"schedule[{i}] must be a mapping")
        if "name" not in entry or not isinstance(entry["name"], str):
            raise ConfigError(f"schedule[{i}].name missing or not string")
        if "weekday" not in entry or not isinstance(entry["weekday"], int):
            raise ConfigError(f"schedule[{i}].weekday missing or not int")
        if not 1 <= entry["weekday"] <= 7:
            raise ConfigError(
                f"schedule[{i}].weekday={entry['weekday']} out of range 1..7"
            )
        if entry["name"] in seen_names:
            raise ConfigError(f"duplicate schedule name: {entry['name']!r}")
        seen_names.add(entry["name"])

    wechat = raw["wechat"]
    for key in ("send_key", "push_time", "timezone"):
        if key not in wechat:
            raise ConfigError(f"wechat.{key} missing")

    wechat["send_key"] = _resolve_env(wechat["send_key"])
    return raw
