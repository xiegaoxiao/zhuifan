"""__main__.py 集成测试。"""
import json
import sys
from datetime import date
import pytest

from anime_notifier import __main__ as cli


def _write_config(tmp_path, schedule, send_key="SCT_TEST"):
    (tmp_path / "config.yaml").write_text(
        "schedule:\n" + "".join(f"  - name: {n}\n    weekday: {w}\n" for n, w in schedule)
        + f"wechat:\n  send_key: {send_key}\n  push_time: '20:00'\n  timezone: Asia/Shanghai\n",
        encoding="utf-8",
    )


def test_dry_run_does_not_modify_state(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, [("巨人", 4)])
    (tmp_path / "state.json").write_text(json.dumps({"last_run": None, "episodes": {}}))

    monkeypatch.setattr(sys, "argv", ["anime_notifier", "--dry-run"])
    rc = cli.main()
    captured = capsys.readouterr()

    assert rc == 0
    assert "巨人" in captured.out
    # state.json 不变
    state = json.loads((tmp_path / "state.json").read_text())
    assert state["episodes"] == {}


def test_normal_run_pushes_and_updates_state(tmp_path, monkeypatch, respx_mock):
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, [("巨人", 4)])
    (tmp_path / "state.json").write_text(json.dumps({"last_run": None, "episodes": {}}))

    import httpx
    respx_mock.post("https://sctapi.ftqq.com/SCT_TEST.send").mock(
        return_value=httpx.Response(200, json={"code": 0, "message": "ok"})
    )

    monkeypatch.setattr(cli, "_now_in_shanghai", lambda: date(2026, 6, 25))

    monkeypatch.setattr(sys, "argv", ["anime_notifier"])
    rc = cli.main()

    assert rc == 0
    state = json.loads((tmp_path / "state.json").read_text())
    assert state["episodes"]["巨人"] == 1
    assert state["last_run"] == "2026-06-25"


def test_normal_run_propagates_notifier_error(tmp_path, monkeypatch, respx_mock):
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, [("巨人", 4)])
    (tmp_path / "state.json").write_text(json.dumps({"last_run": None, "episodes": {}}))

    import httpx
    respx_mock.post("https://sctapi.ftqq.com/SCT_TEST.send").mock(
        return_value=httpx.Response(400, json={"code": 1, "message": "bad key"})
    )

    monkeypatch.setattr(cli, "_now_in_shanghai", lambda: date(2026, 6, 25))
    monkeypatch.setattr(sys, "argv", ["anime_notifier"])

    with pytest.raises(Exception):
        cli.main()