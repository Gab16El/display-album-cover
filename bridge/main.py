import argparse
import asyncio
import secrets
import sys
import webbrowser
from pathlib import Path

from aiohttp import web

from audio_reactive.null_analyzer import NullAnalyzer
from audio_reactive.synthetic_analyzer import SyntheticAnalyzer
from launcher.access_info import lan_address, print_banner
from launcher.mode import LaunchMode, resolve_launch_mode
from now_playing.mock_source import MockSource
from now_playing.poller import NowPlayingPoller
from transport.server import build_app

HOST = "127.0.0.1"
LAN_HOST = "0.0.0.0"
TOKEN_BYTES = 16
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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apple Music now playing bridge")
    parser.add_argument("--mock", action="store_true", help="emit fake tracks and a synthetic beat")
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument(
        "--mode",
        choices=[mode.value for mode in LaunchMode],
        help="pc: browser here, phone: QR for other devices, both. Asked at startup if omitted",
    )
    parser.add_argument("--no-browser", action="store_true", help="do not open the web view")
    parser.add_argument("--lan", action="store_true", help="same as --mode both")
    parser.add_argument("--token", help="access token for other devices (random by default)")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    web_dir = _web_dir()

    interactive = bool(web_dir) and sys.stdin.isatty() and not (args.mock or args.no_browser)
    mode = resolve_launch_mode(args.mode, args.lan, interactive)
    if mode.serves_lan and not web_dir:
        print("Other devices need the built web app. Run `yarn build` first or use the executable.")
        mode = LaunchMode.PC

    if args.mock:
        poller = NowPlayingPoller(MockSource(), use_itunes=False)
        analyzer = SyntheticAnalyzer()
    else:
        from now_playing.smtc_source import SmtcSource

        poller = NowPlayingPoller(SmtcSource())
        analyzer = _real_analyzer()

    token = (args.token or secrets.token_urlsafe(TOKEN_BYTES)) if mode.serves_lan else None
    app = build_app(poller, analyzer, web_dir, token)

    if web_dir and mode.opens_browser and not args.no_browser:
        url = f"http://localhost:{args.port}"

        async def open_browser(application: web.Application) -> None:
            application["browser_task"] = asyncio.create_task(_open_when_ready(url, args.port))

        app.on_startup.append(open_browser)

    if web_dir:
        lan_ip = lan_address() if mode.serves_lan else None
        lan_url = f"http://{lan_ip}:{args.port}/?token={token}" if lan_ip else None
        print_banner(mode, args.port, lan_url)

    web.run_app(
        app,
        host=LAN_HOST if mode.serves_lan else HOST,
        port=args.port,
        print=None if web_dir else print,
    )


if __name__ == "__main__":
    main()
