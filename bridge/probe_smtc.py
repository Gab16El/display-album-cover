"""Prueba de viabilidad: lista las sesiones multimedia de Windows (SMTC)
y muestra lo que publica cada una (título, artista, álbum, portada)."""
import asyncio

from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as Manager,
)


async def main() -> None:
    manager = await Manager.request_async()
    sessions = manager.get_sessions()
    if sessions.size == 0:
        print("No hay sesiones multimedia activas. Reproduce algo en Apple Music.")
        return
    for s in sessions:
        props = await s.try_get_media_properties_async()
        status = s.get_playback_info().playback_status
        print(f"app      : {s.source_app_user_model_id}")
        print(f"estado   : {status}")
        print(f"titulo   : {props.title}")
        print(f"artista  : {props.artist}")
        print(f"album    : {props.album_title}")
        print(f"portada  : {'si' if props.thumbnail else 'no'}")
        print("-" * 30)


asyncio.run(main())
