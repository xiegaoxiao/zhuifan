"""state.py 单元测试。"""
import json
import pytest
from anime_notifier.state import load_state, save_state, StateError


def test_load_state_missing_returns_empty(tmp_path):
    """state.json 不存在时返回空 state，不抛错。"""
    p = tmp_path / "state.json"
    state = load_state(p)
    assert state == {"last_run": None, "episodes": {}}


def test_load_state_valid(tmp_path):
    p = tmp_path / "state.json"
    p.write_text(json.dumps({"last_run": "2026-06-25", "episodes": {"A": 5}}))
    state = load_state(p)
    assert state["last_run"] == "2026-06-25"
    assert state["episodes"]["A"] == 5


def test_load_state_corrupted_backs_up_and_returns_empty(tmp_path):
    """损坏的 state.json 备份为 .bak，返回空 state。"""
    p = tmp_path / "state.json"
    p.write_text("{ this is not valid json")
    state = load_state(p)
    assert state == {"last_run": None, "episodes": {}}
    bak = tmp_path / "state.json.bak"
    assert bak.exists()
    assert bak.read_text(encoding="utf-8") == "{ this is not valid json"


def test_save_state_roundtrip(tmp_path):
    p = tmp_path / "state.json"
    state = {"last_run": "2026-06-25", "episodes": {"A": 5, "B": 3}}
    save_state(p, state)
    loaded = load_state(p)
    assert loaded == state


def test_save_state_writes_valid_json(tmp_path):
    p = tmp_path / "state.json"
    save_state(p, {"last_run": None, "episodes": {}})
    content = p.read_text(encoding="utf-8")
    json.loads(content)  # 不抛错 = 合法 JSON
