import asyncio
import json
import urllib.parse
import urllib.request

from .track import Track

SEARCH_URL = "https://itunes.apple.com/search"
TIMEOUT = 8


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "display-album-cover"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
        return res.read()


def _find_cover_url(track: Track) -> str | None:
    term = urllib.parse.quote(f"{track.title} {track.artist}")
    data = json.loads(_get(f"{SEARCH_URL}?term={term}&entity=song&limit=5"))
    results = data.get("results", [])
    album = track.album.lower()
    best = next((r for r in results if r.get("collectionName", "").lower() == album), None)
    best = best or (results[0] if results else None)
    if not best or "artworkUrl100" not in best:
        return None
    return best["artworkUrl100"].replace("100x100bb", "1000x1000bb")


def _fetch_cover(track: Track) -> bytes | None:
    try:
        url = _find_cover_url(track)
        return _get(url) if url else None
    except (OSError, ValueError):
        return None


async def fetch_cover(track: Track) -> bytes | None:
    return await asyncio.to_thread(_fetch_cover, track)
