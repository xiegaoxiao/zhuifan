"""CLI 入口。

用法：
    python -m anime_notifier            # 正常推送（按当前时间 air_time 匹配）
    python -m anime_notifier --dry-run   # 仅打印不推送
"""
from __future__ import annotations
import argparse
import sys
from datetime import datetime, timezone, timedelta

from . import config as cfg_mod
from . import notifier, scheduler


_SHANGHAI = timezone(timedelta(hours=8))


def _now_in_shanghai() -> datetime:
    """返回当前 Asia/Shanghai 时区的 datetime（精确到秒）。"""
    return datetime.now(tz=_SHANGHAI)


def main() -> int:
    parser = argparse.ArgumentParser(prog="anime_notifier")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印将要推送的消息，不调 Server 酱",
    )
    args = parser.parse_args()

    cfg = cfg_mod.load_config("config.yaml")
    now = _now_in_shanghai()
    title, msg = scheduler.run(now, cfg)

    print(msg)

    if args.dry_run:
        return 0

    if title is None:
        # 无更新，不推送，直接退出
        return 0

    notifier.send_via_serverchan(
        cfg["wechat"]["send_key"],
        msg,
        title=title,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())