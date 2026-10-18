import asyncio
from unittest.mock import Mock

import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request

from transport.access import TOKEN_COOKIE, is_allowed_origin, make_token_guard

TOKEN = "s3cret-token"
HOST = "192.168.1.20:8765"


@pytest.mark.parametrize(
    ("origin", "allowed"),
    [
        ("http://localhost:5173", True),
        ("http://127.0.0.1:8765", True),
        (f"http://{HOST}", True),
        ("https://evil.example", False),
        ("http://localhost.evil.com", False),
        ("http://127.0.0.1.evil.com", False),
        ("http://192.168.1.99:8765", False),
    ],
)
def test_origin_rules(origin, allowed):
    assert is_allowed_origin(origin, HOST) is allowed


def request_from(remote: str, path: str = "/", cookies: str | None = None):
    transport = Mock()
    transport.get_extra_info.return_value = (remote, 51000)
    headers = {"Cookie": cookies} if cookies else {}
    return make_mocked_request("GET", path, headers=headers, transport=transport)


async def ok_handler(_: web.Request) -> web.Response:
    return web.Response(text="ok")


def call_guard(token, request):
    return asyncio.run(make_token_guard(token)(request, ok_handler))


def test_loopback_does_not_need_a_token():
    assert call_guard(TOKEN, request_from("127.0.0.1")).status == 200


def test_guard_is_off_without_a_token():
    assert call_guard(None, request_from("192.168.1.50")).status == 200


def test_remote_without_token_is_rejected():
    with pytest.raises(web.HTTPUnauthorized):
        call_guard(TOKEN, request_from("192.168.1.50"))


def test_remote_with_wrong_token_is_rejected():
    with pytest.raises(web.HTTPUnauthorized):
        call_guard(TOKEN, request_from("192.168.1.50", "/?token=nope"))


def test_remote_with_token_gets_a_cookie():
    response = call_guard(TOKEN, request_from("192.168.1.50", f"/?token={TOKEN}"))
    assert response.status == 200
    assert TOKEN_COOKIE in response.cookies


def test_remote_with_cookie_is_accepted():
    request = request_from("192.168.1.50", "/audio", cookies=f"{TOKEN_COOKIE}={TOKEN}")
    assert call_guard(TOKEN, request).status == 200
