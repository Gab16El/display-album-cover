<p align="center">
  <img src="assets/branding/mark-iridescent.svg" alt="Display Album Cover logo" width="96" />
</p>

<h1 align="center">Display Album Cover</h1>

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

This builds the web app, bundles it with the bridge using PyInstaller and writes `release\DisplayAlbumCover.exe`. Run it and the browser opens at `http://localhost:8765`. Use `--no-browser` to skip that and `--port` to change the port. The bridge only accepts WebSocket connections from its own origin or from localhost.

## Use it on your phone or tablet

Run the bridge with `--lan` (needs the built web app, so use the executable or run `yarn build` first):

```powershell
release\DisplayAlbumCover.exe --lan
```

The console prints a QR code and a link with a secret token. Scan it with a device on the same WiFi network. The token changes on every run, other devices need it, and this PC does not. Windows may ask to allow the app on private networks the first time, and guest networks that isolate devices will not work. Use `--token` to keep a fixed token.

Tips: on iPhone use Share, then Add to Home Screen for a full-screen view without the browser bar. Phones lock the screen on their own, so set auto-lock to never while it is on display.

## Branding

Logo files live in `assets/branding/`: the iridescent and `currentColor` marks, light and dark lockups, the app icon tile and `app-icon.ico`, used for the executable. The favicon is the app icon tile.

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
