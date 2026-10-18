from .levels import AudioLevels


class NullAnalyzer:
    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def snapshot(self) -> AudioLevels:
        return AudioLevels()
