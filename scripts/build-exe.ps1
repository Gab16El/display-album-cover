$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

yarn install --frozen-lockfile
yarn build

$python = Join-Path $root 'bridge\.venv\Scripts\python.exe'
& $python -m pip install --quiet pyinstaller

& $python -m PyInstaller (Join-Path $root 'bridge\main.py') `
    --name DisplayAlbumCover `
    --onefile `
    --icon (Join-Path $root 'assets\branding\app-icon.ico') `
    --noconfirm `
    --paths (Join-Path $root 'bridge') `
    --add-data "$(Join-Path $root 'dist');web" `
    --collect-all winrt `
    --collect-submodules winrt `
    --hidden-import audio_reactive.loopback_analyzer `
    --distpath (Join-Path $root 'release') `
    --workpath (Join-Path $root 'release\build') `
    --specpath (Join-Path $root 'release')

if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed' }
Write-Host 'Built release\DisplayAlbumCover.exe'
