import argparse
import asyncio
import sys
import webbrowser
from pathlib import Path

from aiohttp import web

from audio_reactive.null_analyzer import NullAnalyzer
from audio_reactive.synthetic_analyzer import SyntheticAnalyzer
from now_playing.mock_source import MockSource
from now_playing.poller import NowPlayingPoller
from transport.server import build_app

HOST = "127.0.0.1"
PORT = 8765
READY_ATTEMPTS = 100
READY_INTERVAL = 0.1


def _real_analyzer():
    try:
        from audio_reactive.loopback_analyzer import LoopbackAnalyzer

        return LoopbackAnalyzer()
    except ImportError as exc:
        print(f"audio capture unavailable: {exc}")
        return NullAnalyzer()


async def _open_when_ready(url: str, port: int) -> None:
    for _ in range(READY_ATTEMPTS):
        try:
            _, writer = await asyncio.open_connection(HOST, port)
        except OSError:
            await asyncio.sleep(READY_INTERVAL)
            continue
        writer.close()
        break
    webbrowser.open(url)


def _web_dir() -> Path | None:
    if getattr(sys, "frozen", False):
        candidate = Path(sys._MEIPASS) / "web"
    else:
        candidate = Path(__file__).resolve().parent.parent / "dist"
    return candidate if (candidate / "index.html").exists() else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Apple Music now playing bridge")
    parser.add_argument("--mock", action="store_true", help="emit fake tracks and a synthetic beat")
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--no-browser", action="store_true", help="do not open the web view")
    args = parser.parse_args()

    if args.mock:
        poller = NowPlayingPoller(MockSource(), use_itunes=False)
        analyzer = SyntheticAnalyzer()
    else:
        from now_playing.smtc_source import SmtcSource

        poller = NowPlayingPoller(SmtcSource())
        analyzer = _real_analyzer()

    web_dir = _web_dir()
    app = build_app(poller, analyzer, web_dir)
    url = f"http://localhost:{args.port}"
    if web_dir and not args.no_browser:

        async def open_browser(application: web.Application) -> None:
            application["browser_task"] = asyncio.create_task(_open_when_ready(url, args.port))

        app.on_startup.append(open_browser)
    if web_dir:
        print(f"Display Album Cover running at {url}. Close this window to quit.")

    web.run_app(app, host=HOST, port=args.port, print=None if web_dir else print)


if __name__ == "__main__":
    main()
