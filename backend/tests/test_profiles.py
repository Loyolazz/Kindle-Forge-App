from __future__ import annotations

import unittest

from kindle_forge.profiles import get_profile


class ProfileTests(unittest.TestCase):
    def test_kindle_basic_11_profile_stays_default_size(self) -> None:
        profile = get_profile("kindle11")

        self.assertEqual(profile.resolution, "1072x1448")

    def test_target_reader_profiles_are_available(self) -> None:
        self.assertEqual(get_profile("kindle-scribe").resolution, "1860x2480")
        self.assertEqual(get_profile("generic-hd-eink").resolution, "1072x1448")
        self.assertEqual(get_profile("pocketbook-inkpad-3").resolution, "1404x1872")
        self.assertEqual(get_profile("tablet").resolution, "1200x1920")
        self.assertEqual(get_profile("kindle-paperwhite-12").resolution, "1264x1680")
        self.assertEqual(get_profile("kobo-libra-colour").resolution, "1264x1680")
        self.assertEqual(get_profile("boox-palma").resolution, "824x1648")
        self.assertEqual(get_profile("kindle-scribe-colorsoft-2025").resolution, "1980x2640")


if __name__ == "__main__":
    unittest.main()
