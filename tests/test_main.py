"""__main__.py 集成测试。"""
import sys
from datetime import datetime, timezone, timedelta
import pytest

from anime_notifier import __main__ as cli


_SHANGHAI = timezone(timedelta(hours=8))


def _write_config(tmp_path, schedule, send_key="SCT_TEST"):
    """schedule: list of (name, weekday, air_time)"""
    lines = ["schedule:"]
    for name, weekday, air_time in schedule:
        lines.append(f"  - name: {name}")
        lines.append(f"    weekday: {weekday}")
        lines.append(f'    air_time: "{air_time}"')
    lines += [
        "wechat:",
        f"  send_key: {send_key}",
        "  timezone: Asia/Shanghai",
    ]
    (tmp_path / "config.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_dry_run_does_not_modify_files(tmp_path, monkeypatch, capsys):
    """dry-run 模式：只 print，不调 notifier。"""
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, [("巨人", 4, "11:00")])

    monkeypatch.setattr(
        cli, "_now_in_shanghai",
        lambda: datetime(2026, 6, 25, 11, 0, tzinfo=_SHANGHAI),  # 周四 11:00
    )
    monkeypatch.setattr(sys, "argv", ["anime_notifier", "--dry-run"])
    rc = cli.main()
    captured = capsys.readouterr()

    assert rc == 0
    assert "巨人" in captured.out
    # 不应创建任何 state.json
    assert not (tmp_path / "state.json").exists()


def test_normal_run_pushes_message(tmp_path, monkeypatch, respx_mock):
    """正常模式：调 notifier 推送，title 来自 scheduler。"""
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, [("巨人", 4, "11:00"), ("芙莉莲", 4, "11:00")])

    import httpx
    captured: dict = {}

    def capture(request: httpx.Request) -> httpx.Response:
        captured.update(dict(request.url.params))
        return httpx.Response(200, json={"code": 0, "message": "ok"})

    respx_mock.post("https://sctapi.ftqq.com/SCT_TEST.send").mock(side_effect=capture)

    monkeypatch.setattr(
        cli, "_now_in_shanghai",
        lambda: datetime(2026, 6, 25, 11, 0, tzinfo=_SHANGHAI),
    )
    monkeypatch.setattr(sys, "argv", ["anime_notifier"])
    rc = cli.main()

    assert rc == 0
    assert captured.get("title") == "动漫更新：巨人、芙莉莲"
    assert "巨人" in captured.get("desp", "")


def test_no_match_does_not_push(tmp_path, monkeypatch, respx_mock):
    """无匹配时：notifier 不被调，直接 return。"""
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, [("巨人", 4, "11:00")])  # 周四 11:00 才有

    import httpx
    route = respx_mock.post("https://sctapi.ftqq.com/SCT_TEST.send").mock(
        return_value=httpx.Response(200, json={"code": 0, "message": "ok"})
    )

    # 改时间到周一 10:00（不在任何番的 air_time）
    monkeypatch.setattr(
        cli, "_now_in_shanghai",
        lambda: datetime(2026, 6, 22, 10, 0, tzinfo=_SHANGHAI),  # 周一 10:00
    )
    monkeypatch.setattr(sys, "argv", ["anime_notifier"])
    rc = cli.main()

    assert rc == 0
    assert route.call_count == 0  # notifier 没被调