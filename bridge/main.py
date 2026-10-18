import argparse
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


def _real_analyzer():
    try:
        from audio_reactive.loopback_analyzer import LoopbackAnalyzer

        return LoopbackAnalyzer()
    except ImportError as exc:
        print(f"audio capture unavailable: {exc}")
        return NullAnalyzer()


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
        app.on_startup.append(lambda _: webbrowser.open(url))
    if web_dir:
        print(f"Display Album Cover running at {url}. Close this window to quit.")

    web.run_app(app, host=HOST, port=args.port, print=None if web_dir else print)


if __name__ == "__main__":
    main()
