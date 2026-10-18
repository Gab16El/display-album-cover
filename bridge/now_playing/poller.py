import asyncio
import hashlib
from collections.abc import Awaitable, Callable

from .itunes_cover import fetch_cover
from .palette import extract_palette
from .smtc_source import SmtcSnapshot
from .track import NowPlayingState, Track

POLL_SECONDS = 1.0


class NowPlayingPoller:
    def __init__(self, source, use_itunes: bool = True) -> None:
        self._source = source
        self._use_itunes = use_itunes
        self._track_key: str | None = None
        self.state = NowPlayingState()
        self.cover: bytes | None = None
        self._listeners: list[Callable[[dict], Awaitable[None]]] = []

    def subscribe(self, listener: Callable[[dict], Awaitable[None]]) -> None:
        self._listeners.append(listener)

    async def _load_cover(self, track: Track, snapshot: SmtcSnapshot) -> None:
        cover = await fetch_cover(track) if self._use_itunes else None
        self.cover = cover or snapshot.thumbnail
        if self.cover:
            self.state.palette = extract_palette(self.cover)
            self.state.cover_version = hashlib.sha1(self.cover).hexdigest()[:10]
        else:
            self.state.palette = None
            self.state.cover_version = None

    async def _tick(self) -> None:
        probe = await self._source.read(with_thumbnail=False)
        if probe is None:
            self._track_key = None
            self.state = NowPlayingState()
            self.cover = None
        else:
            track = Track(probe.title, probe.artist, probe.album)
            if track.key != self._track_key:
                self._track_key = track.key
                full = await self._source.read(with_thumbnail=True) or probe
                self.state = NowPlayingState(track=track)
                await self._load_cover(track, full)
            self.state.status = probe.status
            self.state.position = probe.position
            self.state.duration = probe.duration
        payload = self.state.to_dict()
        for listener in self._listeners:
            await listener(payload)

    async def run(self) -> None:
        while True:
            try:
                await self._tick()
            except OSError as exc:
                print(f"poll error: {exc}")
            await asyncio.sleep(POLL_SECONDS)
