"""config.py 单元测试。"""
import pytest
from anime_notifier.config import load_config, ConfigError


def _write_config(tmp_path, schedule, send_key="SCT123", with_wechat=True):
    """辅助函数：写一个临时 config.yaml。"""
    lines = ["schedule:"]
    for s in schedule:
        # s = (name, weekday, air_time) 或 (name, weekday, air_time, extra_dict)
        if len(s) == 3:
            name, weekday, air_time = s
            lines.append(f"  - name: {name}")
            lines.append(f"    weekday: {weekday}")
            lines.append(f'    air_time: "{air_time}"')
        else:
            name, weekday, air_time, extra = s
            lines.append(f"  - name: {name}")
            lines.append(f"    weekday: {weekday}")
            lines.append(f'    air_time: "{air_time}"')
            for k, v in extra.items():
                lines.append(f"    {k}: {v}")
    if with_wechat:
        lines += [
            "wechat:",
            f"  send_key: {send_key}",
            "  timezone: Asia/Shanghai",
        ]
    p = tmp_path / "config.yaml"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def test_load_config_minimal(tmp_path):
    """最小可用配置：1 个 schedule 条目（含 air_time）+ wechat 块。"""
    p = _write_config(tmp_path, [("进击的巨人", 4, "10:00")])
    cfg = load_config(p)
    assert cfg["schedule"][0]["name"] == "进击的巨人"
    assert cfg["schedule"][0]["weekday"] == 4
    assert cfg["schedule"][0]["air_time"] == "10:00"
    assert cfg["wechat"]["send_key"] == "SCT123"
    assert cfg["wechat"]["timezone"] == "Asia/Shanghai"


def test_load_config_missing_schedule(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text("wechat:\n  send_key: x\n  timezone: Asia/Shanghai\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="schedule"):
        load_config(p)


def test_load_config_missing_wechat(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text('schedule:\n  - name: a\n    weekday: 1\n    air_time: "10:00"\n', encoding="utf-8")
    with pytest.raises(ConfigError, match="wechat"):
        load_config(p)


def test_load_config_weekday_out_of_range(tmp_path):
    p = _write_config(tmp_path, [("a", 8, "10:00")])
    with pytest.raises(ConfigError, match="weekday"):
        load_config(p)


def test_load_config_duplicate_name(tmp_path):
    p = _write_config(tmp_path, [("a", 1, "10:00"), ("a", 2, "11:00")])
    with pytest.raises(ConfigError, match="duplicate"):
        load_config(p)


def test_load_config_send_key_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("WECHAT_SEND_KEY", "SCT_FROM_ENV")
    p = _write_config(tmp_path, [("a", 1, "10:00")], send_key='"${WECHAT_SEND_KEY}"')
    cfg = load_config(p)
    assert cfg["wechat"]["send_key"] == "SCT_FROM_ENV"


def test_load_config_env_placeholder_missing(monkeypatch, tmp_path):
    monkeypatch.delenv("WECHAT_SEND_KEY", raising=False)
    p = _write_config(tmp_path, [("a", 1, "10:00")], send_key='"${WECHAT_SEND_KEY}"')
    with pytest.raises(ConfigError, match="WECHAT_SEND_KEY"):
        load_config(p)


@pytest.mark.parametrize("bad_time", ["25:00", "9:00", "10:60", "abc", "10:00:00", ""])
def test_air_time_invalid_format(tmp_path, bad_time):
    p = _write_config(tmp_path, [("a", 1, bad_time)])
    with pytest.raises(ConfigError, match="air_time"):
        load_config(p)


def test_air_time_missing_field(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text(
        "schedule:\n  - name: a\n    weekday: 1\n"
        "wechat:\n  send_key: x\n  timezone: Asia/Shanghai\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="air_time"):
        load_config(p)


def test_wechat_does_not_require_push_time(tmp_path):
    """push_time 字段已被删除，wechat 块只要求 send_key + timezone。"""
    p = _write_config(tmp_path, [("a", 1, "10:00")])
    cfg = load_config(p)
    assert "push_time" not in cfg["wechat"]