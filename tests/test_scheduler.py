"""scheduler.py 单元测试。"""
import copy
from datetime import datetime, timezone, timedelta
from anime_notifier.scheduler import run


_SHANGHAI = timezone(timedelta(hours=8))


def _now(weekday: int, hh: int, mm: int = 0) -> datetime:
    """构造一个 2026-06 的 datetime，weekday 由调用方指定。
    2026-06-22 是周一 weekday=1
    """
    base = datetime(2026, 6, 21 + weekday, hh, mm, tzinfo=_SHANGHAI)
    return base


CONFIG = {
    "schedule": [
        {"name": "将夜", "weekday": 4, "air_time": "11:00"},
        {"name": "完美世界", "weekday": 5, "air_time": "10:00"},
        {"name": "沧元图", "weekday": 5, "air_time": "10:00"},
        {"name": "深空彼岸", "weekday": 5, "air_time": "11:00"},
        {"name": "斗罗大陆2", "weekday": 5, "air_time": "12:00"},
    ],
    "wechat": {"send_key": "x", "timezone": "Asia/Shanghai"},
}


def test_weekday_and_air_time_both_must_match():
    """周五 10:00：完美世界 + 沧元图 两条匹配。"""
    title, msg = run(_now(weekday=5, hh=10), copy.deepcopy(CONFIG))
    assert "完美世界" in msg
    assert "沧元图" in msg
    assert "深空彼岸" not in msg
    assert "斗罗大陆2" not in msg
    assert title == "动漫更新：完美世界、沧元图"


def test_no_match_returns_none_title():
    """周一 10:00：CONFIG 里没有 weekday=1 的番。"""
    title, msg = run(_now(weekday=1, hh=10), copy.deepcopy(CONFIG))
    assert title is None
    assert "💤" in msg


def test_weekday_match_but_air_time_different():
    """周四 10:00：将夜 是周四 11:00，不是 10:00，所以不推。"""
    title, msg = run(_now(weekday=4, hh=10), copy.deepcopy(CONFIG))
    assert title is None
    assert "将夜" not in msg


def test_air_time_minute_matters():
    """周四 11:00：将夜 11:00 匹配。"""
    title, msg = run(_now(weekday=4, hh=11, mm=0), copy.deepcopy(CONFIG))
    assert title == "动漫更新：将夜"


def test_title_format_single_anime():
    """单番时 title = "动漫更新：X"。"""
    title, _ = run(_now(weekday=4, hh=11), copy.deepcopy(CONFIG))
    assert title == "动漫更新：将夜"


def test_title_format_multiple_anime():
    """多番时 title = "动漫更新：X、Y、Z"（顿号分隔）。"""
    title, _ = run(_now(weekday=5, hh=10), copy.deepcopy(CONFIG))
    assert title == "动漫更新：完美世界、沧元图"


def test_msg_format_uses_emoji_and_newline():
    """消息体以 🎉 开头，每行 📺 前缀。"""
    _, msg = run(_now(weekday=5, hh=10), copy.deepcopy(CONFIG))
    assert msg.startswith("🎉")
    assert "📺 完美世界" in msg
    assert "📺 沧元图" in msg
