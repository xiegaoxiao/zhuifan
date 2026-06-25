"""Server 酱 HTTP 推送。

API: POST https://sctapi.ftqq.com/{SendKey}.send
参数: title (可选), desp (消息正文)
"""
from __future__ import annotations
import httpx


class NotifierError(RuntimeError):
    """推送失败。"""


_API = "https://sctapi.ftqq.com"
_TIMEOUT = httpx.Timeout(10.0)
_MAX_RETRIES = 1  # 5xx 重试 1 次


def send_via_serverchan(
    send_key: str,
    desp: str,
    *,
    title: str = "追番更新",
) -> None:
    """通过 Server 酱推送消息到个人微信。失败抛 NotifierError。"""
    url = f"{_API}/{send_key}.send"
    attempts = _MAX_RETRIES + 1
    last_err: Exception | None = None

    for attempt in range(attempts):
        try:
            resp = httpx.post(
                url,
                params={"title": title, "desp": desp},
                timeout=_TIMEOUT,
            )
        except httpx.HTTPError as e:
            last_err = e
            continue

        if 200 <= resp.status_code < 300:
            return
        if 500 <= resp.status_code < 600 and attempt < attempts - 1:
            last_err = NotifierError(f"server-chan {resp.status_code}: {resp.text}")
            continue
        raise NotifierError(f"server-chan {resp.status_code}: {resp.text}")

    raise NotifierError(f"server-chan unreachable: {last_err}")
