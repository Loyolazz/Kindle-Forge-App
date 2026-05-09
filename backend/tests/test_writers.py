from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

from kindle_forge.covers import BookMetadata
from kindle_forge.profiles import get_profile
from kindle_forge.writers import save_page_image, write_epub


class WriterTests(unittest.TestCase):
    def test_epub_contains_fixed_layout_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            tmp_path = Path(temp)
            page = tmp_path / "page_0001.jpg"
            save_page_image(Image.new("L", (1072, 1448), "white"), page, quality=80)
            output = tmp_path / "book.epub"

            write_epub([page], output, BookMetadata(title="Teste", author="Autor"), get_profile("k11"), rtl=True)

            with ZipFile(output) as epub:
                self.assertEqual(epub.read("mimetype"), b"application/epub+zip")
                opf = epub.read("OEBPS/content.opf").decode("utf-8")
                self.assertIn("pre-paginated", opf)
                self.assertIn("1072x1448", opf)
                self.assertIn('page-progression-direction="rtl"', opf)
                self.assertIn('properties="cover-image"', opf)


if __name__ == "__main__":
    unittest.main()
