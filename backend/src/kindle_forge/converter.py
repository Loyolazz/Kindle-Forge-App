from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .covers import BookMetadata, make_generated_cover, prepare_cover_image
from .images import ImageOptions, process_image
from .profiles import DeviceProfile
from .sources import iter_source_images
from .util import slugify
from .writers import save_page_image, write_cbz, write_epub, write_pdf


@dataclass(frozen=True)
class ConvertRequest:
    input_path: Path
    output_dir: Path
    profile: DeviceProfile
    title: Optional[str] = None
    author: str = "Unknown"
    series: str = ""
    volume: str = ""
    language: str = "pt-BR"
    publisher: str = ""
    description: str = ""
    mode: str = "manga"
    output_format: str = "epub"
    cover_mode: str = "first"
    cover_path: Optional[Path] = None
    split_size_mb: int = 200
    quality: int = 85
    crop: bool = True
    split_spreads: bool = True
    protect_first_page: bool = True
    color: bool = False
    dither: bool = False
    upscale: bool = True
    gamma: float = 1.0
    pdf_zoom: float = 1.0
    keep_pages: bool = False


@dataclass(frozen=True)
class ConvertResult:
    title: str
    page_count: int
    outputs: list[Path]
    mode: str
    split: bool = False


class ConvertError(RuntimeError):
    pass


def convert(request: ConvertRequest) -> ConvertResult:
    input_path = request.input_path.expanduser().resolve()
    output_dir = request.output_dir.expanduser().resolve()
    title = request.title or input_path.stem
    base_name = slugify(title)
    mode = detect_mode(input_path, request.profile, request.pdf_zoom) if request.mode == "auto" else request.mode
    metadata = BookMetadata(
        title=title,
        author=request.author,
        series=request.series,
        volume=request.volume,
        language=request.language,
        publisher=request.publisher,
        description=request.description,
    )

    options = ImageOptions(
        profile=request.profile,
        mode=mode,
        crop=request.crop,
        split_spreads=request.split_spreads,
        color=request.color,
        dither=request.dither,
        upscale=request.upscale,
        gamma=request.gamma,
    )

    with tempfile.TemporaryDirectory(prefix="kindle-forge-pages-") as temp:
        page_dir = Path(temp) / "pages"
        page_paths: list[Path] = []
        page_index = 0

        if request.cover_mode == "generated":
            page_index += 1
            page_path = page_dir / f"page_{page_index:04d}.jpg"
            save_page_image(make_generated_cover(metadata, request.profile), page_path, request.quality)
            page_paths.append(page_path)
        elif request.cover_mode == "custom" and request.cover_path:
            page_index += 1
            page_path = page_dir / f"page_{page_index:04d}.jpg"
            save_page_image(prepare_cover_image(request.cover_path.expanduser().resolve(), options), page_path, request.quality)
            page_paths.append(page_path)

        source_index = 0
        for source in iter_source_images(input_path, request.profile, request.pdf_zoom):
            source_index += 1
            source_options = options
            if source_index == 1 and request.protect_first_page and mode != "webtoon":
                source_options = ImageOptions(
                    profile=options.profile,
                    mode=options.mode,
                    crop=options.crop,
                    split_spreads=False,
                    color=options.color,
                    dither=options.dither,
                    upscale=options.upscale,
                    gamma=options.gamma,
                )
            for page in process_image(source.image, source_options):
                page_index += 1
                page_path = page_dir / f"page_{page_index:04d}.jpg"
                save_page_image(page, page_path, request.quality)
                page_paths.append(page_path)

        if not page_paths:
            raise ConvertError(f"No readable pages found in {input_path}")

        output_dir.mkdir(parents=True, exist_ok=True)
        formats = _expand_formats(request.output_format)
        outputs: list[Path] = []
        chunks = _page_chunks(page_paths, request.split_size_mb)
        split_happened = len(chunks) > 1

        if "epub" in formats:
            for index, chunk in enumerate(chunks, start=1):
                part_metadata = _part_metadata(metadata, index, len(chunks))
                outputs.append(
                    write_epub(
                        chunk,
                        output_dir / _part_name(base_name, index, len(chunks), ".epub"),
                        metadata=part_metadata,
                        profile=request.profile,
                        rtl=mode == "manga",
                        cover_index=1,
                    )
                )
        if "cbz" in formats:
            for index, chunk in enumerate(chunks, start=1):
                outputs.append(write_cbz(chunk, output_dir / _part_name(base_name, index, len(chunks), ".cbz")))
        if "pdf" in formats:
            for index, chunk in enumerate(chunks, start=1):
                outputs.append(write_pdf(chunk, output_dir / _part_name(base_name, index, len(chunks), ".pdf")))

        return ConvertResult(title=title, page_count=len(page_paths), outputs=outputs, mode=mode, split=split_happened)


def _expand_formats(output_format: str) -> set[str]:
    normalized = output_format.lower()
    if normalized == "all":
        return {"epub", "cbz", "pdf"}
    formats = {item.strip() for item in normalized.split(",") if item.strip()}
    supported = {"epub", "cbz", "pdf"}
    unknown = formats - supported
    if unknown:
        raise ConvertError(f"Unsupported output format(s): {', '.join(sorted(unknown))}")
    if not formats:
        raise ConvertError("Choose at least one output format.")
    return formats


def _page_chunks(page_paths: list[Path], split_size_mb: int) -> list[list[Path]]:
    if split_size_mb <= 0:
        return [page_paths]
    limit = split_size_mb * 1024 * 1024
    chunks: list[list[Path]] = []
    current: list[Path] = []
    current_size = 0
    for page_path in page_paths:
        size = page_path.stat().st_size
        if current and current_size + size > limit:
            chunks.append(current)
            current = []
            current_size = 0
        current.append(page_path)
        current_size += size
    if current:
        chunks.append(current)
    return chunks or [page_paths]


def _part_metadata(metadata: BookMetadata, index: int, total: int) -> BookMetadata:
    if total == 1:
        return metadata
    return BookMetadata(
        title=f"{metadata.title} - Parte {index}",
        author=metadata.author,
        series=metadata.series,
        volume=metadata.volume,
        language=metadata.language,
        publisher=metadata.publisher,
        description=metadata.description,
    )


def _part_name(base_name: str, index: int, total: int, suffix: str) -> str:
    if total == 1:
        return f"{base_name}{suffix}"
    return f"{base_name}-Parte-{index}{suffix}"


def detect_mode(input_path: Path, profile: DeviceProfile, pdf_zoom: float = 1.0) -> str:
    name = input_path.name.casefold()
    if any(token in name for token in ("webtoon", "manhwa", "vertical", "toon")):
        return "webtoon"
    if any(token in name for token in ("marvel", "dc", "comic", "comics", "hq", "batman", "superman")):
        return "comic"
    tall = 0
    wide = 0
    sampled = 0
    for source in iter_source_images(input_path, profile, pdf_zoom):
        sampled += 1
        ratio = source.image.height / max(1, source.image.width)
        inverse = source.image.width / max(1, source.image.height)
        if ratio >= 2.2:
            tall += 1
        if inverse >= 1.2:
            wide += 1
        if sampled >= 8:
            break
    if sampled and tall / sampled >= 0.5:
        return "webtoon"
    if sampled and wide / sampled >= 0.25:
        return "comic"
    return "manga"
