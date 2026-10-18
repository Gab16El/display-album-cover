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

This builds the web app, bundles it with the bridge using PyInstaller and writes `release\DisplayAlbumCover.exe`.

## Run the executable

Double click it and choose how to view it:

```
1) Open here on this PC (browser)
2) Show a QR code for a phone or tablet
3) Both
```

For a phone or tablet the console prints a QR code and a link with a secret token. Scan it with a device on the same WiFi network. The token changes on every run, other devices need it, and this PC does not. Windows may ask to allow the app on private networks the first time, and guest networks that isolate devices will not work.

Skip the question with options: `--mode pc|phone|both`, `--no-browser`, `--port 8765`, `--token <fixed token>`. `--lan` is the same as `--mode both`. The bridge only accepts WebSocket connections from its own origin or from localhost.

Keeping the screen on: on this PC the page asks the browser to stay awake by itself. On a phone or tablet the connection is plain HTTP, so the browser does not allow that directly. The page shows a small hint, and one tap starts a hidden looping video (`nosleep.js`) that keeps the screen awake. If a device still goes to sleep, set auto-lock to never (iPhone) or turn on Stay awake while charging (Android developer options).

On iPhone use Share, then Add to Home Screen for a full-screen view without the browser bar.

## Branding

Logo files live in `assets/branding/`: the iridescent and `currentColor` marks, light and dark lockups, the app icon tile and `app-icon.ico`, used for the executable. The favicon is the app icon tile.

## Structure

```
bridge/
  now_playing/     SMTC reader, cover lookup, palette, poller
  launcher/        startup mode prompt, QR and access banner
  audio_reactive/  loopback capture and band analysis
  transport/       HTTP and WebSocket server
src/
  app/           store, hooks, root component
  features/
    now-playing/        slice, socket middleware, screen components
    ambient-background/ animated color background
    audio-input/        audio levels socket and shared state
    keep-awake/         keeps the screen from sleeping
    visualizer/         WebGL shader, pulse pool, genre presets
    fullscreen/         fullscreen toggle
  shared/        config and small helpers
```

The background is a WebGL2 shader that warps the cover and reacts to system audio (WASAPI loopback, bass/mid/treble and beat sent over `/audio`). The visual preset depends on the genre returned by iTunes. With `--mock` the bridge emits a synthetic beat.

Covers are resolved through the public iTunes Search API, falling back to the SMTC thumbnail.

## Privacy

Everything runs on your PC. The only thing that leaves it is the track title and artist, sent to the public Apple iTunes Search API to find the album cover and genre. System audio is analyzed locally to drive the animation and is never recorded or sent anywhere. When you share the view with a phone or tablet, it is served only on your local network and protected by a secret token; the default mode (`--mode pc`) does not expose anything to the network.

## Disclaimer

This is an independent project and is not affiliated with, endorsed by or sponsored by Apple Inc. Apple and Apple Music are trademarks of Apple Inc. Album artwork shown by the app belongs to its respective owners and is fetched at runtime; none is stored in this repository.

## License

MIT, see [LICENSE](LICENSE).
