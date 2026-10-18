# display-album-cover

Shows the song playing in Apple Music for Windows as a full-screen web view that adopts the colors of the album cover. A later phase targets an ESP32 display.

```
Apple Music (Windows SMTC) -> Python bridge -> WebSocket -> React web app
```

## Requirements

- Windows 10/11 with the Apple Music app (Microsoft Store)
- Node 20+ and Python 3.11+

## Run

Bridge:

```bash
cd bridge
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py          # real Apple Music
.venv\Scripts\python main.py --mock   # fake tracks for UI work
```

Web:

```bash
yarn install
yarn dev
```

The web app connects to `ws://localhost:8765/ws`. Override with `VITE_BRIDGE_HOST`.

## Build the executable

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-exe.ps1
```

This builds the web app, bundles it with the bridge using PyInstaller and writes `release\DisplayAlbumCover.exe`. Run it and the browser opens at `http://localhost:8765`. Use `--no-browser` to skip that and `--port` to change the port. The bridge only accepts WebSocket connections from local origins.

## Structure

```
bridge/
  now_playing/     SMTC reader, cover lookup, palette, poller
  audio_reactive/  loopback capture and band analysis
  transport/       HTTP and WebSocket server
src/
  app/           store, hooks, root component
  features/
    now-playing/        slice, socket middleware, screen components
    ambient-background/ animated color background
    audio-input/        audio levels socket and shared state
    visualizer/         WebGL shader, pulse pool, genre presets
    fullscreen/         fullscreen toggle
  shared/        config and small helpers
```

The background is a WebGL2 shader that warps the cover and reacts to system audio (WASAPI loopback, bass/mid/treble and beat sent over `/audio`). The visual preset depends on the genre returned by iTunes. With `--mock` the bridge emits a synthetic beat.

Covers are resolved through the public iTunes Search API, falling back to the SMTC thumbnail.
