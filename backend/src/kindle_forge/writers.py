from __future__ import annotations

import html
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from PIL import Image

from .covers import BookMetadata
from .profiles import DeviceProfile


def save_page_image(image: Image.Image, path: Path, quality: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    save_image = image.convert("RGB") if image.mode != "RGB" else image
    save_image.save(path, "JPEG", quality=quality, optimize=True, progressive=False)


def write_cbz(page_paths: list[Path], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output_path, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for index, page_path in enumerate(page_paths, start=1):
            archive.write(page_path, f"page_{index:04d}{page_path.suffix.lower()}")
    return output_path


def write_pdf(page_paths: list[Path], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    images = [Image.open(path).convert("RGB") for path in page_paths]
    try:
        first, rest = images[0], images[1:]
        first.save(output_path, "PDF", resolution=300.0, save_all=True, append_images=rest)
    finally:
        for image in images:
            image.close()
    return output_path


def write_epub(
    page_paths: list[Path],
    output_path: Path,
    metadata: BookMetadata,
    profile: DeviceProfile,
    rtl: bool,
    cover_index: Optional[int] = 1,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    book_uuid = f"urn:uuid:{uuid.uuid4()}"
    modified = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    with ZipFile(output_path, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip", compress_type=ZIP_STORED)
        archive.writestr("META-INF/container.xml", _container_xml(), compress_type=ZIP_DEFLATED)
        archive.writestr("OEBPS/style.css", _style_css(profile), compress_type=ZIP_DEFLATED)
        archive.writestr(
            "OEBPS/content.opf",
            _content_opf(page_paths, metadata, profile, book_uuid, modified, rtl, cover_index),
            compress_type=ZIP_DEFLATED,
        )
        archive.writestr(
            "OEBPS/nav.xhtml",
            _nav_xhtml(metadata.title, page_paths),
            compress_type=ZIP_DEFLATED,
        )
        archive.writestr(
            "OEBPS/toc.ncx",
            _toc_ncx(metadata.title, page_paths, book_uuid),
            compress_type=ZIP_DEFLATED,
        )

        for index, page_path in enumerate(page_paths, start=1):
            image_name = f"page_{index:04d}.jpg"
            page_name = f"page_{index:04d}.xhtml"
            archive.writestr(
                f"OEBPS/pages/{page_name}",
                _page_xhtml(index, image_name, profile),
                compress_type=ZIP_DEFLATED,
            )
            with page_path.open("rb") as file_obj:
                archive.writestr(f"OEBPS/images/{image_name}", file_obj.read(), compress_type=ZIP_DEFLATED)
    return output_path


def copy_pages_to_folder(page_paths: list[Path], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    for page_path in page_paths:
        shutil.copy2(page_path, output_dir / page_path.name)
    return output_dir


def _container_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""


def _style_css(profile: DeviceProfile) -> str:
    return f"""@page {{
  margin: 0;
}}
html, body {{
  margin: 0;
  padding: 0;
  width: {profile.width}px;
  height: {profile.height}px;
  background: #fff;
}}
body {{
  overflow: hidden;
}}
.page {{
  width: {profile.width}px;
  height: {profile.height}px;
}}
img {{
  display: block;
  width: {profile.width}px;
  height: {profile.height}px;
}}
"""


def _content_opf(
    page_paths: list[Path],
    metadata: BookMetadata,
    profile: DeviceProfile,
    book_uuid: str,
    modified: str,
    rtl: bool,
    cover_index: Optional[int],
) -> str:
    escaped_title = html.escape(metadata.title)
    escaped_author = html.escape(metadata.author)
    escaped_language = html.escape(metadata.language or "pt-BR")
    escaped_publisher = html.escape(metadata.publisher)
    escaped_description = html.escape(metadata.description)
    escaped_series = html.escape(metadata.series)
    escaped_volume = html.escape(metadata.volume)
    direction = "rtl" if rtl else "ltr"
    manifest_items = [
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
        '<item id="css" href="style.css" media-type="text/css"/>',
    ]
    spine_items = []
    for index, _page_path in enumerate(page_paths, start=1):
        manifest_items.append(
            f'<item id="page{index}" href="pages/page_{index:04d}.xhtml" media-type="application/xhtml+xml"/>'
        )
        cover_property = ' properties="cover-image"' if cover_index == index else ""
        manifest_items.append(
            f'<item id="img{index}" href="images/page_{index:04d}.jpg" media-type="image/jpeg"{cover_property}/>'
        )
        spine_items.append(f'<itemref idref="page{index}"/>')

    manifest = "\n    ".join(manifest_items)
    spine = "\n    ".join(spine_items)
    cover_meta = f'<meta name="cover" content="img{cover_index}"/>' if cover_index else ""
    publisher = f"<dc:publisher>{escaped_publisher}</dc:publisher>" if escaped_publisher else ""
    description = f"<dc:description>{escaped_description}</dc:description>" if escaped_description else ""
    series_meta = f'<meta property="belongs-to-collection" id="series">{escaped_series}</meta>' if escaped_series else ""
    volume_meta = f'<meta refines="#series" property="group-position">{escaped_volume}</meta>' if escaped_series and escaped_volume else ""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf"
         version="3.0"
         unique-identifier="bookid"
         prefix="rendition: http://www.idpf.org/vocab/rendition/#">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{book_uuid}</dc:identifier>
    <dc:title>{escaped_title}</dc:title>
    <dc:creator>{escaped_author}</dc:creator>
    <dc:language>{escaped_language}</dc:language>
    {publisher}
    {description}
    <meta property="dcterms:modified">{modified}</meta>
    {cover_meta}
    {series_meta}
    {volume_meta}
    <meta property="rendition:layout">pre-paginated</meta>
    <meta property="rendition:orientation">portrait</meta>
    <meta property="rendition:spread">none</meta>
    <meta name="fixed-layout" content="true"/>
    <meta name="orientation-lock" content="portrait"/>
    <meta name="original-resolution" content="{profile.resolution}"/>
    <meta name="book-type" content="comic"/>
    <meta name="primary-writing-mode" content="horizontal-{'rl' if rtl else 'lr'}"/>
  </metadata>
  <manifest>
    {manifest}
  </manifest>
  <spine toc="ncx" page-progression-direction="{direction}">
    {spine}
  </spine>
</package>
"""


def _page_xhtml(index: int, image_name: str, profile: DeviceProfile) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>Page {index}</title>
    <meta name="viewport" content="width={profile.width}, height={profile.height}"/>
    <link rel="stylesheet" type="text/css" href="../style.css"/>
  </head>
  <body>
    <div class="page"><img src="../images/{image_name}" alt="Page {index}"/></div>
  </body>
</html>
"""


def _nav_xhtml(title: str, page_paths: list[Path]) -> str:
    escaped_title = html.escape(title)
    items = "\n        ".join(
        f'<li><a href="pages/page_{index:04d}.xhtml">Page {index}</a></li>'
        for index, _page_path in enumerate(page_paths, start=1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
  <head>
    <title>{escaped_title}</title>
  </head>
  <body>
    <nav epub:type="toc" id="toc">
      <h1>{escaped_title}</h1>
      <ol>
        {items}
      </ol>
    </nav>
  </body>
</html>
"""


def _toc_ncx(title: str, page_paths: list[Path], book_uuid: str) -> str:
    escaped_title = html.escape(title)
    nav_points = []
    for index, _page_path in enumerate(page_paths, start=1):
        nav_points.append(
            f"""<navPoint id="navPoint-{index}" playOrder="{index}">
      <navLabel><text>Page {index}</text></navLabel>
      <content src="pages/page_{index:04d}.xhtml"/>
    </navPoint>"""
        )
    nav_map = "\n    ".join(nav_points)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="{book_uuid}"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>{escaped_title}</text></docTitle>
  <navMap>
    {nav_map}
  </navMap>
</ncx>
"""
