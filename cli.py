"""Command-line interface for the automated file organizer."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from textwrap import dedent

from . import __version__
from .config import load_config
from .exceptions import ConfigurationError, FileOperationError, InvalidDirectoryError, OrganizerError
from .organizer import organize_directory


WELCOME_MESSAGE = dedent(
    """
    Automated File Organizer
    -------------------------
    Clean, safe organization of files into type-based folders.
    """
).strip()


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""

    parser = argparse.ArgumentParser(
        prog="automated-file-organizer",
        description="Organize a directory into categorized folders based on file type.",
    )
    parser.add_argument("directory", nargs="?", help="Directory to organize")
    parser.add_argument("--config", type=Path, help="Optional JSON configuration file")
    parser.add_argument("--recursive", action="store_true", help="Organize files from subdirectories too")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without moving files")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _configure_logging() -> logging.Logger:
    logger = logging.getLogger("automated_file_organizer")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def _print_summary(summary) -> None:
    mode_label = "Dry run" if summary.dry_run else "Completed"
    print()
    print(f"{mode_label} organization for: {summary.root_directory}")
    print(f"Files processed: {summary.processed_files}")
    if summary.dry_run:
        print(f"Planned moves: {summary.planned_files}")
    else:
        print(f"Files moved: {summary.moved_files}")
    print(f"Failed files: {summary.failed_files}")

    if summary.category_counts:
        print("Category breakdown:")
        for category_name in sorted(summary.category_counts):
            print(f"  - {category_name}: {summary.category_counts[category_name]}")

    if summary.errors:
        print("Errors:")
        for error in summary.errors:
            print(f"  - {error}")


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface.

    Parameters
    ----------
    argv:
        Optional custom argument list. When omitted, ``sys.argv[1:]`` is used.

    Returns
    -------
    int
        Process exit code.
    """

    parser = build_parser()
    args = parser.parse_args(argv)
    logger = _configure_logging()

    print(WELCOME_MESSAGE)
    print("Use this tool on a folder that contains files you want to categorize.")
    print("Tip: use --dry-run first when you want to preview the result.")

    if not args.directory:
        parser.print_help()
        return 2

    root_directory = Path(args.directory).expanduser()

    try:
        config = load_config(args.config)
        summary = organize_directory(
            root_directory,
            config,
            recursive=args.recursive,
            dry_run=args.dry_run,
            logger=logger,
        )
        _print_summary(summary)
        return 1 if summary.has_failures else 0
    except (ConfigurationError, InvalidDirectoryError, FileOperationError, OrganizerError) as exc:
        print(f"Error: {exc}")
        return 1
    except KeyboardInterrupt:
        print("Operation cancelled by user.")
        return 130


if __name__ == "__main__":
    sys.exit(main())