import hmac
from urllib.parse import urlparse

from aiohttp import web

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
LOOPBACK_ADDRESSES = {"127.0.0.1", "::1"}
TOKEN_COOKIE = "dac_token"
COOKIE_MAX_AGE = 60 * 60 * 24 * 30


def is_local_origin(origin: str) -> bool:
    return urlparse(origin).hostname in LOCAL_HOSTS


def is_allowed_origin(origin: str, host: str) -> bool:
    return is_local_origin(origin) or urlparse(origin).netloc == host


def require_allowed_origin(request: web.Request) -> None:
    origin = request.headers.get("Origin")
    if origin and not is_allowed_origin(origin, request.host):
        raise web.HTTPForbidden()


def make_token_guard(token: str | None):
    @web.middleware
    async def guard(request: web.Request, handler):
        if token is None or request.remote in LOOPBACK_ADDRESSES:
            return await handler(request)
        supplied = request.query.get("token") or request.cookies.get(TOKEN_COOKIE) or ""
        if not hmac.compare_digest(supplied, token):
            raise web.HTTPUnauthorized(text="Access token required")
        response = await handler(request)
        if request.query.get("token") and not response.prepared:
            response.set_cookie(
                TOKEN_COOKIE, token, httponly=True, samesite="Lax", max_age=COOKIE_MAX_AGE
            )
        return response

    return guard
