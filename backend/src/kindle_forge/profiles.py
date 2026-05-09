from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceProfile:
    key: str
    label: str
    width: int
    height: int
    grayscale_levels: int = 16

    @property
    def resolution(self) -> str:
        return f"{self.width}x{self.height}"


PROFILES: dict[str, DeviceProfile] = {
    "kindle11": DeviceProfile("kindle11", "Kindle Basic 11th generation", 1072, 1448),
    "k11": DeviceProfile("kindle11", "Kindle Basic 11th generation", 1072, 1448),
    "kindle-basic-11": DeviceProfile("kindle11", "Kindle Basic 11th generation", 1072, 1448),
}


def get_profile(name: str) -> DeviceProfile:
    try:
        return PROFILES[name.lower()]
    except KeyError as exc:
        available = ", ".join(sorted(PROFILES))
        raise ValueError(f"Unknown profile '{name}'. Available profiles: {available}") from exc
