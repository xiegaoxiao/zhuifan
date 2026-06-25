"""notifier.py 单元测试。"""
import pytest
import httpx
from anime_notifier.notifier import send_via_serverchan, NotifierError


def _make_response(status_code: int, json_body: dict) -> httpx.Response:
    return httpx.Response(status_code=status_code, json=json_body)


def test_send_success(respx_mock):
    respx_mock.post("https://sctapi.ftqq.com/SCT123.send").mock(
        return_value=_make_response(200, {"code": 0, "message": "ok"})
    )
    send_via_serverchan("SCT123", "hello world")


def test_send_raises_on_4xx(respx_mock):
    respx_mock.post("https://sctapi.ftqq.com/BAD.send").mock(
        return_value=_make_response(400, {"code": 1, "message": "invalid key"})
    )
    with pytest.raises(NotifierError, match="400"):
        send_via_serverchan("BAD", "hello")


def test_send_raises_on_5xx(respx_mock):
    respx_mock.post("https://sctapi.ftqq.com/SCT123.send").mock(
        return_value=_make_response(500, {"message": "server error"})
    )
    with pytest.raises(NotifierError, match="500"):
        send_via_serverchan("SCT123", "hello")


def test_send_payload_includes_title_and_desp(respx_mock):
    """Server 酱接受 title + desp 两个字段。"""
    captured = {}

    def capture(request: httpx.Request) -> httpx.Response:
        captured.update(dict(request.url.params))
        return _make_response(200, {"code": 0, "message": "ok"})

    respx_mock.post("https://sctapi.ftqq.com/SCT123.send").mock(side_effect=capture)
    send_via_serverchan(
        "SCT123",
        "🎉 今日追番更新：\n📺 巨人  第 12 集",
        title="追番更新",
    )
    assert captured.get("title") == "追番更新"
    assert "巨人" in captured.get("desp", "")


def test_send_retries_once_on_5xx(respx_mock):
    """5xx 触发 1 次重试。"""
    route = respx_mock.post("https://sctapi.ftqq.com/SCT123.send").mock(
        side_effect=[
            _make_response(503, {"message": "down"}),
            _make_response(200, {"code": 0, "message": "ok"}),
        ]
    )
    send_via_serverchan("SCT123", "hello")
    assert route.call_count == 2