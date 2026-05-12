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
    "kindle11": DeviceProfile("kindle-basic-11", "Kindle Basic 11th generation", 1072, 1448),
    "k11": DeviceProfile("kindle-basic-11", "Kindle Basic 11th generation", 1072, 1448),
    "kindle": DeviceProfile("kindle", "Kindle", 600, 800),
    "kindle-basic": DeviceProfile("kindle", "Kindle", 600, 800),
    "kindle-basic-10": DeviceProfile("kindle-basic-10", "Kindle Basic 10th generation", 600, 800),
    "kindle-basic-11": DeviceProfile("kindle-basic-11", "Kindle Basic 11th generation", 1072, 1448),
    "kindle-basic-12": DeviceProfile("kindle-basic-12", "Kindle Basic 12th generation", 1072, 1448),
    "kindle-dx": DeviceProfile("kindle-dx", "Kindle DX", 824, 1200),
    "kindle-paperwhite": DeviceProfile("kindle-paperwhite-12", "Kindle Paperwhite 12th generation", 1264, 1680),
    "kindle-paperwhite-7": DeviceProfile("kindle-paperwhite-7", "Kindle Paperwhite 7th generation", 1072, 1448),
    "kindle-paperwhite-10": DeviceProfile("kindle-paperwhite-10", "Kindle Paperwhite 10th generation", 1072, 1448),
    "kindle-paperwhite-11": DeviceProfile("kindle-paperwhite-11", "Kindle Paperwhite 11th generation", 1236, 1648),
    "kindle-paperwhite-12": DeviceProfile("kindle-paperwhite-12", "Kindle Paperwhite 12th generation", 1264, 1680),
    "kindle-paperwhite-3": DeviceProfile("kindle-paperwhite-3", "Kindle Paperwhite 3", 1072, 1448),
    "kindle-oasis": DeviceProfile("kindle-oasis", "Kindle Oasis", 1264, 1680),
    "kindle-oasis-8": DeviceProfile("kindle-oasis-8", "Kindle Oasis 8th generation", 1080, 1440),
    "kindle-oasis-9": DeviceProfile("kindle-oasis-9", "Kindle Oasis 9th generation", 1264, 1680),
    "kindle-oasis-10": DeviceProfile("kindle-oasis-10", "Kindle Oasis 10th generation", 1264, 1680),
    "kindle-voyage": DeviceProfile("kindle-voyage", "Kindle Voyage", 1080, 1440),
    "kindle-scribe": DeviceProfile("kindle-scribe", "Kindle Scribe", 1860, 2480),
    "kindle-scribe-11": DeviceProfile("kindle-scribe-11", "Kindle Scribe 11th generation", 1860, 2480),
    "kindle-scribe-12": DeviceProfile("kindle-scribe-12", "Kindle Scribe 12th generation", 1860, 2480),
    "kindle-scribe-2025": DeviceProfile("kindle-scribe-2025", "Kindle Scribe 2025", 1980, 2640),
    "kindle-scribe-colorsoft-2025": DeviceProfile("kindle-scribe-colorsoft-2025", "Kindle Scribe Colorsoft 2025", 1980, 2640, grayscale_levels=256),
    "kindle-colorsoft-12": DeviceProfile("kindle-colorsoft-12", "Kindle Colorsoft 12th generation", 1264, 1680, grayscale_levels=256),
    "kindle-fire": DeviceProfile("kindle-fire", "Kindle Fire", 1200, 1920, grayscale_levels=256),
    "generic-eink": DeviceProfile("generic-eink", "Generic e-ink", 600, 800),
    "generic-hd-eink": DeviceProfile("generic-hd-eink", "Generic HD e-ink", 1072, 1448),
    "generic-large-eink": DeviceProfile("generic-large-eink", "Generic large e-ink", 1404, 1872),
    "kobo": DeviceProfile("kobo", "Kobo", 1080, 1440),
    "kobo-nia": DeviceProfile("kobo-nia", "Kobo Nia", 758, 1024),
    "kobo-clara-hd": DeviceProfile("kobo-clara-hd", "Kobo Clara HD", 1072, 1448),
    "kobo-clara-2e": DeviceProfile("kobo-clara-2e", "Kobo Clara 2E", 1072, 1448),
    "kobo-clara-bw": DeviceProfile("kobo-clara-bw", "Kobo Clara BW", 1072, 1448),
    "kobo-clara-colour": DeviceProfile("kobo-clara-colour", "Kobo Clara Colour", 1072, 1448, grayscale_levels=256),
    "kobo-libra-2": DeviceProfile("kobo-libra-2", "Kobo Libra 2", 1264, 1680),
    "kobo-libra-colour": DeviceProfile("kobo-libra-colour", "Kobo Libra Colour", 1264, 1680, grayscale_levels=256),
    "kobo-sage": DeviceProfile("kobo-sage", "Kobo Sage", 1440, 1920),
    "kobo-elipsa": DeviceProfile("kobo-elipsa", "Kobo Elipsa", 1404, 1872),
    "kobo-elipsa-2e": DeviceProfile("kobo-elipsa-2e", "Kobo Elipsa 2E", 1404, 1872),
    "pocketbook-900": DeviceProfile("pocketbook-900", "PocketBook 900", 825, 1200),
    "pocketbook-pro-912": DeviceProfile("pocketbook-pro-912", "PocketBook Pro 912", 825, 1200),
    "pocketbook-touch-lux-5": DeviceProfile("pocketbook-touch-lux-5", "PocketBook Touch Lux 5", 758, 1024),
    "pocketbook-verse-pro": DeviceProfile("pocketbook-verse-pro", "PocketBook Verse Pro", 1072, 1448),
    "pocketbook-era": DeviceProfile("pocketbook-era", "PocketBook Era", 1264, 1680),
    "pocketbook-inkpad-3": DeviceProfile("pocketbook-inkpad-3", "PocketBook InkPad 3", 1404, 1872),
    "pocketbook-inkpad-lux": DeviceProfile("pocketbook-inkpad-lux", "PocketBook InkPad Lux", 1200, 1600),
    "pocketbook-inkpad-hd": DeviceProfile("pocketbook-inkpad-hd", "PocketBook InkPad HD", 1440, 1920),
    "pocketbook-inkpad-color-3": DeviceProfile("pocketbook-inkpad-color-3", "PocketBook InkPad Color 3", 1404, 1872, grayscale_levels=256),
    "pocketbook-inkpad-x": DeviceProfile("pocketbook-inkpad-x", "PocketBook InkPad X", 1404, 1872),
    "nook": DeviceProfile("nook", "Nook", 600, 800),
    "nook-glowlight-4": DeviceProfile("nook-glowlight-4", "Nook GlowLight 4", 1072, 1448),
    "nook-glowlight-4-plus": DeviceProfile("nook-glowlight-4-plus", "Nook GlowLight 4 Plus", 1404, 1872),
    "nook-color": DeviceProfile("nook-color", "Nook Color", 600, 1024, grayscale_levels=256),
    "nook-hd-plus": DeviceProfile("nook-hd-plus", "Nook HD Plus", 1280, 1920, grayscale_levels=256),
    "sony": DeviceProfile("sony", "Sony Reader", 600, 800),
    "sony-300": DeviceProfile("sony-300", "Sony 300", 600, 800),
    "sony-900": DeviceProfile("sony-900", "Sony 900", 600, 1024),
    "sony-landscape": DeviceProfile("sony-landscape", "Sony Landscape", 800, 600),
    "sony-t3": DeviceProfile("sony-t3", "Sony T3", 758, 1024),
    "ipad": DeviceProfile("ipad", "Apple iPad", 1536, 2048, grayscale_levels=256),
    "ipad-3": DeviceProfile("ipad-3", "Apple iPad 3", 1536, 2048, grayscale_levels=256),
    "galaxy": DeviceProfile("galaxy", "Galaxy", 1200, 1920, grayscale_levels=256),
    "tablet": DeviceProfile("tablet", "Tablet", 1200, 1920, grayscale_levels=256),
    "tablet-compact": DeviceProfile("tablet-compact", "Compact tablet", 1200, 1920, grayscale_levels=256),
    "tablet-large": DeviceProfile("tablet-large", "Large tablet", 1600, 2560, grayscale_levels=256),
    "android-eink-6": DeviceProfile("android-eink-6", "Android e-ink 6 inch", 1072, 1448),
    "android-eink-7": DeviceProfile("android-eink-7", "Android e-ink 7 inch", 1264, 1680),
    "android-eink-10": DeviceProfile("android-eink-10", "Android e-ink 10 inch", 1404, 1872),
    "boox-palma": DeviceProfile("boox-palma", "Boox Palma", 824, 1648),
    "boox-note-air": DeviceProfile("boox-note-air", "Boox Note Air", 1404, 1872),
    "cybook-3": DeviceProfile("cybook-3", "Cybook 3", 600, 800),
    "cybook-opus": DeviceProfile("cybook-opus", "Cybook Opus", 600, 800),
    "ectaco-jetbook": DeviceProfile("ectaco-jetbook", "Ectaco jetBook", 600, 800),
    "hanlin-v3": DeviceProfile("hanlin-v3", "Hanlin V3", 600, 800),
    "hanlin-v5": DeviceProfile("hanlin-v5", "Hanlin V5", 600, 800),
    "iliad": DeviceProfile("iliad", "iLiad", 768, 1024),
    "irexdr800": DeviceProfile("irexdr800", "IrexDR800", 768, 1024),
    "irexdr1000": DeviceProfile("irexdr1000", "IrexDR1000", 1024, 1280),
    "jetbook": DeviceProfile("jetbook", "jetBook", 600, 800),
    "mobipocket": DeviceProfile("mobipocket", "Mobipocket", 600, 800),
    "ms-reader": DeviceProfile("ms-reader", "MS Reader", 600, 800),
}


def get_profile(name: str) -> DeviceProfile:
    try:
        return PROFILES[name.lower()]
    except KeyError as exc:
        available = ", ".join(sorted(PROFILES))
        raise ValueError(f"Unknown profile '{name}'. Available profiles: {available}") from exc
