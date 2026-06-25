"""scheduler.py 单元测试。"""
import copy
from datetime import date
from anime_notifier.scheduler import run


CONFIG = {
    "schedule": [
        {"name": "进击的巨人", "weekday": 4},   # 周四
        {"name": "芙莉莲", "weekday": 5},      # 周五
        {"name": "孤独摇滚", "weekday": 6},     # 周六
    ],
    "wechat": {"send_key": "x", "push_time": "20:00", "timezone": "Asia/Shanghai"},
}


def test_thursday_only_matches_thursday():
    state = {"last_run": None, "episodes": {}}
    new_state, msg = run(date(2026, 6, 25), copy.deepcopy(CONFIG), copy.deepcopy(state))
    assert "进击的巨人" in msg
    assert "芙莉莲" not in msg
    assert "孤独摇滚" not in msg
    assert new_state["episodes"]["进击的巨人"] == 1


def test_episode_increments_each_thursday():
    state = {"last_run": None, "episodes": {"进击的巨人": 11}}
    new_state, _ = run(date(2026, 6, 25), copy.deepcopy(CONFIG), copy.deepcopy(state))
    assert new_state["episodes"]["进击的巨人"] == 12


def test_no_match_returns_no_update_message():
    """周一没匹配时返回'无更新'消息，state 不变。"""
    state = {"last_run": None, "episodes": {"进击的巨人": 11}}
    new_state, msg = run(date(2026, 6, 22), copy.deepcopy(CONFIG), copy.deepcopy(state))
    assert "没有" in msg or "💤" in msg
    assert new_state["episodes"] == {"进击的巨人": 11}


def test_removed_entry_not_in_state_does_not_crash():
    """config 删除某项后，state 残留记录无害跳过。"""
    cfg = {
        "schedule": [{"name": "芙莉莲", "weekday": 5}],  # 只剩一个
        "wechat": {"send_key": "x", "push_time": "20:00", "timezone": "Asia/Shanghai"},
    }
    state = {"last_run": None, "episodes": {"进击的巨人": 12, "芙莉莲": 3}}
    new_state, msg = run(date(2026, 6, 26), cfg, copy.deepcopy(state))
    assert "芙莉莲" in msg
    assert "进击的巨人" not in msg
    assert new_state["episodes"]["进击的巨人"] == 12  # 不变
    assert new_state["episodes"]["芙莉莲"] == 4


def test_message_format_includes_emoji_and_episode():
    state = {"last_run": None, "episodes": {}}
    _, msg = run(date(2026, 6, 25), copy.deepcopy(CONFIG), copy.deepcopy(state))
    assert msg.startswith("🎉")
    assert "第 1 集" in msg


def test_multiple_matches_in_one_day():
    """同一天有多个更新时都列出。"""
    cfg = {
        "schedule": [
            {"name": "A", "weekday": 4},
            {"name": "B", "weekday": 4},
            {"name": "C", "weekday": 5},
        ],
        "wechat": {"send_key": "x", "push_time": "20:00", "timezone": "Asia/Shanghai"},
    }
    state = {"last_run": None, "episodes": {}}
    _, msg = run(date(2026, 6, 25), cfg, state)
    assert "A" in msg
    assert "B" in msg
    assert "C" not in msg


def test_state_last_run_updated():
    state = {"last_run": None, "episodes": {}}
    new_state, _ = run(date(2026, 6, 25), copy.deepcopy(CONFIG), state)
    assert new_state["last_run"] == "2026-06-25"
