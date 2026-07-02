"""Core file organization workflow."""

from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from typing import Iterable

from .categories import build_extension_lookup, categorize_file
from .config import OrganizerConfig
from .exceptions import FileOperationError, InvalidDirectoryError
from .summary import OrganizationSummary


def _iter_files_non_recursive(root_directory: Path) -> Iterable[Path]:
    for child in root_directory.iterdir():
        if child.is_file():
            yield child


def _iter_files_recursive(root_directory: Path, ignored_directories: set[str], destination_directories: set[str]) -> Iterable[Path]:
    for current_root, directory_names, file_names in os.walk(root_directory):
        current_directory = Path(current_root)
        if current_directory == root_directory:
            directory_names[:] = [name for name in directory_names if name not in ignored_directories and name not in destination_directories]
        else:
            directory_names[:] = [name for name in directory_names if name not in ignored_directories]

        for file_name in file_names:
            candidate = current_directory / file_name
            if candidate.is_file():
                yield candidate


def _split_filename(file_name: str) -> tuple[str, str]:
    suffixes = Path(file_name).suffixes
    if not suffixes:
        return file_name, ""

    suffix = "".join(suffixes)
    stem = file_name[: -len(suffix)]
    return stem, suffix


def _build_unique_destination(target_directory: Path, source_file: Path) -> Path:
    stem, suffix = _split_filename(source_file.name)
    candidate = target_directory / source_file.name
    counter = 1

    while candidate.exists():
        candidate = target_directory / f"{stem}_{counter}{suffix}"
        counter += 1

    return candidate


def organize_directory(
    root_directory: Path,
    config: OrganizerConfig,
    *,
    recursive: bool = False,
    dry_run: bool = False,
    logger: logging.Logger | None = None,
) -> OrganizationSummary:
    """Organize files inside a directory into type-based folders.

    Parameters
    ----------
    root_directory:
        Directory to organize.
    config:
        Runtime configuration and category definitions.
    recursive:
        When ``True``, process files from subdirectories as well.
    dry_run:
        When ``True``, report the planned actions without moving files.
    logger:
        Optional logger used for progress output.

    Returns
    -------
    OrganizationSummary
        A summary of processed, moved, and failed files.

    Raises
    ------
    InvalidDirectoryError
        If the root path is missing or is not a directory.
    FileOperationError
        If the organizer cannot read the directory contents.
    """

    if not root_directory.exists():
        raise InvalidDirectoryError(f"The selected path does not exist: {root_directory}")
    if not root_directory.is_dir():
        raise InvalidDirectoryError(f"The selected path is not a directory: {root_directory}")

    logger = logger or logging.getLogger("automated_file_organizer")
    extension_lookup = build_extension_lookup(config.category_extensions)
    destination_directories = set(config.category_extensions) | {"Others"}
    summary = OrganizationSummary(root_directory=root_directory, recursive=recursive, dry_run=dry_run)

    try:
        if recursive:
            file_iterator = _iter_files_recursive(root_directory, set(config.ignored_directories), destination_directories)
        else:
            file_iterator = _iter_files_non_recursive(root_directory)

        for source_file in file_iterator:
            category = categorize_file(source_file, extension_lookup)
            target_directory = root_directory / category
            destination_file = _build_unique_destination(target_directory, source_file)

            try:
                logger.info("Processing %s -> %s", source_file.name, category)
                if dry_run:
                    summary.register_move(category, dry_run=True)
                    continue

                target_directory.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source_file), str(destination_file))
                summary.register_move(category, dry_run=False)
            except (PermissionError, OSError, shutil.Error) as exc:
                summary.register_error(source_file, str(exc))
                logger.warning("Unable to organize %s: %s", source_file, exc)
    except OSError as exc:
        raise FileOperationError(f"Unable to read the directory contents: {exc}") from exc

    return summary