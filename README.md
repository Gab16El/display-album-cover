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

## Structure

```
bridge/
  now_playing/   SMTC reader, cover lookup, palette, poller
  transport/     HTTP and WebSocket server
src/
  app/           store, hooks, root component
  features/
    now-playing/        slice, socket middleware, screen components
    ambient-background/ animated color background
    fullscreen/         fullscreen toggle
  shared/        config and small helpers
```

Covers are resolved through the public iTunes Search API, falling back to the SMTC thumbnail.
