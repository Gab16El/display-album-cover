import argparse
import asyncio
import secrets
import socket
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


def _lan_address() -> str | None:
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("10.255.255.255", 1))
        return probe.getsockname()[0]
    except OSError:
        return None
    finally:
        probe.close()


def _print_qr(url: str) -> None:
    try:
        import qrcode

        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        code = qrcode.QRCode(border=1)
        code.add_data(url)
        code.print_ascii(invert=True)
    except (ImportError, OSError):
        pass


def _print_banner(port: int, lan_url: str | None) -> None:
    print("Display Album Cover")
    print(f"  This PC : http://localhost:{port}")
    if lan_url:
        print(f"  Phone   : {lan_url}")
        print("  Scan the code below with your phone (same WiFi network).")
        _print_qr(lan_url)
        print("  The token is secret and changes on every run. Close this window to quit.")
    else:
        print("  Close this window to quit.")


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
    parser.add_argument("--lan", action="store_true", help="also serve other devices on your WiFi")
    parser.add_argument("--token", help="access token for --lan (random by default)")
    args = parser.parse_args()

    if args.mock:
        poller = NowPlayingPoller(MockSource(), use_itunes=False)
        analyzer = SyntheticAnalyzer()
    else:
        from now_playing.smtc_source import SmtcSource

        poller = NowPlayingPoller(SmtcSource())
        analyzer = _real_analyzer()

    web_dir = _web_dir()
    token = (args.token or secrets.token_urlsafe(TOKEN_BYTES)) if args.lan else None
    app = build_app(poller, analyzer, web_dir, token)
    url = f"http://localhost:{args.port}"
    lan_ip = _lan_address() if args.lan else None
    lan_url = f"http://{lan_ip}:{args.port}/?token={token}" if lan_ip and web_dir else None
    if web_dir and not args.no_browser:

        async def open_browser(application: web.Application) -> None:
            application["browser_task"] = asyncio.create_task(_open_when_ready(url, args.port))

        app.on_startup.append(open_browser)
    if web_dir:
        _print_banner(args.port, lan_url)
    elif args.lan:
        print("--lan needs the built web app. Run `yarn build` first or use the executable.")

    web.run_app(
        app,
        host=LAN_HOST if args.lan else HOST,
        port=args.port,
        print=None if web_dir else print,
    )


if __name__ == "__main__":
    main()
