"""Tests for the core organization workflow."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from unittest import mock
import unittest

from automated_file_organizer.config import default_config
from automated_file_organizer.exceptions import InvalidDirectoryError
from automated_file_organizer.organizer import organize_directory


class OrganizerTests(unittest.TestCase):
    """Validate file moves, dry runs, and error handling."""

    def _create_file(self, root: Path, relative_path: str, content: str = "sample") -> Path:
        file_path = root / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def test_dry_run_does_not_move_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            original_file = self._create_file(root, "photo.jpg")

            summary = organize_directory(root, default_config(), dry_run=True)

            self.assertTrue(original_file.exists())
            self.assertTrue(summary.dry_run)
            self.assertEqual(summary.planned_files, 1)
            self.assertEqual(summary.moved_files, 0)

    def test_recursive_organization_moves_files_into_categories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            image_file = self._create_file(root, "nested/image.jpg")
            document_file = self._create_file(root, "report.pdf")
            duplicate_source = self._create_file(root, "nested/duplicate.txt")
            duplicate_target = self._create_file(root, "duplicate.txt")

            summary = organize_directory(root, default_config(), recursive=True)

            self.assertFalse(image_file.exists())
            self.assertFalse(document_file.exists())
            self.assertFalse(duplicate_source.exists())
            self.assertFalse(duplicate_target.exists())
            self.assertTrue((root / "Images" / "image.jpg").exists())
            self.assertTrue((root / "PDFs" / "report.pdf").exists())
            self.assertTrue((root / "Documents" / "duplicate.txt").exists())
            self.assertTrue((root / "Documents" / "duplicate_1.txt").exists())
            self.assertEqual(summary.moved_files, 4)
            self.assertEqual(summary.failed_files, 0)

    def test_invalid_directory_raises(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "missing"

            with self.assertRaises(InvalidDirectoryError):
                organize_directory(root, default_config())

    def test_locked_file_is_reported_as_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            file_path = self._create_file(root, "blocked.mp3")
            original_move = shutil.move

            def move_side_effect(source, destination, copy_function=shutil.copy2):
                if Path(source).name == file_path.name:
                    raise PermissionError("file is locked")
                return original_move(source, destination, copy_function=copy_function)

            with mock.patch("automated_file_organizer.organizer.shutil.move", side_effect=move_side_effect):
                summary = organize_directory(root, default_config())

            self.assertTrue(file_path.exists())
            self.assertEqual(summary.failed_files, 1)
            self.assertEqual(summary.moved_files, 0)
            self.assertTrue(summary.errors)


if __name__ == "__main__":
    unittest.main()