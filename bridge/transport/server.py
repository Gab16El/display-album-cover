import asyncio
import json

from aiohttp import WSMsgType, web

from now_playing.poller import NowPlayingPoller

LOCAL_ORIGIN_PREFIXES = ("http://localhost", "http://127.0.0.1")


@web.middleware
async def cors(request: web.Request, handler):
    response = await handler(request)
    origin = request.headers.get("Origin", "")
    if origin.startswith(LOCAL_ORIGIN_PREFIXES):
        response.headers["Access-Control-Allow-Origin"] = origin
    return response


def build_app(poller: NowPlayingPoller) -> web.Application:
    app = web.Application(middlewares=[cors])
    sockets: set[web.WebSocketResponse] = set()

    async def broadcast(payload: dict) -> None:
        message = json.dumps(payload)
        await asyncio.gather(*(ws.send_str(message) for ws in sockets), return_exceptions=True)

    async def ws_handler(request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        sockets.add(ws)
        await ws.send_str(json.dumps(poller.state.to_dict()))
        async for msg in ws:
            if msg.type == WSMsgType.ERROR:
                break
        sockets.discard(ws)
        return ws

    async def cover_handler(_: web.Request) -> web.Response:
        if not poller.cover:
            raise web.HTTPNotFound()
        return web.Response(body=poller.cover, content_type="image/jpeg", headers={"Cache-Control": "no-store"})

    async def now_playing_handler(_: web.Request) -> web.Response:
        return web.json_response(poller.state.to_dict())

    async def start_poller(_: web.Application) -> None:
        poller.subscribe(broadcast)
        app["poller_task"] = asyncio.create_task(poller.run())

    async def stop_poller(_: web.Application) -> None:
        app["poller_task"].cancel()

    app.router.add_get("/ws", ws_handler)
    app.router.add_get("/cover", cover_handler)
    app.router.add_get("/now-playing", now_playing_handler)
    app.on_startup.append(start_poller)
    app.on_cleanup.append(stop_poller)
    return app
