"""CLI 入口。

用法：
    python -m anime_notifier            # 正常推送
    python -m anime_notifier --dry-run   # 仅打印不推送、不写 state
"""
from __future__ import annotations
import argparse
import sys
from datetime import date, datetime, timezone, timedelta

from . import config as cfg_mod
from . import state as state_mod
from . import notifier, scheduler


_SHANGHAI = timezone(timedelta(hours=8))


def _now_in_shanghai() -> date:
    """返回当前 Asia/Shanghai 时区的日期。"""
    return datetime.now(tz=_SHANGHAI).date()


def main() -> int:
    parser = argparse.ArgumentParser(prog="anime_notifier")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印将要推送的消息，不调 Server 酱、不修改 state.json、不 commit",
    )
    args = parser.parse_args()

    cfg = cfg_mod.load_config("config.yaml")
    state = state_mod.load_state("state.json")

    today = _now_in_shanghai()
    new_state, msg = scheduler.run(today, cfg, state)

    print(msg)

    if args.dry_run:
        return 0

    notifier.send_via_serverchan(
        cfg["wechat"]["send_key"],
        msg,
        title="追番更新",
    )
    state_mod.save_state("state.json", new_state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
