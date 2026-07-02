"""Tests for the command-line interface."""

from __future__ import annotations

import contextlib
import io
import tempfile
from pathlib import Path
import unittest

from automated_file_organizer.cli import main


class CliTests(unittest.TestCase):
    """Validate user-facing command-line behavior."""

    def _create_file(self, root: Path, relative_path: str) -> Path:
        file_path = root / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("sample", encoding="utf-8")
        return file_path

    def test_main_moves_files_and_returns_success(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self._create_file(root, "photo.png")

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main([str(root)])

            self.assertEqual(exit_code, 0)
            self.assertTrue((root / "Images" / "photo.png").exists())
            self.assertIn("Automated File Organizer", output.getvalue())

    def test_main_rejects_missing_directory_argument(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = main([])

        self.assertEqual(exit_code, 2)
        self.assertIn("usage:", output.getvalue().lower())


if __name__ == "__main__":
    unittest.main()