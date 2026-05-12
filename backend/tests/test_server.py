from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
