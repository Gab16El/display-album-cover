import argparse

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Apple Music now playing bridge")
    parser.add_argument("--mock", action="store_true", help="emit fake tracks and a synthetic beat")
    parser.add_argument("--port", type=int, default=PORT)
    args = parser.parse_args()

    if args.mock:
        poller = NowPlayingPoller(MockSource(), use_itunes=False)
        analyzer = SyntheticAnalyzer()
    else:
        from now_playing.smtc_source import SmtcSource

        poller = NowPlayingPoller(SmtcSource())
        analyzer = _real_analyzer()

    web.run_app(build_app(poller, analyzer), host=HOST, port=args.port)


if __name__ == "__main__":
    main()
