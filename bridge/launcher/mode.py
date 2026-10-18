from enum import Enum


class LaunchMode(Enum):
    PC = "pc"
    PHONE = "phone"
    BOTH = "both"

    @property
    def serves_lan(self) -> bool:
        return self in (LaunchMode.PHONE, LaunchMode.BOTH)

    @property
    def opens_browser(self) -> bool:
        return self in (LaunchMode.PC, LaunchMode.BOTH)


CHOICES = {
    "1": (LaunchMode.PC, "Open here on this PC (browser)"),
    "2": (LaunchMode.PHONE, "Show a QR code for a phone or tablet"),
    "3": (LaunchMode.BOTH, "Both"),
}
DEFAULT_CHOICE = "1"


def ask_launch_mode() -> LaunchMode:
    print("Display Album Cover\n")
    for key, (_, label) in CHOICES.items():
        print(f"  {key}) {label}")
    while True:
        try:
            answer = input(f"\nChoose 1, 2 or 3 [{DEFAULT_CHOICE}]: ").strip() or DEFAULT_CHOICE
        except EOFError:
            return CHOICES[DEFAULT_CHOICE][0]
        if answer in CHOICES:
            print()
            return CHOICES[answer][0]
        print("Please type 1, 2 or 3.")


def resolve_launch_mode(requested: str | None, lan_flag: bool, interactive: bool) -> LaunchMode:
    if requested:
        return LaunchMode(requested)
    if lan_flag:
        return LaunchMode.BOTH
    return ask_launch_mode() if interactive else LaunchMode.PC
