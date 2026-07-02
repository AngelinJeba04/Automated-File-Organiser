"""Tests for file categorization helpers."""

from pathlib import Path
import unittest

from automated_file_organizer.categories import DEFAULT_CATEGORY_EXTENSIONS, build_extension_lookup, categorize_file, normalize_extension


class CategoryTests(unittest.TestCase):
    """Validate category normalization and file matching."""

    def setUp(self) -> None:
        self.extension_lookup = build_extension_lookup(DEFAULT_CATEGORY_EXTENSIONS)

    def test_normalize_extension_adds_leading_dot(self) -> None:
        self.assertEqual(normalize_extension("jpg"), ".jpg")

    def test_categorizes_multi_suffix_archive(self) -> None:
        category = categorize_file(Path("archive.tar.gz"), self.extension_lookup)
        self.assertEqual(category, "Archives")

    def test_unknown_extension_maps_to_others(self) -> None:
        category = categorize_file(Path("notes.custom"), self.extension_lookup)
        self.assertEqual(category, "Others")


if __name__ == "__main__":
    unittest.main()