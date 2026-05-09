from __future__ import annotations

import textwrap
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .images import ImageOptions, normalize_image, process_image
from .profiles import DeviceProfile


@dataclass(frozen=True)
class BookMetadata:
    title: str
    author: str = "Unknown"
    series: str = ""
    volume: str = ""
    language: str = "pt-BR"
    publisher: str = ""
    description: str = ""


PALETTE = {
    "rich_black": "#000F01",
    "dark_green": "#032221",
    "bangladesh_green": "#03624C",
    "mountain_meadow": "#2CC295",
    "caribbean_green": "#00DF81",
    "anti_flash_white": "#F5F9F6",
    "pine": "#063D2B",
    "basil": "#06433A",
    "forest": "#095544",
    "frog": "#17876D",
    "mint": "#2FA56C",
    "stone": "#707D7D",
    "pistachio": "#AACBC4",
}


def make_generated_cover(metadata: BookMetadata, profile: DeviceProfile) -> Image.Image:
    image = Image.new("RGB", (profile.width, profile.height), PALETTE["rich_black"])
    draw = ImageDraw.Draw(image)
    margin = int(profile.width * 0.08)
    accent_width = int(profile.width * 0.075)

    draw.rectangle((0, 0, profile.width, profile.height), fill=PALETTE["dark_green"])
    draw.rectangle((0, 0, accent_width, profile.height), fill=PALETTE["caribbean_green"])
    draw.rectangle((accent_width, 0, profile.width, int(profile.height * 0.18)), fill=PALETTE["bangladesh_green"])
    draw.rectangle(
        (profile.width - int(profile.width * 0.32), 0, profile.width, profile.height),
        fill=PALETTE["pine"],
    )

    title_font = _font(82)
    subtitle_font = _font(34)
    small_font = _font(27)
    label_font = _font(22)

    y = int(profile.height * 0.25)
    for line in _wrap(metadata.title or "Sem titulo", 13):
        draw.text((margin + accent_width, y), line, fill=PALETTE["anti_flash_white"], font=title_font)
        y += 96

    if metadata.series or metadata.volume:
        series = metadata.series or "Volume"
        volume = f"Vol. {metadata.volume}" if metadata.volume else ""
        draw.text(
            (margin + accent_width, y + 20),
            f"{series} {volume}".strip(),
            fill=PALETTE["mountain_meadow"],
            font=subtitle_font,
        )

    footer_y = profile.height - int(profile.height * 0.18)
    draw.text((margin + accent_width, footer_y), "Kindle Forge", fill=PALETTE["pistachio"], font=label_font)
    draw.text((margin + accent_width, footer_y + 48), metadata.author or "Unknown", fill=PALETTE["anti_flash_white"], font=small_font)
    return image


def prepare_cover_image(path: Path, options: ImageOptions) -> Image.Image:
    cover_options = ImageOptions(
        profile=options.profile,
        mode=options.mode,
        crop=options.crop,
        split_spreads=False,
        color=options.color,
        dither=options.dither,
        upscale=options.upscale,
        gamma=options.gamma,
    )
    with Image.open(path) as image:
        pages = process_image(normalize_image(image), cover_options)
    return pages[0]


def _wrap(text: str, width: int) -> list[str]:
    wrapped = textwrap.wrap(text, width=width, break_long_words=False)
    return wrapped[:5] or [text]


def _font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()
