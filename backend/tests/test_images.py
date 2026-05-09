from __future__ import annotations

import unittest

from PIL import Image, ImageDraw

from kindle_forge.images import ImageOptions, crop_borders, process_image
from kindle_forge.profiles import get_profile


class ImageProcessingTests(unittest.TestCase):
    def test_crop_borders_removes_white_margin(self) -> None:
        image = Image.new("RGB", (200, 200), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((50, 40, 150, 160), fill="black")

        cropped = crop_borders(image, tolerance=8, backup=0)

        self.assertEqual(cropped.size, (101, 121))

    def test_manga_spread_splits_right_side_first(self) -> None:
        image = Image.new("RGB", (400, 200), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 199, 199), fill=(40, 40, 40))
        draw.rectangle((200, 0, 399, 199), fill=(220, 220, 220))
        options = ImageOptions(profile=get_profile("k11"), mode="manga", crop=False, split_spreads=True)

        pages = process_image(image, options)

        self.assertEqual(len(pages), 2)
        self.assertEqual(pages[0].size, (1072, 1448))
        self.assertGreater(pages[0].getpixel((536, 724)), pages[1].getpixel((536, 724)))

    def test_webtoon_slices_tall_page(self) -> None:
        image = Image.new("RGB", (500, 2400), "white")
        options = ImageOptions(profile=get_profile("kindle11"), mode="webtoon", crop=False, split_spreads=False)

        pages = process_image(image, options)

        self.assertGreater(len(pages), 1)
        self.assertTrue(all(page.size == (1072, 1448) for page in pages))


if __name__ == "__main__":
    unittest.main()
