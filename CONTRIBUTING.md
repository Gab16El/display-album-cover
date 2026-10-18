# Contributing

Thanks for wanting to improve Display Album Cover. Issues and pull requests are welcome.

## Before you start

- Open an issue first for anything big, so we can agree on the direction before you spend time on it.
- The app reads Apple Music for Windows through the Windows media session, so it only runs on Windows 10 and 11. The web part runs anywhere.
- Small, focused pull requests are easier to review than large ones.

## Setup

```bash
git clone https://github.com/Gab16El/display-album-cover.git
cd display-album-cover
yarn install

cd bridge
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py --mock   # fake tracks and a synthetic beat, no Apple Music needed
```

In another terminal, from the project root:

```bash
yarn dev
```

## Checks

Run these before opening a pull request. CI runs the same ones.

```bash
yarn lint
yarn build

cd bridge
.venv\Scripts\pip install -r requirements-test.txt
.venv\Scripts\python -m pytest -q
```

If you change the audio analysis, the tempo tracking, the palette or the access rules, add or update a test in `bridge/tests/`.

## Conventions

- **No emojis**, in code, docs or commit messages.
- **Short comments.** Prefer clear names over explanations. Comment the why, not the what.
- **Screaming architecture.** Code is grouped by what it does, not by technical type. On the web side that means `src/features/<name>/` with its own `model`, `api`, `lib` and `ui`; shared helpers go in `src/shared/`. On the bridge side, folders like `now_playing/`, `audio_reactive/`, `launcher/` and `transport/`.
- **Conventional Commits**: `feat(scope): ...`, `fix(scope): ...`, `docs: ...`, `chore: ...`.
- **Match the surrounding style** instead of introducing a new one.

## Privacy and legal

- Do not commit personal data: local paths, emails, tokens, IP addresses.
- Do not commit album artwork or other copyrighted media. The app fetches covers at runtime and the mock source draws its own.
- By contributing you agree that your work is released under the project's [MIT license](LICENSE).
- Security problems: please report them privately through the repository's Security tab instead of opening a public issue.

## Pull requests

1. Fork the repository and create a branch from `main`.
2. Make your change and run the checks above.
3. Open a pull request and fill in the template.
4. Be ready to adjust things after review. Not every proposal will be merged, and that is fine.
