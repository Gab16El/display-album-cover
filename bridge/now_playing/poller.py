import asyncio
import hashlib
import traceback
from collections.abc import Awaitable, Callable

from .itunes_cover import CoverResult, lookup_cover
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
        found = await lookup_cover(track) if self._use_itunes else CoverResult(None, None)
        self.cover = found.image or snapshot.thumbnail
        self.state.genre = found.genre or snapshot.genre
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
            except Exception:
                traceback.print_exc()
            await asyncio.sleep(POLL_SECONDS)
