from __future__ import annotations

import io
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from zipfile import ZipFile

from PIL import Image

from .images import is_image_path, normalize_image
from .profiles import DeviceProfile
from .util import natural_key


ARCHIVE_EXTENSIONS = {".cbz", ".zip", ".epub", ".cbr", ".rar", ".cb7", ".7z"}
ZIP_EXTENSIONS = {".cbz", ".zip", ".epub"}
EXTERNAL_ARCHIVE_EXTENSIONS = {".cbr", ".rar", ".cb7", ".7z"}
DOCUMENT_EXTENSIONS = ARCHIVE_EXTENSIONS | {".pdf"}
SOURCE_EXTENSIONS = DOCUMENT_EXTENSIONS | {
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
class SourceImage:
    name: str
    image: Image.Image


class SourceError(RuntimeError):
    pass


def iter_source_images(path: Path, profile: DeviceProfile, pdf_zoom: float = 1.0) -> Iterator[SourceImage]:
    path = path.expanduser().resolve()
    if not path.exists():
        raise SourceError(f"Input not found: {path}")

    if path.is_dir():
        yield from _iter_directory(path, profile, pdf_zoom)
        return

    suffix = path.suffix.lower()
    if is_image_path(path):
        yield _open_image_file(path)
        return
    if suffix in ZIP_EXTENSIONS:
        yield from _iter_zip(path)
        return
    if suffix in EXTERNAL_ARCHIVE_EXTENSIONS:
        yield from _iter_external_archive(path, profile, pdf_zoom)
        return
    if suffix == ".pdf":
        yield from _iter_pdf(path, profile, pdf_zoom)
        return

    supported = ", ".join(sorted(ARCHIVE_EXTENSIONS | {".pdf"}))
    raise SourceError(f"Unsupported input '{path.suffix}'. Supported archives/documents: {supported}")


def _iter_directory(path: Path, profile: DeviceProfile, pdf_zoom: float) -> Iterator[SourceImage]:
    files = sorted(
        (item for item in path.rglob("*") if item.is_file() and item.suffix.lower() in SOURCE_EXTENSIONS),
        key=natural_key,
    )
    if not files:
        raise SourceError(f"No supported files found in folder: {path}")
    for file_path in files:
        suffix = file_path.suffix.lower()
        if is_image_path(file_path):
            yield _open_image_file(file_path)
        elif suffix in ZIP_EXTENSIONS:
            yield from _iter_zip(file_path)
        elif suffix in EXTERNAL_ARCHIVE_EXTENSIONS:
            yield from _iter_external_archive(file_path, profile, pdf_zoom)
        elif suffix == ".pdf":
            yield from _iter_pdf(file_path, profile, pdf_zoom)


def _open_image_file(path: Path) -> SourceImage:
    try:
        with Image.open(path) as image:
            loaded = normalize_image(image)
            loaded.load()
            return SourceImage(path.name, loaded)
    except Exception as exc:  # pragma: no cover - Pillow errors vary by decoder
        raise SourceError(f"Could not read image: {path}") from exc


def _open_image_bytes(name: str, data: bytes) -> SourceImage:
    try:
        with Image.open(io.BytesIO(data)) as image:
            loaded = normalize_image(image)
            loaded.load()
            return SourceImage(name, loaded)
    except Exception as exc:  # pragma: no cover - Pillow errors vary by decoder
        raise SourceError(f"Could not read image inside archive: {name}") from exc


def _iter_zip(path: Path) -> Iterator[SourceImage]:
    with ZipFile(path) as archive:
        names = sorted((name for name in archive.namelist() if is_image_path(Path(name))), key=natural_key)
        if not names:
            raise SourceError(f"No images found inside archive: {path}")
        for name in names:
            with archive.open(name) as file_obj:
                yield _open_image_bytes(name, file_obj.read())


def _iter_external_archive(path: Path, profile: DeviceProfile, pdf_zoom: float) -> Iterator[SourceImage]:
    extractor = _find_extractor(path.suffix.lower())
    if extractor is None:
        raise SourceError(
            "CBR/RAR/7Z input needs one extractor installed: 7z, 7zz, unar, unrar, or bsdtar."
        )

    with tempfile.TemporaryDirectory(prefix="kindle-forge-archive-") as temp:
        temp_path = Path(temp)
        command = _extract_command(extractor, path, temp_path)
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise SourceError(f"Could not extract {path.name} with {extractor}: {detail}")
        yield from _iter_directory(temp_path, profile, pdf_zoom)


def _find_extractor(suffix: str) -> Optional[str]:
    preferred = ["7zz", "7z", "unar", "unrar", "bsdtar"]
    if suffix in {".cb7", ".7z"}:
        preferred = ["7zz", "7z", "bsdtar"]
    for binary in preferred:
        if shutil.which(binary):
            return binary
    return None


def _extract_command(extractor: str, archive: Path, output_dir: Path) -> list[str]:
    if extractor in {"7z", "7zz"}:
        return [extractor, "x", "-y", f"-o{output_dir}", str(archive)]
    if extractor == "unar":
        return [extractor, "-quiet", "-o", str(output_dir), str(archive)]
    if extractor == "unrar":
        return [extractor, "x", "-idq", str(archive), str(output_dir)]
    return [extractor, "-xf", str(archive), "-C", str(output_dir)]


def _iter_pdf(path: Path, profile: DeviceProfile, pdf_zoom: float) -> Iterator[SourceImage]:
    try:
        import fitz  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SourceError("PDF input needs PyMuPDF. Install with: python -m pip install PyMuPDF") from exc

    document = fitz.open(path)
    try:
        if document.page_count == 0:
            raise SourceError(f"PDF has no pages: {path}")
        for index, page in enumerate(document, start=1):
            rect = page.rect
            fit_zoom = max(profile.width / rect.width, profile.height / rect.height)
            matrix = fitz.Matrix(fit_zoom * pdf_zoom, fit_zoom * pdf_zoom)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            mode = "RGB" if pixmap.n < 4 else "RGBA"
            image = Image.frombytes(mode, (pixmap.width, pixmap.height), pixmap.samples)
            yield SourceImage(f"{path.stem}-{index:04d}.png", normalize_image(image))
    finally:
        document.close()
