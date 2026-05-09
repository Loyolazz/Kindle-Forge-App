from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageOps

from .profiles import DeviceProfile


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".bmp",
    ".tif",
    ".tiff",
}


@dataclass(frozen=True)
class ImageOptions:
    profile: DeviceProfile
    mode: str
    crop: bool = True
    split_spreads: bool = True
    color: bool = False
    dither: bool = False
    upscale: bool = True
    gamma: float = 1.0
    webtoon_overlap: int = 48


def is_image_path(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTENSIONS


def normalize_image(image: Image.Image) -> Image.Image:
    if image.mode in {"RGBA", "LA"} or (image.mode == "P" and "transparency" in image.info):
        base = Image.new("RGB", image.size, "white")
        alpha = image.convert("RGBA").getchannel("A")
        base.paste(image.convert("RGB"), mask=alpha)
        return base
    if image.mode == "RGB":
        return image
    return image.convert("RGB")


def crop_borders(image: Image.Image, tolerance: int = 12, backup: int = 8) -> Image.Image:
    if image.width < 32 or image.height < 32:
        return image

    gray = ImageOps.grayscale(image)
    samples = [
        gray.getpixel((0, 0)),
        gray.getpixel((gray.width - 1, 0)),
        gray.getpixel((0, gray.height - 1)),
        gray.getpixel((gray.width - 1, gray.height - 1)),
    ]
    background = sorted(samples)[len(samples) // 2]
    bg = Image.new("L", gray.size, background)
    diff = ImageChops.difference(gray, bg)
    mask = diff.point(lambda pixel: 255 if pixel > tolerance else 0)
    bbox = mask.getbbox()
    if not bbox:
        return image

    left, top, right, bottom = bbox
    left = max(0, left - backup)
    top = max(0, top - backup)
    right = min(image.width, right + backup)
    bottom = min(image.height, bottom + backup)

    crop_area = (right - left) * (bottom - top)
    original_area = image.width * image.height
    if crop_area < original_area * 0.18:
        return image
    if crop_area > original_area * 0.985:
        return image
    return image.crop((left, top, right, bottom))


def split_spread(image: Image.Image, reading_mode: str) -> list[Image.Image]:
    ratio = image.width / max(1, image.height)
    if ratio < 1.15:
        return [image]

    midpoint = image.width // 2
    left = image.crop((0, 0, midpoint, image.height))
    right = image.crop((midpoint, 0, image.width, image.height))
    if reading_mode == "manga":
        return [right, left]
    return [left, right]


def apply_gamma(image: Image.Image, gamma: float) -> Image.Image:
    if gamma <= 0 or abs(gamma - 1.0) < 0.001:
        return image
    inv = 1.0 / gamma
    table = [min(255, max(0, int((pixel / 255.0) ** inv * 255.0 + 0.5))) for pixel in range(256)]
    if image.mode == "L":
        return image.point(table)
    channels = image.split()
    return Image.merge(image.mode, [channel.point(table) for channel in channels])


def quantize_grayscale(image: Image.Image, levels: int, dither: bool) -> Image.Image:
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray, cutoff=0.5)
    gray = apply_gamma(gray, 1.0)
    if dither:
        palette = Image.new("P", (1, 1))
        colors: list[int] = []
        for index in range(256):
            level = round(index / 255 * (levels - 1)) * round(255 / (levels - 1))
            colors.extend([min(255, level)] * 3)
        palette.putpalette(colors)
        return gray.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG).convert("L")

    step = 255 / (levels - 1)
    return gray.point(lambda pixel: int(round(pixel / step) * step))


def fit_to_canvas(image: Image.Image, options: ImageOptions) -> Image.Image:
    profile = options.profile
    scale = min(profile.width / image.width, profile.height / image.height)
    if not options.upscale:
        scale = min(1.0, scale)
    new_width = max(1, int(round(image.width * scale)))
    new_height = max(1, int(round(image.height * scale)))
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    if options.color:
        prepared = ImageOps.autocontrast(resized.convert("RGB"), cutoff=0.5)
        prepared = apply_gamma(prepared, options.gamma)
        canvas = Image.new("RGB", (profile.width, profile.height), "white")
    else:
        prepared = ImageOps.grayscale(resized)
        prepared = ImageOps.autocontrast(prepared, cutoff=0.5)
        prepared = apply_gamma(prepared, options.gamma)
        prepared = quantize_grayscale(prepared, profile.grayscale_levels, options.dither)
        canvas = Image.new("L", (profile.width, profile.height), "white")

    x = (profile.width - prepared.width) // 2
    y = (profile.height - prepared.height) // 2
    canvas.paste(prepared, (x, y))
    return canvas


def slice_webtoon(image: Image.Image, options: ImageOptions) -> list[Image.Image]:
    profile = options.profile
    if options.crop:
        image = crop_borders(image)

    scale = profile.width / image.width
    new_height = max(1, int(round(image.height * scale)))
    strip = image.resize((profile.width, new_height), Image.Resampling.LANCZOS)
    if options.color:
        strip = ImageOps.autocontrast(strip.convert("RGB"), cutoff=0.5)
        strip = apply_gamma(strip, options.gamma)
    else:
        strip = ImageOps.grayscale(strip)
        strip = ImageOps.autocontrast(strip, cutoff=0.5)
        strip = apply_gamma(strip, options.gamma)
        strip = quantize_grayscale(strip, profile.grayscale_levels, options.dither)

    if strip.height <= profile.height:
        return [fit_to_canvas(strip, options)]

    pages: list[Image.Image] = []
    stride = max(1, profile.height - max(0, options.webtoon_overlap))
    y = 0
    while y < strip.height:
        bottom = min(strip.height, y + profile.height)
        chunk = strip.crop((0, y, profile.width, bottom))
        canvas = Image.new("RGB" if options.color else "L", (profile.width, profile.height), "white")
        canvas.paste(chunk, (0, 0))
        pages.append(canvas)
        if bottom == strip.height:
            break
        y += stride
    return pages


def process_image(image: Image.Image, options: ImageOptions) -> list[Image.Image]:
    image = normalize_image(image)

    if options.mode == "webtoon":
        return slice_webtoon(image, options)

    pieces = [image]
    if options.split_spreads:
        pieces = split_spread(image, options.mode)

    pages: list[Image.Image] = []
    for piece in pieces:
        if options.crop:
            piece = crop_borders(piece)
        pages.append(fit_to_canvas(piece, options))
    return pages
