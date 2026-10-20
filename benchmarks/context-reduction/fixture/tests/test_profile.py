import unittest
from src.profile import Profile, normalize_display_name, render_profile

class ProfileTests(unittest.TestCase):
    def test_normalize_display_name_trims_outer_spaces(self):
        self.assertEqual("Ada", normalize_display_name("  Ada  "))

    def test_render_profile_uses_normalized_display_name(self):
        self.assertEqual("Ada (u-1)", render_profile(Profile("u-1", " Ada ")))

if __name__ == "__main__":
    unittest.main()
