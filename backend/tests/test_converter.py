from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

from kindle_forge.converter import ConvertRequest, convert, filename_title_with_volume
from kindle_forge.profiles import get_profile


class ConverterTests(unittest.TestCase):
    def test_filename_title_with_volume_matches_job_folder_base(self) -> None:
        self.assertEqual(
            filename_title_with_volume("Tensei Shitara Slime datta Ken", "01"),
            "Tensei Shitara Slime datta Ken Vol 01",
        )

    def test_volume_is_added_to_title_and_filename(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            tmp_path = Path(temp)
            source = tmp_path / "page.png"
            Image.new("RGB", (800, 1200), "white").save(source)

            result = convert(
                ConvertRequest(
                    input_path=source,
                    output_dir=tmp_path / "out",
                    profile=get_profile("kindle11"),
                    title="Tensei Shitara Slime datta Ken",
                    series="Tensei Shitara Slime datta Ken",
                    volume="1",
                    crop=False,
                )
            )

            self.assertEqual(result.title, "Tensei Shitara Slime datta Ken - Vol. 1")
            self.assertEqual(result.outputs[0].name, "Tensei-Shitara-Slime-datta-Ken-Vol-1.epub")
            with ZipFile(result.outputs[0]) as epub:
                opf = epub.read("OEBPS/content.opf").decode("utf-8")
                self.assertIn("<dc:title>Tensei Shitara Slime datta Ken - Vol. 1</dc:title>", opf)

    def test_existing_volume_in_title_is_not_duplicated(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            tmp_path = Path(temp)
            source = tmp_path / "page.png"
            Image.new("RGB", (800, 1200), "white").save(source)

            result = convert(
                ConvertRequest(
                    input_path=source,
                    output_dir=tmp_path / "out",
                    profile=get_profile("kindle11"),
                    title="Tensei Shitara Slime datta Ken Vol. 01",
                    volume="1",
                    crop=False,
                )
            )

            self.assertEqual(result.title, "Tensei Shitara Slime datta Ken Vol. 01")

    def test_repeated_conversion_does_not_overwrite_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            tmp_path = Path(temp)
            source = tmp_path / "page.png"
            output_dir = tmp_path / "out"
            Image.new("RGB", (800, 1200), "white").save(source)

            request = ConvertRequest(
                input_path=source,
                output_dir=output_dir,
                profile=get_profile("kindle11"),
                title="Livro Teste",
                volume="1",
                crop=False,
            )

            first = convert(request)
            second = convert(request)

            self.assertEqual(first.outputs[0].name, "Livro-Teste-Vol-1.epub")
            self.assertEqual(second.outputs[0].name, "Livro-Teste-Vol-1-2.epub")
            self.assertTrue(first.outputs[0].exists())
            self.assertTrue(second.outputs[0].exists())


if __name__ == "__main__":
    unittest.main()
