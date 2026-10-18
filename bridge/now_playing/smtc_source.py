from dataclasses import dataclass

from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as Manager,
)
from winrt.windows.storage.streams import DataReader

APP_ID_HINT = "applemusic"
PLAYING = 4
PAUSED = 5


@dataclass
class SmtcSnapshot:
    title: str
    artist: str
    album: str
    status: str
    position: float
    duration: float
    thumbnail: bytes | None
    genre: str | None = None


async def _read_thumbnail(props) -> bytes | None:
    ref = props.thumbnail
    if not ref:
        return None
    try:
        stream = await ref.open_read_async()
        reader = DataReader(stream)
        await reader.load_async(stream.size)
        buf = bytearray(stream.size)
        reader.read_bytes(buf)
        return bytes(buf)
    except OSError:
        return None


ARTIST_ALBUM_SEPARATOR = " — "


def _split_artist_album(artist: str, album: str) -> tuple[str, str]:
    if album or ARTIST_ALBUM_SEPARATOR not in artist:
        return artist, album
    name, _, album_name = artist.partition(ARTIST_ALBUM_SEPARATOR)
    return name, album_name


def _status_name(code: int) -> str:
    return {PLAYING: "playing", PAUSED: "paused"}.get(int(code), "stopped")


class SmtcSource:
    def __init__(self) -> None:
        self._manager = None

    async def read(self, with_thumbnail: bool) -> SmtcSnapshot | None:
        if self._manager is None:
            self._manager = await Manager.request_async()
        for session in self._manager.get_sessions():
            if APP_ID_HINT not in session.source_app_user_model_id.lower():
                continue
            props = await session.try_get_media_properties_async()
            if not props.title:
                return None
            timeline = session.get_timeline_properties()
            artist, album = _split_artist_album(props.artist, props.album_title)
            return SmtcSnapshot(
                title=props.title,
                artist=artist,
                album=album,
                status=_status_name(session.get_playback_info().playback_status),
                position=timeline.position.total_seconds(),
                duration=timeline.end_time.total_seconds(),
                thumbnail=await _read_thumbnail(props) if with_thumbnail else None,
            )
        return None
