from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from kindle_forge import server


class ServerOutputLayoutTests(unittest.TestCase):
    def test_collection_id_uses_series_as_single_parent_folder(self) -> None:
        self.assertEqual(
            server._collection_id(
                "Tensei Shitara Slime datta Ken",
                "Tensei Shitara Slime datta Ken Vol. 01",
                "01",
            ),
            "Tensei-Shitara-Slime-datta-Ken",
        )

    def test_collection_id_strips_volume_from_title_when_series_is_empty(self) -> None:
        self.assertEqual(
            server._collection_id("", "Tensei Shitara Slime datta Ken Vol. 02", "02"),
            "Tensei-Shitara-Slime-datta-Ken",
        )

    def test_collection_id_infers_series_from_volume_title_without_volume_field(self) -> None:
        self.assertEqual(
            server._collection_id("", "Tensei Shitara Slime datta Ken Vol. 02", ""),
            "Tensei-Shitara-Slime-datta-Ken",
        )

    def test_file_payload_points_to_file_inside_epub_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            original_output_root = server.OUTPUT_ROOT
            try:
                server.OUTPUT_ROOT = Path(temp)
                output = server.OUTPUT_ROOT / "Serie" / "epub" / "Volume-01.epub"
                output.parent.mkdir(parents=True)
                output.write_bytes(b"epub")

                payload = server._file_payload("Serie", output)

                self.assertEqual(payload["name"], "Volume-01.epub")
                self.assertEqual(payload["url"], "/download/Serie/epub%2FVolume-01.epub")
            finally:
                server.OUTPUT_ROOT = original_output_root

    def test_attachment_limits_reject_too_many_pdfs(self) -> None:
        names = [f"capitulo-{index:03d}.pdf" for index in range(server.MAX_PDF_ATTACHMENTS + 1)]

        with self.assertRaisesRegex(ValueError, "Limite de PDFs"):
            server._validate_attachment_limits(names)

    def test_attachment_limits_reject_too_many_images(self) -> None:
        names = [f"pagina-{index:04d}.jpg" for index in range(server.MAX_IMAGE_ATTACHMENTS + 1)]

        with self.assertRaisesRegex(ValueError, "Limite de imagens"):
            server._validate_attachment_limits(names)

    def test_merge_pdf_files_creates_output_and_page_count(self) -> None:
        try:
            import fitz  # type: ignore[import-not-found]
        except ImportError:
            self.skipTest("PyMuPDF não está instalado")

        with tempfile.TemporaryDirectory() as temp:
            tmp_path = Path(temp)
            first = tmp_path / "001.pdf"
            second = tmp_path / "002.pdf"
            output = tmp_path / "merged.pdf"
            Image.new("RGB", (80, 120), "white").save(first, "PDF")
            Image.new("RGB", (90, 130), "gray").save(second, "PDF")

            result = server._merge_pdf_files([first, second], output)

            self.assertEqual(result.page_count, 2)
            self.assertEqual(result.outputs, [output])
            self.assertFalse(result.split)
            merged = fitz.open(result.outputs[0])
            try:
                self.assertEqual(merged.page_count, 2)
            finally:
                merged.close()

    def test_merge_pdf_files_splits_to_send_to_kindle_limit(self) -> None:
        try:
            import fitz  # type: ignore[import-not-found]
        except ImportError:
            self.skipTest("PyMuPDF não está instalado")

        with tempfile.TemporaryDirectory() as temp:
            tmp_path = Path(temp)
            first = tmp_path / "001.pdf"
            second = tmp_path / "002.pdf"
            output = tmp_path / "merged.pdf"
            Image.frombytes("RGB", (1200, 1200), os.urandom(1200 * 1200 * 3)).save(first, "PDF")
            Image.frombytes("RGB", (1200, 1200), os.urandom(1200 * 1200 * 3)).save(second, "PDF")

            result = server._merge_pdf_files([first, second], output, max_size_mb=1)

            self.assertEqual(result.page_count, 2)
            self.assertTrue(result.split)
            self.assertEqual(len(result.outputs), 2)
            self.assertTrue(all(path.stat().st_size <= server._send_to_kindle_max_bytes(1) for path in result.outputs))
            for path in result.outputs:
                merged = fitz.open(path)
                try:
                    self.assertEqual(merged.page_count, 1)
                finally:
                    merged.close()


if __name__ == "__main__":
    unittest.main()
