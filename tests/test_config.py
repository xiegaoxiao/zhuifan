"""config.py 单元测试。"""
import pytest
from anime_notifier.config import load_config, ConfigError


def test_load_config_minimal(tmp_path):
    """最小可用配置：1 个 schedule 条目 + wechat 块。"""
    p = tmp_path / "config.yaml"
    p.write_text(
        "schedule:\n"
        "  - name: 进击的巨人\n"
        "    weekday: 4\n"
        "wechat:\n"
        "  send_key: SCT123\n"
        "  push_time: '20:00'\n"
        "  timezone: Asia/Shanghai\n"
    )
    cfg = load_config(p)
    assert cfg["schedule"][0]["name"] == "进击的巨人"
    assert cfg["schedule"][0]["weekday"] == 4
    assert cfg["wechat"]["send_key"] == "SCT123"


def test_load_config_missing_schedule(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text("wechat:\n  send_key: x\n  push_time: '20:00'\n  timezone: Asia/Shanghai\n")
    with pytest.raises(ConfigError, match="schedule"):
        load_config(p)


def test_load_config_missing_wechat(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text("schedule:\n  - name: a\n    weekday: 1\n")
    with pytest.raises(ConfigError, match="wechat"):
        load_config(p)


def test_load_config_weekday_out_of_range(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text(
        "schedule:\n"
        "  - name: a\n"
        "    weekday: 8\n"
        "wechat:\n"
        "  send_key: x\n"
        "  push_time: '20:00'\n"
        "  timezone: Asia/Shanghai\n"
    )
    with pytest.raises(ConfigError, match="weekday"):
        load_config(p)


def test_load_config_duplicate_name(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text(
        "schedule:\n"
        "  - name: a\n"
        "    weekday: 1\n"
        "  - name: a\n"
        "    weekday: 2\n"
        "wechat:\n"
        "  send_key: x\n"
        "  push_time: '20:00'\n"
        "  timezone: Asia/Shanghai\n"
    )
    with pytest.raises(ConfigError, match="duplicate"):
        load_config(p)


def test_load_config_send_key_from_env(tmp_path, monkeypatch):
    """send_key='${WECHAT_SEND_KEY}' 时从环境变量读取。"""
    monkeypatch.setenv("WECHAT_SEND_KEY", "SCT_FROM_ENV")
    p = tmp_path / "config.yaml"
    p.write_text(
        "schedule:\n"
        "  - name: a\n"
        "    weekday: 1\n"
        "wechat:\n"
        "  send_key: '${WECHAT_SEND_KEY}'\n"
        "  push_time: '20:00'\n"
        "  timezone: Asia/Shanghai\n"
    )
    cfg = load_config(p)
    assert cfg["wechat"]["send_key"] == "SCT_FROM_ENV"


def test_load_config_env_placeholder_missing(monkeypatch, tmp_path):
    """环境变量占位符但环境变量未设置时抛错。"""
    monkeypatch.delenv("WECHAT_SEND_KEY", raising=False)
    p = tmp_path / "config.yaml"
    p.write_text(
        "schedule:\n"
        "  - name: a\n"
        "    weekday: 1\n"
        "wechat:\n"
        "  send_key: '${WECHAT_SEND_KEY}'\n"
        "  push_time: '20:00'\n"
        "  timezone: Asia/Shanghai\n"
    )
    with pytest.raises(ConfigError, match="WECHAT_SEND_KEY"):
        load_config(p)
