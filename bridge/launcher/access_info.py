import socket
import sys

from .mode import LaunchMode


def lan_address() -> str | None:
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("10.255.255.255", 1))
        return probe.getsockname()[0]
    except OSError:
        return None
    finally:
        probe.close()


def _print_qr(url: str) -> None:
    try:
        import qrcode

        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        code = qrcode.QRCode(border=1)
        code.add_data(url)
        code.print_ascii(invert=True)
    except (ImportError, OSError):
        pass


def print_banner(mode: LaunchMode, port: int, lan_url: str | None) -> None:
    print("Display Album Cover")
    if mode.opens_browser:
        print(f"  This PC : http://localhost:{port}")
    if mode.serves_lan:
        if lan_url:
            print(f"  Phone   : {lan_url}")
            print("  Scan the code below with your phone (same WiFi network).")
            _print_qr(lan_url)
            print("  The token is secret and changes on every run.")
        else:
            print("  Could not find a network address for other devices.")
    print("  Close this window to quit.")
