import argparse

from aiohttp import web

from now_playing.mock_source import MockSource
from now_playing.poller import NowPlayingPoller
from transport.server import build_app

HOST = "127.0.0.1"
PORT = 8765


def main() -> None:
    parser = argparse.ArgumentParser(description="Apple Music now playing bridge")
    parser.add_argument("--mock", action="store_true", help="emit fake tracks")
    parser.add_argument("--port", type=int, default=PORT)
    args = parser.parse_args()

    if args.mock:
        poller = NowPlayingPoller(MockSource(), use_itunes=False)
    else:
        from now_playing.smtc_source import SmtcSource

        poller = NowPlayingPoller(SmtcSource())

    web.run_app(build_app(poller), host=HOST, port=args.port)


if __name__ == "__main__":
    main()
