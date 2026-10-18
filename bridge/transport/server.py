import asyncio
import json
from pathlib import Path

from aiohttp import WSMsgType, web

from now_playing.poller import NowPlayingPoller

from .access import is_local_origin, make_token_guard, require_allowed_origin

AUDIO_INTERVAL = 1 / 30


@web.middleware
async def cors(request: web.Request, handler):
    response = await handler(request)
    origin = request.headers.get("Origin", "")
    if origin and is_local_origin(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
    return response


async def _send_all(sockets: set[web.WebSocketResponse], payload: dict) -> None:
    message = json.dumps(payload)
    await asyncio.gather(*(ws.send_str(message) for ws in sockets), return_exceptions=True)


def build_app(
    poller: NowPlayingPoller,
    analyzer,
    web_dir: Path | None = None,
    token: str | None = None,
) -> web.Application:
    app = web.Application(middlewares=[make_token_guard(token), cors])
    sockets: set[web.WebSocketResponse] = set()
    audio_sockets: set[web.WebSocketResponse] = set()

    async def broadcast(payload: dict) -> None:
        await _send_all(sockets, payload)

    async def audio_loop() -> None:
        while True:
            if audio_sockets:
                await _send_all(audio_sockets, analyzer.snapshot().to_dict())
            await asyncio.sleep(AUDIO_INTERVAL)

    async def audio_ws_handler(request: web.Request) -> web.WebSocketResponse:
        require_allowed_origin(request)
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        audio_sockets.add(ws)
        async for _ in ws:
            pass
        audio_sockets.discard(ws)
        return ws

    async def ws_handler(request: web.Request) -> web.WebSocketResponse:
        require_allowed_origin(request)
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

    async def start_tasks(_: web.Application) -> None:
        poller.subscribe(broadcast)
        try:
            analyzer.start()
        except OSError as exc:
            print(f"audio capture unavailable: {exc}")
        app["tasks"] = [asyncio.create_task(poller.run()), asyncio.create_task(audio_loop())]

    async def close_sockets(_: web.Application) -> None:
        for ws in [*sockets, *audio_sockets]:
            await ws.close()

    async def stop_tasks(_: web.Application) -> None:
        for task in app["tasks"]:
            task.cancel()
        analyzer.stop()

    app.router.add_get("/ws", ws_handler)
    app.router.add_get("/audio", audio_ws_handler)
    app.router.add_get("/cover", cover_handler)
    app.router.add_get("/now-playing", now_playing_handler)
    if web_dir:

        async def index_handler(_: web.Request) -> web.FileResponse:
            return web.FileResponse(web_dir / "index.html")

        app.router.add_get("/", index_handler)
        app.router.add_static("/", web_dir)

    app.on_startup.append(start_tasks)
    app.on_shutdown.append(close_sockets)
    app.on_cleanup.append(stop_tasks)
    return app
