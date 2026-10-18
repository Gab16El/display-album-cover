import asyncio
import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass

from .track import Track

SEARCH_URL = "https://itunes.apple.com/search"
TIMEOUT = 8


@dataclass(frozen=True)
class CoverResult:
    image: bytes | None
    genre: str | None


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "display-album-cover"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
        return res.read()


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _overlaps(a: str, b: str) -> bool:
    a, b = _norm(a), _norm(b)
    return bool(a) and bool(b) and (a in b or b in a)


def _find_match(track: Track) -> tuple[dict | None, bool]:
    term = urllib.parse.quote(f"{track.title} {track.artist}")
    data = json.loads(_get(f"{SEARCH_URL}?term={term}&entity=song&limit=10"))
    by_artist = [r for r in data.get("results", []) if _overlaps(track.artist, r.get("artistName", ""))]
    same_album = next((r for r in by_artist if _overlaps(track.album, r.get("collectionName", ""))), None)
    if same_album:
        return same_album, True
    return (by_artist[0] if by_artist else None), False


def _lookup(track: Track) -> CoverResult:
    try:
        match, album_matches = _find_match(track)
        if not match:
            return CoverResult(None, None)
        genre = match.get("primaryGenreName")
        url = match.get("artworkUrl100", "").replace("100x100bb", "1000x1000bb")
        return CoverResult(_get(url) if url and album_matches else None, genre)
    except (OSError, ValueError):
        return CoverResult(None, None)


async def lookup_cover(track: Track) -> CoverResult:
    return await asyncio.to_thread(_lookup, track)
