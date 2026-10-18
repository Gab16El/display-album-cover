import asyncio
import json
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


def _find_match(track: Track) -> dict | None:
    term = urllib.parse.quote(f"{track.title} {track.artist}")
    data = json.loads(_get(f"{SEARCH_URL}?term={term}&entity=song&limit=5"))
    results = data.get("results", [])
    album = track.album.lower()
    best = next((r for r in results if r.get("collectionName", "").lower() == album), None)
    return best or (results[0] if results else None)


def _lookup(track: Track) -> CoverResult:
    try:
        match = _find_match(track)
        if not match:
            return CoverResult(None, None)
        url = match.get("artworkUrl100", "").replace("100x100bb", "1000x1000bb")
        return CoverResult(_get(url) if url else None, match.get("primaryGenreName"))
    except (OSError, ValueError):
        return CoverResult(None, None)


async def lookup_cover(track: Track) -> CoverResult:
    return await asyncio.to_thread(_lookup, track)
