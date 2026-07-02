# Project Documentation

## Introduction

Automated File Organizer is a Python command-line utility that sorts files in a chosen directory into category folders based on file extensions.

## Objectives

- Automate repetitive file sorting.
- Improve folder cleanliness and discoverability.
- Provide a safe, readable, and maintainable implementation.

## Problem Statement

Manually sorting files in download folders, desktop folders, and shared workspaces is slow and inconsistent. Users need a dependable tool that groups files by type without deleting data or producing confusing results.

## Solution

The application scans a target directory, classifies each file by extension, creates destination folders when required, and moves the files into their matching category. It also supports recursive traversal, dry-run mode, and duplicate filename handling.

## Architecture

The codebase uses a small modular architecture:

- `categories.py` manages extension-to-category matching.
- `config.py` loads and validates JSON configuration files.
- `organizer.py` contains the file traversal and move logic.
- `summary.py` stores run results and reporting data.
- `cli.py` exposes the user-facing command-line interface.

## Workflow

1. Parse command-line arguments.
2. Load the default or custom configuration.
3. Validate the selected directory.
4. Traverse the directory tree.
5. Categorize each file.
6. Move or preview the file action.
7. Print a completion summary.

## Folder Structure

```text
Automated File Organiser/
├── docs/
├── screenshots/
├── src/automated_file_organizer/
└── tests/
```

## Libraries Used

- `argparse` for CLI argument parsing.
- `dataclasses` for lightweight data models.
- `json` for configuration loading.
- `logging` for status reporting.
- `pathlib` for filesystem handling.
- `shutil` for moving files.
- `unittest` for automated testing.

## Module Explanation

- `categories.py`: Normalizes extensions and maps files to categories.
- `config.py`: Reads optional JSON settings and merges them with safe defaults.
- `exceptions.py`: Defines a clean exception hierarchy.
- `organizer.py`: Traverses files, creates folders, and moves files safely.
- `summary.py`: Captures counts, errors, and run metadata.
- `cli.py`: Presents the welcome message, options, and summary output.

## Function Overview

- `normalize_extension`: Ensures consistent extension formatting.
- `normalize_category_extensions`: Validates category configuration.
- `build_extension_lookup`: Builds a reverse extension lookup table.
- `categorize_file`: Selects the correct category for a file.
- `load_config`: Loads and validates optional JSON settings.
- `organize_directory`: Executes the main organization workflow.
- `main`: Provides the command-line entry point.

## Testing

Automated tests cover:

- Common category mappings.
- Multi-suffix archives.
- Dry-run behavior.
- Recursive organization.
- Duplicate filename handling.
- Invalid directory errors.
- Permission-related failures.
- CLI success and usage behavior.

Run tests with:

```bash
python -m unittest discover -s tests
```

## Results

The project delivers a working, non-destructive file organizer with clean output, controlled recursion, and a summary that helps users confirm what happened during the run.

## Advantages

- Minimal dependency footprint.
- Simple and predictable behavior.
- Safe duplicate handling.
- Straightforward customization through JSON.

## Limitations

- Classification is extension-based, not content-based.
- The command-line interface is the only interface included.
- Files with unusual or unknown extensions fall back to `Others`.

## Future Scope

- GUI support.
- Rule-based automation beyond extensions.
- Undo or restore functionality.
- Per-folder organization profiles.

## Conclusion

Automated File Organizer is a practical, professional-quality utility for sorting files quickly and safely while keeping the codebase easy to maintain.